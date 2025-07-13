#!/usr/bin/env python3
"""
Тестирование бесплатных LLM для агента отчетности
"""

import argparse
import os
import sys
from ai_agent import MarketingAnalyticsAgent

def test_ollama():
    """Тестирование Ollama"""
    print("🏠 Тестирование Ollama (локальный LLM)")
    print("=" * 50)
    
    try:
        import ollama
        
        # Проверяем доступность Ollama
        try:
            models = ollama.list()
            print(f"✅ Ollama доступен. Модели: {[m['name'] for m in models['models']]}")
        except Exception as e:
            print(f"❌ Ollama недоступен: {e}")
            print("💡 Установите Ollama: https://ollama.ai/")
            return False
        
        # Инициализируем агента
        agent = MarketingAnalyticsAgent()
        
        # Тестируем улучшение отчета
        test_report = """# 📊 Отчет по кампании ФРК4

## 📈 Основные показатели
- Показы: 1,234,567
- Клики: 12,345
- CTR: 1.0%
- CPC: 45.67 ₽
- Расход: 564,123 ₽"""

        enhanced_report = agent.enhance_report_with_ollama(
            test_report, 
            "Покажи отчет по кампании ФРК4"
        )
        
        print("📝 Улучшенный отчет:")
        print("-" * 40)
        print(enhanced_report)
        print("-" * 40)
        
        return True
        
    except ImportError:
        print("❌ Ollama не установлен")
        print("💡 Установите: pip install ollama")
        return False

def test_huggingface():
    """Тестирование Hugging Face"""
    print("🌐 Тестирование Hugging Face (онлайн LLM)")
    print("=" * 50)
    
    try:
        import requests
        
        # Проверяем токен
        token = os.getenv('HUGGINGFACE_TOKEN')
        if not token:
            print("❌ HUGGINGFACE_TOKEN не найден")
            print("💡 Установите переменную окружения:")
            print("   export HUGGINGFACE_TOKEN='hf_your-token-here'")
            return False
        
        print("✅ Hugging Face токен найден")
        
        # Инициализируем агента
        agent = MarketingAnalyticsAgent()
        
        # Тестируем улучшение отчета
        test_report = """# 📊 Отчет по кампании ФРК4

## 📈 Основные показатели
- Показы: 1,234,567
- Клики: 12,345
- CTR: 1.0%
- CPC: 45.67 ₽
- Расход: 564,123 ₽"""

        enhanced_report = agent.enhance_report_with_huggingface(
            test_report, 
            "Покажи отчет по кампании ФРК4"
        )
        
        print("📝 Улучшенный отчет:")
        print("-" * 40)
        print(enhanced_report)
        print("-" * 40)
        
        return True
        
    except ImportError:
        print("❌ requests не установлен")
        print("💡 Установите: pip install requests")
        return False

def test_local_templates():
    """Тестирование локальных шаблонов"""
    print("📝 Тестирование локальных шаблонов")
    print("=" * 50)
    
    # Инициализируем агента
    agent = MarketingAnalyticsAgent()
    
    # Тестируем улучшение отчета
    test_report = """# 📊 Отчет по кампании ФРК4

## 📈 Основные показатели
- Показы: 1,234,567
- Клики: 12,345
- CTR: 1.0%
- CPC: 45.67 ₽
- Расход: 564,123 ₽"""

    # Тестовые данные
    data_summary = {
        "total_impressions": 1234567,
        "total_clicks": 12345,
        "total_cost": 564123,
        "avg_ctr": 1.0,
        "avg_cpc": 45.67
    }

    enhanced_report = agent.enhance_report_with_local_llm(
        test_report, 
        "Покажи отчет по кампании ФРК4",
        data_summary
    )
    
    print("📝 Улучшенный отчет:")
    print("-" * 40)
    print(enhanced_report)
    print("-" * 40)
    
    return True

def test_all_free_llm():
    """Тестирование всех бесплатных LLM"""
    print("🆓 Тестирование всех бесплатных LLM")
    print("=" * 60)
    
    results = {}
    
    # Тестируем Ollama
    print("\n1️⃣ Тестирование Ollama...")
    results['ollama'] = test_ollama()
    
    # Тестируем Hugging Face
    print("\n2️⃣ Тестирование Hugging Face...")
    results['huggingface'] = test_huggingface()
    
    # Тестируем локальные шаблоны
    print("\n3️⃣ Тестирование локальных шаблонов...")
    results['local'] = test_local_templates()
    
    # Итоги
    print("\n📊 Результаты тестирования:")
    print("=" * 40)
    
    for llm, success in results.items():
        status = "✅ Работает" if success else "❌ Не работает"
        print(f"{llm.upper():15} {status}")
    
    working_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n🎯 Итого: {working_count}/{total_count} LLM работают")
    
    if working_count > 0:
        print("✅ Агент готов к работе с бесплатными LLM!")
    else:
        print("⚠️ Ни один бесплатный LLM не работает")
        print("💡 Проверьте настройки или используйте локальные шаблоны")

def main():
    parser = argparse.ArgumentParser(description='Тестирование бесплатных LLM')
    parser.add_argument('--type', choices=['ollama', 'huggingface', 'local', 'all'], 
                       default='all', help='Тип LLM для тестирования')
    
    args = parser.parse_args()
    
    print("🚀 Запуск тестирования бесплатных LLM")
    
    if args.type == 'ollama':
        test_ollama()
    elif args.type == 'huggingface':
        test_huggingface()
    elif args.type == 'local':
        test_local_templates()
    else:
        test_all_free_llm()

if __name__ == "__main__":
    main() 