import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_fixed import SimpleMarketingAgent

def test_agent():
    print("🧪 Тестирование улучшенного AI агента...")
    
    agent = SimpleMarketingAgent()
    
    # Тест 1: Поиск по кампании с разными вариантами написания
    test_cases = [
        "сделай отчет по фрк4",
        "анализ кампании ФРК-4", 
        "статистика по ФРК4",
        "отчет по фрк 4",
        "покажи данные по ФРК-4"
    ]
    
    print("\n📋 Тест поиска кампаний:")
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
        "итого по всем кампаниям"
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
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    test_agent() 