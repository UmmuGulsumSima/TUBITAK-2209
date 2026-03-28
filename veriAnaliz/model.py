# ======================================
# 1. KÜTÜPHANELER
# ======================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

from scipy.stats import f_oneway

# ======================================
# 2. VERİ OKUMA
# ======================================
df = pd.read_excel("yumurta kalitesi kalite.xlsx")
df = df.drop(columns=["Unnamed: 27"], errors="ignore")

# ======================================
# 3. SÜTUN İSİMLERİNİ TEMİZLE
# ======================================
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("ı", "i")
    .str.replace("ğ", "g")
    .str.replace("ü", "u")
    .str.replace("ş", "s")
    .str.replace("ö", "o")
    .str.replace("ç", "c")
)

print("\nTemizlenmiş sütun isimleri:")
print(df.columns)

# ======================================
# 4. HEDEF DEĞİŞKEN (TEMİZ HALİYLE)
# ======================================
target = "ortalama"

# ======================================
# 5. GENOTİP ANOVA ANALİZİ
# ======================================
print("\n--- GENOTIP ANOVA ANALIZI ---")

groups = [
    df[df["genotip"] == g][target]
    for g in df["genotip"].unique()
]

f_stat, p_value = f_oneway(*groups)

print(f"F-istatistigi: {f_stat:.3f}")
print(f"p-degeri: {p_value:.6f}")

# ======================================
# 6. KATEGORIK → SAYISAL
# ======================================
df = pd.get_dummies(df, columns=["genotip"], drop_first=False)

# ======================================
# 7. GİRDİ / ÇIKTI AYIRMA
# ======================================
# Modelde kullanılmayacak sütunlar
drop_cols = ["kut", "orta", "si̇vri̇"]

df = df.drop(columns=[c for c in drop_cols if c in df.columns])

X = df.drop(columns=[target])
y = df[target]

X = X.select_dtypes(include=["int64", "float64"])

# ======================================
# 8. ÖLÇEKLEME
# ======================================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=X.columns)

# ======================================
# 9. TRAIN / TEST
# ======================================
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# ======================================
# 10. MODELLER
# ======================================
models = {
    "Linear Regression": LinearRegression(),
    "Ridge Regression": Ridge(alpha=1.0),
    "Random Forest": RandomForestRegressor(
        n_estimators=300,
        random_state=42
    )
}

results = []

# ======================================
# 11. MODEL EĞİTİM & DEĞERLENDİRME
# ======================================
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    results.append([name, rmse, r2])

# ======================================
# 12. MODEL KARŞILAŞTIRMA TABLOSU
# ======================================
results_df = pd.DataFrame(
    results, columns=["Model", "RMSE", "R2"]
).sort_values(by="R2", ascending=False)

print("\n--- MODEL KARŞILAŞTIRMA ---")
print(results_df)

# ======================================
# 13. MODEL KARŞILAŞTIRMA GRAFİĞİ
# ======================================
plt.figure(figsize=(8, 5))
sns.barplot(x="Model", y="R2", data=results_df)
plt.title("Modellere Gore R2 Karsilastirmasi")
plt.tight_layout()
plt.show()

# ======================================
# 14. RANDOM FOREST FEATURE IMPORTANCE
# ======================================
rf_model = models["Random Forest"]

importance_df = pd.DataFrame({
    "Degisken": X.columns,
    "Onem": rf_model.feature_importances_
}).sort_values(by="Onem", ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(
    x="Onem",
    y="Degisken",
    data=importance_df.head(15)
)
plt.title("Random Forest - Degisken Onemleri")
plt.tight_layout()
plt.show()

# ======================================
# 15. TAMAMLANDI
# ======================================
print("\nTum analizler basariyla tamamlandi.")
