import sqlite3
import pandas as pd

def check_frk4_campaigns():
    """Проверка кампаний ФРК4 в базе данных"""
    conn = sqlite3.connect('marketing_analytics.db')
    
    print("🔍 Поиск кампаний ФРК4 в базе данных")
    print("=" * 50)
    
    # Проверяем все кампании с ФРК4
    query = """
    SELECT DISTINCT "Название кампании" 
    FROM campaign_metrics 
    WHERE UPPER("Название кампании") LIKE '%ФРК4%'
       OR UPPER("Название кампании") LIKE '%ФРК 4%'
       OR UPPER("Название кампании") LIKE '%ФРК-4%'
    ORDER BY "Название кампании"
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"Найдено кампаний с ФРК4: {len(df)}")
    
    if len(df) > 0:
        print("\nСписок кампаний ФРК4:")
        for idx, row in df.iterrows():
            print(f"  {idx+1}. {row['Название кампании']}")
    else:
        print("\n❌ Кампании ФРК4 не найдены!")
        
        # Проверяем все кампании для понимания структуры
        print("\nПроверяем все кампании в базе:")
        all_campaigns = pd.read_sql_query("SELECT DISTINCT \"Название кампании\" FROM campaign_metrics ORDER BY \"Название кампании\"", conn)
        print(f"Всего кампаний в базе: {len(all_campaigns)}")
        
        # Показываем первые 20 кампаний
        print("\nПервые 20 кампаний:")
        for idx, row in all_campaigns.head(20).iterrows():
            print(f"  {idx+1}. {row['Название кампании']}")
    
    # Проверяем данные для конкретной кампании
    print("\n" + "=" * 50)
    print("Проверка данных для кампании 'ФРК4 Бизнес-Фест, апрель':")
    
    test_query = """
    SELECT "Название кампании", "Площадка", "Показы", "Клики", "Расход до НДС"
    FROM campaign_metrics 
    WHERE "Название кампании" = 'ФРК4 Бизнес-Фест, апрель'
    LIMIT 5
    """
    
    test_df = pd.read_sql_query(test_query, conn)
    print(f"Записей для 'ФРК4 Бизнес-Фест, апрель': {len(test_df)}")
    
    if len(test_df) > 0:
        print("\nДанные:")
        print(test_df)
    else:
        print("❌ Данные для 'ФРК4 Бизнес-Фест, апрель' не найдены")
    
    conn.close()

if __name__ == "__main__":
    check_frk4_campaigns() 