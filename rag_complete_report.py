from rag_system import RAGSystem
from typing import Dict, List

def generate_rag_report():
    """Генерирует полный отчет о RAG системе"""
    rag = RAGSystem()
    
    print("📊 ПОЛНЫЙ ОТЧЕТ О RAG СИСТЕМЕ")
    print("=" * 80)
    
    # Подсчитываем статистику
    total_terms = 0
    categories_stats = {}
    
    for category, items in rag.knowledge_base.items():
        categories_stats[category] = len(items)
        total_terms += len(items)
    
    print(f"🎯 ВСЕГО ТЕРМИНОВ В RAG СИСТЕМЕ: {total_terms}")
    print("\n📁 РАСПРЕДЕЛЕНИЕ ПО КАТЕГОРИЯМ:")
    print("-" * 40)
    
    for category, count in categories_stats.items():
        print(f"   {category}: {count} терминов")
    
    print("\n" + "=" * 80)
    print("📝 ДЕТАЛЬНЫЙ СПИСОК ТЕРМИНОВ ПО КАТЕГОРИЯМ:")
    print("=" * 80)
    
    for category, items in rag.knowledge_base.items():
        print(f"\n🔹 КАТЕГОРИЯ: {category.upper()} ({len(items)} терминов)")
        print("-" * 50)
        
        for i, item in enumerate(items, 1):
            print(f"{i:2d}. {item.term}")
            print(f"    📖 {item.definition}")
            if item.examples:
                print(f"    💡 Примеры: {', '.join(item.examples)}")
            if item.related_terms:
                print(f"    🔗 Связанные: {', '.join(item.related_terms)}")
            print()
    
    print("=" * 80)
    print("✅ ИТОГОВАЯ СТАТИСТИКА:")
    print("=" * 80)
    
    print(f"📚 Всего терминов: {total_terms}")
    print(f"📁 Категорий: {len(categories_stats)}")
    
    # Анализируем покрытие из файла контекстных данных
    print(f"\n📄 АНАЛИЗ ПОКРЫТИЯ КОНТЕКСТНЫХ ДАННЫХ:")
    print("-" * 40)
    
    # Термины из файла контекстных данных
    file_terms = [
        "КИБ", "МАРК", "МКИБ", "ММБ", "ОТР", "СББОЛ", "ТАКБ", "ФРК", "ЧОД",
        "AOV", "CAC", "CPI", "CPA", "BR", "Average page view duration"
    ]
    
    found_in_rag = 0
    missing_terms = []
    
    for term in file_terms:
        items = rag.search_knowledge(term)
        if items:
            found_in_rag += 1
        else:
            missing_terms.append(term)
    
    print(f"✅ Найдено в RAG: {found_in_rag}/{len(file_terms)} терминов")
    print(f"❌ Отсутствует в RAG: {len(missing_terms)} терминов")
    
    if missing_terms:
        print(f"📋 Отсутствующие термины: {', '.join(missing_terms)}")
    
    coverage_percentage = (found_in_rag / len(file_terms)) * 100
    print(f"📊 Покрытие: {coverage_percentage:.1f}%")
    
    print("\n" + "=" * 80)
    print("🎯 РЕКОМЕНДАЦИИ:")
    print("=" * 80)
    
    if coverage_percentage >= 90:
        print("✅ Отличное покрытие! RAG система содержит большинство терминов из контекстных данных.")
    elif coverage_percentage >= 70:
        print("⚠️  Хорошее покрытие, но есть возможности для улучшения.")
    else:
        print("❌ Низкое покрытие. Рекомендуется добавить недостающие термины.")
    
    print(f"\n💡 RAG система готова к использованию в AI агенте!")
    print(f"💡 Все термины автоматически используются для улучшения отчетов.")
    print(f"💡 Система поддерживает поиск по частичному совпадению.")

if __name__ == "__main__":
    generate_rag_report() 