from ai_agent import MarketingAnalyticsAgent
import sqlite3
import pandas as pd

# Создаем агента
agent = MarketingAnalyticsAgent()

# Подключаемся к базе данных
conn = sqlite3.connect('marketing_analytics.db')

# SQL запрос из вашего примера
sql = """SELECT campaign_name, platform, SUM(impressions) as impressions, SUM(clicks) as clicks, 
SUM(cost_before_vat) as cost, SUM(visits) as visits, 
ROUND(SUM(clicks) * 100.0 / SUM(impressions), 2) as ctr, 
ROUND(SUM(cost_before_vat) / SUM(clicks), 2) as cpc 
FROM campaign_metrics 
WHERE (campaign_name = 'Годовой Performance РКО + ОТР (Транспорт B2B)' 
OR campaign_name = 'Годовой Performance РКО + ОТР (Продажи B2B)' 
OR campaign_name = 'Годовой performance. Сбер Бизнес-старт 2025' 
OR campaign_name = 'Годовой Performance РКО + ОТР (Недвижимость B2B)' 
OR campaign_name = 'Годовой Performance РКО + ОТР (Услуги B2C)' 
OR campaign_name = 'Годовой Performance РКО + ОТР (Кафе B2C)' 
OR campaign_name = 'Годовой performance. РКО 2025.' 
OR campaign_name = 'Годовой Performance РКО + ОТР (eCom)' 
OR campaign_name = 'Годовой Performance РКО + ОТР (Торговля B2C)' 
OR campaign_name = 'Годовой performance. РКО 2025 (Медийка)') 
GROUP BY campaign_name, platform ORDER BY campaign_name ASC"""

# Выполняем запрос
df = pd.read_sql_query(sql, conn)
conn.close()

print("DataFrame columns:", df.columns.tolist())
print("DataFrame shape:", df.shape)
print("First few rows:")
print(df.head())

# Анализируем данные
analysis = agent.analyze_data(df, 'сделай отчет по Годовой performance')

print("\nAnalysis summary keys:", list(analysis['summary'].keys()))
print("Found campaigns:", analysis['summary'].get('found_campaigns', 'NOT FOUND'))

# Генерируем отчет
report = agent.generate_report(analysis, 'сделай отчет по Годовой performance')

print("\n" + "="*50)
print("GENERATED REPORT:")
print("="*50)
print(report) 