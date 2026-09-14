import streamlit as st
import random
import pandas as pd
from datetime import datetime

# Configure the web browser page parameters completely automatically
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
    # 📊 Historical dataframe database table memory storage array
    st.session_state.df_history = pd.DataFrame(columns=["Timestamp", "Status", "Temperature", "Voltage", "Risk_Level"])

# 🖥️ VISUAL DISPLAY ARCHITECTURE: THE WEB GRAPHICS LAYOUT
st.title("🏭 SCADA Master Control Dashboard Node")
st.markdown("---")

# Layout Configuration: Split the screen into two large panels
col_left, col_right = st.columns([2, 1])

with col_right:
    st.subheader("⚙️ Safety Parameters Configuration")
    st.session_state.max_temp_limit = st.slider(
        "Maximum Allowed Temperature Limit (°C)",
        min_value=60, max_value=120,
        value=st.session_state.max_temp_limit
    )

    st.markdown("### Control Interface Controls")
    if st.button("🚀 Execute Live Telemetry Query Pass", use_container_width=True):
        st.session_state.total_scans += 1
        st.session_state.current_temp = random.randint(50, 110)
        st.session_state.current_volt = random.uniform(220.0, 245.0)

        # Evaluate threshold logic against our live web slider value
        if st.session_state.current_temp > st.session_state.max_temp_limit:
            st.session_state.status_code = "[ERR-500]"
            st.session_state.alert_type = "critical"
            risk = "CRITICAL"
        elif st.session_state.current_volt < 225.0:
            st.session_state.status_code = "[WARN-404]"
            st.session_state.alert_type = "warning"
            risk = "HIGH"
        else:
            st.session_state.status_code = "[OK-200]"
            st.session_state.alert_type = "nominal"
            st.session_state.nominal_scans += 1
            risk = "NONE"

        # Construct a dictionary log entry row for this scan cycle
        new_row = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Status": st.session_state.status_code,
            "Temperature": st.session_state.current_temp,
            "Voltage": round(st.session_state.current_volt, 2),
            "Risk_Level": risk
        }

        # Inject the new log entry dictionary directly into the Pandas frame history
        st.session_state.df_history = pd.concat([st.session_state.df_history, pd.DataFrame([new_row])], ignore_index=True)

    st.markdown("---")
    st.markdown("### 📥 Compliance Data Exporter")

    # NEW: Automated spreadsheet generator block
    if not st.session_state.df_history.empty:
        # Convert our live Pandas table memory grid into a clean raw text CSV string data sheet
        csv_data = st.session_state.df_history.to_csv(index=False).encode('utf-8')

        # Render the direct file exporter button widget onto the page layout
        st.download_button(
            label="💾 Download Shift Data Log Sheet (.CSV)",
            data=csv_data,
            file_name=f"SCADA_Shift_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("Run telemetry passes first to generate an exportable database sheet.")

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

    st.markdown("### Operational Response Feedback System")
    if st.session_state.alert_type == "critical":
        st.error(f"🚨 CRITICAL ALERT {st.session_state.status_code}: Core Overheating detected! Temperature at {st.session_state.current_temp}°C crosses threshold barrier limit.")
    elif st.session_state.alert_type == "warning":
        st.warning(f"⚠️ STABILITY WARNING {st.session_state.status_code}: Low line voltage input fluctuation detected ({st.session_state.current_volt:.2f}V). Check phase breakers.")
    else:
        st.success(f"✅ STATUS {st.session_state.status_code}: System Nominal. Asset running at peak output efficiency limits.")

    # Render a clean, interactive data preview grid block directly on the web page layout view
    st.markdown("### Live Operations History Log Preview")
    st.dataframe(st.session_state.df_history.tail(10), use_container_width=True)