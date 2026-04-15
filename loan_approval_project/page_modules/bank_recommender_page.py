"""
page_modules/bank_recommender_page.py — Full Bank Recommender Page
"""
import os
import sys
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

BANKS = {
    "SBI (State Bank of India)": {
        "logo": "🏛️", "type": "Public Sector",
        "max_risk": 35, "min_grade": ["A", "B", "C"],
        "rate_min": 8.5, "rate_max": 12.0,
        "max_loan": 2000000, "min_income": 25000,
        "processing_fee": "0.5%", "tenure": "1–7 years",
        "turnaround": "5–7 working days",
        "best_for": "Salaried government employees",
        "features": ["Zero prepayment charges", "Lowest interest rates", "Wide branch network"],
        "apply_link": "https://www.sbi.co.in/web/personal-banking/loans",
        "color": "#1a237e",
    },
    "HDFC Bank": {
        "logo": "🔵", "type": "Private Sector",
        "max_risk": 38, "min_grade": ["A", "B", "C"],
        "rate_min": 9.0, "rate_max": 14.0,
        "max_loan": 4000000, "min_income": 30000,
        "processing_fee": "1%", "tenure": "1–5 years",
        "turnaround": "2–3 working days",
        "best_for": "Salaried professionals",
        "features": ["Instant online approval", "Flexible repayment", "No collateral needed"],
        "apply_link": "https://www.hdfcbank.com/personal/loans",
        "color": "#1565c0",
    },
    "ICICI Bank": {
        "logo": "🟠", "type": "Private Sector",
        "max_risk": 42, "min_grade": ["A", "B", "C", "D"],
        "rate_min": 9.5, "rate_max": 15.0,
        "max_loan": 3000000, "min_income": 28000,
        "processing_fee": "1–2%", "tenure": "1–6 years",
        "turnaround": "2–4 working days",
        "best_for": "Self-employed and salaried",
        "features": ["iMobile app approval", "Pre-approved offers", "Doorstep service"],
        "apply_link": "https://www.icicibank.com/personal-banking/loans",
        "color": "#e65100",
    },
    "Axis Bank": {
        "logo": "🟣", "type": "Private Sector",
        "max_risk": 45, "min_grade": ["A", "B", "C", "D"],
        "rate_min": 10.0, "rate_max": 15.5,
        "max_loan": 2500000, "min_income": 25000,
        "processing_fee": "1.5–2%", "tenure": "1–5 years",
        "turnaround": "2–3 working days",
        "best_for": "Flexible repayment seekers",
        "features": ["Flexible EMI options", "Online account management", "Quick disbursal"],
        "apply_link": "https://www.axisbank.com/retail/loans",
        "color": "#6a1b9a",
    },
    "Kotak Mahindra Bank": {
        "logo": "🔴", "type": "Private Sector",
        "max_risk": 50, "min_grade": ["A", "B", "C", "D", "E"],
        "rate_min": 10.5, "rate_max": 17.0,
        "max_loan": 2000000, "min_income": 20000,
        "processing_fee": "1–2.5%", "tenure": "1–5 years",
        "turnaround": "3–4 working days",
        "best_for": "Medium risk profiles",
        "features": ["Instant digital loans", "No hidden charges", "24/7 support"],
        "apply_link": "https://www.kotak.com/en/personal-banking/loans.html",
        "color": "#b71c1c",
    },
    "Bajaj Finserv": {
        "logo": "🟡", "type": "NBFC",
        "max_risk": 58, "min_grade": ["B", "C", "D", "E", "F"],
        "rate_min": 12.0, "rate_max": 22.0,
        "max_loan": 1500000, "min_income": 18000,
        "processing_fee": "2–3%", "tenure": "1–5 years",
        "turnaround": "24 hours",
        "best_for": "Quick disbursal needs",
        "features": ["24hr disbursal", "Minimal documents", "Flexi loan option"],
        "apply_link": "https://www.bajajfinserv.in/personal-loan",
        "color": "#f57f17",
    },
    "Tata Capital": {
        "logo": "🔷", "type": "NBFC",
        "max_risk": 62, "min_grade": ["C", "D", "E", "F"],
        "rate_min": 13.0, "rate_max": 24.0,
        "max_loan": 1000000, "min_income": 15000,
        "processing_fee": "2–3.5%", "tenure": "1–6 years",
        "turnaround": "2–3 working days",
        "best_for": "Borderline credit profiles",
        "features": ["Wide eligibility", "Flexible tenure", "Online application"],
        "apply_link": "https://www.tatacapital.com/personal-loan.html",
        "color": "#0277bd",
    },
    "Muthoot Finance": {
        "logo": "🟤", "type": "NBFC",
        "max_risk": 75, "min_grade": ["D", "E", "F", "G"],
        "rate_min": 16.0, "rate_max": 28.0,
        "max_loan": 500000, "min_income": 12000,
        "processing_fee": "2–4%", "tenure": "1–3 years",
        "turnaround": "Same day",
        "best_for": "High risk, gold loan option",
        "features": ["Gold loan available", "Same day approval", "Minimal credit check"],
        "apply_link": "https://www.muthootfinance.com/loan-against-gold",
        "color": "#4e342e",
    },
    "Manappuram Finance": {
        "logo": "⚫", "type": "NBFC",
        "max_risk": 85, "min_grade": ["E", "F", "G"],
        "rate_min": 18.0, "rate_max": 30.0,
        "max_loan": 300000, "min_income": 10000,
        "processing_fee": "2–4%", "tenure": "3 months – 3 years",
        "turnaround": "Same day",
        "best_for": "Emergency/last resort option",
        "features": ["No credit score needed", "Gold as collateral", "Instant cash"],
        "apply_link": "https://www.manappuram.com/gold-loan.html",
        "color": "#212121",
    },
}


def calculate_emi(principal, rate_annual, tenure_months):
    r = rate_annual / (12 * 100)
    if r == 0:
        return principal / tenure_months
    emi = principal * r * (1 + r)**tenure_months / ((1 + r)**tenure_months - 1)
    return emi


def get_recommendations(risk_pct, loan_amnt, person_income, loan_grade, has_default):
    approved, rejected = [], []
    for name, info in BANKS.items():
        reasons = []
        ok = True
        if risk_pct > info["max_risk"]:
            ok = False
            reasons.append(f"Risk too high ({risk_pct:.0f}% > {info['max_risk']}% max)")
        if loan_grade not in info["min_grade"]:
            ok = False
            reasons.append(f"Grade {loan_grade} not accepted")
        if loan_amnt > info["max_loan"]:
            ok = False
            reasons.append(f"Amount ₹{loan_amnt:,} exceeds limit ₹{info['max_loan']:,}")
        if person_income < info["min_income"]:
            ok = False
            reasons.append(f"Income ₹{person_income:,} below minimum ₹{info['min_income']:,}")
        if has_default == "Y" and info["max_risk"] < 50:
            ok = False
            reasons.append("Prior default disqualifies from this bank")
        entry = {**info, "name": name, "reasons": reasons}
        if ok:
            approved.append(entry)
        else:
            rejected.append(entry)
    return approved, rejected


def render():
    st.markdown('<p class="section-header">🏦 Bank Loan Recommender</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Enter your profile and instantly see which Indian banks will approve your loan.</p>', unsafe_allow_html=True)

    # ── Input Form ────────────────────────────────────────────
    with st.form("bank_form"):
        st.markdown("#### 👤 Your Profile")
        c1, c2, c3 = st.columns(3)
        with c1:
            loan_amnt   = st.number_input("Loan Amount (₹)", min_value=10000, max_value=5000000, value=200000, step=10000)
        with c2:
            person_income = st.number_input("Monthly Income (₹)", min_value=5000, max_value=1000000, value=40000, step=1000)
        with c3:
            loan_grade  = st.selectbox("Your Loan Grade", ["A","B","C","D","E","F","G"], help="A=Best, G=Riskiest")

        c4, c5, c6 = st.columns(3)
        with c4:
            risk_score  = st.slider("Your Risk Score (%)", 0, 100, 30, help="From the Predict Loan page")
        with c5:
            has_default = st.selectbox("Prior Default on Record?", ["N", "Y"])
        with c6:
            tenure_yr   = st.selectbox("Preferred Tenure", [1, 2, 3, 4, 5, 6, 7], index=2)

        submitted = st.form_submit_button("🔍 Find Best Banks For Me", use_container_width=True)

    if submitted:
        approved, rejected = get_recommendations(
            risk_score, loan_amnt, person_income, loan_grade, has_default
        )
        tenure_months = tenure_yr * 12

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Summary metrics ───────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Banks Approving",  f"{len(approved)}")
        c2.metric("Banks Rejecting",  f"{len(rejected)}")
        c3.metric("Loan Amount",      f"₹{loan_amnt:,}")
        c4.metric("Your Risk Score",  f"{risk_score}%")

        # ── Approval donut chart ──────────────────────────────
        if approved or rejected:
            fig = go.Figure(go.Pie(
                labels=["Will Approve", "Will Reject"],
                values=[len(approved), len(rejected)],
                hole=0.6,
                marker_colors=["#00b09b", "#f5515f"],
                textinfo="label+percent",
                textfont_color="white",
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=250,
                showlegend=False,
                annotations=[dict(
                    text=f"{len(approved)}/{len(approved)+len(rejected)}",
                    x=0.5, y=0.5, font_size=22,
                    font_color="white", showarrow=False
                )]
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # ── Approved Banks ────────────────────────────────────
        if approved:
            st.markdown(f"### ✅ Banks Likely to Approve You ({len(approved)})")

            for bank in approved:
                emi = calculate_emi(loan_amnt, bank["rate_min"], tenure_months)
                emi_max = calculate_emi(loan_amnt, bank["rate_max"], tenure_months)

                with st.expander(f"{bank['logo']} {bank['name']}  |  {bank['rate_min']}%–{bank['rate_max']}% p.a.  |  EMI: ₹{emi:,.0f}–₹{emi_max:,.0f}", expanded=True):
                    col_l, col_r = st.columns([2, 1])

                    with col_l:
                        st.markdown(f"""
                        <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px">
                            <span style="background:rgba(0,176,155,0.2); color:#00e676;
                                padding:4px 12px; border-radius:20px; font-size:0.82rem;
                                font-weight:600">✅ ELIGIBLE</span>
                            <span style="background:rgba(255,255,255,0.1); color:#ccc;
                                padding:4px 12px; border-radius:20px; font-size:0.82rem">
                                🏢 {bank['type']}</span>
                            <span style="background:rgba(255,255,255,0.1); color:#ccc;
                                padding:4px 12px; border-radius:20px; font-size:0.82rem">
                                ⏱️ {bank['turnaround']}</span>
                        </div>

                        <div style="color:#cccccc; font-size:0.88rem; margin-bottom:10px">
                            <strong style="color:#7eb3ff">Best For:</strong> {bank['best_for']}
                        </div>

                        <div style="margin-bottom:10px">
                            {"".join([f'<span style="background:rgba(126,179,255,0.1); color:#aaa; padding:3px 10px; border-radius:6px; font-size:0.8rem; margin-right:6px; margin-bottom:4px; display:inline-block">✓ {f}</span>' for f in bank["features"]])}
                        </div>
                        """, unsafe_allow_html=True)

                        # EMI breakdown
                        st.markdown(f"""
                        <div style="background:rgba(255,255,255,0.05); border-radius:10px; padding:12px; margin-bottom:10px">
                            <strong style="color:#ffffff">💰 EMI Estimate for ₹{loan_amnt:,} over {tenure_yr} years:</strong>
                            <div style="display:flex; gap:20px; margin-top:8px; flex-wrap:wrap">
                                <div>
                                    <div style="color:#aaa; font-size:0.8rem">Best Rate ({bank['rate_min']}%)</div>
                                    <div style="color:#00e676; font-size:1.1rem; font-weight:700">₹{emi:,.0f}/month</div>
                                    <div style="color:#aaa; font-size:0.78rem">Total: ₹{emi*tenure_months:,.0f}</div>
                                </div>
                                <div>
                                    <div style="color:#aaa; font-size:0.8rem">Max Rate ({bank['rate_max']}%)</div>
                                    <div style="color:#f7b733; font-size:1.1rem; font-weight:700">₹{emi_max:,.0f}/month</div>
                                    <div style="color:#aaa; font-size:0.78rem">Total: ₹{emi_max*tenure_months:,.0f}</div>
                                </div>
                                <div>
                                    <div style="color:#aaa; font-size:0.8rem">Processing Fee</div>
                                    <div style="color:#c9b8ff; font-size:1.1rem; font-weight:700">{bank['processing_fee']}</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col_r:
                        # Rate gauge
                        avg_rate = (bank["rate_min"] + bank["rate_max"]) / 2
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=avg_rate,
                            title={"text": "Avg Rate %", "font": {"color": "white", "size": 12}},
                            gauge={
                                "axis": {"range": [0, 35], "tickcolor": "white"},
                                "bar": {"color": "#667eea"},
                                "steps": [
                                    {"range": [0, 12],  "color": "#00b09b"},
                                    {"range": [12, 20], "color": "#f7b733"},
                                    {"range": [20, 35], "color": "#f5515f"},
                                ],
                            },
                            number={"suffix": "%", "font": {"color": "white", "size": 24}},
                        ))
                        fig.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            font_color="white", height=180, margin=dict(t=30, b=0, l=10, r=10)
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        st.link_button(
                            f"Apply at {bank['name'].split(' ')[0]} →",
                            bank["apply_link"],
                            use_container_width=True
                        )
        else:
            st.error("❌ No banks are likely to approve at your current profile. Follow the Improvement Plan on the Predict page.")

        # ── Rejected Banks ────────────────────────────────────
        if rejected:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander(f"❌ Banks Likely to Reject ({len(rejected)}) — Click to see why"):
                for bank in rejected:
                    st.markdown(f"""
                    <div style="background:rgba(245,81,95,0.07);
                        border:1px solid rgba(245,81,95,0.2);
                        border-radius:10px; padding:12px; margin-bottom:8px">
                        <strong style="color:#ffffff">{bank['logo']} {bank['name']}</strong>
                        <span style="color:#888; font-size:0.8rem; margin-left:8px">{bank['type']}</span>
                        <div style="margin-top:6px">
                        {"".join([f'<div style="color:#ff9999;font-size:0.82rem">• {r}</div>' for r in bank["reasons"]])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)



