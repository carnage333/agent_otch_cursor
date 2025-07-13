import pandas as pd
import sqlite3
import os
from pathlib import Path

def setup_database():
    """Создание базы данных SQLite с данными из CSV файлов"""
    
    # Создаем базу данных
    conn = sqlite3.connect('marketing_analytics.db')
    cursor = conn.cursor()
    
    # Загружаем данные из CSV файлов
    print("Загрузка данных из CSV файлов...")
    
    # Эконометрические данные
    try:
        econometric_df = pd.read_csv('rko_econometric_sample.csv', encoding='utf-8')
        print(f"Загружено {len(econometric_df)} строк эконометрических данных")
        
        # Переименовываем колонки для SQL совместимости
        column_mapping = {
            'Дата': 'date',
            'ID Кампании': 'campaign_id',
            'Название кампании': 'campaign_name',
            'Кампания': 'campaign',
            'Площадка': 'platform',
            'Показы': 'impressions',
            'Клики': 'clicks',
            'Расход до НДС': 'cost_before_vat',
            'Визиты': 'visits'
        }
        
        econometric_df = econometric_df.rename(columns=column_mapping)
        
        # Сохраняем в базу данных
        econometric_df.to_sql('campaign_metrics', conn, if_exists='replace', index=False)
        print("Таблица campaign_metrics создана")
        
    except Exception as e:
        print(f"Ошибка при загрузке эконометрических данных: {e}")
    
    # Создаем тестовые данные для воронки
    def create_test_funnel_data():
        """Создание тестовых данных для воронки"""
        import random
        from datetime import datetime, timedelta
        
        # Тестовые данные
        test_data = []
        start_date = datetime(2025, 1, 1)
        
        # UTM кампании
        utm_campaigns = ['rko_spring2024', 'rko_summer2024', 'rko_autumn2024']
        utm_sources = ['yandex', 'google', 'vk', 'telegram']
        utm_mediums = ['cpc', 'cpm', 'banner']
        
        for i in range(100):  # 100 записей
            date = start_date + timedelta(days=i % 30)
            utm_campaign = random.choice(utm_campaigns)
            utm_source = random.choice(utm_sources)
            utm_medium = random.choice(utm_mediums)
            
            visits = random.randint(50, 200)
            submits = random.randint(5, 30)
            accounts_opened = random.randint(2, 15)
            quality_leads = random.randint(1, 10)
            
            test_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'traffic_source': utm_source,
                'utm_campaign': utm_campaign,
                'utm_source': utm_source,
                'utm_medium': utm_medium,
                'utm_content': f'content_{i}',
                'utm_term': f'term_{i}',
                'visit_id': f'visit_{i}',
                'submits': submits,
                'res': submits * 0.8,
                'subs_all': submits,
                'account_num': accounts_opened,
                'created_flag': accounts_opened,
                'call_answered_flag': random.randint(0, 5),
                'quality_flag': quality_leads,
                'quality': quality_leads
            })
        
        return test_data

    try:
        # Загружаем данные воронки
        print("Загрузка данных воронки...")
        test_funnel_data = create_test_funnel_data()
        funnel_df = pd.DataFrame(test_funnel_data)
        
        # Сохраняем в базу данных
        funnel_df.to_sql('funnel_data', conn, if_exists='replace', index=False)
        print(f"Загружено {len(funnel_df)} строк данных воронки")
        
    except Exception as e:
        print(f"Ошибка при загрузке данных воронки: {e}")
        # Создаем пустую таблицу для совместимости
        conn.execute('''
            CREATE TABLE IF NOT EXISTS funnel_data (
                date TEXT,
                traffic_source TEXT,
                utm_campaign TEXT,
                utm_source TEXT,
                utm_medium TEXT,
                utm_content TEXT,
                utm_term TEXT,
                visit_id TEXT,
                submits REAL,
                res REAL,
                subs_all REAL,
                account_num INTEGER,
                created_flag INTEGER,
                call_answered_flag INTEGER,
                quality_flag INTEGER,
                quality INTEGER
            )
        ''')
        print("Создаем пустую таблицу funnel_data для совместимости")
    
    # Создаем индексы для оптимизации запросов
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaign_date ON campaign_metrics(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaign_id ON campaign_metrics(campaign_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_funnel_date ON funnel_data(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_funnel_campaign ON funnel_data(utm_campaign)")
    except Exception as e:
        print(f"Ошибка при создании индексов: {e}")
    
    conn.commit()
    conn.close()
    
    print("База данных успешно создана!")
    
    # Выводим информацию о структуре данных
    print("\nСтруктура данных:")
    print("=" * 50)
    
    conn = sqlite3.connect('marketing_analytics.db')
    
    # Информация о таблице campaign_metrics
    try:
        cursor = conn.execute("PRAGMA table_info(campaign_metrics)")
        columns = cursor.fetchall()
        print("\nТаблица campaign_metrics:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
    except Exception as e:
        print(f"Ошибка при получении информации о таблице campaign_metrics: {e}")
    
    # Информация о таблице funnel_data
    try:
        cursor = conn.execute("PRAGMA table_info(funnel_data)")
        columns = cursor.fetchall()
        print("\nТаблица funnel_data:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
    except Exception as e:
        print(f"Ошибка при получении информации о таблице funnel_data: {e}")
    
    # Примеры данных
    try:
        print("\nПримеры данных campaign_metrics:")
        cursor = conn.execute("SELECT * FROM campaign_metrics LIMIT 3")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  {row}")
    except Exception as e:
        print(f"Ошибка при получении примеров campaign_metrics: {e}")
    
    try:
        print("\nПримеры данных funnel_data:")
        cursor = conn.execute("SELECT * FROM funnel_data LIMIT 3")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  {row}")
    except Exception as e:
        print(f"Ошибка при получении примеров funnel_data: {e}")
    
    conn.close()

if __name__ == "__main__":
    setup_database() 