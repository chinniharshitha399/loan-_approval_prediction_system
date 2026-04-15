import streamlit as st
import os
import sys
from dotenv import load_dotenv

# Load .env from project root — applies to ALL pages
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path, override=True)

sys.path.append(os.path.dirname(__file__))


st.set_page_config(
    page_title="LOAN APPROVAL PREDICTION SYSTEM",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>

/* ── Force all text white ── */
html, body, [class*="css"], [data-testid="stAppViewContainer"],
p, span, label, div, h1, h2, h3, h4, h5, h6,
.stMarkdown, .stText, .element-container {
    color: #ffffff !important;
}

/* ── Background ── */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e) !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(15, 12, 41, 0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.15) !important;
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

/* ── Inputs, selects, sliders ── */
input, textarea, select,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] select {
    background-color: rgba(255,255,255,0.1) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 8px !important;
}

/* ── Select box dropdown ── */
[data-testid="stSelectbox"] > div > div {
    background-color: #1e1b4b !important;
    color: #ffffff !important;
}

/* ── Slider ── */
[data-testid="stSlider"] * {
    color: #ffffff !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
[data-testid="stMetric"] * {
    color: #ffffff !important;
}
[data-testid="stMetricDelta"] {
    color: #00e676 !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] button {
    color: #aaaaaa !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #7eb3ff !important;
    border-bottom: 2px solid #7eb3ff !important;
}

/* ── Dataframe / Table ── */
[data-testid="stDataFrame"] * {
    color: #ffffff !important;
    background-color: #1e1b4b !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] * {
    color: #ffffff !important;
}

/* ── Alerts / Info / Warning / Success ── */
[data-testid="stAlert"] {
    background: rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
}
.stSuccess { background: rgba(0,176,155,0.2) !important; color: #ffffff !important; }
.stWarning { background: rgba(255,193,7,0.2)  !important; color: #ffffff !important; }
.stError   { background: rgba(245,81,95,0.2)  !important; color: #ffffff !important; }
.stInfo    { background: rgba(126,179,255,0.2) !important; color: #ffffff !important; }

/* ── Buttons ── */
div[data-testid="stButton"] > button {
    background: linear-gradient(90deg, #667eea, #764ba2) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 28px !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    transition: transform 0.2s !important;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(102,126,234,0.5) !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(90deg, #00b09b, #96c93d) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
}

/* ── Form ── */
[data-testid="stForm"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 16px !important;
    padding: 24px !important;
}

/* ── Cards ── */
.metric-card {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    text-align: center !important;
    margin-bottom: 16px !important;
    color: #ffffff !important;
}
.metric-card h3 { color: #7eb3ff !important; }
.metric-card p  { color: #cccccc !important; }

/* ── Result banners ── */
.approved-banner {
    background: linear-gradient(135deg, #00b09b, #96c93d) !important;
    padding: 24px !important; border-radius: 16px !important;
    text-align: center !important; font-size: 1.8rem !important;
    font-weight: 700 !important; color: #ffffff !important;
    box-shadow: 0 8px 32px rgba(0,176,155,0.4) !important;
}
.rejected-banner {
    background: linear-gradient(135deg, #f5515f, #9f041b) !important;
    padding: 24px !important; border-radius: 16px !important;
    text-align: center !important; font-size: 1.8rem !important;
    font-weight: 700 !important; color: #ffffff !important;
    box-shadow: 0 8px 32px rgba(245,81,95,0.4) !important;
}

/* ── Section headers ── */
.section-header {
    font-size: 1.8rem !important; font-weight: 700 !important;
    background: linear-gradient(90deg, #7eb3ff, #c9b8ff) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    margin-bottom: 4px !important;
}
.section-sub {
    color: #bbbbbb !important;
    font-size: 0.95rem !important;
    margin-bottom: 28px !important;
}

/* ── Chat bubbles ── */
.chat-user {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    padding: 12px 18px !important; border-radius: 18px 18px 4px 18px !important;
    margin: 8px 0 !important; max-width: 75% !important;
    margin-left: auto !important; color: #ffffff !important;
    font-size: 0.95rem !important;
}
.chat-ai {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    padding: 12px 18px !important; border-radius: 18px 18px 18px 4px !important;
    margin: 8px 0 !important; max-width: 80% !important;
    color: #ffffff !important; font-size: 0.95rem !important;
}

/* ── Number input arrows ── */
[data-testid="stNumberInput"] button {
    background: rgba(255,255,255,0.1) !important;
    color: #ffffff !important;
    border: none !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] * { color: #7eb3ff !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0f0c29; }
::-webkit-scrollbar-thumb { background: #764ba2; border-radius: 3px; }

</style>
""", unsafe_allow_html=True)

# ── SINGLE import block — no duplicates ───────────────────────
from page_modules import (
    home_page,
    predict_page,
    dashboard_page,
    visualization_page,
    chatbot_page,
    bank_recommender_page,
    finance_news_page,
)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:

    st.markdown(" ## 🏦 Loan Approval Prediction System ")
    st.markdown("---")

    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"

    if st.button("🏠  Home",                use_container_width=True): st.session_state.current_page = "home"
    if st.button("🔮  Predict Loan",        use_container_width=True): st.session_state.current_page = "predict"
    if st.button("📊  Dashboard",           use_container_width=True): st.session_state.current_page = "dashboard"
    if st.button("📈  Analytics",           use_container_width=True): st.session_state.current_page = "visualization"
    if st.button("🏦  Bank Recommender",    use_container_width=True): st.session_state.current_page = "bank"
    if st.button("📰  Finance News & Tips", use_container_width=True): st.session_state.current_page = "finance"
    if st.button("🤖  AI Chatbot",          use_container_width=True): st.session_state.current_page = "chatbot"

    st.markdown("---")
    st.markdown("<small style='color:#666'>Powered by ML + ChromaDB + MySQL</small>", unsafe_allow_html=True)

# ── Page routing ──────────────────────────────────────────────
page = st.session_state.current_page

if   page == "home":          home_page.render()
elif page == "predict":       predict_page.render()
elif page == "dashboard":     dashboard_page.render()
elif page == "visualization": visualization_page.render()
elif page == "bank":          bank_recommender_page.render()
elif page == "finance":       finance_news_page.render()
elif page == "chatbot":       chatbot_page.render()