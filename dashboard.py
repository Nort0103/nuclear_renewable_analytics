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

except sqlite3.OperationalError:
    st.error(
        "Database not found. Please ensure the pipeline container has run successfully.")
