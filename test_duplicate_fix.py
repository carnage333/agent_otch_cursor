from ai_agent import MarketingAnalyticsAgent

def test_report_generation():
    """Тестирует генерацию отчета на предмет дублирования"""
    
    print("🧪 Тестирование генерации отчета...")
    
    agent = MarketingAnalyticsAgent()
    
    # Тестируем запрос
    question = "сделай отчет по фрк4"
    result = agent.process_question(question)
    
    print("📊 Результат:")
    print(result)
    
    # Проверяем на дублирование заголовков
    lines = result.split('\n')
    headers = []
    
    for line in lines:
        if line.startswith('## 📋') or line.startswith('## 📱') or line.startswith('## 📊'):
            headers.append(line)
    
    print(f"\n🔍 Найдено заголовков: {len(headers)}")
    for i, header in enumerate(headers, 1):
        print(f"{i}. {header}")
    
    # Проверяем дубликаты
    unique_headers = set(headers)
    if len(headers) != len(unique_headers):
        print("❌ Обнаружены дублирующиеся заголовки!")
        duplicates = [h for h in headers if headers.count(h) > 1]
        print("Дубликаты:", duplicates)
    else:
        print("✅ Дубликатов заголовков не найдено")

if __name__ == "__main__":
    test_report_generation() 