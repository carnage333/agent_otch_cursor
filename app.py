import streamlit as st
import pandas as pd
from ai_agent import MarketingAnalyticsAgent
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sqlite3

# Настройка страницы с улучшенным дизайном
st.set_page_config(
    page_title="AI-агент отчетности | Маркетинг",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Кастомные CSS стили для современного UI
st.markdown("""
<style>
    /* Основные стили */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .chat-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    
    .example-question {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .example-question:hover {
        background: #e9ecef;
        transform: translateX(5px);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .success-message {
        background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .info-message {
        background: linear-gradient(90deg, #17a2b8 0%, #6f42c1 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .warning-message {
        background: linear-gradient(90deg, #ffc107 0%, #fd7e14 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Анимации */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Улучшенные графики */
    .plotly-chart {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    
    /* Кастомные метрики */
    .metric-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .metric-label {
        color: #6c757d;
        font-size: 0.9rem;
    }
    
    /* Стили для поля ввода */
    .stChatInput {
        margin: 2rem auto;
        width: 100%;
        max-width: 800px;
    }
    
    .stChatInput > div {
        background: white;
        border-radius: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .stChatInput > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
        transform: translateY(-2px);
    }
    
    .stChatInput input {
        border: none !important;
        background: transparent !important;
        padding: 15px 20px !important;
        font-size: 16px !important;
    }
    
    .stChatInput input:focus {
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* Отступ для контента, чтобы не перекрывался полем ввода */
    .main-content {
        padding-bottom: 100px;
    }
</style>
""", unsafe_allow_html=True)

# Инициализация базы данных
import init_db
init_db.init_database()

# Инициализация агента
@st.cache_resource
def get_agent():
    try:
        return MarketingAnalyticsAgent()
    except Exception as e:
        st.error(f"Ошибка инициализации агента: {e}")
        return None

agent = get_agent()

# Проверяем, что агент инициализирован
if agent is None:
    st.error("Не удалось инициализировать агент. Приложение не может работать.")
    st.stop()



# Главный заголовок с градиентом
st.markdown("""
<div class="main-header fade-in">
    <h1>Прототип AI-Агента отчетности в Cursor</h1>
    <p style="margin: 0; opacity: 0.9;">AI-агент отчетности по рекламным кампаниям</p>
</div>
""", unsafe_allow_html=True)

# Основной контент - только диалог с агентом
st.markdown('<div class="main-content">', unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pending_campaign_select" not in st.session_state:
    st.session_state.pending_campaign_select = None
if "pending_user_question" not in st.session_state:
    st.session_state.pending_user_question = None
    
# Контейнер для чата
chat_container = st.container()
with chat_container:
    for i, message in enumerate(st.session_state.chat_history):
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(message["content"])
                
                # Кнопка скачивания Excel
                if "excel_data" in message and message["excel_data"] and len(message["excel_data"]) > 0:
                    st.download_button(
                        label="📊 Скачать Excel отчет",
                        data=message["excel_data"],
                        file_name=f"отчет_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                elif "excel_data" in message and (not message["excel_data"] or len(message["excel_data"]) == 0):
                    st.info("📊 Excel отчет недоступен (требуется библиотека openpyxl)")
                
                if "sql_query" in message and message["sql_query"]:
                    with st.expander("🔍 Показать SQL запрос", expanded=False):
                        # Форматируем SQL запрос для лучшей читаемости
                        sql_query = message["sql_query"]
                        # Добавляем переносы строк для лучшей читаемости
                        formatted_sql = sql_query.replace("SELECT", "\nSELECT")
                        formatted_sql = formatted_sql.replace("FROM", "\nFROM")
                        formatted_sql = formatted_sql.replace("WHERE", "\nWHERE")
                        formatted_sql = formatted_sql.replace("GROUP BY", "\nGROUP BY")
                        formatted_sql = formatted_sql.replace("ORDER BY", "\nORDER BY")
                        formatted_sql = formatted_sql.replace("SUM(", "\n  SUM(")
                        formatted_sql = formatted_sql.replace("ROUND(", "\n  ROUND(")
                        
                        st.code(formatted_sql, language="sql")
                        st.markdown("*Этот SQL запрос был автоматически создан агентом для получения данных*")
    
# Если ожидается выбор кампании
if st.session_state.pending_campaign_select:
    st.markdown("""
    <div class="info-message">
        <h4>🎯 Найдено несколько кампаний</h4>
        <p>Пожалуйста, выберите одну для детального отчета или выберите 'Все кампании' для общего анализа.</p>
    </div>
    """, unsafe_allow_html=True)
    
    campaign_options = ["Все кампании"] + st.session_state.pending_campaign_select
    selected_campaign = st.selectbox("Выберите кампанию:", campaign_options, key=f"select_{st.session_state.pending_user_question}")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("📊 Показать отчет", key=f"show_report_{st.session_state.pending_user_question}"):
            if selected_campaign == "Все кампании":
                # Для "Все кампаний" формируем SQL запрос для всех найденных кампаний
                campaign_conditions = " OR ".join([f"\"Название кампании\" = '{campaign}'" for campaign in st.session_state.pending_campaign_select])
                sql_query = f"""
                SELECT 
                    "Название кампании" as campaign_name,
                    "Площадка" as platform,
                    SUM("Показы") as impressions,
                    SUM("Клики") as clicks,
                    SUM("Расход до НДС") as cost,
                    SUM("Визиты") as visits,
                    ROUND(SUM("Клики") * 100.0 / SUM("Показы"), 2) as ctr,
                    ROUND(SUM("Расход до НДС") / SUM("Клики"), 2) as cpc
                FROM campaign_metrics 
                WHERE {campaign_conditions}
                GROUP BY "Название кампании", "Площадка"
                ORDER BY "Название кампании" ASC
                """
                if agent:
                    df = agent.execute_query(sql_query)
                    analysis = agent.analyze_data(df, str(st.session_state.pending_user_question))
                    response = agent.generate_report(analysis, str(st.session_state.pending_user_question), sql_query)
                    try:
                        excel_data = agent.generate_excel_report(analysis, str(st.session_state.pending_user_question))
                    except Exception as e:
                        print(f"Ошибка генерации Excel: {e}")
                        excel_data = None
                    # SQL запрос передается отдельно
                else:
                    response = "❌ Ошибка: агент недоступен"
                    sql_query = ""
                    excel_data = None
            else:
                # Формируем SQL запрос только для выбранной кампании
                sql_query = f"SELECT \"Название кампании\" as campaign_name, \"Площадка\" as platform, SUM(\"Показы\") as impressions, SUM(\"Клики\") as clicks, SUM(\"Расход до НДС\") as cost, SUM(\"Визиты\") as visits, ROUND(SUM(\"Клики\") * 100.0 / SUM(\"Показы\"), 2) as ctr, ROUND(SUM(\"Расход до НДС\") / SUM(\"Клики\"), 2) as cpc FROM campaign_metrics WHERE \"Название кампании\" = '{selected_campaign}' GROUP BY \"Название кампании\", \"Площадка\" ORDER BY \"Название кампании\" ASC"
                if agent:
                    df = agent.execute_query(sql_query)
                    analysis = agent.analyze_data(df, f"Сделай отчет по кампании {selected_campaign}")
                    response = agent.generate_report(analysis, f"Сделай отчет по кампании {selected_campaign}", sql_query)
                    try:
                        excel_data = agent.generate_excel_report(analysis, f"Сделай отчет по кампании {selected_campaign}")
                    except Exception as e:
                        print(f"Ошибка генерации Excel: {e}")
                        excel_data = None
                    # SQL запрос передается отдельно
                else:
                    response = "❌ Ошибка: агент недоступен"
                    sql_query = ""
                    excel_data = None
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "sql_query": sql_query,
                "excel_data": excel_data
            })
            st.session_state.pending_campaign_select = None
            st.session_state.pending_user_question = None
            st.rerun()
    
    with col2:
        if st.button("🔄 Отменить", key=f"cancel_{st.session_state.pending_user_question}"):
            st.session_state.pending_campaign_select = None
            st.session_state.pending_user_question = None
            st.rerun()

# Кнопка очистки истории только если есть сообщения в истории
if st.session_state.chat_history:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🗑️ Очистить историю диалога", key="clear_history"):
            st.session_state.chat_history = []
            st.success("✅ История диалога очищена!")
            st.rerun()

# Поле ввода с улучшенным дизайном
user_question = st.chat_input("💬 Задайте вопрос агенту...")

st.markdown('</div>', unsafe_allow_html=True)

# Сброс ожидания выбора кампании при новом вопросе
if user_question and st.session_state.pending_campaign_select:
    st.session_state.pending_campaign_select = None
    st.session_state.pending_user_question = None

# --- Новая логика выбора кампании ---
if user_question and not st.session_state.pending_campaign_select:
    if agent:
        matching_campaigns = agent.get_matching_campaigns(user_question)
        if len(matching_campaigns) > 1:
            st.session_state.pending_campaign_select = matching_campaigns
            st.session_state.pending_user_question = user_question
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            st.rerun()
        elif len(matching_campaigns) == 1:
            # Если найдена только одна кампания, сразу показываем отчет
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            with st.spinner("🤖 Агент анализирует данные..."):
                response, sql_query, excel_data = agent.process_question(user_question)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "sql_query": sql_query,
                "excel_data": excel_data
            })
            st.rerun()
        else:
            # Если кампании не найдены, показываем сообщение об ошибке
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "❌ Не найдено кампаний по вашему запросу. Попробуйте изменить формулировку вопроса.",
                "sql_query": ""
            })
            st.rerun()
    else:
        st.error("❌ Агент недоступен. Пожалуйста, перезапустите приложение.") 