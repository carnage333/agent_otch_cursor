import docx
import re
from typing import List, Dict

def extract_all_from_docx(file_path: str) -> str:
    """Извлекает ВСЕ данные из Word документа"""
    try:
        doc = docx.Document(file_path)
        full_text = ""
        
        print("📄 Извлечение всех данных из файла...")
        
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:
                full_text += text + "\n"
        
        print(f"✅ Извлечено {len(full_text)} символов")
        return full_text
        
    except Exception as e:
        print(f"❌ Ошибка при чтении файла: {e}")
        return ""

def extract_all_terms(text: str) -> List[Dict]:
    """Извлекает ВСЕ термины и определения из текста"""
    terms = []
    
    # Разбиваем на строки
    lines = text.split('\n')
    
    print("🔍 Поиск всех терминов и определений...")
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
        
        # Ищем различные паттерны
        patterns = [
            # ТЕРМИН: определение
            r'^([А-Я][А-Я\s\d]+):\s*(.+)',
            # ТЕРМИН - определение  
            r'^([А-Я][А-Я\s\d]+)\s*-\s*(.+)',
            # ТЕРМИН = определение
            r'^([А-Я][А-Я\s\d]+)\s*=\s*(.+)',
            # ТЕРМИН (определение)
            r'^([А-Я][А-Я\s\d]+)\s*\((.+)\)',
            # ТЕРМИН. определение
            r'^([А-Я][А-Я\s\d]+)\.\s*(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                term = match.group(1).strip()
                definition = match.group(2).strip()
                
                # Фильтруем слишком короткие или нерелевантные
                if (len(term) > 2 and len(definition) > 10 and 
                    not term.isdigit() and not definition.isdigit()):
                    
                    terms.append({
                        'term': term,
                        'definition': definition,
                        'line': line
                    })
                    break
    
    print(f"✅ Найдено {len(terms)} терминов")
    return terms

def show_all_extracted_data():
    """Показывает все извлеченные данные"""
    text = extract_all_from_docx("контекстные данные.docx")
    
    if not text:
        print("❌ Не удалось прочитать файл")
        return
    
    print("\n" + "=" * 80)
    print("📄 ПОЛНЫЙ ТЕКСТ ИЗ ФАЙЛА:")
    print("=" * 80)
    print(text[:2000] + "..." if len(text) > 2000 else text)
    
    terms = extract_all_terms(text)
    
    print("\n" + "=" * 80)
    print("🔍 ВСЕ НАЙДЕННЫЕ ТЕРМИНЫ:")
    print("=" * 80)
    
    for i, term in enumerate(terms, 1):
        print(f"{i:2d}. {term['term']}")
        print(f"    {term['definition']}")
        print(f"    📝 Строка: {term['line']}")
        print()
    
    print(f"\n📊 ИТОГО: {len(terms)} терминов извлечено из файла")
    
    return terms

if __name__ == "__main__":
    show_all_extracted_data() 