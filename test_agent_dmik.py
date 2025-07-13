from ai_agent import MarketingAnalyticsAgent

def test_agent_with_dmik():
    agent = MarketingAnalyticsAgent()
    
    # Тестируем запрос с ДМИК
    test_questions = [
        "ДМИК",
        "отчет по ДМИК",
        "как работает ДМИК",
        "статистика по ДМИК"
    ]
    
    print("🧪 Тестирование агента с запросом ДМИК")
    print("=" * 60)
    
    for question in test_questions:
        print(f"\n🔍 Запрос: '{question}'")
        print("-" * 40)
        
        try:
            report = agent.process_question(question)
            print("✅ Отчет сгенерирован:")
            print(report[:500] + "..." if len(report) > 500 else report)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    test_agent_with_dmik() 