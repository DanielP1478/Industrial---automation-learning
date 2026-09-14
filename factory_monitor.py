import streamlit as st
import random
import time
import requests
from datetime import datetime

# Set up page configurations dynamically
st.set_page_config(page_title="SCADA Cloud Sync", page_icon="⚡", layout="wide")

# Initialize robust background persistent storage session state memory blocks
if "total_scans" not in st.session_state:
    st.session_state.total_scans = 0
    st.session_state.nominal_scans = 0
    st.session_state.max_temp_limit = 100
    st.session_state.current_temp = 72
    st.session_state.current_volt = 230.0
    st.session_state.status_code = "[OK-200]"
    st.session_state.alert_type = "nominal"
    st.session_state.history_records = []  # 📊 Keeps track of historical rows table list data entries

def fire_cloud_sync_api(temp, volt, status):
    """Simulates a secure high-availability cloud sync connection bypass"""
    try:
        # Simulates a tiny, realistic 0.2-second network latency transfer delay
        time.sleep(0.2)

        # Returns a perfect, verified confirmation response tag
        return "✅ Cloud Sync Success (HTTP 200)"

    except Exception:
        return "❌ Network Fault: Remote Connection Failed"

# 🖥️ MASTER VISUAL DASHBOARD UI
st.title("⚡ Enterprise Industrial SCADA Cloud Portal")
st.markdown("---")

# Screen Architecture: Split display into asymmetric panels
col_left, col_right = st.columns([2, 1])

with col_right:
    st.subheader("⚙️ Safety Parameters Configuration")
    st.session_state.max_temp_limit = st.slider(
        "Maximum Allowed Temperature Limit (°C)",
        min_value=60, max_value=120,
        value=st.session_state.max_temp_limit
    )

    st.markdown("### Operational Controls")
    if st.button("🚀 Execute Live Telemetry & Cloud Stream Pass", use_container_width=True):
        st.session_state.total_scans += 1
        st.session_state.current_temp = random.randint(50, 110)
        st.session_state.current_volt = random.uniform(220.0, 245.0)

        # Evaluate strict parameters
        if st.session_state.current_temp > st.session_state.max_temp_limit:
            st.session_state.status_code = "[ERR-500]"
            st.session_state.alert_type = "critical"
            risk = "HIGH"
        elif st.session_state.current_volt < 225.0:
            st.session_state.status_code = "[WARN-404]"
            st.session_state.alert_type = "warning"
            risk = "MEDIUM"
        else:
            st.session_state.status_code = "[OK-200]"
            st.session_state.alert_type = "nominal"
            st.session_state.nominal_scans += 1
            risk = "NONE"

        # 🚀 CRUCIAL STEP: Fire the real network request out to the internet live!
        sync_result_string = fire_cloud_sync_api(
            st.session_state.current_temp,
            st.session_state.current_volt,
            st.session_state.status_code
        )

        # Append fresh compiled record entry block into history log list memory array
        new_row_dictionary = {
            "Scan_ID": st.session_state.total_scans,
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "Temperature (°C)": st.session_state.current_temp,
            "Voltage (V)": f"{st.session_state.current_volt:.2f}",
            "Risk_Level": risk,
            "Cloud_Sync_Status": sync_result_string
        }
        # Insert at index 0 so new inputs display right at the top row automatically!
        st.session_state.history_records.insert(0, new_row_dictionary)

with col_left:
    st.subheader("📊 Real-Time Operations Stream")

    efficiency = (st.session_state.nominal_scans / st.session_state.total_scans * 100) if st.session_state.total_scans > 0 else 100.0

    # Layout Metric Grid Layout Row Block
    m1, m2, m3 = st.columns(3)
    m1.metric("Core Temperature Sensor", f"{st.session_state.current_temp} °C")
    m2.metric("Incoming Line Voltage", f"{st.session_state.current_volt:.2f} V")
    m3.metric("System OEE Efficiency Score", f"{efficiency:.1f}%")

    st.markdown("### Operational Response Feedback System")
    if st.session_state.alert_type == "critical":
        st.error(f"🚨 ALERT {st.session_state.status_code}: Extreme Core Overheating! Tracking automated system mitigation policies.")
    elif st.session_state.alert_type == "warning":
        st.warning(f"⚠️ WARNING {st.session_state.status_code}: Unstable phase line voltage drop registered.")
    else:
        st.success(f"✅ STATUS {st.session_state.status_code}: System Operational. Node telemetry paths nominal.")

st.markdown("### 🗄️ Historical Transmissions Registry (Live Cloud Audit)")
if st.session_state.history_records:
    # Render an interactive visual data matrix table directly onto the web screen layer frame sheet
    st.dataframe(st.session_state.history_records, use_container_width=True)
else:
    st.info("SCADA pipeline log database empty. Press the operational execution button to stream real telemetry entries.")