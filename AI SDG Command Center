# app.py — SDG Command Center (8-slide deck, black & white)
# Slides: KPIs, Operations, Donuts & Bars, Map (Holo Earth), What-If, Forecast, OLAP, SDG Insights (interactive visuals)
import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# ---------- Optional Prophet ----------
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except Exception:
    PROPHET_AVAILABLE = False

# ---------- Page ----------
st.set_page_config(page_title="SDG Command Center — Slides", page_icon="📊", layout="wide")
pio.templates.default = "plotly_dark"

# ---------- Theme & spacing ----------
STYLES = """
:root{ --bg:#000; --panel:#0a0a0a; --border:#272727; --text:#fff; --muted:#cfcfcf; }
html,body,.stApp{ background:var(--bg)!important; color:var(--text)!important; }
.block-container{ max-width:1400px; padding-top:3.25rem; }   /* push content down so top controls are visible */
div[data-testid="stToolbar"]{ top:2.4rem; }                  /* move Streamlit toolbar down */
section[data-testid="stSidebar"]{ background:var(--panel)!important; border-right:1px solid var(--border); }
.infocard{ background:var(--panel); border:1px solid var(--border); border-radius:14px; padding:14px; box-shadow:0 10px 24px rgba(0,0,0,.45) }
.kpi .label{ font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.08em }
.kpi .value{ font-size:24px; font-weight:700; color:var(--text) }
hr{ border-color:var(--border) }
.dataframe td,.dataframe th{ border-color:var(--border)!important; color:var(--text)!important }
.space{ height:18px; }
.bigspace{ height:28px; }
"""
st.markdown(f"<style>{STYLES}</style>", unsafe_allow_html=True)
WHITE_PALETTE = ["#FFFFFF", "#DADADA", "#BFBFBF", "#A6A6A6", "#8C8C8C"]

# ---------- Data ----------
def get_csv_path() -> str:
    return os.getenv("CSV_PATH", r"C:\Users\malli\Downloads\DataCoSupplyChainDataset.csv")

@st.cache_data(show_spinner=False)
def load_data(path: str):
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path, encoding="latin1")
    df.columns = df.columns.str.strip()

    # detect date column
    date_col = None
    for c in df.columns:
        s = c.lower()
        if "dateorders" in s or ("order" in s and "date" in s):
            date_col = c; break
    if date_col is None:
        date_col = "OrderDate" if "OrderDate" in df.columns else None
    if date_col is None:
        raise ValueError("Order date column not found.")

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col]).copy().rename(columns={date_col: "OrderDate"})

    # ensure essential fields
    defaults = {
        "Sales": 0.0,
        "Order Profit Per Order": 0.0,
        "Late_delivery_risk": 0.0,
        "Order Id": "Unknown",
        "Market": "Unknown",
        "Customer Segment": "Unknown",
        "Order City": "Unknown",
        "Category Name": "Unknown",
        "Latitude": np.nan,
        "Longitude": np.nan,
        "Order Country": "Unknown",
        "Customer Id": "Unknown",
        "Customer Fname": "",
        "Customer Lname": "",
    }
    for k, v in defaults.items():
        if k not in df.columns:
            df[k] = v

    # numeric safety
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce").fillna(0.0)
    df["Order Profit Per Order"] = pd.to_numeric(df["Order Profit Per Order"], errors="coerce").fillna(0.0)

    # derived
    df["is_late"] = (df.get("Late_delivery_risk", 0) > 0).astype(int)
    df["SLA_Breach"] = df["is_late"]
    df["Order Year"] = df["OrderDate"].dt.year
    df["Month"] = df["OrderDate"].dt.to_period("M").astype(str)
    return df

PATH = get_csv_path()
st.sidebar.subheader("Data Source")
st.sidebar.code(PATH, language="text")
df = load_data(PATH)
if df is None:
    st.error(f"CSV not found at:\n{PATH}")
    st.stop()

# ---------- Filters ----------
st.sidebar.subheader("Filters")
min_d, max_d = df["OrderDate"].min().date(), df["OrderDate"].max().date()
d1, d2 = st.sidebar.slider("Order Date Range", min_value=min_d, max_value=max_d, value=(min_d, max_d))
mk_all = sorted([m for m in df["Market"].dropna().unique() if m != "Unknown"])
sg_all = sorted([s for s in df["Customer Segment"].dropna().unique() if s != "Unknown"])
yr_all = sorted(df["Order Year"].dropna().unique().astype(int), reverse=True)
mk = st.sidebar.multiselect("Markets", mk_all, default=mk_all)
sg = st.sidebar.multiselect("Segments", sg_all, default=sg_all)
yr = st.sidebar.multiselect("Years", yr_all, default=yr_all)

f = df[(df["OrderDate"].dt.date >= d1) & (df["OrderDate"].dt.date <= d2)].copy()
if mk: f = f[f["Market"].isin(mk)]
if sg: f = f[f["Customer Segment"].isin(sg)]
if yr: f = f[f["Order Year"].isin(yr)]

# ---------- Slides ----------
SLIDES = [
    "Slide 1 — KPIs",
    "Slide 2 — Operations",
    "Slide 3 — Donuts & Bars",
    "Slide 4 — Map (Holo Earth)",
    "Slide 5 — What-If",
    "Slide 6 — Forecast",
    "Slide 7 — OLAP Explorer",
    "Slide 8 — SDG Insights (Interactive)",
]

if "slide_index" not in st.session_state:
    st.session_state.slide_index = 0

def next_slide():
    st.session_state.slide_index = (st.session_state.slide_index + 1) % len(SLIDES)

def prev_slide():
    st.session_state.slide_index = (st.session_state.slide_index - 1) % len(SLIDES)

# ---------- Nav bar (synced) ----------
c1, c2, c3 = st.columns([1, 6, 1])
with c1:
    if st.button("◀ Prev", key="prev_btn"):
        prev_slide()
with c2:
    st.session_state.slide_index = st.selectbox(
        "Choose Slide",
        range(len(SLIDES)),
        format_func=lambda i: SLIDES[i],
        index=st.session_state.slide_index,
        key="slide_select"
    )
with c3:
    if st.button("Next ▶", key="next_btn"):
        next_slide()

st.markdown("<div class='space'></div>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("<div class='bigspace'></div>", unsafe_allow_html=True)

# ---------- Helpers ----------
def card_kpi(label, val):
    st.markdown(
        f"<div class='infocard kpi'><div class='label'>{label}</div><div class='value'>{val}</div></div>",
        unsafe_allow_html=True,
    )

def fig_style(fig, h=340):
    fig.update_layout(
        height=h, margin=dict(l=10, r=10, t=36, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FFFFFF"),
        xaxis=dict(gridcolor="#2a2a2a", zerolinecolor="#2a2a2a"),
        yaxis=dict(gridcolor="#2a2a2a", zerolinecolor="#2a2a2a"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig

# ---------- Slide functions ----------
def slide_1_kpis():
    st.markdown("## Executive KPIs")
    c1, c2, c3, c4 = st.columns(4)
    total_sales = float(f["Sales"].sum()) if len(f) else 0.0
    total_profit = float(f["Order Profit Per Order"].sum()) if len(f) else 0.0
    on_time = 1.0 - (f["is_late"].mean() if len(f) else 0.0)
    orders = int(f["Order Id"].nunique()) if len(f) else 0
    with c1: card_kpi("Total Sales", f"${total_sales:,.0f}")
    with c2: card_kpi("Total Profit", f"${total_profit:,.0f}")
    with c3: card_kpi("On-Time Delivery", f"{on_time*100:,.1f}%")
    with c4: card_kpi("Total Orders", f"{orders:,}")
    st.markdown("<div class='space'></div>", unsafe_allow_html=True)

    g1, g2, g3, g4 = st.columns(4)
    def gauge(v, title, rng=100):
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=v, title={'text': title},
            number={'font': {'color': '#FFFFFF'}},
            gauge={
                'axis': {'range': [0, rng], 'tickcolor': '#FFFFFF'},
                'bar': {'color': '#FFFFFF'},
                'bordercolor': '#FFFFFF',
                'bgcolor': 'rgba(255,255,255,0.02)',
                'steps': [{'range': [0, rng], 'color': 'rgba(255,255,255,0.05)'}],
            }
        ))
        fig_style(fig, h=200); st.plotly_chart(fig, use_container_width=True)
    with g1: gauge(max(0, on_time*100), "Service OK %")
    with g2: gauge(min(100, (1-on_time)*100), "Late %")
    with g3:
        margin = (total_profit/max(total_sales, 1))*100 if total_sales else 0
        gauge(margin, "Margin %")
    with g4:
        avg = total_sales/max(orders, 1)
        gauge(avg, "Avg $/Order", rng=max(100, avg*1.2))

def slide_2_ops():
    st.markdown("## Operations")
    if not len(f): st.info("No data."); return
    a, b = st.columns(2)
    daily = (f.set_index("OrderDate").resample("D")
             .agg(Sales=("Sales","sum"), Orders=("Order Id","nunique"), Breach=("SLA_Breach","mean")))
    with a:
        fig = px.line(daily, y="Orders", labels={"value":"Orders", "index":"Date"},
                      color_discrete_sequence=["#FFFFFF"])
        fig.update_traces(mode="lines+markers"); fig_style(fig); st.plotly_chart(fig, use_container_width=True)
    with b:
        fig = px.line(daily, y="Sales", labels={"value":"Sales", "index":"Date"},
                      color_discrete_sequence=["#BFBFBF"])
        fig.update_traces(mode="lines+markers"); fig_style(fig); st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='space'></div>", unsafe_allow_html=True)
    st.markdown("### SLA Heatmap (Market × Segment)")
    risk = f.pivot_table(index="Market", columns="Customer Segment", values="SLA_Breach", aggfunc="mean")*100
    fig_h = px.imshow(risk.fillna(0), aspect="auto", color_continuous_scale="Reds", labels=dict(color="Breach %"))
    fig_style(fig_h, h=420); st.plotly_chart(fig_h, use_container_width=True)

def slide_3_composition():
    st.markdown("## Composition — Donuts & Bars")
    if not len(f): st.info("No data."); return
    a, b, c = st.columns([1.2, 1.2, 1])
    with a:
        seg = f.groupby("Customer Segment")["Sales"].sum().reset_index()
        fig = px.pie(seg, values="Sales", names="Customer Segment", hole=.55,
                     color_discrete_sequence=WHITE_PALETTE)
        fig.update_traces(textfont_color="#000"); fig_style(fig); st.plotly_chart(fig, use_container_width=True)
    with b:
        late = pd.DataFrame({"Status": ["On-time","Late"],
                             "Orders": [(f["is_late"]==0).sum(), (f["is_late"]==1).sum()]})
        fig = px.pie(late, values="Orders", names="Status", hole=.55,
                     color_discrete_sequence=["#FFF", "#BFBFBF"])
        fig.update_traces(textfont_color="#000"); fig_style(fig); st.plotly_chart(fig, use_container_width=True)
    with c:
        mkp = (f.groupby("Market")[["Sales","Order Profit Per Order"]]
               .sum().reset_index().rename(columns={"Order Profit Per Order":"Profit"}))
        fig = go.Figure()
        fig.add_bar(x=mkp["Market"], y=mkp["Sales"], name="Sales", marker_color="#FFF")
        fig.add_bar(x=mkp["Market"], y=mkp["Profit"], name="Profit", marker_color="#BFBFBF")
        fig.update_layout(barmode="group"); fig_style(fig); st.plotly_chart(fig, use_container_width=True)

def slide_4_map():
    st.markdown("## Global Map — Holo Earth (Risk & Volume)")
    if not len(f): st.info("No data."); return

    # Prefer country choropleth
    if "Order Country" in f.columns and f["Order Country"].nunique() > 1:
        cc = (f.groupby("Order Country")
              .agg(Orders=("Order Id","nunique"), Sales=("Sales","sum"), Breach=("SLA_Breach","mean"))
              .reset_index())
        cc["Breach %"] = (cc["Breach"]*100).round(2)
        # Teal->yellow->orange->red
        scale = [[0.0, "#00C2A8"], [0.5, "#FFE066"], [0.8, "#FF8C42"], [1.0, "#E63946"]]
        fig = px.choropleth(
            cc, locations="Order Country", locationmode="country names",
            color="Breach %", hover_name="Order Country",
            hover_data={"Orders": True, "Sales": ":,", "Breach %": True},
            color_continuous_scale=scale
        )
        fig.update_geos(
            projection_type="orthographic",
            showcountries=True, countrycolor="#222",
            showcoastlines=True, coastlinecolor="#333",
            showocean=True,  oceancolor="rgba(20,25,40,1)",
            showland=True,   landcolor="rgba(10,10,10,1)",
            lataxis_showgrid=True, lataxis_gridcolor="#1f2536",
            lonaxis_showgrid=True,  lonaxis_gridcolor="#1f2536",
            showframe=True, framecolor="#1f2536"
        )
        fig.update_layout(coloraxis_colorbar=dict(title="Breach %"),
                          margin=dict(l=10, r=10, t=20, b=10), height=520)
        st.plotly_chart(fig, use_container_width=True)
        return

    # Fallback to lat/lon bubbles
    if {"Latitude","Longitude"}.issubset(f.columns):
        pts = f.dropna(subset=["Latitude","Longitude"])
        if len(pts):
            agg = pts.groupby(["Latitude","Longitude"]).agg(Orders=("Order Id","nunique")).reset_index()
            scale = [[0.0, "#00C2A8"], [0.5, "#FFE066"], [0.8, "#FF8C42"], [1.0, "#E63946"]]
            fig = px.scatter_geo(
                agg, lat="Latitude", lon="Longitude", size="Orders",
                color="Orders", color_continuous_scale=scale
            )
            fig.update_geos(
                projection_type="orthographic",
                showcountries=True, countrycolor="#222",
                showcoastlines=True, coastlinecolor="#333",
                showocean=True,  oceancolor="rgba(20,25,40,1)",
                showland=True,   landcolor="rgba(10,10,10,1)",
                lataxis_showgrid=True, lataxis_gridcolor="#1f2536",
                lonaxis_showgrid=True,  lonaxis_gridcolor="#1f2536",
                showframe=True, framecolor="#1f2536"
            )
            fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=520)
            st.plotly_chart(fig, use_container_width=True)
            return

    st.info("No country/geo fields available for map.")

def slide_5_whatif():
    st.markdown("## What-If — Scenario Lab (Profit & SLA)")
    if not len(f): st.info("No data."); return
    c1, c2, c3, c4 = st.columns(4)
    with c1: price_uplift = st.slider("Price uplift (%)", -10, 20, 0, key="wi_price")
    with c2: demand_shift = st.slider("Demand change (%)", -30, 30, 0, key="wi_demand")
    with c3: breach_improve = st.slider("SLA improvement (pp)", 0, 15, 0, key="wi_breach")
    with c4: variable_cost_pct = st.slider("Variable cost (%)", 30, 90, 60, key="wi_var")

    base_sales  = f["Sales"].sum()
    base_profit = f["Order Profit Per Order"].sum()
    base_breach = (f["SLA_Breach"].sum()/len(f))*100 if len(f) else 0.0

    new_sales  = base_sales * (1 + price_uplift/100.0) * (1 + demand_shift/100.0)
    margin_gain = base_sales * (price_uplift/100.0) * (1 - variable_cost_pct/100.0)
    new_profit = base_profit + margin_gain
    new_breach = max(0.0, base_breach - breach_improve)

    d1, d2, d3 = st.columns(3)
    d1.metric("Projected Sales", f"${new_sales:,.0f}", delta=f"{(new_sales - base_sales)/max(base_sales,1)*100:,.1f}%")
    d2.metric("Projected Profit", f"${new_profit:,.0f}", delta=f"{(new_profit - base_profit)/max(base_profit,1)*100:,.1f}%")
    d3.metric("Projected Breach %", f"{new_breach:,.1f}%", delta=f"{-breach_improve:.1f} pp")

    st.markdown("### Suggested Actions")
    suggestions = []
    if price_uplift > 0 and demand_shift < 0:
        suggestions.append("Pilot uplift on loyal segments; A/B test elasticities by region.")
    if breach_improve >= 5:
        suggestions.append("Renegotiate SLAs and buffer volatile lanes.")
    if variable_cost_pct > 70:
        suggestions.append("Drive supplier/3PL cost-down initiatives.")
    if not suggestions:
        suggestions.append("Maintain status quo; iterate on high-volume lanes for small gains.")
    for s in suggestions: st.markdown(f"- {s}")

def slide_6_forecast():
    st.markdown("## Sales Forecast (6–12 months)")
    gran = st.radio("Aggregate by", ["Monthly","Weekly"], horizontal=True, key="fc_gran")
    horizon = st.slider("Horizon", 6, 18, 6, key="fc_h")
    freq = "MS" if gran == "Monthly" else "W"
    if not len(f): st.info("No data."); return
    s = f.set_index("OrderDate")["Sales"].resample(freq).sum().reset_index().rename(columns={"OrderDate":"ds","Sales":"y"})
    if PROPHET_AVAILABLE and s["y"].sum()>0 and len(s)>=8:
        m = Prophet(daily_seasonality=False, weekly_seasonality=(gran=="Weekly"), yearly_seasonality=True)
        m.fit(s); future = m.make_future_dataframe(periods=horizon, freq=freq)
        fc = m.predict(future)
        fig = go.Figure()
        fig.add_scatter(x=s["ds"], y=s["y"], name="Actual", line_color="#FFF")
        fig.add_scatter(x=fc["ds"], y=fc["yhat"], name="Forecast", line_color="#BFBFBF")
        fig.add_scatter(x=fc["ds"], y=fc["yhat_lower"], showlegend=False, line=dict(width=0))
        fig.add_scatter(x=fc["ds"], y=fc["yhat_upper"], showlegend=False, fill="tonexty", line=dict(width=0))
        fig_style(fig); st.plotly_chart(fig, use_container_width=True)
    else:
        s["ma"] = s["y"].rolling(6, min_periods=3).mean()
        fig = go.Figure()
        fig.add_scatter(x=s["ds"], y=s["y"], name="Actual", line_color="#FFF")
        fig.add_scatter(x=s["ds"], y=s["ma"], name="MA(6)", line_color="#BFBFBF")
        fig_style(fig); st.plotly_chart(fig, use_container_width=True)

def slide_7_olap():
    st.markdown("## OLAP Explorer — Slice · Dice · Drill")
    if not len(f): st.info("No data."); return

    # Controls
    c1, c2, c3, c4 = st.columns([1.2, 1.2, 1, 1])
    with c1:
        row_dims = st.multiselect("Rows (dimensions)",
            options=["Order Year","Market","Customer Segment","Category Name","Order City"],
            default=["Order Year","Market"], key="olap_rows")
    with c2:
        col_dims = st.multiselect("Columns (dimensions)",
            options=["Customer Segment","Market","Category Name","Order Year"],
            default=["Customer Segment"], key="olap_cols")
    with c3:
        measure = st.selectbox("Measure", ["Sales","Order Profit Per Order","Orders","Late %"], index=0, key="olap_measure")
    with c4:
        agg = st.selectbox("Aggregation", ["sum","mean","count"], index=0, key="olap_agg")

    # Slicing helpers
    s1, s2, s3 = st.columns(3)
    with s1:
        pick_market = st.multiselect("Slice: Market", sorted(f["Market"].unique()), default=sorted(set(f["Market"])))
    with s2:
        pick_seg = st.multiselect("Slice: Segment", sorted(f["Customer Segment"].unique()), default=sorted(set(f["Customer Segment"])))
    with s3:
        pick_year = st.multiselect("Slice: Year", sorted(f["Order Year"].unique()), default=sorted(set(f["Order Year"])))

    df_ = f[f["Market"].isin(pick_market) & f["Customer Segment"].isin(pick_seg) & f["Order Year"].isin(pick_year)].copy()

    # OLAP fields
    df_["Orders"] = 1
    df_["Late %"] = df_["is_late"] * 100

    if not row_dims and not col_dims:
        st.warning("Choose at least one row or column dimension.")
        return

    # Pivot
    values = measure
    aggfunc = {"sum": np.sum, "mean": np.mean, "count": "count"}[agg]
    try:
        pvt = pd.pivot_table(
            df_,
            index=row_dims if row_dims else None,
            columns=col_dims if col_dims else None,
            values=values,
            aggfunc=aggfunc,
            fill_value=0
        )
    except Exception as e:
        st.error(f"Could not build pivot: {e}")
        return

    st.markdown("### Pivot Table")
    st.dataframe(pvt)

    st.markdown("<div class='space'></div>", unsafe_allow_html=True)

    # Chart
    t1, t2 = st.columns([1,1])
    with t1:
        chart_type = st.radio("Chart", ["Heatmap","Bars","Line"], horizontal=True, key="olap_chart")
    with t2:
        topk = st.slider("Top-K rows by total", 5, 30, 10, key="olap_topk")

    if chart_type == "Heatmap":
        fig = px.imshow(
            pvt if isinstance(pvt, pd.DataFrame) else pvt.to_frame(),
            color_continuous_scale="Blues", aspect="auto", labels=dict(color=measure)
        )
        fig_style(fig, h=460)
        st.plotly_chart(fig, use_container_width=True)
    else:
        # flatten rows for bars/lines
        if isinstance(pvt, pd.Series):
            series = pvt.sort_values(ascending=False).head(topk)
            x = series.index.astype(str); y = series.values
        else:
            series = pvt.sum(axis=1).sort_values(ascending=False).head(topk)
            x = [" • ".join(map(str, idx)) if isinstance(idx, tuple) else str(idx) for idx in series.index]
            y = series.values

        if chart_type == "Bars":
            fig = px.bar(x=x, y=y, labels={"x":"", "y":f"{agg.upper()} {measure}"}, color_discrete_sequence=["#FFFFFF"])
        else:
            fig = px.line(x=x, y=y, markers=True, labels={"x":"", "y":f"{agg.upper()} {measure}"}, color_discrete_sequence=["#FFFFFF"])
        fig.update_xaxes(tickangle=-30)
        fig_style(fig, h=420)
        st.plotly_chart(fig, use_container_width=True)

# ---------- NEW: Slide 8 — SDG Insights (answers with visuals) ----------
def slide_8_sdg():
    st.markdown("## SDG Insights — Where to Act (Visual Answers)")
    if not len(f): st.info("No data."); return

    # Controls for interactivity
    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns(4)
    with ctrl1:
        topN_market = st.slider("Top N Markets (Late %)", 3, 12, 6, key="sdg_topN_mkt")
    with ctrl2:
        q_sales = st.slider("Category High-Sales quantile", 0.50, 0.95, 0.75, 0.05, key="sdg_qsales")
    with ctrl3:
        topN_city = st.slider("Top N Cities (Breach)", 3, 15, 8, key="sdg_topN_city")
    with ctrl4:
        co2_factor = st.number_input("CO₂e proxy factor (kg per $)", min_value=0.0001, max_value=0.01, value=0.0008, step=0.0001, format="%.4f", key="sdg_co2f")

    st.markdown("<div class='space'></div>", unsafe_allow_html=True)

    # Row 1 — Markets (Late %) & Categories (High Sales + Low Margin)
    r1a, r1b = st.columns(2)

    # Markets Late %
    with r1a:
        by_mkt = f.groupby("Market").agg(
            LatePct=("SLA_Breach", "mean"),
            Sales=("Sales","sum"),
            Profit=("Order Profit Per Order","sum")
        ).reset_index()
        by_mkt["LatePct"] = by_mkt["LatePct"]*100
        top_mkt = by_mkt.sort_values("LatePct", ascending=False).head(topN_market)
        fig_mkt = px.bar(
            top_mkt, x="Market", y="LatePct",
            hover_data={"Sales":":,", "Profit":":,"},
            color_discrete_sequence=["#FFFFFF"],
            labels={"LatePct":"Late %"}
        )
        fig_mkt.update_yaxes(title="Late %")
        fig_style(fig_mkt, h=360)
        st.plotly_chart(fig_mkt, use_container_width=True)
        st.caption("Markets ranked by Late %. Reducing late deliveries here drives SDG9/12/13 outcomes.")

    # Categories high sales, low margin
    with r1b:
        cat = f.groupby("Category Name").agg(
            Sales=("Sales","sum"),
            Profit=("Order Profit Per Order","sum")
        ).reset_index()
        cat["Margin %"] = np.where(cat["Sales"]>0, (cat["Profit"]/cat["Sales"])*100, 0)
        sales_thr = cat["Sales"].quantile(q_sales) if len(cat) else 0
        cand = cat[cat["Sales"]>=sales_thr].copy()
        hi_sales_low_margin = cand.sort_values(["Margin %","Sales"], ascending=[True, False]).head(12)
        fig_cat = px.bar(
            hi_sales_low_margin, x="Category Name", y="Margin %",
            hover_data={"Sales":":,","Profit":":,"},
            color_discrete_sequence=["#BFBFBF"]
        )
        fig_cat.update_xaxes(tickangle=-25)
        fig_style(fig_cat, h=360)
        st.plotly_chart(fig_cat, use_container_width=True)
        st.caption("High-sales categories with lower margins — targets for cost, packaging, or pricing (SDG12).")

    st.markdown("<div class='space'></div>", unsafe_allow_html=True)

    # Row 2 — Cities (Hotspots) & Seasonality (Heatmap + CO2 proxy)
    r2a, r2b = st.columns(2)

    # Cities with highest SLA breaches
    with r2a:
        city = (f.groupby("Order City")["SLA_Breach"].mean()*100).sort_values(ascending=False).head(topN_city)
        city_df = city.reset_index().rename(columns={"SLA_Breach":"Late %"})
        fig_city = px.bar(city_df, x="Order City", y="Late %", color_discrete_sequence=["#FFFFFF"])
        fig_city.update_xaxes(tickangle=-25)
        fig_style(fig_city, h=360)
        st.plotly_chart(fig_city, use_container_width=True)
        st.caption("City-level hotspots for operational root cause (lanes, lead-times, carriers).")

    # Seasonality — heatmap of Late % Month × Market + CO2 proxy line
    with r2b:
        tmp = f.copy()
        tmp["MonthNum"] = tmp["OrderDate"].dt.month
        tmp["MonthName"] = tmp["OrderDate"].dt.strftime("%b")
        heat = tmp.pivot_table(index="MonthName", columns="Market", values="SLA_Breach", aggfunc="mean")*100
        # order months Jan..Dec
        month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        heat = heat.reindex(month_order)

        fig_heat = px.imshow(
            heat.fillna(0),
            aspect="auto",
            color_continuous_scale="Reds",
            labels=dict(color="Late %")
        )
        fig_style(fig_heat, h=280)
        st.plotly_chart(fig_heat, use_container_width=True)

        # CO2e proxy monthly trend
        monthly = f.set_index("OrderDate")["Sales"].resample("MS").sum()
        co2 = (monthly * co2_factor).rename("CO2e (kg)").reset_index()
        fig_co2 = px.area(co2, x="OrderDate", y="CO2e (kg)", color_discrete_sequence=["#BFBFBF"])
        fig_style(fig_co2, h=220)
        st.plotly_chart(fig_co2, use_container_width=True)
        st.caption("Seasonality of Late % by Market + CO₂e proxy trend (supports SDG13 via mode/expedite reduction).")

    st.markdown("<div class='space'></div>", unsafe_allow_html=True)

    # Impact panel — quick SDG tie-in, computed from current filter
    total_sales = float(f["Sales"].sum()) if len(f) else 0.0
    on_time = 1.0 - (f["is_late"].mean() if len(f) else 0.0)
    margin = (f["Order Profit Per Order"].sum()/max(total_sales,1))*100 if total_sales else 0.0

    k1,k2,k3 = st.columns(3)
    k1.metric("On-Time (now)", f"{on_time*100:,.1f}%")
    k2.metric("Margin % (now)", f"{margin:,.1f}%")
    k3.metric("CO₂e proxy (last 12M)", f"{(monthly.tail(12).sum()*co2_factor):,.0f} kg")

    st.caption("Focus on the markets (late%), categories (high-sales/low-margin), and cities (hotspots) above to lift SDG-aligned outcomes.")

# ---------- Dispatch ----------
i = st.session_state.slide_index
st.markdown(f"### {SLIDES[i]}")

if   i == 0: slide_1_kpis()
elif i == 1: slide_2_ops()
elif i == 2: slide_3_composition()
elif i == 3: slide_4_map()
elif i == 4: slide_5_whatif()
elif i == 5: slide_6_forecast()
elif i == 6: slide_7_olap()
else:         slide_8_sdg()

st.markdown("<div class='bigspace'></div>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("<div class='space'></div>", unsafe_allow_html=True)

# Bottom nav (also synced)
b1, _, b2 = st.columns([1, 6, 1])
with b1:
    if st.button("◀ Previous", use_container_width=True, key="bottom_prev"): prev_slide()
with b2:
    if st.button("Next ▶", use_container_width=True, key="bottom_next"): next_slide()
st.markdown("<div class='bigspace'></div>", unsafe_allow_html=True)
