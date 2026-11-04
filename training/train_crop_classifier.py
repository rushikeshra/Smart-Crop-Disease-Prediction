import os
import sys
import json
import random
import argparse
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, callbacks
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

CROP_MAPPING = {
    "Apple": ["Apple___Apple_scab", "Apple___Black_rot", "Apple___healthy"],
    "Bell_Pepper": ["Pepper__bell___Bacterial_spot", "Pepper__bell___healthy"],
    "Corn": ["Corn_(maize)___Common_rust_", "Corn_(maize)___healthy"],
    "Cotton": [
        "Cotton___Alternaria_leaf_spot",
        "Cotton___Bacterial_blight",
        "Cotton___Leaf_curl_virus",
        "Cotton___healthy"
    ],
    "Grape": ["Grape___Black_rot", "Grape___healthy"],
    "Green_Gram": [
        "Green_Gram___Cercospora_leaf_spot",
        "Green_Gram___Powdery_mildew",
        "Green_Gram___Yellow_mosaic",
        "Green_Gram___healthy"
    ],
    "Pigeon_Pea": [
        "Pigeon_Pea___Cercospora_leaf_spot",
        "Pigeon_Pea___Phytophthora_blight",
        "Pigeon_Pea___Sterility_mosaic",
        "Pigeon_Pea___healthy"
    ],
    "Potato": ["Potato___Early_blight", "Potato___Late_blight", "Potato___healthy"],
    "Soybean": [
        "Soybean___healthy",
        "Soybean___Bacterial_blight",
        "Soybean___Frogeye_leaf_spot",
        "Soybean___Soybean_rust"
    ],
    "Tomato": ["Tomato___Early_blight", "Tomato___Late_blight", "Tomato___healthy"]
}

def get_class_to_crop_map():
    mapping = {}
    for crop, diseases in CROP_MAPPING.items():
        for d in diseases:
            mapping[d] = crop
    return mapping

def load_crop_dataset_from_split(split_dir, crop_names, img_size=(224, 224)):
    """
    Load images from processed split directory, mapping 16 disease folders into 7 crop classes.
    """
    class_to_crop = get_class_to_crop_map()
    crop_to_idx = {name: i for i, name in enumerate(crop_names)}

    image_paths = []
    labels = []

    for d in sorted(os.listdir(split_dir)):
        disease_dir = os.path.join(split_dir, d)
        if not os.path.isdir(disease_dir):
            continue
        crop = class_to_crop.get(d)
        if crop is None or crop not in crop_to_idx:
            continue
        crop_idx = crop_to_idx[crop]

        for fname in sorted(os.listdir(disease_dir)):
            fpath = os.path.join(disease_dir, fname)
            if os.path.isfile(fpath) and fname.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                image_paths.append(fpath)
                labels.append(crop_idx)

    return image_paths, labels

def create_tf_dataset(image_paths, labels, num_classes, img_size=(224, 224), batch_size=32, shuffle=True):
    def parse_function(filename, label):
        image_string = tf.io.read_file(filename)
        image = tf.io.decode_jpeg(image_string, channels=3)
        image = tf.image.resize(image, img_size)
        image = tf.cast(image, tf.float32)
        label_one_hot = tf.one_hot(label, depth=num_classes)
        return image, label_one_hot

    dataset = tf.data.Dataset.from_tensor_slices((image_paths, labels))
    if shuffle:
        dataset = dataset.shuffle(buffer_size=len(image_paths), seed=SEED)
    dataset = dataset.map(parse_function, num_parallel_calls=tf.data.AUTOTUNE)
    dataset = dataset.batch(batch_size)
    dataset = dataset.prefetch(buffer_size=tf.data.AUTOTUNE)
    return dataset

def build_crop_model(num_classes, img_size=(224, 224, 3), dropout_rate=0.3):
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.12),
        layers.RandomZoom(0.1),
        layers.RandomTranslation(0.05, 0.05),
        layers.RandomContrast(0.1)
    ], name="crop_data_augmentation")

    inputs = layers.Input(shape=img_size, name="input_image")
    x = data_augmentation(inputs)
    x = preprocess_input(x)

    base_model = MobileNetV2(
        input_shape=img_size,
        include_top=False,
        weights="imagenet"
    )
    base_model.trainable = False

    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D(name="crop_gap")(x)
    x = layers.BatchNormalization(name="crop_bn_1")(x)
    x = layers.Dropout(dropout_rate, name="crop_dropout_1")(x)
    x = layers.Dense(128, activation="relu", name="crop_features")(x)
    x = layers.BatchNormalization(name="crop_bn_2")(x)
    x = layers.Dropout(0.2, name="crop_dropout_2")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="crop_predictions")(x)

    model = models.Model(inputs=inputs, outputs=outputs, name="Crop_Classifier_MobileNetV2")
    return model, base_model

def compute_crop_centroids(model, image_paths, labels, crop_names, img_size=(224, 224)):
    """Compute and return 128-dimensional normalized centroids and distance bounds for each crop."""
    print("\n[INFO] Computing crop centroids in feature space for OOD detection...")
    feat_extractor = tf.keras.Model(inputs=model.input, outputs=model.get_layer("crop_features").output)

    crop_features = {c: [] for c in crop_names}

    # Batch process
    batch_size = 64
    for i in range(0, len(image_paths), batch_size):
        batch_paths = image_paths[i:i+batch_size]
        batch_labels = labels[i:i+batch_size]
        
        batch_imgs = []
        for p in batch_paths:
            with Image.open(p) as img:
                img_rgb = img.convert("RGB").resize(img_size)
                batch_imgs.append(np.array(img_rgb, dtype=np.float32))
        
        batch_tensor = np.array(batch_imgs, dtype=np.float32)
        feats = feat_extractor.predict(batch_tensor, verbose=0)
        # L2-normalize
        norms = np.linalg.norm(feats, axis=1, keepdims=True) + 1e-7
        norm_feats = feats / norms

        for idx, lbl in enumerate(batch_labels):
            crop_name = crop_names[lbl]
            crop_features[crop_name].append(norm_feats[idx])

    profiles = {}
    for crop in crop_names:
        vecs = np.array(crop_features[crop], dtype=np.float32)
        centroid = np.mean(vecs, axis=0)
        centroid = centroid / (np.linalg.norm(centroid) + 1e-7)
        # Compute cosine similarities of training samples to centroid
        sims = np.dot(vecs, centroid)
        p5 = float(np.percentile(sims, 5))
        min_sim = float(np.min(sims))
        mean_sim = float(np.mean(sims))
        calibrated_thresholds = {
            "Bell_Pepper": 0.785,
            "Corn": 0.760,
            "Apple": 0.630,
            "Grape": 0.780,
            "Potato": 0.680,
            "Soybean": 0.750,
            "Tomato": 0.620
        }
        ood_th = calibrated_thresholds.get(crop, max(0.65, round(p5 - 0.08, 3)))
        profiles[crop] = {
            "centroid": centroid.tolist(),
            "mean_cosine_similarity": mean_sim,
            "min_cosine_similarity": min_sim,
            "p5_cosine_similarity": p5,
            "ood_threshold": ood_th,
            "num_samples": len(vecs)
        }
        print(f"  {crop:<12} -> Centroid computed (N={len(vecs)}). Mean Sim: {mean_sim:.4f}, P5: {p5:.4f}, OOD Thresh: {profiles[crop]['ood_threshold']:.3f}")

    return profiles

def plot_crop_confusion_matrix(cm, crop_names, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.figure(figsize=(9, 7))
    display_names = [name.replace("_", " ") for name in crop_names]
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=display_names,
        yticklabels=display_names,
        cbar=True,
        linewidths=0.5
    )
    plt.title("Confusion Matrix - Supported Crop Classification", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Predicted Crop", fontsize=11, labelpad=8)
    plt.ylabel("True Crop", fontsize=11, labelpad=8)
    plt.xticks(rotation=30, ha="right", fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[INFO] Crop Confusion Matrix saved to: {output_path}")

def train_crop_classifier(data_dir, models_dir, epochs=12, batch_size=32, lr=1e-3):
    print("=" * 70)
    print("TRAINING DEDICATED SUPPORTED-CROP CLASSIFIER")
    print("=" * 70)

    crop_names = sorted(list(CROP_MAPPING.keys()))
    num_classes = len(crop_names)
    print(f"Target Supported Crops ({num_classes}): {crop_names}")

    train_dir = os.path.join(data_dir, "train")
    val_dir = os.path.join(data_dir, "val")
    test_dir = os.path.join(data_dir, "test")

    train_paths, train_labels = load_crop_dataset_from_split(train_dir, crop_names)
    val_paths, val_labels = load_crop_dataset_from_split(val_dir, crop_names)
    test_paths, test_labels = load_crop_dataset_from_split(test_dir, crop_names)

    print(f"Dataset split sizes: Train={len(train_paths)}, Val={len(val_paths)}, Test={len(test_paths)}")

    train_ds = create_tf_dataset(train_paths, train_labels, num_classes, batch_size=batch_size, shuffle=True)
    val_ds = create_tf_dataset(val_paths, val_labels, num_classes, batch_size=batch_size, shuffle=False)

    model, base_model = build_crop_model(num_classes=num_classes)
    model.compile(
        optimizer=optimizers.Adam(learning_rate=lr),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    os.makedirs(models_dir, exist_ok=True)
    best_weights_path = os.path.join(models_dir, "crop_model_best.h5")

    cb = [
        callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True, verbose=1),
        callbacks.ModelCheckpoint(filepath=best_weights_path, monitor="val_accuracy", mode="max", save_best_only=True, verbose=1),
        callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.3, patience=2, min_lr=1e-6, verbose=1)
    ]

    print("\n--- Training Crop Classification Head ---")
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=cb
    )

    # Save final Keras model
    keras_crop_model_path = os.path.join(models_dir, "crop_model.keras")
    model.save(keras_crop_model_path)
    print(f"[SUCCESS] Saved Crop Classifier to: {keras_crop_model_path}")

    # Save crop class mapping
    crop_classes_path = os.path.join(models_dir, "crop_classes.json")
    with open(crop_classes_path, "w", encoding="utf-8") as f:
        json.dump(crop_names, f, indent=4)
    print(f"[SUCCESS] Saved Crop Classes to: {crop_classes_path}")

    # Compute Feature Centroids and OOD Thresholds
    profiles = compute_crop_centroids(model, train_paths, train_labels, crop_names)
    centroids_path = os.path.join(models_dir, "crop_centroids.json")
    with open(centroids_path, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=4)
    print(f"[SUCCESS] Saved Crop Centroids and OOD profiles to: {centroids_path}")

    # Evaluate on Unseen Test Set
    print("\n" + "=" * 70)
    print("EVALUATING CROP CLASSIFIER ON INDEPENDENT TEST SET")
    print("=" * 70)
    
    test_ds = create_tf_dataset(test_paths, test_labels, num_classes, batch_size=batch_size, shuffle=False)
    y_preds_raw = model.predict(test_ds, verbose=0)
    y_pred_classes = np.argmax(y_preds_raw, axis=1)
    y_true_classes = np.array(test_labels)

    acc = float(accuracy_score(y_true_classes, y_pred_classes))
    print(f"\n>> UNSEEN TEST ACCURACY: {acc * 100:.2f}%\n")

    report = classification_report(y_true_classes, y_pred_classes, target_names=crop_names, output_dict=True)
    print(classification_report(y_true_classes, y_pred_classes, target_names=crop_names))

    cm = confusion_matrix(y_true_classes, y_pred_classes)
    cm_plot_path = os.path.join(BASE_DIR, "static", "images", "crop_confusion_matrix.png")
    plot_crop_confusion_matrix(cm, crop_names, cm_plot_path)

    metrics_out = {
        "test_accuracy": acc,
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "crop_classes": crop_names,
        "test_samples": len(test_labels)
    }
    metrics_path = os.path.join(models_dir, "crop_evaluation_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_out, f, indent=4)
    print(f"[SUCCESS] Saved evaluation metrics to: {metrics_path}")

    return model, profiles

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Crop Species Classifier & Compute OOD Profiles")
    parser.add_argument("--data_dir", type=str, default=os.path.join(BASE_DIR, "dataset", "processed"))
    parser.add_argument("--models_dir", type=str, default=os.path.join(BASE_DIR, "models"))
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    args = parser.parse_args()

    train_crop_classifier(
        args.data_dir,
        args.models_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr
    )
