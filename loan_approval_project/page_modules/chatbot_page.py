"""page_modules/chatbot_page.py — AI Chatbot powered by Groq LLaMA + ChromaDB
"""
import os
import sys
import streamlit as st
from dotenv import load_dotenv

# Load .env from project root
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path, override=True)

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.chroma_kb import build_knowledge_base, query_knowledge
from utils.db import save_chat_message, db_connected

# ── SYSTEM PROMPT — defined FIRST before any function ─────────
SYSTEM_PROMPT = """You are LoanAI Assistant, a friendly and professional AI expert built into the LoanAI application.

This app has the following pages you can explain:
1. 🏠 Home — Overview of the app and dataset stats
2. 🔮 Predict Loan — ML-powered loan approval prediction form with risk gauge, bank recommendations column and improvement plan column
3. 📊 Dashboard — Model performance metrics, accuracy, AUC-ROC, feature importance charts
4. 📈 Visualizations — 20+ interactive EDA charts about the credit risk dataset
5. 🤖 AI Chatbot — That is you! Powered by Groq LLaMA + ChromaDB
6. 📋 Application History — All predictions stored in MySQL database with filters
7. 🏦 Bank Recommender — Full dedicated page to check which Indian banks (SBI, HDFC, ICICI, Axis, Kotak, Bajaj, Tata, Muthoot, Manappuram) will approve the loan, with EMI estimates, interest rates, processing fees, and a side-by-side comparison table
8. 📰 Finance News & Tips — 4 tabs: AI Finance Tips (click topics to get Groq-powered tips), EMI Calculator (with amortization schedule and tenure comparison), Credit Score Guide (score bands + simulator), Ask Finance AI (open question answering)

You help users understand:
- How to use each page of this app
- Loan approval factors and how the ML model decides
- Which banks to approach based on their profile
- How to use the EMI calculator and what the results mean
- How to interpret their credit score and improve it
- How to read the bank recommender results
- Credit scores, interest rates, and loan types in India
- How to improve loan approval chances step by step
- General Indian banking and finance advice

Always be friendly, simple, and practical. Use Indian context (₹, Indian banks, RBI rules).
"""


# ── Groq client ───────────────────────────────────────────────
def get_groq_client():
    try:
        from groq import Groq
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        load_dotenv(dotenv_path=env_path, override=True)
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            return None
        return Groq(api_key=api_key)
    except Exception as e:
        return None


# ── Main chat function ────────────────────────────────────────
def chat_with_ai(messages: list, user_message: str) -> str:
    client = get_groq_client()

    if client is None:
        return "⚠️ Groq API key not set. Please add GROQ_API_KEY to your .env file."

    # Get relevant knowledge from ChromaDB
    context = query_knowledge(user_message, n_results=3)

    full_system = SYSTEM_PROMPT
    if context:
        full_system += f"\n\n--- RELEVANT KNOWLEDGE BASE ---\n{context}\n---"

    # Build message history
    api_messages = [{"role": "system", "content": full_system}]
    for msg in messages[-10:]:
        api_messages.append({"role": msg["role"], "content": msg["content"]})
    api_messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=api_messages,
            max_tokens=600,
            temperature=0.7,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ Groq API error: {str(e)}\n\nPlease check your GROQ_API_KEY in the .env file."


# ── Main render function ──────────────────────────────────────
def render():
    st.markdown('<p class="section-header">🤖 AI Chatbot</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Ask me anything about loans, credit scores, finance, or this app!</p>', unsafe_allow_html=True)

    # ── Build ChromaDB knowledge base on first load ───────────
    if "chroma_ready" not in st.session_state:
        with st.spinner("Loading AI knowledge base..."):
            try:
                build_knowledge_base()
                st.session_state.chroma_ready = True
            except Exception as e:
                st.session_state.chroma_ready = False
                st.warning(f"ChromaDB warning: {e}")

    # ── Check Groq key ────────────────────────────────────────
    client = get_groq_client()

    if client is None:
        st.warning("""
        ⚠️ **Groq API key not configured.**

        To enable the AI chatbot:
        1. Go to [console.groq.com](https://console.groq.com) 
        2. Sign up and click **API Keys** → **Create API Key**
        3. Open your `.env` file
        4. Add this line:  `GROQ_API_KEY=uryo_actual_key_here`
        5. Restart the app

        **For now, use the Demo Mode below ↓**
        """)
        _demo_chatbot()
        return

    # ── Initialize chat history ───────────────────────────────
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": (
                "👋 Hi! I'm **LoanAI Assistant**, your personal finance AI.\n\n"
                "I can help you with:\n"
                "- 📋 Understanding loan approval factors\n"
                "- 💳 Credit score tips\n"
                "- 📊 How this app's ML model works\n"
                "- 💰 General financial advice\n\n"
                "What would you like to know?"
            )
        })

    # ── Quick question buttons ────────────────────────────────
    st.markdown("**💡 Quick Questions:**")
    q_cols = st.columns(3)
    quick_qs = [
        "How can I improve my loan approval chances?",
        "What is a credit score?",
        "Why was my loan rejected?",
        "What does loan grade mean?",
        "How does this ML model work?",
        "What is debt-to-income ratio?",
    ]
    for i, q in enumerate(quick_qs):
        with q_cols[i % 3]:
            if st.button(q, key=f"quick_{i}", use_container_width=True):
                st.session_state._quick_question = q

    st.markdown("---")

    # ── Display chat history ──────────────────────────────────
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-user">
                <strong>You</strong><br>{msg["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-ai">
                <strong>🤖 LoanAI</strong><br>{msg["content"]}
            </div>
            """, unsafe_allow_html=True)

    # ── Input area ────────────────────────────────────────────
    col_input, col_send, col_clear = st.columns([5, 1, 1])

    with col_input:
        user_input = st.text_input(
            "message",
            key="chat_input",
            placeholder="e.g. How do I improve my credit score?",
            label_visibility="collapsed"
        )
    with col_send:
        send_clicked = st.button("Send 🚀", use_container_width=True)
    with col_clear:
        if st.button("Clear 🗑️", use_container_width=True):
            st.session_state.chat_messages = []
            if "chroma_ready" in st.session_state:
                del st.session_state.chroma_ready
            st.rerun()

    # ── Handle quick question ─────────────────────────────────
    if hasattr(st.session_state, "_quick_question"):
        user_input   = st.session_state._quick_question
        send_clicked = True
        del st.session_state._quick_question

    # ── Process and respond ───────────────────────────────────
    if send_clicked and user_input and user_input.strip():
        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_input
        })

        with st.spinner("Thinking..."):
            response = chat_with_ai(
                st.session_state.chat_messages[:-1],
                user_input
            )

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response
        })

        if db_connected():
            save_chat_message("user", user_input)
            save_chat_message("assistant", response)

        st.rerun()


# ── Demo mode when no API key ─────────────────────────────────
def _demo_chatbot():
    st.markdown("### 🤖 Demo Mode (No API Key Required)")

    DEMO_QA = {
        "credit score":  "A credit score (300–850) measures your creditworthiness. Above 750 = excellent. Lenders use it to decide loan approval and interest rates.",
        "loan rejected": "Common reasons: low credit score, high debt, unstable employment, insufficient income, or too large a loan amount.",
        "improve":       "Tips: Pay off debt, fix credit report errors, get a co-signer, apply for a smaller amount, maintain stable employment.",
        "interest rate": "Interest rate is the cost of borrowing money. Personal loans: 6–36%. Mortgages: 3–7%. Higher credit score = lower rate.",
        "loan grade":    "Grades A–G represent risk. Grade A = safest, lowest interest. Grade G = riskiest, highest interest.",
        "dti":           "Debt-to-Income ratio = monthly debt / monthly income. Lenders prefer under 36%.",
        "default":       "A default happens when you stop making loan payments. It damages your credit score for 7 years.",
        "ml model":      "This app uses XGBoost, Random Forest, and Gradient Boosting trained on 32,000+ real credit records.",
    }

    if "demo_messages" not in st.session_state:
        st.session_state.demo_messages = [{
            "role": "assistant",
            "content": "👋 Hi! I'm in demo mode. Ask me about credit scores, loan grades, or interest rates!"
        }]

    for msg in st.session_state.demo_messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user"><strong>You</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-ai"><strong>🤖 LoanAI Demo</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)

    user_q = st.text_input("Ask a question:", key="demo_input",
                            placeholder="e.g. What is a credit score?")

    if st.button("Ask", key="demo_send"):
        if user_q:
            st.session_state.demo_messages.append({"role": "user",      "content": user_q})
            q_lower = user_q.lower()
            answer  = "I'm in demo mode with limited responses. Set your Groq API key for full AI answers!"
            for keyword, response in DEMO_QA.items():
                if keyword in q_lower:
                    answer = response
                    break
            st.session_state.demo_messages.append({"role": "assistant", "content": answer})
            st.rerun()