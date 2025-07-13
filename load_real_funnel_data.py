import pandas as pd
import sqlite3
import os

def load_real_funnel_data():
    """Загрузка реальных данных из CSV в таблицу funnel_data"""
    
    # Подключаемся к базе
    conn = sqlite3.connect('marketing_analytics.db')
    
    try:
        # Читаем CSV файл с ограничением строк для GitHub
        print("Загрузка данных из CSV файла...")
        
        # Пробуем разные варианты чтения файла
        try:
            # Вариант 1: стандартное чтение
            df = pd.read_csv('rko_funnel_sample-1750856109631.csv', nrows=2000)
        except:
            try:
                # Вариант 2: с разделителем точка с запятой
                df = pd.read_csv('rko_funnel_sample-1750856109631.csv', nrows=2000, sep=';')
            except:
                # Вариант 3: с табуляцией
                df = pd.read_csv('rko_funnel_sample-1750856109631.csv', nrows=2000, sep='\t')
        
        print(f"Загружено {len(df)} строк из CSV")
        print(f"Колонки: {df.columns.tolist()}")
        
        # Переименовываем колонки для соответствия структуре funnel_data
        column_mapping = {
            'date': 'date',
            'lastTrafficSource': 'utm_source',
            'UTMCampaign_clear': 'utm_campaign', 
            'UTMSource': 'utm_source',
            'UTMMedium': 'utm_medium',
            'UTMContent': 'utm_content',
            'UTMTerm': 'utm_term',
            'visitID': 'visit_id',
            'submits': 'submits',
            'res': 'res',
            'subs_all': 'subs_all',
            'account_num': 'account_num',
            'created_flag': 'created_flag',
            'call_answered_flag': 'call_answered_flag',
            'quality_flag': 'quality_flag',
            'quality': 'quality'
        }
        
        # Применяем переименование только для существующих колонок
        existing_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_columns)
        
        # Добавляем недостающие колонки с дефолтными значениями
        required_columns = {
            'step_name': 'Этап воронки',
            'step_order': 1,
            'visitors': df.get('submits', 0),
            'conversions': df.get('res', 0),
            'conversion_rate': 0.0
        }
        
        for col, default_value in required_columns.items():
            if col not in df.columns:
                df[col] = default_value
        
        # Вычисляем conversion_rate если есть данные
        if 'visitors' in df.columns and 'conversions' in df.columns:
            df['conversion_rate'] = (df['conversions'] / df['visitors'] * 100).fillna(0)
        
        # Сохраняем в базу данных
        df.to_sql('funnel_data', conn, if_exists='replace', index=False)
        
        print(f"Добавлено {len(df)} записей в funnel_data")
        
        # Проверяем данные для rko_spring2024
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM funnel_data WHERE utm_campaign LIKE '%rko%' OR utm_campaign LIKE '%spring%'")
        count = cursor.fetchone()[0]
        print(f"Записей с RKO/spring кампаниями: {count}")
        
        # Показываем уникальные UTM кампании
        cursor.execute("SELECT DISTINCT utm_campaign FROM funnel_data LIMIT 10")
        campaigns = cursor.fetchall()
        print("\nУникальные UTM кампании:")
        for campaign in campaigns:
            print(f"  - {campaign[0]}")
        
        # Показываем пример данных
        cursor.execute("SELECT * FROM funnel_data LIMIT 3")
        data = cursor.fetchall()
        print("\nПример данных:")
        for row in data:
            print(f"  {row}")
        
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        print("Создаем пустую таблицу funnel_data")
        
        # Создаем пустую таблицу для совместимости
        conn.execute('''
            CREATE TABLE IF NOT EXISTS funnel_data (
                date TEXT,
                utm_source TEXT,
                utm_campaign TEXT,
                utm_medium TEXT,
                utm_content TEXT,
                utm_term TEXT,
                step_name TEXT,
                step_order INTEGER,
                visitors INTEGER,
                conversions INTEGER,
                conversion_rate REAL
            )
        ''')
    
    conn.close()

if __name__ == "__main__":
    load_real_funnel_data() 