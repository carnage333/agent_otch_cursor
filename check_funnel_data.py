import sqlite3
import pandas as pd

conn = sqlite3.connect('marketing_analytics.db')

print("=== ПРОВЕРКА ДАННЫХ ВОРОНКИ ===")
print()

# Проверяем структуру таблицы funnel_data
print("Структура таблицы funnel_data:")
cursor = conn.execute("PRAGMA table_info(funnel_data)")
for row in cursor.fetchall():
    print(f"  {row[1]} ({row[2]})")
print()

# Проверяем количество записей
try:
    count = conn.execute("SELECT COUNT(*) FROM funnel_data").fetchone()[0]
    print(f"Всего записей в funnel_data: {count}")
    print()
except Exception as e:
    print(f"Ошибка при проверке funnel_data: {e}")
    print()

# Проверяем уникальные UTM кампании
try:
    cursor.execute("SELECT DISTINCT utm_campaign FROM funnel_data")
    campaigns = cursor.fetchall()
    print("Уникальные UTM кампании:")
    for campaign in campaigns:
        print(f"  - {campaign[0]}")
    print()
except Exception as e:
    print(f"Ошибка при проверке UTM кампаний: {e}")
    print()

# Проверяем данные для rko_spring2024
try:
    cursor.execute("SELECT * FROM funnel_data WHERE utm_campaign = 'rko_spring2024' LIMIT 5")
    data = cursor.fetchall()
    print("Данные для rko_spring2024:")
    for row in data:
        print(f"  {row}")
    print()
except Exception as e:
    print(f"Ошибка при проверке rko_spring2024: {e}")
    print()

conn.close() 