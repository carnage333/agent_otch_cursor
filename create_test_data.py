#!/usr/bin/env python3
"""
Создание тестовых данных для funnel_data
"""

import sqlite3
import random
from datetime import datetime, timedelta

def create_test_funnel_data():
    """Создает тестовые данные для funnel_data"""
    
    print("🧪 Создание тестовых данных для funnel_data...")
    
    conn = sqlite3.connect('marketing_analytics.db')
    
    # Создаем таблицу
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
    
    # Очищаем таблицу
    conn.execute('DELETE FROM funnel_data')
    
    # Тестовые данные
    utm_campaigns = ['rko_spring2024', '06133744', '111959248', '17262419', '22066899', '23226611']
    utm_sources = ['yandex', 'google', 'vsp', 'organic', 'direct']
    utm_mediums = ['cpc', 'cpm', 'organic', 'vsp', 'email']
    traffic_sources = ['Ad traffic', 'Organic traffic', 'Direct traffic', 'Referral traffic']
    
    # Генерируем данные за последние 30 дней
    start_date = datetime.now() - timedelta(days=30)
    
    test_data = []
    visit_id_counter = 1
    
    for day in range(30):
        current_date = start_date + timedelta(days=day)
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Генерируем 50-100 записей в день
        daily_records = random.randint(50, 100)
        
        for _ in range(daily_records):
            utm_campaign = random.choice(utm_campaigns)
            utm_source = random.choice(utm_sources)
            utm_medium = random.choice(utm_mediums)
            traffic_source = random.choice(traffic_sources)
            
            # Генерируем метрики
            visits = random.randint(1, 5)
            submits = random.randint(0, visits)  # Заявки не больше визитов
            res = random.randint(0, submits)  # Результаты не больше заявок
            subs_all = random.randint(0, submits)
            account_num = random.randint(0, res)
            created_flag = random.randint(0, account_num)
            call_answered_flag = random.randint(0, submits)
            quality_flag = random.randint(0, created_flag)
            quality = random.randint(0, quality_flag)
            
            # UTM контент и термины
            utm_content = f"content_{random.randint(1000, 9999)}"
            utm_term = f"term_{random.randint(100, 999)}"
            
            test_data.append((
                date_str,
                traffic_source,
                utm_campaign,
                utm_source,
                utm_medium,
                utm_content,
                utm_term,
                str(visit_id_counter),
                float(submits),
                float(res),
                float(subs_all),
                account_num,
                created_flag,
                call_answered_flag,
                quality_flag,
                quality
            ))
            
            visit_id_counter += 1
    
    # Вставляем данные
    conn.executemany('''
        INSERT INTO funnel_data 
        (date, traffic_source, utm_campaign, utm_source, utm_medium, utm_content, utm_term, 
         visit_id, submits, res, subs_all, account_num, created_flag, call_answered_flag, quality_flag, quality)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', test_data)
    
    conn.commit()
    
    print(f"✅ Создано {len(test_data)} тестовых записей")
    
    # Показываем примеры
    sample = conn.execute('SELECT * FROM funnel_data LIMIT 3').fetchall()
    print("\n📋 Примеры данных:")
    for row in sample:
        print(row)
    
    campaigns = conn.execute('SELECT DISTINCT utm_campaign FROM funnel_data LIMIT 10').fetchall()
    print(f"🎯 Примеры utm_campaign: {[c[0] for c in campaigns]}")
    
    sources = conn.execute('SELECT DISTINCT utm_source FROM funnel_data LIMIT 5').fetchall()
    print(f"🌐 Примеры utm_source: {[s[0] for s in sources]}")
    
    # Статистика
    total_visits = conn.execute('SELECT COUNT(*) FROM funnel_data').fetchone()[0]
    total_submits = conn.execute('SELECT SUM(submits) FROM funnel_data').fetchone()[0]
    total_accounts = conn.execute('SELECT SUM(account_num) FROM funnel_data').fetchone()[0]
    
    print(f"\n📊 Статистика:")
    print(f"Всего записей: {total_visits}")
    print(f"Всего заявок: {total_submits}")
    print(f"Всего счетов: {total_accounts}")
    
    conn.close()

if __name__ == "__main__":
    create_test_funnel_data() 