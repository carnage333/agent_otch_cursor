#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
import random

def create_demo_data():
    """Создание демо-данных для AI-агента"""
    
    print("Создание демо-данных...")
    
    # Создаем данные для campaign_metrics
    campaigns = [
        "ФРК4 Бизнес-Фест, апрель-декабрь 2025",
        "ФРК4_Продвижение_РКО в рупиях за 0_май-июнь 2025",
        "ФРК1 Годовой Performance 2025",
        "СберБизнес РКО для ИП",
        "Бизнес-старт РКО",
        "Торговля B2C РКО"
    ]
    
    platforms = [
        "Telegram Ads",
        "Yandex.Direct", 
        "Google Ads",
        "VK Реклама",
        "MyTarget",
        "Regionza",
        "NativeRent"
    ]
    
    # Генерируем данные
    campaign_data = []
    start_date = datetime(2025, 1, 1)
    
    for campaign in campaigns:
        for platform in platforms:
            # Генерируем реалистичные данные
            impressions = random.randint(10000, 500000)
            clicks = random.randint(50, 2000)
            cost = random.randint(5000, 100000)
            visits = random.randint(10, 500)
            
            # Рассчитываем CTR и CPC
            ctr = round((clicks / impressions) * 100, 2) if impressions > 0 else 0
            cpc = round(cost / clicks, 2) if clicks > 0 else 0
            
            # Добавляем вариативность по датам
            for i in range(30):
                date = start_date + timedelta(days=i)
                
                # Добавляем случайные колебания
                daily_impressions = max(0, impressions + random.randint(-1000, 1000))
                daily_clicks = max(0, clicks + random.randint(-10, 10))
                daily_cost = max(0, cost + random.randint(-100, 100))
                daily_visits = max(0, visits + random.randint(-5, 5))
                
                campaign_data.append({
                    'campaign_name': campaign,
                    'platform': platform,
                    'impressions': daily_impressions,
                    'clicks': daily_clicks,
                    'cost_before_vat': daily_cost,
                    'visits': daily_visits,
                    'date': date.strftime('%Y-%m-%d')
                })
    
    # Создаем DataFrame
    df_campaigns = pd.DataFrame(campaign_data)
    
    # Создаем данные для funnel_data
    utm_sources = [
        "google",
        "yandex", 
        "telegram",
        "vk",
        "direct",
        "organic"
    ]
    
    funnel_data = []
    
    for source in utm_sources:
        visits = random.randint(1000, 10000)
        submits = random.randint(50, 500)
        accounts_opened = random.randint(20, 200)
        created = random.randint(10, 100)
        calls_answered = random.randint(30, 300)
        quality_leads = random.randint(40, 400)
        
        funnel_data.append({
            'utm_source': source,
            'visits': visits,
            'submits': submits,
            'accounts_opened': accounts_opened,
            'created': created,
            'calls_answered': calls_answered,
            'quality_leads': quality_leads
        })
    
    df_funnel = pd.DataFrame(funnel_data)
    
    # Сохраняем в CSV файлы
    df_campaigns.to_csv('rko_econometric_sample.csv', index=False)
    df_funnel.to_csv('rko_funnel_sample-1750856109631.csv', index=False)
    
    print(f"Создано {len(df_campaigns)} записей для campaign_metrics")
    print(f"Создано {len(df_funnel)} записей для funnel_data")
    print("Демо-данные сохранены в CSV файлы")

if __name__ == "__main__":
    create_demo_data() 