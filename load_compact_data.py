import pandas as pd
import sqlite3
import os
from datetime import datetime

def load_compact_data_to_db():
    """Загружает компактную версию данных из CSV файлов"""
    
    print("🔄 Загрузка компактной версии данных...")
    
    # Создаем подключение к базе данных
    conn = sqlite3.connect('marketing_analytics.db')
    
    # Загружаем данные кампаний (только первые 1000 записей)
    if os.path.exists('rko_econometric_sample.csv'):
        print("📊 Загружаю компактные данные кампаний...")
        df_campaigns = pd.read_csv('rko_econometric_sample.csv', nrows=1000)
        
        # Переименовываем колонки для совместимости
        df_campaigns = df_campaigns.rename(columns={
            'Дата': 'date',
            'Название кампании': 'campaign_name',
            'Площадка': 'platform',
            'Показы': 'impressions',
            'Клики': 'clicks',
            'Расход до НДС': 'cost_before_vat',
            'Визиты': 'visits'
        })
        
        # Очищаем и оптимизируем данные
        df_campaigns = df_campaigns.dropna(subset=['campaign_name'])
        
        # Добавляем недостающие колонки
        df_campaigns['conversions'] = 0  # По умолчанию
        df_campaigns['revenue'] = 0.0    # По умолчанию
        
        # Сохраняем в базу
        df_campaigns.to_sql('campaign_metrics', conn, if_exists='replace', index=False)
        print(f"✅ Загружено {len(df_campaigns)} записей кампаний (компактная версия)")
        
        # Показываем уникальные кампании
        unique_campaigns = df_campaigns['campaign_name'].unique()
        print(f"📋 Уникальные кампании: {len(unique_campaigns)}")
        for i, campaign in enumerate(unique_campaigns[:5]):
            print(f"  {i+1}. {campaign}")
        if len(unique_campaigns) > 5:
            print(f"  ... и еще {len(unique_campaigns) - 5} кампаний")
            
    else:
        print("❌ Файл rko_econometric_sample.csv не найден")
    
    # Создаем пустую таблицу воронки
    print("🔄 Создаю пустую таблицу воронки...")
    empty_funnel = pd.DataFrame(columns=[
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
        'step_name', 'step_order', 'visitors', 'conversions', 'conversion_rate', 'date'
    ])
    empty_funnel.to_sql('funnel_data', conn, if_exists='replace', index=False)
    print("✅ Создана пустая таблица воронки")
    
    conn.commit()
    conn.close()
    
    # Проверяем размер файла
    file_size = os.path.getsize('marketing_analytics.db') / (1024 * 1024)
    print(f"📁 Размер базы данных: {file_size:.2f} МБ")
    
    if file_size > 10:
        print("⚠️ Внимание: база данных больше 10 МБ. Может быть проблема с загрузкой в GitHub.")
    else:
        print("✅ Размер базы данных подходит для GitHub")

if __name__ == "__main__":
    load_compact_data_to_db() 