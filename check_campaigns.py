#!/usr/bin/env python3
"""
Скрипт для проверки кампаний в базе данных
"""

import sqlite3
import pandas as pd

def check_campaigns():
    """Проверяем кампании в базе данных"""
    try:
        conn = sqlite3.connect('marketing_analytics.db')
        
        # Получаем все кампании
        query = 'SELECT DISTINCT "Название кампании" FROM campaign_metrics LIMIT 20'
        df = pd.read_sql_query(query, conn)
        
        print("📋 Все кампании в базе данных:")
        print("=" * 50)
        for i, campaign in enumerate(df['Название кампании'], 1):
            print(f"{i}. {campaign}")
        
        print("\n" + "=" * 50)
        
        # Ищем кампании с ФРК
        query_frk = 'SELECT DISTINCT "Название кампании" FROM campaign_metrics WHERE "Название кампании" LIKE "%ФРК%"'
        df_frk = pd.read_sql_query(query_frk, conn)
        
        print("🔍 Кампании с 'ФРК':")
        for i, campaign in enumerate(df_frk['Название кампании'], 1):
            print(f"{i}. {campaign}")
        
        print("\n" + "=" * 50)
        
        # Ищем кампании с ФРК1
        query_frk1 = 'SELECT DISTINCT "Название кампании" FROM campaign_metrics WHERE "Название кампании" LIKE "%ФРК1%"'
        df_frk1 = pd.read_sql_query(query_frk1, conn)
        
        print("🔍 Кампании с 'ФРК1':")
        for i, campaign in enumerate(df_frk1['Название кампании'], 1):
            print(f"{i}. {campaign}")
        
        print("\n" + "=" * 50)
        
        # Ищем кампании с ФРК4
        query_frk4 = 'SELECT DISTINCT "Название кампании" FROM campaign_metrics WHERE "Название кампании" LIKE "%ФРК4%"'
        df_frk4 = pd.read_sql_query(query_frk4, conn)
        
        print("🔍 Кампании с 'ФРК4':")
        for i, campaign in enumerate(df_frk4['Название кампании'], 1):
            print(f"{i}. {campaign}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    check_campaigns() 