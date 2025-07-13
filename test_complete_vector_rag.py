from simple_vector_rag import SimpleVectorRAG

def test_complete_vector_rag():
    print("🧪 Тестирование полной векторной RAG системы")
    print("=" * 60)
    
    # Инициализируем RAG
    rag = SimpleVectorRAG()
    
    # Тестируем все категории терминов
    test_queries = [
        # Банковские термины
        "КИБ", "МКИБ", "ММБ", "СББОЛ", "ТАКБ", "ЧОД", "МАРК", "ОТР", "РКО",
        
        # Метрики
        "AOV", "CAC", "CPI", "CPA", "BR", "CTR", "CPC", "CPM", "ROI", "CPL", "CPO", "CPS", "CPV", "CR", "ДРР",
        
        # Бизнес-термины
        "ДМИК", "ФРК4", "маркетинг", "коммуникации", "брендинг", "УТП",
        
        # Платформы
        "Яндекс.Директ", "VK Реклама", "Telegram Ads", "MyTarget",
        
        # Кампании
        "РКО кампании", "РБИДОС кампании", "Бизнес-карты кампании", "Бизнес-кредиты кампании"
    ]
    
    print(f"🔍 Тестируем {len(test_queries)} запросов...")
    
    found_count = 0
    total_queries = len(test_queries)
    
    for query in test_queries:
        results = rag.search(query, top_k=1)
        
        if results:
            found_count += 1
            print(f"✅ {query}: найдено")
        else:
            print(f"❌ {query}: не найдено")
    
    print(f"\n📊 Результаты:")
    print(f"   Найдено: {found_count}/{total_queries}")
    print(f"   Покрытие: {(found_count/total_queries)*100:.1f}%")
    
    # Тестируем улучшение отчета
    print(f"\n📝 Тестирование улучшения отчета:")
    test_report = "Это тестовый отчет о рекламных кампаниях."
    test_question = "ДМИК"
    
    enhanced_report = rag.enhance_report(test_report, test_question)
    print(f"🔍 Запрос: {test_question}")
    print("✨ Улучшенный отчет:")
    print(enhanced_report[:300] + "..." if len(enhanced_report) > 300 else enhanced_report)
    
    print(f"\n✅ Полная векторная RAG система работает!")

if __name__ == "__main__":
    test_complete_vector_rag() 