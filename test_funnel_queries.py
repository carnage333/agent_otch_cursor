#!/usr/bin/env python3
"""
Тестовый скрипт для проверки запросов по воронке и UTM-меткам
"""

import sqlite3
import pandas as pd
from ai_agent import MarketingAnalyticsAgent

def test_funnel_queries():
    """Тестируем различные запросы по воронке и UTM"""
    
    print("🧪 Тестирование запросов по воронке и UTM-меткам\n")
    
    # Инициализируем агента
    agent = MarketingAnalyticsAgent()
    
    # Список тестовых запросов
    test_queries = [
        "Покажи воронку по utm_campaign = 'rko_spring2024'",
        "Сколько было заявок и сколько из них качественные по utm_source = 'yandex'",
        "Сравни конверсию в заявки по utm_medium = 'cpc' и utm_medium = 'organic'",
        "Покажи топ-5 utm_campaign по количеству открытых счетов",
        "Покажи динамику по дням по utm_campaign = 'rko_spring2024'",
        "Сколько заявок пришло с utm_source = 'yandex'?",
        "Какой трафик и конверсия по разным источникам?",
        "Сколько визитов, заявок, успешных регистраций по кампании '06133744'?",
        "Какой процент качественных лидов по разным каналам?",
        "Сколько было звонков/ответов/качественных заявок по UTM-меткам?",
        "Сравни эффективность разных UTM-кампаний",
        "Построй воронку: визиты → заявки → счета → успешные регистрации"
    ]
    
    # Проверяем данные в БД
    print("📊 Проверка данных в БД:")
    conn = sqlite3.connect('marketing_analytics.db')
    cursor = conn.cursor()
    
    # Проверяем количество записей
    cursor.execute('SELECT COUNT(*) FROM funnel_data')
    total_rows = cursor.fetchone()[0]
    print(f"Всего записей в funnel_data: {total_rows}")
    
    # Проверяем примеры данных
    cursor.execute('SELECT * FROM funnel_data LIMIT 3')
    sample_data = cursor.fetchall()
    print("Примеры данных:")
    for i, row in enumerate(sample_data, 1):
        print(f"  {i}. {row}")
    
    # Проверяем уникальные значения UTM
    cursor.execute('SELECT DISTINCT utm_campaign FROM funnel_data WHERE utm_campaign IS NOT NULL LIMIT 5')
    campaigns = cursor.fetchall()
    print(f"Примеры utm_campaign: {[c[0] for c in campaigns]}")
    
    cursor.execute('SELECT DISTINCT utm_source FROM funnel_data WHERE utm_source IS NOT NULL LIMIT 5')
    sources = cursor.fetchall()
    print(f"Примеры utm_source: {[s[0] for s in sources]}")
    
    cursor.execute('SELECT DISTINCT utm_medium FROM funnel_data WHERE utm_medium IS NOT NULL LIMIT 5')
    mediums = cursor.fetchall()
    print(f"Примеры utm_medium: {[m[0] for m in mediums]}")
    
    conn.close()
    print()
    
    # Тестируем запросы
    for i, query in enumerate(test_queries, 1):
        print(f"🔍 Тест {i}: {query}")
        try:
            response = agent.process_question(query)
            print(f"✅ Ответ получен (длина: {len(response)} символов)")
            print(f"📝 Начало ответа: {response[:200]}...")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        print("-" * 80)
        print()

if __name__ == "__main__":
    test_funnel_queries() 