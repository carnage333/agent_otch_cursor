import streamlit as st
import sqlite3
import pandas as pd

st.title("Тестовое приложение")

st.write("Приложение работает!")

# Простой тест базы данных
try:
    conn = sqlite3.connect('marketing_analytics.db')
    df = pd.read_sql_query("SELECT COUNT(*) as count FROM campaign_metrics", conn)
    conn.close()
    st.write(f"В базе данных {df.iloc[0]['count']} записей")
except Exception as e:
    st.write(f"Ошибка базы данных: {e}") 