import sqlite3

def test_search():
    conn = sqlite3.connect('marketing_analytics.db')
    cursor = conn.cursor()
    
    # Ищем кампании с ФРК4
    cursor.execute('SELECT DISTINCT "Название кампании" FROM campaign_metrics WHERE "Название кампании" LIKE "%ФРК4%"')
    results = cursor.fetchall()
    
    print("Кампании с ФРК4:")
    for row in results:
        print(f"- {row[0]}")
    
    conn.close()

if __name__ == "__main__":
    test_search() 