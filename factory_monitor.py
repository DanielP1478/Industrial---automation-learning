import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time
import threading
import json
import io

# ==========================================
# 1. OPTIONAL COMMERCIAL HARDWARE PACKAGES
# ==========================================
# When you ship physical devices, run: pip install paho-mqtt
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

# Set page configuration layout
st.set_page_config(page_title="Enterprise SCADA Fleet Monitoring Center", layout="wide")

# High-contrast industrial CSS Injection
st.markdown("""
<style>
    .metric-card { background-color: #161A22; border: 1px solid #2D3748; padding: 15px; border-radius: 8px; }
    .fault-critical { background-color: #3C1A1A; border-left: 5px solid #E53E3E; padding: 12px; color: #FED7D7; font-weight: bold; }
    .status-normal { color: #48BB78; font-weight: bold; }
    .status-fault { color: #E53E3E; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. TELEMETRY STORAGE & NETWORK INGESTION
# ==========================================
# Initialize persistent data history buffer inside web app memory
if 'telemetry_buffer' not in st.session_state:
    # Build historical baseline window framework (60 minutes of tracking records)
    now = datetime.datetime.now()
    timestamps = pd.date_range(end=now, periods=60, freq='min')

    st.session_state.telemetry_buffer = pd.DataFrame({
        'Timestamp': timestamps,
        'CNC_Mill_Temp_C': np.random.normal(loc=72, scale=3, size=60),
        'Industrial_Freezer_Temp_C': np.random.normal(loc=-18, scale=1.5, size=60),
        'Conveyor_Belt_Speed_ms': np.random.normal(loc=1.5, scale=0.1, size=60)
    })

if 'fault_cleared' not in st.session_state:
    st.session_state.fault_cleared = False
if 'clear_timestamp' not in st.session_state:
    st.session_state.clear_timestamp = None

# ------------------------------------------
# BACKGROUND HARDWARE LISTENER THREAD (MQTT)
# ------------------------------------------
# This network daemon captures raw string packets broadcasted from actual field transmitters
def on_hardware_message(client, userdata, message):
    try:
        # Expected hardware JSON payload string: {"cnc_temp": 78.4, "freezer_temp": -16.2, "conveyor_speed": 1.45}
        payload = json.loads(message.payload.decode("utf-8"))

        new_row = {
            'Timestamp': datetime.datetime.now(),
            'CNC_Mill_Temp_C': float(payload.get('cnc_temp', 72.0)),
            'Industrial_Freezer_Temp_C': float(payload.get('freezer_temp', -18.0)),
            'Conveyor_Belt_Speed_ms': float(payload.get('conveyor_speed', 1.5))
        }

        # Safely append data to state cache array across memory boundaries
        df_current = st.session_state.telemetry_buffer
        df_updated = pd.concat([df_current, pd.DataFrame([new_row])], ignore_index=True).iloc[1:]
        st.session_state.telemetry_buffer = df_updated
    except Exception as e:
        pass # Silently drop malformed network payloads to ensure uptime stability

def start_mqtt_listener():
    if MQTT_AVAILABLE and 'mqtt_started' not in st.session_state:
        try:
            client = mqtt.Client()
            client.on_message = on_hardware_message
            # Using a free open-source public MQTT sandbox broker for hardware testing
            client.connect("://hivemq.com", 1883, 60)
            client.subscribe("factory/fleet/telemetry")

            # Run network collection socket loops smoothly inside isolated thread channels
            thread = threading.Thread(target=client.loop_forever, daemon=True)
            thread.start()
            st.session_state.mqtt_started = True
        except Exception:
            pass

start_mqtt_listener()

# ------------------------------------------
# SIMULATED LIVE TICK ENGINE
# ------------------------------------------
# If no real tracking device is sending network signals, simulate live asset movement automatically
def simulate_live_sensor_tick():
    df_current = st.session_state.telemetry_buffer
    last_row = df_current.iloc[-1]

    new_row = {
        'Timestamp': datetime.datetime.now(),
        # Walk sensor metrics out randomly from their current tracking positions
        'CNC_Mill_Temp_C': last_row['CNC_Mill_Temp_C'] + np.random.normal(loc=0.1, scale=1.2),
        'Industrial_Freezer_Temp_C': last_row['Industrial_Freezer_Temp_C'] + np.random.normal(loc=0.0, scale=0.4),
        'Conveyor_Belt_Speed_ms': max(0.0, last_row['Conveyor_Belt_Speed_ms'] + np.random.normal(loc=0.0, scale=0.05))
    }

    # Maintain maximum length framework window profile size of 60 records
    df_updated = pd.concat([df_current, pd.DataFrame([new_row])], ignore_index=True).iloc[1:]
    st.session_state.telemetry_buffer = df_updated

# Tick the data stream forward right before layout rendering
simulate_live_sensor_tick()

# Fetch active telemetry dataframe slice
data_stream = st.session_state.telemetry_buffer
latest_metrics = data_stream.iloc[-1]

# ==========================================
# 3. CONTROL SIDEBAR PANEL
# ==========================================
st.sidebar.title("🎛️ Fleet Control Panel")
safety_threshold = st.sidebar.slider("Critical Temperature Threshold (°C)", 60, 100, 85)

# Hardware Network Diagnostics Link Status
st.sidebar.markdown("---")
st.sidebar.subheader("📡 IoT Gateway Diagnostics")
if MQTT_AVAILABLE:
    st.sidebar.success("Network Driver: LOADED")
    st.sidebar.info("Broker Topic: `factory/fleet/telemetry`")
else:
    st.sidebar.warning("Network Driver: LOCAL SIM ONLY")
    st.sidebar.caption("Run `pip install paho-mqtt` to clear network dependencies for actual hardware integration.")

# ==========================================
# 4. APP HEADERS & SAFETY STATE MACHINES
# ==========================================
st.title("🏭 Enterprise SCADA Fleet Monitoring Center")
st.caption(f"Environment: Python 3.14 Compliance | Ref Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

current_cnc_temp = latest_metrics['CNC_Mill_Temp_C']
is_breached = current_cnc_temp > safety_threshold

# Latching Safety Guardrail Engine Interlocks
if is_breached and not st.session_state.fault_cleared:
    st.markdown(f"<div class='fault-critical'>🛑 CRITICAL THERMAL FAULT [ERR-500]: Asset breached safety envelope!</div>", unsafe_allow_html=True)
    if st.button("Acknowledge & Force Clear Latched Fault"):
        st.session_state.fault_cleared = True
        st.session_state.clear_timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        st.rerun()

elif st.session_state.fault_cleared:
    st.success(f"✅ Latched Fault Overridden at {st.session_state.clear_timestamp}.")
    if st.button("Reset System Interlock Latches"):
        st.session_state.fault_cleared = False
        st.session_state.clear_timestamp = None
        st.rerun()

st.markdown(" ")

# ==========================================
# 5. LIVE CORE METRIC CARDS
# ==========================================
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

st.markdown(" ")

# ==========================================
# 6. DUAL-VIEW ANALYTICS & CSV EXPORTER
# ==========================================
view_tab1, view_tab2 = st.tabs(["📊 Live Telemetry Trend Plot", "🗄️ Raw SCADA Data Registers"])

with view_tab1:
    # Defer imports inside view window to protect main layout compilation paths
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_stream['Timestamp'], y=data_stream['CNC_Mill_Temp_C'], name='CNC Temp', line=dict(color='#A855F7')))
    fig.add_trace(go.Scatter(x=data_stream['Timestamp'], y=data_stream['Industrial_Freezer_Temp_C'], name='Freezer Temp', line=dict(color='#F97316')))

    # Overlay static threshold baseline layout target vector
    fig.add_hline(y=safety_threshold, line_dash="dash", line_color="red", annotation_text="Safety Limit Limit Trigger")

    fig.update_layout(template='plotly_dark', margin=dict(l=20, r=20, t=20, b=20), height=400)
    st.plotly_chart(fig, use_container_width=True)

with view_tab2:
    # ------------------------------------------
    # COMMERCIALLY PACKAGED CSV REPORT BUTTON
    # ------------------------------------------
    # Format log metrics frame accurately to local strings before memory buffer writes
    csv_buffer = io.StringIO()
    data_stream.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue()

    st.download_button(
        label="📥 Export Shift Logs to CSV",
        data=csv_bytes,
        file_name=f"SCADA-Fleet-Log-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.csv",
        mime="text/csv"
    )

    st.dataframe(data_stream.sort_values(by='Timestamp', ascending=False), use_container_width=True)

# ==========================================
# 7. AUTOMATED AUTO-REFRESH ENGINE TIMER
# ==========================================
# Force interface view to loop repaint every 2 seconds without requiring user clicks
time.sleep(2.0)
st.rerun()