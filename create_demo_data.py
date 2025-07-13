#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def create_demo_database():
    """Создает демо-базу данных с небольшим объемом данных для деплоя"""
    
    # Создаем подключение к базе данных
    conn = sqlite3.connect('marketing_analytics.db')
    cursor = conn.cursor()
    
    # Создаем таблицы
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS campaign_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_name TEXT NOT NULL,
        platform TEXT NOT NULL,
        date TEXT NOT NULL,
        impressions INTEGER,
        clicks INTEGER,
        cost_before_vat REAL,
        visits INTEGER,
        conversions INTEGER,
        revenue REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS funnel_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        utm_source TEXT,
        utm_medium TEXT,
        utm_campaign TEXT,
        utm_content TEXT,
        utm_term TEXT,
        step_name TEXT,
        step_order INTEGER,
        visitors INTEGER,
        conversions INTEGER,
        conversion_rate REAL,
        date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Генерируем демо-данные для кампаний
    campaigns = [
        "ФРК4 БИЗНЕС-ФЕСТ",
        "ФРК4_ПРОДВИЖЕНИЕ_РКО", 
        "ФРК1",
        "ГОДОВОЙ PERFORMANCE",
        "СБЕРБИЗНЕС",
        "БИЗНЕС-СТАРТ",
        "ТОРГОВЛЯ B2C"
    ]
    
    platforms = ["Telegram Ads", "Regionza", "NativeRent", "yandex", "vsp"]
    
    # Генерируем данные за последние 7 дней (вместо 30)
    start_date = datetime.now() - timedelta(days=7)
    campaign_data = []
    
    for i in range(7):  # 7 дней вместо 30
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime('%Y-%m-%d')
        
        for campaign in campaigns[:3]:  # Только первые 3 кампании
            for platform in platforms[:3]:  # Только первые 3 платформы
                # Генерируем реалистичные данные
                impressions = random.randint(100, 5000)  # Уменьшили диапазон
                clicks = random.randint(10, int(impressions * 0.1))
                ctr = clicks / impressions if impressions > 0 else 0
                cpc = random.uniform(10, 100)
                cost = clicks * cpc
                visits = int(clicks * random.uniform(0.7, 1.2))
                conversions = int(visits * random.uniform(0.01, 0.05))
                revenue = conversions * random.uniform(500, 2000)
                
                campaign_data.append({
                    'campaign_name': campaign,
                    'platform': platform,
                    'date': date_str,
                    'impressions': impressions,
                    'clicks': clicks,
                    'cost_before_vat': round(cost, 2),
                    'visits': visits,
                    'conversions': conversions,
                    'revenue': round(revenue, 2)
                })
    
    # Создаем DataFrame и сохраняем в базу
    df_campaigns = pd.DataFrame(campaign_data)
    df_campaigns.to_sql('campaign_metrics', conn, if_exists='replace', index=False)
    
    # Генерируем демо-данные для воронки
    utm_sources = ["google", "yandex", "telegram", "vk", "direct"]
    utm_mediums = ["cpc", "banner", "social", "email", "organic"]
    utm_campaigns = ["brand", "product", "seasonal", "promo", "retargeting"]
    
    funnel_data = []
    step_names = ["Показ", "Клик", "Переход", "Регистрация", "Оплата"]
    
    for i in range(5):  # 5 записей вместо 20
        current_date = start_date + timedelta(days=random.randint(0, 6))
        date_str = current_date.strftime('%Y-%m-%d')
        
        for step_order, step_name in enumerate(step_names, 1):
            visitors = random.randint(50, 1000)  # Уменьшили диапазон
            conversion_rate = random.uniform(0.1, 0.8)
            conversions = int(visitors * conversion_rate)
            
            funnel_data.append({
                'utm_source': random.choice(utm_sources),
                'utm_medium': random.choice(utm_mediums),
                'utm_campaign': random.choice(utm_campaigns),
                'utm_content': f"content_{random.randint(1, 5)}",
                'utm_term': f"term_{random.randint(1, 10)}",
                'step_name': step_name,
                'step_order': step_order,
                'visitors': visitors,
                'conversions': conversions,
                'conversion_rate': round(conversion_rate, 4),
                'date': date_str
            })
    
    # Создаем DataFrame и сохраняем в базу
    df_funnel = pd.DataFrame(funnel_data)
    df_funnel.to_sql('funnel_data', conn, if_exists='replace', index=False)
    
    conn.commit()
    conn.close()
    
    print("✅ Демо-база данных создана успешно!")
    print(f"📊 Создано {len(campaign_data)} записей кампаний")
    print(f"🔄 Создано {len(funnel_data)} записей воронки")
    
    # Проверяем размер файла
    import os
    file_size = os.path.getsize('marketing_analytics.db') / (1024 * 1024)
    print(f"📁 Размер базы данных: {file_size:.2f} МБ")

if __name__ == "__main__":
    create_demo_database() 