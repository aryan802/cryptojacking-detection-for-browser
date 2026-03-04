# train_baselines.py

# 1. Load dataset
# 2. Encode labels
# 3. Drop metadata columns
# 4. Log transform
# 5. DATASET CHECK ← add correlation here
# 6. Cross-validation setup
# 7. Model tuning

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import make_scorer, f1_score, precision_score, recall_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.model_selection import cross_validate
from sklearn.metrics import precision_recall_curve

# Load dataset
data = pd.read_csv("../data/features/features_fast.csv")

# Convert labels to binary
data["label"] = data["label"].map({
    "benign": 0,
    "cryptojacking": 1
})

# Drop non-feature columns
data = data.drop(columns=["dataset", "site_id"])

# Split features and labels
X = data.drop("label", axis=1).values
y = data["label"].values

print("Dataset shape:", data.shape)
print("Feature count:", X.shape[1])
print("Class distribution:\n", pd.Series(y).value_counts())

# log transformation  (heap_mean and heap_delta have large scale variance)
X = data.drop("label", axis=1)

# Apply log transform only where values are >= 0
X_log = X.copy()

for col in X.columns:
    if (X[col] >= 0).all():
        X_log[col] = np.log1p(X[col])

X = X_log.values
y = data["label"].values

# print("NaN values:", np.isnan(X).sum())
# print("Inf values:", np.isinf(X).sum())

# Save the Processed Dataset

processed = pd.DataFrame(X, columns=X_log.columns)
processed["label"] = y

processed.to_csv(
    "../data/features/features_fast_log.csv",
    index=False
)

# feature correlation analysis

# Convert X back to DataFrame for analysis
feature_names = [
    "task_mean",
    "task_std",
    "heap_delta",
    "heap_mean",
    "heap_std",
    "total_requests",
    "script_requests",
    "wasm_requests",
    "unique_hosts"
]

df_features = pd.DataFrame(X, columns=feature_names)

corr = df_features.corr()

print("\nFeature Correlation Matrix:\n")
print(corr)

plt.figure(figsize=(8,6))
sns.heatmap(
    corr,
    annot=True,
    cmap="coolwarm",
    fmt=".2f"
)

plt.title("FAST Feature Correlation Matrix")
plt.tight_layout()
plt.show()

# Key Observations from correlation matrix

# 1. task_mean vs task_std

# Correlation ≈ 0.98

# Implication:

# Almost identical signal.

# Both measure variability of the same runtime metric.

# Action:
# Keep only one.

# Recommended: keep task_mean.

# 2. Network Activity Cluster

# Strong correlations:

# total_requests ↔ script_requests → 0.91

# total_requests ↔ unique_hosts → 0.88

# heap_mean ↔ total_requests → 0.88

# heap_mean ↔ unique_hosts → 0.80

# Interpretation:

# Pages with:

# more scripts

# more hosts

# more requests

# → allocate more heap memory.

# This cluster represents page complexity / activity intensity.

# 3. Heap Behavior
# heap_mean ↔ heap_std = 0.80

# Both measure memory footprint.

# Keep heap_mean, drop heap_std if dimensionality reduction is needed.

# 4. heap_delta

# Very weak correlation with most features:

# 0.13 – 0.22

# This is good.

# It likely captures dynamic memory changes, which may indicate mining loops.

# Keep it.

# 5. wasm_requests

# Almost independent feature.

# correlations ≈ 0

# This is excellent for detection because cryptojackers often use:

# WebAssembly miners

# wasm-based hashing engines

# Keep it.

# conclusion -> droping task_std and heap_std

# feature reduction implementation

features_to_drop = [
    "task_std",
    "heap_std"
]

data = data.drop(columns=features_to_drop)

X = data.drop("label", axis=1).values
y = data["label"].values

print("Final feature count:", X.shape[1])

# cross validation step

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

# define evaluation matrics

scoring = {
    "roc_auc": "roc_auc",
    "f1": make_scorer(f1_score),
    "precision": make_scorer(precision_score),
    "recall": make_scorer(recall_score),
    "pr_auc": "average_precision"
}

# random forest tuning

rf = RandomForestClassifier(random_state=42)

rf_params = {
    "n_estimators": [200, 400],
    "max_depth": [None, 5, 10],
    "min_samples_split": [2, 5],
    "min_samples_leaf": [1, 2],
    "max_features": ["sqrt"],
    "class_weight": ["balanced"]
}

rf_grid = GridSearchCV(
    rf,
    rf_params,
    scoring="roc_auc",
    cv=cv,
    n_jobs=-1,
    verbose=2
)

rf_grid.fit(X, y)

best_rf = rf_grid.best_estimator_

print("Best RF:", rf_grid.best_params_)

probs = best_rf.predict_proba(X)[:,1]

precision, recall, thresholds = precision_recall_curve(y, probs)

f1_scores = 2 * (precision * recall) / (precision + recall)

best_idx = np.argmax(f1_scores)
best_threshold = thresholds[best_idx]

print("Optimal threshold:", best_threshold)
print("Best F1:", f1_scores[best_idx])

# SVM (RBF Kernel)
svm_pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("svm", SVC(probability=True))
])

svm_params = {
    "svm__C": [0.1, 1, 10],
    "svm__gamma": ["scale", 0.01, 0.001],
    "svm__kernel": ["rbf"],
    "svm__class_weight": ["balanced"]
}

svm_grid = GridSearchCV(
    svm_pipe,
    svm_params,
    scoring="roc_auc",
    cv=cv,
    n_jobs=-1,
    verbose=2
)

svm_grid.fit(X, y)

best_svm = svm_grid.best_estimator_

print("Best SVM:", svm_grid.best_params_)

# XGBoost Tuning

xgb = XGBClassifier(
    objective="binary:logistic",
    eval_metric="logloss",
    random_state=42
)

xgb_params = {
    "n_estimators": [200, 400],
    "max_depth": [3, 5, 7],
    "learning_rate": [0.01, 0.1],
    "subsample": [0.8, 1.0],
    "colsample_bytree": [0.8, 1.0]
}

xgb_grid = GridSearchCV(
    xgb,
    xgb_params,
    scoring="roc_auc",
    cv=cv,
    n_jobs=-1,
    verbose=2
)

xgb_grid.fit(X, y)

best_xgb = xgb_grid.best_estimator_

print("Best XGB:", xgb_grid.best_params_)

# Evaluate Models (Research Metrics)

def evaluate_model(model, X, y):

    scores = cross_validate(
        model,
        X,
        y,
        scoring=scoring,
        cv=cv
    )

    for metric in scoring.keys():
        mean = scores[f"test_{metric}"].mean()
        std = scores[f"test_{metric}"].std()

        print(f"{metric}: {mean:.3f} ± {std:.3f}")

print("\nRandom Forest Performance")
evaluate_model(best_rf, X, y)

print("\nSVM Performance")
evaluate_model(best_svm, X, y)

print("\nXGBoost Performance")
evaluate_model(best_xgb, X, y)

# Extract Feature Importance
importances = best_rf.feature_importances_

feature_names = [
"task_mean",
"heap_delta",
"heap_mean",
"total_requests",
"script_requests",
"wasm_requests",
"unique_hosts"
]

importance_df = pd.DataFrame({
"feature": feature_names,
"importance": importances
}).sort_values("importance", ascending=False)

print(importance_df)

