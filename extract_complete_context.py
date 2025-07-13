import docx
import re
from typing import List, Dict, Any

def extract_complete_data_from_docx(file_path: str) -> Dict[str, Any]:
    """Извлекает ВСЕ данные из Word документа"""
    try:
        doc = docx.Document(file_path)
        full_text = ""
        
        print("Извлечение всех данных из файла...")
        
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:
                full_text += text + "\n"
        
        print(f"Извлечено {len(full_text)} символов")
        
        # Анализируем все данные
        data = {
            'full_text': full_text,
            'metrics': extract_metrics(full_text),
            'formulas': extract_formulas(full_text),
            'terms': extract_terms(full_text),
            'report_structures': extract_report_structures(full_text),
            'campaigns': extract_campaigns(full_text),
            'platforms': extract_platforms(full_text),
            'business_units': extract_business_units(full_text)
        }
        
        return data
        
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return {}

def extract_metrics(text: str) -> List[Dict]:
    """Извлекает метрики и их определения"""
    metrics = []
    
    # Паттерны для метрик
    patterns = [
        r'([A-Z]{2,4})\s*\(([^)]+)\):\s*(.+?)(?:\.|$)',  # AOV (Average Order Value): определение
        r'([A-Z]{2,4}):\s*(.+?)(?:\.|$)',  # AOV: определение
    ]
    
    for pattern in patterns:
        try:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                try:
                    metric_code = match.group(1)
                    if len(match.groups()) > 1:
                        metric_name = match.group(2)
                        definition = match.group(3)
                    else:
                        metric_name = ""
                        definition = match.group(2)
                    
                    if len(metric_code) >= 2 and len(definition) > 10:
                        metrics.append({
                            'code': metric_code,
                            'name': metric_name,
                            'definition': definition.strip(),
                            'full_match': match.group(0)
                        })
                except IndexError:
                    continue
        except Exception as e:
            print(f"Ошибка в паттерне {pattern}: {e}")
            continue
    
    return metrics

def extract_formulas(text: str) -> List[Dict]:
    """Извлекает формулы расчета"""
    formulas = []
    
    # Паттерны для формул
    patterns = [
        r'Формула расчета:\s*(.+?)(?:\.|$)',  # Формула расчета: формула
        r'Расчет:\s*(.+?)(?:\.|$)',  # Расчет: формула
        r'Формула:\s*(.+?)(?:\.|$)',  # Формула: формула
    ]
    
    for pattern in patterns:
        try:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                formula = match.group(1).strip()
                if len(formula) > 5:
                    formulas.append({
                        'formula': formula,
                        'context': match.group(0)
                    })
        except Exception as e:
            print(f"Ошибка в паттерне формул {pattern}: {e}")
            continue
    
    return formulas

def extract_terms(text: str) -> List[Dict]:
    """Извлекает термины и определения"""
    terms = []
    
    # Разбиваем на строки
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
        
        # Ищем различные паттерны
        patterns = [
            r'^([А-Я][А-Я\s\d]+):\s*(.+)',  # ТЕРМИН: определение
            r'^([А-Я][А-Я\s\d]+)\s*-\s*(.+)',  # ТЕРМИН - определение  
            r'^([А-Я][А-Я\s\d]+)\s*=\s*(.+)',  # ТЕРМИН = определение
            r'^([А-Я][А-Я\s\d]+)\s*\((.+)\)',  # ТЕРМИН (определение)
            r'^([А-Я][А-Я\s\d]+)\.\s*(.+)',  # ТЕРМИН. определение
        ]
        
        for pattern in patterns:
            try:
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
            except Exception as e:
                continue
    
    return terms

def extract_report_structures(text: str) -> List[Dict]:
    """Извлекает структуры отчетов"""
    structures = []
    
    # Ищем разделы с описанием отчетов
    sections = re.split(r'\n\d+\.\s*', text)
    
    for section in sections:
        if any(keyword in section.lower() for keyword in ['отчет', 'структура', 'раздел', 'анализ']):
            lines = section.split('\n')
            title = lines[0].strip() if lines else ""
            content = '\n'.join(lines[1:]).strip()
            
            if len(content) > 20:
                structures.append({
                    'title': title,
                    'content': content
                })
    
    return structures

def extract_campaigns(text: str) -> List[str]:
    """Извлекает названия кампаний"""
    campaigns = []
    
    # Ищем упоминания кампаний
    patterns = [
        r'кампания[:\s]+([А-Я][А-Я\s\d]+)',
        r'ФРК\d+',
        r'кампания\s+([А-Я][А-Я\s\d]+)',
    ]
    
    for pattern in patterns:
        try:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    campaign = match.group(1) if len(match.groups()) > 0 else match.group(0)
                    if campaign not in campaigns:
                        campaigns.append(campaign)
                except IndexError:
                    continue
        except Exception as e:
            continue
    
    return campaigns

def extract_platforms(text: str) -> List[str]:
    """Извлекает платформы"""
    platforms = []
    
    # Ищем упоминания платформ
    platform_keywords = ['платформа', 'система', 'сервис', 'инструмент']
    
    lines = text.split('\n')
    for line in lines:
        for keyword in platform_keywords:
            if keyword in line.lower():
                # Извлекаем название платформы
                try:
                    match = re.search(r'([А-Я][А-Я\s\d]+)', line)
                    if match:
                        platform = match.group(1)
                        if platform not in platforms:
                            platforms.append(platform)
                except Exception:
                    continue
    
    return platforms

def extract_business_units(text: str) -> List[str]:
    """Извлекает бизнес-единицы"""
    units = []
    
    # Ищем упоминания бизнес-единиц
    patterns = [
        r'трайб[:\s]+([А-Я][А-Я\s\d]+)',
        r'подразделение[:\s]+([А-Я][А-Я\s\d]+)',
        r'департамент[:\s]+([А-Я][А-Я\s\d]+)',
    ]
    
    for pattern in patterns:
        try:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    unit = match.group(1)
                    if unit not in units:
                        units.append(unit)
                except IndexError:
                    continue
        except Exception as e:
            continue
    
    return units

def show_complete_extracted_data():
    """Показывает все извлеченные данные"""
    data = extract_complete_data_from_docx("контекстные данные.docx")
    
    if not data:
        print("Не удалось прочитать файл")
        return
    
    print("\n" + "=" * 80)
    print("📊 ПОЛНЫЙ АНАЛИЗ ДАННЫХ:")
    print("=" * 80)
    
    print(f"\n📈 МЕТРИКИ ({len(data['metrics'])}):")
    for i, metric in enumerate(data['metrics'], 1):
        print(f"{i:2d}. {metric['code']} - {metric['definition'][:100]}...")
    
    print(f"\n🧮 ФОРМУЛЫ ({len(data['formulas'])}):")
    for i, formula in enumerate(data['formulas'], 1):
        print(f"{i:2d}. {formula['formula']}")
    
    print(f"\n📝 ТЕРМИНЫ ({len(data['terms'])}):")
    for i, term in enumerate(data['terms'], 1):
        print(f"{i:2d}. {term['term']} - {term['definition'][:80]}...")
    
    print(f"\n📋 СТРУКТУРЫ ОТЧЕТОВ ({len(data['report_structures'])}):")
    for i, structure in enumerate(data['report_structures'], 1):
        print(f"{i:2d}. {structure['title']}")
        print(f"    {structure['content'][:100]}...")
    
    print(f"\n🎯 КАМПАНИИ ({len(data['campaigns'])}):")
    for i, campaign in enumerate(data['campaigns'], 1):
        print(f"{i:2d}. {campaign}")
    
    print(f"\n🖥️ ПЛАТФОРМЫ ({len(data['platforms'])}):")
    for i, platform in enumerate(data['platforms'], 1):
        print(f"{i:2d}. {platform}")
    
    print(f"\n🏢 БИЗНЕС-ЕДИНИЦЫ ({len(data['business_units'])}):")
    for i, unit in enumerate(data['business_units'], 1):
        print(f"{i:2d}. {unit}")
    
    return data

if __name__ == "__main__":
    show_complete_extracted_data() 