#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import pandas as pd
from pathlib import Path

def create_compact_database():
    """Создание компактной базы данных с обрезанными данными"""
    
    # Путь к базе данных
    db_path = 'marketing_analytics.db'
    
    print("Создание компактной базы данных...")
    
    # Удаляем старую БД если есть
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Удалена старая база данных")
    
    # Создаем подключение к базе данных
    conn = sqlite3.connect(db_path)
    
    try:
        # Обрабатываем rko_econometric_sample.csv (оставляем как есть)
        if os.path.exists('rko_econometric_sample.csv'):
            print("Загрузка данных из rko_econometric_sample.csv...")
            df_econometric = pd.read_csv('rko_econometric_sample.csv')
            df_econometric.to_sql('campaign_metrics', conn, if_exists='replace', index=False)
            print(f"Таблица campaign_metrics создана с {len(df_econometric)} записями")
        
        # Обрабатываем rko_funnel_sample-1750856109631.csv (обрезаем на 30%)
        if os.path.exists('rko_funnel_sample-1750856109631.csv'):
            print("Загрузка и обрезка данных из rko_funnel_sample-1750856109631.csv...")
            
            # Читаем файл с правильными параметрами
            df_funnel = pd.read_csv('rko_funnel_sample-1750856109631.csv', 
                                   sep=',', 
                                   quotechar='"', 
                                   escapechar='\\',
                                   encoding='utf-8',
                                   on_bad_lines='skip')
            
            # Обрезаем на 30% с конца
            original_length = len(df_funnel)
            cut_percentage = 0.3
            cut_length = int(original_length * cut_percentage)
            df_funnel_trimmed = df_funnel.iloc[:-cut_length]
            
            df_funnel_trimmed.to_sql('funnel_data', conn, if_exists='replace', index=False)
            print(f"Таблица funnel_data создана с {len(df_funnel_trimmed)} записями (обрезано {cut_length} записей)")
        
        # Создаем индексы для оптимизации
        print("Создание индексов...")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_campaign_name ON campaign_metrics(campaign_name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_platform ON campaign_metrics(platform)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON campaign_metrics(date)")
        
        print("Компактная база данных успешно создана!")
        
        # Показываем размер файла
        file_size = os.path.getsize(db_path) / (1024 * 1024)  # в МБ
        print(f"Размер базы данных: {file_size:.2f} МБ")
        
    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_compact_database() 