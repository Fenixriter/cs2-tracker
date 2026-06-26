import streamlit as st
import json
import os
import requests
import plotly.express as px
from datetime import datetime

# Настройка страницы
st.set_page_config(page_title="CS2 Portfolio Dashboard 2026", layout="wide")

# --- ФУНКЦИЯ КИБЕРБЕЗОПАСНОСТИ (ЧТЕНИЕ СЕКРЕТОВ) ---
def get_secret_password():
    """Читает пароль из скрытого файла. Если файла нет, создает временный."""
    secrets_file = "secrets.txt"
    if os.path.exists(secrets_file):
        with open(secrets_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    else:
        # Если файла нет, создаем его с безопасным паролем по умолчанию
        with open(secrets_file, "w", encoding="utf-8") as f:
            f.write("SafePassword2026")
        return "SafePassword2026"

def check_password():
    """Проверяет введенный пользователем пароль."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.title("🔒 Доступ ограничен")
    st.markdown("Этот дашборд защищен. Введите пароль из вашего локального файла конфигурации.")
    
    password = st.text_input("Введите секретный пароль:", type="password")
    
    if st.button("Войти"):
        # Сравниваем с паролем из скрытого файла, а не из кода!
        correct_password = get_secret_password()
        if password == correct_password:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ Неверный пароль! Доступ заблокирован.")
            
    return False

# Если проверка пройдена, запускаем приложение
if check_password():

    DATA_FILE = "cs2_portfolio.json"
    PRICES_URL = "https://githubusercontent.com"
    EXCHANGE_URL = "https://cbr-xml-daily.ru"

    @st.cache_data(ttl=3600)
    def fetch_market_data():
        try:
            prices = requests.get(PRICES_URL, timeout=10).json()
        except:
            prices = {}
            
        try:
            response = requests.get(EXCHANGE_URL, timeout=10).json()
            usd_to_rub = response["Valute"]["USD"]["Value"]
        except:
            usd_to_rub = 92.50
        return prices, usd_to_rub

    def load_portfolio():
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_portfolio(data):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # Инициализация данных
    prices_db, usd_to_rub = fetch_market_data()
    portfolio = load_portfolio()

    all_skins_list = sorted(list(prices_db.keys())) if prices_db else ["AK-47 | Redline (Field-Tested)"]

    # --- НАСТРОЙКА ТЕМ ОФОРМЛЕНИЯ ---
    with st.sidebar:
        st.header("Настройки интерфейса")
        theme_choice = st.radio("Выберите тему оформления:", options=["Стандартная темная (Classic Dark)", "Светлая (Clean Light)"], index=0)
        st.markdown("---")

    if theme_choice == "Стандартная темная (Classic Dark)":
        plotly_theme = "plotly_dark"
        color_scale = px.colors.sequential.Plotly3
        st.markdown("""
            <style>
            .stApp { background-color: #0e1117 !important; color: #ffffff !important; }
            div[data-testid="stSidebar"] { background-color: #111827 !important; }
            div[data-testid="stMetric"] { 
                background-color: #1f2937 !important; 
                border-radius: 12px !important; 
                padding: 20px !important; 
                border: 1px solid #374151 !important; 
            }
            div[data-testid="stMetric"] label, 
            div[data-testid="stMetric"] div[data-testid="stMetricValue"] { 
                color: #ffffff !important; 
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        plotly_theme = "plotly_white"
        color_scale = px.colors.sequential.Viridis
        st.markdown("""
            <style>
            .stApp { background-color: #f9fafb !important; color: #111827 !important; }
            div[data-testid="stSidebar"] { background-color: #f3f4f6 !important; }
            div[data-testid="stMetric"] { 
                background-color: #ffffff !important; 
                border-radius: 12px !important; 
                padding: 20px !important; 
                border: 1px solid #e5e7eb !important; 
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1) !important; 
            }
            div[data-testid="stMetric"] label, 
            div[data-testid="stMetric"] div[data-testid="stMetricValue"] { 
                color: #111827 !important; 
            }
            </style>
        """, unsafe_allow_html=True)

    # --- ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ---
    st.title("CS2 Portfolio Dashboard Pro (v2026)")
    st.markdown("---")

    with st.sidebar:
        st.header("Управление активами")
        skin_name = st.selectbox("Выберите скин из базы Steam:", options=all_skins_list)
        buy_price = st.number_input("Цена покупки ($):", min_value=0.0, value=10.0, step=0.5)
        quantity = st.number_input("Количество (шт):", min_value=1, value=1, step=1)
        
        if st.button("Добавить в портфель", use_container_width=True):
            new_item = {
                "date": datetime.now().strftime("%d.%m.%Y"),
                "name": skin_name,
                "buy_price": buy_price,
                "quantity": quantity
            }
            portfolio.append(new_item)
            save_portfolio(portfolio)
            st.success("Предмет успешно добавлен!")
            st.rerun()

        st.markdown("---")
        st.subheader("Удаление предметов")
        if portfolio:
            item_to_delete = st.selectbox("Выберите предмет для удаления:", options=[i["name"] for i in portfolio])
            if st.button("Удалить выбранное", use_container_width=True):
                portfolio = [i for i in portfolio if i["name"] != item_to_delete]
                save_portfolio(portfolio)
                st.warning("Предмет удален.")
                st.rerun()
        else:
            st.info("Портфолио пока пусто.")

    # --- РАСЧЕТ МЕТРИК ---
    total_invested_usd = 0.0
    total_current_usd = 0.0
    processed_items = []

    for item in portfolio:
        name = item["name"]
        b_price = item["buy_price"]
        qty = item["quantity"]
        spent = b_price * qty
        total_invested_usd += spent
        
        price_data = prices_db.get(name, {})
        live_price = 0.0
        if isinstance(price_data, dict):
            live_price = price_data.get("average", price_data.get("lowest_price", 0.0))
        elif isinstance(price_data, (int, float)):
            live_price = float(price_data)
            
        if live_price == 0.0:
            live_price = b_price
            
        current_val = live_price * qty
        total_current_usd += current_val
        
        profit = current_val - spent
        roi = (profit / spent) * 100 if spent > 0 else 0.0
        
        processed_items.append({
            "Дата": item["date"],
            "Название скина": name,
            "Цена покупки": f"${b_price:.2f}",
            "Кол-во": qty,
            "Потрачено ($)": spent,
            "Текущая цена": f"${live_price:.2f}",
            "Профит ($)": round(profit, 2),
            "ROI": f"{roi:.1f}%",
            "Raw_Current_Val": current_val
        })

    total_profit_usd = total_current_usd - total_invested_usd
    total_roi = (total_profit_usd / total_invested_usd) * 100 if total_invested_usd > 0 else 0.0

    # --- КАРТОЧКИ СТАТИСТИКИ ---
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="ИНВЕСТИРОВАНО (В СЕГО)", 
                  value=f"${total_invested_usd:,.2f}", 
                  delta=f"{total_invested_usd * usd_to_rub:,.0f} RUB")

    with col2:
        st.metric(label="ТЕКУЩАЯ СТОИМОСТЬ", 
                  value=f"${total_current_usd:,.2f}", 
                  delta=f"{total_current_usd * usd_to_rub:,.0f} RUB")

    with col3:
        sign = "+" if total_profit_usd >= 0 else ""
        st.metric(label="ЧИСТЫЙ ПРОФИТ / ROI", 
                  value=f"{sign}${total_profit_usd:,.2f} ({sign}{total_roi:.1f}%)",
                  delta=f"{total_profit_usd * usd_to_rub:,.0f} RUB",
                  delta_color="normal" if total_profit_usd >= 0 else "inverse")

    st.markdown("---")

    # --- ТАБЛИЦА И ГРАФИКИ ---
    if portfolio:
        tab1, tab2 = st.tabs(["Инвентарная таблица", "Визуальный анализ долей"])
        
        with tab1:
            st.subheader("Ваши активные инвестиции")
            st.dataframe(processed_items, use_container_width=True, hide_index=True)
            st.caption(f"Курс доллара обновлен по данным ЦБ РФ: 1 USD = {usd_to_rub:.2f} RUB")
            
        with tab2:
            st.subheader("Распределение капитала в портфеле")
            fig = px.pie(
                processed_items, 
                values='Raw_Current_Val', 
                names='Название скина', 
                hole=0.4,
                template=plotly_theme,
                color_discrete_sequence=color_scale
            )
            fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Добавьте ваш первый скин на боковой панели слева, чтобы запустить аналитику!")
