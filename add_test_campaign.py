import sqlite3
import pandas as pd

def add_test_campaign():
    """Добавление тестовой кампании rko_spring2024"""
    
    conn = sqlite3.connect('marketing_analytics.db')
    
    # Создаем тестовые данные для rko_spring2024
    test_data = []
    for i in range(50):
        test_data.append({
            'date': '2024-03-15',
            'traffic_source': 'yandex',
            'utm_campaign': 'rko_spring2024',
            'utm_source': 'yandex',
            'utm_medium': 'cpc',
            'utm_content': f'content_{i}',
            'utm_term': f'term_{i}',
            'visit_id': f'visit_{i}',
            'submits': 100 + i,
            'res': 10 + i,
            'subs_all': 100 + i,
            'account_num': 5 + i,
            'created_flag': 3 + i,
            'call_answered_flag': 2 + i,
            'quality_flag': 1 + i,
            'quality': 1 + i,
            'step_name': 'Этап воронки',
            'step_order': 1,
            'visitors': 100 + i,
            'conversions': 10 + i,
            'conversion_rate': 10.0
        })
    
    # Создаем DataFrame
    df = pd.DataFrame(test_data)
    
    # Добавляем в базу (не заменяем существующие данные)
    df.to_sql('funnel_data', conn, if_exists='append', index=False)
    
    print(f"Добавлено {len(df)} записей для кампании rko_spring2024")
    
    # Проверяем
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM funnel_data WHERE utm_campaign = 'rko_spring2024'")
    count = cursor.fetchone()[0]
    print(f"Всего записей для rko_spring2024: {count}")
    
    conn.close()

if __name__ == "__main__":
    add_test_campaign() 