# ===============================
# SHAP ANALIZI - RANDOM FOREST
# ===============================

import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor

# -------------------------------
# 1. Veri Okuma
# -------------------------------
df = pd.read_excel("yumurta kalitesi kalite.xlsx")  # dosya adını gerekirse değiştir

# -------------------------------
# 2. Hedef ve Feature Seçimi
# -------------------------------
target = "ortalama"

features = [
    "yas(hafta)",
    "agirlik",
    "uzunluk",
    "geni̇sli̇k",
    "sekil_i̇ndeksi",
    "mukavemet",
    "ak_uzunlugu",
    "sari_yuksekli̇gi̇",
    "sari_geni̇sli̇gi̇",
    "sari_i̇ndeksi",
    "sari_skoru",
    "ph"
]

X = df[features]
y = df[target]

# -------------------------------
# 3. Feature Engineering
# -------------------------------
X["agirlik_uzunluk_orani"] = X["agirlik"] / X["uzunluk"]
X["genislik_uzunluk_orani"] = X["geni̇sli̇k"] / X["uzunluk"]

# -------------------------------
# 4. Train-Test Split
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------------
# 5. Ölçekleme (0–1)
# -------------------------------
scaler = MinMaxScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns)
X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns)

# -------------------------------
# 6. OPTIMIZE RANDOM FOREST
# -------------------------------
rf = RandomForestRegressor(
    n_estimators=400,
    max_depth=6,
    min_samples_split=10,
    min_samples_leaf=4,
    random_state=42,
    n_jobs=-1
)

rf.fit(X_train_scaled, y_train)

# -------------------------------
# 7. SHAP EXPLAINER
# -------------------------------
explainer = shap.Explainer(rf, X_train_scaled)
shap_values = explainer(X_test_scaled)

# -------------------------------
# 8. SHAP SUMMARY PLOT
# -------------------------------
plt.figure()
shap.summary_plot(shap_values, X_test_scaled, show=False)
plt.tight_layout()
plt.show()

# -------------------------------
# 9. EN ÖNEMLI 3 DEĞIŞKEN IÇIN DETAY
# -------------------------------
important_features = [
    "mukavemet",
    "sari_yuksekli̇gi̇",
    "ph"
]

for feature in important_features:
    plt.figure()
    shap.dependence_plot(
        feature,
        shap_values.values,
        X_test_scaled,
        show=False
    )
    plt.tight_layout()
    plt.show()

print("✔ SHAP analizi tamamlandı.")
