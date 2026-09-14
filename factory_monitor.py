import streamlit as st
import random
import pandas as pd
from datetime import datetime

# Automatically configure the web browser viewport layout parameters
st.set_page_config(page_title="SCADA Asset Monitor", page_icon="📈", layout="wide")

# Initialize persistent memory structures inside the web browser's tracking storage
if "total_scans" not in st.session_state:
    st.session_state.total_scans = 0
    st.session_state.nominal_scans = 0
    st.session_state.max_temp_limit = 100
    st.session_state.current_temp = 75
    st.session_state.current_volt = 230.0
    st.session_state.status_code = "[OK-200]"
    st.session_state.alert_type = "nominal"
    # 📈 NEW: Tracking arrays to store historical data rows for the visual timeline graph
    st.session_state.history_records = []

# 🖥️ VISUAL DISPLAY ARCHITECTURE: THE WEB GRAPHICS LAYOUT
st.title("🏭 SCADA Master Control Dashboard Node")
st.markdown("---")

col_left, col_right = st.columns([2, 1]) # Allocates more visual space layout to the graphing panel

with col_right:
    st.subheader("⚙️ Safety Parameters Configuration")
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

        # 📈 Record the historical metrics inside our memory array cache on every single click
        st.session_state.history_records.append({
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Temperature (°C)": st.session_state.current_temp,
            "Voltage (V)": round(st.session_state.current_volt, 1)
        })

with col_left:
    st.subheader("📊 Live Asset Telemetry Stream")

    if st.session_state.total_scans > 0:
        efficiency = (st.session_state.nominal_scans / st.session_state.total_scans) * 100
    else:
        efficiency = 100.0

    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Asset Core Temperature", f"{st.session_state.current_temp} °C")
    m_col2.metric("Line Voltage Input", f"{st.session_state.current_volt:.2f} V")
    m_col3.metric("OEE Operational Efficiency Score", f"{efficiency:.1f}%")

    # 📈 NEW: Convert our historical log cache dictionary rows into a clean Pandas line chart timeline layout
    if st.session_state.history_records:
        st.markdown("### 📈 Real-Time Thermal Trend Tracking Timeline")
        # Format raw cache arrays into dataframes
        df_history = pd.DataFrame(st.session_state.history_records)
        # Renders the line graph right on the user screen layout
        st.line_chart(df_history.set_index("Time")[["Temperature (°C)"]])

    st.markdown("### Operational Response Feedback System")
    if st.session_state.alert_type == "critical":
        st.error(f"🚨 CRITICAL ALERT {st.session_state.status_code}: Core Overheating detected! Temperature at {st.session_state.current_temp}°C crosses threshold barrier limit.")
    elif st.session_state.alert_type == "warning":
        st.warning(f"⚠️ STABILITY WARNING {st.session_state.status_code}: Low line voltage input fluctuation detected ({st.session_state.current_volt:.2f}V). Check phase breakers.")
    else:
        st.success(f"✅ STATUS {st.session_state.status_code}: System Nominal. Asset running at peak output efficiency limits.")

    st.caption(f"Total Telemetry Scanning Logs Recorded on Current Shift: {st.session_state.total_scans}")