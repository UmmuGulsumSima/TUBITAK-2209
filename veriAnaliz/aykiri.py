# aykiri.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------------------------------------
# 1. VERİ SETİNİ OKU
# -----------------------------------------------------------
df = pd.read_excel("yumurta kalitesi kalite.xlsx") # buraya senin dosya adını yaz

# -----------------------------------------------------------
# 2. "Ortalama" kolonunu seç
# -----------------------------------------------------------
ortalama = df["Ortalama"]

# -----------------------------------------------------------
# 3. IQR YÖNTEMİYLE AYKIRI DEĞER TESPİTİ
#    IQR = Q3 - Q1
#    outlier = < Q1 - 1.5*IQR  veya  > Q3 + 1.5*IQR
# -----------------------------------------------------------
Q1 = ortalama.quantile(0.25)  # %25'lik dilim
Q3 = ortalama.quantile(0.75)  # %75'lik dilim
IQR = Q3 - Q1

alt_sinir = Q1 - 1.5 * IQR
ust_sinir = Q3 + 1.5 * IQR

# Aykırı satırları bul
aykiri_satirlar = df[(ortalama < alt_sinir) | (ortalama > ust_sinir)]

print("\n===== AYKIRI DEĞERLERE SAHİP SATIRLAR =====")
print(aykiri_satirlar)   # Bu satırlar üzerine analiz yapabilirsin

# -----------------------------------------------------------
# 4. GÖRSELLEŞTİRME (Histogram + Boxplot)
# -----------------------------------------------------------

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
sns.histplot(ortalama, kde=True)  # KDE çizgisi dağılımın şeklini gösterir
plt.title("Ortalama Kolonu Histogram + KDE")

plt.subplot(1, 2, 2)
sns.boxplot(x=ortalama)
plt.title("Ortalama Kolonu Boxplot (Aykırı Değer Göstergesi)")

plt.tight_layout()
plt.show()

print("\n🔎 Aykırı satırların istatistiksel özeti:")
print(aykiri_satirlar.describe())

# -----------------------------------------------------------
# 6. AYKIRI VS NORMAL KARŞILAŞTIRMA
# -----------------------------------------------------------
df["AykiriMi"] = (df["Ortalama"] < alt_sinir) | (df["Ortalama"] > ust_sinir)

kolonlar = ["AĞIRLIK", "Sarı İndeksi", "SARI SKORU", "PH"]

for col in kolonlar:
    plt.figure(figsize=(6,4))
    sns.boxplot(x="AykiriMi", y=col, data=df)
    plt.title(f"Aykırı ve Normal Gruplarda {col}")
    plt.show()
