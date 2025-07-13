#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ai_agent import MarketingAnalyticsAgent

def test_agent():
    """Тестирование исправленного агента"""
    agent = MarketingAnalyticsAgent()
    
    # Тестовые вопросы
    test_questions = [
        "как дела",  # Общий вопрос - должен вернуть сообщение об уточнении
        "покажи общую статистику",  # Конкретный запрос
        "анализ по кампаниям",  # Конкретный запрос
        "эффективность площадок",  # Конкретный запрос
        "топ кампаний",  # Конкретный запрос
        "тренды по дням"  # Конкретный запрос
    ]
    
    print("🧪 Тестирование исправленного агента\n")
    
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
    test_agent() 