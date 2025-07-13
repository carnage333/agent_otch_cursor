#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ai_agent import MarketingAnalyticsAgent

def test_csv_generation():
    """Тестируем генерацию CSV отчета"""
    print("🧪 Тестируем генерацию CSV отчета...")
    
    # Инициализируем агента
    agent = MarketingAnalyticsAgent()
    
    # Создаем тестовые данные
    test_analysis = {
        "summary": {
            "campaigns_count": 1,
            "total_impressions": 3590013,
            "total_clicks": 120923,
            "total_cost": 18991650,
            "total_visits": 0,
            "avg_ctr": 3.37,
            "avg_cpc": 157.06,
            "campaigns": [
                {
                    "campaign_name": "Годовой performance. РКО 2025.",
                    "platform": "VK Реклама",
                    "impressions": 210979,
                    "clicks": 5934,
                    "cost": 21378,
                    "visits": 0,
                    "ctr": 2.81,
                    "cpc": 3.60
                },
                {
                    "campaign_name": "Годовой performance. РКО 2025.",
                    "platform": "Яндекс.Директ",
                    "impressions": 3379034,
                    "clicks": 114989,
                    "cost": 18970272,
                    "visits": 0,
                    "ctr": 3.40,
                    "cpc": 164.97
                }
            ],
            "platforms": [
                {
                    "platform": "VK Реклама",
                    "impressions": 210979,
                    "clicks": 5934,
                    "cost": 21378,
                    "visits": 0,
                    "ctr": 2.81,
                    "cpc": 3.60
                },
                {
                    "platform": "Яндекс.Директ",
                    "impressions": 3379034,
                    "clicks": 114989,
                    "cost": 18970272,
                    "visits": 0,
                    "ctr": 3.40,
                    "cpc": 164.97
                }
            ]
        },
        "insights": [
            "Высокий средний CTR указывает на эффективность рекламных кампаний"
        ],
        "recommendations": [
            "Стоит пересмотреть ставки и таргетинг для снижения CPC",
            "Низкая конверсия кликов в визиты - проверьте качество трафика"
        ]
    }
    
    # Генерируем CSV
    question = "Сделай отчет по кампании Годовой performance. РКО 2025."
    csv_data = agent.generate_csv_report(test_analysis, question)
    
    print(f"✅ CSV данные сгенерированы!")
    print(f"📊 Длина CSV данных: {len(csv_data)} байт")
    print(f"📄 Первые 500 символов:")
    print("-" * 50)
    print(csv_data[:500].decode('utf-8'))
    print("-" * 50)
    
    # Проверяем, что данные не пустые
    if len(csv_data) > 0:
        print("✅ УСПЕХ: CSV данные не пустые!")
        return True
    else:
        print("❌ ОШИБКА: CSV данные пустые!")
        return False

if __name__ == "__main__":
    success = test_csv_generation()
    if success:
        print("\n🎉 Тест пройден успешно! CSV генерация работает корректно.")
    else:
        print("\n💥 Тест провален! CSV генерация не работает.") 