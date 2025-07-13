from rag_system import RAGSystem

def test_extended_rag_system():
    rag = RAGSystem()
    
    # Тестируем поиск различных терминов
    test_queries = [
        "ДМИК",
        "ФРК4", 
        "ФРК",
        "маркетинг",
        "коммуникации",
        "брендинг",
        "исследования",
        "рекламные кампании",
        "мероприятия",
        "медиаресурсы",
        "продуктовые гипотезы",
        "конверсия",
        "рост пользователей",
        "команды",
        "подразделения",
        "потребители",
        "конкуренты",
        "РКО кампании",
        "РБИДОС кампании",
        "Бизнес-карты кампании",
        "Бизнес-кредиты кампании"
    ]
    
    print("🧪 Тестирование расширенной RAG системы")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n🔍 Запрос: '{query}'")
        items = rag.search_knowledge(query)
        
        if items:
            print(f"✅ Найдено {len(items)} релевантных элементов:")
            for item in items:
                print(f"   📝 {item.term}")
                print(f"   📖 {item.definition[:100]}...")
                if item.examples:
                    print(f"   💡 Примеры: {', '.join(item.examples)}")
                if item.related_terms:
                    print(f"   🔗 Связанные термины: {', '.join(item.related_terms)}")
                print()
        else:
            print("❌ Релевантные знания не найдены")
    
    # Тестируем сложные запросы
    print("\n" + "=" * 60)
    print("🔍 Тестирование сложных запросов")
    print("=" * 60)
    
    complex_queries = [
        "отчет по ФРК4",
        "анализ маркетинга",
        "эффективность коммуникаций",
        "брендинг кампании",
        "исследования потребителей",
        "рекламные кампании ДМиК",
        "мероприятия по продвижению",
        "медиаресурсы компании",
        "продуктовые гипотезы тестирование",
        "конверсия из рекламных каналов",
        "рост пользователей продуктов",
        "команды разработки",
        "подразделения маркетинга",
        "анализ конкурентов",
        "РКО кампании эффективность"
    ]
    
    for query in complex_queries:
        print(f"\n🔍 Сложный запрос: '{query}'")
        items = rag.search_knowledge(query)
        
        if items:
            print(f"✅ Найдено {len(items)} релевантных элементов:")
            for item in items[:3]:  # Показываем только первые 3
                print(f"   📝 {item.term}")
                print(f"   📖 {item.definition[:80]}...")
        else:
            print("❌ Релевантные знания не найдены")

if __name__ == "__main__":
    test_extended_rag_system() 