import os
import sys
import json
import argparse
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, callbacks
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Set reproducibility seeds
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

def plot_training_curves(history_data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.figure(figsize=(14, 5))

    # Accuracy subplot
    plt.subplot(1, 2, 1)
    acc = history_data.get("accuracy", [])
    val_acc = history_data.get("val_accuracy", [])
    epochs_range = range(1, len(acc) + 1)
    plt.plot(epochs_range, acc, label="Training Accuracy", color="#2e7d32", linewidth=2)
    plt.plot(epochs_range, val_acc, label="Validation Accuracy", color="#1565c0", linewidth=2, linestyle="--")
    plt.title("Model Accuracy over Epochs", fontsize=13, fontweight="bold")
    plt.xlabel("Epoch", fontsize=11)
    plt.ylabel("Accuracy", fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.legend(loc="lower right")

    # Loss subplot
    plt.subplot(1, 2, 2)
    loss = history_data.get("loss", [])
    val_loss = history_data.get("val_loss", [])
    plt.plot(epochs_range, loss, label="Training Loss", color="#c62828", linewidth=2)
    plt.plot(epochs_range, val_loss, label="Validation Loss", color="#ef6c00", linewidth=2, linestyle="--")
    plt.title("Model Loss over Epochs", fontsize=13, fontweight="bold")
    plt.xlabel("Epoch", fontsize=11)
    plt.ylabel("Loss (Categorical Cross-Entropy)", fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[INFO] Training curves saved to: {output_path}")

def build_model(num_classes, img_size=(224, 224, 3), dropout_rate=0.3):
    # Data Augmentation pipeline (only active during training)
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.12),
        layers.RandomZoom(0.1),
        layers.RandomTranslation(0.05, 0.05),
        layers.RandomContrast(0.1)
    ], name="data_augmentation")

    inputs = layers.Input(shape=img_size, name="input_image")
    
    # Augmented input
    x = data_augmentation(inputs)
    
    # Preprocessing layer for MobileNetV2 [-1, 1]
    x = preprocess_input(x)
    
    # Pretrained MobileNetV2 Base
    base_model = MobileNetV2(
        input_shape=img_size,
        include_top=False,
        weights="imagenet"
    )
    base_model.trainable = False  # Initial freeze
    
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    x = layers.BatchNormalization(name="batch_norm_1")(x)
    x = layers.Dropout(dropout_rate, name="dropout_1")(x)
    x = layers.Dense(256, activation="relu", name="dense_features")(x)
    x = layers.BatchNormalization(name="batch_norm_2")(x)
    x = layers.Dropout(0.2, name="dropout_2")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = models.Model(inputs=inputs, outputs=outputs, name="PlantVillage_MobileNetV2")
    return model, base_model

def train_crop_model(data_dir, models_dir, epochs=15, fine_tune_epochs=10, batch_size=32, lr=1e-3, fine_tune_lr=1e-5):
    print("=" * 70)
    print("STARTING MOBILENETV2 TRANSFER LEARNING TRAINING PIPELINE")
    print("=" * 70)

    train_dir = os.path.join(data_dir, "train")
    val_dir = os.path.join(data_dir, "val")

    if not os.path.exists(train_dir) or not os.path.exists(val_dir):
        print(f"[ERROR] Processed train or val directories missing in {data_dir}.")
        print("Please run `python training/prepare_dataset.py` first.")
        return None

    # Load dataset using tf.keras.utils.image_dataset_from_directory
    img_size = (224, 224)
    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        label_mode="categorical",
        image_size=img_size,
        batch_size=batch_size,
        shuffle=True,
        seed=SEED
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        val_dir,
        label_mode="categorical",
        image_size=img_size,
        batch_size=batch_size,
        shuffle=False
    )

    class_names = train_ds.class_names
    num_classes = len(class_names)
    print(f"\n[INFO] Detected {num_classes} classes from training directory:")
    class_mapping = {i: name for i, name in enumerate(class_names)}
    for idx, name in class_mapping.items():
        print(f"  [{idx:>2}] -> {name}")

    os.makedirs(models_dir, exist_ok=True)
    mapping_path = os.path.join(models_dir, "class_names.json")
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(class_mapping, f, indent=4)
    print(f"[INFO] Saved class mapping to: {mapping_path}")

    # Optimize data pipeline performance
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

    # Build Model
    model, base_model = build_model(num_classes=num_classes)
    model.summary()

    # Compile Initial Stage
    model.compile(
        optimizer=optimizers.Adam(learning_rate=lr),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    best_model_path = os.path.join(models_dir, "disease_model.h5")
    
    cb_list = [
        callbacks.EarlyStopping(
            monitor="val_loss",
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        callbacks.ModelCheckpoint(
            filepath=best_model_path,
            monitor="val_accuracy",
            mode="max",
            save_best_only=True,
            verbose=1
        ),
        callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.3,
            patience=2,
            min_lr=1e-7,
            verbose=1
        )
    ]

    print("\n" + "=" * 70)
    print("STAGE 1: TRAINING CLASSIFICATION HEAD (BASE FROZEN)")
    print("=" * 70)
    history_stage1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=cb_list
    )

    # Stage 2: Controlled Fine-Tuning
    if fine_tune_epochs > 0:
        print("\n" + "=" * 70)
        print("STAGE 2: CONTROLLED FINE-TUNING (UNFREEZING TOP MOBILENETV2 LAYERS)")
        print("=" * 70)
        base_model.trainable = True
        
        # Unfreeze only the last 30 layers of MobileNetV2
        fine_tune_at = len(base_model.layers) - 30
        for layer in base_model.layers[:fine_tune_at]:
            layer.trainable = False

        print(f"[INFO] Total Base Layers: {len(base_model.layers)}, Trainable deeper layers: {len(base_model.layers) - fine_tune_at}")

        model.compile(
            optimizer=optimizers.Adam(learning_rate=fine_tune_lr),
            loss="categorical_crossentropy",
            metrics=["accuracy"]
        )

        total_epochs = epochs + fine_tune_epochs
        history_stage2 = model.fit(
            train_ds,
            validation_data=val_ds,
            initial_epoch=len(history_stage1.history["loss"]),
            epochs=total_epochs,
            callbacks=cb_list
        )

        merged_history = {
            "accuracy": history_stage1.history["accuracy"] + history_stage2.history["accuracy"],
            "val_accuracy": history_stage1.history["val_accuracy"] + history_stage2.history["val_accuracy"],
            "loss": history_stage1.history["loss"] + history_stage2.history["loss"],
            "val_loss": history_stage1.history["val_loss"] + history_stage2.history["val_loss"],
        }
    else:
        merged_history = history_stage1.history

    if not os.path.exists(best_model_path):
        model.save(best_model_path)
        print(f"[INFO] Saved model to: {best_model_path}")

    keras_model_path = os.path.join(models_dir, "disease_model.keras")
    try:
        if os.path.exists(best_model_path):
            best_m = tf.keras.models.load_model(best_model_path)
            best_m.save(keras_model_path)
        else:
            model.save(keras_model_path)
        print(f"[INFO] Exported native Keras model to: {keras_model_path}")
    except Exception as e:
        print(f"[WARNING] Native Keras export notice: {e}")

    hist_path = os.path.join(models_dir, "training_history.json")
    with open(hist_path, "w", encoding="utf-8") as f:
        json.dump(merged_history, f, indent=4)
    print(f"[INFO] Saved training history to: {hist_path}")

    curve_path = os.path.join(BASE_DIR, "static", "images", "training_curves.png")
    plot_training_curves(merged_history, curve_path)

    print("\n[SUCCESS] Model training complete!")
    return model

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train MobileNetV2 on Crop Disease Dataset")
    parser.add_argument("--data_dir", type=str, default=os.path.join(BASE_DIR, "dataset", "processed"), help="Path to processed dataset")
    parser.add_argument("--models_dir", type=str, default=os.path.join(BASE_DIR, "models"), help="Path to save models & mapping")
    parser.add_argument("--epochs", type=int, default=15, help="Stage 1 training epochs")
    parser.add_argument("--fine_tune_epochs", type=int, default=10, help="Stage 2 fine-tuning epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Stage 1 initial learning rate")
    parser.add_argument("--fine_tune_lr", type=float, default=1e-5, help="Stage 2 fine-tuning learning rate")
    args = parser.parse_args()

    train_crop_model(
        os.path.abspath(args.data_dir),
        os.path.abspath(args.models_dir),
        args.epochs,
        args.fine_tune_epochs,
        args.batch_size,
        args.lr,
        args.fine_tune_lr
    )
