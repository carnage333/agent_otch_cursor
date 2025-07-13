#!/usr/bin/env python3
"""
Тестирование интеграции с OpenAI GPT
"""

import os
import sys
from ai_agent import MarketingAnalyticsAgent

def test_openai_integration():
    """Тестирование интеграции с OpenAI"""
    
    print("🧪 Тестирование интеграции с OpenAI GPT")
    print("=" * 50)
    
    # Проверяем наличие API ключа
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY не найден в переменных окружения")
        print("💡 Установите переменную окружения:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    print("✅ OpenAI API ключ найден")
    
    # Инициализируем агента
    print("\n🤖 Инициализация агента...")
    agent = MarketingAnalyticsAgent()
    
    if not agent.openai_available:
        print("❌ OpenAI недоступен в агенте")
        return False
    
    print("✅ OpenAI доступен в агенте")
    
    # Тестируем улучшение отчета
    print("\n📊 Тестирование улучшения отчета...")
    
    test_report = """# 📊 Отчет по кампании ФРК4

## 📈 Основные показатели
- Показы: 1,234,567
- Клики: 12,345
- CTR: 1.0%
- CPC: 45.67 ₽
- Расход: 564,123 ₽

## 📋 Заключение
Кампания показывает средние результаты."""

    enhanced_report = agent.enhance_report_with_openai(
        test_report, 
        "Покажи отчет по кампании ФРК4"
    )
    
    print("📝 Улучшенный отчет:")
    print("-" * 40)
    print(enhanced_report)
    print("-" * 40)
    
    # Тестируем генерацию инсайтов
    print("\n💡 Тестирование генерации инсайтов...")
    
    import pandas as pd
    test_data = pd.DataFrame({
        'campaign_name': ['ФРК4_Бизнес', 'ФРК4_РКО'],
        'impressions': [1000000, 500000],
        'clicks': [10000, 3000],
        'cost': [400000, 120000],
        'ctr': [1.0, 0.6],
        'cpc': [40.0, 40.0]
    })
    
    insights = agent.generate_insights_with_openai(
        test_data, 
        "Проанализируй эффективность кампаний"
    )
    
    print("🔍 Сгенерированные инсайты:")
    for insight in insights:
        print(f"  {insight}")
    
    # Тестируем генерацию рекомендаций
    print("\n🎯 Тестирование генерации рекомендаций...")
    
    recommendations = agent.generate_recommendations_with_openai(
        test_data, 
        "Дай рекомендации по оптимизации"
    )
    
    print("📋 Сгенерированные рекомендации:")
    for rec in recommendations:
        print(f"  {rec}")
    
    print("\n✅ Тестирование завершено успешно!")
    return True

def test_fallback_to_rag():
    """Тестирование fallback на RAG систему"""
    
    print("\n🔄 Тестирование fallback на RAG систему")
    print("=" * 50)
    
    # Временно убираем API ключ
    original_key = os.getenv('OPENAI_API_KEY')
    os.environ.pop('OPENAI_API_KEY', None)
    
    # Инициализируем агента
    agent = MarketingAnalyticsAgent()
    
    if agent.rag_system is not None:
        print("✅ RAG система доступна как fallback")
        
        # Тестируем RAG
        test_report = "Отчет по кампании"
        enhanced = agent.rag_system.enhance_report(test_report, "Что такое CTR?")
        
        if enhanced != test_report:
            print("✅ RAG система работает корректно")
        else:
            print("⚠️ RAG система не улучшила отчет")
    else:
        print("❌ RAG система недоступна")
    
    # Восстанавливаем API ключ
    if original_key:
        os.environ['OPENAI_API_KEY'] = original_key

if __name__ == "__main__":
    print("🚀 Запуск тестирования интеграции с OpenAI")
    
    # Основное тестирование
    success = test_openai_integration()
    
    # Тестирование fallback
    test_fallback_to_rag()
    
    if success:
        print("\n🎉 Все тесты пройдены успешно!")
        print("💡 Агент готов к работе с OpenAI GPT")
    else:
        print("\n⚠️ Некоторые тесты не пройдены")
        print("💡 Проверьте настройки OpenAI API") 