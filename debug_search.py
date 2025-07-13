#!/usr/bin/env python3
"""
Скрипт для отладки поиска кампаний
"""

from ai_agent import MarketingAnalyticsAgent
import sqlite3
import pandas as pd

# Создаем агента
agent = MarketingAnalyticsAgent()

# Тестируем поиск
question = "сделай отчет по фрк4"
print(f"Вопрос: {question}")

# Проверяем SQL запрос
sql_query = agent.generate_sql_query(question)
print(f"\nSQL запрос:\n{sql_query}")

# Выполняем запрос напрямую
conn = sqlite3.connect('marketing_analytics.db')
df = pd.read_sql_query(sql_query, conn)
conn.close()

print(f"\nРезультат запроса:")
print(f"Количество строк: {len(df)}")
if not df.empty:
    print(df.head())
    print(f"\nСуммарные данные:")
    print(f"Показы: {df['impressions'].sum():,.0f}")
    print(f"Клики: {df['clicks'].sum():,.0f}")
    print(f"Расход: {df['cost'].sum():,.0f} ₽")
    print(f"Визиты: {df['visits'].sum():,.0f}")
else:
    print("Нет данных")

# Проверяем, что есть в базе для ФРК4
print(f"\n=== Проверка базы данных ===")
conn = sqlite3.connect('marketing_analytics.db')
cursor = conn.cursor()
cursor.execute('SELECT DISTINCT "Название кампании" FROM campaign_metrics WHERE "Название кампании" LIKE "%ФРК4%"')
campaigns = cursor.fetchall()
print(f"Кампании с ФРК4 в базе:")
for campaign in campaigns:
    print(f"  - {campaign[0]}")

# Проверяем данные
cursor.execute('''
SELECT "Название кампании", "Площадка", 
       SUM("Показы") as impressions, 
       SUM("Клики") as clicks, 
       SUM("Расход до НДС") as cost, 
       SUM("Визиты") as visits
FROM campaign_metrics 
WHERE "Название кампании" LIKE "%ФРК4%"
GROUP BY "Название кампании", "Площадка"
''')
data = cursor.fetchall()
print(f"\nДанные по ФРК4:")
for row in data:
    print(f"  {row[0]} | {row[1]} | {row[2]:,.0f} показов | {row[3]:,.0f} кликов | {row[4]:,.0f} ₽ | {row[5]:,.0f} визитов")

conn.close() 