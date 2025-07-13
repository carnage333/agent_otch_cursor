import sqlite3
import pandas as pd
import json
from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime

# Пытаемся импортировать RAG систему, но не блокируем запуск если она недоступна
try:
    from simple_vector_rag import SimpleVectorRAG
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("RAG система недоступна, будет использоваться упрощенный режим")

from marketing_goals import marketing_goals

class MarketingAnalyticsAgent:
    """
    AI-агент для автоматического формирования отчетов по рекламным кампаниям
    """
    
    def __init__(self, db_path: str = 'marketing_analytics.db'):
        self.db_path = db_path
        self.conversation_history = []
        self.domain_knowledge = self._load_domain_knowledge()
        
        # Инициализируем RAG систему только если она доступна
        if RAG_AVAILABLE:
            try:
                self.rag_system = SimpleVectorRAG()
            except Exception as e:
                print(f"Ошибка инициализации RAG системы: {e}")
                self.rag_system = None
        else:
            self.rag_system = None
    
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
    
    def _normalize_campaign_name(self, name: str) -> str:
        """Нормализация названия кампании: приводит к верхнему регистру и убирает лишние пробелы"""
        return ' '.join(name.upper().replace('-', ' ').split())

    def _normalize_search_term(self, term: str) -> str:
        """Нормализация поискового термина"""
        return term.upper().strip()

    def _get_similar_words(self, word: str) -> list:
        """Получение похожих слов для обработки опечаток"""
        similar_words = {
            # Опечатки и вариации
            "ГОДОВЙ": ["ГОДОВОЙ"],
            "ГОДОВО": ["ГОДОВОЙ"],
            "ПЕРФОМАНС": ["PERFORMANCE"],
            "ПЕРФОРМАНС": ["PERFORMANCE"],
            "СБЕРБИЗНЕС": ["СБЕРБИЗНЕС"],
            "СБЕРБИЗНЕСС": ["СБЕРБИЗНЕС"],
            
            # Сокращения
            "РКО": ["РКО", "РАСЧЕТНО-КАССОВОЕ", "РАСЧЕТНО КАССОВОЕ"],
            "РБИДОС": ["РБИДОС", "РБИДОС"],
            "ФРК": ["ФРК1", "ФРК4"],
            "ФРК1": ["ФРК1"],
            "ФРК4": ["ФРК4"],
            
            # Продукты
            "БИЗНЕС-КАРТЫ": ["БИЗНЕС-КАРТЫ", "БИЗНЕС КАРТЫ"],
            "БИЗНЕС-КРЕДИТЫ": ["БИЗНЕС-КРЕДИТЫ", "БИЗНЕС КРЕДИТЫ"],
            "БИЗНЕС КАРТЫ": ["БИЗНЕС-КАРТЫ", "БИЗНЕС КАРТЫ"],
            "БИЗНЕС КРЕДИТЫ": ["БИЗНЕС-КРЕДИТЫ", "БИЗНЕС КРЕДИТЫ"],
        }
        
        normalized = self._normalize_search_term(word)
        return similar_words.get(normalized, [normalized])

    def _extract_search_terms(self, question: str) -> list:
        """Извлечение поисковых терминов с улучшенной обработкой вариаций"""
        import re
        
        # Нормализуем вопрос
        question_upper = question.upper()
        
        # Ищем после ключевых слов
        keywords = []
        for kw in ["ПО КАМПАНИИ", "КАМПАНИЯ", "ОТЧЕТ ПО", "ОТЧЁТ ПО", "СДЕЛАЙ ОТЧЕТ ПО", "ПОКАЖИ ОТЧЕТ ПО", "АНАЛИЗ КАМПАНИИ"]:
            if kw in question_upper:
                part = question_upper.split(kw, 1)[-1].strip()
                # Убираем лишние слова
                for w in ["ПОКАЖИ", "ОТЧЕТ", "ОТЧЁТ", "АНАЛИЗ", "СТАТИСТИКА", "ДАННЫЕ", "ПО"]:
                    part = part.replace(w, "").strip()
                keywords = [w for w in re.split(r"[\s,()]+", part) if w and len(w) > 1]
                break
        
        if not keywords:
            # Если не нашли, берём все значимые слова
            keywords = [w for w in re.split(r"[\s,()]+", question_upper) if len(w) > 2]
        
        # Обрабатываем каждое слово с улучшенной логикой
        search_terms = []
        for keyword in keywords:
            # Разбиваем составные слова
            words = keyword.split()
            for word in words:
                if len(word) > 1:  # Игнорируем слишком короткие слова
                    # Нормализуем слово (убираем дефисы, пробелы)
                    normalized_word = word.replace('-', '').replace(' ', '')
                    
                    # Получаем похожие слова для обработки опечаток
                    similar_words = self._get_similar_words(normalized_word)
                    search_terms.extend(similar_words)
                    
                    # Добавляем варианты с дефисами и пробелами
                    if '-' in word or ' ' in word:
                        search_terms.append(word)
        
        return list(set(search_terms))  # Убираем дубликаты

    def _build_flexible_sql_conditions(self, search_terms: list) -> list:
        """Построение гибких SQL условий для поиска с улучшенной обработкой вариаций"""
        conditions = []
        
        for term in search_terms:
            # Создаем несколько вариантов поиска для каждого термина
            term_conditions = []
            
            # 1. Точное совпадение (регистр не важен)
            term_conditions.append(f"UPPER(\"Название кампании\") LIKE '%{term}%'")
            
            # 2. Поиск без пробелов и дефисов
            normalized_term = term.replace(' ', '').replace('-', '')
            if normalized_term != term:
                term_conditions.append(f"REPLACE(REPLACE(UPPER(\"Название кампании\"), ' ', ''), '-', '') LIKE '%{normalized_term}%'")
            
            # 3. Поиск с заменой дефисов на пробелы и наоборот
            if '-' in term:
                space_version = term.replace('-', ' ')
                term_conditions.append(f"UPPER(\"Название кампании\") LIKE '%{space_version}%'")
            
            if ' ' in term:
                dash_version = term.replace(' ', '-')
                term_conditions.append(f"UPPER(\"Название кампании\") LIKE '%{dash_version}%'")
            
            # 4. Поиск по частям слова (для длинных терминов)
            if len(term) > 4:
                parts = term.split()
                if len(parts) > 1:
                    for part in parts:
                        if len(part) > 2:
                            term_conditions.append(f"UPPER(\"Название кампании\") LIKE '%{part}%'")
            
            # 5. Поиск с игнорированием регистра и специальных символов
            clean_term = term.replace('-', '').replace(' ', '').replace('_', '')
            if clean_term != term:
                term_conditions.append(f"REPLACE(REPLACE(REPLACE(UPPER(\"Название кампании\"), ' ', ''), '-', ''), '_', '') LIKE '%{clean_term}%'")
            
            # Объединяем условия для одного термина через OR
            if term_conditions:
                conditions.append(f"({' OR '.join(term_conditions)})")
        
        return conditions

    def _extract_campaign_keywords(self, question: str) -> list:
        """Извлекает ключевые слова для поиска кампании из вопроса пользователя"""
        import re
        # Берём слова после ключевых фраз или всё, что похоже на название
        keywords = []
        question_upper = question.upper()
        # Попробуем найти после ключевых слов
        for kw in ["ПО КАМПАНИИ", "КАМПАНИЯ", "ОТЧЕТ ПО", "ОТЧЁТ ПО"]:
            if kw in question_upper:
                part = question_upper.split(kw, 1)[-1].strip()
                # Убираем лишние слова
                for w in ["ПОКАЖИ", "ОТЧЕТ", "ОТЧЁТ", "АНАЛИЗ", "СТАТИСТИКА"]:
                    part = part.replace(w, "").strip()
                keywords = [w for w in re.split(r"[\s,()]+", part) if w]
                break
        if not keywords:
            # Если не нашли, берём все слова длиннее 2 символов
            keywords = [w for w in re.split(r"[\s,()]+", question_upper) if len(w) > 2]
        
        # Разбиваем составные слова на отдельные
        final_keywords = []
        for keyword in keywords:
            # Разбиваем по пробелам и добавляем каждое слово отдельно
            words = keyword.split()
            final_keywords.extend(words)
        
        return final_keywords

    def _extract_campaign_name(self, question: str) -> str:
        """
        Извлечение названия кампании из вопроса пользователя
        """
        question_lower = question.lower()
        
        # Известные кампании для поиска (в нижнем регистре для сравнения)
        known_campaigns = [
            "фрк4 бизнес-фест",
            "фрк4_продвижение_рко",
            "фрк1",
            "годовой performance",
            "сбербизнес",
            "бизнес-старт",
            "торговля b2c"
        ]
        
        for campaign in known_campaigns:
            if campaign in question_lower:
                return self._normalize_campaign_name(campaign)
        
        # Если не найдено, ищем после ключевых слов
        keywords = ["по кампании", "кампания", "отчет по"]
        for keyword in keywords:
            if keyword in question_lower:
                # Извлекаем текст после ключевого слова
                start_idx = question_lower.find(keyword) + len(keyword)
                if start_idx < len(question_lower):
                    campaign_text = question_lower[start_idx:].strip()
                    # Убираем лишние слова
                    for word in ["покажи", "отчет", "анализ", "статистика"]:
                        campaign_text = campaign_text.replace(word, "").strip()
                    if campaign_text:
                        return self._normalize_campaign_name(campaign_text)
        
        # Если просто есть фрагмент типа "фрк4", "фрк-4", "фрк 4"
        import re
        match = re.search(r"фрк[\s\-]?4", question_lower)
        if match:
            return self._normalize_campaign_name(match.group(0))
        
        return ""
    
    def _extract_product_name(self, question: str) -> str:
        """
        Извлечение названия продукта из вопроса пользователя
        """
        question_lower = question.lower()
        
        # Известные продукты
        known_products = {
            "рко": "РКО",
            "рбидос": "РБиДОС", 
            "бизнес-карты": "Бизнес-карты",
            "бизнес-кредиты": "Бизнес-кредиты",
            "бизнес карты": "Бизнес-карты",
            "бизнес кредиты": "Бизнес-кредиты",
            "расчетно-кассовое обслуживание": "РКО",
            "расчетно кассовое обслуживание": "РКО"
        }
        
        for product_key, product_name in known_products.items():
            if product_key in question_lower:
                return product_name
        
        # Если не найдено, ищем после ключевых слов
        keywords = ["по продукту", "продукт", "для продукта", "статистика по"]
        for keyword in keywords:
            if keyword in question_lower:
                # Извлекаем текст после ключевого слова
                start_idx = question_lower.find(keyword) + len(keyword)
                if start_idx < len(question_lower):
                    product_text = question_lower[start_idx:].strip()
                    # Убираем лишние слова
                    for word in ["покажи", "отчет", "анализ", "статистика"]:
                        product_text = product_text.replace(word, "").strip()
                    if product_text:
                        return product_text
        
        return ""
    
    def _identify_product_from_campaigns(self, campaign_names: List[str]) -> str:
        """
        Определение продукта на основе названий кампаний
        """
        product_mapping = {
            "РКО": ["РКО", "расчетно-кассовое"],
            "Бизнес-карты": ["Бизнес-карты", "карты"],
            "Бизнес-кредиты": ["Бизнес-кредиты", "кредиты"],
            "РБиДОС": ["РБиДОС", "РБиДОС"]
        }
        
        for campaign_name in campaign_names:
            for product, keywords in product_mapping.items():
                if any(keyword in campaign_name for keyword in keywords):
                    return product
        
        return "Неизвестный продукт"
    
    def _get_all_campaign_names(self):
        """Получить все уникальные названия кампаний из базы для fuzzy-поиска"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT \"Название кампании\" FROM campaign_metrics")
        names = [row[0] for row in cursor.fetchall()]
        conn.close()
        return names

    def _translit_and_synonyms(self, word: str) -> list:
        """Транслитерация и англо-русские синонимы"""
        translit_dict = {
            "perfomans": ["performance"],
            "перфоманс": ["performance"],
            "бизнес": ["business"],
            "business": ["бизнес"],
            "карты": ["карты", "cards"],
            "кредиты": ["кредиты", "credits"],
        }
        w = word.lower()
        return translit_dict.get(w, [word])

    def _fuzzy_search_campaigns(self, search_terms: list, threshold: int = 80) -> list:
        """Простой поиск по campaign_name. Возвращает наиболее похожие названия кампаний."""
        all_names = self._get_all_campaign_names()
        found = set()
        for term in search_terms:
            # Добавляем транслит и синонимы
            variants = [term] + self._translit_and_synonyms(term)
            for v in variants:
                # Простой поиск по подстроке
                for name in all_names:
                    if v.upper() in name.upper():
                        found.add(name)
        return list(found)

    def get_matching_campaigns(self, user_question: str) -> list:
        """
        Возвращает список найденных кампаний по пользовательскому вопросу (fuzzy-поиск).
        Группирует кампании по названию, исключая разные площадки.
        """
        search_terms = self._extract_search_terms(user_question)
        fuzzy_names = self._fuzzy_search_campaigns(search_terms)
        
        # Группируем кампании по названию (без площадки)
        unique_campaigns = set()
        for campaign_name in fuzzy_names:
            # Убираем информацию о площадке из названия кампании
            # Ищем паттерны типа "Кампания - Площадка" или "Кампания (Площадка)"
            clean_name = campaign_name
            
            # Убираем площадки в скобках
            import re
            clean_name = re.sub(r'\s*\([^)]+\)\s*$', '', clean_name)
            
            # Убираем площадки после дефиса
            clean_name = re.sub(r'\s*-\s*[^-]+$', '', clean_name)
            
            # Убираем площадки после двоеточия
            clean_name = re.sub(r'\s*:\s*[^:]+$', '', clean_name)
            
            # Убираем площадки после пробела (если это не часть названия кампании)
            # Это более сложная логика, поэтому оставляем как есть для основных случаев
            
            unique_campaigns.add(clean_name.strip())
        
        return list(unique_campaigns)

    def generate_sql_query(self, user_question: str) -> str:
        """
        Генерация SQL запроса на основе вопроса пользователя
        """
        question_lower = user_question.lower()
        
        # Проверяем, является ли это запросом к воронке или UTM-меткам
        if self._is_funnel_query(user_question) or self._is_utm_query(user_question):
            utm_params = self._extract_utm_parameters(user_question)
            return self._generate_funnel_sql(user_question, utm_params)
        
        # Определяем тип запроса
        is_general_stats = any(word in question_lower for word in [
            "общая статистика", "общие показатели", "всего", "итого", 
            "общий расход", "общие показы", "общие клики", "покажи общую статистику",
            "все кампании", "всех кампаний"
        ])
        
        if is_general_stats:
            select_fields = [
                "COUNT(DISTINCT \"ID Кампании\") as campaigns_count",
                "SUM(\"Показы\") as total_impressions", 
                "SUM(\"Клики\") as total_clicks",
                "SUM(\"Расход до НДС\") as total_cost",
                "SUM(\"Визиты\") as total_visits",
                "ROUND(SUM(\"Клики\") * 100.0 / SUM(\"Показы\"), 2) as avg_ctr",
                "ROUND(SUM(\"Расход до НДС\") / SUM(\"Клики\"), 2) as avg_cpc"
            ]
            group_by = []
        else:
            select_fields = [
                "\"Название кампании\" as campaign_name", "\"Площадка\" as platform", 
                "SUM(\"Показы\") as impressions", 
                "SUM(\"Клики\") as clicks", 
                "SUM(\"Расход до НДС\") as cost", 
                "SUM(\"Визиты\") as visits", 
                "ROUND(SUM(\"Клики\") * 100.0 / SUM(\"Показы\"), 2) as ctr", 
                "ROUND(SUM(\"Расход до НДС\") / SUM(\"Клики\"), 2) as cpc"
            ]
            group_by = ["\"Название кампании\"", "\"Площадка\""]
        
        # Извлекаем поисковые термины
        search_terms = self._extract_search_terms(user_question)
        
        # Строим условия поиска
        where_conditions = []
        if search_terms and not is_general_stats:
            # Используем улучшенную логику поиска
            conditions = self._build_flexible_sql_conditions(search_terms)
            if conditions:
                where_conditions.extend(conditions)
        
        # Определяем ORDER BY
        order_by = []
        if any(word in question_lower for word in ["дорогой", "расход", "стоимость"]):
            order_by.append("cost DESC")
        elif any(word in question_lower for word in ["показы", "трафик"]):
            order_by.append("impressions DESC")
        elif any(word in question_lower for word in ["клики"]):
            order_by.append("clicks DESC")
        elif is_general_stats:
            order_by.append("total_cost DESC")
        else:
            order_by.append("\"Название кампании\" ASC")
        
        # Определяем LIMIT
        limit_clause = ""
        if any(word in question_lower for word in ["топ", "лучшие", "лучший"]):
            limit_clause = "LIMIT 10"
        elif any(word in question_lower for word in ["первые", "первые 5"]):
            limit_clause = "LIMIT 5"
        
        # Собираем SQL запрос
        sql = f"SELECT {', '.join(select_fields)} FROM campaign_metrics"
        
        if where_conditions:
            sql += f" WHERE {' AND '.join(where_conditions)}"
        
        if group_by:
            sql += f" GROUP BY {', '.join(group_by)}"
        
        if order_by:
            sql += f" ORDER BY {', '.join(order_by)}"
        
        if limit_clause:
            sql += f" {limit_clause}"
        
        return sql
    
    def execute_query(self, sql_query: str) -> pd.DataFrame:
        """Выполнение SQL запроса и возврат результатов"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(sql_query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Ошибка выполнения SQL запроса: {e}")
            return pd.DataFrame()
    
    def analyze_data(self, df: pd.DataFrame, question: str) -> Dict:
        """
        Динамический анализ данных на основе структуры DataFrame
        """
        if df.empty:
            return {"error": "Нет данных для анализа по вашему запросу"}
        
        # Проверяем, является ли это анализом воронки
        if self._is_funnel_query(question) or self._is_utm_query(question):
            return self._analyze_funnel_data(df, question)
        
        # Оригинальная логика для campaign_metrics
        columns = df.columns.tolist()
        question_lower = question.lower()
        
        # Определяем тип анализа
        is_all_campaigns = any(word in question_lower for word in [
            "все кампании", "всех кампаний", "общая статистика", "общие показы", "общие клики", "покажи общую статистику"
        ])
        
        # Определяем тип анализа
        analysis_type = "all_campaigns" if is_all_campaigns else "specific_campaign"
        
        # Проверяем, есть ли результативные колонки
        has_result_columns = any(col.startswith('total_') for col in columns)
        
        # Анализируем данные
        summary = {}
        
        if has_result_columns:
            # Общая статистика
            summary = {
                "analysis_type": "general_stats",
                "total_impressions": df.iloc[0].get('total_impressions', 0),
                "total_clicks": df.iloc[0].get('total_clicks', 0),
                "total_cost": df.iloc[0].get('total_cost', 0),
                "total_visits": df.iloc[0].get('total_visits', 0),
                "avg_ctr": df.iloc[0].get('avg_ctr', 0),
                "avg_cpc": df.iloc[0].get('avg_cpc', 0),
                "campaigns_count": df.iloc[0].get('campaigns_count', 0)
            }
        else:
            # Детальная статистика по кампаниям
            if 'campaign_name' in df.columns:
                unique_campaigns_count = df['campaign_name'].nunique()
            else:
                unique_campaigns_count = len(df)
            summary = {
                "analysis_type": analysis_type,
                "total_impressions": df['impressions'].sum(),
                "total_clicks": df['clicks'].sum(),
                "total_cost": df['cost'].sum(),
                "total_visits": df['visits'].sum(),
                "avg_ctr": round((df['clicks'].sum() / df['impressions'].sum()) * 100, 2) if df['impressions'].sum() > 0 else 0,
                "avg_cpc": round(df['cost'].sum() / df['clicks'].sum(), 2) if df['clicks'].sum() > 0 else 0,
                "campaigns_count": unique_campaigns_count
            }
            
            # Добавляем данные по кампаниям
            if 'campaign_name' in columns:
                campaigns_data = []
                for _, row in df.iterrows():
                    campaign_data = {
                        'campaign_name': row.get('campaign_name', '—'),
                        'platform': row.get('platform', '—'),
                        'impressions': row.get('impressions', 0),
                        'clicks': row.get('clicks', 0),
                        'cost': row.get('cost', 0),
                        'visits': row.get('visits', 0),
                        'ctr': row.get('ctr', 0),
                        'cpc': row.get('cpc', 0)
                    }
                    campaigns_data.append(campaign_data)
                
                summary["campaigns"] = campaigns_data
                
                # Сортируем кампании по эффективности
                if campaigns_data:
                    sorted_campaigns = sorted(campaigns_data, key=lambda x: x.get('ctr', 0), reverse=True)
                    summary["top_campaigns"] = sorted_campaigns[:5]
            
            # Анализ по площадкам
            if 'platform' in df.columns and 'ctr' in df.columns:
                platform_stats = df.groupby('platform').agg({
                    'impressions': 'sum',
                    'clicks': 'sum',
                    'cost': 'sum',
                    'visits': 'sum',
                    'ctr': 'mean',
                    'cpc': 'mean'
                }).reset_index()
                
                platforms_data = []
                for _, row in platform_stats.iterrows():
                    platform_data = {
                        'platform': row.get('platform', '—'),
                        'impressions': row.get('impressions', 0),
                        'clicks': row.get('clicks', 0),
                        'cost': row.get('cost', 0),
                        'visits': row.get('visits', 0),
                        'ctr': row.get('ctr', 0),
                        'cpc': row.get('cpc', 0)
                    }
                    platforms_data.append(platform_data)
                
                summary["platforms"] = platforms_data
        
        # Генерируем инсайты
        insights = []
        
        if summary.get('avg_ctr', 0) > 2:
            insights.append("Высокий средний CTR указывает на эффективность рекламных кампаний")
        elif summary.get('avg_ctr', 0) < 0.5:
            insights.append("Низкий CTR требует оптимизации креативов и таргетинга")
        
        if summary.get('avg_cpc', 0) > 200:
            insights.append("Высокий CPC может указывать на дорогие ключевые слова или неэффективный таргетинг")
        elif summary.get('avg_cpc', 0) < 50:
            insights.append("Экономичный CPC показывает эффективное управление бюджетом")
        
        if summary.get('total_visits', 0) > summary.get('total_clicks', 0) * 2:
            insights.append("Хорошая конверсия кликов в визиты")
        
        # Генерируем рекомендации
        recommendations = []
        
        if summary.get('avg_ctr', 0) < 1:
            recommendations.append("Рекомендуется оптимизировать рекламные креативы для повышения CTR")
        
        if summary.get('avg_cpc', 0) > 150:
            recommendations.append("Стоит пересмотреть ставки и таргетинг для снижения CPC")
        
        if summary.get('total_visits', 0) < summary.get('total_clicks', 0):
            recommendations.append("Низкая конверсия кликов в визиты - проверьте качество трафика")
        
        return {
            "summary": summary,
            "insights": insights,
            "recommendations": recommendations
        }
    
    def _analyze_funnel_data(self, df: pd.DataFrame, question: str) -> Dict:
        """
        Анализ данных воронки
        """
        if df.empty:
            return {"error": "Нет данных воронки для анализа"}
        
        columns = df.columns.tolist()
        question_lower = question.lower()
        
        summary = {
            "analysis_type": "funnel_analysis"
        }
        
        # Определяем тип анализа воронки
        if 'metric' in columns and len(df) == 1:
            # Общая воронка
            row = df.iloc[0]
            summary.update({
                "visits": row.get('visits', 0),
                "submits": row.get('submits', 0),
                "accounts_opened": row.get('accounts_opened', 0),
                "created": row.get('created', 0),
                "calls_answered": row.get('calls_answered', 0),
                "quality_leads": row.get('quality_leads', 0),
                "conversion_to_submits": row.get('conversion_to_submits', 0),
                "conversion_to_accounts": row.get('conversion_to_accounts', 0),
                "conversion_to_quality": row.get('conversion_to_quality', 0)
            })
        
        elif 'utm_source' in columns:
            # Сравнение источников
            summary["sources_comparison"] = []
            for _, row in df.iterrows():
                source_data = {
                    'utm_source': row.get('utm_source', '—'),
                    'visits': row.get('visits', 0),
                    'submits': row.get('submits', 0),
                    'accounts_opened': row.get('accounts_opened', 0),
                    'quality_leads': row.get('quality_leads', 0),
                    'conversion_to_submits': row.get('conversion_to_submits', 0),
                    'conversion_to_accounts': row.get('conversion_to_accounts', 0),
                    'conversion_to_quality': row.get('conversion_to_quality', 0)
                }
                summary["sources_comparison"].append(source_data)
        
        elif 'date' in columns:
            # Динамика по дням
            summary["daily_trends"] = []
            for _, row in df.iterrows():
                trend_data = {
                    'date': row.get('date', '—'),
                    'visits': row.get('visits', 0),
                    'submits': row.get('submits', 0),
                    'accounts_opened': row.get('accounts_opened', 0),
                    'quality_leads': row.get('quality_leads', 0)
                }
                summary["daily_trends"].append(trend_data)
        
        elif 'utm_campaign' in columns:
            # Топ кампаний
            summary["top_campaigns"] = []
            for _, row in df.iterrows():
                campaign_data = {
                    'utm_campaign': row.get('utm_campaign', '—'),
                    'visits': row.get('visits', 0),
                    'submits': row.get('submits', 0),
                    'accounts_opened': row.get('accounts_opened', 0),
                    'quality_leads': row.get('quality_leads', 0),
                    'conversion_to_submits': row.get('conversion_to_submits', 0)
                }
                summary["top_campaigns"].append(campaign_data)
        
        # Генерируем инсайты для воронки
        insights = []
        
        conversion_to_submits = summary.get('conversion_to_submits', 0) or 0
        conversion_to_accounts = summary.get('conversion_to_accounts', 0) or 0
        conversion_to_quality = summary.get('conversion_to_quality', 0) or 0
        
        if conversion_to_submits > 20:
            insights.append("Высокая конверсия визитов в заявки - отличные результаты")
        elif conversion_to_submits < 5:
            insights.append("Низкая конверсия визитов в заявки - требуется оптимизация")
        
        if conversion_to_accounts > 30:
            insights.append("Хорошая конверсия заявок в открытые счета")
        elif conversion_to_accounts < 10:
            insights.append("Низкая конверсия заявок в счета - проверьте процесс оформления")
        
        if conversion_to_quality > 50:
            insights.append("Высокий процент качественных лидов")
        elif conversion_to_quality < 20:
            insights.append("Низкий процент качественных лидов - требуется улучшение качества трафика")
        
        # Генерируем рекомендации для воронки
        recommendations = []
        
        if summary.get('conversion_to_submits', 0) < 10:
            recommendations.append("Оптимизируйте лендинги и формы заявок для повышения конверсии")
        
        if summary.get('conversion_to_accounts', 0) < 20:
            recommendations.append("Упростите процесс открытия счетов для повышения конверсии")
        
        if summary.get('conversion_to_quality', 0) < 30:
            recommendations.append("Улучшите таргетинг для привлечения более качественного трафика")
        
        return {
            "summary": summary,
            "insights": insights,
            "recommendations": recommendations
        }
    
    def generate_report(self, analysis: Dict, question: str, sql_query: str = "") -> str:
        """
        Динамическая генерация отчета на основе типа запроса и данных
        """
        if "error" in analysis:
            return f"## Нет данных для анализа по вашему запросу.\n"
        
        question_lower = question.lower()
        summary = analysis.get("summary", {})
        
        # Проверяем тип анализа из данных
        analysis_type = summary.get('analysis_type', 'general')
        
        # Определяем тип отчета на основе запроса
        is_general_stats = (
            any(word in question_lower for word in [
                "общая статистика", "общие показатели", "всего", "итого", 
                "общий расход", "общие показы", "общие клики", "покажи общую статистику"
            ]) or analysis_type == "all_campaigns"
        )
        
        # Проверяем, есть ли конкретное название кампании в запросе
        campaign_name = self._extract_campaign_name(question)
        
        # Если это анализ всех кампаний, то не считаем это анализом конкретной кампании
        is_campaign_specific = (
            any(word in question_lower for word in [
                "по кампании", "кампания", "отчет по", "статистика по", "сделай отчет по", "покажи отчет по"
            ]) and campaign_name and analysis_type != "all_campaigns"
        )
        
        is_product_specific = any(word in question_lower for word in [
            "по продукту", "продукт", "рко", "рбидос", "бизнес-карты", "бизнес-кредиты"
        ]) and not campaign_name  # Не показываем анализ продукта, если есть конкретная кампания
        
        is_platform_analysis = any(word in question_lower for word in [
            "по площадкам", "площадки", "платформа", "эффективность площадок"
        ])
        
        is_performance_analysis = any(word in question_lower for word in [
            "эффективность", "конверсия", "результат", "лучший", "лучшие", "топ"
        ])
        
        is_trend_analysis = any(word in question_lower for word in [
            "по дням", "тренд", "динамика", "время", "дата", "график"
        ])
        
        # Проверяем, является ли это анализом воронки
        is_funnel_analysis = analysis.get("summary", {}).get("analysis_type") == "funnel_analysis"
        
        if is_funnel_analysis:
            return self._generate_funnel_report(analysis, question, sql_query)
        
        # Используем уже определенные переменные
        
        # Начинаем формировать отчет
        report = f"# 📊 Отчет по запросу: {question}\n\n"
        
        # Общая статистика
        if analysis_type == "all_campaigns":
            report += "## 📈 Общая статистика по всем кампаниям\n\n"
            report += f"**Всего кампаний:** {summary.get('campaigns_count', 0)}\n"
            report += f"**Общие показы:** {summary.get('total_impressions', 0):,.0f}\n"
            report += f"**Общие клики:** {summary.get('total_clicks', 0):,.0f}\n"
            report += f"**Общий расход:** {summary.get('total_cost', 0):,.0f} ₽\n"
            report += f"**Общие визиты:** {summary.get('total_visits', 0):,.0f}\n"
            report += f"**Средний CTR:** {summary.get('avg_ctr', 0):.2f}%\n"
            report += f"**Средний CPC:** {summary.get('avg_cpc', 0):.2f} ₽\n\n"
            
            # Показываем найденные кампании
            if "found_campaigns" in summary:
                report += "## 🎯 Проанализированные кампании\n\n"
                if len(summary["found_campaigns"]) <= 10:
                    for i, campaign in enumerate(summary["found_campaigns"], 1):
                        report += f"{i}. **{campaign.get('campaign_name', '—')}**\n"
                else:
                    report += f"**Всего кампаний:** {len(summary['found_campaigns'])}\n"
                    report += "**Основные кампании:**\n"
                    for i, campaign in enumerate(summary["found_campaigns"][:5], 1):
                        report += f"{i}. **{campaign.get('campaign_name', '—')}**\n"
                    report += f"... и еще {len(summary['found_campaigns']) - 5} кампаний\n"
                report += "\n"
            
            # Сравнительная таблица маркетинговых показателей
            if "campaigns" in summary and summary["campaigns"]:
                # Фильтруем только валидные кампании с данными
                valid_campaigns = [c for c in summary["campaigns"] if c.get('impressions', 0) > 0 and c.get('clicks', 0) > 0]
                
                if valid_campaigns:
                    report += "## 📊 Сравнительная таблица маркетинговых показателей\n\n"
                    
                    # Создаем таблицу с заголовками
                    report += "| Кампания | CTR | CPC | CPM | Конверсия | Показы | Клики | Расход |\n"
                    report += "|----------|-----|-----|-----|-----------|--------|-------|--------|\n"
                    
                    for campaign in valid_campaigns:
                        campaign_name = campaign.get('campaign_name', '—')
                        impressions = campaign.get('impressions', 0)
                        clicks = campaign.get('clicks', 0)
                        cost = campaign.get('cost', 0)
                        ctr = campaign.get('ctr', 0)
                        cpc = campaign.get('cpc', 0)
                        visits = campaign.get('visits', 0)
                        
                        # Рассчитываем дополнительные метрики
                        cpm = round((cost / impressions) * 1000, 2) if impressions > 0 else 0
                        conversion_rate = round((visits / clicks) * 100, 2) if clicks > 0 else 0
                        
                        # Форматируем данные для таблицы
                        report += f"| {campaign_name} | {ctr:.2f}% | {cpc:.2f} ₽ | {cpm:.2f} ₽ | {conversion_rate:.2f}% | {impressions:,.0f} | {clicks:,.0f} | {cost:,.0f} ₽ |\n"
                    
                    report += "\n"
                    
                    # Добавляем детальные маркетинговые показатели для каждой кампании
                    report += "## 📊 Детальные маркетинговые показатели по кампаниям\n\n"
                    
                    for i, campaign in enumerate(valid_campaigns, 1):
                        campaign_name = campaign.get('campaign_name', '—')
                        impressions = campaign.get('impressions', 0)
                        clicks = campaign.get('clicks', 0)
                        cost = campaign.get('cost', 0)
                        ctr = campaign.get('ctr', 0)
                        cpc = campaign.get('cpc', 0)
                        visits = campaign.get('visits', 0)
                        
                        # Рассчитываем дополнительные метрики
                        cpm = round((cost / impressions) * 1000, 2) if impressions > 0 else 0
                        conversion_rate = round((visits / clicks) * 100, 2) if clicks > 0 else 0
                        
                        report += f"### 🎯 {i}. {campaign_name}\n\n"
                        report += "**Основные метрики:**\n"
                        report += f"- CTR: **{ctr:.2f}%** - Click-Through Rate\n"
                        report += f"- CPC: **{cpc:.2f} ₽** - Cost Per Click\n"
                        report += f"- CPM: **{cpm:.2f} ₽** - Cost Per Mille\n"
                        report += f"- Конверсия: **{conversion_rate:.2f}%** - отношение посещений к кликам\n\n"
                        
                        report += "**Объемные показатели:**\n"
                        report += f"- Показы: {impressions:,.0f}\n"
                        report += f"- Клики: {clicks:,.0f}\n"
                        report += f"- Посещения: {visits:,.0f}\n"
                        report += f"- Расход: {cost:,.0f} ₽\n\n"
                        
                        # Добавляем оценку эффективности
                        if ctr > 2:
                            report += "**🏆 Оценка:** Высокий CTR - отличные результаты!\n"
                        elif ctr > 0.5:
                            report += "**✅ Оценка:** Средний CTR - хорошие результаты\n"
                        else:
                            report += "**⚠️ Оценка:** Низкий CTR - требует оптимизации\n"
                        
                        if cpc < 50:
                            report += "**💰 Оценка:** Экономичный CPC - эффективные затраты\n"
                        elif cpc < 200:
                            report += "**✅ Оценка:** Средний CPC - приемлемые затраты\n"
                        else:
                            report += "**💸 Оценка:** Высокий CPC - дорогие клики\n"
                        
                        report += "\n---\n\n"
        
        elif (is_campaign_specific or campaign_name) and "campaigns" in summary:
            # Анализ конкретной кампании или кампаний
            if len(summary["campaigns"]) == 1:
                # Одна кампания - показываем детальную статистику
                campaign = summary["campaigns"][0]
                report += f"## 📊 Отчет по кампании: {campaign.get('campaign_name', '—')}\n\n"
                
                # Основные метрики
                report += "### 📈 Основные показатели\n\n"
                report += f"**Показы:** {campaign.get('impressions', 0):,.0f}\n"
                report += f"**Клики:** {campaign.get('clicks', 0):,.0f}\n"
                report += f"**Расход:** {campaign.get('cost', 0):,.0f} ₽\n"
                report += f"**Посещения:** {campaign.get('visits', 0):,.0f}\n"
                report += f"**CTR:** {campaign.get('ctr', 0):.2f}%\n"
                report += f"**CPC:** {campaign.get('cpc', 0):.2f} ₽\n\n"
                
                # Рассчитываем дополнительные метрики
                impressions = campaign.get('impressions', 0)
                clicks = campaign.get('clicks', 0)
                cost = campaign.get('cost', 0)
                visits = campaign.get('visits', 0)
                
                if impressions > 0 and clicks > 0:
                    cpm = round((cost / impressions) * 1000, 2)
                    conversion_rate = round((visits / clicks) * 100, 2) if clicks > 0 else 0
                    
                    report += "**Дополнительные метрики:**\n"
                    report += f"- CPM: **{cpm:.2f} ₽** - Cost Per Mille\n"
                    report += f"- Конверсия: **{conversion_rate:.2f}%** - отношение посещений к кликам\n\n"
                    
                    # Оценка эффективности
                    ctr = campaign.get('ctr', 0)
                    cpc = campaign.get('cpc', 0)
                    
                    if ctr > 2:
                        report += "**🏆 Оценка CTR:** Высокий CTR - отличные результаты!\n"
                    elif ctr > 0.5:
                        report += "**✅ Оценка CTR:** Средний CTR - хорошие результаты\n"
                    else:
                        report += "**⚠️ Оценка CTR:** Низкий CTR - требует оптимизации\n"
                    
                    if cpc < 50:
                        report += "**💰 Оценка CPC:** Экономичный CPC - эффективные затраты\n"
                    elif cpc < 200:
                        report += "**✅ Оценка CPC:** Средний CPC - приемлемые затраты\n"
                    else:
                        report += "**💸 Оценка CPC:** Высокий CPC - дорогие клики\n"
                    
                    report += "\n"
            else:
                # Несколько кампаний - показываем общую статистику
                report += "## 📊 Общая статистика по кампаниям\n\n"
                report += f"**Всего кампаний:** {len(summary['campaigns'])}\n"
                report += f"**Общие показы:** {summary.get('total_impressions', 0):,.0f}\n"
                report += f"**Общие клики:** {summary.get('total_clicks', 0):,.0f}\n"
                report += f"**Общий расход:** {summary.get('total_cost', 0):,.0f} ₽\n"
                report += f"**Общие визиты:** {summary.get('total_visits', 0):,.0f}\n"
                report += f"**Средний CTR:** {summary.get('avg_ctr', 0):.2f}%\n"
                report += f"**Средний CPC:** {summary.get('avg_cpc', 0):.2f} ₽\n\n"
                
                # Детальная таблица по кампаниям
                # Фильтруем только кампании с данными
                campaigns_with_data = []
                for campaign in summary["campaigns"]:
                    impressions = campaign.get('impressions', 0)
                    clicks = campaign.get('clicks', 0)
                    cost = campaign.get('cost', 0)
                    
                    # Показываем кампанию только если есть хотя бы показы или клики
                    if impressions > 0 or clicks > 0:
                        campaigns_with_data.append(campaign)
                
                if campaigns_with_data:
                    # Добавляем заголовок только если он еще не был добавлен
                    if "## 📋 Детальная статистика по кампаниям" not in report:
                        report += "## 📋 Детальная статистика по кампаниям\n\n"
                    report += "| Кампания | Площадка | Показы | Клики | Расход | Визиты | CTR | CPC |\n"
                    report += "|----------|----------|--------|-------|--------|--------|-----|-----|\n"
                    
                    for campaign in campaigns_with_data:
                        campaign_name = campaign.get('campaign_name', '—')
                        platform = campaign.get('platform', '—')
                        impressions = campaign.get('impressions', 0)
                        clicks = campaign.get('clicks', 0)
                        cost = campaign.get('cost', 0)
                        visits = campaign.get('visits', 0)
                        ctr = campaign.get('ctr', 0)
                        cpc = campaign.get('cpc', 0)
                        
                        # Проверяем на NaN
                        if pd.isna(impressions) or impressions == 0:
                            impressions_str = "—"
                        else:
                            impressions_str = f"{impressions:,.0f}"
                        
                        if pd.isna(clicks) or clicks == 0:
                            clicks_str = "—"
                        else:
                            clicks_str = f"{clicks:,.0f}"
                        
                        if pd.isna(cost) or cost == 0:
                            cost_str = "—"
                        else:
                            cost_str = f"{cost:,.0f} ₽"
                        
                        if pd.isna(visits) or visits == 0:
                            visits_str = "—"
                        else:
                            visits_str = f"{visits:,.0f}"
                        
                        if pd.isna(ctr) or ctr == 0:
                            ctr_str = "—"
                        else:
                            ctr_str = f"{ctr:.2f}%"
                        
                        if pd.isna(cpc) or cpc == 0:
                            cpc_str = "—"
                        else:
                            cpc_str = f"{cpc:.2f} ₽"
                        
                        report += f"| {campaign_name} | {platform} | {impressions_str} | {clicks_str} | {cost_str} | {visits_str} | {ctr_str} | {cpc_str} |\n"
                    
                    report += "\n"
                
                report += "\n"
            
            # Анализ по площадкам
            if "platforms" in summary and summary["platforms"]:
                report += "## 📱 Эффективность по площадкам\n\n"
                # Убираем дубликаты площадок
                unique_platforms = {}
                for platform in summary["platforms"]:
                    platform_name = platform.get('platform', '—')
                    if platform_name not in unique_platforms:
                        unique_platforms[platform_name] = platform
                    else:
                        # Если площадка уже есть, суммируем данные
                        existing = unique_platforms[platform_name]
                        existing['impressions'] = existing.get('impressions', 0) + platform.get('impressions', 0)
                        existing['clicks'] = existing.get('clicks', 0) + platform.get('clicks', 0)
                        existing['cost'] = existing.get('cost', 0) + platform.get('cost', 0)
                        # Пересчитываем CTR и CPC
                        if existing['impressions'] > 0:
                            existing['ctr'] = round((existing['clicks'] / existing['impressions']) * 100, 2)
                        if existing['clicks'] > 0:
                            existing['cpc'] = round(existing['cost'] / existing['clicks'], 2)
                
                # Фильтруем только площадки с данными
                platforms_with_data = []
                for platform_name, platform_data in unique_platforms.items():
                    impressions = platform_data.get('impressions', 0)
                    clicks = platform_data.get('clicks', 0)
                    cost = platform_data.get('cost', 0)
                    
                    # Показываем площадку только если есть хотя бы показы или клики
                    if impressions > 0 or clicks > 0:
                        platforms_with_data.append((platform_name, platform_data))
                
                if platforms_with_data:
                    for platform_name, platform_data in platforms_with_data:
                        report += f"### {platform_name}\n\n"
                        
                        impressions = platform_data.get('impressions', 0)
                        clicks = platform_data.get('clicks', 0)
                        cost = platform_data.get('cost', 0)
                        ctr = platform_data.get('ctr', 0)
                        cpc = platform_data.get('cpc', 0)
                        
                        if impressions > 0:
                            report += f"**Показы:** {impressions:,.0f}\n\n"
                        
                        if clicks > 0:
                            report += f"**Клики:** {clicks:,.0f}\n\n"
                        
                        if cost > 0:
                            report += f"**Расход:** {cost:,.0f} ₽\n\n"
                        
                        if ctr > 0:
                            report += f"**CTR:** {ctr:.2f}%\n\n"
                        
                        if cpc > 0:
                            report += f"**CPC:** {cpc:.2f} ₽\n\n"
                        
                        report += "---\n\n"
        
        elif is_product_specific and "product_name" in summary:
            # Анализ продукта
            report += "## 📦 Статистика продукта\n\n"
            report += f"**Показы:** {summary.get('total_impressions', 0):,.0f}\n"
            report += f"**Клики:** {summary.get('total_clicks', 0):,.0f}\n"
            report += f"**Расход:** {summary.get('total_cost', 0):,.0f} ₽\n"
            report += f"**Средний CTR:** {summary.get('avg_ctr', 0):.2f}%\n"
            report += f"**Средний CPC:** {summary.get('avg_cpc', 0):.2f} ₽\n"
            report += f"**Количество кампаний:** {summary.get('campaigns_count', 0)}\n\n"
            
            # Анализ по кампаниям
            if "campaigns" in summary and summary["campaigns"]:
                report += "## 🎯 Кампании продукта\n\n"
                for campaign in summary["campaigns"]:
                    report += f"### {campaign.get('campaign_name', '—')}\n"
                    report += f"- Площадка: {campaign.get('platform', '—')}\n"
                    report += f"- Показы: {campaign.get('impressions', 0):,.0f}\n"
                    report += f"- Клики: {campaign.get('clicks', 0):,.0f}\n"
                    report += f"- Расход: {campaign.get('cost', 0):,.0f} ₽\n"
                    report += f"- CTR: {campaign.get('ctr', 0):.2f}%\n"
                    report += f"- CPC: {campaign.get('cpc', 0):.2f} ₽\n\n"
        
        elif is_platform_analysis and "platforms" in summary:
            # Анализ площадок
            report += "## 📱 Сравнение площадок\n\n"
            for platform in summary["platforms"]:
                report += f"### {platform.get('platform', '—')}\n"
                report += f"- Показы: {platform.get('impressions', 0):,.0f}\n"
                report += f"- Клики: {platform.get('clicks', 0):,.0f}\n"
                report += f"- Расход: {platform.get('cost', 0):,.0f} ₽\n"
                report += f"- CTR: {platform.get('ctr', 0):.2f}%\n"
                report += f"- CPC: {platform.get('cpc', 0):.2f} ₽\n\n"
        
        elif is_performance_analysis and "top_campaigns" in summary:
            # Анализ эффективности
            report += "## 🏆 Топ эффективных кампаний\n\n"
            for i, campaign in enumerate(summary["top_campaigns"], 1):
                report += f"### {i}. {campaign.get('campaign_name', '—')}\n"
                report += f"- Показы: {campaign.get('impressions', 0):,.0f}\n"
                report += f"- Клики: {campaign.get('clicks', 0):,.0f}\n"
                report += f"- Расход: {campaign.get('cost', 0):,.0f} ₽\n"
                report += f"- CTR: {campaign.get('ctr', 0):.2f}%\n"
                report += f"- CPC: {campaign.get('cpc', 0):.2f} ₽\n\n"
        
        elif is_trend_analysis and "trends" in summary:
            # Анализ трендов
            report += f"## 📈 Динамика за {summary.get('total_days', 0)} дней\n\n"
            for trend in summary["trends"][:10]:  # Показываем первые 10 дней
                report += f"### {trend.get('date', '—')}\n"
                report += f"- Показы: {trend.get('impressions', 0):,.0f}\n"
                report += f"- Клики: {trend.get('clicks', 0):,.0f}\n"
                report += f"- Расход: {trend.get('cost', 0):,.0f} ₽\n"
                report += f"- CTR: {trend.get('ctr', 0):.2f}%\n\n"
        
        # Инсайты
        if analysis.get("insights"):
            report += "## 💡 Ключевые инсайты\n\n"
            for insight in analysis["insights"]:
                report += f"• {insight}\n\n"
            report += "\n"
        
        # Маркетинговые показатели (показываем только для конкретных кампаний, не для всех кампаний)
        if analysis.get("marketing_metrics") and analysis.get("summary", {}).get("analysis_type") != "all_campaigns":
            metrics_report = marketing_goals.format_metrics_report(
                analysis["marketing_metrics"], 
                analysis.get("goals_comparison", {})
            )
            report += metrics_report + "\n"
        
        # Рекомендации
        if analysis.get("recommendations"):
            report += "## 🎯 Рекомендации\n\n"
            for rec in analysis["recommendations"]:
                report += f"• {rec}\n\n"
            report += "\n"
        
        return report
    
    def _generate_funnel_report(self, analysis: Dict, question: str, sql_query: str = "") -> str:
        """
        Генерация отчета по воронке
        """
        summary = analysis.get("summary", {})
        report = f"# 📊 Отчет по воронке: {question}\n\n"
        
        # Общая воронка
        if "visits" in summary:
            report += "## 🎯 Воронка конверсии\n\n"
            report += f"**Визиты:** {summary.get('visits', 0):,.0f}\n"
            report += f"**Заявки:** {summary.get('submits', 0):,.0f}\n"
            report += f"**Открытые счета:** {summary.get('accounts_opened', 0):,.0f}\n"
            report += f"**Созданные счета:** {summary.get('created', 0):,.0f}\n"
            report += f"**Отвеченные звонки:** {summary.get('calls_answered', 0):,.0f}\n"
            report += f"**Качественные лиды:** {summary.get('quality_leads', 0):,.0f}\n\n"
            
            report += "**Конверсии:**\n"
            report += f"- Визиты → Заявки: **{summary.get('conversion_to_submits', 0):.2f}%**\n"
            report += f"- Заявки → Счета: **{summary.get('conversion_to_accounts', 0):.2f}%**\n"
            report += f"- Счета → Качество: **{summary.get('conversion_to_quality', 0):.2f}%**\n\n"
        
        # Сравнение источников
        elif "sources_comparison" in summary:
            report += "## 📊 Сравнение источников трафика\n\n"
            report += "| Источник | Визиты | Заявки | Счета | Качественные | Конв. в заявки | Конв. в счета |\n"
            report += "|----------|--------|--------|-------|--------------|----------------|---------------|\n"
            
            for source in summary["sources_comparison"]:
                report += f"| {source.get('utm_source', '—')} | {source.get('visits', 0):,.0f} | {source.get('submits', 0):,.0f} | {source.get('accounts_opened', 0):,.0f} | {source.get('quality_leads', 0):,.0f} | {source.get('conversion_to_submits', 0):.2f}% | {source.get('conversion_to_accounts', 0):.2f}% |\n"
            
            report += "\n"
        
        # Динамика по дням
        elif "daily_trends" in summary:
            report += "## 📈 Динамика по дням\n\n"
            report += "| Дата | Визиты | Заявки | Счета | Качественные |\n"
            report += "|------|--------|--------|-------|--------------|\n"
            
            for trend in summary["daily_trends"][:10]:  # Показываем первые 10 дней
                report += f"| {trend.get('date', '—')} | {trend.get('visits', 0):,.0f} | {trend.get('submits', 0):,.0f} | {trend.get('accounts_opened', 0):,.0f} | {trend.get('quality_leads', 0):,.0f} |\n"
            
            report += "\n"
        
        # Топ кампаний
        elif "top_campaigns" in summary:
            report += "## 🏆 Топ кампаний по заявкам\n\n"
            report += "| Кампания | Визиты | Заявки | Счета | Качественные | Конверсия |\n"
            report += "|----------|--------|--------|-------|--------------|-----------|\n"
            
            for campaign in summary["top_campaigns"]:
                report += f"| {campaign.get('utm_campaign', '—')} | {campaign.get('visits', 0):,.0f} | {campaign.get('submits', 0):,.0f} | {campaign.get('accounts_opened', 0):,.0f} | {campaign.get('quality_leads', 0):,.0f} | {campaign.get('conversion_to_submits', 0):.2f}% |\n"
            
            report += "\n"
        
        # Инсайты
        if analysis.get("insights"):
            report += "## 💡 Ключевые инсайты\n\n"
            for insight in analysis["insights"]:
                report += f"- {insight}\n"
            report += "\n"
        
        # Рекомендации
        if analysis.get("recommendations"):
            report += "## 🎯 Рекомендации\n\n"
            for rec in analysis["recommendations"]:
                report += f"- {rec}\n"
            report += "\n"
        
        return report
    
    def process_question(self, question: str) -> str:
        """
        Обработка вопроса пользователя с динамическим анализом
        """
        # Проверяем, является ли это запросом к воронке или UTM-меткам
        is_funnel_query = self._is_funnel_query(question)
        is_utm_query = self._is_utm_query(question)
        
        # Генерируем SQL запрос
        sql_query = self.generate_sql_query(question)
        
        # Выполняем запрос
        df = self.execute_query(sql_query)
        
        # Проверяем, есть ли данные
        has_data = not df.empty and not (len(df) == 1 and df.iloc[0].get('result') == 'no_data')
        
        # Проверяем, спрашивает ли пользователь о терминах/метриках
        is_asking_about_terms = any(word in question.lower() for word in [
            'что такое', 'что означает', 'определение', 'расшифровка', 'ctr', 'cpc', 'cpm', 'конверсия'
        ])
        
        # Анализируем данные только если они есть
        if has_data:
            analysis = self.analyze_data(df, question)
            report = self.generate_report(analysis, question, sql_query)
        else:
            # Если данных нет, создаем базовый отчет
            report = f"# 📋 Отчет по запросу: {question}\n\n"
            report += "Нет данных для анализа по вашему запросу.\n\n"
        
        # Используем RAG только в определенных случаях:
        # 1. Нет данных для анализа ИЛИ
        # 2. Пользователь явно спрашивает о терминах/метриках
        should_use_rag = not has_data or is_asking_about_terms
        
        if should_use_rag and self.rag_system is not None:
            try:
                # Улучшаем отчет с помощью RAG системы
                enhanced_report = self.rag_system.enhance_report(report, question)
                if enhanced_report != report:
                    report = enhanced_report
            except Exception as e:
                # Если RAG система недоступна, используем базовый отчет
                pass
        
        # Сохраняем в историю
        self.conversation_history.append({
            "question": question,
            "answer": report,
            "timestamp": datetime.now().isoformat()
        })
        
        # Возвращаем отчет и SQL запрос отдельно
        return report, sql_query
    
    def get_conversation_history(self) -> List[Dict]:
        """Получение истории диалога"""
        return self.conversation_history
    
    def _extract_utm_parameters(self, question: str) -> Dict[str, str]:
        """
        Извлечение UTM-параметров из вопроса пользователя
        """
        question_lower = question.lower()
        utm_params = {}
        
        # Ищем UTM-параметры
        utm_patterns = {
            'utm_campaign': ['utm_campaign', 'utm campaign', 'кампания utm', 'utm кампания'],
            'utm_source': ['utm_source', 'utm source', 'источник utm', 'utm источник'],
            'utm_medium': ['utm_medium', 'utm medium', 'канал utm', 'utm канал'],
            'utm_content': ['utm_content', 'utm content', 'контент utm', 'utm контент'],
            'utm_term': ['utm_term', 'utm term', 'термин utm', 'utm термин']
        }
        
        for param, patterns in utm_patterns.items():
            for pattern in patterns:
                if pattern in question_lower:
                    # Ищем значение после знака равенства, двоеточия или пробела
                    start_idx = question_lower.find(pattern) + len(pattern)
                    if start_idx < len(question_lower):
                        # Ищем знак равенства, двоеточие или пробел
                        for sep in ['=', ':', ' ']:
                            if sep in question_lower[start_idx:]:
                                value_start = question_lower.find(sep, start_idx) + 1
                                if value_start < len(question_lower):
                                    # Извлекаем значение до следующего пробела или конца
                                    value_end = question_lower.find(' ', value_start)
                                    if value_end == -1:
                                        value_end = len(question_lower)
                                    value = question_lower[value_start:value_end].strip()
                                    if value:
                                        utm_params[param] = value
                                        break
                        break
        
        # Дополнительная логика для извлечения названий кампаний после UTM-параметров
        if 'utm_campaign' in question_lower:
            # Ищем название кампании после "utm_campaign"
            campaign_keywords = ['rko_spring2024', 'rko', 'spring2024', 'spring', '2024']
            for keyword in campaign_keywords:
                if keyword in question_lower:
                    utm_params['utm_campaign'] = keyword
                    break
                    break
        
        return utm_params
    
    def _is_funnel_query(self, question: str) -> bool:
        """
        Определение, является ли запрос связанным с воронкой
        """
        question_lower = question.lower()
        funnel_keywords = [
            'воронка', 'воронку', 'конверсия', 'конверсии', 'заявки', 'заявок',
            'лиды', 'лидов', 'счета', 'счетов', 'регистрации', 'регистраций',
            'визиты', 'визитов', 'submits', 'account_num', 'created_flag',
            'call_answered_flag', 'quality_flag', 'quality', 'динамика', 'тренд'
        ]
        
        return any(keyword in question_lower for keyword in funnel_keywords)
    
    def _is_utm_query(self, question: str) -> bool:
        """
        Определение, является ли запрос связанным с UTM-метками
        """
        question_lower = question.lower()
        utm_keywords = [
            'utm', 'utm_campaign', 'utm_source', 'utm_medium', 'utm_content', 'utm_term',
            'метки', 'метка', 'параметры', 'параметр'
        ]
        
        return any(keyword in question_lower for keyword in utm_keywords)
    
    def _generate_funnel_sql(self, question: str, utm_params: Dict[str, str] = None) -> str:
        """
        Генерация SQL запроса для анализа воронки
        """
        question_lower = question.lower()
        
        # Определяем тип анализа воронки
        if any(word in question_lower for word in ['воронка', 'воронку', 'конверсия']):
            # Анализ воронки для конкретной кампании
            if utm_params and 'utm_campaign' in utm_params:
                campaign_value = utm_params['utm_campaign']
                sql = f"""
                SELECT 
                    'Воронка конверсии' as metric,
                    COUNT(DISTINCT visitID) as visits,
                    SUM(submits) as submits,
                    SUM(account_num) as accounts_opened,
                    SUM(created_flag) as created,
                    SUM(call_answered_flag) as calls_answered,
                    SUM(quality_flag) as quality_leads,
                    ROUND(SUM(submits) * 100.0 / COUNT(DISTINCT visitID), 2) as conversion_to_submits,
                    ROUND(SUM(account_num) * 100.0 / SUM(submits), 2) as conversion_to_accounts,
                    ROUND(SUM(quality_flag) * 100.0 / SUM(account_num), 2) as conversion_to_quality
                FROM funnel_data 
                WHERE utm_campaign = '{campaign_value}'
                """
            else:
                # Общая воронка
                sql = """
                SELECT 
                    'Общая воронка' as metric,
                    COUNT(DISTINCT visit_id) as visits,
                    SUM(submits) as submits,
                    SUM(account_num) as accounts_opened,
                    SUM(created_flag) as created,
                    SUM(call_answered_flag) as calls_answered,
                    SUM(quality_flag) as quality_leads,
                    ROUND(SUM(submits) * 100.0 / COUNT(DISTINCT visit_id), 2) as conversion_to_submits,
                    ROUND(SUM(account_num) * 100.0 / SUM(submits), 2) as conversion_to_accounts,
                    ROUND(SUM(quality_flag) * 100.0 / SUM(account_num), 2) as conversion_to_quality
                FROM funnel_data
                """
        
        elif any(word in question_lower for word in ['сравни', 'сравнение', 'источники', 'каналы']):
            # Сравнение источников
            sql = """
            SELECT 
                utm_source,
                COUNT(DISTINCT visit_id) as visits,
                SUM(submits) as submits,
                SUM(account_num) as accounts_opened,
                SUM(quality_flag) as quality_leads,
                ROUND(SUM(submits) * 100.0 / COUNT(DISTINCT visit_id), 2) as conversion_to_submits,
                ROUND(SUM(account_num) * 100.0 / SUM(submits), 2) as conversion_to_accounts,
                ROUND(SUM(quality_flag) * 100.0 / SUM(account_num), 2) as conversion_to_quality
            FROM funnel_data 
            WHERE utm_source IS NOT NULL
            GROUP BY utm_source
            ORDER BY visits DESC
            """
        
        elif any(word in question_lower for word in ['динамика', 'тренд', 'по дням', 'график']):
            # Динамика по дням
            # Извлекаем название кампании из запроса
            campaign_name = self._extract_campaign_name(question)
            if campaign_name:
                sql = f"""
                SELECT 
                    date,
                    COUNT(DISTINCT visit_id) as visits,
                    SUM(submits) as submits,
                    SUM(account_num) as accounts_opened,
                    SUM(quality_flag) as quality_leads
                FROM funnel_data 
                WHERE utm_campaign = '{campaign_name}'
                GROUP BY date
                ORDER BY date
                """
            elif utm_params and 'utm_campaign' in utm_params:
                campaign_value = utm_params['utm_campaign']
                sql = f"""
                SELECT 
                    date,
                    COUNT(DISTINCT visit_id) as visits,
                    SUM(submits) as submits,
                    SUM(account_num) as accounts_opened,
                    SUM(quality_flag) as quality_leads
                FROM funnel_data 
                WHERE utm_campaign = '{campaign_value}'
                GROUP BY date
                ORDER BY date
                """
            else:
                sql = """
                SELECT 
                    date,
                    COUNT(DISTINCT visit_id) as visits,
                    SUM(submits) as submits,
                    SUM(account_num) as accounts_opened,
                    SUM(quality_flag) as quality_leads
                FROM funnel_data 
                GROUP BY date
                ORDER BY date
                """
        
        elif any(word in question_lower for word in ['топ', 'лучшие', 'лучший']):
            # Топ кампаний
            sql = """
            SELECT 
                utm_campaign,
                COUNT(DISTINCT visit_id) as visits,
                SUM(submits) as submits,
                SUM(account_num) as accounts_opened,
                SUM(quality_flag) as quality_leads,
                ROUND(SUM(submits) * 100.0 / COUNT(DISTINCT visit_id), 2) as conversion_to_submits
            FROM funnel_data 
            WHERE utm_campaign IS NOT NULL
            GROUP BY utm_campaign
            ORDER BY submits DESC
            LIMIT 10
            """
        
        else:
            # Общая статистика
            sql = """
            SELECT 
                COUNT(DISTINCT visit_id) as visits,
                SUM(submits) as submits,
                SUM(account_num) as accounts_opened,
                SUM(created_flag) as created,
                SUM(call_answered_flag) as calls_answered,
                SUM(quality_flag) as quality_leads
            FROM funnel_data
            """
        
        return sql

# Пример использования
if __name__ == "__main__":
    agent = MarketingAnalyticsAgent()
    
    # Тестовые вопросы
    test_questions = [
        "Покажи общую статистику по рекламным кампаниям",
        "Какие кампании самые эффективные?",
        "Как работают разные площадки?",
        "Покажи тренды по дням"
    ]
    
    for question in test_questions:
        print(f"\n{'='*50}")
        print(f"Вопрос: {question}")
        print(f"{'='*50}")
        report = agent.process_question(question)
        print(report) 