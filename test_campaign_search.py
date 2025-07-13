import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent import MarketingAnalyticsAgent

def test_campaign_search():
    print("🧪 Тестирование улучшенного поиска кампаний...")
    
    agent = MarketingAnalyticsAgent()
    
    # Тест 1: Различные варианты написания ФРК4
    test_cases = [
        "сделай отчет по фрк4",
        "анализ кампании ФРК-4", 
        "статистика по ФРК4",
        "отчет по фрк 4",
        "покажи данные по ФРК-4",
        "анализ кампании фрк4"
    ]
    
    print("\n📋 Тест поиска кампаний ФРК4:")
    for i, question in enumerate(test_cases, 1):
        sql = agent.generate_sql_query(question)
        print(f"{i}. Вопрос: {question}")
        print(f"   SQL: {sql}")
        print()
    
    # Тест 2: Общая статистика
    print("📊 Тест общей статистики:")
    general_questions = [
        "покажи общую статистику",
        "общие показатели по кампаниям",
        "итого по всем кампаниям",
        "общая статистика"
    ]
    
    for i, question in enumerate(general_questions, 1):
        sql = agent.generate_sql_query(question)
        print(f"{i}. Вопрос: {question}")
        print(f"   SQL: {sql}")
        print()
    
    # Тест 3: Выполнение реального запроса
    print("🔍 Тест выполнения запроса:")
    test_question = "сделай отчет по фрк4"
    sql = agent.generate_sql_query(test_question)
    df = agent.execute_query(sql)
    
    print(f"Вопрос: {test_question}")
    print(f"SQL: {sql}")
    print(f"Найдено записей: {len(df)}")
    
    if not df.empty:
        print("Первые результаты:")
        print(df.head())
    else:
        print("Данные не найдены")
    
    # Тест 4: Проверка извлечения поисковых терминов
    print("\n🔍 Тест извлечения поисковых терминов:")
    test_questions = [
        "сделай отчет по фрк4",
        "анализ кампании годовой performance",
        "статистика по бизнес-карты"
    ]
    
    for question in test_questions:
        terms = agent._extract_search_terms(question)
        print(f"Вопрос: {question}")
        print(f"Термины: {terms}")
        print()
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    test_campaign_search() 