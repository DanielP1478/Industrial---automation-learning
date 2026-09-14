import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Enterprise SCADA Fleet Monitoring Center", layout="wide")

st.markdown("""
<style>
    .metric-card { background-color: #161A22; border: 1px solid #2D3748; padding: 15px; border-radius: 8px; }
    .fault-critical { background-color: #3C1A1A; border-left: 5px solid #E53E3E; padding: 12px; color: #FED7D7; font-weight: bold; }
    .status-normal { color: #48BB78; font-weight: bold; }
    .status-fault { color: #E53E3E; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

if 'fault_cleared' not in st.session_state: st.session_state.fault_cleared = False
if 'clear_timestamp' not in st.session_state: st.session_state.clear_timestamp = None

@st.cache_data
def generate_historical_telemetry():
    now = datetime.datetime.now()
    timestamps = pd.date_range(end=now, periods=60, freq='min')
    return pd.DataFrame({
        'Timestamp': timestamps,
        'CNC_Mill_Temp_C': np.random.normal(loc=72, scale=3, size=60),
        'Industrial_Freezer_Temp_C': np.random.normal(loc=-18, scale=1.5, size=60),
        'Conveyor_Belt_Speed_ms': np.random.normal(loc=1.5, scale=0.1, size=60)
    })

data_stream = generate_historical_telemetry()
latest_metrics = data_stream.iloc[-1]

st.sidebar.title("🎛️ Fleet Control Panel")
safety_threshold = st.sidebar.slider("Critical Temperature Threshold (°C)", 60, 100, 85)

st.title("🏭 Enterprise SCADA Fleet Monitoring Center")
st.caption(f"Environment: Python 3.14 Compliance | Ref Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

current_cnc_temp = latest_metrics['CNC_Mill_Temp_C']
is_breached = current_cnc_temp > safety_threshold

if is_breached and not st.session_state.fault_cleared:
    st.markdown(f"<div class='fault-critical'>🛑 CRITICAL THERMAL FAULT [ERR-500]: Asset breached safety envelope!</div>", unsafe_allow_html=True)
    if st.button("Acknowledge & Force Clear Latched Fault"):
        st.session_state.fault_cleared = True
        st.session_state.clear_timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        st.sidebar.button("Rerun System")
elif st.session_state.fault_cleared:
    st.success(f"✅ Latched Fault Overridden at {st.session_state.clear_timestamp}.")
    if st.button("Reset System Interlock Latches"):
        st.session_state.fault_cleared = False
        st.session_state.clear_timestamp = None

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<div class='metric-card'>🤖 CNC Mill Node", unsafe_allow_html=True)
    st.metric("Core Temp", f"{current_cnc_temp:.2f} °C")
    st.markdown("</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='metric-card'>❄️ Industrial Freezer", unsafe_allow_html=True)
    st.metric("Internal Temp", f"{latest_metrics['Industrial_Freezer_Temp_C']:.2f} °C")
    st.markdown("</div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='metric-card'>📦 Conveyor Subsystem", unsafe_allow_html=True)
    st.metric("Linear Velocity", f"{latest_metrics['Conveyor_Belt_Speed_ms']:.2f} m/s")
    st.markdown("</div>", unsafe_allow_html=True)

view_tab1, view_tab2 = st.tabs(["📊 Live Telemetry Trend Plot", "🗄️ Raw SCADA Data Registers"])
with view_tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_stream['Timestamp'], y=data_stream['CNC_Mill_Temp_C'], name='CNC Temp'))
    fig.add_trace(go.Scatter(x=data_stream['Timestamp'], y=data_stream['Industrial_Freezer_Temp_C'], name='Freezer Temp'))
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
with view_tab2:
    st.dataframe(data_stream)