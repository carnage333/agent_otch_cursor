from rag_system import RAGSystem

def test_complete_rag_system():
    rag = RAGSystem()
    
    # Тестируем все категории терминов
    test_queries = [
        # Бизнес-термины
        "ДМИК", "ФРК4", "маркетинг", "коммуникации", "брендинг",
        
        # Банковские термины
        "КИБ", "МКИБ", "ММБ", "СББОЛ", "ТАКБ", "ЧОД", "МАРК", "ОТР",
        
        # Метрики
        "AOV", "CAC", "CPI", "CPA", "BR", "ROI", "CTR", "CPC",
        
        # Кампании
        "ФРК4", "РКО кампании", "Бизнес-карты кампании",
        
        # Сложные запросы
        "отчет по КИБ", "анализ ММБ", "метрики СББОЛ", "эффективность МАРК"
    ]
    
    print("🧪 Тестирование полной RAG системы")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n🔍 Запрос: '{query}'")
        items = rag.search_knowledge(query)
        
        if items:
            print(f"✅ Найдено {len(items)} релевантных элементов:")
            for item in items[:3]:  # Показываем только первые 3
                print(f"   📝 {item.term}")
                print(f"   📖 {item.definition[:80]}...")
                if item.examples:
                    print(f"   💡 Примеры: {', '.join(item.examples)}")
                if item.related_terms:
                    print(f"   🔗 Связанные термины: {', '.join(item.related_terms)}")
                print()
        else:
            print("❌ Релевантные знания не найдены")
    
    # Подсчитываем общее количество терминов
    total_terms = 0
    categories = {}
    
    for category, items in rag.knowledge_base.items():
        categories[category] = len(items)
        total_terms += len(items)
    
    print("\n" + "=" * 60)
    print("📊 Статистика RAG системы:")
    print("=" * 60)
    
    for category, count in categories.items():
        print(f"📁 {category}: {count} терминов")
    
    print(f"\n🎯 Всего терминов в RAG системе: {total_terms}")
    
    # Тестируем улучшение отчета
    print("\n" + "=" * 60)
    print("📝 Тестирование улучшения отчета")
    print("=" * 60)
    
    test_report = "Это тестовый отчет о рекламных кампаниях."
    test_questions = ["КИБ", "AOV", "ММБ", "СББОЛ"]
    
    for question in test_questions:
        print(f"\n🔍 Запрос: {question}")
        enhanced_report = rag.enhance_report(test_report, question)
        print(f"✨ Улучшенный отчет:")
        print(enhanced_report[:300] + "..." if len(enhanced_report) > 300 else enhanced_report)

if __name__ == "__main__":
    test_complete_rag_system() 