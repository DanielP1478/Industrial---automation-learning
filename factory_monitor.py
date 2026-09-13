import streamlit as st
import random
import os
from datetime import datetime

# Automatically configure the web browser viewport layout parameters
st.set_page_config(page_title="Autonomous SCADA Monitor", page_icon="⚙️", layout="wide")

# Initialize persistent memory structures inside the web browser session memory
if "total_scans" not in st.session_state:
    st.session_state.total_scans = 0
    st.session_state.nominal_scans = 0
    st.session_state.max_temp_limit = 100
    st.session_state.current_temp = 75
    st.session_state.current_volt = 230.0
    st.session_state.status_code = "[OK-200]"
    st.session_state.alert_type = "nominal"
    st.session_state.history = []  # 📊 Historical list data store for the live view table

# 🖥️ VISUAL DISPLAY ARCHITECTURE: THE WEB GRAPHICS LAYOUT
st.title("🏭 SCADA Autonomous Control Dashboard")
st.markdown("---")

# Layout Configuration: Split the screen into two large panels
col_left, col_right = st.columns([2, 1])
with col_right:
    st.subheader("⚙️ Safety Parameters Configuration")
    # Interactive Slider Widget: Lets the user drag a dial to change safety thresholds live!
    st.session_state.max_temp_limit = st.slider(
        "Maximum Allowed Temperature Limit (°C)", 
        min_value=60, max_value=120, 
        value=st.session_state.max_temp_limit
    )

    st.markdown("### System Log Configuration Summary")
    st.info(f"Monitoring Array: Active\nTarget Node: CNC_Assembly_Robot_1\nRules Engine: Local Database Buffer")

# ⏱️ AUTOMATED BACKGROUND FRAGMENT ENGINE LOOP
# This specific component tells the browser to run this function every 2 seconds completely hands-free!
@st.fragment(run_every=2)
def autonomous_telemetry_loop():
    # 1. Run real-time background sensor simulations
    temperature = random.randint(50, 110)
    voltage = random.uniform(220.0, 245.0)
    timestamp = datetime.now().strftime("%H:%M:%S")

    st.session_state.total_scans += 1
    st.session_state.current_temp = temperature
    st.session_state.current_volt = voltage
# Evaluate dynamic rules against your live slider threshold variables
    if temperature > st.session_state.max_temp_limit:
        st.session_state.status_code = "[ERR-500]"
        st.session_state.alert_type = "critical"
    elif voltage < 225.0:
        st.session_state.status_code = "[WARN-404]"
        st.session_state.alert_type = "warning"
    else:
        st.session_state.status_code = "[OK-200]"
        st.session_state.alert_type = "nominal"
        st.session_state.nominal_scans += 1

# Append fresh telemetry snapshots directly to our history chart tracking storage lists
    st.session_state.history.append(f"[{timestamp}] CODE: {st.session_state.status_code} | T: {temperature}°C | V: {voltage:.2f}V")

# Keep historical logs constrained to the last 8 entries for smooth display layouts
    if len(st.session_state.history) > 8:
        st.session_state.history.pop(0)
# Execute the autonomous background container loop
with col_left:
    autonomous_telemetry_loop()

    st.subheader("📊 Live Asset Telemetry Stream (Refreshing every 2s)")

# Calculate live operational safety efficiency score on the fly
    if st.session_state.total_scans > 0:
        efficiency = (st.session_state.nominal_scans / st.session_state.total_scans) * 100
    else:
        efficiency = 100.0

    # Render clean visual dashboard summary metric cards
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Asset Core Temperature", f"{st.session_state.current_temp} °C")
    m_col2.metric("Line Voltage Input", f"{st.session_state.current_volt:.2f} V")
    m_col3.metric("OEE Operational Efficiency Score", f"{efficiency:.1f}%")

    st.markdown("### Operational Response Feedback System")

# Dynamic Banner Alerts: Flash matching colors completely automatically based on real metrics
    if st.session_state.alert_type == "critical":
        st.error(f"🚨 CRITICAL ALERT {st.session_state.status_code}: Core Overheating detected! Temperature at {st.session_state.current_temp}°C crosses threshold barrier limit.")
    elif st.session_state.alert_type == "warning":
        st.warning(f"⚠️ STABILITY WARNING {st.session_state.status_code}: Low line voltage input fluctuation detected ({st.session_state.current_volt:.2f}V). Check phase breakers.")
    else:
        st.success(f"✅ STATUS {st.session_state.status_code}: System Nominal. Asset running at peak output efficiency limits.")

    # 📊 NEW VISUAL ELEMENT: Historical Log Table display view right on the webpage panel!
    st.markdown("### Live Telemetry Timeline History Feed")
    for log_entry in reversed(st.session_state.history):
        st.text(log_entry)