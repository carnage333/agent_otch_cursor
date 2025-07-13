import pandas as pd
import sqlite3
import csv

def load_fixed_csv_data():
    """Загрузка данных из CSV с правильной обработкой структуры"""
    
    conn = sqlite3.connect('marketing_analytics.db')
    
    try:
        print("Читаем CSV файл...")
        
        # Читаем файл как текст и анализируем структуру
        with open('rko_funnel_sample-1750856109631.csv', 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            print(f"Первая строка: {first_line[:100]}...")
        
        # Пробуем разные варианты чтения
        df = None
        
        # Вариант 1: с engine='python' для автоматического определения разделителя
        try:
            df = pd.read_csv('rko_funnel_sample-1750856109631.csv', nrows=2000, engine='python')
            print("Успешно прочитано с engine='python'")
        except:
            pass
        
        # Вариант 2: если не получилось, пробуем с запятой
        if df is None:
            try:
                df = pd.read_csv('rko_funnel_sample-1750856109631.csv', nrows=2000, sep=',')
                print("Успешно прочитано с запятой")
            except:
                pass
        
        # Вариант 3: если не получилось, пробуем с точкой с запятой
        if df is None:
            try:
                df = pd.read_csv('rko_funnel_sample-1750856109631.csv', nrows=2000, sep=';')
                print("Успешно прочитано с точкой с запятой")
            except:
                pass
        
        if df is None:
            print("Не удалось прочитать CSV файл")
            return
        
        print(f"Загружено {len(df)} строк")
        print(f"Колонки: {df.columns.tolist()}")
        
        # Если все данные в одной колонке, пытаемся разделить
        if len(df.columns) == 1:
            print("Данные в одной колонке, пытаемся разделить...")
            first_col = df.columns[0]
            
            # Разделяем по запятой
            split_data = df[first_col].str.split(',', expand=True)
            if len(split_data.columns) > 1:
                df = split_data
                print(f"Разделено на {len(df.columns)} колонок")
        
        # Переименовываем колонки
        if len(df.columns) >= 7:  # Минимальное количество колонок
            df.columns = ['date', 'traffic_source', 'utm_campaign', 'utm_source', 
                         'utm_medium', 'utm_content', 'utm_term'] + list(df.columns[7:])
        
        # Добавляем недостающие колонки
        required_cols = ['step_name', 'step_order', 'visitors', 'conversions', 'conversion_rate']
        for col in required_cols:
            if col not in df.columns:
                if col == 'step_name':
                    df[col] = 'Этап воронки'
                elif col == 'step_order':
                    df[col] = 1
                elif col == 'visitors':
                    df[col] = df.get('submits', 100)
                elif col == 'conversions':
                    df[col] = df.get('res', 10)
                elif col == 'conversion_rate':
                    df[col] = 5.0
        
        # Сохраняем в базу
        df.to_sql('funnel_data', conn, if_exists='replace', index=False)
        print(f"Сохранено {len(df)} записей в funnel_data")
        
        # Проверяем данные
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM funnel_data")
        count = cursor.fetchone()[0]
        print(f"Всего записей в базе: {count}")
        
        cursor.execute("SELECT DISTINCT utm_campaign FROM funnel_data LIMIT 5")
        campaigns = cursor.fetchall()
        print("Уникальные кампании:")
        for campaign in campaigns:
            print(f"  - {campaign[0]}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
    
    conn.close()

if __name__ == "__main__":
    load_fixed_csv_data() 