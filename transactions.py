import pandas as pd
import random
from datetime import datetime, timedelta

# количество пользователей и диапазон транзакций на каждого
user_ids = list(range(1, 101))  # 100 клиентов
min_tx_per_user = 50
max_tx_per_user = 300

# категории по типу продуктов
categories = {
    201: ("Property", "Mortgage payment"),
    202: ("Auto", "Auto loan installment"),
    203: ("Business", "Business credit payment"),
    204: ("Personal needs", "Consumer loan payment"),
    205: ("Education", "Student loan payment"),
    206: ("Deposit", "Account top-up"),
    207: ("Card", "Card replenishment"),
    208: ("Healthcare", "Insurance payment"),
    999: ("Charity", random.choice(["Donation", "Zakat payment", "Waqf support"]))
}

product_ids = list(categories.keys())
emotion_types = ["Rational", "Routine", "Planned"]
payment_types = ["Card", "Transfer", "Cash"]

start_date = datetime(2023, 1, 1)
end_date = datetime(2025, 10, 18)

def random_date(start, end):
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

transactions = []
tx_id = 1

for user_id in user_ids:
    num_tx = random.randint(min_tx_per_user, max_tx_per_user)
    for _ in range(num_tx):
        # вероятность благотворительной транзакции
        if random.random() < 0.08:
            product_id = 999
            category, subcategory = categories[999]
            amount = round(random.uniform(5_000, 200_000), 2)
        else:
            product_id = random.choice(list(categories.keys())[:-1])  # без charity
            category, subcategory = categories[product_id]
            amount = round(random.uniform(20_000, 5_000_000), 2)

        necessity_level = random.randint(3, 5)
        emotion_type = random.choice(emotion_types)
        payment_type = random.choice(payment_types)
        date = random_date(start_date, end_date)

        transactions.append([
            tx_id,
            user_id,
            date.date(),
            category,
            subcategory,
            amount,
            necessity_level,
            emotion_type,
            payment_type,
            None if product_id == 999 else product_id
        ])

        tx_id += 1

columns = [
    "transaction_id",
    "user_id",
    "date",
    "category",
    "subcategory",
    "amount",
    "necessity_level",
    "emotion_type",
    "payment_type",
    "product_id"
]

df = pd.DataFrame(transactions, columns=columns)
df.to_csv("transactions.csv", index=False, encoding="utf-8-sig")

print("✅ Файл 'transactions.csv' успешно создан!")
print(f"Всего транзакций: {len(df)}")
print("Пример данных:")
print(df.head(20))
print("\nКоличество транзакций на каждого пользователя:")
print(df['user_id'].value_counts().sort_index().head(10))
