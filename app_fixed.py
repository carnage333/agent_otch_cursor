import streamlit as st
import sqlite3
import pandas as pd
import json
from typing import Dict, List, Optional, Tuple
import re

# Простой агент без rapidfuzz
class SimpleMarketingAgent:
    def __init__(self, db_path: str = 'marketing_analytics.db'):
        self.db_path = db_path
    
    def _extract_search_terms(self, question: str) -> list:
        """Извлечение поисковых терминов"""
        question_upper = question.upper()
        keywords = []
        
        # Ищем после ключевых слов
        for kw in ["ПО КАМПАНИИ", "КАМПАНИЯ", "ОТЧЕТ ПО", "ОТЧЁТ ПО", "СДЕЛАЙ ОТЧЕТ ПО"]:
            if kw in question_upper:
                part = question_upper.split(kw, 1)[-1].strip()
                for w in ["ПОКАЖИ", "ОТЧЕТ", "ОТЧЁТ", "АНАЛИЗ", "СТАТИСТИКА"]:
                    part = part.replace(w, "").strip()
                keywords = [w for w in re.split(r"[\s,()]+", part) if w and len(w) > 1]
                break
        
        if not keywords:
            keywords = [w for w in re.split(r"[\s,()]+", question_upper) if len(w) > 2]
        
        return keywords
    
    def generate_sql_query(self, user_question: str) -> str:
        """Генерация SQL запроса"""
        question_lower = user_question.lower()
        
        # Определяем тип запроса
        is_general_stats = any(word in question_lower for word in [
            "общая статистика", "общие показатели", "всего", "итого", 
            "общий расход", "общие показы", "общие клики", "покажи общую статистику"
        ])
        
        if is_general_stats:
            select_fields = [
                "COUNT(DISTINCT campaign_id) as campaigns_count",
                "SUM(impressions) as total_impressions", 
                "SUM(clicks) as total_clicks",
                "SUM(cost_before_vat) as total_cost",
                "SUM(visits) as total_visits",
                "ROUND(SUM(clicks) * 100.0 / SUM(impressions), 2) as avg_ctr",
                "ROUND(SUM(cost_before_vat) / SUM(clicks), 2) as avg_cpc"
            ]
        else:
            select_fields = [
                "campaign_name",
                "platform", 
                "SUM(impressions) as impressions",
                "SUM(clicks) as clicks",
                "SUM(cost_before_vat) as cost",
                "SUM(visits) as visits",
                "ROUND(SUM(clicks) * 100.0 / SUM(impressions), 2) as ctr",
                "ROUND(SUM(cost_before_vat) / SUM(clicks), 2) as cpc"
            ]
        
        # Извлекаем поисковые термины
        search_terms = self._extract_search_terms(user_question)
        
        # Строим условия поиска
        where_conditions = []
        if search_terms:
            for term in search_terms:
                where_conditions.append(f"UPPER(campaign_name) LIKE '%{term}%'")
        
        # Собираем SQL
        sql = f"SELECT {', '.join(select_fields)} FROM campaign_metrics"
        if where_conditions:
            sql += f" WHERE {' AND '.join(where_conditions)}"
        sql += " GROUP BY campaign_name, platform ORDER BY campaign_name ASC"
        
        return sql
    
    def execute_query(self, sql_query: str) -> pd.DataFrame:
        """Выполнение SQL запроса"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(sql_query, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Ошибка выполнения SQL запроса: {e}")
            return pd.DataFrame()
    
    def generate_report(self, df: pd.DataFrame, question: str) -> str:
        """Генерация отчета"""
        if df.empty:
            return "## Нет данных для анализа по вашему запросу.\n"
        
        report = f"# Отчет по запросу: {question}\n\n"
        
        if "total_impressions" in df.columns:
            # Общая статистика
            row = df.iloc[0]
            report += "## Общая статистика\n\n"
            report += f"- **Количество кампаний:** {row.get('campaigns_count', '—')}\n"
            report += f"- **Общие показы:** {row.get('total_impressions', '—')}\n"
            report += f"- **Общие клики:** {row.get('total_clicks', '—')}\n"
            report += f"- **Общий расход:** {row.get('total_cost', '—')} ₽\n"
            report += f"- **Средний CTR:** {row.get('avg_ctr', '—')}%\n"
            report += f"- **Средний CPC:** {row.get('avg_cpc', '—')} ₽\n\n"
        else:
            # Детальная статистика
            report += "## Детальная статистика\n\n"
            for _, row in df.iterrows():
                report += f"### {row.get('campaign_name', '—')}\n"
                report += f"- Площадка: {row.get('platform', '—')}\n"
                report += f"- Показы: {row.get('impressions', '—')}\n"
                report += f"- Клики: {row.get('clicks', '—')}\n"
                report += f"- Расход: {row.get('cost', '—')} ₽\n"
                report += f"- CTR: {row.get('ctr', '—')}%\n"
                report += f"- CPC: {row.get('cpc', '—')} ₽\n\n"
        
        return report

# Streamlit приложение
st.set_page_config(page_title="AI Агент Отчетности", layout="wide")

st.title("🤖 AI Агент Отчетности по Рекламным Кампаниям")

# Инициализация агента
@st.cache_resource
def get_agent():
    return SimpleMarketingAgent()

agent = get_agent()

# Боковая панель
with st.sidebar:
    st.header("💬 Диалог с AI-агентом")
    
    # Поле ввода
    user_question = st.text_area(
        "Введите ваш вопрос:",
        placeholder="Например: сделай отчет по фрк4, покажи общую статистику, анализ по кампаниям...",
        height=100
    )
    
    if st.button("🔍 Получить отчет", type="primary"):
        if user_question.strip():
            with st.spinner("Генерирую отчет..."):
                # Генерируем SQL
                sql_query = agent.generate_sql_query(user_question)
                
                # Выполняем запрос
                df = agent.execute_query(sql_query)
                
                # Генерируем отчет
                report = agent.generate_report(df, user_question)
                
                # Сохраняем результаты в session_state
                st.session_state.sql_query = sql_query
                st.session_state.report = report
                st.session_state.data = df

# Основная область
if 'report' in st.session_state:
    st.markdown("## 📊 Результат анализа")
    
    # SQL запрос
    with st.expander("🔍 SQL запрос, сгенерированный агентом:", expanded=True):
        st.code(st.session_state.sql_query, language="sql")
        st.caption("Этот SQL запрос был автоматически создан агентом для получения данных")
    
    # Отчет
    st.markdown(st.session_state.report)

# Примеры вопросов
with st.expander("💡 Примеры вопросов"):
    st.markdown("""
    **Общая статистика:**
    - покажи общую статистику
    - общие показатели по кампаниям
    
    **По кампаниям:**
    - сделай отчет по фрк4
    - анализ кампании годовой performance
    - статистика по ФРК-4
    
    **По продуктам:**
    - отчет по рко
    - анализ по бизнес-карты
    - статистика по рбидос
    
    **По площадкам:**
    - эффективность площадок
    - анализ по платформам
    
    **Топ и рейтинги:**
    - топ кампаний
    - лучшие кампании по ctr
    """)

st.markdown("---")
st.caption("AI агент автоматически анализирует данные и генерирует SQL запросы для получения нужной информации.") 