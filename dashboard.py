import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Energy Analytics Platform",
                   page_icon="⚡", layout="wide")

st.title("⚡ Energy Analytics Platform")
st.markdown("### Nuclear vs. Renewable Energy Performance Metrics")
st.markdown("This dashboard analyzes LCOE (Levelized Cost of Energy) and EROI (Energy Return on Investment) across different energy sources.")

# 2. Database Connection


@st.cache_data
def load_data():
    """Connects to the SQLite DB and loads data into Pandas DataFrames."""
    conn = sqlite3.connect("energy_platform.db")

    # Fetch tables
    df_gen = pd.read_sql_query("SELECT * FROM generation_sources", conn)
    df_econ = pd.read_sql_query("SELECT * FROM economic_parameters", conn)

    conn.close()
    return df_gen, df_econ


# 3. Load and Display Data
try:
    df_generation, df_economics = load_data()

    # Create two columns for layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Economic & Performance Baselines")
        st.dataframe(df_economics, use_container_width=True)

    with col2:
        st.subheader("Current Generation (MW) by Technology")
        if not df_generation.empty:
            # Create a Plotly bar chart
            fig = px.bar(
                df_generation,
                x="technology",
                y="generation_mw",
                color="technology",
                text_auto=True,
                color_discrete_map={
                    "nuclear": "#e74c3c",
                    "onshore_wind": "#3498db",
                    "solar_pv": "#f1c40f"
                }
            )
            fig.update_layout(xaxis_title="Energy Source",
                              yaxis_title="Generation (MW)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Waiting for data pipeline...")

    # ==========================================
    # RESTORED: EROI & CAPEX SECTION
    # ==========================================
    st.markdown("---")
    st.subheader("Advanced Metrics: EROI & Capital Costs")

    col3, col4 = st.columns(2)

    with col3:
        if not df_economics.empty:
            fig_eroi = px.bar(
                df_economics,
                x="technology",
                y="eroi_baseline",
                color="technology",
                text_auto=True,
                title="Energy Return on Investment (EROI)",
                color_discrete_map={
                    "nuclear": "#e74c3c",
                    "onshore_wind": "#3498db",
                    "solar_pv": "#f1c40f"
                }
            )
            st.plotly_chart(fig_eroi, use_container_width=True)

    with col4:
        if not df_economics.empty:
            fig_capex = px.bar(
                df_economics,
                x="technology",
                y="capex_per_mw",
                color="technology",
                text_auto='.2s',
                title="Capital Expenditure (CAPEX) per MW (€)",
                color_discrete_map={
                    "nuclear": "#e74c3c",
                    "onshore_wind": "#3498db",
                    "solar_pv": "#f1c40f"
                }
            )
            st.plotly_chart(fig_capex, use_container_width=True)

    # ==========================================
    # PHASE 4: DYNAMIC LCOE CALCULATION
    # ==========================================
    st.markdown("---")
    st.subheader("Dynamic LCOE (Levelized Cost of Energy) Calculation")

    if not df_economics.empty:
        # Create a copy for calculations to keep the original dataframe clean
        df_lcoe = df_economics.copy()

        # Math Step 1: Total Cost per MW over lifespan (CAPEX + Lifetime OPEX)
        df_lcoe['total_cost'] = df_lcoe['capex_per_mw'] + \
            (df_lcoe['opex_annual_per_mw'] * df_lcoe['lifespan_years'])

        # Math Step 2: Total Energy (MWh) per MW over lifespan (8760 hours/year * Capacity Factor * Lifespan)
        df_lcoe['total_mwh'] = 1 * 8760 * \
            df_lcoe['capacity_factor'] * df_lcoe['lifespan_years']

        # Math Step 3: Final LCOE (€ / MWh)
        df_lcoe['lcoe_per_mwh'] = df_lcoe['total_cost'] / df_lcoe['total_mwh']

        # Display Results
        col5, col6 = st.columns(2)

        with col5:
            st.markdown("**Calculated Financials**")
            # Select specific columns to show
            display_df = df_lcoe[['technology',
                                  'total_cost', 'total_mwh', 'lcoe_per_mwh']]
            st.dataframe(display_df, use_container_width=True)

        with col6:
            # Render LCOE Chart
            fig_lcoe = px.bar(
                df_lcoe,
                x="technology",
                y="lcoe_per_mwh",
                color="technology",
                text_auto='.2f',
                title="Calculated LCOE (€/MWh)",
                color_discrete_map={
                    "nuclear": "#e74c3c",
                    "onshore_wind": "#3498db",
                    "solar_pv": "#f1c40f"
                }
            )
            st.plotly_chart(fig_lcoe, use_container_width=True)

# The exception handler is now correctly placed at the very end
except sqlite3.OperationalError:
    st.error(
        "Database not found. Please ensure the pipeline container has run successfully.")
