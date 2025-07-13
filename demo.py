#!/usr/bin/env python3
"""
Демонстрация AI-агента отчетности по рекламным кампаниям
"""

import sys
import time
from ai_agent import MarketingAnalyticsAgent
from rag_system import RAGSystem

def print_header(title: str):
    """Красивый заголовок"""
    print("\n" + "="*60)
    print(f"🎯 {title}")
    print("="*60)

def print_section(title: str):
    """Заголовок секции"""
    print(f"\n📋 {title}")
    print("-" * 40)

def demo_agent_capabilities():
    """Демонстрация возможностей агента"""
    
    print_header("AI-агент отчетности | Демонстрация возможностей")
    
    # Инициализация агента
    print("🤖 Инициализация AI-агента...")
    agent = MarketingAnalyticsAgent()
    print("✅ Агент готов к работе!")
    
    # Демонстрация RAG системы
    print_section("RAG система - контекстные знания")
    rag = RAGSystem()
    
    test_queries = [
        "Что такое CTR?",
        "Как работает Яндекс.Директ?",
        "Что такое оптимизация бюджета?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Поиск знаний для: '{query}'")
        items = rag.search_knowledge(query)
        if items:
            for item in items:
                print(f"  📚 {item.term}: {item.definition}")
        else:
            print("  ❌ Знания не найдены")
    
    # Демонстрация анализа данных
    print_section("Анализ данных и генерация отчетов")
    
    demo_questions = [
        "Покажи общую статистику по рекламным кампаниям",
        "Какие кампании самые эффективные?",
        "Как работают разные площадки?",
        "Покажи тренды по дням"
    ]
    
    for i, question in enumerate(demo_questions, 1):
        print(f"\n{i}. Вопрос: {question}")
        print("🤖 Агент анализирует данные...")
        
        start_time = time.time()
        report = agent.process_question(question)
        end_time = time.time()
        
        print(f"⏱️ Время обработки: {end_time - start_time:.2f} сек")
        print("📊 Отчет:")
        print(report[:500] + "..." if len(report) > 500 else report)
    
    # Демонстрация агентности
    print_section("Уровни агентности")
    
    agent_capabilities = [
        "✅ Принятие роли - работает как аналитик маркетинга",
        "✅ Понимание запроса - анализ естественного языка",
        "✅ Планирование задач - генерация SQL запросов",
        "✅ Контекстные знания - предметная область маркетинга",
        "✅ Самостоятельные действия - анализ и генерация отчетов"
    ]
    
    for capability in agent_capabilities:
        print(f"  {capability}")
    
    # Статистика использования
    print_section("Статистика использования")
    
    history = agent.get_conversation_history()
    print(f"📈 Количество обработанных запросов: {len(history) // 2}")
    print(f"💬 Общая длина диалога: {len(history)} сообщений")
    
    # Рекомендации для комиссии
    print_section("Рекомендации для защиты перед комиссией")
    
    recommendations = [
        "🎯 Подчеркнуть высокий уровень агентности - система самостоятельно анализирует данные",
        "📊 Показать качество анализа - инсайты и рекомендации",
        "💬 Демонстрировать интерактивность - диалог на естественном языке",
        "🔧 Показать техническую реализацию - SQL генерация, RAG система",
        "📈 Продемонстрировать бизнес-ценность - автоматизация рутинных задач"
    ]
    
    for rec in recommendations:
        print(f"  {rec}")

def demo_web_interface():
    """Инструкции по запуску веб-интерфейса"""
    print_section("Веб-интерфейс")
    
    print("🌐 Для запуска веб-интерфейса выполните:")
    print("   streamlit run app.py")
    print("\n📱 Веб-приложение будет доступно по адресу:")
    print("   http://localhost:8501")
    
    print("\n🎨 Возможности веб-интерфейса:")
    web_features = [
        "💬 Интерактивный диалог с агентом",
        "📈 Быстрые отчеты по кнопкам",
        "📊 Интерактивные графики и визуализация",
        "⚙️ Настройки и управление системой"
    ]
    
    for feature in web_features:
        print(f"  {feature}")

def main():
    """Главная функция демонстрации"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--web":
        demo_web_interface()
    else:
        demo_agent_capabilities()
    
    print_header("Демонстрация завершена")
    print("🎉 AI-агент отчетности готов к использованию!")
    print("\n📞 Для запуска веб-интерфейса: python demo.py --web")

if __name__ == "__main__":
    main() 