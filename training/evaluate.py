import os
import sys
import json
import argparse
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support, accuracy_score
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def plot_confusion_matrix(cm, class_names, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.figure(figsize=(12, 10))
    
    # Format labels for clean display
    display_names = [name.replace("___", " - ").replace("_", " ") for name in class_names]
    
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Greens",
        xticklabels=display_names,
        yticklabels=display_names,
        cbar=True,
        linewidths=0.5
    )
    plt.title("Confusion Matrix - Crop Disease Classification", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Predicted Class", fontsize=12, labelpad=10)
    plt.ylabel("True Class", fontsize=12, labelpad=10)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[INFO] Confusion Matrix heatmap saved to: {output_path}")

def analyze_cross_crop_confusion(cm, class_names):
    print("\n" + "=" * 70)
    print("CROSS-CROP CONFUSION ANALYSIS")
    print("=" * 70)
    
    pairs_to_check = [
        ("Potato___Early_blight", "Tomato___Early_blight"),
        ("Potato___Late_blight", "Tomato___Late_blight"),
        ("Pepper__bell___Bacterial_spot", "Tomato___Bacterial_spot"),
        ("Potato___healthy", "Tomato___healthy"),
        ("Pepper__bell___healthy", "Tomato___healthy"),
        ("Pepper__bell___healthy", "Potato___healthy")
    ]

    name_to_idx = {name: i for i, name in enumerate(class_names)}
    found_confusion = False

    for c1, c2 in pairs_to_check:
        if c1 in name_to_idx and c2 in name_to_idx:
            idx1 = name_to_idx[c1]
            idx2 = name_to_idx[c2]
            conf_1_as_2 = cm[idx1][idx2]
            conf_2_as_1 = cm[idx2][idx1]
            
            print(f"Check: '{c1}' vs '{c2}':")
            print(f"  - True {c1} misclassified as {c2}: {conf_1_as_2}")
            print(f"  - True {c2} misclassified as {c1}: {conf_2_as_1}")
            if conf_1_as_2 > 0 or conf_2_as_1 > 0:
                found_confusion = True
    
    if not found_confusion:
        print("[SUCCESS] Zero cross-crop confusion detected between similar disease names across crops!")
    print("=" * 70)

def evaluate_model(test_dir, model_path, class_names_path, output_metrics_path):
    print("=" * 70)
    print("EVALUATING CROP DISEASE CLASSIFIER")
    print("=" * 70)

    if not os.path.exists(test_dir):
        print(f"[ERROR] Test directory not found: {test_dir}")
        return None

    if not os.path.exists(model_path):
        h5_path = model_path.replace(".keras", ".h5")
        if os.path.exists(h5_path):
            model_path = h5_path
        else:
            print(f"[ERROR] Model file not found: {model_path}")
            return None

    if not os.path.exists(class_names_path):
        print(f"[ERROR] Class names mapping not found: {class_names_path}")
        return None

    with open(class_names_path, "r", encoding="utf-8") as f:
        class_mapping = json.load(f)
    
    class_names = [class_mapping[str(i)] if str(i) in class_mapping else class_mapping[i] for i in range(len(class_mapping))]

    print(f"[INFO] Loading model from: {model_path}")
    model = tf.keras.models.load_model(model_path, compile=False)

    # Load test dataset
    test_ds = tf.keras.utils.image_dataset_from_directory(
        test_dir,
        label_mode="categorical",
        image_size=(224, 224),
        batch_size=32,
        shuffle=False
    )

    y_true_list = []
    y_pred_list = []

    print("[INFO] Running test set predictions...")
    for images, labels in test_ds:
        preds = model.predict(images, verbose=0)
        y_true_list.extend(np.argmax(labels.numpy(), axis=1))
        y_pred_list.extend(np.argmax(preds, axis=1))

    y_true = np.array(y_true_list)
    y_pred = np.array(y_pred_list)

    # Calculate overall metrics
    test_acc = accuracy_score(y_true, y_pred)
    prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
    prec_weighted, rec_weighted, f1_weighted, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)

    # Classification report
    clf_report = classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        output_dict=True,
        zero_division=0
    )
    clf_report_text = classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        zero_division=0
    )

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)

    print("\n" + "=" * 70)
    print("TEST EVALUATION RESULTS")
    print("=" * 70)
    print(f"Overall Test Accuracy:    {test_acc * 100:.2f}%")
    print(f"Macro Precision:          {prec_macro * 100:.2f}%")
    print(f"Macro Recall:             {rec_macro * 100:.2f}%")
    print(f"Macro F1-Score:           {f1_macro * 100:.2f}%")
    print(f"Weighted F1-Score:        {f1_weighted * 100:.2f}%")
    print("\n[CLASSIFICATION REPORT]")
    print(clf_report_text)

    # Cross-crop analysis
    analyze_cross_crop_confusion(cm, class_names)

    # Plot Confusion Matrix
    cm_path = os.path.join(BASE_DIR, "static", "images", "confusion_matrix.png")
    plot_confusion_matrix(cm, class_names, cm_path)

    # Save metrics JSON
    metrics = {
        "test_accuracy": float(test_acc),
        "macro_precision": float(prec_macro),
        "macro_recall": float(rec_macro),
        "macro_f1": float(f1_macro),
        "weighted_f1": float(f1_weighted),
        "classification_report": clf_report,
        "confusion_matrix": cm.tolist(),
        "class_names": class_names
    }

    os.makedirs(os.path.dirname(output_metrics_path), exist_ok=True)
    with open(output_metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)
    print(f"[INFO] Saved metrics report to: {output_metrics_path}")

    return metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate MobileNetV2 Model on Test Set")
    parser.add_argument("--test_dir", type=str, default=os.path.join(BASE_DIR, "dataset", "processed", "test"), help="Path to test set")
    parser.add_argument("--model_path", type=str, default=os.path.join(BASE_DIR, "models", "disease_model.keras"), help="Path to model file")
    parser.add_argument("--class_names_path", type=str, default=os.path.join(BASE_DIR, "models", "class_names.json"), help="Path to class mapping")
    parser.add_argument("--metrics_path", type=str, default=os.path.join(BASE_DIR, "models", "evaluation_metrics.json"), help="Path to save metrics JSON")
    args = parser.parse_args()

    evaluate_model(
        os.path.abspath(args.test_dir),
        os.path.abspath(args.model_path),
        os.path.abspath(args.class_names_path),
        os.path.abspath(args.metrics_path)
    )
