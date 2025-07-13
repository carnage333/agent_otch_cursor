#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ai_agent import MarketingAnalyticsAgent

def test_frk4():
    """Тестирование поиска ФРК4"""
    agent = MarketingAnalyticsAgent()
    
    # Тестовые вопросы
    test_questions = [
        "сделай отчет по фрк4",
        "анализ кампании фрк4",
        "статистика по ФРК4",
        "покажи данные по фрк4 бизнес-фест"
    ]
    
    print("🧪 Тестирование поиска ФРК4\n")
    
    for i, question in enumerate(test_questions, 1):
        print(f"Тест {i}: '{question}'")
        print("-" * 50)
        
        try:
            result = agent.process_question(question)
            print(result)
        except Exception as e:
            print(f"Ошибка: {e}")
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_frk4() 