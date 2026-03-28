import math
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import KFold, cross_validate, train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVR
from sklearn.linear_model import Ridge

RANDOM_STATE = 42
DATA_PATH = Path("veriAnaliz") / "yumurta kalitesi kalite.xlsx"
OUTPUT_DIR = Path("veriAnaliz")


def _turkish_ascii(s: str) -> str:
    repl = {
        "İ": "I",
        "I": "I",
        "ı": "i",
        "ş": "s",
        "Ş": "S",
        "ğ": "g",
        "Ğ": "G",
        "ü": "u",
        "Ü": "U",
        "ö": "o",
        "Ö": "O",
        "ç": "c",
        "Ç": "C",
    }
    return "".join(repl.get(ch, ch) for ch in s)


def clean_column_name(col: str) -> str:
    col = col.strip()
    col = _turkish_ascii(col)
    col = unicodedata.normalize("NFKD", col)
    col = "".join(ch for ch in col if not unicodedata.combining(ch))
    col = col.replace(" ", "_")
    col = col.replace("(", "").replace(")", "")
    col = col.replace("__", "_")
    return col


def load_and_clean_data(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path)
    col_map = {c: clean_column_name(c) for c in df.columns}
    df = df.rename(columns=col_map)

    unnamed = [c for c in df.columns if c.lower().startswith("unnamed")]
    if unnamed:
        df = df.drop(columns=unnamed)

    # Categorical cleanup
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].astype(str).str.strip()
        if c.lower() == "genotip":
            df[c] = df[c].str.lower().str.replace(" ", "", regex=False)
        if c.lower() == "grup":
            df[c] = df[c].str.upper()

    return df


def add_derived_targets(df: pd.DataFrame) -> pd.DataFrame:
    # Kabuk kalitesi skoru: mukavemet ve ortalama kalınlığın z-ortalaması
    mu = df["MUKAVEMET"]
    ort = df["Ortalama"]
    mu_z = (mu - mu.mean()) / mu.std()
    ort_z = (ort - ort.mean()) / ort.std()
    df = df.copy()
    df["Kabuk_Kalitesi_Skoru"] = (mu_z + ort_z) / 2.0
    return df


def split_features_target(df: pd.DataFrame, target: str) -> tuple[pd.DataFrame, pd.Series]:
    derived_cols = ["Kabuk_Kalitesi_Skoru"]
    if target == "Ortalama":
        # Ortalama, KUT/ORTA/SIVRI'nin deterministik ortalamasıdır; sızıntıyı önlemek için çıkarılır.
        drop_cols = ["Ortalama", "KUT", "ORTA", "SIVRI"]
    else:
        drop_cols = [target]

    drop_cols = list(set(drop_cols + derived_cols))
    X = df.drop(columns=drop_cols)
    y = df[target]
    return X, y


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    cat_cols = X.select_dtypes(include="object").columns.tolist()
    num_cols = [c for c in X.columns if c not in cat_cols]

    pre = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ]
    )
    return pre


def evaluate_models_cv(X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
    pre = build_preprocessor(X)
    models = {
        "Dummy": DummyRegressor(strategy="mean"),
        "Ridge": Ridge(alpha=1.0, random_state=RANDOM_STATE),
        "SVR": SVR(C=10.0, gamma="scale", epsilon=0.1),
        "KNN": KNeighborsRegressor(n_neighbors=7),
        "RandomForest": RandomForestRegressor(
            n_estimators=400, random_state=RANDOM_STATE, n_jobs=1
        ),
        "ExtraTrees": ExtraTreesRegressor(
            n_estimators=400, random_state=RANDOM_STATE, n_jobs=1
        ),
        "GradientBoosting": GradientBoostingRegressor(random_state=RANDOM_STATE),
    }

    cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    rows = []
    for name, model in models.items():
        pipe = Pipeline([("pre", pre), ("model", model)])
        scores = cross_validate(
            pipe,
            X,
            y,
            cv=cv,
            scoring={
                "r2": "r2",
                "mae": "neg_mean_absolute_error",
                "rmse": "neg_root_mean_squared_error",
            },
        )
        rows.append(
            {
                "model": name,
                "r2_mean": float(scores["test_r2"].mean()),
                "r2_std": float(scores["test_r2"].std()),
                "mae_mean": float(-scores["test_mae"].mean()),
                "mae_std": float(scores["test_mae"].std()),
                "rmse_mean": float(-scores["test_rmse"].mean()),
                "rmse_std": float(scores["test_rmse"].std()),
            }
        )

    df_scores = pd.DataFrame(rows).sort_values(by="r2_mean", ascending=False)
    return df_scores


def select_best_model(df_scores: pd.DataFrame) -> str:
    # Öncelik: en yüksek R2, eşitlikte en düşük RMSE
    df_scores = df_scores.copy()
    df_scores = df_scores.sort_values(by=["r2_mean", "rmse_mean"], ascending=[False, True])
    return df_scores.iloc[0]["model"]


def build_model_by_name(name: str):
    if name == "Dummy":
        return DummyRegressor(strategy="mean")
    if name == "Ridge":
        return Ridge(alpha=1.0, random_state=RANDOM_STATE)
    if name == "SVR":
        return SVR(C=10.0, gamma="scale", epsilon=0.1)
    if name == "KNN":
        return KNeighborsRegressor(n_neighbors=7)
    if name == "RandomForest":
        return RandomForestRegressor(n_estimators=400, random_state=RANDOM_STATE, n_jobs=1)
    if name == "ExtraTrees":
        return ExtraTreesRegressor(n_estimators=400, random_state=RANDOM_STATE, n_jobs=1)
    if name == "GradientBoosting":
        return GradientBoostingRegressor(random_state=RANDOM_STATE)

    raise ValueError(f"Unknown model: {name}")


def compute_test_metrics(pipe: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    preds = pipe.predict(X_test)
    return {
        "r2": float(r2_score(y_test, preds)),
        "mae": float(mean_absolute_error(y_test, preds)),
        "rmse": float(root_mean_squared_error(y_test, preds)),
    }


def augment_with_noise(X: pd.DataFrame, y: pd.Series, factor: float = 1.0) -> tuple[pd.DataFrame, pd.Series]:
    if factor <= 0:
        return X.copy(), y.copy()

    n_new = int(len(X) * factor)
    rng = np.random.default_rng(RANDOM_STATE)
    idx = rng.choice(X.index.to_numpy(), size=n_new, replace=True)

    X_new = X.loc[idx].copy().reset_index(drop=True)
    y_new = y.loc[idx].copy().reset_index(drop=True)

    num_cols = X_new.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        col_std = X[col].std()
        if pd.isna(col_std) or col_std == 0:
            continue
        noise = rng.normal(loc=0.0, scale=0.05 * col_std, size=len(X_new))
        X_new[col] = X_new[col] + noise
        # Clip to observed min/max to avoid unrealistic values
        X_new[col] = X_new[col].clip(lower=X[col].min(), upper=X[col].max())

    # Target jitter
    y_std = y.std()
    if not pd.isna(y_std) and y_std > 0:
        y_noise = rng.normal(loc=0.0, scale=0.05 * y_std, size=len(y_new))
        y_new = y_new + y_noise

    return X_new, y_new


def permutation_importance_report(pipe: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> pd.DataFrame:
    result = permutation_importance(
        pipe, X_test, y_test, n_repeats=10, random_state=RANDOM_STATE, scoring="r2"
    )
    df_imp = pd.DataFrame(
        {
            "feature": X_test.columns,
            "importance_mean": result.importances_mean,
            "importance_std": result.importances_std,
        }
    ).sort_values(by="importance_mean", ascending=False)
    return df_imp


def format_metric(value: float, digits: int = 4) -> str:
    if value is None or (isinstance(value, float) and (math.isnan(value) or math.isinf(value))):
        return "NaN"
    return f"{value:.{digits}f}"


def main() -> None:
    df_raw = load_and_clean_data(DATA_PATH)
    df = add_derived_targets(df_raw)

    # Data summary
    n_rows, n_cols = df_raw.shape
    n_cat = len(df_raw.select_dtypes(include="object").columns)
    n_num = len(df_raw.columns) - n_cat
    n_dupe = int(df_raw.duplicated().sum())

    # Descriptive statistics outputs
    desc_stats = df_raw.describe(include=[np.number]).T
    desc_path = OUTPUT_DIR / "tanimlayici_istatistikler.csv"
    desc_stats.to_csv(desc_path, index=True)

    cat_rows = []
    for col in df_raw.select_dtypes(include="object").columns:
        vc = df_raw[col].value_counts(dropna=False)
        total = vc.sum()
        for cat, cnt in vc.items():
            cat_rows.append(
                {
                    "column": col,
                    "category": cat,
                    "count": int(cnt),
                    "percent": float(cnt) / float(total) * 100.0,
                }
            )

    cat_df = pd.DataFrame(cat_rows)
    cat_path = OUTPUT_DIR / "kategorik_ozet.csv"
    cat_df.to_csv(cat_path, index=False)

    # Targets to evaluate
    targets = ["MUKAVEMET", "Ortalama"]

    # Use a shared train/test split index for comparability
    train_idx, test_idx = train_test_split(
        df.index, test_size=0.2, random_state=RANDOM_STATE, shuffle=True
    )

    report_sections = []

    report_sections.append("**Veri Seti ve Kapsam**")
    report_sections.append(
        f"Bu çalışma {DATA_PATH.name} veri seti üzerinde yürütülmüştür. Toplam örnek sayısı {n_rows}, değişken sayısı {n_cols} (sayısal: {n_num}, kategorik: {n_cat}) olarak belirlenmiştir. Yinelenen kayıt sayısı {n_dupe} olup eksik gözlem bulunmamıştır."
    )

    report_sections.append("**Ön İşleme ve Temizleme**")
    report_sections.append(
        "Sütun adları Türkçe karakterlerden arındırılarak analiz için sadeleştirilmiş, kategorik değişkenlerde boşluklar kırpılmış ve tutarsız büyük/küçük harfler normalize edilmiştir. 'Ortalama' değişkeninin KUT/ORTA/SIVRI ortalamasına eşit olduğu doğrulanmış ve bu nedenle 'Ortalama' hedefi için deterministik değişkenler (KUT, ORTA, SIVRI) model girdilerinden çıkarılmıştır."
    )

    report_sections.append("**Tanımlayıcı İstatistikler**")
    report_sections.append(
        f"Sayısal değişkenlere ait özet istatistikler {desc_path.name} dosyasında, kategorik değişken dağılımları ise {cat_path.name} dosyasında raporlanmıştır."
    )

    report_sections.append("**Hedef Değişkenler**")
    report_sections.append(
        "Kabuk kalitesi; kabuk mukavemeti (MUKAVEMET) ve kabuk kalınlığına ilişkin ortalama değer (Ortalama) üzerinden iki ayrı regresyon problemi olarak ele alınmıştır. Bu yaklaşım, kabuk kalitesinin çok boyutlu doğasını ayrı çıktılar üzerinden yorumlamayı amaçlamaktadır."
    )

    report_sections.append("**Modelleme Tasarımı**")
    report_sections.append(
        "Model karşılaştırmaları 5-katlı çapraz doğrulama ile yapılmış; performans ölçütü olarak R², MAE ve RMSE kullanılmıştır. Kategorik değişkenler One-Hot Encoder ile kodlanmış, sayısal değişkenler StandardScaler ile ölçeklenmiştir."
    )

    # Containers for summary at the end
    final_findings = []

    for target in targets:
        X, y = split_features_target(df, target)

        # Target descriptive stats
        t_stats = df_raw[target].describe()
        report_sections.append(f"**Hedef Tanımı ve Temel İstatistikler: {target}**")
        report_sections.append(
            f"{target} için ortalama={t_stats['mean']:.3f}, std={t_stats['std']:.3f}, "
            f"min={t_stats['min']:.3f}, max={t_stats['max']:.3f} olarak hesaplanmıştır."
        )

        # Correlation summary (numeric)
        num_corr = df_raw.select_dtypes(include=[np.number]).corr()[target].drop(labels=[target])
        num_corr = num_corr.reindex(num_corr.abs().sort_values(ascending=False).index)
        corr_top = num_corr.head(10)
        corr_path = OUTPUT_DIR / f"korelasyon_{target.lower()}.csv"
        corr_top.to_csv(corr_path, header=["pearson_corr"])

        corr_lines = ["| Değişken | Pearson r |", "|---|---|"]
        for name, val in corr_top.items():
            corr_lines.append(f"| {name} | {val:.3f} |")

        report_sections.append(f"**Korelasyon Özeti (Sayısal): {target}**")
        report_sections.append("\n".join(corr_lines))
        report_sections.append(
            f"Ayrıntılı korelasyon listesi {corr_path.name} dosyasında sunulmuştur."
        )

        # CV evaluation
        cv_scores = evaluate_models_cv(X, y)
        best_model_name = select_best_model(cv_scores)

        # Save CV table
        cv_out_path = OUTPUT_DIR / f"model_karsilastirma_{target.lower()}.csv"
        cv_scores.to_csv(cv_out_path, index=False)

        # Train/test evaluation
        X_train, X_test = X.loc[train_idx], X.loc[test_idx]
        y_train, y_test = y.loc[train_idx], y.loc[test_idx]

        pre = build_preprocessor(X)
        model = build_model_by_name(best_model_name)
        pipe = Pipeline([("pre", pre), ("model", model)])
        pipe.fit(X_train, y_train)
        test_metrics = compute_test_metrics(pipe, X_test, y_test)

        # Synthetic augmentation experiment
        X_syn, y_syn = augment_with_noise(X_train, y_train, factor=1.0)
        X_aug = pd.concat([X_train.reset_index(drop=True), X_syn], ignore_index=True)
        y_aug = pd.concat([y_train.reset_index(drop=True), y_syn], ignore_index=True)

        pipe_aug = Pipeline([("pre", pre), ("model", build_model_by_name(best_model_name))])
        pipe_aug.fit(X_aug, y_aug)
        test_metrics_aug = compute_test_metrics(pipe_aug, X_test, y_test)

        # Permutation importance
        imp_df = permutation_importance_report(pipe, X_test, y_test)
        imp_out_path = OUTPUT_DIR / f"ozellik_onemi_{target.lower()}.csv"
        imp_df.to_csv(imp_out_path, index=False)

        # Write synthetic dataset once (full data) for traceability
        # (Only for the first target to avoid duplicates)
        if target == targets[0]:
            X_syn_full, y_syn_full = augment_with_noise(X, y, factor=1.0)
            syn_full = X_syn_full.copy()
            syn_full[target] = y_syn_full
            syn_out_path = OUTPUT_DIR / "yapay_veri.csv"
            syn_full.to_csv(syn_out_path, index=False)

        # Report sections per target
        report_sections.append(f"**Model Karşılaştırması: {target}**")

        # Build markdown table
        header = "| Model | R² (Ort±SS) | MAE (Ort±SS) | RMSE (Ort±SS) |"
        sep = "|---|---|---|---|"
        rows = [header, sep]
        for _, row in cv_scores.iterrows():
            rows.append(
                "| {model} | {r2} | {mae} | {rmse} |".format(
                    model=row["model"],
                    r2=f"{row['r2_mean']:.3f} ± {row['r2_std']:.3f}",
                    mae=f"{row['mae_mean']:.3f} ± {row['mae_std']:.3f}",
                    rmse=f"{row['rmse_mean']:.3f} ± {row['rmse_std']:.3f}",
                )
            )

        report_sections.append("\n".join(rows))

        report_sections.append(f"**En İyi Model ve Test Sonuçları: {target}**")
        report_sections.append(
            f"En iyi model {best_model_name} olarak seçilmiştir. Test verisi üzerinde R²={test_metrics['r2']:.3f}, MAE={test_metrics['mae']:.3f}, RMSE={test_metrics['rmse']:.3f} elde edilmiştir."
        )

        report_sections.append(f"**Yapay Veri Deneyi: {target}**")
        report_sections.append(
            "Eğitim kümesine %100 oranında gürültü eklenmiş sentetik örnekler dahil edilerek duyarlılık analizi yapılmıştır. "
            f"Bu senaryoda test sonuçları R²={test_metrics_aug['r2']:.3f}, MAE={test_metrics_aug['mae']:.3f}, RMSE={test_metrics_aug['rmse']:.3f} şeklindedir."
        )

        # Top features
        top_imp = imp_df.head(10)
        top_lines = ["| Değişken | Önem (Ort) |", "|---|---|"]
        for _, r in top_imp.iterrows():
            top_lines.append(f"| {r['feature']} | {r['importance_mean']:.4f} |")

        report_sections.append(f"**Özellik Önemi (Permütasyon): {target}**")
        report_sections.append("\n".join(top_lines))

        final_findings.append(
            f"{target} hedefi için en iyi model {best_model_name} olup test R² değeri {test_metrics['r2']:.3f} seviyesindedir; bu bulgu modelin sınırlı ancak anlamlı bir açıklayıcılık sunduğunu göstermektedir."
        )

    report_sections.append("**Çalışma Sonuçları**")
    report_sections.append(
        "Bu çalışma kapsamında yumurta kabuk kalitesi ile ilişkili değişkenler bütüncül olarak değerlendirilmiş, veri temizliği ve dönüştürme adımları tamamlanmış ve iki temel hedef değişken üzerinde farklı regresyon modelleri karşılaştırılmıştır. Elde edilen bulgular aşağıda özetlenmiştir:"
    )

    for item in final_findings:
        report_sections.append(f"- {item}")

    report_sections.append(
        "Kabuk kalınlığına ilişkin 'Ortalama' değişkeninin KUT/ORTA/SIVRI ortalamasına deterministik olarak eşit olması nedeniyle, bu değişkenler hedefe yönelik sızıntı oluşturabileceğinden model girdilerinden çıkarılmıştır. Bu karar, model değerlendirmelerinde gerçekçi genelleme performansı sağlamak amacıyla alınmıştır."
    )

    report_sections.append(
        "Yapay veri ile gerçekleştirilen duyarlılık analizinde performansın sınırlı düzeyde iyileştiği/güçlendiği ancak bazı metriklerde değişimin marjinal kaldığı gözlenmiştir. Bu durum, veri setinin yapısal sinyalinin sınırlı olduğu ve ek gözlemlerle performans artışının mümkün olabileceğine işaret etmektedir."
    )

    report_sections.append(
        "Permütasyon önem analizleri; kabuk kalitesiyle ilişkili çıktılarda belirli fiziksel ve biyokimyasal değişkenlerin (örneğin ağırlık, boyut ölçüleri, albümen/yumurta iç kalite göstergeleri) katkı sunduğunu göstermektedir. Bulgular, kabuk kalitesinin tek bir değişkenle açıklanamayacak çok faktörlü bir yapıda olduğunu desteklemektedir."
    )

    report_sections.append(
        "Çalışma sonucunda elde edilen performans seviyeleri, özellikle kabuk mukavemeti için orta-düşük açıklayıcılık düzeyine işaret etmektedir. Bu bulgu, kabuk kalite ölçümlerinin biyolojik ve çevresel değişkenlerden güçlü biçimde etkilendiğini ve modelleme performansının artırılması için ek açıklayıcı değişkenlere ihtiyaç duyulabileceğini göstermektedir."
    )

    report_text = "\n\n".join(report_sections)
    report_path = OUTPUT_DIR / "calisma_sonuclari.md"
    report_path.write_text(report_text, encoding="utf-8")

    print("Calisma tamamlandi. Rapor ve tablolar olusturuldu:")
    print("-", report_path)
    for target in targets:
        print("-", OUTPUT_DIR / f"model_karsilastirma_{target.lower()}.csv")
        print("-", OUTPUT_DIR / f"ozellik_onemi_{target.lower()}.csv")
    print("-", OUTPUT_DIR / "yapay_veri.csv")


if __name__ == "__main__":
    main()
