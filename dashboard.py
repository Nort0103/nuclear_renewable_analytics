import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Energy Analytics Platform",
                   page_icon="⚡", layout="wide")

st.title("⚡ Energy Analytics Platform: Era Comparison")
st.markdown("### 2005 (Nuclear Peak) vs. 2026 (Renewable Transition)")
st.markdown(
    "Comparing system-level performance, EROI, and LCOE across two distinct energy paradigms.")

# 2. Database Connection & Math


@st.cache_data
def load_data():
    """Connects to SQLite, loads data, and calculates LCOE upfront."""
    conn = sqlite3.connect("energy_platform.db")
    df_gen = pd.read_sql_query("SELECT * FROM generation_sources", conn)
    df_econ = pd.read_sql_query("SELECT * FROM economic_parameters", conn)
    conn.close()

    # Calculate Dynamic LCOE for all data at once
    if not df_econ.empty:
        df_econ['total_cost'] = df_econ['capex_per_mw'] + \
            (df_econ['opex_annual_per_mw'] * df_econ['lifespan_years'])
        df_econ['total_mwh'] = 1 * 8760 * \
            df_econ['capacity_factor'] * df_econ['lifespan_years']
        df_econ['lcoe_per_mwh'] = df_econ['total_cost'] / df_econ['total_mwh']

    return df_gen, df_econ

# --- HELPER FUNCTION FOR CLEAN CODE ---


def draw_era_metrics(scenario_name, df_gen, df_econ, title_prefix):
    """Filters data by scenario and draws the three core charts."""
    # Filter data for the specific era
    df_g = df_gen[df_gen['scenario'] == scenario_name]
    df_e = df_econ[df_econ['scenario'] == scenario_name]

    # Standardized colors
    color_map = {"nuclear": "#e74c3c",
                 "onshore_wind": "#3498db", "solar_pv": "#f1c40f"}

    # 1. Generation Chart
    fig_gen = px.bar(df_g, x="technology", y="generation_mw", color="technology",
                     text_auto='.2s', title=f"{title_prefix}: Actual Generation (MW)",
                     color_discrete_map=color_map)
    st.plotly_chart(fig_gen, use_container_width=True,
                    key=f"gen_{scenario_name}")

    # 2. LCOE Chart
    fig_lcoe = px.bar(df_e, x="technology", y="lcoe_per_mwh", color="technology",
                      text_auto='.2f', title=f"{title_prefix}: LCOE (€/MWh)",
                      color_discrete_map=color_map)
    st.plotly_chart(fig_lcoe, use_container_width=True,
                    key=f"lcoe_{scenario_name}")

    # 3. EROI Chart
    fig_eroi = px.bar(df_e, x="technology", y="eroi_baseline", color="technology",
                      text_auto=True, title=f"{title_prefix}: Energy Return on Investment",
                      color_discrete_map=color_map)
    st.plotly_chart(fig_eroi, use_container_width=True,
                    key=f"eroi_{scenario_name}")


# 3. Main Dashboard Layout
try:
    df_generation, df_economics = load_data()

    # Split the screen into two massive columns
    col_2005, col_2026 = st.columns(2)

    # LEFT SIDE: 2005
    with col_2005:
        st.header("⚛️ 2005: Nuclear Peak")
        st.markdown("*High baseload, highly amortized legacy assets.*")
        draw_era_metrics('2005_nuclear_peak', df_generation,
                         df_economics, "2005")

    # RIGHT SIDE: 2026
    with col_2026:
        st.header("🌬️ 2026: Renewable Era")
        st.markdown("*High installed capacity, highly variable output.*")
        draw_era_metrics('2026_renewable_era',
                         df_generation, df_economics, "2026")

    # ==========================================
    # PHASE 5: NUCLEAR REVIVAL PROJECTION
    # ==========================================
    st.markdown("---")
    st.subheader("🔮 Financial Projection: Nuclear Revival Costs")
    st.markdown("Analysis of Capital Expenditure (CAPEX) and Return on Investment (ROI) required to build **21,000 MW** of new nuclear capacity (returning to 2005 levels) under modern economic conditions.")

    # Inputs for modern Gen III+ Nuclear
    modern_nuclear_capex_mw = 10000000
    target_capacity_mw = 21000
    market_price_mwh = 80
    opex_annual_mw = 150000
    capacity_factor = 0.90

    # Math Model
    total_investment = modern_nuclear_capex_mw * target_capacity_mw
    annual_generation_mwh = target_capacity_mw * 8760 * capacity_factor
    annual_revenue = annual_generation_mwh * market_price_mwh
    annual_opex_total = opex_annual_mw * target_capacity_mw
    annual_profit = annual_revenue - annual_opex_total

    if annual_profit > 0:
        payback_years = total_investment / annual_profit
    else:
        payback_years = float('inf')

    # Visualization
    col7, col8, col9 = st.columns(3)

    with col7:
        st.metric(label="Required Investment (CAPEX)",
                  value=f"€ {total_investment / 1e9:,.1f} Billion")
        st.caption(f"Based on €{modern_nuclear_capex_mw/1e6:,.1f}M per MW")

    with col8:
        st.metric(label="Estimated Payback Period",
                  value=f"{payback_years:,.1f} Years")
        st.caption(f"At wholesale price of €{market_price_mwh}/MWh")

    with col9:
        st.metric(label="Annual Profit (Pre-Tax)",
                  value=f"€ {annual_profit / 1e9:,.2f} Billion")
        st.caption("Revenue minus Operational Expenses (OPEX)")

    st.info("**Engineering Insight:** Building new nuclear units requires colossal upfront capital compared to operating amortized legacy plants. Beyond the massive CAPEX, the long construction cycle (10-15 years per unit) freezes capital without generating power.")

except sqlite3.OperationalError:
    st.error(
        "Database not found. Please ensure the pipeline container has run successfully.")
