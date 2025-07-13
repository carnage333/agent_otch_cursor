from ai_agent import MarketingAnalyticsAgent

def test_agent():
    """Тестирование агента с разными запросами"""
    
    agent = MarketingAnalyticsAgent()
    
    test_questions = [
        "Покажи общую статистику по рекламным кампаниям",
        "Покажи статистику по продукту РКО",
        "Покажи отчет по кампании ФРК4 Бизнес-Фест",
        "Анализ кампании Годовой performance",
        "Какие кампании самые эффективные?",
        "Как работают разные площадки?"
    ]
    
    print("=== ТЕСТИРОВАНИЕ AI-АГЕНТА ===")
    print()
    
    for i, question in enumerate(test_questions, 1):
        print(f"Тест {i}: {question}")
        print("-" * 50)
        
        try:
            # Получаем ответ от агента
            response = agent.process_question(question)
            
            # Проверяем наличие SQL запроса
            if "## 🔍 SQL запрос" in response:
                print("✅ SQL запрос найден")
                
                # Извлекаем SQL запрос
                sql_start = response.find("## 🔍 SQL запрос")
                sql_end = response.find("```", sql_start + len("## 🔍 SQL запрос"))
                if sql_end != -1:
                    sql_end = response.find("\n```", sql_end)
                    if sql_end != -1:
                        sql_query = response[sql_start:sql_end + 4]
                        sql_content = sql_query.replace("## 🔍 SQL запрос\n```sql\n", "").replace("\n```", "")
                        print(f"SQL: {sql_content[:100]}...")
            else:
                print("❌ SQL запрос не найден")
            
            # Показываем начало ответа
            response_preview = response[:300] + "..." if len(response) > 300 else response
            print(f"Ответ: {response_preview}")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    test_agent() 