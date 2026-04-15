"""
page_modules/finance_news_page.py — Finance News & Tips powered by Groq AI
"""
import os
import sys
import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


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
        st.error(f"Groq error: {e}")
        return None


def ask_groq(prompt: str) -> str:
    client = get_groq_client()
    if client is None:
        return "⚠️ Groq API key not set. Add GROQ_API_KEY to your .env file."
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional Indian financial advisor and banking expert. Give practical, accurate, helpful advice about loans, credit, banking and personal finance in India. Be concise and use simple language."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


def calculate_emi(principal, annual_rate, months):
    r = annual_rate / (12 * 100)
    if r == 0:
        return principal / months
    return principal * r * (1 + r)**months / ((1 + r)**months - 1)


def render():
    import plotly.graph_objects as go
    import plotly.express as px
    import pandas as pd

    st.markdown('<p class="section-header">📰 Finance News & Tips</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">AI-powered financial tips, EMI calculator, credit guide, and latest loan advice.</p>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📰 AI Finance Tips",
        "🧮 EMI Calculator",
        "📈 Credit Score Guide",
        "❓ Ask Finance AI",
    ])

    # ════════════════════════════════════════════════════════
    # TAB 1 — AI Finance Tips
    # ════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 📰 Today's AI-Generated Finance Tips")
        st.markdown("*Powered by Groq LLaMA — click any topic to get instant tips*")

        topics = [
            ("💳 Credit Score Tips",         "Give me 5 practical tips to improve credit score in India in 2024. Be specific and actionable."),
            ("🏠 Home Loan Guide",            "Explain the home loan process in India step by step. Include documents needed, eligibility, and tips to get best rates."),
            ("💰 Personal Loan Tips",         "What are the top 5 things to check before taking a personal loan in India? Include hidden charges to watch out for."),
            ("📉 How to Reduce Debt",         "Give a practical debt reduction plan for a middle-class Indian earning ₹40,000 per month with multiple loans."),
            ("🎓 Education Loan Guide",       "Explain education loans in India — eligibility, interest rates, moratorium period, tax benefits under 80E."),
            ("🚗 Car Loan vs Personal Loan",  "Compare car loan vs personal loan for buying a car in India. Which is better and when?"),
            ("🏦 Fixed Deposit vs Loan",      "When should someone use their fixed deposit instead of taking a loan? Explain with examples."),
            ("📊 Loan Insurance Guide",       "Should I take loan protection insurance in India? Explain the pros, cons, and whether it is worth it."),
        ]

        cols = st.columns(2)
        for i, (label, prompt) in enumerate(topics):
            with cols[i % 2]:
                if st.button(label, key=f"tip_{i}", use_container_width=True):
                    st.session_state[f"tip_result_{i}"] = None
                    with st.spinner(f"Getting tips on {label}..."):
                        result = ask_groq(prompt)
                    st.session_state[f"tip_result_{i}"] = result

                if st.session_state.get(f"tip_result_{i}"):
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.05);
                        border:1px solid rgba(126,179,255,0.3);
                        border-radius:12px; padding:16px; margin-top:8px;
                        color:#cccccc; font-size:0.88rem; line-height:1.6">
                        {st.session_state[f'tip_result_{i}'].replace(chr(10), '<br>')}
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 💡 Daily Finance Fact")
        if st.button("🎲 Generate Random Finance Fact", use_container_width=True):
            with st.spinner("Generating fact..."):
                fact = ask_groq("Give me one surprising and useful financial fact about banking or loans in India. Keep it to 2-3 sentences.")
            st.info(f"💡 {fact}")

    # ════════════════════════════════════════════════════════
    # TAB 2 — EMI Calculator
    # ════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 🧮 EMI Calculator")
        st.markdown("*Calculate your Equated Monthly Installment instantly*")

        c1, c2, c3 = st.columns(3)
        with c1:
            principal = st.number_input("Loan Amount (₹)", min_value=1000, max_value=10000000, value=500000, step=10000)
        with c2:
            annual_rate = st.slider("Annual Interest Rate (%)", min_value=1.0, max_value=36.0, value=11.0, step=0.5)
        with c3:
            tenure_years = st.selectbox("Loan Tenure", [1, 2, 3, 4, 5, 7, 10, 15, 20, 30], index=4)

        tenure_months  = tenure_years * 12
        emi            = calculate_emi(principal, annual_rate, tenure_months)
        total_payment  = emi * tenure_months
        total_interest = total_payment - principal

        st.markdown("<br>", unsafe_allow_html=True)
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Monthly EMI",    f"₹{emi:,.0f}")
        r2.metric("Total Payment",  f"₹{total_payment:,.0f}")
        r3.metric("Total Interest", f"₹{total_interest:,.0f}")
        r4.metric("Interest %",     f"{(total_interest/principal*100):.1f}%")

        col_l, col_r = st.columns(2)

        with col_l:
            fig = go.Figure(go.Pie(
                labels=["Principal", "Total Interest"],
                values=[principal, total_interest],
                hole=0.55,
                marker_colors=["#7eb3ff", "#f5515f"],
                textfont_color="white",
                textinfo="label+percent",
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white", height=300,
                title=dict(text="Payment Breakdown", font=dict(color="white")),
                annotations=[dict(
                    text=f"₹{emi:,.0f}<br>/month",
                    x=0.5, y=0.5, font_size=14,
                    font_color="white", showarrow=False
                )]
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.markdown("### 🔄 Compare EMI Across Different Tenures")
        tenures    = [1, 2, 3, 5, 7, 10, 15, 20]
        emis       = [calculate_emi(principal, annual_rate, t * 12) for t in tenures]

        fig2 = px.line(
            x=[f"{t}yr" for t in tenures],
            y=emis,
            markers=True,
            labels={"x": "Tenure", "y": "Monthly EMI (₹)"},
            title=f"Monthly EMI vs Tenure for ₹{principal:,} at {annual_rate}%",
        )
        fig2.update_traces(line_color="#7eb3ff", marker_color="#c9b8ff")
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white", height=300,
            xaxis=dict(gridcolor="rgba(255,255,255,0.07)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.07)"),
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        if st.button("🤖 Get AI Advice on This Loan", use_container_width=True):
            prompt = f"""
            Someone is taking a loan with these details:
            - Loan Amount: ₹{principal:,}
            - Interest Rate: {annual_rate}%
            - Tenure: {tenure_years} years
            - Monthly EMI: ₹{emi:,.0f}
            - Total Interest: ₹{total_interest:,.0f}
            Is this a good deal? What should they watch out for?
            Give practical advice in 4-5 bullet points.
            """
            with st.spinner("Getting AI advice..."):
                advice = ask_groq(prompt)
            st.markdown(f"""
            <div style="background:rgba(126,179,255,0.08);
                border:1px solid rgba(126,179,255,0.3);
                border-radius:12px; padding:16px; color:#cccccc; font-size:0.9rem">
                🤖 <strong style="color:#7eb3ff">AI Advice:</strong><br><br>
                {advice.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # TAB 3 — Credit Score Guide
    # ════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 📈 Credit Score Complete Guide")

        bands = [
            ("🔴 300–549", "Poor",      "#f5515f", "Loan rejection very likely. Need significant improvement before applying."),
            ("🟠 550–649", "Fair",       "#ff7043", "Limited options. Only NBFCs may approve, at very high interest."),
            ("🟡 650–699", "Average",    "#f7b733", "Some private banks may approve. Higher interest rates expected."),
            ("🔵 700–749", "Good",       "#7eb3ff", "Most banks will consider. Reasonable interest rates available."),
            ("🟢 750–799", "Very Good",  "#00b09b", "Strong profile. Good rates from most major banks."),
            ("⭐ 800–900", "Excellent",  "#00e676", "Best rates, instant approvals, pre-approved offers from all banks."),
        ]

        for band, label, color, desc in bands:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:16px;
                background:rgba(255,255,255,0.04);
                border-left:4px solid {color};
                border-radius:8px; padding:14px; margin-bottom:8px">
                <div style="min-width:120px">
                    <strong style="color:{color}">{band}</strong><br>
                    <span style="color:{color}; font-size:0.9rem">{label}</span>
                </div>
                <div style="color:#cccccc; font-size:0.88rem">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🎯 Credit Score Simulator")
        st.markdown("*Check how your actions affect your credit score*")

        your_score = st.slider("Your Current Credit Score", 300, 900, 650)
        st.markdown("**Select actions you will take:**")

        a1 = st.checkbox("✅ Pay all bills on time for 6 months (+40 to +60 points)")
        a2 = st.checkbox("✅ Reduce credit card usage below 30% (+20 to +30 points)")
        a3 = st.checkbox("✅ Close all overdue accounts (+30 to +50 points)")
        a4 = st.checkbox("✅ Do not apply for new loans for 6 months (+10 to +20 points)")
        a5 = st.checkbox("✅ Dispute and fix credit report errors (+20 to +40 points)")
        a6 = st.checkbox("❌ Apply for multiple loans at once (-20 to -30 points)")
        a7 = st.checkbox("❌ Miss an EMI payment (-40 to -60 points)")

        improvement = 0
        if a1: improvement += 50
        if a2: improvement += 25
        if a3: improvement += 40
        if a4: improvement += 15
        if a5: improvement += 30
        if a6: improvement -= 25
        if a7: improvement -= 50

        projected   = max(300, min(900, your_score + improvement))
        delta_color = "normal" if improvement >= 0 else "inverse"

        st.markdown("<br>", unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Current Score",   your_score)
        sc2.metric("Projected Score", projected, delta=f"{improvement:+d} points", delta_color=delta_color)
        sc3.metric("Change",          f"{improvement:+d} pts", delta="Improving" if improvement >= 0 else "Declining", delta_color=delta_color)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🤖 Get Personalized Credit Improvement Plan", use_container_width=True):
            prompt = f"My credit score is {your_score}. Give me a detailed 90-day action plan to improve it. Be specific with weekly tasks."
            with st.spinner("Creating your plan..."):
                plan = ask_groq(prompt)
            st.markdown(f"""
            <div style="background:rgba(0,176,155,0.08);
                border:1px solid rgba(0,176,155,0.3);
                border-radius:12px; padding:16px;
                color:#cccccc; font-size:0.88rem; line-height:1.6">
                🤖 <strong style="color:#00b09b">Your 90-Day Credit Improvement Plan:</strong><br><br>
                {plan.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # TAB 4 — Ask Finance AI  ← FIXED
    # ════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### ❓ Ask Anything About Finance")
        st.markdown("*Your personal AI financial advisor — ask any question*")

        # Initialise session state keys on first load
        if "finance_ai_question" not in st.session_state:
            st.session_state.finance_ai_question = ""
        if "finance_ai_answer" not in st.session_state:
            st.session_state.finance_ai_answer = ""

        quick = [
            "How do I get a loan with low CIBIL score?",
            "What documents do I need for a personal loan?",
            "How to check my credit score for free in India?",
            "What is the difference between secured and unsecured loans?",
            "How does loan foreclosure work in India?",
            "What happens if I default on a loan in India?",
        ]

        st.markdown("**Quick Questions:**")
        qc = st.columns(3)
        for i, q in enumerate(quick):
            with qc[i % 3]:
                # KEY FIX: clicking a quick-question button sets the question
                # into session state AND immediately fetches the answer.
                if st.button(q, key=f"fq_{i}", use_container_width=True):
                    st.session_state.finance_ai_question = q
                    st.session_state.finance_ai_answer = ""        # clear old answer
                    with st.spinner("Thinking..."):
                        st.session_state.finance_ai_answer = ask_groq(q)

        st.markdown("---")

        # Text area is driven by session state (no `key=` so we manage it manually).
        # We write the current question into it via `value=`.
        question = st.text_area(
            "Type your finance question here:",
            value=st.session_state.finance_ai_question,   # ← always reflects state
            placeholder="e.g. I earn ₹35,000/month. Can I get a ₹5 lakh personal loan?",
            height=100,
        )

        if st.button("💬 Get AI Answer", use_container_width=True):
            if question.strip():
                # Sync whatever the user typed back into state
                st.session_state.finance_ai_question = question
                st.session_state.finance_ai_answer = ""
                with st.spinner("Thinking..."):
                    st.session_state.finance_ai_answer = ask_groq(question)
            else:
                st.warning("Please type a question first!")

        # Display the answer (persists across reruns)
        if st.session_state.finance_ai_answer:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05);
                border:1px solid rgba(201,184,255,0.3);
                border-radius:12px; padding:20px; margin-top:16px;
                color:#cccccc; font-size:0.9rem; line-height:1.7">
                🤖 <strong style="color:#c9b8ff">AI Answer:</strong><br><br>
                {st.session_state.finance_ai_answer.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)