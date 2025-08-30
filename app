import os
import io
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# ---------- Optional Prophet (graceful fallback) ----------
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except Exception:
    PROPHET_AVAILABLE = False

# ---------- Page config ----------
st.set_page_config(
    page_title="AI SDG Command Center — Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- One consistent DARK theme (no glitter) ----------
pio.templates.default = "plotly_dark"
DARK_CSS = """
.stApp { background: #0d1117; }
.block-container { padding-top: 0.8rem; max-width: 1300px; }
h1,h2,h3 { color:#E0E0E0; letter-spacing: .2px; }
.metric-card { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 10px; }
.small-label { color: #8b949e; font-size: 11px; text-transform: uppercase; letter-spacing: .06em; }
.big-number { font-size: 22px; font-weight: 700; color: #f0f6fc; }
section[data-testid="stSidebar"] { background: #161b22; border-right: 1px solid #30363d; }
.dataframe td, .dataframe th { border-color: #30363d !important; }
"""
st.markdown(f"<style>{DARK_CSS}</style>", unsafe_allow_html=True)

# ---------- Utils ----------
@st.cache_data(show_spinner=False)
def load_data(local_path: str):
    """Load & prep dataset from local path only."""
    if not local_path or not os.path.exists(local_path):
        return None

    try:
        df = pd.read_csv(local_path, encoding="latin1")
    except Exception:
        return None

    # cleanup
    df.columns = df.columns.str.strip()

    # detect order date column
    date_col = None
    for c in df.columns:
        low = c.lower()
        if "dateorders" in low or ("order" in low and "date" in low):
            date_col = c
            break
    if date_col is None:
        # try common fallback
        if "OrderDate" in df.columns:
            date_col = "OrderDate"
        else:
            raise ValueError("Order date column not found. Expect e.g. 'order date (DateOrders)'.")

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col]).copy()
    df.rename(columns={date_col: "OrderDate"}, inplace=True)

    # make sure expected columns exist (create safe defaults if missing)
    needed = {
        "Sales": 0.0,
        "Order Profit Per Order": 0.0,
        "Late_delivery_risk": 0.0,
        "Order Id": "Unknown",
        "Market": "Unknown",
        "Customer Segment": "Unknown",
        "Order City": "Unknown",
        "Order Status": "Unknown",
        "Category Name": "Unknown",
        "Latitude": np.nan,
        "Longitude": np.nan,
    }
    for k, v in needed.items():
        if k not in df.columns:
            df[k] = v

    # derived fields
    df["Order Year"] = df["OrderDate"].dt.year
    df["Order Month"] = df["OrderDate"].dt.to_period("M").astype(str)
    df["is_late"] = (df.get("Late_delivery_risk", 0) > 0).astype(int)
    df["SLA_Breach"] = df["is_late"]

    return df


def kpi_card(label: str, value: str):
    st.markdown(
        f"<div class='metric-card'><div class='small-label'>{label}</div>"
        f"<div class='big-number'>{value}</div></div>",
        unsafe_allow_html=True,
    )


def percent(n, d):
    return 0.0 if d == 0 else (n / d) * 100.0


# =============================
# DATA SOURCE — LOCAL PATH ONLY
# =============================
st.sidebar.subheader("Data Source")
DEFAULT_CSV_PATH = r"C:\Users\malli\Downloads\DataCoSupplyChainDataset.csv"  # <- your path
csv_path = st.sidebar.text_input("Local CSV path", value=DEFAULT_CSV_PATH)

df = load_data(csv_path)
if df is None:
    st.error(f"Could not load dataset from:\n{csv_path}\n\nCheck the path and file name, then rerun.")
    st.stop()

# =============================
# FILTERS
# =============================
st.sidebar.subheader("Filters")
markets = ["All"] + sorted([m for m in df["Market"].dropna().unique().tolist() if m != "Unknown"])
segments = ["All"] + sorted([s for s in df["Customer Segment"].dropna().unique().tolist() if s != "Unknown"])
years = ["All"] + sorted(df["Order Year"].dropna().unique().astype(int).tolist(), reverse=True)

selected_market = st.sidebar.selectbox("Market", markets)
selected_segment = st.sidebar.selectbox("Customer Segment", segments)
selected_year = st.sidebar.selectbox("Order Year", years)

f = df.copy()
if selected_market != "All":
    f = f[f["Market"] == selected_market]
if selected_segment != "All":
    f = f[f["Customer Segment"] == selected_segment]
if selected_year != "All":
    f = f[f["Order Year"] == selected_year]

# =============================
# HEADER
# =============================
st.markdown("# AI SDG Command Center — Dashboard")
st.caption("A focused, minimal control room for supply-chain performance & sustainability.")

# =============================
# KPIs
# =============================
col1, col2, col3, col4 = st.columns(4)

total_sales = float(f["Sales"].sum())
total_profit = float(f["Order Profit Per Order"].sum())
on_time = 1.0 - (f["is_late"].sum() / len(f) if len(f) else 0.0)
orders = int(f["Order Id"].nunique())

with col1:
    kpi_card("Total Sales", f"${total_sales:,.0f}")
with col2:
    kpi_card("Total Profit", f"${total_profit:,.0f}")
with col3:
    kpi_card("On-Time Delivery", f"{on_time*100:,.1f}%")
with col4:
    kpi_card("Total Orders", f"{orders:,}")

st.markdown("---")

# =============================
# TABS
# =============================
t_overview, t_ops, t_risk, t_forecast, t_whatif, t_dq = st.tabs(
    ["Overview", "Operations", "Risk & SLA", "Forecast", "What-If", "Data Quality"]
)

# ---------- OVERVIEW ----------
with t_overview:
    c1, c2 = st.columns([1.4, 1.0])

    with c1:
        st.subheader("Sales Trend")
        if len(f):
            daily = f.set_index("OrderDate")["Sales"].resample("D").sum()
            fig = px.line(daily, labels={"value": "Sales", "index": "Date"})
            fig.update_layout(height=360)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")

    with c2:
        st.subheader("Sales & Profit by Market")
        if len(f):
            agg = (
                f.groupby("Market", dropna=False)[["Sales", "Order Profit Per Order"]]
                .sum()
                .reset_index()
            )
            fig2 = go.Figure()
            fig2.add_bar(x=agg["Market"], y=agg["Sales"], name="Sales")
            fig2.add_bar(x=agg["Market"], y=agg["Order Profit Per Order"], name="Profit")
            fig2.update_layout(barmode="group", height=360)
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Category Mix — Sales vs Margin")
    if len(f):
        cat = (
            f.groupby("Category Name", dropna=False)
            .agg(Sales=("Sales", "sum"), Profit=("Order Profit Per Order", "sum"))
            .reset_index()
        )
        cat["Margin %"] = np.where(cat["Sales"] > 0, cat["Profit"] / cat["Sales"] * 100, 0)
        fig3 = px.scatter(
            cat,
            x="Sales",
            y="Margin %",
            size="Sales",
            color="Category Name",
            size_max=36,
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Segment Share (Sales)")
    if len(f):
        seg = f.groupby("Customer Segment", dropna=False).agg(Sales=("Sales", "sum")).reset_index()
        fig4 = px.pie(seg, values="Sales", names="Customer Segment", hole=0.5)
        fig4.update_layout(height=360)
        st.plotly_chart(fig4, use_container_width=True)

# ---------- OPERATIONS ----------
with t_ops:
    st.subheader("Throughput & Service Levels")
    if len(f):
        daily = (
            f.set_index("OrderDate")
            .resample("D")
            .agg(Sales=("Sales", "sum"), Orders=("Order Id", "nunique"), Breach=("SLA_Breach", "mean"))
        )
        c1, c2 = st.columns(2)
        with c1:
            fig = px.line(daily, y="Orders", labels={"value": "Orders", "index": "Date"})
            fig.update_layout(height=340)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = px.line(daily, y="Sales", labels={"value": "Sales", "index": "Date"})
            fig.update_layout(height=340)
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Bottlenecks")
    c3, c4, c5 = st.columns(3)
    with c3:
        top_breach_cities = (
            f.groupby("Order City")["SLA_Breach"].mean().sort_values(ascending=False).head(5)
            if len(f)
            else pd.Series(dtype=float)
        )
        st.write("**Top SLA Breach Cities**")
        st.dataframe(top_breach_cities.rename("Breach Rate").to_frame())
    with c4:
        low_margin = (
            f.groupby("Category Name")
            .apply(lambda x: (x["Order Profit Per Order"].sum() / max(x["Sales"].sum(), 1)) * 100 if len(x) else 0)
            .sort_values()
            .head(5)
        )
        st.write("**Lowest Margin Categories**")
        st.dataframe(low_margin.rename("Margin %").to_frame())
    with c5:
        if "Order Status" in f.columns:
            returns = (
                f[f["Order Status"].str.contains("Return", case=False, na=False)]
                .groupby("Category Name")["Order Id"]
                .nunique()
                .sort_values(ascending=False)
                .head(5)
            )
        else:
            returns = pd.Series(dtype=int)
        st.write("**Return-Prone Categories**")
        st.dataframe(returns.rename("Return Orders").to_frame())

# ---------- RISK & SLA ----------
with t_risk:
    st.subheader("SLA Breach Heatmap")
    if len(f):
        risk = (
            f.pivot_table(index="Market", columns="Customer Segment", values="SLA_Breach", aggfunc="mean")
            * 100
        )
        # Avoid text_auto for compatibility across Plotly versions
        fig = px.imshow(risk.fillna(0), aspect="auto", color_continuous_scale="Reds", labels=dict(color="Breach %"))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Quick Recommendations")
    tips = []
    breach_rate = percent(f["SLA_Breach"].sum(), len(f))
    if breach_rate > 8:
        tips.append("Raise safety stock / buffer days on repeat-breach lanes (>8%).")
    if on_time < 0.94:
        tips.append("Audit carrier performance and rebalance volume toward top-quartile carriers.")
    if (f["Order Profit Per Order"] < 0).mean() > 0.05:
        tips.append(">5% orders are loss-making: tighten discounting and review freight surcharges.")
    if not tips:
        tips = ["Stable system. Continue weekly monitoring and exception-based reviews."]
    for t in tips:
        st.markdown(f"- {t}")

# ---------- FORECAST ----------
with t_forecast:
    st.subheader("Sales Forecast (Next 180 Days)")
    granularity = st.radio("Aggregate by", ["Daily", "Weekly", "Monthly"], horizontal=True)

    if not len(f):
        st.info("Not enough data to forecast.")
    else:
        rule = {"Daily": "D", "Weekly": "W", "Monthly": "MS"}[granularity]
        series = (
            f.set_index("OrderDate")["Sales"]
            .resample(rule)
            .sum()
            .reset_index()
            .rename(columns={"OrderDate": "ds", "Sales": "y"})
        )

        if PROPHET_AVAILABLE and series["y"].sum() > 0 and len(series) >= 10:
            m = Prophet(
                daily_seasonality=(granularity == "Daily"),
                weekly_seasonality=(granularity != "Monthly"),
                yearly_seasonality=True,
            )
            m.fit(series)
            future = m.make_future_dataframe(
                periods=180,
                freq=("D" if granularity == "Daily" else "W" if granularity == "Weekly" else "MS"),
            )
            fc = m.predict(future)

            fig = go.Figure()
            fig.add_scatter(x=series["ds"], y=series["y"], name="Actual")
            fig.add_scatter(x=fc["ds"], y=fc["yhat"], name="Forecast")
            fig.add_scatter(x=fc["ds"], y=fc["yhat_lower"], name="Lower", line=dict(width=0), showlegend=False)
            fig.add_scatter(x=fc["ds"], y=fc["yhat_upper"], name="Upper", fill="tonexty", line=dict(width=0), showlegend=False)
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Prophet not available or insufficient data — showing 14-day moving average.")
            s = f.set_index("OrderDate")["Sales"].resample("D").sum()
            if len(s):
                ma = s.rolling(14, min_periods=7).mean()
                fig = go.Figure()
                fig.add_scatter(x=s.index, y=s.values, name="Actual")
                fig.add_scatter(x=ma.index, y=ma.values, name="MA(14)")
                fig.update_layout(height=380)
                st.plotly_chart(fig, use_container_width=True)

# ---------- WHAT-IF ----------
with t_whatif:
    st.subheader("Scenario Lab — Profit & SLA")
    if len(f):
        c1, c2, c3 = st.columns(3)
        with c1:
            price_uplift = st.slider("Price uplift (%)", -10, 20, 0)
        with c2:
            demand_shift = st.slider("Demand change (%)", -30, 30, 0)
        with c3:
            breach_improve = st.slider("SLA improvement (pp)", 0, 15, 0)

        base_sales = f["Sales"].sum()
        base_profit = f["Order Profit Per Order"].sum()
        base_breach = percent(f["SLA_Breach"].sum(), len(f))

        new_sales = base_sales * (1 + price_uplift / 100) * (1 + demand_shift / 100)
        # simple profit sensitivity: assume ~60% variable cost; price uplift partially lifts margin
        new_profit = base_profit + (base_sales * (price_uplift / 100) * 0.4)
        new_breach = max(0, base_breach - breach_improve)

        d1, d2, d3 = st.columns(3)
        d1.metric("Projected Sales", f"${new_sales:,.0f}",
                  delta=f"{(new_sales - base_sales) / max(base_sales, 1) * 100:,.1f}%")
        d2.metric("Projected Profit", f"${new_profit:,.0f}",
                  delta=f"{(new_profit - base_profit) / max(base_profit, 1) * 100:,.1f}%")
        d3.metric("Projected Breach %", f"{new_breach:,.1f}%",
                  delta=f"{-breach_improve:.1f} pp")

        st.markdown("### Suggested Actions")
        suggestions = []
        if price_uplift > 0 and demand_shift < 0:
            suggestions.append("Pilot uplift on loyal segments; A/B test elasticities by region.")
        if breach_improve >= 5:
            suggestions.append("Renegotiate SLAs and add buffer days on volatile lanes.")
        if not suggestions:
            suggestions.append("Maintain status quo; iterate on high-volume lanes for small wins.")
        for s in suggestions:
            st.markdown(f"- {s}")
    else:
        st.info("Load data to run scenarios.")

# ---------- DATA QUALITY ----------
with t_dq:
    st.subheader("Data Completeness")
    cols = ["OrderDate", "Sales", "Order Profit Per Order", "Market", "Customer Segment", "Order Id", "Latitude", "Longitude"]
    missing = {c: f[c].isna().mean() * 100 if c in f.columns else 100 for c in cols}
    dq = pd.DataFrame({"Column": list(missing.keys()), "Missing %": [round(v, 2) for v in missing.values()]})
    st.dataframe(dq)

    st.markdown("### Export Current Filtered Data")
    csv = f.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv, file_name="filtered_supply_chain.csv", mime="text/csv")

    st.markdown("### Sample Records")
    st.dataframe(f.head(500))

# ---------- Footer ----------
st.caption("© Command Center · Minimal, decisive, and consistent.")
