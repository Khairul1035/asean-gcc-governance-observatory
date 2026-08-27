import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.request
import json

# 1. Page Configuration
st.set_page_config(
    page_title="ASEAN-GCC Governance Observatory | Mohd Khairul Ridhuan",
    page_icon="🏛️",
    layout="wide"
)

# 2. McKinsey / PwC Light Theme Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #F8F9FA;
        color: #1A202C;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 18px;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    h1, h2, h3 {
        color: #0F2C59 !important;
        font-weight: 600;
    }
    .author-badge {
        background-color: #0F2C59;
        color: #FFFFFF;
        padding: 6px 14px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 500;
        display: inline-block;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar Metadata
st.sidebar.markdown("### 🏛️ Research & Ownership")
st.sidebar.markdown("""
**Lead Researcher:**  
**Mohd Khairul Ridhuan bin Mohd Fadzil**  
*Governance & Risk Analytics Researcher*  
🇲🇾 Malaysia
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📡 Authenticated Data Feed")
st.sidebar.info("Data Source: World Bank Open Data REST API (Indicator: Current Health Exp % GDP)")
st.sidebar.caption("© 2026 Mohd Khairul Ridhuan bin Mohd Fadzil. All rights reserved.")

# 4. Header Section
st.markdown('<div class="author-badge">PRINCIPAL INVESTIGATOR: MOHD KHAIRUL RIDHUAN BIN MOHD FADZIL (MALAYSIA)</div>', unsafe_allow_html=True)
st.title("🏛️ ASEAN-GCC Trade & Healthcare Governance Observatory")
st.caption("Executive Decision Support Platform | Real-Time World Bank Macro Analytics")

# 5. Direct API Fetching from World Bank (Real Data)
@st.cache_data(ttl=3600)
def fetch_world_bank_data():
    countries = "MYS;SGP;THA;IDN;SAU;ARE;QAT;KWT;GBR;TUR;IND"
    url = f"https://api.worldbank.org/v2/country/{countries}/indicator/SH.XPD.CHEX.GD.ZS?date=2015:2024&format=json&per_page=500"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        
    records = []
    if len(data) > 1 and data[1]:
        for entry in data[1]:
            records.append({
                "Country": entry["country"]["value"],
                "Country_Code": entry["countryiso3code"],
                "Year": entry["date"],
                "Health_Expenditure_%_GDP": entry["value"]
            })
    df = pd.DataFrame(records)
    df = df.dropna(subset=["Health_Expenditure_%_GDP"])
    return df

try:
    df = fetch_world_bank_data()

    st.info("""
    **Executive Summary:** Developed by **Mohd Khairul Ridhuan bin Mohd Fadzil**, this observatory synthesizes live macro data directly from the **World Bank Open Data REST API** to establish baseline healthcare governance indicators across ASEAN, GCC, and strategic transit corridors.
    """)

    st.markdown("---")

    # 6. Executive Metrics
    col1, col2, col3 = st.columns(3)
    avg_exp = df["Health_Expenditure_%_GDP"].mean()
    col1.metric(label="Authenticated World Bank Records", value=f"{len(df)} Points", delta="Verified API Feed")
    col2.metric(label="Corridor Avg Health Exp (% GDP)", value=f"{avg_exp:.2f}%", delta="World Bank Baseline")
    col3.metric(label="Monitored Corridors", value="11 Core Nations", delta="ASEAN + GCC + Transit")

    st.markdown("<br>", unsafe_allow_html=True)

    # 7. Visualizations
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 Health Expenditure (% GDP) by Country")
        fig_bar = px.bar(
            df.sort_values(by="Year", ascending=False).groupby("Country").first().reset_index(), 
            x="Country", 
            y="Health_Expenditure_%_GDP", 
            color="Country",
            template="plotly_white",
            labels={"Health_Expenditure_%_GDP": "Health Exp (% GDP)"}
        )
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("🌐 Multi-Year Trend Analysis (2015–2024)")
        fig_line = px.line(
            df, 
            x="Year", 
            y="Health_Expenditure_%_GDP", 
            color="Country",
            template="plotly_white",
            markers=True
        )
        fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_line, use_container_width=True)

    # 8. Data Table
    st.markdown("---")
    st.subheader("📋 Authenticated Data Preview (World Bank API)")
    st.dataframe(df, use_container_width=True)
    
    st.caption("Data Source: World Bank Group (Official REST API Dataset). Synthesized and presented by Mohd Khairul Ridhuan bin Mohd Fadzil (Malaysia).")

except Exception as e:
    st.error(f"Gagal menarik data dari API Bank Dunia: {e}")
