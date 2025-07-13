#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ai_agent import MarketingAnalyticsAgent
import pandas as pd

def test_csv_generation():
    """Тестирование генерации CSV отчетов"""
    agent = MarketingAnalyticsAgent()
    
    # Тестовые данные
    test_analysis = {
        "summary": {
            "campaigns_count": 1,
            "total_impressions": 286116,
            "total_clicks": 411,
            "total_cost": 35132,
            "total_visits": 5294,
            "avg_ctr": 0.14,
            "avg_cpc": 85.48,
            "campaigns": [
                {
                    "campaign_name": "ФРК4 Бизнес-Фест, апрель-декабрь 2025",
                    "platform": "Telegram Ads",
                    "impressions": 286116,
                    "clicks": 411,
                    "cost": 35132,
                    "visits": 133,
                    "ctr": 0.14,
                    "cpc": 85.48
                }
            ],
            "platforms": [
                {
                    "platform": "Telegram Ads",
                    "impressions": 286116,
                    "clicks": 411,
                    "cost": 35132,
                    "visits": 133,
                    "ctr": 0.14,
                    "cpc": 85.48
                }
            ]
        },
        "insights": [
            "Низкий CTR требует оптимизации креативов и таргетинга",
            "Хорошая конверсия кликов в визиты"
        ],
        "recommendations": [
            "Рекомендуется оптимизировать рекламные креативы для повышения CTR"
        ]
    }
    
    print("🧪 Тестирование генерации CSV отчета")
    print("=" * 50)
    
    try:
        # Тестируем CSV генерацию
        csv_data = agent._generate_csv_report(test_analysis, "Сделай отчет по кампании ФРК4 Бизнес-Фест, апрель")
        
        print(f"✅ CSV сгенерирован успешно!")
        print(f"📏 Размер данных: {len(csv_data)} байт")
        
        # Показываем первые строки
        csv_text = csv_data.decode('utf-8-sig')
        lines = csv_text.split('\n')[:10]
        print("\n📄 Первые 10 строк CSV:")
        for i, line in enumerate(lines, 1):
            print(f"{i:2d}: {line}")
        
        # Проверяем доступность openpyxl
        try:
            import openpyxl
            print(f"\n✅ openpyxl доступен: {openpyxl.__version__}")
        except ImportError:
            print(f"\n❌ openpyxl недоступен")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка генерации CSV: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_csv_generation() 