import streamlit as st
import sqlite3
import pandas as pd

st.title("Тест развертывания")

# Проверяем наличие базы данных
try:
    conn = sqlite3.connect('marketing_analytics.db')
    st.success("✅ База данных подключена")
    
    # Проверяем таблицы
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    st.write(f"📊 Таблицы в базе: {[t[0] for t in tables]}")
    
    # Проверяем campaign_metrics
    if ('campaign_metrics',) in tables:
        st.success("✅ Таблица campaign_metrics найдена")
        
        # Проверяем структуру
        cursor.execute("PRAGMA table_info(campaign_metrics)")
        columns = cursor.fetchall()
        st.write("📋 Структура таблицы campaign_metrics:")
        for col in columns:
            st.write(f"  - {col[1]} ({col[2]})")
        
        # Проверяем количество записей
        cursor.execute("SELECT COUNT(*) FROM campaign_metrics")
        count = cursor.fetchone()[0]
        st.write(f"📈 Количество записей: {count}")
        
        # Проверяем уникальные кампании
        cursor.execute("SELECT DISTINCT \"Название кампании\" FROM campaign_metrics LIMIT 5")
        campaigns = cursor.fetchall()
        st.write("🎯 Примеры кампаний:")
        for campaign in campaigns:
            st.write(f"  - {campaign[0]}")
        
        # Тестируем запрос ФРК4
        cursor.execute("""
            SELECT DISTINCT "Название кампании" 
            FROM campaign_metrics 
            WHERE UPPER("Название кампании") LIKE '%ФРК4%'
        """)
        frk4_campaigns = cursor.fetchall()
        st.write(f"🔍 Кампании с ФРК4: {[c[0] for c in frk4_campaigns]}")
        
    else:
        st.error("❌ Таблица campaign_metrics не найдена")
    
    conn.close()
    
except Exception as e:
    st.error(f"❌ Ошибка: {e}")
    import traceback
    st.code(traceback.format_exc()) 