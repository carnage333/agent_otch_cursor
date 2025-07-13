import sqlite3
import pandas as pd

conn = sqlite3.connect('marketing_analytics.db')

# Проверяем все кампании с ФРК4
query = """
SELECT DISTINCT campaign_name 
FROM campaign_metrics 
WHERE LOWER(campaign_name) LIKE '%фрк4%'
ORDER BY campaign_name
"""

df = pd.read_sql_query(query, conn)
print("Кампании с ФРК4:")
print(df)

# Проверяем данные для конкретной кампании
query2 = """
SELECT campaign_name, platform, impressions, clicks, cost_before_vat
FROM campaign_metrics 
WHERE campaign_name LIKE '%ФРК4%'
LIMIT 10
"""

df2 = pd.read_sql_query(query2, conn)
print("\nДанные ФРК4:")
print(df2)

conn.close() 