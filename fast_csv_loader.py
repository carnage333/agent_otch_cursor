import pandas as pd
import sqlite3
import time
import csv
import re
import os

def parse_csv_line(line):
    """Парсит строку CSV с вложенными кавычками"""
    # Убираем лишние кавычки по краям
    line = line.strip()
    if line.startswith('"') and line.endswith('"'):
        line = line[1:-1]
    
    # Разбиваем по запятой, но учитываем кавычки
    result = []
    current = ""
    in_quotes = False
    i = 0
    
    while i < len(line):
        char = line[i]
        
        if char == '"':
            if in_quotes and i + 1 < len(line) and line[i + 1] == '"':
                # Двойная кавычка внутри кавычек
                current += '"'
                i += 2
            else:
                # Одиночная кавычка
                in_quotes = not in_quotes
                i += 1
        elif char == ',' and not in_quotes:
            # Запятая вне кавычек - разделитель
            result.append(current.strip())
            current = ""
            i += 1
        else:
            current += char
            i += 1
    
    # Добавляем последнее значение
    result.append(current.strip())
    return result

def preprocess_csv_manual(input_path, output_path):
    """Создаёт очищенную версию CSV с ручным парсингом"""
    with open(input_path, 'r', encoding='utf-8') as fin, open(output_path, 'w', encoding='utf-8', newline='') as fout:
        for line_num, line in enumerate(fin, 1):
            if line_num == 1:
                # Обрабатываем заголовок
                parsed = parse_csv_line(line)
                # Берем только первые 15 столбцов (основные данные)
                header = parsed[:15]
                # Очищаем заголовки от лишних кавычек
                clean_header = []
                for col in header:
                    col = col.replace('""', '"')
                    col = re.sub(r'^"|"$', '', col)
                    clean_header.append(col)
                fout.write(','.join(clean_header) + '\n')
            else:
                # Обрабатываем данные
                parsed = parse_csv_line(line)
                # Берем только первые 15 столбцов
                data = parsed[:15]
                # Очищаем данные от лишних кавычек
                clean_data = []
                for val in data:
                    val = val.replace('""', '"')
                    val = re.sub(r'^"|"$', '', val)
                    clean_data.append(val)
                fout.write(','.join(clean_data) + '\n')

def get_column_mapping(columns):
    """Возвращает маппинг колонок CSV -> funnel_data"""
    mapping = {
        'date': 'date',
        'lastTrafficSource': 'traffic_source',
        'traffic_source': 'traffic_source',
        'UTMCampaign_clear': 'utm_campaign',
        'utm_campaign': 'utm_campaign',
        'UTMSource': 'utm_source',
        'utm_source': 'utm_source',
        'UTMMedium': 'utm_medium',
        'utm_medium': 'utm_medium',
        'UTMContent': 'utm_content',
        'utm_content': 'utm_content',
        'UTMTerm': 'utm_term',
        'utm_term': 'utm_term',
        'visitID': 'visit_id',
        'visit_id': 'visit_id',
        'submits': 'submits',
        'res': 'res',
        'subs_all': 'subs_all',
        'account_num': 'account_num',
        'created_flag': 'created_flag',
        'call_answered_flag': 'call_answered_flag',
        'quality_flag': 'quality_flag',
        'quality': 'quality',
    }
    return {col: mapping[col] for col in columns if col in mapping}

def create_funnel_table(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS funnel_data (
            date TEXT,
            traffic_source TEXT,
            utm_campaign TEXT,
            utm_source TEXT,
            utm_medium TEXT,
            utm_content TEXT,
            utm_term TEXT,
            visit_id TEXT,
            submits REAL,
            res REAL,
            subs_all REAL,
            account_num INTEGER,
            created_flag INTEGER,
            call_answered_flag INTEGER,
            quality_flag INTEGER,
            quality INTEGER
        )
    ''')
    conn.commit()

def fast_load_csv_to_db(csv_file, db_path='marketing_analytics.db', chunk_size=10000):
    print(f"\n🚀 Быстрая загрузка {csv_file} в funnel_data...")
    start = time.time()
    
    # Создаем очищенный файл
    temp_file = 'cleaned_funnel_sample.csv'
    preprocess_csv_manual(csv_file, temp_file)
    print(f"✅ Создан очищенный файл: {temp_file}")
    
    conn = sqlite3.connect(db_path)
    create_funnel_table(conn)
    conn.execute('DELETE FROM funnel_data')
    print("🗑️ Очищена таблица funnel_data")
    
    total = 0
    chunk_num = 0
    
    # Читаем очищенный файл
    reader = pd.read_csv(
        temp_file,
        sep=',',
        dtype=str,
        on_bad_lines='skip',
        header=0
    )
    
    print(f"📊 Заголовки: {list(reader.columns)}")
    print(f"📊 Размер данных: {len(reader)} строк")
    
    # Обрабатываем данные чанками
    for chunk_start in range(0, len(reader), chunk_size):
        chunk_num += 1
        chunk_end = min(chunk_start + chunk_size, len(reader))
        chunk = reader.iloc[chunk_start:chunk_end].copy()
        
        # Маппинг колонок
        mapping = get_column_mapping(chunk.columns)
        chunk = chunk.rename(columns=mapping)
        
        # Оставляем только нужные колонки
        expected = [
            'date', 'traffic_source', 'utm_campaign', 'utm_source', 'utm_medium',
            'utm_content', 'utm_term', 'visit_id', 'submits', 'res', 'subs_all',
            'account_num', 'created_flag', 'call_answered_flag', 'quality_flag', 'quality'
        ]
        
        for col in expected:
            if col not in chunk.columns:
                chunk[col] = None
        
        chunk = chunk[expected]
        
        # Загружаем в БД
        chunk.to_sql('funnel_data', conn, if_exists='append', index=False, method=None)
        total += len(chunk)
        print(f"📦 Чанк {chunk_num}: {len(chunk)} строк (всего: {total})")
    
    conn.commit()
    print(f"✅ Загрузка завершена! Всего строк: {total}. Время: {time.time()-start:.1f} сек.")
    
    # Показываем примеры
    sample = conn.execute('SELECT * FROM funnel_data LIMIT 3').fetchall()
    print("\n📋 Примеры данных:")
    for row in sample:
        print(row)
    
    campaigns = conn.execute('SELECT DISTINCT utm_campaign FROM funnel_data WHERE utm_campaign IS NOT NULL LIMIT 10').fetchall()
    print(f"🎯 Примеры utm_campaign: {[c[0] for c in campaigns]}")
    
    sources = conn.execute('SELECT DISTINCT utm_source FROM funnel_data WHERE utm_source IS NOT NULL LIMIT 5').fetchall()
    print(f"🌐 Примеры utm_source: {[s[0] for s in sources]}")
    
    conn.close()
    
    # Удаляем временный файл
    if os.path.exists(temp_file):
        os.remove(temp_file)

if __name__ == "__main__":
    fast_load_csv_to_db('rko_funnel_sample-1750856109631.csv') 