import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta

def add_funnel_data():
    """Добавление тестовых данных воронки"""
    conn = sqlite3.connect('marketing_analytics.db')
    
    # Создаем тестовые данные для воронки
    test_data = []
    start_date = datetime(2024, 3, 1)  # Весна 2024
    
    # UTM кампании
    utm_campaigns = ['rko_spring2024', 'rko_summer2024', 'rko_autumn2024']
    utm_sources = ['yandex', 'google', 'vk', 'telegram']
    utm_mediums = ['cpc', 'cpm', 'banner']
    step_names = ['Показ', 'Клик', 'Переход на сайт', 'Заполнение формы', 'Заявка']
    
    for i in range(200):  # 200 записей
        date = start_date + timedelta(days=i % 90)  # 3 месяца
        utm_campaign = random.choice(utm_campaigns)
        utm_source = random.choice(utm_sources)
        utm_medium = random.choice(utm_mediums)
        step_name = random.choice(step_names)
        step_order = random.randint(1, 5)
        
        visitors = random.randint(100, 1000)
        conversions = random.randint(5, int(visitors * 0.1))  # 10% конверсия
        conversion_rate = round(conversions / visitors * 100, 2)
        
        test_data.append({
            'utm_source': utm_source,
            'utm_medium': utm_medium,
            'utm_campaign': utm_campaign,
            'utm_content': f'content_{i}',
            'utm_term': f'term_{i}',
            'step_name': step_name,
            'step_order': step_order,
            'visitors': visitors,
            'conversions': conversions,
            'conversion_rate': conversion_rate,
            'date': date.strftime('%Y-%m-%d')
        })
    
    # Создаем DataFrame
    funnel_df = pd.DataFrame(test_data)
    
    # Сохраняем в базу данных
    funnel_df.to_sql('funnel_data', conn, if_exists='replace', index=False)
    
    print(f"Добавлено {len(funnel_df)} записей в funnel_data")
    
    # Проверяем данные для rko_spring2024
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM funnel_data WHERE utm_campaign = 'rko_spring2024'")
    count = cursor.fetchone()[0]
    print(f"Записей для rko_spring2024: {count}")
    
    # Показываем пример данных
    cursor.execute("SELECT * FROM funnel_data WHERE utm_campaign = 'rko_spring2024' LIMIT 3")
    data = cursor.fetchall()
    print("\nПример данных для rko_spring2024:")
    for row in data:
        print(f"  {row}")
    
    conn.close()

if __name__ == "__main__":
    add_funnel_data() 