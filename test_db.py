import sqlite3
import pandas as pd

# Подключение к базе
conn = sqlite3.connect('marketing_analytics.db')

print("=== ПРОВЕРКА ДАННЫХ В БАЗЕ ===")
print()

# Проверяем структуру таблицы
print("Структура таблицы campaign_metrics:")
cursor = conn.execute("PRAGMA table_info(campaign_metrics)")
for row in cursor.fetchall():
    print(f"  {row[1]} ({row[2]})")
print()

# Проверяем количество записей
count = conn.execute("SELECT COUNT(*) FROM campaign_metrics").fetchone()[0]
print(f"Всего записей: {count}")
print()

# Проверяем уникальные кампании
print("Уникальные кампании:")
campaigns = conn.execute("SELECT DISTINCT campaign_name FROM campaign_metrics LIMIT 15").fetchall()
for campaign in campaigns:
    print(f"  - {campaign[0]}")
print()

# Проверяем кампании с продуктами
print("Кампании с продуктами:")
product_campaigns = conn.execute("""
    SELECT DISTINCT campaign_name 
    FROM campaign_metrics 
    WHERE campaign_name LIKE '%РКО%' 
       OR campaign_name LIKE '%Бизнес%' 
       OR campaign_name LIKE '%РБиДОС%'
    LIMIT 10
""").fetchall()
for campaign in product_campaigns:
    print(f"  - {campaign[0]}")
print()

# Проверяем общую статистику
print("Общая статистика:")
stats = conn.execute("""
    SELECT 
        COUNT(DISTINCT campaign_id) as campaigns_count,
        SUM(impressions) as total_impressions,
        SUM(clicks) as total_clicks,
        SUM(cost_before_vat) as total_cost
    FROM campaign_metrics 
    WHERE impressions IS NOT NULL
""").fetchone()
print(f"  Кампаний: {stats[0]}")
print(f"  Показов: {stats[1]:,}")
print(f"  Кликов: {stats[2]:,}")
print(f"  Расход: {stats[3]:,.2f} ₽")
print()

conn.close() 