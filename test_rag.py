from rag_system import RAGSystem

def test_rag_system():
    rag = RAGSystem()
    
    # Тестируем поиск ДМИК
    test_queries = [
        "ДМИК",
        "дмик", 
        "Договор на комплексное обслуживание",
        "РКО",
        "рко",
        "Бизнес-карты"
    ]
    
    print("🧪 Тестирование RAG системы")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n🔍 Запрос: '{query}'")
        items = rag.search_knowledge(query)
        
        if items:
            print(f"✅ Найдено {len(items)} релевантных элементов:")
            for item in items:
                print(f"   📝 {item.term}")
                print(f"   📖 {item.definition}")
                if item.examples:
                    print(f"   💡 Примеры: {', '.join(item.examples)}")
                if item.related_terms:
                    print(f"   🔗 Связанные термины: {', '.join(item.related_terms)}")
                print()
        else:
            print("❌ Релевантные знания не найдены")
    
    # Тестируем улучшение отчета
    print("\n" + "=" * 50)
    print("📊 Тестирование улучшения отчета")
    print("=" * 50)
    
    test_report = "Это тестовый отчет о рекламных кампаниях."
    test_question = "ДМИК"
    
    enhanced_report = rag.enhance_report(test_report, test_question)
    print(f"\n📝 Оригинальный отчет: {test_report}")
    print(f"\n🔍 Запрос: {test_question}")
    print(f"\n✨ Улучшенный отчет:")
    print(enhanced_report)

if __name__ == "__main__":
    test_rag_system() 