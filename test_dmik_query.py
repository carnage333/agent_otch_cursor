#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent import MarketingAnalyticsAgent

def test_dmik_query():
    """Тестируем запрос 'Что такое ДМИК?'"""
    print("🧪 Тестирование запроса 'Что такое ДМИК?'")
    print("=" * 60)
    
    # Создаем агента
    agent = MarketingAnalyticsAgent()
    
    # Тестовый запрос
    question = "Что такое ДМИК?"
    
    print(f"📝 Запрос: {question}")
    print("-" * 40)
    
    # Обрабатываем запрос
    response = agent.process_question(question)
    
    print("📊 Результат:")
    print("=" * 60)
    print(response)
    print("=" * 60)
    
    # Анализируем логику
    print("\n🔍 Анализ логики:")
    print("-" * 40)
    
    # Проверяем детекцию терминов
    question_lower = question.lower()
    is_asking_about_terms = any(word in question_lower for word in [
        "что такое", "как считается", "формула", "метрика", "определение",
        "расшифровка", "означает", "означает ли", "что значит"
    ])
    
    print(f"✅ Детекция терминов: {is_asking_about_terms}")
    
    # Генерируем SQL для проверки данных
    sql_query = agent.generate_sql_query(question)
    print(f"🔍 SQL запрос: {sql_query}")
    
    # Выполняем запрос для проверки данных
    df = agent.execute_query(sql_query)
    has_data = len(df) > 0
    print(f"📊 Есть данные: {has_data} (строк: {len(df)})")
    
    # Проверяем логику RAG
    should_use_rag = not has_data or is_asking_about_terms
    print(f"🤖 Использовать RAG: {should_use_rag}")
    
    print("\n✅ Тест завершен!")

if __name__ == "__main__":
    test_dmik_query() 