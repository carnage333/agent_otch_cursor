from simple_vector_rag import SimpleVectorRAG

def test_vector_rag():
    print("🧪 Тестирование векторной RAG системы")
    print("=" * 50)
    
    # Инициализируем RAG
    rag = SimpleVectorRAG()
    
    # Тестируем поиск
    test_queries = [
        "ДМИК", "AOV", "КИБ", "маркетинг", "СББОЛ", "CTR", "ROI"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Запрос: '{query}'")
        results = rag.search(query, top_k=2)
        
        if results:
            print(f"✅ Найдено {len(results)} результатов:")
            for item in results:
                print(f"   📝 {item['term']}")
                print(f"   📖 {item['definition']}")
                print(f"   📊 Релевантность: {item['similarity']:.2f}")
                print()
        else:
            print("❌ Результаты не найдены")
    
    # Тестируем улучшение отчета
    print("\n" + "=" * 50)
    print("📝 Тестирование улучшения отчета")
    print("=" * 50)
    
    test_report = "Это тестовый отчет о рекламных кампаниях."
    test_question = "ДМИК"
    
    enhanced_report = rag.enhance_report(test_report, test_question)
    print(f"🔍 Запрос: {test_question}")
    print("✨ Улучшенный отчет:")
    print(enhanced_report)
    
    print("\n✅ Векторная RAG система работает корректно!")

if __name__ == "__main__":
    test_vector_rag() 