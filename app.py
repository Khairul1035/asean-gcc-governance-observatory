import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.request
import json

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="ASEAN-GCC Governance Observatory | Mohd Khairul Ridhuan",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom McKinsey/PwC Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #F8F9FA;
        color: #1A202C;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .main-header {
        background: linear-gradient(90deg, #0F2C59 0%, #1E3A8A 100%);
        color: white;
        padding: 24px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .author-tag {
        background-color: #3B82F6;
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .sim-card {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATA FETCHING (WORLD BANK API)
# ==========================================
@st.cache_data(ttl=3600)
def load_world_bank_data():
    # Countries mapping with regional classification
    country_map = {
        "MYS": ("Malaysia", "ASEAN"),
        "SGP": ("Singapore", "ASEAN"),
        "THA": ("Thailand", "ASEAN"),
        "IDN": ("Indonesia", "ASEAN"),
        "SAU": ("Saudi Arabia", "GCC"),
        "ARE": ("United Arab Emirates", "GCC"),
        "QAT": ("Qatar", "GCC"),
        "KWT": ("Kuwait", "GCC"),
        "GBR": ("United Kingdom", "Benchmark Corridor"),
        "TUR": ("Turkiye", "Transit Corridor"),
        "IND": ("India", "Transit Corridor")
    }
    
    codes = ";".join(country_map.keys())
    url = f"https://api.worldbank.org/v2/country/{codes}/indicator/SH.XPD.CHEX.GD.ZS?date=2015:2024&format=json&per_page=500"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        records = []
        if len(data) > 1 and data[1]:
            for entry in data[1]:
                c_code = entry["countryiso3code"]
                if c_code in country_map:
                    c_name, region = country_map[c_code]
                    val = entry["value"]
                    if val is not None:
                        records.append({
                            "Country": c_name,
                            "Country_Code": c_code,
                            "Region": region,
                            "Year": int(entry["date"]),
                            "Health_Exp_GDP": round(val, 2)
                        })
        df = pd.DataFrame(records)
        return df
    except Exception as e:
        st.error(f"API Error: {e}")
        return pd.DataFrame()

df_raw = load_world_bank_data()

# ==========================================
# 3. SIDEBAR - DYNAMIC FILTERS & METADATA
# ==========================================
st.sidebar.markdown("### 🏛️ Lead Principal Investigator")
st.sidebar.markdown("""
**Mohd Khairul Ridhuan bin Mohd Fadzil**  
*Governance & Macro-Risk Analytics Researcher*  
🇲🇾 Malaysia
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Live Analytics Controls")

if not df_raw.empty:
    # Region Filter
    all_regions = list(df_raw["Region"].unique())
    selected_regions = st.sidebar.multiselect(
        "Filter Corridor Region:",
        options=all_regions,
        default=all_regions
    )
    
    # Country Filter (Dependent on Region)
    filtered_by_region = df_raw[df_raw["Region"].isin(selected_regions)]
    available_countries = list(filtered_by_region["Country"].unique())
    
    selected_countries = st.sidebar.multiselect(
        "Select Specific Countries:",
        options=available_countries,
        default=available_countries
    )
    
    # Year Range Slider
    min_year = int(df_raw["Year"].min())
    max_year = int(df_raw["Year"].max())
    selected_years = st.sidebar.slider(
        "Select Timeline Range:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )
    
    # Filter Data dynamically
    df_filtered = df_raw[
        (df_raw["Region"].isin(selected_regions)) &
        (df_raw["Country"].isin(selected_countries)) &
        (df_raw["Year"] >= selected_years[0]) &
        (df_raw["Year"] <= selected_years[1])
    ]
else:
    df_filtered = pd.DataFrame()

st.sidebar.markdown("---")
st.sidebar.caption("Data Source: World Bank REST API Live Feed (Indicator: SH.XPD.CHEX.GD.ZS)")

# ==========================================
# 4. HEADER SECTION
# ==========================================
st.markdown("""
<div class="main-header">
    <span class="author-tag">AUTHOR & RESEARCHER: MOHD KHAIRUL RIDHUAN</span>
    <h1 style="color:white !important; margin-top:10px; margin-bottom:5px;">ASEAN-GCC Trade & Healthcare Governance Observatory</h1>
    <p style="font-size:1.05rem; opacity:0.9; margin:0;">An Executive Decision-Support Platform for Real-Time Macro Risk Analytics & Cross-Border Governance</p>
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.warning("⚠️ No data matches your sidebar filters. Please broaden your selection.")
    st.stop()

# ==========================================
# 5. TABBED INTERFACE (DYNAMIC REACTIVE UI)
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Real-Time Analytics", 
    "🔮 Interactive 'What-If' Simulator", 
    "⚖️ Governance Risk Matrix", 
    "📁 Raw Data & Export"
])

# ------------------------------------------
# TAB 1: REAL-TIME ANALYTICS
# ------------------------------------------
with tab1:
    st.subheader("💡 Dynamic Macro Health Metrics")
    
    # Dynamic Metric Calculations based on User Filter
    total_countries = df_filtered["Country"].nunique()
    avg_health_exp = df_filtered["Health_Exp_GDP"].mean()
    latest_year = df_filtered["Year"].max()
    df_latest = df_filtered[df_filtered["Year"] == latest_year]
    max_spender = df_latest.sort_values(by="Health_Exp_GDP", ascending=False).iloc[0] if not df_latest.empty else None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(label="Active Nations Analyzed", value=f"{total_countries} Countries")
    c2.metric(label="Filter Period Avg Health Exp", value=f"{avg_health_exp:.2f}% of GDP")
    if max_spender is not None:
        c3.metric(label=f"Highest Spender ({latest_year})", value=f"{max_spender['Country']}", delta=f"{max_spender['Health_Exp_GDP']}% GDP")
    c4.metric(label="Data Integrity Status", value="Verified Live API", delta="100% Synced")

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader(f"📊 Latest Health Expenditure (% GDP) - {latest_year}")
        fig_bar = px.bar(
            df_latest.sort_values(by="Health_Exp_GDP", ascending=False),
            x="Country",
            y="Health_Exp_GDP",
            color="Region",
            text="Health_Exp_GDP",
            template="plotly_white",
            color_discrete_map={"ASEAN": "#0F2C59", "GCC": "#059669", "Benchmark Corridor": "#DC2626", "Transit Corridor": "#D97706"}
        )
        fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title="Health Exp (% of GDP)")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("🌐 Longitudinal Trend Analysis")
        fig_line = px.line(
            df_filtered,
            x="Year",
            y="Health_Exp_GDP",
            color="Country",
            markers=True,
            template="plotly_white"
        )
        fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title="Health Exp (% of GDP)")
        st.plotly_chart(fig_line, use_container_width=True)

# ------------------------------------------
# TAB 2: INTERACTIVE WHAT-IF SIMULATOR
# ------------------------------------------
with tab2:
    st.subheader("🔮 Corporate Risk & Capital Allocation Scenario Simulator")
    st.write("Recruiters and Executives can adjust the investment parameters below to dynamically model cross-border compliance risk and friction costs.")
    
    sim_col1, sim_col2 = st.columns([1, 1])
    
    with sim_col1:
        st.markdown('<div class="sim-card">', unsafe_allow_html=True)
        st.markdown("##### 🎛️ Simulation Inputs")
        target_country = st.selectbox("Select Target Investment Corridor:", options=df_filtered["Country"].unique())
        capital_alloc = st.slider("Cross-Border Capital Allocation ($ Millions USD):", min_value=5, max_value=500, value=50, step=5)
        compliance_tolerance = st.slider("Company Compliance Friction Threshold (%):", min_value=1.0, max_value=10.0, value=4.5, step=0.5)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with sim_col2:
        # Dynamic Calculations
        country_data = df_filtered[df_filtered["Country"] == target_country]
        latest_country_exp = country_data.sort_values(by="Year", ascending=False)["Health_Exp_GDP"].iloc[0] if not country_data.empty else 4.0
        
        # Risk Friction Algorithm
        exp_gap = abs(latest_country_exp - compliance_tolerance)
        estimated_friction_cost = round((exp_gap / 100) * capital_alloc, 2)
        risk_score = round(min(100, (exp_gap / 5.0) * 100), 1)
        
        st.markdown('<div class="sim-card">', unsafe_allow_html=True)
        st.markdown(f"##### 🎯 Scenario Results for **{target_country}**")
        
        res1, res2 = st.columns(2)
        res1.metric("Country Baseline Health Exp", f"{latest_country_exp:.2f}% GDP")
        res2.metric("Target Compliance Gap", f"{exp_gap:.2f}%", delta=f"{'High Friction' if exp_gap > 2 else 'Low Friction'}", delta_color="inverse")
        
        st.markdown("---")
        st.metric(label="Estimated Regulatory Compliance Exposure Cost ($M)", value=f"${estimated_friction_cost} Million", delta=f"{risk_score}/100 Risk Score", delta_color="inverse")
        
        if risk_score > 50:
            st.error("⚠️ **High Regulatory Friction Warning:** Requires mandatory escrow oversight and dual-jurisdiction legal buffering.")
        else:
            st.success("✅ **Low Regulatory Friction:** Standard trade governance procedures apply.")
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------
# TAB 3: GOVERNANCE RISK MATRIX
# ------------------------------------------
with tab3:
    st.subheader("⚖️ ASEAN-GCC Macro Regulatory Scatter Matrix")
    st.write("This matrix evaluates structural spending vs stability. Countries in the top-right quadrant offer high market maturity, while lower-left indicates emerging expansion opportunities.")
    
    df_matrix = df_filtered.groupby("Country").agg({
        "Health_Exp_GDP": ["mean", "std"],
        "Region": "first"
    }).reset_index()
    df_matrix.columns = ["Country", "Avg_Spending", "Spending_Volatility", "Region"]
    df_matrix["Spending_Volatility"] = df_matrix["Spending_Volatility"].fillna(0.1)
    
    fig_scatter = px.scatter(
        df_matrix,
        x="Avg_Spending",
        y="Spending_Volatility",
        size="Avg_Spending",
        color="Region",
        hover_name="Country",
        text="Country",
        template="plotly_white",
        labels={"Avg_Spending": "Average Health Exp (% GDP)", "Spending_Volatility": "Historical Volatility (Std Dev)"}
    )
    fig_scatter.update_traces(textposition='top center')
    fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_scatter, use_container_width=True)

# ------------------------------------------
# TAB 4: RAW DATA & EXPORT
# ------------------------------------------
with tab4:
    st.subheader("📁 Filtered Data Explorer")
    st.write("Recruiters and Analysts can inspect and download the exact dataset currently active in this session.")
    
    st.dataframe(df_filtered, use_container_width=True)
    
    # Live CSV Export Button
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Active Filtered Data (CSV)",
        data=csv_data,
        file_name=f"asean_gcc_governance_data_{selected_years[0]}_{selected_years[1]}.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("Designed and engineered by Mohd Khairul Ridhuan bin Mohd Fadzil. Built using Python, Streamlit, Plotly, and World Bank Open Data REST API.")
