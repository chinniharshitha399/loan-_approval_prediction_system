"""
page_modules/dashboard_page.py — Live Dashboard
"""
import os
import sys
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.db import get_all_applications, db_connected

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "credit_risk_dataset.csv")

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font_color   ="white",
    xaxis=dict(gridcolor="rgba(255,255,255,0.07)", showgrid=True),
    yaxis=dict(gridcolor="rgba(255,255,255,0.07)", showgrid=True),
    margin=dict(t=50, b=30, l=20, r=20),
    legend=dict(
        font=dict(color="white"),
        bgcolor="rgba(0,0,0,0)",
        orientation="h",
        yanchor="bottom", y=1.02,
        xanchor="right",  x=1,
    ),
)


def kpi_card(title, value, subtitle="", color="#7eb3ff", icon="📌"):
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg,
            rgba(255,255,255,0.08),
            rgba(255,255,255,0.03));
        border: 1px solid rgba(255,255,255,0.13);
        border-top: 4px solid {color};
        border-radius: 18px;
        padding: 22px 16px 18px 16px;
        text-align: center;
        margin-bottom: 8px;
        min-height: 130px;">
        <div style="font-size:1.6rem; margin-bottom:6px">{icon}</div>
        <div style="font-size:1.65rem; font-weight:800;
            color:{color}; margin-bottom:4px; line-height:1.1">
            {value}
        </div>
        <div style="font-size:0.88rem; font-weight:600;
            color:#ffffff; margin-bottom:4px">{title}</div>
        <div style="font-size:0.76rem; color:#999">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


@st.cache_data
def load_dataset():
    df = pd.read_csv(DATA_PATH)
    df = df.dropna()
    df = df[df["person_age"] < 100]
    df = df[df["person_emp_length"] < 60]
    df["loan_status_label"] = df["loan_status"].map({0: "Approved", 1: "Rejected"})
    return df


def divider(title):
    st.markdown(f"""
    <div style="margin: 36px 0 20px 0;
        display: flex; align-items: center; gap: 14px">
        <div style="font-size:1.15rem; font-weight:700;
            color:#7eb3ff; white-space:nowrap">{title}</div>
        <div style="flex:1; height:1px;
            background:rgba(255,255,255,0.1)"></div>
    </div>
    """, unsafe_allow_html=True)


def render():
    st.markdown('<p class="section-header">📊 Live Dashboard</p>',
                unsafe_allow_html=True)

    if not db_connected():
        st.error("⚠️ MySQL not connected. Check your .env file.")
        return

    apps = get_all_applications()

    if apps.empty:
        st.markdown("""
        <div style="text-align:center; padding:70px 20px;
            background:rgba(255,255,255,0.03);
            border:1px dashed rgba(255,255,255,0.15);
            border-radius:20px; margin-top:20px">
            <div style="font-size:4rem">📭</div>
            <h3 style="color:#7eb3ff; margin:16px 0 8px">
                No Applications Yet</h3>
            <p style="color:#888; font-size:0.95rem">
                Go to <strong style="color:#c9b8ff">🔮 Predict Loan</strong>
                and submit applications — they will show up here instantly.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Precompute KPIs ───────────────────────────────────────
    total     = len(apps)
    approved  = (apps["prediction"] == "Approved").sum()
    rejected  = (apps["prediction"] == "Rejected").sum()
    avg_risk  = apps["probability"].mean()
    high_risk = (apps["probability"] > 0.6).sum()
    avg_loan  = apps["loan_amnt"].mean()     if "loan_amnt"     in apps.columns else 0
    avg_inc   = apps["person_income"].mean() if "person_income" in apps.columns else 0

    # ══════════════════════════════════════════════════════════
    # SECTION 1 — KPI Cards
    # ══════════════════════════════════════════════════════════
    divider("🎯 Portfolio Overview")
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    with c1: kpi_card("Total",      f"{total:,}",         "Applications",          "#7eb3ff", "📋")
    with c2: kpi_card("Approved",   f"{approved:,}",      f"{approved/total:.0%}", "#00b09b", "✅")
    with c3: kpi_card("Rejected",   f"{rejected:,}",      f"{rejected/total:.0%}", "#f5515f", "❌")
    with c4: kpi_card("Avg Risk",   f"{avg_risk:.1%}",    "Default probability",   "#f7b733", "⚠️")
    with c5: kpi_card("High Risk",  f"{high_risk:,}",     "Risk score > 60%",      "#ff6b6b", "🔴")
    with c6: kpi_card("Avg Loan",   f"₹{avg_loan:,.0f}", "Per application",       "#c9b8ff", "💰")
    with c7: kpi_card("Avg Income", f"₹{avg_inc:,.0f}",  "Per applicant",         "#7bffb8", "💵")

    # ══════════════════════════════════════════════════════════
    # SECTION 2 — Approval Split + Timeline
    # ══════════════════════════════════════════════════════════
    divider("📈 Approval & Risk")
    col_left, col_right = st.columns(2)

    with col_left:
        fig = go.Figure(go.Pie(
            labels=["Approved", "Rejected"],
            values=[approved, rejected],
            hole=0.65,
            marker_colors=["#00b09b", "#f5515f"],
            textfont=dict(color="white", size=14),
            textinfo="label+percent",
        ))
        fig.update_layout(
            **LAYOUT,
            height=320,
            showlegend=False,
            title=dict(
                text="Approval Split",
                font=dict(color="white", size=15),
                x=0.5, xanchor="center"
            ),
            annotations=[dict(
                text=f"<b>{approved/total:.0%}</b><br>approved",
                x=0.5, y=0.5, font_size=18,
                font_color="white", showarrow=False
            )]
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        if "created_at" in apps.columns:
            apps["created_at"] = pd.to_datetime(apps["created_at"])
            apps["date"]       = apps["created_at"].dt.date
            daily = (apps.groupby(["date", "prediction"])
                        .size().reset_index(name="count"))
            if len(daily) >= 2:
                fig = px.area(
                    daily, x="date", y="count", color="prediction",
                    color_discrete_map={"Approved": "#00b09b",
                                        "Rejected": "#f5515f"},
                    title="Applications Over Time",
                    labels={"date": "Date", "count": "Count",
                            "prediction": "Result"},
                    line_shape="spline",
                )
                fig.update_traces(opacity=0.55)
                fig.update_layout(**LAYOUT, height=320)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown("""
                <div style="height:320px; display:flex;
                    align-items:center; justify-content:center;
                    background:rgba(255,255,255,0.03);
                    border:1px dashed rgba(255,255,255,0.12);
                    border-radius:16px; color:#666; font-size:0.9rem">
                    Submit more applications to see the timeline
                </div>
                """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # SECTION 3 — Breakdown Charts
    # ══════════════════════════════════════════════════════════
    divider("🔍 Application Breakdown")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if "loan_grade" in apps.columns:
            gd = (apps.groupby(["loan_grade", "prediction"])
                      .size().reset_index(name="count"))
            fig = px.bar(
                gd, x="loan_grade", y="count", color="prediction",
                color_discrete_map={"Approved": "#00b09b",
                                    "Rejected": "#f5515f"},
                barmode="group",
                title="By Loan Grade",
                labels={"loan_grade": "Grade",
                        "count": "Applications",
                        "prediction": "Result"},
            )
            fig.update_layout(**LAYOUT, height=310)
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        if "loan_intent" in apps.columns:
            id_ = (apps.groupby(["loan_intent", "prediction"])
                       .size().reset_index(name="count"))
            fig = px.bar(
                id_, x="count", y="loan_intent", color="prediction",
                color_discrete_map={"Approved": "#00b09b",
                                    "Rejected": "#f5515f"},
                orientation="h",
                title="By Loan Purpose",
                labels={"loan_intent": "Purpose",
                        "count": "Applications",
                        "prediction": "Result"},
            )
            fig.update_layout(**LAYOUT, height=310)
            st.plotly_chart(fig, use_container_width=True)

    with col_c:
        if "person_home_ownership" in apps.columns:
            hd = (apps.groupby(["person_home_ownership", "prediction"])
                      .size().reset_index(name="count"))
            fig = px.bar(
                hd, x="person_home_ownership", y="count",
                color="prediction",
                color_discrete_map={"Approved": "#00b09b",
                                    "Rejected": "#f5515f"},
                barmode="stack",
                title="By Home Ownership",
                labels={"person_home_ownership": "Ownership",
                        "count": "Applications",
                        "prediction": "Result"},
            )
            fig.update_layout(**LAYOUT, height=310)
            st.plotly_chart(fig, use_container_width=True)

    # ══════════════════════════════════════════════════════════
    # SECTION 4 — Risk Distribution
    # ══════════════════════════════════════════════════════════
    divider("⚠️ Risk Score Distribution")
    col_d, col_e = st.columns(2)

    with col_d:
        fig = px.histogram(
            apps, x="probability", color="prediction",
            nbins=20, barmode="overlay", opacity=0.8,
            color_discrete_map={"Approved": "#00b09b",
                                "Rejected": "#f5515f"},
            title="Default Risk Score Distribution",
            labels={"probability": "Default Probability",
                    "prediction": "Result"},
        )
        fig.update_layout(**LAYOUT, height=300)
        st.plotly_chart(fig, use_container_width=True)



    # ══════════════════════════════════════════════════════════
    # SECTION 5 — Recent Applications HTML Table
    # ══════════════════════════════════════════════════════════
    divider("📋 Recent Applications")

    display_cols = [
        "id", "person_age", "person_income", "loan_amnt",
        "loan_grade", "loan_intent", "prediction",
        "probability", "created_at"
    ]
    display_cols = [c for c in display_cols if c in apps.columns]
    recent = apps[display_cols].head(15).copy()

    # Format values
    if "probability"   in recent.columns:
        recent["probability"]   = (recent["probability"]*100).round(1).astype(str) + "%"
    if "person_income" in recent.columns:
        recent["person_income"] = recent["person_income"].apply(lambda x: f"₹{int(x):,}")
    if "loan_amnt"     in recent.columns:
        recent["loan_amnt"]     = recent["loan_amnt"].apply(lambda x: f"₹{int(x):,}")
    if "created_at"    in recent.columns:
        recent["created_at"]    = pd.to_datetime(
            recent["created_at"]).dt.strftime("%d %b %Y %H:%M")

    # Rename columns
    recent = recent.rename(columns={
        "id":                  "ID",
        "person_age":          "Age",
        "person_income":       "Income",
        "loan_amnt":           "Loan Amount",
        "loan_grade":          "Grade",
        "loan_intent":         "Purpose",
        "prediction":          "Decision",
        "probability":         "Risk Score",
        "created_at":          "Submitted At",
    })

    # Build HTML table
    header_cols = list(recent.columns)

    header_html = "".join([
        f"<th style='background:#1a1750; color:#7eb3ff;"
        f"font-size:0.88rem; font-weight:700; padding:13px 18px;"
        f"text-align:left; border-bottom:2px solid rgba(126,179,255,0.4);"
        f"white-space:nowrap'>{col}</th>"
        for col in header_cols
    ])

    rows_html = ""
    for i, (_, row) in enumerate(recent.iterrows()):
        bg = "rgba(30,27,75,0.85)" if i % 2 == 0 else "rgba(22,20,65,0.85)"
        cells = ""
        for col in header_cols:
            val = row[col]
            if col == "Decision":
                if val == "Approved":
                    extra = ("background:rgba(0,176,155,0.3);"
                             "color:#00e676; font-weight:700; text-align:center;")
                else:
                    extra = ("background:rgba(245,81,95,0.3);"
                             "color:#ff6b6b; font-weight:700; text-align:center;")
            elif col == "Risk Score":
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
        border:1px solid rgba(255,255,255,0.12);
        margin-bottom:20px; overflow-x:auto;">
        <table style="width:100%; border-collapse:collapse;
            font-family:sans-serif;">
            <thead><tr>{header_html}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # Download button
    csv = apps.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️  Download All Applications as CSV",
        data=csv,
        file_name="loan_applications.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # ══════════════════════════════════════════════════════════
