import pennylane as qml
import pennylane.numpy as pnp
import numpy as np
import pandas as pd

from sklearn.svm import SVC
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

# ----------------------------
# Reproducibility
# ----------------------------
np.random.seed(42)

# ----------------------------
# Load dataset
# ----------------------------
data = pd.read_csv(r"..\data\features\features_fast_log.csv")

if data["label"].dtype == "object":
    data["label"] = data["label"].map({
        "benign": 0,
        "cryptojacking": 1
    })

for col in ["dataset", "site_id", "task_std", "heap_std"]:
    if col in data.columns:
        data = data.drop(columns=[col])

# ----------------------------
# Feature selection
# ----------------------------
features = [
    "task_mean",
    "heap_mean",
    "heap_delta",
    "script_requests"
]

X = data[features].values
y = data["label"].values

print("Using features:", features)
print("X shape:", X.shape)

# ----------------------------
# Scaling + encoding
# ----------------------------
scaler = RobustScaler()
X_scaled = scaler.fit_transform(X)

X_min = X_scaled.min(axis=0)
X_max = X_scaled.max(axis=0)

X_encoded = np.pi * (X_scaled - X_min) / (X_max - X_min + 1e-8)

# ----------------------------
# 🔥 BALANCED SUBSET (fix crash)
# ----------------------------
idx_class0 = np.where(y == 0)[0]
idx_class1 = np.where(y == 1)[0]

n = min(len(idx_class0), len(idx_class1), 30)

idx_balanced = np.concatenate([
    np.random.choice(idx_class0, n, replace=False),
    np.random.choice(idx_class1, n, replace=False)
])

np.random.shuffle(idx_balanced)

X_encoded = X_encoded[idx_balanced]
y = y[idx_balanced]

# convert to pnp
X_encoded = pnp.array(X_encoded)
y = pnp.array(y)

# ----------------------------
# Quantum device
# ----------------------------
n_qubits = X_encoded.shape[1]
dev = qml.device("default.qubit", wires=n_qubits)

# ----------------------------
# Feature map
# ----------------------------
def variational_map(x, weights):
    for i in range(n_qubits):
        qml.RY(x[i], wires=i)

    for i in range(n_qubits):
        qml.RY(weights[i], wires=i)

    for i in range(n_qubits - 1):
        qml.CZ(wires=[i, i+1])

# ----------------------------
# Kernel circuit
# ----------------------------
@qml.qnode(dev)
def kernel_circuit(x1, x2, weights):
    variational_map(x1, weights)
    qml.adjoint(variational_map)(x2, weights)
    return qml.probs(wires=range(n_qubits))

def quantum_kernel(x1, x2, weights):
    return kernel_circuit(x1, x2, weights)[0]

# ----------------------------
# Kernel matrix
# ----------------------------
def compute_kernel(X1, X2, weights):
    rows = []
    for i in range(len(X1)):
        row = []
        for j in range(len(X2)):
            row.append(quantum_kernel(X1[i], X2[j], weights))
        rows.append(pnp.stack(row))
    return pnp.stack(rows)

# ----------------------------
# Kernel alignment
# ----------------------------
def kernel_alignment(K, y):
    y = y * 2 - 1
    Y = pnp.outer(y, y)

    return pnp.sum(K * Y) / (
        pnp.sqrt(pnp.sum(K**2)) * pnp.sqrt(pnp.sum(Y**2)) + 1e-8
    )

# ----------------------------
# Train kernel (fixed)
# ----------------------------
weights = pnp.array(
    np.random.uniform(0, np.pi, n_qubits),
    requires_grad=True
)

opt = qml.GradientDescentOptimizer(stepsize=0.1)

print("\nTraining quantum kernel...")

for step in range(6):

    def cost(w):
        # balanced subsample each step
        idx0 = np.where(y == 0)[0]
        idx1 = np.where(y == 1)[0]

        sub_n = min(len(idx0), len(idx1), 15)

        idx = np.concatenate([
            np.random.choice(idx0, sub_n, replace=False),
            np.random.choice(idx1, sub_n, replace=False)
        ])

        X_sub = X_encoded[idx]
        y_sub = y[idx]

        K = compute_kernel(X_sub, X_sub, w)
        return -kernel_alignment(K, y_sub)

    weights = opt.step(cost, weights)

    K_dbg = compute_kernel(X_encoded[:20], X_encoded[:20], weights)
    print(f"Step {step}, Alignment: {kernel_alignment(K_dbg, y[:20]):.4f}")

# ----------------------------
# Evaluation
# ----------------------------
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scores = []

for fold, (train_idx, test_idx) in enumerate(cv.split(X_encoded, y), 1):
    print(f"\n--- Fold {fold} ---")

    X_train, X_test = X_encoded[train_idx], X_encoded[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    K_train = compute_kernel(X_train, X_train, weights)
    K_test = compute_kernel(X_test, X_train, weights)

    K_train = np.array(K_train, dtype=float)
    K_test = np.array(K_test, dtype=float)

    model = SVC(kernel="precomputed", probability=True, C=10)
    model.fit(K_train, y_train)

    probs = model.predict_proba(K_test)[:, 1]
    auc = roc_auc_score(y_test, probs)

    print(f"Fold AUC: {auc:.4f}")
    scores.append(auc)

# ----------------------------
# Final
# ----------------------------
print("\n==============================")
print("Balanced Trainable QML ROC-AUC:")
print(f"{np.mean(scores):.4f} ± {np.std(scores):.4f}")
print("==============================")