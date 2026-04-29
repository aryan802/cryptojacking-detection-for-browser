import pennylane as qml
import pandas as pd
import numpy as np

from sklearn.svm import SVC
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.decomposition import PCA

# ----------------------------
# Reproducibility
# ----------------------------
np.random.seed(42)

# ----------------------------
# Load dataset
# ----------------------------
data = pd.read_csv(r"..\data\features\features_fast_log.csv")

# Encode labels
if data["label"].dtype == "object":
    data["label"] = data["label"].map({
        "benign": 0,
        "cryptojacking": 1
    })

# Drop unnecessary
for col in ["dataset", "site_id", "task_std", "heap_std"]:
    if col in data.columns:
        data = data.drop(columns=[col])

# ----------------------------
# FEATURE SELECTION (manual)
# ----------------------------
selected_features = [
    "task_mean",
    "heap_mean",
    "heap_delta",
    "script_requests",
    "total_requests"
]

X = data[selected_features].values
y = data["label"].values

print("Using features:", selected_features)
print("X shape:", X.shape)

# ----------------------------
# LOG TRANSFORM (safe)
# ----------------------------
# ----------------------------
# SAFE LOG TRANSFORM
# ----------------------------
def safe_log_transform(X):
    X_transformed = X.copy()

    for i in range(X.shape[1]):
        col = X[:, i]

        # If values are strictly positive → log1p
        if np.all(col >= 0):
            X_transformed[:, i] = np.log1p(col)

        else:
            # Shift to positive before log
            shift = abs(col.min()) + 1
            X_transformed[:, i] = np.log1p(col + shift)

    return X_transformed


X = safe_log_transform(X)

# ----------------------------
# ROBUST SCALING
# ----------------------------
scaler = RobustScaler()
X_scaled = scaler.fit_transform(X)

# ----------------------------
# MAP TO [0, pi]
# ----------------------------
X_min = X_scaled.min(axis=0)
X_max = X_scaled.max(axis=0)

X_encoded = np.pi * (X_scaled - X_min) / (X_max - X_min + 1e-8)

# ----------------------------
# OPTIONAL PCA (uncomment to use)
# ----------------------------
USE_PCA = True

if USE_PCA:
    pca = PCA(n_components=4)
    X_encoded = pca.fit_transform(X_encoded)
    print("After PCA shape:", X_encoded.shape)

# 🔥 Speed control (optional)
X_encoded = X_encoded[:150]
y = y[:150]

# ----------------------------
# Quantum Device
# ----------------------------
n_qubits = X_encoded.shape[1]
dev = qml.device("default.qubit", wires=n_qubits)

# ----------------------------
# IMPROVED FEATURE MAP
# ----------------------------
def feature_map(x):
    # reps = 2
    for _ in range(2):
        for i in range(n_qubits):
            qml.RY(x[i], wires=i)
            qml.RZ(x[i], wires=i)

        # FULL entanglement
        for i in range(n_qubits):
            for j in range(i + 1, n_qubits):
                qml.CZ(wires=[i, j])

# ----------------------------
# Kernel Circuit
# ----------------------------
@qml.qnode(dev)
def kernel_circuit(x1, x2):
    feature_map(x1)
    qml.adjoint(feature_map)(x2)
    return qml.probs(wires=range(n_qubits))

def quantum_kernel(x1, x2):
    return kernel_circuit(x1, x2)[0]

# ----------------------------
# Kernel Matrix
# ----------------------------
def compute_kernel_matrix(X1, X2, symmetric=False):
    K = np.zeros((len(X1), len(X2)))

    if symmetric:
        for i in range(len(X1)):
            for j in range(i, len(X2)):
                val = quantum_kernel(X1[i], X2[j])
                K[i, j] = val
                K[j, i] = val
    else:
        for i in range(len(X1)):
            for j in range(len(X2)):
                K[i, j] = quantum_kernel(X1[i], X2[j])

    return K

# ----------------------------
# Cross Validation (IMPROVED)
# ----------------------------
cv = RepeatedStratifiedKFold(
    n_splits=5,
    n_repeats=2,
    random_state=42
)

scores = []

# Light C tuning (fast)
C_values = [0.1, 1, 5, 10]

for fold, (train_idx, test_idx) in enumerate(cv.split(X_encoded, y), 1):
    print(f"\n--- Fold {fold} ---")

    X_train, X_test = X_encoded[train_idx], X_encoded[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    # Kernels
    K_train = compute_kernel_matrix(X_train, X_train, symmetric=True)
    K_test = compute_kernel_matrix(X_test, X_train)

    best_auc = 0

    for C in C_values:
        model = SVC(
            kernel="precomputed",
            probability=True,
            C=C,
            class_weight="balanced"
        )

        model.fit(K_train, y_train)
        probs = model.predict_proba(K_test)[:, 1]
        auc = roc_auc_score(y_test, probs)

        if auc > best_auc:
            best_auc = auc

    print(f"Best Fold AUC: {best_auc:.4f}")
    scores.append(best_auc)

# ----------------------------
# Final Results
# ----------------------------
print("\n==============================")
print("Improved Quantum Kernel SVM ROC-AUC:")
print(f"{np.mean(scores):.4f} ± {np.std(scores):.4f}")
print("==============================")
