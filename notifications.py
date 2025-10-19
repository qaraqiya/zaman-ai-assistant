import pandas as pd
from datetime import datetime
import random

# Пример транзакций (можно читать из CSV)
transactions = pd.read_csv("/Users/dana/Downloads/test/st/transactions.csv")
transactions["date"] = pd.to_datetime(transactions["date"])
print(transactions['category'].unique())
# Категории по исламским целям
GOALS = {
    "education": ["Education"],
    "business": ["Business"],
    "property": ["Property", "имущество"],
    "healthcare": ["Healthcare"],
    # "travel": ["Travel"],
    "personal_needs": ["Personal_needs", "Personal needs"],
    "auto": ["Auto"],
    "deposit": ["Deposit"],
    "card": ["Card"],
    "charity": ["Charity", "Donation", "Zakat", "Waqf"]
}

NOW = datetime(2025, 10, 18)

# =======================================================
# === 1. Расчёт RFM и целей пользователя ===
# =======================================================

def compute_insight(df_user: pd.DataFrame):
    now = NOW
    R = (now - df_user["date"].max()).days
    F = len(df_user)
    M = df_user["amount"].sum()

    total = df_user["amount"].sum()
    shares = {}
    for goal, cats in GOALS.items():
        amt = df_user[df_user["category"].isin(cats)]["amount"].sum()
        shares[goal] = round(amt / total, 3) if total > 0 else 0

    main_focus = max(shares, key=shares.get) if shares else None
    charity_ratio = shares.get("charity", 0)
    print(f"R: {R}, F: {F}, M: {M}, shares: {shares}, main_focus: {main_focus}, charity_ratio: {charity_ratio}")
    return {"R": R, "F": F, "M": M, "shares": shares, "main_focus": main_focus, "charity_ratio": charity_ratio}

# =======================================================
# === 2. Правила принятия решения ===
# =======================================================

def decide_notification(insight):
    R = insight["R"]
    F = insight["F"]
    M = insight["M"]
    shares = insight["shares"]
    focus = insight["main_focus"]

    # Благотворительность
    if shares.get("charity", 0) >= 0.25:
        return random.choice([
            "Вы проявляете щедрость 🌙 Хотите оформить постоянный Waqf-счёт?",
            "Вижу частые пожертвования 💖 Хотите ежемесячный отчёт по благотворительности?",
            "Вы регулярно помогаете другим 🤲 Показать, как оптимизировать выплаты закята?"
        ])

    # Образование
    if focus == "education":
        return random.choice([
            "Вы активно инвестируете в знания 📚 Подобрать рассрочку на обучение?",
            "Вижу акцент на образовании 🎓 Рекомендовать халяль-курсы для развития?",
            "Ваш фокус — образование 🏫 Хотите рассмотреть варианты учебных грантов?"
        ])

    # Бизнес
    if focus == "business":
        return random.choice([
            "У вас бизнес-направление 💼 Подобрать халяльные инвестиционные инструменты?",
            "Активны в бизнесе 📊 Рассказать про поддержку предпринимателей?",
            "Заметна активность в бизнесе 💹 Хотите рекомендации по увеличению оборота?"
        ])

    # Недвижимость
    if focus == "property":
        return random.choice([
            "Интерес к недвижимости 🏠 Рассказать о халяльной ипотеке (Иджара)?",
            "Вижу внимание к жилью 🏡 Хотите рассчитать рассрочку без процентов?",
            "Планируете покупку жилья? 🕌 Подобрать исламскую ипотеку?"
        ])

    # Авто
    if focus == "auto":
        return random.choice([
            "Вы рассматриваете авто 🚗 Рассказать про рассрочку без рибы?",
            "Активность в автосфере 🛞 Подобрать халяльный автолизинг?",
            "Планируете покупку машины? 🚘 Есть выгодные исламские предложения!"
        ])

    # Депозиты / накопления
    if shares.get("deposit", 0) + shares.get("card", 0) > 0.5:
        return random.choice([
            "Вы аккуратно копите 💰 Рассказать про накопительные продукты?",
            "Активны в управлении средствами 🏦 Хотите персональный финансовый план?",
            "Вы хорошо управляете балансом 💹 Подобрать гибкий халяль-депозит?"
        ])

    # Неактивные
    if R > 60 and F < 5:
        return random.choice([
            "Давно не было активности ⏳ Напомнить о накопительных возможностях?",
            "Вы немного пропали 🤔 Подсказать свежие предложения?",
            "Аккаунт не активен 💤 Хотите я помогу с новыми идеями?"
        ])

    # Базовый сценарий
    if M > 0:
        return random.choice([
            "Хотите персональный план финансовых целей?",
            "Подобрать предложения на основе ваших операций?",
            "Показать, как улучшить баланс расходов и накоплений?"
        ])
    return None

# =======================================================
# === 3. Основной запуск ===
# =======================================================

def run_notifications(transactions):
    notifications = []
    for uid, group in transactions.groupby("user_id"):
        insight = compute_insight(group)
        msg = decide_notification(insight)
        if msg:
            notifications.append({"user_id": uid, "message": msg, "focus": insight["main_focus"]})
    return pd.DataFrame(notifications)

# =======================================================
# === 4. Результат ===
# =======================================================

if __name__ == "__main__":
    df = run_notifications(transactions)
    for r in df.itertuples():
        print(f"User {r.user_id}: {r.message} (Focus: {r.focus})")