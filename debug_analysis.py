#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ai_agent import MarketingAnalyticsAgent
import pandas as pd

def debug_analysis():
    """Отладка анализа данных для ФРК4"""
    agent = MarketingAnalyticsAgent()
    
    # Генерируем SQL для ФРК4
    sql_query = agent.generate_sql_query("сделай отчет по фрк4")
    print(f"SQL запрос: {sql_query}")
    
    # Выполняем запрос
    df = agent.execute_query(sql_query)
    print(f"\nДанные:\n{df}")
    print(f"\nКолонки: {df.columns.tolist()}")
    
    # Проверяем, есть ли campaign_name
    if 'campaign_name' in df.columns:
        print(f"\nУникальные кампании: {df['campaign_name'].unique()}")
        print(f"Уникальные площадки: {df['platform'].unique()}")
        
        # Проверяем агрегацию по площадкам
        if 'platform' in df.columns and 'ctr' in df.columns:
            platform_stats = df.groupby('platform').agg({'ctr': 'mean'}).reset_index()
            print(f"\nАгрегированные данные по площадкам:\n{platform_stats}")
            print(f"Количество площадок: {len(platform_stats)}")
    
    # Анализируем данные
    analysis = agent.analyze_data(df, "сделай отчет по фрк4")
    print(f"\nИнсайты: {analysis.get('insights', [])}")
    print(f"Рекомендации: {analysis.get('recommendations', [])}")

if __name__ == "__main__":
    debug_analysis() 