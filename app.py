import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Executive Analytics", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

.glass-card {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 16px;
    padding: 25px;
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 15px;
}

.stSidebar {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("Sample - Superstore.csv", encoding="latin1")
    df = df.drop_duplicates()
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Year"] = df["Order Date"].dt.year
    df["Profit Margin"] = np.where(df["Sales"] != 0, df["Profit"] / df["Sales"], 0)
    return df

df = load_data()

st.title("🚀 Executive Performance Intelligence")

st.sidebar.header("Filters")

years = sorted(df["Year"].dropna().unique())
regions = sorted(df["Region"].unique())
categories = sorted(df["Category"].unique())

selected_year = st.sidebar.selectbox("Year", years, index=len(years)-1)
selected_region = st.sidebar.multiselect("Region", regions, default=regions)
selected_category = st.sidebar.multiselect("Category", categories, default=categories)

filtered_df = df[
    (df["Year"] == selected_year) &
    (df["Region"].isin(selected_region)) &
    (df["Category"].isin(selected_category))
]

previous_df = df[df["Year"] == selected_year - 1]

total_revenue = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
margin = total_profit / total_revenue if total_revenue != 0 else 0

prev_revenue = previous_df["Sales"].sum()
revenue_growth = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue != 0 else 0

def animated_metric(label, value, suffix=""):
    placeholder = st.empty()
    for i in np.linspace(0, value, 40):
        placeholder.markdown(
            f"""
            <div class="glass-card">
                <h4>{label}</h4>
                <h2>{i:,.0f}{suffix}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(0.01)

col1, col2, col3 = st.columns(3)

with col1:
    animated_metric("Revenue", total_revenue, "$")

with col2:
    animated_metric("Profit", total_profit, "$")

with col3:
    animated_metric("Profit Margin", margin * 100, "%")

st.markdown("---")

col4, col5 = st.columns([2,1])

with col4:
    monthly = (
        filtered_df
        .groupby(filtered_df["Order Date"].dt.to_period("M"))["Sales"]
        .sum()
        .reset_index()
    )
    monthly["Order Date"] = monthly["Order Date"].astype(str)

    fig_line = px.area(
        monthly,
        x="Order Date",
        y="Sales",
        template="plotly_dark"
    )
    fig_line.update_traces(line_color="#00f5c4")
    fig_line.update_layout(
        title="Monthly Revenue Flow",
        transition_duration=800
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col5:
    category = (
        filtered_df.groupby("Category")["Profit"]
        .sum()
        .reset_index()
    )

    fig_donut = px.pie(
        category,
        names="Category",
        values="Profit",
        hole=0.65,
        template="plotly_dark"
    )
    fig_donut.update_layout(
        title="Profit Distribution",
        transition_duration=800
    )
    st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("---")

col6, col7 = st.columns(2)

with col6:
    region = (
        filtered_df.groupby("Region")[["Sales", "Profit"]]
        .sum()
        .reset_index()
    )

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=region["Region"],
        y=region["Sales"],
        name="Sales",
        marker_color="#00f5c4"
    ))
    fig_bar.add_trace(go.Bar(
        x=region["Region"],
        y=region["Profit"],
        name="Profit",
        marker_color="#ff6b6b"
    ))

    fig_bar.update_layout(
        barmode="group",
        template="plotly_dark",
        title="Regional Performance",
        transition_duration=800
    )

    st.plotly_chart(fig_bar, use_container_width=True)

with col7:
    top_products = (
        filtered_df.groupby("Product Name")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )

    fig_top = px.bar(
        top_products,
        x="Sales",
        y="Product Name",
        orientation="h",
        template="plotly_dark"
    )
    fig_top.update_layout(
        title="Top Products",
        transition_duration=800
    )
    st.plotly_chart(fig_top, use_container_width=True)

st.markdown("---")

if revenue_growth > 0:
    st.success(f"Revenue increased by {revenue_growth:.1f}% compared to last year.")
else:
    st.error(f"Revenue declined by {abs(revenue_growth):.1f}% compared to last year.")
