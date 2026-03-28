# -----------------------------
# 1️⃣ Kütüphaneler
# -----------------------------
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.impute import SimpleImputer

# -----------------------------
# 2️⃣ Veriyi yükleme
# -----------------------------
# Dosya aynı klasördeyse sadece dosya adını yaz yeter
df = pd.read_excel("yumurta kalitesi kalite.xlsx")

# İlk 5 satır, bilgi ve eksik değer kontrolü
print(df.head())
print(df.info())
print(df.isnull().sum())

# num_imputer = SimpleImputer(strategy="median")
# cat_imputer = SimpleImputer(strategy="most_frequent")
#SimpleImputer  kullanarak eksik değerler dolduruldu bunu başka türlü de yapardık mesela 
# -----------------------------
# 3️⃣ Gereksiz sütunları silme
# -----------------------------
if "Unnamed: 27" in df.columns:
    df = df.drop(columns=["Unnamed: 27"])

print("Güncel sütunlar:", df.columns)

# -----------------------------
# 4️⃣ Özet istatistikler ve değer sayıları
# -----------------------------
print(df.describe())                 # Sayısal sütunlar için özet istatistikler
print(df['GRUP'].value_counts())     # GRUP sütunundaki kategoriler
print(df['Genotip'].value_counts())  # Genotip sütunundaki kategoriler

# -----------------------------
# 5️⃣ Kategorik sütunları belirleme
# -----------------------------
cat_cols = df.select_dtypes(include='object').columns
print("Kategorik sütunlar:", cat_cols)

# -----------------------------
# 6️⃣ Kategorik değişkenleri sayısallaştırma
# -----------------------------
# LabelEncoder sıralı veriler için mantıklı, burada sıralı değil
# Bu yüzden One-Hot Encoding kullandık
df = pd.get_dummies(df, columns=['Genotip', 'GRUP'], drop_first=True)
print(df.head())

# -----------------------------
# 7️⃣ Sayısal sütunları belirleme
# -----------------------------
num_cols = df.select_dtypes(include='number').columns
print("Sayısal sütunlar:", num_cols)

# -----------------------------
# 8️⃣ Sayısal değişkenler arası korelasyon
# -----------------------------
corr = df[num_cols].corr()
print("\nSayısal değişkenler korelasyon matrisi:")
print(corr)

# Görselleştirme
plt.figure(figsize=(12,9))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm")
plt.title("Sayısal Değişkenler Korelasyon Matrisi")
plt.show()

corr = df[num_cols].corr()

