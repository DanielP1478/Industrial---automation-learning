import streamlit as st
import random
import os
from datetime import datetime

# Configure the web browser page parameters automatically
st.set_page_config(page_title="SCADA Asset Monitor", page_icon="⚙️", layout="wide")

# Initialize persistent memory structures inside the web browser's tracking storage
if "total_scans" not in st.session_state:
    st.session_state.total_scans = 0
    st.session_state.nominal_scans = 0
    st.session_state.max_temp_limit = 100
    st.session_state.current_temp = 75
    st.session_state.current_volt = 230.0
    st.session_state.status_code = "[OK-200]"
    st.session_state.alert_type = "nominal"

# 🖥️ VISUAL DISPLAY ARCHITECTURE: THE WEB GRAPHICS LAYOUT
st.title("🏭 SCADA Master Control Dashboard Node")
st.markdown("---")

# Layout Configuration: Split the screen into two large panels
col_left, col_right = st.columns(2)

with col_right:
    st.subheader("⚙️ Safety Parameters Configuration")
    # Interactive Slider Widget: Lets the user drag a dial to change safety thresholds live!
    st.session_state.max_temp_limit = st.slider(
        "Maximum Allowed Temperature Limit (°C)", 
        min_value=60, max_value=120, 
        value=st.session_state.max_temp_limit
    )

    st.markdown("### Control Interface Controls")
    # Action Trigger Button
    if st.button("🚀 Execute Live Telemetry Query Pass", use_container_width=True):
        st.session_state.total_scans += 1
        st.session_state.current_temp = random.randint(50, 110)
        st.session_state.current_volt = random.uniform(220.0, 245.0)

# Evaluate threshold logic against our live web slider value
        if st.session_state.current_temp > st.session_state.max_temp_limit:
            st.session_state.status_code = "[ERR-500]"
            st.session_state.alert_type = "critical"
        elif st.session_state.current_volt < 225.0:
            st.session_state.status_code = "[WARN-404]"
            st.session_state.alert_type = "warning"
        else:
            st.session_state.status_code = "[OK-200]"
            st.session_state.alert_type = "nominal"
            st.session_state.nominal_scans += 1

with col_left:
    st.subheader("📊 Live Asset Telemetry Stream")

# Calculate live efficiency percentage score on the fly
    if st.session_state.total_scans > 0:
        efficiency = (st.session_state.nominal_scans / st.session_state.total_scans) * 100
    else:
        efficiency = 100.0

    # Render clean visual dashboard summary cards across the screen width
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Asset Core Temperature", f"{st.session_state.current_temp} °C")
    m_col2.metric("Line Voltage Input", f"{st.session_state.current_volt:.2f} V")
    m_col3.metric("OEE Operational Efficiency Score", f"{efficiency:.1f}%")

    st.markdown("### Operational Response Feedback System")

# Dynamic Banner Alerts: Flash matching colors based on the tracking state parameters
    if st.session_state.alert_type == "critical":
        st.error(f"🚨 CRITICAL ALERT {st.session_state.status_code}: Core Overheating detected! Temperature at {st.session_state.current_temp}°C crosses threshold barrier limit.")
    elif st.session_state.alert_type == "warning":
        st.warning(f"⚠️ STABILITY WARNING {st.session_state.status_code}: Low line voltage input fluctuation detected ({st.session_state.current_volt:.2f}V). Check phase breakers.")
    else:
        st.success(f"✅ STATUS {st.session_state.status_code}: System Nominal. Asset running at peak output efficiency limits.")

    st.caption(f"Total Telemetry Scanning Logs Recorded on Current Shift: {st.session_state.total_scans}")