#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправлений
"""

from ai_agent import MarketingAnalyticsAgent

def test_sql_display():
    """Тест отображения SQL в отчетах"""
    print("🔍 Тестирование отображения SQL в отчетах...")
    
    agent = MarketingAnalyticsAgent()
    
    # Тест 1: Запрос динамики по дням
    question = "Покажи динамику по дням по rko_spring2024"
    print(f"\n📝 Запрос: {question}")
    
    report = agent.process_question(question)
    print("\n📊 Отчет:")
    print(report)
    
    # Проверяем, есть ли SQL в отчете
    if "🔍 SQL запрос" in report:
        print("✅ SQL запрос отображается в отчете")
    else:
        print("❌ SQL запрос НЕ отображается в отчете")
    
    # Тест 2: Запрос воронки
    question2 = "Покажи воронку конверсии для rko_spring2024"
    print(f"\n📝 Запрос: {question2}")
    
    report2 = agent.process_question(question2)
    print("\n📊 Отчет:")
    print(report2)
    
    # Проверяем, есть ли SQL в отчете
    if "🔍 SQL запрос" in report2:
        print("✅ SQL запрос отображается в отчете воронки")
    else:
        print("❌ SQL запрос НЕ отображается в отчете воронки")

def test_dynamic_query():
    """Тест правильной обработки запросов динамики"""
    print("\n🔍 Тестирование обработки запросов динамики...")
    
    agent = MarketingAnalyticsAgent()
    
    # Тест: запрос динамики с названием кампании
    question = "Покажи динамику по дням по rko_spring2024"
    print(f"\n📝 Запрос: {question}")
    
    # Генерируем SQL
    sql_query = agent.generate_sql_query(question)
    print(f"\n🔍 Сгенерированный SQL:")
    print(sql_query)
    
    # Проверяем, содержит ли SQL фильтр по кампании
    if "rko_spring2024" in sql_query:
        print("✅ SQL содержит фильтр по кампании rko_spring2024")
    else:
        print("❌ SQL НЕ содержит фильтр по кампании rko_spring2024")
    
    # Выполняем запрос
    df = agent.execute_query(sql_query)
    print(f"\n📊 Результат запроса:")
    print(f"Количество строк: {len(df)}")
    if not df.empty:
        print(f"Колонки: {list(df.columns)}")
        print(f"Первые 3 строки:")
        print(df.head(3))

if __name__ == "__main__":
    print("🚀 Начинаем тестирование исправлений...")
    
    try:
        test_sql_display()
        test_dynamic_query()
        print("\n✅ Все тесты завершены!")
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc() 