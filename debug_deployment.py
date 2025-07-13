import streamlit as st
import sqlite3
import os

st.title("🔍 Диагностика развертывания")

# Проверяем файлы
st.header("📁 Проверка файлов")
try:
    files = os.listdir('.')
    st.write("Файлы в директории:")
    for file in sorted(files):
        if file.endswith('.py') or file.endswith('.db'):
            st.write(f"  - {file}")
except Exception as e:
    st.error(f"Ошибка при чтении директории: {e}")

# Проверяем базу данных
st.header("🗄️ Проверка базы данных")
try:
    if os.path.exists('marketing_analytics.db'):
        st.success("✅ База данных найдена")
        size = os.path.getsize('marketing_analytics.db')
        st.write(f"Размер: {size:,} байт")
        
        conn = sqlite3.connect('marketing_analytics.db')
        cursor = conn.cursor()
        
        # Проверяем таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        st.write(f"Таблицы: {[t[0] for t in tables]}")
        
        if ('campaign_metrics',) in tables:
            st.success("✅ Таблица campaign_metrics найдена")
            
            # Проверяем структуру
            cursor.execute("PRAGMA table_info(campaign_metrics)")
            columns = cursor.fetchall()
            st.write("Структура таблицы:")
            for col in columns:
                st.write(f"  - {col[1]} ({col[2]})")
            
            # Проверяем количество записей
            cursor.execute("SELECT COUNT(*) FROM campaign_metrics")
            count = cursor.fetchone()[0]
            st.write(f"Количество записей: {count}")
            
            # Тестируем запрос
            try:
                cursor.execute("SELECT DISTINCT \"Название кампании\" FROM campaign_metrics LIMIT 3")
                campaigns = cursor.fetchall()
                st.write("Примеры кампаний:")
                for campaign in campaigns:
                    st.write(f"  - {campaign[0]}")
            except Exception as e:
                st.error(f"Ошибка при запросе: {e}")
        else:
            st.error("❌ Таблица campaign_metrics не найдена")
        
        conn.close()
    else:
        st.error("❌ База данных не найдена")
        
except Exception as e:
    st.error(f"Ошибка при работе с базой данных: {e}")
    import traceback
    st.code(traceback.format_exc())

# Проверяем версию кода
st.header("📝 Проверка кода")
try:
    with open('ai_agent.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if len(lines) >= 320:
            line_320 = lines[319].strip()  # 0-based indexing
            st.write(f"Строка 320: {line_320}")
            if "Название кампании" in line_320:
                st.success("✅ Код исправлен правильно")
            else:
                st.error("❌ Код не исправлен")
        else:
            st.error("❌ Файл слишком короткий")
except Exception as e:
    st.error(f"Ошибка при чтении файла: {e}")

st.header("🎯 Рекомендации")
st.write("""
1. Если база данных не найдена - проблема с развертыванием
2. Если код не исправлен - изменения не применились
3. Если все в порядке - попробуйте перезапустить приложение
""") 