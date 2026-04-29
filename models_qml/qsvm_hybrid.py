import pennylane as qml
import pennylane.numpy as pnp
import numpy as np
import pandas as pd

from sklearn.svm import SVC
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.neural_network import MLPClassifier

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

features = [
    "task_mean",
    "heap_mean",
    "heap_delta",
    "script_requests"
]

X = data[features].values
y = data["label"].values

# ----------------------------
# Scaling
# ----------------------------
scaler = RobustScaler()
X_scaled = scaler.fit_transform(X)

# ----------------------------
# 🔥 SUPERVISED NN (KEY FIX)
# ----------------------------
mlp = MLPClassifier(
    hidden_layer_sizes=(16, 8),
    max_iter=1000,
    random_state=42
)

mlp.fit(X_scaled, y)

# Use hidden layer output as features
def get_latent_features(model, X):
    hidden = X
    for i in range(len(model.coefs_) - 1):
        hidden = np.dot(hidden, model.coefs_[i]) + model.intercepts_[i]
        hidden = np.tanh(hidden)
    return hidden

X_nn = get_latent_features(mlp, X_scaled)

# ----------------------------
# Map to [0, pi]
# ----------------------------
X_min = X_nn.min(axis=0)
X_max = X_nn.max(axis=0)

X_encoded = np.pi * (X_nn - X_min) / (X_max - X_min + 1e-8)

# Limit size for speed
X_encoded = X_encoded[:120]
y = y[:120]

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
def feature_map(x):
    for _ in range(2):
        for i in range(n_qubits):
            qml.RY(x[i], wires=i)

        for i in range(n_qubits - 1):
            qml.CZ(wires=[i, i+1])

# ----------------------------
# Kernel
# ----------------------------
@qml.qnode(dev)
def kernel_circuit(x1, x2):
    feature_map(x1)
    qml.adjoint(feature_map)(x2)
    return qml.probs(wires=range(n_qubits))

def quantum_kernel(x1, x2):
    return kernel_circuit(x1, x2)[0]

def compute_kernel(X1, X2):
    rows = []
    for i in range(len(X1)):
        row = []
        for j in range(len(X2)):
            row.append(quantum_kernel(X1[i], X2[j]))
        rows.append(pnp.stack(row))
    return pnp.stack(rows)

# ----------------------------
# CV
# ----------------------------
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scores = []

for fold, (train_idx, test_idx) in enumerate(cv.split(X_encoded, y), 1):
    print(f"\n--- Fold {fold} ---")

    X_train, X_test = X_encoded[train_idx], X_encoded[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    K_train = compute_kernel(X_train, X_train)
    K_test = compute_kernel(X_test, X_train)

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
print("Supervised Hybrid QML ROC-AUC:")
print(f"{np.mean(scores):.4f} ± {np.std(scores):.4f}")
print("==============================")