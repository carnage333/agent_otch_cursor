#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import pandas as pd
from pathlib import Path

def init_database():
    """Инициализация базы данных при развертывании"""
    
    # Путь к базе данных
    db_path = 'marketing_analytics.db'
    
    # Проверяем, существует ли база данных
    if os.path.exists(db_path):
        print("База данных уже существует")
        return
    
    print("Создание базы данных...")
    
    # Создаем подключение к базе данных
    conn = sqlite3.connect(db_path)
    
    try:
        # Загружаем данные из CSV файлов
        csv_files = [
            'rko_econometric_sample.csv',
            'rko_funnel_sample-1750856109631.csv'
        ]
        
        csv_found = False
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                csv_found = True
                print(f"Загрузка данных из {csv_file}...")
                
                # Читаем CSV файл
                df = pd.read_csv(csv_file)
                
                # Определяем имя таблицы на основе имени файла
                if 'econometric' in csv_file:
                    table_name = 'campaign_metrics'
                elif 'funnel' in csv_file:
                    table_name = 'funnel_data'
                else:
                    table_name = csv_file.replace('.csv', '').replace('-', '_')
                
                # Сохраняем в базу данных
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                print(f"Таблица {table_name} создана с {len(df)} записями")
        
        # Если CSV файлы не найдены, создаем демо-данные
        if not csv_found:
            print("CSV файлы не найдены. Создание демо-данных...")
            try:
                from create_demo_data import create_demo_data
                create_demo_data()
                
                # Теперь загружаем созданные демо-данные
                for csv_file in csv_files:
                    if os.path.exists(csv_file):
                        print(f"Загрузка демо-данных из {csv_file}...")
                        df = pd.read_csv(csv_file)
                        
                        if 'econometric' in csv_file:
                            table_name = 'campaign_metrics'
                        elif 'funnel' in csv_file:
                            table_name = 'funnel_data'
                        else:
                            table_name = csv_file.replace('.csv', '').replace('-', '_')
                        
                        df.to_sql(table_name, conn, if_exists='replace', index=False)
                        print(f"Таблица {table_name} создана с {len(df)} записями")
            except Exception as e:
                print(f"Ошибка при создании демо-данных: {e}")
                print("Создание пустых таблиц...")
                
                # Создаем пустые таблицы с правильной структурой
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS campaign_metrics (
                        campaign_name TEXT,
                        platform TEXT,
                        impressions INTEGER,
                        clicks INTEGER,
                        cost_before_vat REAL,
                        visits INTEGER,
                        date TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS funnel_data (
                        utm_source TEXT,
                        visits INTEGER,
                        submits INTEGER,
                        accounts_opened INTEGER,
                        created INTEGER,
                        calls_answered INTEGER,
                        quality_leads INTEGER
                    )
                """)
        
        # Создаем индексы для оптимизации
        print("Создание индексов...")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_campaign_name ON campaign_metrics(campaign_name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_platform ON campaign_metrics(platform)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON campaign_metrics(date)")
        
        print("База данных успешно создана!")
        
    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    init_database() 