# Machine Learning Models & Evaluation Documentation

This project incorporates two distinct machine learning models engineered for precision agriculture.

---

## 1. Crop Recommendation Model (Random Forest)

### 1.1 Mathematical Formulation
Random Forest is an ensemble learning method constructed from multiple decorrelated decision trees.
Given a feature vector:
$$\mathbf{x} = [N, P, K, \text{temp}, \text{humidity}, \text{pH}, \text{rainfall}]^T \in \mathbb{R}^7$$

Each tree $T_b$ ($b = 1, \dots, B$) casts a unit vote for class $k$:
$$\hat{C}_{\text{rf}}^B(\mathbf{x}) = \text{majority vote} \left\{ \hat{C}_b(\mathbf{x}) \right\}_{1}^B$$

The class probability $P(Y = k \mid \mathbf{x})$ is computed by averaging predictions across all trees:
$$P(Y = k \mid \mathbf{x}) = \frac{1}{B} \sum_{b=1}^{B} I(\hat{C}_b(\mathbf{x}) = k)$$

### 1.2 Training Specifications
- **Dataset**: 2,200 rows covering 22 distinct crops (100 samples per crop).
- **Split Ratio**: 80% Training ($n=1760$), 20% Testing ($n=440$) with stratification.
- **Hyperparameters**:
  - `n_estimators`: 100
  - `max_depth`: 16
  - `criterion`: 'gini'
  - `min_samples_split`: 2

### 1.3 Genuine Evaluated Metrics (Calculated on Test Split)
- **Accuracy**: **98.86%**
- **Macro Precision**: **98.87%**
- **Macro Recall**: **98.86%**
- **Macro F1-Score**: **98.86%**

#### Feature Importances:
1. **Rainfall**: $21.23\%$
2. **Humidity**: $19.82\%$
3. **Potassium (K)**: $17.14\%$
4. **Phosphorus (P)**: $16.96\%$
5. **Nitrogen (N)**: $13.34\%$
6. **Temperature**: $6.57\%$
7. **Soil pH**: $4.93\%$

---

## 2. Crop Disease Prediction Model (MobileNetV2 CNN)

### 2.1 Deep Learning Architecture
MobileNetV2 uses **depthwise separable convolutions** with **inverted residual linear bottlenecks** to drastically minimize parameters and computational operations while preserving high representational capacity.

```text
Input Tensor (224 x 224 x 3)
      ↓
Data Augmentation (Flip, Rotation, Zoom, Translation, Contrast)
      ↓
MobileNetV2 Base Feature Extractor (ImageNet Pre-trained)
      ↓
GlobalAveragePooling2D
      ↓
BatchNormalization + Dropout (Rate = 0.3)
      ↓
Dense Layer (256 Neurons, ReLU Activation)
      ↓
BatchNormalization + Dropout (Rate = 0.2)
      ↓
Dense Output Layer (16 Classes, Softmax Activation)
```

### 2.2 Preprocessing & Training
- Built-in MobileNetV2 preprocessing layer (`tf.math.truediv` by 127.5, `tf.math.subtract` 1.0) mapping raw $[0, 255]$ pixel values to $[-1, 1]$.
- Optimizer: Adam ($\alpha = 0.001$, fine-tuning $\alpha = 0.00001$).
- Loss Function: Categorical Cross-Entropy.
- Callbacks: Early Stopping (patience = 5), ModelCheckpoint, ReduceLROnPlateau.

### 2.3 Genuine Evaluated Metrics (Calculated on 519 Test Images in `models/evaluation_metrics.json`)
- **Evaluated Test Set Size**: 519 images
- **Number of Disease Classes**: **16 classes** across **7 crops**
- **Test Accuracy**: **96.34%**
- **Macro Precision**: **96.40%**
- **Macro Recall**: **96.33%**
- **Macro F1-Score**: **96.32%**

#### The 16 Authoritative Disease Classes:
1. `Apple___Apple_scab`
2. `Apple___Black_rot`
3. `Apple___healthy`
4. `Corn_(maize)___Common_rust_`
5. `Corn_(maize)___healthy`
6. `Grape___Black_rot`
7. `Grape___healthy`
8. `Pepper__bell___Bacterial_spot`
9. `Pepper__bell___healthy`
10. `Potato___Early_blight`
11. `Potato___Late_blight`
12. `Potato___healthy`
13. `Soybean___healthy`
14. `Tomato___Early_blight`
15. `Tomato___Late_blight`
16. `Tomato___healthy`
