import pandas as pd
import numpy as np

from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, f1_score, precision_recall_curve, auc

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import OneClassSVM

# --------------------
# Load data
# --------------------
df = pd.read_csv("../data/features/features_fast.csv")

y = (df["label"] == "cryptojacking").astype(int).values

feature_cols = [
    "task_mean","task_std",
    "heap_delta","heap_mean","heap_std",
    "total_requests","script_requests","wasm_requests","unique_hosts"
]
X = df[feature_cols].values

# --------------------
# CV setup
# --------------------
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

def pr_auc(y_true, scores):
    p, r, _ = precision_recall_curve(y_true, scores)
    return auc(r, p)

results = []

# --------------------
# Logistic Regression
# --------------------
lr = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(max_iter=200, class_weight="balanced"))
])

# --------------------
# Random Forest
# --------------------
rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=None,
    class_weight="balanced",
    random_state=42
)

models = {
    "LogisticRegression": lr,
    "RandomForest": rf,
}

for name, model in models.items():
    aucs, f1s, praucs = [], [], []
    for train, test in cv.split(X, y):
        model.fit(X[train], y[train])
        scores = model.predict_proba(X[test])[:, 1]
        preds = (scores > 0.5).astype(int)

        aucs.append(roc_auc_score(y[test], scores))
        f1s.append(f1_score(y[test], preds))
        praucs.append(pr_auc(y[test], scores))

    results.append([name, np.mean(aucs), np.mean(f1s), np.mean(praucs)])

# --------------------
# One-Class SVM (Anomaly)
# trained on BENIGN only
# --------------------
benign_mask = (y == 0)
ocsvm = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", OneClassSVM(kernel="rbf", nu=0.1, gamma="scale"))
])

aucs, f1s, praucs = [], [], []
for train, test in cv.split(X, y):
    ocsvm.fit(X[train][benign_mask[train]])
    scores = -ocsvm.decision_function(X[test])  # higher = more anomalous
    preds = (scores > np.percentile(scores, 90)).astype(int)

    aucs.append(roc_auc_score(y[test], scores))
    f1s.append(f1_score(y[test], preds))
    praucs.append(pr_auc(y[test], scores))

results.append(["OneClassSVM", np.mean(aucs), np.mean(f1s), np.mean(praucs)])

# --------------------
# Report
# --------------------
out = pd.DataFrame(results, columns=["Model","ROC_AUC","F1","PR_AUC"])
print(out.round(3))
out.to_csv("../data/features/baseline_results.csv", index=False)
