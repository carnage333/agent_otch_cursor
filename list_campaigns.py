import sqlite3

conn = sqlite3.connect('marketing_analytics.db')
cursor = conn.cursor()

cursor.execute("SELECT DISTINCT campaign_name FROM campaign_metrics ORDER BY campaign_name")
campaigns = cursor.fetchall()

print("Список всех campaign_name:")
for c in campaigns:
    print(c[0])

conn.close() 