# # =====================================================
# # 1. KÜTÜPHANELER
# # =====================================================
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt

# from sklearn.model_selection import train_test_split, GridSearchCV
# from sklearn.preprocessing import StandardScaler
# from sklearn.metrics import r2_score, mean_squared_error
# from sklearn.ensemble import RandomForestRegressor

# # =====================================================
# # 2. VERİ OKUMA
# # =====================================================
# df = pd.read_excel("yumurta kalitesi kalite.xlsx")

# # =====================================================
# # 3. SÜTUN İSİMLERİNİ TEMİZLE (KRİTİK!)
# # =====================================================
# df.columns = (
#     df.columns
#     .str.strip()
#     .str.lower()
#     .str.replace(" ", "_")
#     .str.replace("(", "_")
#     .str.replace(")", "")
#     .str.replace("ı", "i")
#     .str.replace("ğ", "g")
#     .str.replace("ü", "u")
#     .str.replace("ş", "s")
#     .str.replace("ö", "o")
#     .str.replace("ç", "c")
# )


# # =====================================================
# # 4. HEDEF DEĞİŞKEN
# # =====================================================
# target = "ortalama"

# # =====================================================
# # 5. MODELDE KULLANILMAYACAK SÜTUNLAR
# # =====================================================
# drop_cols = [
#     "kut",
#     "orta",
#     "sivri"
# ]

# df = df.drop(columns=[c for c in drop_cols if c in df.columns])

# # =====================================================
# # 6. FEATURE ENGINEERING (1. ADIM)
# # =====================================================

# # Yaş kategorisi (haftaya göre)
# df["yas_grubu"] = pd.cut(
#     df["yas_hafta"],
#     bins=[0, 30, 60, 100],
#     labels=["genc", "orta", "yasli"]
# )

# # Ak indeksi / Sarı indeksi oranı
# df["ak_sari_orani"] = df["ak"] / (df["sari_indeksi"] + 1)

# # Ağırlık – şekil etkileşimi
# df["agirlik_sekil_etkilesim"] = df["agirlik"] * df["sekil_indeksi"]

# # =====================================================
# # 7. KATEGORİK DEĞİŞKENLERİ SAYISALA ÇEVİR
# # =====================================================
# categorical_cols = ["genotip", "grup", "yas_grubu"]

# df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

# # =====================================================
# # 8. X / y AYIRMA
# # =====================================================
# X = df.drop(columns=[target])
# y = df[target]

# # Sadece sayısal kolonlar
# X = X.select_dtypes(include=["int64", "float64"])

# # =====================================================
# # 9. ÖLÇEKLEME
# # =====================================================
# scaler = StandardScaler()
# X_scaled = scaler.fit_transform(X)

# # =====================================================
# # 10. TRAIN / TEST
# # =====================================================
# X_train, X_test, y_train, y_test = train_test_split(
#     X_scaled,
#     y,
#     test_size=0.2,
#     random_state=42
# )

# # =====================================================
# # 11. RANDOM FOREST + HİPERPARAMETRE OPTİMİZASYONU
# # =====================================================
# rf = RandomForestRegressor(random_state=42)

# param_grid = {
#     "n_estimators": [300, 500],
#     "max_depth": [None, 10, 20],
#     "min_samples_leaf": [1, 2, 4],
#     "max_features": ["sqrt", "log2"]
# }

# grid = GridSearchCV(
#     rf,
#     param_grid,
#     cv=5,
#     scoring="r2",
#     n_jobs=-1
# )

# grid.fit(X_train, y_train)

# best_model = grid.best_estimator_

# # =====================================================
# # 12. MODEL DEĞERLENDİRME
# # =====================================================
# y_pred = best_model.predict(X_test)

# r2 = r2_score(y_test, y_pred)
# rmse = np.sqrt(mean_squared_error(y_test, y_pred))

# print("\nEN IYI PARAMETRELER:")
# print(grid.best_params_)

# print("\nMODEL PERFORMANSI:")
# print(f"R2  : {r2:.3f}")
# print(f"RMSE: {rmse:.3f}")

# # =====================================================
# # 13. GERÇEK vs TAHMİN GRAFİĞİ
# # =====================================================
# plt.figure(figsize=(7, 7))
# plt.scatter(y_test, y_pred, alpha=0.7)
# plt.plot(
#     [y_test.min(), y_test.max()],
#     [y_test.min(), y_test.max()],
#     linestyle="--"
# )
# plt.xlabel("Gercek Ortalama")
# plt.ylabel("Tahmin Edilen Ortalama")
# plt.title("Random Forest – Gercek vs Tahmin")
# plt.grid(True)
# plt.tight_layout()
# plt.show()

# ======================================
# 1. KÜTÜPHANELER
# ======================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# ======================================
# 2. VERİ OKUMA
# ======================================
df = pd.read_excel("yumurta kalitesi kalite.xlsx")
df = df.drop(columns=["Unnamed: 27"], errors="ignore")
# ======================================
# SÜTUN İSİMLERİNİ PROFESYONELCE TEMİZLE
# ======================================
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("(", "")
    .str.replace(")", "")
    .str.replace("ı", "i")
    .str.replace("ğ", "g")
    .str.replace("ü", "u")
    .str.replace("ş", "s")
    .str.replace("ö", "o")
    .str.replace("ç", "c")
)

# ======================================
# 3. HEDEF
# ======================================
target = "ortalama"

# ======================================
# 4. FEATURE ENGINEERING
# ======================================
df["agirlik_uzunluk_orani"] = df["agirlik"] / df["uzunluk"]
df["genislik_uzunluk_orani"] = df["geni̇sli̇k"] / df["uzunluk"]

df["ak_yukseklik_orani"] = df["ak"] / (df["ak"] + df["sari"])
df["sari_oran"] = df["sari"] / (df["ak"] + df["sari"])

df["haugh_log"] = np.log1p(df["haugh_birimi"])

# ======================================
# 5. KULLANILMAYACAK SÜTUNLAR
# ======================================
drop_cols = [
    "kut",
    "orta",
    "si̇vri̇"
]

df = df.drop(columns=[c for c in drop_cols if c in df.columns])

# ======================================
# 6. KATEGORİK → SAYISAL
# ======================================
df = pd.get_dummies(df, columns=["genotip"], drop_first=True)

# ======================================
# 7. GİRDİ / ÇIKTI
# ======================================
X = df.drop(columns=[target])
y = df[target]

X = X.select_dtypes(include=["int64", "float64"])

# ======================================
# 8. TRAIN / TEST
# ======================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ======================================
# 9. RANDOM FOREST + GRIDSEARCH
# ======================================
rf = RandomForestRegressor(random_state=42)

param_grid = {
    "n_estimators": [200, 400, 600],
    "max_depth": [6, 8, 12, None],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4]
}

grid = GridSearchCV(
    rf,
    param_grid,
    cv=5,
    scoring="r2",
    n_jobs=-1
)

grid.fit(X_train, y_train)

best_rf = grid.best_estimator_

# ======================================
# 10. TEST PERFORMANSI
# ======================================
y_pred = best_rf.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\n--- OPTİMİZE RANDOM FOREST ---")
print("En iyi parametreler:")
print(grid.best_params_)

print(f"\nRMSE: {rmse:.3f}")
print(f"R²  : {r2:.3f}")

# ======================================
# 11. FEATURE IMPORTANCE
# ======================================
importance_df = pd.DataFrame({
    "Degisken": X.columns,
    "Onem": best_rf.feature_importances_
}).sort_values(by="Onem", ascending=False)

plt.figure(figsize=(10,6))
sns.barplot(
    x="Onem",
    y="Degisken",
    data=importance_df.head(15)
)
plt.title("Optimize Random Forest - Degisken Onemleri")
plt.tight_layout()
plt.show()

print("\n✔ Feature engineering + GridSearchCV tamamlandı.")
