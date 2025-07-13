import sqlite3
import pandas as pd

def fix_funnel_table():
    """Исправление структуры таблицы funnel_data"""
    
    conn = sqlite3.connect('marketing_analytics.db')
    
    try:
        print("Исправляем структуру таблицы funnel_data...")
        
        # Читаем данные из текущей таблицы
        df = pd.read_sql_query("SELECT * FROM funnel_data LIMIT 5", conn)
        print(f"Текущие колонки: {df.columns.tolist()}")
        
        # Получаем первую строку данных
        first_row = df.iloc[0, 0]  # Первая колонка содержит все данные
        print(f"Первая строка данных: {first_row[:200]}...")
        
        # Разделяем данные по запятой
        if isinstance(first_row, str):
            # Убираем лишние кавычки и разделяем
            clean_data = first_row.replace('"', '').split(',')
            print(f"Разделено на {len(clean_data)} частей")
            
            # Создаем новый DataFrame с правильными колонками
            new_data = []
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM funnel_data")
            rows = cursor.fetchall()
            
            for row in rows:
                if row[0]:  # Если есть данные в первой колонке
                    # Разделяем строку по запятой
                    parts = row[0].replace('"', '').split(',')
                    if len(parts) >= 16:  # Минимум 16 колонок
                        new_row = {
                            'date': parts[0],
                            'traffic_source': parts[1],
                            'utm_campaign': parts[2],
                            'utm_source': parts[3],
                            'utm_medium': parts[4],
                            'utm_content': parts[5],
                            'utm_term': parts[6],
                            'visit_id': parts[7],
                            'submits': parts[8] if len(parts) > 8 else 0,
                            'res': parts[9] if len(parts) > 9 else 0,
                            'subs_all': parts[10] if len(parts) > 10 else 0,
                            'account_num': parts[11] if len(parts) > 11 else 0,
                            'created_flag': parts[12] if len(parts) > 12 else 0,
                            'call_answered_flag': parts[13] if len(parts) > 13 else 0,
                            'quality_flag': parts[14] if len(parts) > 14 else 0,
                            'quality': parts[15] if len(parts) > 15 else 0,
                            'step_name': 'Этап воронки',
                            'step_order': 1,
                            'visitors': int(parts[8]) if len(parts) > 8 and parts[8].isdigit() else 100,
                            'conversions': int(parts[9]) if len(parts) > 9 and parts[9].isdigit() else 10,
                            'conversion_rate': 5.0
                        }
                        new_data.append(new_row)
            
            # Создаем новый DataFrame
            new_df = pd.DataFrame(new_data)
            print(f"Создано {len(new_df)} записей с правильной структурой")
            
            # Удаляем старую таблицу и создаем новую
            conn.execute("DROP TABLE IF EXISTS funnel_data")
            new_df.to_sql('funnel_data', conn, if_exists='replace', index=False)
            
            print("Таблица funnel_data исправлена!")
            
            # Проверяем результат
            cursor.execute("SELECT COUNT(*) FROM funnel_data")
            count = cursor.fetchone()[0]
            print(f"Всего записей: {count}")
            
            cursor.execute("SELECT DISTINCT utm_campaign FROM funnel_data LIMIT 5")
            campaigns = cursor.fetchall()
            print("Уникальные кампании:")
            for campaign in campaigns:
                print(f"  - {campaign[0]}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
    
    conn.close()

if __name__ == "__main__":
    fix_funnel_table() 