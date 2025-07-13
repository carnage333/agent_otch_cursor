"""
Модуль для хранения маркетинговых целей и расчета показателей
"""

import json
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
import pandas as pd

class MarketingGoals:
    """Класс для управления маркетинговыми целями и показателями"""
    
    def __init__(self):
        # Цели по периодам
        self.goals = {
            "conversion_to_deal": {
                "2025-09-30": {
                    "plan": 0.45,
                    "fact": 0.0,
                    "description": "Конверсия платного трафика в сделку до 30.09.2025"
                },
                "2025-12-31": {
                    "plan": 0.45,
                    "fact": 0.0,
                    "description": "Конверсия платного трафика в сделку до 31.12.2025"
                }
            },
            "mroi": {
                "2025-12-31": {
                    "plan": 150.0,
                    "fact": 0.0,
                    "description": "Marketing Return On Investment (MROI) по направлению digital до 31.12.2025"
                }
            }
        }
        
        # Формулы для расчета показателей
        self.metrics_formulas = {
            "ctr": {
                "formula": "clicks / impressions * 100",
                "description": "Click-Through Rate (CTR) - процент кликов от показов"
            },
            "cpc": {
                "formula": "cost / clicks",
                "description": "Cost Per Click (CPC) - стоимость за клик"
            },
            "cpm": {
                "formula": "cost / impressions * 1000",
                "description": "Cost Per Mille (CPM) - стоимость за 1000 показов"
            },
            "conversion_rate": {
                "formula": "visits / clicks * 100",
                "description": "Конверсия кликов в посещения"
            },
            "roas": {
                "formula": "revenue / cost * 100",
                "description": "Return on Ad Spend (ROAS) - возврат на рекламные расходы"
            },
            "mroi": {
                "formula": "(revenue - cost) / cost * 100",
                "description": "Marketing Return on Investment (MROI) - маркетинговый ROI"
            }
        }
    
    def calculate_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Рассчитывает маркетинговые показатели для датафрейма"""
        metrics = {}
        
        if df.empty:
            return metrics
        
        # Базовые метрики
        total_impressions = df['impressions'].sum()
        total_clicks = df['clicks'].sum()
        total_cost = df['cost'].sum()
        total_visits = df['visits'].sum()
        
        # Рассчитываем показатели только если есть данные
        if total_impressions > 0 and total_clicks > 0:
            metrics['ctr'] = round((total_clicks / total_impressions) * 100, 2)
        
        if total_clicks > 0 and total_cost > 0:
            metrics['cpc'] = round(total_cost / total_clicks, 2)
        
        if total_impressions > 0 and total_cost > 0:
            metrics['cpm'] = round((total_cost / total_impressions) * 1000, 2)
        
        if total_clicks > 0 and total_visits > 0:
            metrics['conversion_rate'] = round((total_visits / total_clicks) * 100, 2)
        
        # Для ROAS и MROI нужны данные о выручке
        # Пока используем примерные данные или оставляем пустыми
        # В реальном проекте эти данные должны быть в базе
        
        return metrics
    
    def get_goals_for_period(self, period: str = "2025-12-31") -> Dict[str, Dict]:
        """Получает цели для указанного периода"""
        goals_for_period = {}
        
        for metric_type, periods in self.goals.items():
            if period in periods:
                goals_for_period[metric_type] = periods[period]
        
        return goals_for_period
    
    def compare_with_goals(self, metrics: Dict[str, float], period: str = "2025-12-31") -> Dict[str, Dict]:
        """Сравнивает фактические показатели с целями"""
        goals = self.get_goals_for_period(period)
        comparison = {}
        
        for metric_name, metric_value in metrics.items():
            if metric_name in goals:
                goal = goals[metric_name]
                comparison[metric_name] = {
                    "fact": metric_value,
                    "plan": goal["plan"],
                    "achievement": round((metric_value / goal["plan"]) * 100, 2) if goal["plan"] > 0 else 0,
                    "description": goal["description"],
                    "status": "achieved" if metric_value >= goal["plan"] else "not_achieved"
                }
        
        return comparison
    
    def format_metrics_report(self, metrics: Dict[str, float], comparison: Dict[str, Dict]) -> str:
        """Форматирует отчет с показателями и сравнением с целями"""
        report = "## 📊 Маркетинговые показатели\n\n"
        
        # Основные показатели
        report += "### 🎯 Ключевые метрики\n\n"
        for metric_name, value in metrics.items():
            if metric_name in self.metrics_formulas:
                description = self.metrics_formulas[metric_name]["description"]
                # Форматируем значения в зависимости от типа метрики
                if metric_name in ['ctr', 'conversion_rate']:
                    # Процентные значения
                    report += f"- **{metric_name.upper()}**: {value}% - {description}\n"
                elif metric_name in ['cpc', 'cpm']:
                    # Абсолютные значения в рублях
                    report += f"- **{metric_name.upper()}**: {value} ₽ - {description}\n"
                else:
                    # Остальные значения
                    report += f"- **{metric_name.upper()}**: {value} - {description}\n"
        
        # Сравнение с целями
        if comparison:
            report += "\n### 🎯 Сравнение с целями\n\n"
            for metric_name, comp_data in comparison.items():
                status_emoji = "✅" if comp_data["status"] == "achieved" else "⚠️"
                report += f"{status_emoji} **{metric_name.upper()}**\n"
                report += f"   - План: {comp_data['plan']}%\n"
                report += f"   - Факт: {comp_data['fact']}%\n"
                report += f"   - Выполнение: {comp_data['achievement']}%\n"
                report += f"   - {comp_data['description']}\n\n"
        
        return report
    
    def get_metrics_description(self) -> str:
        """Возвращает описание всех доступных показателей"""
        description = "## 📈 Доступные маркетинговые показатели\n\n"
        
        for metric_name, info in self.metrics_formulas.items():
            description += f"### {metric_name.upper()}\n"
            description += f"{info['description']}\n"
            description += f"Формула: `{info['formula']}`\n\n"
        
        return description

# Глобальный экземпляр для использования в приложении
marketing_goals = MarketingGoals() 