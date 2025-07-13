#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ai_agent import MarketingAnalyticsAgent

def test_edge_cases():
    """Тестирование всех краевых случаев поиска"""
    agent = MarketingAnalyticsAgent()
    
    # Тестовые случаи
    test_cases = [
        # Регистр и пробелы
        "сделай отчет по фрк4",
        "сделай отчет по ФРК-4", 
        "сделай отчет по фрк 4",
        "сделай отчет по Годовой performance",
        "сделай отчет по ГОДОВОЙ PERFORMANCE",
        
        # Опечатки
        "сделай отчет по годовй performance",
        "сделай отчет по годово performance",
        "сделай отчет по перфоманс",
        
        # Сокращения
        "сделай отчет по рко",
        "сделай отчет по рбидос",
        "сделай отчет по фрк",
        
        # Частичные названия
        "сделай отчет по годовой",
        "сделай отчет по performance",
        "сделай отчет по бизнес",
        
        # Разные форматы
        "сделай отчет по бизнес-карты",
        "сделай отчет по бизнес карты",
        "сделай отчет по сбербизнес",
    ]
    
    print("🧪 Тестирование краевых случаев поиска\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Тест {i}: '{test_case}'")
        print("-" * 50)
        
        try:
            # Генерируем SQL
            sql = agent.generate_sql_query(test_case)
            print(f"SQL: {sql}")
            
            # Выполняем запрос
            df = agent.execute_query(sql)
            print(f"Найдено записей: {len(df)}")
            
            if not df.empty:
                print("Найденные кампании:")
                for _, row in df.head(3).iterrows():
                    print(f"  - {row.get('campaign_name', 'N/A')}")
            
        except Exception as e:
            print(f"Ошибка: {e}")
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_edge_cases() 