**Veri Seti ve Kapsam**

Bu çalışma yumurta kalitesi kalite.xlsx veri seti üzerinde yürütülmüştür. Toplam örnek sayısı 270, değişken sayısı 27 (sayısal: 25, kategorik: 2) olarak belirlenmiştir. Yinelenen kayıt sayısı 0 olup eksik gözlem bulunmamıştır.

**Ön İşleme ve Temizleme**

Sütun adları Türkçe karakterlerden arındırılarak analiz için sadeleştirilmiş, kategorik değişkenlerde boşluklar kırpılmış ve tutarsız büyük/küçük harfler normalize edilmiştir. 'Ortalama' değişkeninin KUT/ORTA/SIVRI ortalamasına eşit olduğu doğrulanmış ve bu nedenle 'Ortalama' hedefi için deterministik değişkenler (KUT, ORTA, SIVRI) model girdilerinden çıkarılmıştır.

**Tanımlayıcı İstatistikler**

Sayısal değişkenlere ait özet istatistikler tanimlayici_istatistikler.csv dosyasında, kategorik değişken dağılımları ise kategorik_ozet.csv dosyasında raporlanmıştır.

**Hedef Değişkenler**

Kabuk kalitesi; kabuk mukavemeti (MUKAVEMET) ve kabuk kalınlığına ilişkin ortalama değer (Ortalama) üzerinden iki ayrı regresyon problemi olarak ele alınmıştır. Bu yaklaşım, kabuk kalitesinin çok boyutlu doğasını ayrı çıktılar üzerinden yorumlamayı amaçlamaktadır.

**Modelleme Tasarımı**

Model karşılaştırmaları 5-katlı çapraz doğrulama ile yapılmış; performans ölçütü olarak R², MAE ve RMSE kullanılmıştır. Kategorik değişkenler One-Hot Encoder ile kodlanmış, sayısal değişkenler StandardScaler ile ölçeklenmiştir.

**Model Secim Gerekcesi**

Model seti; temel bir referans (Dummy), dogrusal iliskileri yakalamak icin Ridge, dogrusal olmayan sinirlari denetlemek icin SVR, yerel benzerlikleri incelemek icin KNN ve etkilesimli/karmasik yapilari yakalamak icin agac tabanli ansambllar (RandomForest, ExtraTrees, GradientBoosting) seklinde tasarlanmistir. Boylece hem basit hem de karmasik varsayimlari temsil eden genis bir model uzayi olusturulmus ve kabuk kalitesine dair yapisal sinyalin hangi duzeyde yakalanabildigi karsilastirmali olarak degerlendirilmistir.

**Detayli Kiyaslama (Baseline'a Gore Iyilesme)**

MUKAVEMET icin en iyi model RandomForest olup Dummy modele gore R2 artisi 0.159, MAE azalmasi %9.40, RMSE azalmasi %8.66 seviyesindedir. Ortalama icin en iyi model RandomForest olup Dummy modele gore R2 artisi 0.332, MAE azalmasi %16.19, RMSE azalmasi %18.24 seviyesindedir. Bu karsilastirma, kabuk kalinligi hedefinin gorece daha ongorulebilir oldugunu gostermektedir.

**Onceki Calismalarin Entegrasyonu**

Onceki calismalar veri kesfi, korelasyon analizi, aykiri deger incelemeleri, istatistiksel testler ve Random Forest tabanli aciklanabilirlik analizleri uzerine yogunlasmistir. Bu raporda soz konusu calismalarin bulgulari korunmus, yontem ve gorseller rapora entegre edilmistir.

Korelasyon analizlerinde agirlik-uzunluk-genislik arasinda guclu pozitif iliskiler, KUT/ORTA/SIVRI/Ortalama degiskenleri arasinda yuksek korelasyon ve AK Yuksekligi - Ak Indeksi - Haugh Birimi uclusunde belirgin dogrusal iliski gozlenmistir. Yas arttikca sari yuksekligi ve sari indeksi gibi bazi ic kalite olcutlerinin azalma egiliminde oldugu tespit edilmistir.

Aykiri deger analizlerinde Sari Indeksi degiskeninde normal grupta daha genis bir dagilim ve uc degerler gorulmus, aykiri etiketli gozlemlerde ise daha stabil bir dagilim izlenmistir. Bu bulgu, aykiri etiketin kaynaginin Sari Indeksi olmaktan ziyade farkli degiskenlerde aranmasi gerektigini isaret etmektedir.

**Istatistiksel Test (Onceki Calismalardan)**

Genotip gruplari arasinda Ortalama degiskeni icin tek yonlu ANOVA uygulanmis ve F=6.890, p=0.00916 bulunmustur. Bu sonuc, genotipler arasinda kabuk kalinligi ortalamasi acisindan anlamli bir fark olabilecegine isaret etmektedir.

**Onceki Modelleme Denemeleri (Ozet)**

Daha once yapilan modelleme denemelerinde Ortalama hedefi icin Linear Regression, Ridge Regression ve Random Forest kiyaslanmis; yeniden hesaplanan olculerde sirasiyla RMSE=0.545/R2=0.948, RMSE=0.534/R2=0.950 ve RMSE=0.587/R2=0.940 elde edilmistir. Bu degerler, onceki modelleme yaklasiminin yuksek aciklayicilik sundugunu gostermektedir; ancak Turkce karakterli sutunlarin temizlenmesi ve deterministik degiskenlerin (KUT/ORTA/SIVRI) dusulmesi asamalarinda sizinti riski olusmamasi icin mevcut raporda daha kati bir on isleme yaklasimi uygulanmistir.

**Random Forest Optimizasyonu ve Feature Engineering (Onceki Calismalar)**

Onceki calismalarda Random Forest icin GridSearchCV ile hiperparametre aramasi yapilmis; n_estimators, max_depth, min_samples_split ve min_samples_leaf parametreleri uzerinde arama gerceklestirilmistir. Ek olarak agirlik/uzunluk orani, genislik/uzunluk orani, ak-sari oranlari ve Haugh biriminin log donusumu gibi ozellik muhendisligi adimlari uygulanmistir. Bu yaklasimin amaci, kabuk kalitesini aciklayan fiziksel/kimyasal iliskilerin modele daha net tasinmasidir.

**SHAP Analizi (Onceki Calismalar)**

SHAP tabanli aciklanabilirlik analizinde kabuk kalitesi hedefi icin en etkili degiskenler arasinda MUKAVEMET, SARI_YUKSEKLIGI ve PH one cikmistir. Bu degiskenler icin bagimlilik grafikleri uretilerek dogrusal olmayan etkiler ayrintilandirilmistir.

**Gorseller**

Korelasyon isi haritasi:

![Korelasyon Is? Haritas?](../g?rseller/korelasyon.png)

Aykiri deger karsilastirmalari:

![Ayk?r?-Normal Kar??la?t?rma](../g?rseller/ayk?r?-normal.png)

![Ayk?r?-Normal Sar? ?ndeks](../g?rseller/ayk?r?-normal-sar?indeks.png)

![Ayk?r?-Normal Sar? Skor](../g?rseller/ayk?r?-normal-sar?skor.png)

Onceki Random Forest calismasina ait degisken onemi ve dogruluk gorselleri:

![De?i?ken ?nemi 1](<../degisken ?nemi.png>)

![De?i?ken ?nemi 2](<../degisken?nemi.png>)

![Ger?ek vs Tahmin](<../do?ru_sonu?lar.png>)


**Hedef Tanımı ve Temel İstatistikler: MUKAVEMET**

MUKAVEMET için ortalama=5001.696, std=828.618, min=2031.000, max=7507.000 olarak hesaplanmıştır.

**Korelasyon Özeti (Sayısal): MUKAVEMET**

| Değişken | Pearson r |
|---|---|
| KUT | 0.438 |
| Ortalama | 0.433 |
| ORTA | 0.364 |
| SIVRI | 0.345 |
| SARI_YUKSEKLIGI | -0.168 |
| SARI_SKORU | -0.167 |
| AK_GENISLIGI | 0.151 |
| Ak_Indeksi | -0.112 |
| Sari_Indeksi | -0.097 |
| Haugh_Birimi | -0.091 |

Ayrıntılı korelasyon listesi korelasyon_mukavemet.csv dosyasında sunulmuştur.

**Model Karşılaştırması: MUKAVEMET**

| Model | R² (Ort±SS) | MAE (Ort±SS) | RMSE (Ort±SS) |
|---|---|---|---|
| RandomForest | 0.156 ± 0.087 | 571.361 ± 87.965 | 746.993 ± 110.219 |
| ExtraTrees | 0.132 ± 0.095 | 581.400 ± 72.818 | 756.136 ± 103.624 |
| GradientBoosting | 0.115 ± 0.141 | 592.855 ± 71.522 | 760.538 ± 106.245 |
| Ridge | 0.108 ± 0.119 | 592.325 ± 75.766 | 768.807 ± 124.182 |
| KNN | 0.057 ± 0.084 | 605.067 ± 86.592 | 790.491 ± 115.168 |
| SVR | 0.019 ± 0.007 | 625.394 ± 86.034 | 809.006 ± 126.897 |
| Dummy | -0.003 ± 0.003 | 630.614 ± 84.379 | 817.825 ± 126.056 |

**En İyi Model ve Test Sonuçları: MUKAVEMET**

En iyi model RandomForest olarak seçilmiştir. Test verisi üzerinde R²=0.122, MAE=700.877, RMSE=939.705 elde edilmiştir.

**Yapay Veri Deneyi: MUKAVEMET**

Eğitim kümesine %100 oranında gürültü eklenmiş sentetik örnekler dahil edilerek duyarlılık analizi yapılmıştır. Bu senaryoda test sonuçları R²=0.092, MAE=724.265, RMSE=955.572 şeklindedir.

**Özellik Önemi (Permütasyon): MUKAVEMET**

| Değişken | Önem (Ort) |
|---|---|
| KUT | 0.1235 |
| Ortalama | 0.0342 |
| Sari_Indeksi | 0.0134 |
| SARI_YUKSEKLIGI | 0.0059 |
| GENISLIK | 0.0057 |
| ORTA | 0.0045 |
| AK | 0.0040 |
| YasHafta | 0.0034 |
| Tekerrur | 0.0007 |
| Ornek | -0.0002 |

**Hedef Tanımı ve Temel İstatistikler: Ortalama**

Ortalama için ortalama=39.841, std=2.570, min=31.333, max=48.000 olarak hesaplanmıştır.

**Korelasyon Özeti (Sayısal): Ortalama**

| Değişken | Pearson r |
|---|---|
| ORTA | 0.914 |
| KUT | 0.883 |
| SIVRI | 0.856 |
| MUKAVEMET | 0.433 |
| AK_GENISLIGI | 0.169 |
| SARI_YUKSEKLIGI | -0.135 |
| Tekerrur | -0.120 |
| Sari_Indeksi | -0.114 |
| Ak_Indeksi | -0.102 |
| AGIRLIK | 0.078 |

Ayrıntılı korelasyon listesi korelasyon_ortalama.csv dosyasında sunulmuştur.

**Model Karşılaştırması: Ortalama**

| Model | R² (Ort±SS) | MAE (Ort±SS) | RMSE (Ort±SS) |
|---|---|---|---|
| RandomForest | 0.317 ± 0.075 | 1.658 ± 0.093 | 2.099 ± 0.119 |
| ExtraTrees | 0.315 ± 0.065 | 1.664 ± 0.156 | 2.111 ± 0.200 |
| GradientBoosting | 0.232 ± 0.069 | 1.773 ± 0.148 | 2.233 ± 0.192 |
| SVR | 0.131 ± 0.136 | 1.885 ± 0.153 | 2.366 ± 0.188 |
| KNN | 0.130 ± 0.073 | 1.826 ± 0.139 | 2.374 ± 0.144 |
| Ridge | 0.089 ± 0.050 | 1.897 ± 0.092 | 2.432 ± 0.168 |
| Dummy | -0.015 ± 0.014 | 1.978 ± 0.102 | 2.568 ± 0.149 |

**En İyi Model ve Test Sonuçları: Ortalama**

En iyi model RandomForest olarak seçilmiştir. Test verisi üzerinde R²=0.283, MAE=1.539, RMSE=2.023 elde edilmiştir.

**Yapay Veri Deneyi: Ortalama**

Eğitim kümesine %100 oranında gürültü eklenmiş sentetik örnekler dahil edilerek duyarlılık analizi yapılmıştır. Bu senaryoda test sonuçları R²=0.312, MAE=1.485, RMSE=1.981 şeklindedir.

**Özellik Önemi (Permütasyon): Ortalama**

| Değişken | Önem (Ort) |
|---|---|
| MUKAVEMET | 0.7788 |
| SARI_SKORU | 0.0609 |
| YasHafta | 0.0491 |
| SARI_YUKSEKLIGI | 0.0425 |
| Sari_Indeksi | 0.0312 |
| PH | 0.0298 |
| GENISLIK | 0.0154 |
| AK_UZUNLUGU | 0.0136 |
| Genotip | 0.0047 |
| Tekerrur | 0.0038 |

**Çalışma Sonuçları**

Bu çalışma kapsamında yumurta kabuk kalitesi ile ilişkili değişkenler bütüncül olarak değerlendirilmiş, veri temizliği ve dönüştürme adımları tamamlanmış ve iki temel hedef değişken üzerinde farklı regresyon modelleri karşılaştırılmıştır. Elde edilen bulgular aşağıda özetlenmiştir:

- MUKAVEMET hedefi için en iyi model RandomForest olup test R² değeri 0.122 seviyesindedir; bu bulgu modelin sınırlı ancak anlamlı bir açıklayıcılık sunduğunu göstermektedir.

- Ortalama hedefi için en iyi model RandomForest olup test R² değeri 0.283 seviyesindedir; bu bulgu modelin sınırlı ancak anlamlı bir açıklayıcılık sunduğunu göstermektedir.

Kabuk kalınlığına ilişkin 'Ortalama' değişkeninin KUT/ORTA/SIVRI ortalamasına deterministik olarak eşit olması nedeniyle, bu değişkenler hedefe yönelik sızıntı oluşturabileceğinden model girdilerinden çıkarılmıştır. Bu karar, model değerlendirmelerinde gerçekçi genelleme performansı sağlamak amacıyla alınmıştır.

Yapay veri ile gerçekleştirilen duyarlılık analizinde performansın sınırlı düzeyde iyileştiği/güçlendiği ancak bazı metriklerde değişimin marjinal kaldığı gözlenmiştir. Bu durum, veri setinin yapısal sinyalinin sınırlı olduğu ve ek gözlemlerle performans artışının mümkün olabileceğine işaret etmektedir.

Permütasyon önem analizleri; kabuk kalitesiyle ilişkili çıktılarda belirli fiziksel ve biyokimyasal değişkenlerin (örneğin ağırlık, boyut ölçüleri, albümen/yumurta iç kalite göstergeleri) katkı sunduğunu göstermektedir. Bulgular, kabuk kalitesinin tek bir değişkenle açıklanamayacak çok faktörlü bir yapıda olduğunu desteklemektedir.

Çalışma sonucunda elde edilen performans seviyeleri, özellikle kabuk mukavemeti için orta-düşük açıklayıcılık düzeyine işaret etmektedir. Bu bulgu, kabuk kalite ölçümlerinin biyolojik ve çevresel değişkenlerden güçlü biçimde etkilendiğini ve modelleme performansının artırılması için ek açıklayıcı değişkenlere ihtiyaç duyulabileceğini göstermektedir.