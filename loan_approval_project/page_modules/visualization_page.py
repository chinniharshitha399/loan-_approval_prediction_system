"""
page_modules/visualization_page.py — Analytics & Insights
"""
import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "credit_risk_dataset.csv")

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font_color   ="white",
    xaxis=dict(gridcolor="rgba(255,255,255,0.07)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.07)"),
    margin=dict(t=50, b=30, l=20, r=20),
    legend=dict(
        font=dict(color="white"),
        bgcolor="rgba(0,0,0,0)",
        orientation="h",
        yanchor="bottom", y=1.02,
        xanchor="right", x=1,
    ),
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df = df.dropna()
    df = df[df["person_age"] < 100]
    df = df[df["person_emp_length"] < 60]
    df["loan_status_label"] = df["loan_status"].map({0: "Approved", 1: "Rejected"})
    return df


def info_box(text):
    """Light explanation box shown above each chart."""
    st.markdown(f"""
    <div style="
        background: rgba(126,179,255,0.08);
        border-left: 4px solid #7eb3ff;
        border-radius: 8px;
        padding: 10px 16px;
        margin-bottom: 16px;
        color: #cccccc;
        font-size: 0.88rem;
        line-height: 1.6">
        💡 {text}
    </div>
    """, unsafe_allow_html=True)


def render():
    st.markdown('<p class="section-header">📈 Analytics & Insights</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Explore the credit risk dataset through simple, easy-to-read charts.</p>',
                unsafe_allow_html=True)

    if not os.path.exists(DATA_PATH):
        st.error("Dataset not found.")
        return

    df = load_data()

    # ── Top summary strip ─────────────────────────────────────
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Total Records",     f"{len(df):,}")
    s2.metric("Approved",          f"{(df['loan_status']==0).sum():,}")
    s3.metric("Rejected",          f"{(df['loan_status']==1).sum():,}")
    s4.metric("Approval Rate",     f"{(df['loan_status']==0).mean():.1%}")
    s5.metric("Avg Interest Rate", f"{df['loan_int_rate'].mean():.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "🧑 Who Are the Applicants?",
        "💳 Loan Details",
        "🔗 How Things Are Connected",
        "⚠️ What Causes Rejection?",
    ])

    # ════════════════════════════════════════════════════════
    # TAB 1 — Who Are the Applicants?
    # Simple demographic breakdown
    # ════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 🧑 Who Are the Applicants?")
        st.markdown("This tab shows the **personal background** of loan applicants — their age, income, employment, and housing situation.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Chart 1 — Age
        info_box("This chart shows the age groups of applicants. Younger people tend to have more rejections because they have less credit history.")
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(
                df, x="person_age",
                color="loan_status_label",
                nbins=30,
                barmode="overlay",
                opacity=0.78,
                color_discrete_map={"Approved": "#00b09b", "Rejected": "#f5515f"},
                title="📅 Age of Applicants",
                labels={"person_age": "Age (years)",
                        "loan_status_label": "Loan Result",
                        "count": "Number of People"},
            )
            fig.update_layout(**LAYOUT, height=320)
            st.plotly_chart(fig, use_container_width=True)

        # Chart 2 — Employment Length
        with col2:
            info_box("People with longer employment history are seen as more stable and reliable by banks.")
            fig = px.box(
                df,
                x="loan_status_label",
                y="person_emp_length",
                color="loan_status_label",
                color_discrete_map={"Approved": "#00b09b", "Rejected": "#f5515f"},
                title="💼 Employment Length vs Loan Result",
                labels={"loan_status_label": "Loan Result",
                        "person_emp_length": "Years Employed"},
            )
            fig.update_layout(**LAYOUT, height=320, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Chart 3 — Income
        info_box("Higher income applicants generally get approved more. The box shows where most people's income falls.")
        col3, col4 = st.columns(2)
        with col3:
            fig = px.box(
                df,
                x="loan_status_label",
                y="person_income",
                color="loan_status_label",
                color_discrete_map={"Approved": "#00b09b", "Rejected": "#f5515f"},
                title="💰 Annual Income vs Loan Result",
                labels={"loan_status_label": "Loan Result",
                        "person_income": "Annual Income (₹)"},
            )
            fig.update_layout(**LAYOUT, height=320, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        # Chart 4 — Home Ownership
        with col4:
            info_box("Homeowners and mortgage holders tend to get approved more because they have assets that show financial stability.")
            home = (df.groupby(["person_home_ownership", "loan_status_label"])
                      .size().reset_index(name="count"))
            fig = px.bar(
                home,
                x="person_home_ownership",
                y="count",
                color="loan_status_label",
                barmode="group",
                color_discrete_map={"Approved": "#00b09b", "Rejected": "#f5515f"},
                title="🏠 Home Ownership vs Loan Result",
                labels={"person_home_ownership": "Housing Status",
                        "count": "Number of Applicants",
                        "loan_status_label": "Loan Result"},
            )
            fig.update_layout(**LAYOUT, height=320)
            st.plotly_chart(fig, use_container_width=True)

    # ════════════════════════════════════════════════════════
    # TAB 2 — Loan Details
    # Simple loan amount / interest / purpose breakdown
    # ════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 💳 Loan Details")
        st.markdown("This tab shows **what kind of loans** people applied for — how much money, at what interest rate, and for what purpose.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Chart 1 — Loan Amount
        info_box("Most approved loans are for smaller amounts. Very large loans are more likely to be rejected.")
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(
                df,
                x="loan_amnt",
                color="loan_status_label",
                nbins=40,
                barmode="overlay",
                opacity=0.78,
                color_discrete_map={"Approved": "#00b09b", "Rejected": "#f5515f"},
                title="💵 Loan Amount Distribution",
                labels={"loan_amnt": "Loan Amount (₹)",
                        "loan_status_label": "Loan Result",
                        "count": "Number of Applicants"},
            )
            fig.update_layout(**LAYOUT, height=320)
            st.plotly_chart(fig, use_container_width=True)

        # Chart 2 — Interest rate by grade
        with col2:
            info_box("Loan Grade goes from A (safest, lowest interest) to G (riskiest, highest interest). Most rejections happen in grades D, E, F, G.")
            fig = px.box(
                df,
                x="loan_grade",
                y="loan_int_rate",
                color="loan_grade",
                color_discrete_sequence=px.colors.sequential.Plasma,
                title="📊 Interest Rate by Loan Grade (A=Best, G=Worst)",
                labels={"loan_grade": "Loan Grade",
                        "loan_int_rate": "Interest Rate (%)"},
            )
            fig.update_layout(**LAYOUT, height=320, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Chart 3 — Loan Purpose
        info_box("This shows what people are borrowing money for. Education and medical loans have higher rejection rates.")
        col3, col4 = st.columns(2)
        with col3:
            intent = (df.groupby(["loan_intent", "loan_status_label"])
                        .size().reset_index(name="count"))
            fig = px.bar(
                intent,
                x="loan_intent",
                y="count",
                color="loan_status_label",
                barmode="stack",
                color_discrete_map={"Approved": "#00b09b", "Rejected": "#f5515f"},
                title="🎯 What Is the Loan For?",
                labels={"loan_intent": "Loan Purpose",
                        "count": "Number of Applicants",
                        "loan_status_label": "Loan Result"},
            )
            fig.update_layout(**LAYOUT, height=340)
            st.plotly_chart(fig, use_container_width=True)

        # Chart 4 — Average loan by purpose
        with col4:
            info_box("Venture and home improvement loans tend to be for larger amounts on average.")
            avg_loan = (df.groupby("loan_intent")["loan_amnt"]
                          .mean()
                          .sort_values(ascending=True)
                          .reset_index())
            avg_loan.columns = ["Purpose", "Avg Loan Amount"]
            fig = px.bar(
                avg_loan,
                x="Avg Loan Amount",
                y="Purpose",
                orientation="h",
                color="Avg Loan Amount",
                color_continuous_scale=["#302b63", "#7eb3ff"],
                title="💰 Average Loan Amount by Purpose",
                labels={"Avg Loan Amount": "Avg Amount (₹)",
                        "Purpose": "Loan Purpose"},
                text="Avg Loan Amount",
            )
            fig.update_traces(
                texttemplate="₹%{text:,.0f}",
                textposition="outside",
                textfont_color="white",
            )
            fig.update_layout(**LAYOUT, height=340, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    # ════════════════════════════════════════════════════════
    # TAB 3 — How Things Are Connected
    # Simple correlation explained in plain English
    # ════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 🔗 How Things Are Connected")
        st.markdown("This tab shows **which factors most affect loan approval**. The stronger the connection to rejection, the more important that factor is.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Chart 1 — Correlation bar chart (plain English)
        info_box("This bar shows which features are most connected to loan rejection (red = increases rejection chance, green = decreases rejection chance).")

        numeric_cols = [
            "person_age", "person_income", "person_emp_length",
            "loan_amnt", "loan_int_rate", "loan_percent_income",
            "cb_person_cred_hist_length", "loan_status"
        ]
        corr = df[numeric_cols].corr()["loan_status"].drop("loan_status").sort_values()

        readable_names = {
            "person_age":               "Age of Applicant",
            "person_income":            "Annual Income",
            "person_emp_length":        "Employment Length",
            "loan_amnt":                "Loan Amount",
            "loan_int_rate":            "Interest Rate",
            "loan_percent_income":      "Loan as % of Income",
            "cb_person_cred_hist_length": "Credit History Length",
        }
        corr.index = [readable_names.get(i, i) for i in corr.index]
        colors = ["#f5515f" if v > 0 else "#00b09b" for v in corr.values]

        fig = go.Figure(go.Bar(
            x=corr.values,
            y=corr.index,
            orientation="h",
            marker_color=colors,
            text=[f"{v:+.3f}" for v in corr.values],
            textposition="outside",
            textfont=dict(color="white"),
            hovertemplate="<b>%{y}</b><br>Correlation: %{x:.3f}<extra></extra>",
        ))
        fig.update_layout(
            **LAYOUT,
            height=380,
            title=dict(
                text="Which Factors Are Most Connected to Loan Rejection?",
                font=dict(color="white", size=14)
            ),
            xaxis_title="Correlation Score (positive = increases rejection risk)",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div style="background:rgba(255,255,255,0.04);
            border:1px solid rgba(255,255,255,0.1);
            border-radius:12px; padding:20px; margin-top:8px">
            <strong style="color:#7eb3ff; font-size:1rem">
                📖 How to Read This Chart
            </strong>
            <div style="margin-top:12px; display:grid;
                grid-template-columns:1fr 1fr; gap:12px">
                <div style="color:#cccccc; font-size:0.88rem">
                    🔴 <strong style="color:#f5515f">Red bars (positive)</strong><br>
                    These factors <strong>increase</strong> rejection risk.<br>
                    Example: High interest rate → more likely rejected.
                </div>
                <div style="color:#cccccc; font-size:0.88rem">
                    🟢 <strong style="color:#00b09b">Green bars (negative)</strong><br>
                    These factors <strong>decrease</strong> rejection risk.<br>
                    Example: High income → more likely approved.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Chart 2 — Heatmap (simplified)
        info_box("This heatmap shows how all features relate to each other. Dark red = strong positive link. Dark blue = strong negative link.")

        full_corr = df[numeric_cols].corr()
        full_corr.index   = [readable_names.get(i, i) for i in full_corr.index]
        full_corr.columns = [readable_names.get(i, i) for i in full_corr.columns]

        fig = px.imshow(
            full_corr,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            title="Full Feature Correlation Map",
            aspect="auto",
            zmin=-1, zmax=1,
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=440,
            margin=dict(t=50, b=20, l=20, r=20),
        )
        fig.update_traces(textfont_color="white")
        st.plotly_chart(fig, use_container_width=True)

    # ════════════════════════════════════════════════════════
    # TAB 4 — What Causes Rejection?
    # Risk factors explained simply
    # ════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### ⚠️ What Causes Rejection?")
        st.markdown("This tab highlights the **biggest reasons why loans get rejected** — so you know exactly what to improve.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Chart 1 — Prior Default
        info_box("Having a previous loan default is one of the biggest red flags for banks. It means you failed to repay a loan before.")
        col1, col2 = st.columns(2)
        with col1:
            default_data = (df.groupby(["cb_person_default_on_file",
                                         "loan_status_label"])
                              .size().reset_index(name="count"))
            default_data["cb_person_default_on_file"] = (
                default_data["cb_person_default_on_file"]
                .map({"Y": "Yes — Has Default", "N": "No — Clean Record"})
            )
            fig = px.bar(
                default_data,
                x="cb_person_default_on_file",
                y="count",
                color="loan_status_label",
                barmode="group",
                color_discrete_map={"Approved": "#00b09b", "Rejected": "#f5515f"},
                title="🚨 Prior Loan Default vs Outcome",
                labels={"cb_person_default_on_file": "Prior Default?",
                        "count": "Number of Applicants",
                        "loan_status_label": "Loan Result"},
            )
            fig.update_layout(**LAYOUT, height=330)
            st.plotly_chart(fig, use_container_width=True)

        # Chart 2 — Rejection rate by grade
        with col2:
            info_box("Lower loan grades have much higher rejection rates. Grade A almost never gets rejected. Grade G almost always does.")
            grade_risk = (df.groupby("loan_grade")["loan_status"]
                            .mean().reset_index())
            grade_risk.columns = ["Loan Grade", "Rejection Rate"]
            grade_risk["Rejection Rate %"] = (
                grade_risk["Rejection Rate"] * 100
            ).round(1)

            fig = px.bar(
                grade_risk,
                x="Loan Grade",
                y="Rejection Rate %",
                color="Rejection Rate %",
                color_continuous_scale=["#00b09b", "#f7b733", "#f5515f"],
                title="📉 Rejection Rate by Loan Grade (%)",
                text="Rejection Rate %",
                labels={"Rejection Rate %": "Rejection Rate (%)"},
            )
            fig.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
                textfont_color="white",
            )
            fig.update_layout(**LAYOUT, height=330,
                              coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Chart 3 — Loan to Income Ratio
        info_box("When your loan amount is too large compared to your income, banks get worried you cannot repay it. Keep your loan below 30% of your income.")
        col3, col4 = st.columns(2)
        with col3:
            fig = px.box(
                df,
                x="loan_status_label",
                y="loan_percent_income",
                color="loan_status_label",
                color_discrete_map={"Approved": "#00b09b", "Rejected": "#f5515f"},
                title="⚖️ Loan-to-Income Ratio vs Outcome",
                labels={"loan_status_label": "Loan Result",
                        "loan_percent_income": "Loan as % of Income"},
            )
            fig.update_layout(**LAYOUT, height=330, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        # Chart 4 — Credit history length
        with col4:
            info_box("People with longer credit history are more trustworthy to banks because there is more data showing they repay loans responsibly.")
            fig = px.histogram(
                df,
                x="cb_person_cred_hist_length",
                color="loan_status_label",
                nbins=25,
                barmode="overlay",
                opacity=0.78,
                color_discrete_map={"Approved": "#00b09b", "Rejected": "#f5515f"},
                title="📅 Credit History Length vs Outcome",
                labels={"cb_person_cred_hist_length": "Credit History (years)",
                        "loan_status_label": "Loan Result",
                        "count": "Number of Applicants"},
            )
            fig.update_layout(**LAYOUT, height=330)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Risk Summary Table — plain and readable
        info_box("This table summarizes rejection rates and average loan details for each loan grade. Use it to understand where you stand.")
        st.markdown("#### 📋 Rejection Rate Summary by Loan Grade")

        risk_summary = df.groupby("loan_grade").agg(
            Total       =("loan_status", "count"),
            Rejected    =("loan_status", "sum"),
            Avg_Rate    =("loan_int_rate", "mean"),
            Avg_Amount  =("loan_amnt", "mean"),
        ).reset_index()

        risk_summary["Rejection Rate"] = (
            risk_summary["Rejected"] / risk_summary["Total"] * 100
        ).round(1).astype(str) + "%"
        risk_summary["Avg Interest Rate"] = risk_summary["Avg_Rate"].round(2).astype(str) + "%"
        risk_summary["Avg Loan Amount"]   = risk_summary["Avg_Amount"].round(0).apply(lambda x: f"₹{int(x):,}")

        display = risk_summary[[
            "loan_grade", "Total", "Rejected",
            "Rejection Rate", "Avg Interest Rate", "Avg Loan Amount"
        ]].rename(columns={"loan_grade": "Loan Grade"})

        # Build HTML table
        header_html = "".join([
            f"<th style='background:#1a1750; color:#7eb3ff; font-size:0.88rem;"
            f"font-weight:700; padding:13px 18px; text-align:left;"
            f"border-bottom:2px solid rgba(126,179,255,0.4);'>{col}</th>"
            for col in display.columns
        ])

        rows_html = ""
        for i, (_, row) in enumerate(display.iterrows()):
            bg = "rgba(30,27,75,0.85)" if i % 2 == 0 else "rgba(22,20,65,0.85)"
            cells = ""
            for col in display.columns:
                val = row[col]
                if col == "Rejection Rate":
                    try:
                        v = float(str(val).replace("%",""))
                        if v > 60:
                            extra = "color:#f5515f; font-weight:700"
                        elif v > 35:
                            extra = "color:#f7b733; font-weight:700"
                        else:
                            extra = "color:#00b09b; font-weight:700"
                    except Exception:
                        extra = "color:#ffffff"
                else:
                    extra = "color:#ffffff"
                cells += (
                    f"<td style='padding:12px 18px; font-size:0.88rem;"
                    f"border-bottom:1px solid rgba(255,255,255,0.07);"
                    f"{extra}'>{val}</td>"
                )
            rows_html += f"<tr style='background:{bg}'>{cells}</tr>"

        st.markdown(f"""
        <div style="border-radius:16px; overflow:hidden;
            border:1px solid rgba(255,255,255,0.12); margin-top:8px">
            <table style="width:100%; border-collapse:collapse; font-family:sans-serif;">
                <thead><tr>{header_html}</tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)