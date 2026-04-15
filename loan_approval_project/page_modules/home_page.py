import os
import sys
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


def render():

    # ── Hero ──────────────────────────────────────────────────
    st.markdown(
        "<div style='text-align:center; padding:40px 0 10px 0;'>"
        "<span style='background:rgba(126,179,255,0.12); "
        "border:1px solid rgba(126,179,255,0.35); "
        "border-radius:30px; padding:6px 20px; "
        "font-size:0.82rem; color:#7eb3ff; "
        "font-weight:600; letter-spacing:0.08em;'>"
        " 🏦 LOAN APPROVAL PREDICTION SYSTEM "
        "</span></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<h1 style='text-align:center; font-size:3rem; "
        "font-weight:900; color:#ffffff; "
        "margin:20px 0 10px 0;'>"
        "Smarter Lending Decisions, Instantly."
        "</h1>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<p style='text-align:center; font-size:1.1rem; "
        "color:#aaaaaa; max-width:560px; "
        "margin:0 auto 10px auto; line-height:1.7;'>"
        "Submit a loan application and receive an "
        "<strong style='color:#c9b8ff'>AI-powered credit decision</strong>"
        " in seconds."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<p style='text-align:center; font-size:0.92rem; "
        "color:#777777; max-width:520px; "
        "margin:0 auto 30px auto; line-height:1.6;'>"
        "Trained on <strong style='color:#7eb3ff'>32,000+</strong> "
        "real credit records across income levels, loan grades and "
        "risk profiles — so every decision is grounded in real data."
        "</p>",
        unsafe_allow_html=True,
    )

    # ── CTA buttons using Streamlit columns ───────────────────
    _, b1, b2, _ = st.columns([2, 1, 1, 2])
    with b1:
        if st.button("🔮 Predict a Loan", use_container_width=True):
            st.session_state.current_page = "predict"
            st.rerun()
    with b2:
        if st.button("📊 View Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Stats strip using Streamlit columns ───────────────────
    st.markdown(
        "<div style='background:rgba(255,255,255,0.04); "
        "border:1px solid rgba(255,255,255,0.09); "
        "border-radius:16px; padding:4px 0; "
        "margin-bottom:40px;'></div>",
        unsafe_allow_html=True,
    )

    stats = [
        ("32,581",  "Training Records",    "#7eb3ff"),
        ("94.2%",   "Model Accuracy",      "#00b09b"),
        ("3",       "ML Models Trained",   "#c9b8ff"),
        ("9",       "Indian Banks",        "#f7b733"),
        ("< 1s",    "Prediction Time",     "#ff9adb"),
    ]

    s1, s2, s3, s4, s5 = st.columns(5)
    scols = [s1, s2, s3, s4, s5]
    for i, (val, label, color) in enumerate(stats):
        with scols[i]:
            st.markdown(
                f"<div style='text-align:center; "
                f"background:rgba(255,255,255,0.04); "
                f"border:1px solid rgba(255,255,255,0.09); "
                f"border-radius:14px; padding:18px 8px;'>"
                f"<div style='font-size:1.7rem; font-weight:800; "
                f"color:{color};'>{val}</div>"
                f"<div style='font-size:0.78rem; color:#888; "
                f"margin-top:4px;'>{label}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Feature Cards ─────────────────────────────────────────
    st.markdown(
        "<h3 style='text-align:center; color:#ffffff; "
        "font-size:1.2rem; margin-bottom:6px;'>"
        "Everything You Need in One Place</h3>"
        "<p style='text-align:center; color:#777; "
        "font-size:0.88rem; margin-bottom:20px;'>"
        "Seven powerful modules working together</p>",
        unsafe_allow_html=True,
    )

    features = [
        ("🔮", "Loan Prediction",  "#7eb3ff",
         "Instant AI decision with risk score and confidence level."),
        ("🏦", "Bank Recommender", "#00b09b",
         "See which Indian banks approve you and at what rate."),
        ("💡", "Improvement Plan", "#c9b8ff",
         "Step-by-step plan to improve your approval chances."),
        ("🧮", "EMI Calculator",   "#f7b733",
         "Calculate monthly EMI and compare across tenures."),
        ("📈", "Analytics",        "#ff9adb",
         "20+ interactive charts from 32,000+ credit records."),
        ("🤖", "AI Chatbot",       "#7bffb8",
         "Ask anything — powered by Groq LLaMA and ChromaDB."),
        ("📊", "Live Dashboard",   "#ffb347",
         "Track all applications in real time with full stats."),
    ]

    c1, c2, c3, c4 = st.columns(4)
    fcols = [c1, c2, c3, c4]
    for i, (icon, title, color, desc) in enumerate(features):
        with fcols[i % 4]:
            st.markdown(
                f"<div style='background:rgba(255,255,255,0.05); "
                f"border:1px solid rgba(255,255,255,0.1); "
                f"border-top:3px solid {color}; "
                f"border-radius:14px; padding:20px 16px; "
                f"margin-bottom:14px; min-height:155px;'>"
                f"<div style='font-size:1.7rem; "
                f"margin-bottom:10px;'>{icon}</div>"
                f"<div style='font-size:0.92rem; font-weight:700; "
                f"color:{color}; margin-bottom:7px;'>{title}</div>"
                f"<div style='font-size:0.8rem; color:#aaa; "
                f"line-height:1.5;'>{desc}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── How It Works ──────────────────────────────────────────
    st.markdown(
        "<h3 style='text-align:center; color:#ffffff; "
        "font-size:1.2rem; margin-bottom:6px;'>"
        "How It Works</h3>"
        "<p style='text-align:center; color:#777; "
        "font-size:0.88rem; margin-bottom:20px;'>"
        "From application to decision in 5 simple steps</p>",
        unsafe_allow_html=True,
    )

    steps = [
        ("1", "#7eb3ff", "Fill the Form",
         "Enter age, income, loan amount, employment and credit details."),
        ("2", "#c9b8ff", "AI Analyses",
         "XGBoost processes 11 features against 32,000+ records instantly."),
        ("3", "#00b09b", "Get Decision",
         "Approved or Rejected with a risk score and confidence level."),
        ("4", "#f7b733", "See Bank Options",
         "Which Indian banks approve you with rates and EMI estimates."),
        ("5", "#ff9adb", "Follow the Plan",
         "Get a personalized improvement plan with a clear timeline."),
    ]

    st1, st2, st3, st4, st5 = st.columns(5)
    step_cols = [st1, st2, st3, st4, st5]
    for i, (num, color, title, desc) in enumerate(steps):
        with step_cols[i]:
            st.markdown(
                f"<div style='text-align:center; padding:14px 6px;'>"
                f"<div style='width:42px; height:42px; "
                f"border:2px solid {color}; border-radius:50%; "
                f"display:flex; align-items:center; "
                f"justify-content:center; margin:0 auto 10px auto; "
                f"font-size:1.05rem; font-weight:800; color:{color};'>"
                f"{num}</div>"
                f"<div style='font-size:0.88rem; font-weight:700; "
                f"color:#ffffff; margin-bottom:5px;'>{title}</div>"
                f"<div style='font-size:0.78rem; color:#888; "
                f"line-height:1.5;'>{desc}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)



    # ── Footer ────────────────────────────────────────────────
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center; padding:20px; "
        "border-top:1px solid rgba(255,255,255,0.08); "
        "color:#555; font-size:0.8rem;'>"
        "© 2026 LoanAI. Empowering smarter financial decisions. <br> "
        "Privacy Policy | Terms of Service | Support"
        "</div>",
        unsafe_allow_html=True,
    )