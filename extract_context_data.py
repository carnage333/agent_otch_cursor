import docx
import re
from typing import List, Dict

def extract_from_docx(file_path: str) -> str:
    """Извлекает текст из Word документа"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return ""

def extract_terms_from_text(text: str) -> List[Dict]:
    """Извлекает термины и их определения из текста"""
    terms = []
    
    # Ищем паттерны типа "ТЕРМИН: определение" или "ТЕРМИН - определение"
    patterns = [
        r'([А-Я][А-Я\s]+):\s*(.+)',
        r'([А-Я][А-Я\s]+)\s*-\s*(.+)',
        r'([А-Я][А-Я\s]+)\s*=\s*(.+)',
    ]
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                term = match.group(1).strip()
                definition = match.group(2).strip()
                
                # Фильтруем слишком короткие термины
                if len(term) > 2 and len(definition) > 10:
                    terms.append({
                        'term': term,
                        'definition': definition,
                        'line': line
                    })
                break
    
    return terms

def compare_with_rag():
    """Сравнивает извлеченные термины с RAG системой"""
    from rag_system import RAGSystem
    
    # Извлекаем данные из Word файла
    text = extract_from_docx("контекстные данные.docx")
    if not text:
        print("❌ Не удалось прочитать файл контекстные данные.docx")
        return
    
    print("📄 Извлеченный текст из файла:")
    print("=" * 60)
    print(text[:1000] + "..." if len(text) > 1000 else text)
    print("\n" + "=" * 60)
    
    # Извлекаем термины
    extracted_terms = extract_terms_from_text(text)
    
    print(f"\n🔍 Найдено {len(extracted_terms)} терминов в файле:")
    for i, term in enumerate(extracted_terms, 1):
        print(f"{i}. {term['term']}: {term['definition'][:100]}...")
    
    # Проверяем, что есть в RAG системе
    rag = RAGSystem()
    rag_terms = []
    
    for category, items in rag.knowledge_base.items():
        for item in items:
            rag_terms.append(item.term)
    
    print(f"\n📚 В RAG системе есть {len(rag_terms)} терминов:")
    for i, term in enumerate(rag_terms, 1):
        print(f"{i}. {term}")
    
    # Находим термины, которых нет в RAG
    extracted_term_names = [term['term'] for term in extracted_terms]
    missing_terms = []
    
    for term in extracted_terms:
        term_name = term['term']
        found_in_rag = False
        
        for rag_term in rag_terms:
            if term_name.lower() in rag_term.lower() or rag_term.lower() in term_name.lower():
                found_in_rag = True
                break
        
        if not found_in_rag:
            missing_terms.append(term)
    
    print(f"\n❌ Термины, которых НЕТ в RAG системе ({len(missing_terms)}):")
    for term in missing_terms:
        print(f"- {term['term']}: {term['definition'][:80]}...")
    
    if missing_terms:
        print(f"\n💡 Рекомендация: Добавить {len(missing_terms)} терминов в RAG систему")
    else:
        print("\n✅ Все термины из файла уже есть в RAG системе!")

if __name__ == "__main__":
    compare_with_rag() 