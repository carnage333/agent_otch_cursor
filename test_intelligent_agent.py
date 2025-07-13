#!/usr/bin/env python3
"""
Тестовый скрипт для демонстрации интеллектуального агента
"""

from intelligent_agent import IntelligentMarketingAgent

def test_agent():
    """Тестирование интеллектуального агента"""
    print("🤖 Тестирование интеллектуального агента")
    print("=" * 50)
    
    # Инициализируем агента
    agent = IntelligentMarketingAgent()
    
    # Тестовые вопросы разных типов
    test_questions = [
        "Покажи отчет по ФРК1",
        "Что такое CTR?",
        "Сравни кампании",
        "Дай рекомендации",
        "Покажи общую статистику",
        "Как работает кампания Годовой performance?",
        "Объясни метрику CPC",
        "Какие кампании самые эффективные?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Вопрос: {question}")
        print("-" * 30)
        
        try:
            response = agent.process_question(question)
            print(f"Ответ: {response}")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_agent() 