import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

# === 1. Загружаем данные ===
transactions = pd.read_csv("/Users/dana/Downloads/test/st/transactions.csv")
transactions.columns = [c.strip().lower().replace(" ", "_") for c in transactions.columns]
transactions["date"] = pd.to_datetime(transactions["date"], errors="coerce")
transactions["category"] = transactions["category"].astype(str).str.lower().str.strip()

now = pd.Timestamp(datetime(2025, 10, 18))

# === 2. RFM ===
rfm = (
    transactions.groupby("user_id")
    .agg(
        last_tx=("date", "max"),
        first_tx=("date", "min"),
        F=("transaction_id", "count"),
        M=("amount", "sum")
    )
    .reset_index()
)
rfm["R"] = (now - rfm["last_tx"]).dt.days.fillna(9999)
rfm["activity_span"] = (rfm["last_tx"] - rfm["first_tx"]).dt.days.fillna(0)
rfm.drop(columns=["first_tx", "last_tx"], inplace=True)

# === 3. Нормализация по сумме транзакций пользователя ===
user_totals = transactions.groupby("user_id")["amount"].sum()
transactions = transactions.merge(user_totals, on="user_id", suffixes=("", "_user_total"))
transactions["amount_share"] = transactions["amount"] / transactions["amount_user_total"]

# === 4. Тематические фичи по сумме расходов ===
def category_share(cat_list):
    mask = transactions["category"].isin(cat_list)
    return transactions[mask].groupby("user_id")["amount_share"].sum().fillna(0)

features = rfm.copy()
features["Z_charity"] = category_share(["charity", "donation", "zakat", "waqf"])
features["Edu"] = category_share(["education"])
features["Biz"] = category_share(["business"])
features["Prop"] = category_share(["property", "имущество"])
features["Health"] = category_share(["healthcare"])
features["Deposit"] = category_share(["deposit", "card"])
features.fillna(0, inplace=True)

# === 5. Динамическая активность ===
r_thresh = features["R"].quantile(0.8)
f_thresh = features["F"].quantile(0.2)

def classify_activity(row):
    if row["R"] > r_thresh and row["F"] < f_thresh:
        return "Засыпающий"
    elif row["R"] < features["R"].quantile(0.3):
        return "Просыпающийся"
    else:
        return "Активный"

features["activity_stage"] = features.apply(classify_activity, axis=1)

# === 6. Определение целей (goals) ===
def detect_goal(user_tx):
    cats = user_tx["category"].value_counts(normalize=True)
    if cats.get("property", 0) + cats.get("имущество", 0) > 0.35:
        return "Покупка недвижимости"
    elif cats.get("auto", 0) > 0.3:
        return "Покупка автомобиля"
    elif cats.get("education", 0) > 0.3:
        return "Инвестиции в образование"
    elif cats.get("business", 0) > 0.3:
        return "Развитие бизнеса"
    elif cats.get("charity", 0) + cats.get("zakat", 0) > 0.2:
        return "Благотворительность"
    elif cats.get("deposit", 0) + cats.get("card", 0) > 0.4:
        return "Накопление"
    elif cats.get("healthcare", 0) > 0.25:
        return "Медицинская защита"
    else:
        return "Общие расходы"

goal_map = transactions.groupby("user_id", group_keys=False).apply(detect_goal).reset_index()
goal_map.columns = ["user_id", "goal"]
features = features.merge(goal_map, on="user_id", how="left")

# === 7. Масштабирование и PCA ===
scaler = StandardScaler()
scaled = scaler.fit_transform(features[["R", "F", "M", "Z_charity", "Edu", "Biz", "Prop", "Health", "Deposit"]])

pca = PCA(n_components=0.95, random_state=42)
reduced = pca.fit_transform(scaled)

# === 8. Gaussian Mixture ===
gmm = GaussianMixture(n_components=8, covariance_type="full", random_state=42)
features["cluster"] = gmm.fit_predict(reduced)

# === 9. Динамические пороги для авто-лейблов ===
def above_dynamic_threshold(row, col):
    return row[col] > features[col].quantile(0.75)

def label_cluster(row):
    if above_dynamic_threshold(row, "Z_charity"):
        return "Благотворительный лидер"
    elif above_dynamic_threshold(row, "Edu"):
        return "Развивающийся ученик"
    elif above_dynamic_threshold(row, "Biz"):
        return "Бизнес-инвестор"
    elif above_dynamic_threshold(row, "Prop"):
        return "Семейный строитель"
    elif above_dynamic_threshold(row, "Health"):
        return "Заботящийся о здоровье"
    elif above_dynamic_threshold(row, "Deposit"):
        return "Финансово стратегический"
    elif row["F"] > features["F"].quantile(0.8):
        return "Сверхактивный пользователь"
    elif row["R"] > features["R"].quantile(0.8):
        return "Засыпающий"
    else:
        return "Сбалансированный клиент"

features["segment"] = features.apply(label_cluster, axis=1)

# === 10. Совмещение активности и сегмента ===
features.loc[features["activity_stage"] == "Засыпающий", "segment"] = "Засыпающий"
features.loc[features["activity_stage"] == "Просыпающийся", "segment"] = "Просыпающийся"

# === 11. Сохранение и визуализация ===
features.to_csv("smart_segments_final.csv", index=False, encoding="utf-8-sig")

print("✅ Умная кластеризация завершена!")
print(features[["user_id", "segment", "goal", "activity_stage"]].head(20))

# === 12. Визуализация распределения сегментов ===
plt.figure(figsize=(10,5))
sns.countplot(x="segment", data=features, order=features["segment"].value_counts().index)
plt.xticks(rotation=45)
plt.title("📊 Распределение сегментов пользователей")
plt.tight_layout()
plt.show()
# ...existing code...

# === 11.5. Собираем обогащённый датасет транзакций (каждая транзакция + фичи пользователя) ===
enrich_cols = [
    "user_id", "segment", "goal", "activity_stage", "cluster",
    "R", "F", "M", "Z_charity", "Edu", "Biz", "Prop", "Health", "Deposit"
]
# убедимся, что нужные столбцы присутствуют в features
enrich_cols = [c for c in enrich_cols if c in features.columns]

enriched_transactions = transactions.merge(
    features[enrich_cols],
    on="user_id",
    how="left",
    validate="m:1"  # many transactions -> one user row
)

# сохраняем
enriched_transactions.to_csv("enriched_transactions.csv", index=False, encoding="utf-8-sig")
# (опционально) сохраняем user-level датасет отдельно
features.to_csv("user_features.csv", index=False, encoding="utf-8-sig")

print("✅ Enriched transactions saved to enriched_transactions.csv")
# ...existing code...
