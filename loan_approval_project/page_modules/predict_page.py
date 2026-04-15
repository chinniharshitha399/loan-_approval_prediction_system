"""
page_modules/predict_page.py — Loan Prediction Form
"""
import streamlit as st
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.model import load_model, predict
from utils.db import save_application, db_connected


def render():
    st.markdown('<p class="section-header">🔮 Loan Approval Prediction</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Fill in the applicant details and get an instant AI-powered decision.</p>', unsafe_allow_html=True)

    # ── Load model ────────────────────────────────────────────────────────
    artifacts = load_model()
    if artifacts is None:
        st.error("⚠️  No trained model found! Please run:  **python train_model.py**  first.")
        st.code("cd loan_approval_project\npython train_model.py")
        return



    # ── Form ──────────────────────────────────────────────────────────────
    with st.form("loan_form"):
        st.markdown("#### 👤 Personal Information")
        col1, col2, col3 = st.columns(3)

        with col1:
            person_age = st.number_input("Age", min_value=18, max_value=100, value=30,
                                         help="Applicant's age")
        with col2:
            person_income = st.number_input("Annual Income ($)", min_value=1000,
                                            max_value=10_000_000, value=55000, step=1000,
                                            help="Gross annual income")
        with col3:
            person_emp_length = st.number_input("Employment Length (years)",
                                                 min_value=0.0, max_value=60.0,
                                                 value=5.0, step=0.5)

        person_home_ownership = st.selectbox(
            "Home Ownership",
            options=["RENT", "OWN", "MORTGAGE", "OTHER"],
            help="Current housing status"
        )

        st.markdown("#### 💳 Loan Details")
        col4, col5, col6 = st.columns(3)

        with col4:
            loan_amnt = st.number_input("Loan Amount ($)", min_value=500,
                                         max_value=500_000, value=10000, step=500)
        with col5:
            loan_int_rate = st.slider("Interest Rate (%)", min_value=1.0,
                                       max_value=30.0, value=11.0, step=0.5)
        with col6:
            loan_grade = st.selectbox("Loan Grade", options=["A", "B", "C", "D", "E", "F", "G"],
                                       help="A = safest, G = riskiest")

        loan_intent = st.selectbox(
            "Loan Purpose",
            options=["PERSONAL", "EDUCATION", "MEDICAL", "VENTURE",
                     "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"]
        )

        st.markdown("#### 📋 Credit History")
        col7, col8, col9 = st.columns(3)

        with col7:
            loan_percent_income = st.slider(
                "Loan as % of Income", min_value=0.0, max_value=1.0,
                value=0.15, step=0.01,
                help="loan_amnt / person_income"
            )
        with col8:
            cb_person_default_on_file = st.selectbox(
                "Previous Default on Record?",
                options=["N", "Y"]
            )
        with col9:
            cb_person_cred_hist_length = st.number_input(
                "Credit History Length (years)",
                min_value=1, max_value=30, value=5
            )

        submitted = st.form_submit_button("🚀 Predict Loan Approval", use_container_width=True)

    # ── Prediction ────────────────────────────────────────────────────────
    if submitted:
        input_data = {
            "person_age":                   person_age,
            "person_income":                person_income,
            "person_home_ownership":        person_home_ownership,
            "person_emp_length":            person_emp_length,
            "loan_intent":                  loan_intent,
            "loan_grade":                   loan_grade,
            "loan_amnt":                    loan_amnt,
            "loan_int_rate":                loan_int_rate,
            "loan_percent_income":          loan_percent_income,
            "cb_person_default_on_file":    cb_person_default_on_file,
            "cb_person_cred_hist_length":   cb_person_cred_hist_length,
        }

        with st.spinner("Analyzing application..."):
            prediction, probability = predict(input_data, artifacts)

        # ── Result banner ──────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)

        if prediction == "Approved":
            st.markdown(f"""
            <div class="approved-banner">
                ✅ LOAN APPROVED
                <br><small style="font-size:1rem; font-weight:400">
                Confidence: {(1 - probability)*100:.1f}%
                </small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="rejected-banner">
                ❌ LOAN REJECTED
                <br><small style="font-size:1rem; font-weight:400">
                Default Risk: {probability*100:.1f}%
                </small>
            </div>
            """, unsafe_allow_html=True)

        # ── Risk gauge ─────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        import plotly.graph_objects as go

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=probability * 100,
            title={"text": "Default Risk Score (%)", "font": {"color": "white"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "white"},
                "bar":  {"color": "#764ba2"},
                "steps": [
                    {"range": [0, 30],  "color": "#00b09b"},
                    {"range": [30, 60], "color": "#f7b733"},
                    {"range": [60, 100],"color": "#f5515f"},
                ],
                "threshold": {
                    "line": {"color": "white", "width": 4},
                    "thickness": 0.75,
                    "value": probability * 100,
                },
            },
            number={"suffix": "%", "font": {"color": "white", "size": 40}},
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font={"color": "white"},
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Key insights ───────────────────────────────────────────────
        st.markdown("#### 💡 Key Insights")
        col_a, col_b, col_c = st.columns(3)

        dti = (loan_amnt / person_income) if person_income > 0 else 0
        col_a.metric("Debt-to-Income Ratio", f"{dti:.2%}", delta="Good" if dti < 0.36 else "High", delta_color="normal" if dti < 0.36 else "inverse")
        col_b.metric("Loan Grade Risk",       loan_grade, delta="Low" if loan_grade in ["A","B"] else ("Medium" if loan_grade in ["C","D"] else "High"))
        col_c.metric("Prior Default",         "Yes ⚠️" if cb_person_default_on_file == "Y" else "No ✅")

        # ── Save to DB ─────────────────────────────────────────────────
        db_data = {**input_data, "prediction": prediction, "probability": round(probability, 4)}
        if db_connected():
            saved = save_application(db_data)
            if saved:
                st.success("✅ Application saved to MySQL database.")
            else:
                st.warning("⚠️ Could not save to database.")
        else:
            st.info("ℹ️ Database not connected — result not saved. Check your .env settings.")

        # ── Tips ───────────────────────────────────────────────────────
        if prediction == "Rejected":
            st.markdown("#### 🛠️ Tips to Improve Approval Chances")
            tips = []
            if cb_person_default_on_file == "Y":
                tips.append("🔴 Resolve any past defaults — they heavily impact decisions.")
            if loan_grade in ["E", "F", "G"]:
                tips.append("🔴 Improve your credit score to get a better loan grade.")
            if dti > 0.4:
                tips.append("🟡 Reduce your loan amount or increase your income to lower DTI.")
            if person_emp_length < 2:
                tips.append("🟡 Lenders prefer at least 2 years of stable employment.")
            if not tips:
                tips.append("🟡 Consider applying for a smaller loan amount.")
            for tip in tips:
                st.markdown(f"- {tip}")
