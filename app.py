from __future__ import annotations

from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analytics import (
    add_features, apply_filters, calculate_kpis, grouped_metrics, load_data
)
from modeling import (
    MODEL_FEATURES, feature_importance, predict_customer, train_and_evaluate
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "European_Bank.csv"

st.set_page_config(
    page_title="Customer Retention Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {background: #f5f7fb;}
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
    .hero {
        padding: 1.5rem 1.7rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #101a38 0%, #294b9d 100%);
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 10px 25px rgba(16,26,56,.12);
    }
    .hero h1 {margin: 0; font-size: 2.15rem;}
    .hero p {margin: .55rem 0 0 0; opacity: .88;}
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e3e8f1;
        border-radius: 14px;
        padding: 1rem;
        box-shadow: 0 4px 14px rgba(30,45,80,.04);
    }
    .insight {
        background: white;
        border-left: 5px solid #2f65d9;
        border-radius: 10px;
        padding: .9rem 1rem;
        margin: .5rem 0;
        border-top: 1px solid #e5eaf2;
        border-right: 1px solid #e5eaf2;
        border-bottom: 1px solid #e5eaf2;
    }
    .risk-critical {font-weight: 700; color: #9d1c1c;}
    .small-note {font-size: .85rem; opacity: .75;}
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(show_spinner=False)
def get_data():
    return add_features(load_data(DATA_PATH))

@st.cache_resource(show_spinner="Training churn-risk model...")
def get_model(data):
    return train_and_evaluate(data)

try:
    data = get_data()
except FileNotFoundError as exc:
    st.error("The project dataset could not be found.")
    st.code(str(exc))
    st.info(
        "Required GitHub path: data/European_Bank.csv"
    )
    st.stop()
except Exception as exc:
    st.error("The dataset could not be loaded.")
    st.exception(exc)
    st.stop()
model, evaluation_metrics = get_model(data)

# Add model scores to the dashboard dataset once the operational model is ready.
# These fields power the premium-risk map, priority queue and customer explorer.
data = data.copy()
data["PredictedChurnProbability"] = model.predict_proba(data[MODEL_FEATURES])[:, 1]
data["PredictedRiskTier"] = pd.cut(
    data["PredictedChurnProbability"],
    bins=[-float("inf"), 0.30, 0.55, 0.75, float("inf")],
    labels=["Low", "Moderate", "High", "Critical"],
).astype(str)

with st.sidebar:
    st.title("Filters")
    geography = st.multiselect(
        "Geography",
        sorted(data["Geography"].unique()),
        default=sorted(data["Geography"].unique()),
    )
    gender = st.multiselect(
        "Gender",
        sorted(data["Gender"].unique()),
        default=sorted(data["Gender"].unique()),
    )
    age_range = st.slider(
        "Age range",
        int(data["Age"].min()), int(data["Age"].max()),
        (int(data["Age"].min()), int(data["Age"].max())),
    )
    tenure_range = st.slider(
        "Tenure range",
        int(data["Tenure"].min()), int(data["Tenure"].max()),
        (int(data["Tenure"].min()), int(data["Tenure"].max())),
    )
    products = st.multiselect(
        "Number of products",
        sorted(data["NumOfProducts"].unique().tolist()),
        default=sorted(data["NumOfProducts"].unique().tolist()),
    )
    balance_range = st.slider(
        "Balance range",
        float(data["Balance"].min()), float(data["Balance"].max()),
        (float(data["Balance"].min()), float(data["Balance"].max())),
        step=1000.0,
        format="€%.0f",
    )
    st.caption("All KPIs and charts update from these filters.")

filtered = apply_filters(
    data, geography, gender, age_range, tenure_range, products, balance_range
)

st.markdown(
    """
    <div class="hero">
      <h1>Customer Engagement & Product Utilization Analytics</h1>
      <p>Retention intelligence for engagement strategy, product optimization,
      premium-customer protection and evidence-based decision-making.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning("No customers match the current filter combination.")
    st.stop()

kpi = calculate_kpis(filtered)

row1 = st.columns(5)
row1[0].metric("Customers", f"{kpi['customers']:,}")
row1[1].metric("Churn Rate", f"{kpi['churn_rate']:.1%}")
row1[2].metric("Retention Rate", f"{kpi['retention_rate']:.1%}")
row1[3].metric("Active Members", f"{kpi['active_rate']:.1%}")
row1[4].metric("Avg. Products", f"{kpi['avg_products']:.2f}")

row2 = st.columns(5)
row2[0].metric("Engagement Retention", f"{kpi['engagement_retention_ratio']:.1%}")
row2[1].metric("Product Depth Index", f"{kpi['product_depth_index']:.1%}")
row2[2].metric("High-Balance Disengagement", f"{kpi['high_balance_disengagement_rate']:.1%}")
row2[3].metric("Credit-Card Stickiness", f"{kpi['credit_card_stickiness_score']:.1%}")
row2[4].metric("Relationship Strength", f"{kpi['relationship_strength_index']:.1f}/100")

tabs = st.tabs([
    "Executive Overview",
    "Engagement",
    "Product Utilization",
    "Premium Risk",
    "Churn Model",
    "Customer Explorer",
])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        geo = grouped_metrics(filtered, "Geography")
        fig = px.bar(
            geo, x="Geography", y="ChurnRate",
            text=geo["ChurnRate"].map(lambda x: f"{x:.1%}"),
            title="Churn Rate by Geography",
        )
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        activity = grouped_metrics(filtered, "ActivityStatus")
        fig = px.bar(
            activity, x="ActivityStatus", y="ChurnRate",
            text=activity["ChurnRate"].map(lambda x: f"{x:.1%}"),
            title="Churn Rate by Activity Status",
        )
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        age = grouped_metrics(filtered, "AgeBand")
        fig = px.line(
            age, x="AgeBand", y="ChurnRate", markers=True,
            title="Churn Across Age Bands",
        )
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        tiers = filtered["RelationshipTier"].value_counts().rename_axis("Tier").reset_index(name="Customers")
        fig = px.pie(
            tiers, names="Tier", values="Customers",
            hole=0.55, title="Relationship Strength Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)

    best_geo = geo.sort_values("ChurnRate").iloc[0]
    worst_geo = geo.sort_values("ChurnRate", ascending=False).iloc[0]
    active_rates = activity.set_index("ActivityStatus")["ChurnRate"].to_dict()
    st.markdown(
        f"""
        <div class="insight"><b>Geographic priority:</b>
        {worst_geo['Geography']} has the highest filtered churn rate
        ({worst_geo['ChurnRate']:.1%}), compared with
        {best_geo['Geography']} at {best_geo['ChurnRate']:.1%}.</div>
        <div class="insight"><b>Engagement signal:</b>
        Inactive customers churn at {active_rates.get('Inactive', 0):.1%},
        while active customers churn at {active_rates.get('Active', 0):.1%}.
        Activity is therefore a major operational retention signal.</div>
        """,
        unsafe_allow_html=True,
    )

with tabs[1]:
    segments = grouped_metrics(filtered, "EngagementSegment")
    fig = px.scatter(
        segments,
        x="ActiveRate", y="ChurnRate", size="Customers",
        color="EngagementSegment",
        hover_data=["AverageProducts", "AverageBalance", "RelationshipStrength"],
        title="Engagement Segments: Activity vs Churn",
    )
    fig.update_xaxes(tickformat=".0%")
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        heat = (
            filtered.pivot_table(
                index="ActivityStatus",
                columns="NumOfProducts",
                values="Exited",
                aggfunc="mean",
                observed=False,
            )
        )
        fig = px.imshow(
            heat,
            text_auto=".1%",
            aspect="auto",
            labels={"x": "Products", "y": "Activity", "color": "Churn"},
            title="Churn Heatmap: Activity and Product Count",
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        balance_engagement = (
            filtered.groupby("EngagementSegment", observed=False)
            .agg(Customers=("CustomerId", "count"), AverageBalance=("Balance", "mean"))
            .reset_index()
        )
        fig = px.bar(
            balance_engagement, x="EngagementSegment", y="AverageBalance",
            text_auto=".3s", title="Average Balance by Engagement Segment",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        segments.style.format({
            "ChurnRate": "{:.1%}",
            "RetentionRate": "{:.1%}",
            "ActiveRate": "{:.1%}",
            "AverageProducts": "{:.2f}",
            "AverageBalance": "€{:,.0f}",
            "RelationshipStrength": "{:.1f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

with tabs[2]:
    products_table = grouped_metrics(filtered, "NumOfProducts")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(
            products_table, x="NumOfProducts", y="ChurnRate",
            text=products_table["ChurnRate"].map(lambda x: f"{x:.1%}"),
            title="Churn by Product Count",
        )
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(
            products_table, x="NumOfProducts", y="Customers",
            text_auto=True, title="Customer Distribution by Product Count",
        )
        st.plotly_chart(fig, use_container_width=True)

    card = grouped_metrics(filtered, "CardStatus")
    fig = px.bar(
        card, x="CardStatus", y=["RetentionRate", "ChurnRate"],
        barmode="group", title="Credit Card Retention Comparison",
    )
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "Interpret product count non-linearly: two products show the strongest "
        "historical retention, while the small three- and four-product groups "
        "show unusually high churn and should be investigated for product-fit "
        "or service-complexity issues."
    )

with tabs[3]:
    q75 = filtered["Balance"].quantile(0.75)
    premium = filtered[filtered["Balance"].ge(q75)].copy()
    premium["RiskLabel"] = premium.apply(
        lambda r: (
            "Exited" if r["Exited"] == 1 else
            "Premium At Risk" if r["IsActiveMember"] == 0 else
            "Premium Engaged"
        ),
        axis=1,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Premium Threshold", f"€{q75:,.0f}")
    c2.metric("Premium Customers", f"{len(premium):,}")
    c3.metric(
        "Inactive Premium Churn",
        f"{premium.loc[premium['IsActiveMember'].eq(0), 'Exited'].mean():.1%}"
        if (premium["IsActiveMember"] == 0).any() else "0.0%",
    )

    fig = px.scatter(
        premium,
        x="Balance", y="EstimatedSalary",
        color="RiskLabel", size="PredictedChurnProbability",
        hover_data=[
            "CustomerId", "Geography", "Age", "NumOfProducts",
            "IsActiveMember", "RelationshipStrengthIndex"
        ],
        title="Premium Customer Risk Map",
    )
    st.plotly_chart(fig, use_container_width=True)

    premium_priority = (
        premium[
            premium["Exited"].eq(0)
            & (
                premium["IsActiveMember"].eq(0)
                | premium["PredictedChurnProbability"].ge(0.55)
            )
        ]
        .sort_values(["PredictedChurnProbability", "Balance"], ascending=False)
    )
    st.subheader("Premium Retention Priority Queue")
    st.dataframe(
        premium_priority[[
            "CustomerId", "Surname", "Geography", "Age", "Balance",
            "NumOfProducts", "IsActiveMember", "RelationshipStrengthIndex",
            "PredictedChurnProbability", "EngagementSegment"
        ]].head(100).style.format({
            "Balance": "€{:,.2f}",
            "RelationshipStrengthIndex": "{:.1f}",
            "PredictedChurnProbability": "{:.1%}",
        }),
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Download premium priority queue",
        premium_priority.to_csv(index=False).encode("utf-8"),
        "premium_retention_priority.csv",
        "text/csv",
    )

with tabs[4]:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("ROC AUC", f"{evaluation_metrics['ROC AUC']:.3f}")
    m2.metric("Accuracy", f"{evaluation_metrics['Accuracy']:.1%}")
    m3.metric("Precision", f"{evaluation_metrics['Precision']:.1%}")
    m4.metric("Recall", f"{evaluation_metrics['Recall']:.1%}")
    m5.metric("F1 Score", f"{evaluation_metrics['F1 Score']:.3f}")

    c1, c2 = st.columns([1.15, 0.85])
    with c1:
        importance = feature_importance(model).head(12)
        fig = px.bar(
            importance.sort_values("Importance"),
            x="Importance", y="Feature", orientation="h",
            title="Feature Importance",
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Churn Risk Simulator")
        with st.form("risk_form"):
            credit = st.slider("Credit score", 300, 900, 650)
            geo = st.selectbox("Geography", sorted(data["Geography"].unique()))
            age = st.slider("Age", 18, 92, 40)
            tenure = st.slider("Tenure", 0, 10, 5)
            balance = st.number_input("Balance (€)", 0.0, 300000.0, 90000.0, 1000.0)
            products_n = st.selectbox("Number of products", [1, 2, 3, 4], index=1)
            card = st.selectbox("Has credit card", [0, 1], format_func=lambda x: "Yes" if x else "No")
            active = st.selectbox("Active member", [0, 1], index=1, format_func=lambda x: "Yes" if x else "No")
            salary = st.number_input("Estimated salary (€)", 0.0, 300000.0, 100000.0, 1000.0)
            submitted = st.form_submit_button("Estimate Risk")

        if submitted:
            score = predict_customer(model, {
                "CreditScore": credit,
                "Geography": geo,
                "Age": age,
                "Tenure": tenure,
                "Balance": balance,
                "NumOfProducts": products_n,
                "HasCrCard": card,
                "IsActiveMember": active,
                "EstimatedSalary": salary,
            })
            if score < 0.30:
                tier = "Low"
            elif score < 0.55:
                tier = "Moderate"
            elif score < 0.75:
                tier = "High"
            else:
                tier = "Critical"
            st.metric("Predicted churn probability", f"{score:.1%}")
            st.write(f"Risk tier: **{tier}**")

    st.caption(
        "The model is a decision-support tool, not an automated decision maker. "
        "Gender is excluded from prediction and retained only for fairness monitoring."
    )

with tabs[5]:
    st.subheader("Customer-Level Analytics")
    search = st.text_input("Search Customer ID or surname")
    explorer = filtered.copy()
    if search.strip():
        token = search.strip().lower()
        explorer = explorer[
            explorer["CustomerId"].astype(str).str.contains(token, na=False)
            | explorer["Surname"].str.lower().str.contains(token, na=False)
        ]

    show_columns = [
        "CustomerId", "Surname", "Geography", "Gender", "Age", "Tenure",
        "CreditScore", "Balance", "NumOfProducts", "HasCrCard",
        "IsActiveMember", "EstimatedSalary", "Exited",
        "EngagementSegment", "RelationshipStrengthIndex"
    ]
    st.dataframe(
        explorer[show_columns],
        use_container_width=True,
        hide_index=True,
        height=520,
    )
    st.download_button(
        "Download filtered customer data",
        explorer.to_csv(index=False).encode("utf-8"),
        "filtered_customer_analytics.csv",
        "text/csv",
    )

st.markdown(
    """
    <p class="small-note">
    Project prepared for Aniket Chakraborty. Customer Engagement & Product Utilization Analytics for Retention Strategy.
    Historical associations do not establish causation; validate interventions through controlled pilots.
    </p>
    """,
    unsafe_allow_html=True,
)
