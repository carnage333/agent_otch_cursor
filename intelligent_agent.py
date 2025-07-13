import sqlite3
import pandas as pd
import json
from typing import Dict, List, Optional, Tuple, Any
import re
from datetime import datetime
import io
import os
import numpy as np

# Пытаемся импортировать LLM провайдеры
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI недоступен")

try:
    import requests
    FREE_LLM_AVAILABLE = True
except ImportError:
    FREE_LLM_AVAILABLE = False
    print("Библиотека requests недоступна")

class IntelligentMarketingAgent:
    """
    Интеллектуальный агент для работы с рекламными данными
    Использует LLM для понимания запросов и имеет специализированные tools
    """
    
    def __init__(self, db_path: str = 'marketing_analytics.db'):
        self.db_path = db_path
        self.conversation_history = []
        self.domain_knowledge = self._load_domain_knowledge()
        
        # Инициализируем LLM
        self.llm_available = self._init_llm()
        
        # Доступные tools
        self.tools = {
            "search_campaigns": self.search_campaigns,
            "get_campaign_data": self.get_campaign_data,
            "analyze_metrics": self.analyze_metrics,
            "generate_report": self.generate_report,
            "explain_metric": self.explain_metric,
            "get_database_info": self.get_database_info,
            "compare_campaigns": self.compare_campaigns,
            "get_trends": self.get_trends,
            "get_recommendations": self.get_recommendations
        }
    
    def _init_llm(self) -> bool:
        """Инициализация LLM"""
        if OPENAI_AVAILABLE:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                openai.api_key = api_key
                print("✅ OpenAI GPT доступен")
                return True
        
        if FREE_LLM_AVAILABLE:
            print("✅ Hugging Face доступен")
            return True
        
        print("⚠️ LLM недоступен, будет использоваться базовый режим")
        return False
    
    def _load_domain_knowledge(self) -> Dict:
        """Загрузка знаний предметной области"""
        return {
            "metrics": {
                "impressions": "Количество показов рекламы",
                "clicks": "Количество кликов по рекламе",
                "ctr": "Click-Through Rate - отношение кликов к показам",
                "cpc": "Cost Per Click - стоимость за клик",
                "cpm": "Cost Per Mille - стоимость за 1000 показов",
                "visits": "Количество визитов на сайт",
                "conversion_rate": "Конверсия - отношение целевых действий к визитам",
                "roi": "Return on Investment - возврат инвестиций"
            },
            "platforms": {
                "Telegram Ads": "Реклама в Telegram",
                "Regionza": "Региональная реклама",
                "NativeRent": "Нативная реклама",
                "yandex": "Яндекс.Директ",
                "vsp": "VK СамоПродвижение"
            },
            "analysis_types": {
                "performance": "Анализ эффективности кампаний",
                "trends": "Анализ трендов",
                "comparison": "Сравнительный анализ",
                "optimization": "Рекомендации по оптимизации"
            }
        }
    
    def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Вызов LLM для обработки запроса"""
        if not self.llm_available:
            return "LLM недоступен"
        
        try:
            # Пробуем OpenAI
            if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=500,
                    temperature=0.7
                )
                return response.choices[0].message.content
            
            # Пробуем Hugging Face
            elif FREE_LLM_AVAILABLE:
                API_URL = "https://api-inference.huggingface.co/models/gpt2"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_length": 200,
                        "temperature": 0.8,
                        "do_sample": True
                    }
                }
                
                response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get('generated_text', '')
                
                return "Ошибка при обращении к LLM"
            
        except Exception as e:
            print(f"Ошибка при обращении к LLM: {e}")
            return "Ошибка при обращении к LLM"
    
    def _understand_request(self, user_question: str) -> Dict:
        """Понимание запроса пользователя с помощью LLM"""
        system_prompt = """Ты помощник для анализа рекламных данных. Твоя задача - понять, что хочет пользователь и какие инструменты нужно использовать.

Доступные инструменты:
- search_campaigns: поиск кампаний по названию
- get_campaign_data: получение данных по кампаниям
- analyze_metrics: анализ метрик (CTR, CPC, конверсия)
- generate_report: генерация отчета
- explain_metric: объяснение метрики
- get_database_info: информация о базе данных
- compare_campaigns: сравнение кампаний
- get_trends: анализ трендов
- get_recommendations: получение рекомендаций

Ответь в формате JSON:
{
    "intent": "что хочет пользователь",
    "tools_needed": ["список нужных инструментов"],
    "parameters": {"параметры для инструментов"},
    "response_type": "тип ответа (report, explanation, data, comparison)"
}"""

        prompt = f"Пользователь спрашивает: {user_question}\n\nОпредели, что ему нужно и какие инструменты использовать."

        llm_response = self._call_llm(prompt, system_prompt)
        
        try:
            # Пытаемся парсить JSON ответ
            if llm_response.startswith('{'):
                return json.loads(llm_response)
            else:
                # Если LLM не вернул JSON, используем базовую логику
                return self._basic_request_understanding(user_question)
        except:
            return self._basic_request_understanding(user_question)
    
    def _basic_request_understanding(self, user_question: str) -> Dict:
        """Базовая логика понимания запроса без LLM"""
        question_lower = user_question.lower()
        
        # Проверяем, является ли это запросом о кампаниях
        campaign_keywords = ['фрк', 'годовой', 'performance', 'кампания', 'отчет', 'покажи', 'сделай']
        is_campaign_query = any(keyword in question_lower for keyword in campaign_keywords)
        
        # Если запрос содержит только название кампании (например, "фрк4"), считаем его запросом о кампании
        if not is_campaign_query and len(question_lower.strip()) <= 10:
            # Проверяем, есть ли в базе кампании с таким названием
            try:
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM campaign_metrics WHERE "Название кампании" LIKE ?', (f'%{question_lower.upper()}%',))
                count = cursor.fetchone()[0]
                conn.close()
                if count > 0:
                    is_campaign_query = True
            except:
                pass
        
        # Проверяем, является ли это запросом о метриках
        metric_keywords = ['ctr', 'cpc', 'конверсия', 'метрика', 'что такое']
        is_metric_query = any(keyword in question_lower for keyword in metric_keywords)
        
        # Проверяем, является ли это запросом о сравнении
        comparison_keywords = ['сравни', 'сравнение', 'топ', 'лучшие']
        is_comparison_query = any(keyword in question_lower for keyword in comparison_keywords)
        
        # Проверяем, является ли это общим приветствием или простым вопросом
        greeting_keywords = ['привет', 'здравствуй', 'hi', 'hello']
        is_greeting = any(keyword in question_lower for keyword in greeting_keywords)
        
        if is_campaign_query:
            # Извлекаем ключевые слова для поиска кампаний
            search_keywords = []
            if 'фрк1' in question_lower:
                search_keywords.append('ФРК1')
            elif 'фрк4' in question_lower:
                search_keywords.append('ФРК4')
            elif 'фрк' in question_lower:
                search_keywords.append('ФРК')
            
            if 'годовой' in question_lower or 'performance' in question_lower:
                search_keywords.append('Годовой')
            
            if search_keywords:
                return {
                    "intent": "search_campaigns",
                    "tools_needed": ["search_campaigns", "get_campaign_data"],
                    "parameters": {"search_terms": " ".join(search_keywords)},
                    "response_type": "report"
                }
            else:
                return {
                    "intent": "search_campaigns",
                    "tools_needed": ["search_campaigns", "get_campaign_data"],
                    "parameters": {"search_terms": user_question},
                    "response_type": "report"
                }
        
        elif is_metric_query:
            return {
                "intent": "explain_metric",
                "tools_needed": ["explain_metric"],
                "parameters": {"metric": user_question},
                "response_type": "explanation"
            }
        
        elif is_comparison_query:
            return {
                "intent": "compare_campaigns",
                "tools_needed": ["compare_campaigns"],
                "parameters": {"comparison_type": "campaigns"},
                "response_type": "comparison"
            }
        
        elif is_greeting:
            return {
                "intent": "greeting",
                "tools_needed": ["get_database_info"],
                "parameters": {},
                "response_type": "greeting"
            }
        
        else:
            return {
                "intent": "general_query",
                "tools_needed": ["get_database_info"],
                "parameters": {},
                "response_type": "data"
            }
    
    def search_campaigns(self, search_terms: str) -> Dict:
        """Поиск кампаний в базе данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Улучшенный поиск с обработкой различных вариантов
            search_variants = [
                search_terms.upper(),
                search_terms.upper().replace(' ', ''),
                search_terms.upper().replace('-', ''),
                search_terms.upper().replace('_', ''),
                search_terms.upper().replace(' ', '').replace('-', ''),
                search_terms.upper().replace(' ', '').replace('_', '')
            ]
            
            # Создаем условия для поиска
            conditions = []
            for variant in search_variants:
                if len(variant) > 1:  # Игнорируем слишком короткие варианты
                    conditions.append(f'UPPER("Название кампании") LIKE "%{variant}%"')
            
            if not conditions:
                conditions = [f'UPPER("Название кампании") LIKE "%{search_terms.upper()}%"']
            
            query = f'''
            SELECT DISTINCT "Название кампании", "Площадка"
            FROM campaign_metrics 
            WHERE {" OR ".join(conditions)}
            LIMIT 10
            '''
            
            print(f"🔍 SQL запрос для поиска: {query}")
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            result = {
                "success": True,
                "campaigns": df.to_dict('records') if not df.empty else [],
                "count": len(df)
            }
            
            print(f"📋 Найдено кампаний: {result['count']}")
            if result['campaigns']:
                print("📋 Найденные кампании:")
                for campaign in result['campaigns']:
                    print(f"  - {campaign['Название кампании']}")
            
            return result
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            return {"success": False, "error": str(e)}
    
    def get_campaign_data(self, campaign_name: str) -> Dict:
        """Получение данных по конкретной кампании"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = f'''
            SELECT * FROM campaign_metrics 
            WHERE UPPER("Название кампании") LIKE '%{campaign_name.upper()}%'
            '''
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                return {"success": False, "error": "Кампания не найдена"}
            
            # Анализируем данные
            analysis = {
                "total_impressions": df["Показы"].sum(),
                "total_clicks": df["Клики"].sum(),
                "total_cost": df["Расход до НДС"].sum(),
                "avg_ctr": df["CTR"].mean(),
                "avg_cpc": df["CPC"].mean(),
                "platforms": df["Площадка"].unique().tolist()
            }
            
            return {
                "success": True,
                "data": df.to_dict('records'),
                "analysis": analysis
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_metrics(self, data: List[Dict]) -> Dict:
        """Анализ метрик"""
        if not data:
            return {"success": False, "error": "Нет данных для анализа"}
        
        df = pd.DataFrame(data)
        
        analysis = {
            "total_impressions": df["Показы"].sum(),
            "total_clicks": df["Клики"].sum(),
            "total_cost": df["Расход до НДС"].sum(),
            "avg_ctr": df["CTR"].mean(),
            "avg_cpc": df["CPC"].mean(),
            "best_performing": df.loc[df["CTR"].idxmax()].to_dict() if not df.empty else None,
            "worst_performing": df.loc[df["CTR"].idxmin()].to_dict() if not df.empty else None
        }
        
        return {"success": True, "analysis": analysis}
    
    def generate_report(self, analysis: Dict, question: str) -> str:
        """Генерация отчета"""
        if not analysis.get("success"):
            return "❌ Не удалось сгенерировать отчет"
        
        report = f"# 📊 Отчет по запросу: {question}\n\n"
        
        data = analysis.get("analysis", {})
        report += f"## 📈 Общая статистика\n\n"
        report += f"- **Всего показов:** {data.get('total_impressions', 0):,}\n"
        report += f"- **Всего кликов:** {data.get('total_clicks', 0):,}\n"
        report += f"- **Общий расход:** {data.get('total_cost', 0):,.2f} ₽\n"
        report += f"- **Средний CTR:** {data.get('avg_ctr', 0):.2f}%\n"
        report += f"- **Средний CPC:** {data.get('avg_cpc', 0):.2f} ₽\n\n"
        
        # Добавляем инсайты
        report += "## 💡 Ключевые инсайты\n\n"
        ctr = data.get('avg_ctr', 0)
        if ctr > 2:
            report += "• Высокий CTR указывает на эффективные креативы\n"
        elif ctr < 0.5:
            report += "• Низкий CTR требует оптимизации креативов\n"
        else:
            report += "• Средний CTR, есть возможности для улучшения\n"
        
        return report
    
    def explain_metric(self, metric: str) -> str:
        """Объяснение метрики"""
        explanations = {
            "ctr": "**CTR (Click-Through Rate)** - процент кликов от показов. Показывает, насколько эффективны ваши креативы.",
            "cpc": "**CPC (Cost Per Click)** - стоимость за клик. Важно для контроля бюджета и эффективности.",
            "конверсия": "**Конверсия** - процент посетителей, совершивших целевое действие (покупка, регистрация и т.д.).",
            "roi": "**ROI (Return on Investment)** - возврат инвестиций. Показывает прибыльность рекламных кампаний."
        }
        
        metric_lower = metric.lower()
        for key, explanation in explanations.items():
            if key in metric_lower:
                return explanation
        
        return "Эта метрика не найдена в базе знаний. Попробуйте спросить о CTR, CPC, конверсии или ROI."
    
    def get_database_info(self) -> Dict:
        """Получение информации о базе данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Получаем список кампаний
            cursor.execute('SELECT DISTINCT "Название кампании" FROM campaign_metrics LIMIT 5')
            campaigns = [row[0] for row in cursor.fetchall()]
            
            # Получаем статистику
            cursor.execute('SELECT COUNT(*) FROM campaign_metrics')
            total_records = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "success": True,
                "total_records": total_records,
                "sample_campaigns": campaigns,
                "available_data": "Показы, клики, расход, CTR, CPC, площадки"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def compare_campaigns(self, comparison_type: str) -> str:
        """Сравнение кампаний"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = '''
            SELECT "Название кампании", "Площадка", 
                   AVG("CTR") as avg_ctr, 
                   AVG("CPC") as avg_cpc,
                   SUM("Показы") as total_impressions,
                   SUM("Клики") as total_clicks
            FROM campaign_metrics 
            GROUP BY "Название кампании"
            ORDER BY avg_ctr DESC
            LIMIT 5
            '''
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                return "❌ Нет данных для сравнения"
            
            report = "## 🏆 Топ-5 кампаний по эффективности\n\n"
            report += "| Кампания | Площадка | CTR (%) | CPC (₽) | Показы | Клики |\n"
            report += "|----------|----------|---------|---------|--------|-------|\n"
            
            for _, row in df.iterrows():
                report += f"| {row['Название кампании']} | {row['Площадка']} | {row['avg_ctr']:.2f} | {row['avg_cpc']:.2f} | {row['total_impressions']:,} | {row['total_clicks']:,} |\n"
            
            return report
        except Exception as e:
            return f"❌ Ошибка при сравнении: {str(e)}"
    
    def get_trends(self) -> str:
        """Анализ трендов"""
        return "📈 Анализ трендов будет добавлен в следующей версии"
    
    def get_recommendations(self) -> str:
        """Получение рекомендаций"""
        recommendations = [
            "🎯 **Оптимизируйте креативы** - тестируйте разные варианты",
            "📊 **Анализируйте аудиторию** - уточните таргетинг",
            "💰 **Контролируйте бюджет** - следите за CPC и ROI",
            "🔄 **Регулярно анализируйте** - установите еженедельные ревью"
        ]
        
        return "## 🎯 Рекомендации по оптимизации\n\n" + "\n".join(recommendations)
    
    def process_question(self, user_question: str) -> tuple:
        """Основной метод обработки вопроса пользователя"""
        print(f"🤖 Обрабатываю вопрос: {user_question}")
        
        # Понимаем запрос с помощью LLM
        understanding = self._understand_request(user_question)
        print(f"📋 Понимание запроса: {understanding}")
        
        # Выполняем нужные инструменты
        results = {}
        for tool_name in understanding.get("tools_needed", []):
            if tool_name in self.tools:
                tool = self.tools[tool_name]
                params = understanding.get("parameters", {})
                
                if tool_name == "search_campaigns":
                    results[tool_name] = tool(params.get("search_terms", user_question))
                elif tool_name == "get_campaign_data":
                    # Сначала ищем кампании
                    search_result = self.search_campaigns(user_question)
                    if search_result.get("success") and search_result.get("campaigns"):
                        campaign_name = search_result["campaigns"][0]["Название кампании"]
                        results[tool_name] = tool(campaign_name)
                elif tool_name == "explain_metric":
                    results[tool_name] = tool(params.get("metric", user_question))
                else:
                    results[tool_name] = tool(**params)
        
        # Генерируем ответ
        response_type = understanding.get("response_type", "data")
        
        if response_type == "report":
            # Генерируем отчет
            if "get_campaign_data" in results and results["get_campaign_data"].get("success"):
                data = results["get_campaign_data"]["data"]
                analysis = self.analyze_metrics(data)
                response = self.generate_report(analysis, user_question)
            else:
                response = "❌ Не удалось найти данные для отчета"
        elif response_type == "explanation":
            # Объяснение
            if "explain_metric" in results:
                response = results["explain_metric"]
            else:
                response = "❌ Не удалось найти объяснение"
        elif response_type == "comparison":
            # Сравнение
            if "compare_campaigns" in results:
                response = results["compare_campaigns"]
            else:
                response = "❌ Не удалось выполнить сравнение"
        elif response_type == "greeting":
            # Приветствие
            response = "👋 Привет! Я ваш AI-помощник для анализа рекламных кампаний. Могу помочь с:\n\n"
            response += "📊 **Отчетами по кампаниям** - 'Сделай отчет по ФРК1'\n"
            response += "📈 **Объяснением метрик** - 'Что такое CTR?'\n"
            response += "🏆 **Сравнением кампаний** - 'Сравни кампании'\n"
            response += "💡 **Рекомендациями** - 'Дай рекомендации'\n\n"
            response += "Задайте любой вопрос! 🚀"
        else:
            # Общие данные
            if "get_database_info" in results and results["get_database_info"].get("success"):
                info = results["get_database_info"]
                response = f"📊 **Информация о базе данных:**\n\n- Всего записей: {info['total_records']:,}\n- Примеры кампаний: {', '.join(info['sample_campaigns'])}\n- Доступные данные: {info['available_data']}"
            else:
                response = "❌ Не удалось получить информацию"
        
        # Возвращаем кортеж в формате (response, sql_query, excel_data, dashboard_data)
        return response, "", None, None

# Пример использования
if __name__ == "__main__":
    agent = IntelligentMarketingAgent()
    
    # Тестовые вопросы
    test_questions = [
        "Покажи отчет по ФРК1",
        "Что такое CTR?",
        "Сравни кампании",
        "Дай рекомендации",
        "Покажи общую статистику"
    ]
    
    for question in test_questions:
        print(f"\n{'='*50}")
        print(f"Вопрос: {question}")
        print(f"{'='*50}")
        response = agent.process_question(question)
        print(response) 