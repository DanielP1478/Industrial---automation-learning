import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time
import os
import json

# Set page configuration layout for mobile browser previewing
st.set_page_config(page_title="Butcher Cold-Chain Protection Center", layout="wide")

# ==========================================
# 1. HARDENED JSON FILE PERSISTENCE ENGINE
# ==========================================
def save_telemetry_permanently(payload):
    """Appends incoming sensor readings to a permanent background data file safely."""
    try:
        log_file = "telemetry_log.json"
        existing_data = []

        # Read historical entries from cloud storage disk if file exists
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                try:
                    existing_data = json.load(f)
                except Exception:
                    existing_data = []

        # Append the new sensor payload log data block
        existing_data.append(payload)

        # Structural defense cap: retain last 10,000 logs to prevent drive bloating
        existing_data = existing_data[-10000:]

        # Lock data back down to the workspace hard drive
        with open(log_file, "w") as f:
            json.dump(existing_data, f, indent=4)
    except Exception:
        pass

# ==========================================
# 2. APPLICATION MEMORY STATE MACHINE INITIALIZATION
# ==========================================
if 'telemetry_buffer' not in st.session_state:
    now = datetime.datetime.now()
    timestamps = pd.date_range(end=now, periods=60, freq='min')
    st.session_state.telemetry_buffer = pd.DataFrame({
        'Timestamp': timestamps,
        'WalkIn_Freezer_Temp_C': np.random.normal(loc=-19.5, scale=0.5, size=60),
        'Display_Counter_Temp_C': np.random.normal(loc=2.2, scale=0.3, size=60)
    })

if 'snooze_active_until' not in st.session_state:
    st.session_state.snooze_active_until = None
if 'consecutive_breach_ticks' not in st.session_state:
    st.session_state.consecutive_breach_ticks = 0
if 'sms_sent_latch' not in st.session_state:
    st.session_state.sms_sent_latch = False
if 'sms_log_feed' not in st.session_state:
    st.session_state.sms_log_feed = []

# ==========================================
# 3. SIMULATED SENSOR TICK ENGINE
# ==========================================
def simulate_live_sensor_tick():
    df_current = st.session_state.telemetry_buffer
    last_row = df_current.iloc[-1]

    # Text-formatted string timestamp prevents JSON encoding exceptions
    timestamp_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    new_row = {
        'Timestamp': timestamp_str,
        'WalkIn_Freezer_Temp_C': float(last_row['WalkIn_Freezer_Temp_C'] + np.random.normal(loc=0.0, scale=0.4)),
        'Display_Counter_Temp_C': float(last_row['Display_Counter_Temp_C'] + np.random.normal(loc=0.0, scale=0.1))
    }

    # Fire the persistent hard-drive logger tool automatically on every tick
    save_telemetry_permanently(new_row)

    df_updated = pd.concat([df_current, pd.DataFrame([new_row])], ignore_index=True).iloc[-300:]
    st.session_state.telemetry_buffer = df_updated

simulate_live_sensor_tick()

data_stream = st.session_state.telemetry_buffer
latest_metrics = data_stream.iloc[-1]
current_freezer_temp = latest_metrics['WalkIn_Freezer_Temp_C']

# ==========================================
# 4. CONTROL PANEL SIDEBAR & ONBOARDING SETUP
# ==========================================
st.sidebar.title("🎛️ Shop Control Panel")
safety_threshold = st.sidebar.slider("Critical Freezer Threshold (°C)", -25, -2, -10)
minutes_buffer = st.sidebar.slider("Defrost Delay Filter (Minutes)", 1, 60, 45)

st.sidebar.markdown("---")
st.sidebar.subheader("📱 Client Phone Setup")
st.sidebar.caption("Onboard new shops visually by entering details right here.")
client_phone = st.sidebar.text_input("Butcher's Mobile Number", value="+447123456789")
twilio_sid = st.sidebar.text_input("Twilio Account SID", value="ACxxxxxxxxxxxxxxxx")
twilio_token = st.sidebar.text_input("Twilio Auth Token", value="xxxxxxxxxxxxxxxx", type="password")
twilio_number = st.sidebar.text_input("Your Twilio Number", value="+15552223333")

st.sidebar.markdown("---")
st.sidebar.subheader("📋 HACCP Health Compliance Log")
csv_buffer = data_stream.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Download Inspection Log (.CSV)",
    data=csv_buffer,
    file_name=f"HACCP_Temperature_Log_{datetime.date.today()}.csv",
    mime="text/csv"
)

# ==========================================
# 5. COMMERCIAL DURATION ENGINE & ALARM PATTERNS
# ==========================================
is_breached = current_freezer_temp > safety_threshold
is_muted = False

if st.session_state.snooze_active_until is not None:
    if datetime.datetime.now() < st.session_state.snooze_active_until:
        is_muted = True
    else:
        st.session_state.snooze_active_until = None

if is_breached:
    st.session_state.consecutive_breach_ticks += 1
else:
    st.session_state.consecutive_breach_ticks = 0
    st.session_state.sms_sent_latch = False

# Calculate tick intervals (runs every 2 seconds on app page loops)
seconds_persistent = st.session_state.consecutive_breach_ticks * 2
duration_met = seconds_persistent >= (minutes_buffer * 60)

if duration_met and not st.session_state.sms_sent_latch and not is_muted:
    alert_msg = f"ALERT: Freezer high temp breach! Current: {current_freezer_temp:.1f}°C. Limit: {safety_threshold}°C."
    log_time = datetime.datetime.now().strftime('%H:%M:%S')

    if twilio_sid.startswith("ACxxxx") or len(twilio_sid) < 10:
        st.session_state.sms_log_feed.append(f"🧪 [{log_time}] TEST SANDBOX LOGGED: Alert routing to {client_phone} is armed.")
    else:
        try:
            from twilio.rest import Client as TwilioClient
            client = TwilioClient(twilio_sid, twilio_token)
            message = client.messages.create(body=alert_msg, from_=twilio_number, to=client_phone)
            st.session_state.sms_log_feed.append(f"📡 [{log_time}] LIVE SMS DEPLOYED TO {client_phone} | SID: {message.sid}")
        except Exception as e:
            st.session_state.sms_log_feed.append(f"❌ [{log_time}] CARRIER TRANSIT ERROR: {str(e)}")

    st.session_state.sms_sent_latch = True

# ==========================================
# 6. BUSINESS INTERFACE RENDERING
# ==========================================
st.title("🥩 Butcher Cold-Chain Asset Protection Engine")
st.caption(f"Ref Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if is_breached:
    if is_muted:
        st.info("🔕 System alerts muted for 2 hours while operator manages inventory migration.")
    elif duration_met:
        st.error(f"🛑 CRITICAL HEAT EXPOSURE: Asset has outlasted defrost safety buffer for {seconds_persistent // 60}m!")
        if st.button("Acknowledge Emergency & Silence Alerts for 2 Hours"):
            st.session_state.snooze_active_until = datetime.datetime.now() + datetime.timedelta(hours=2)
            st.rerun()
    else:
        st.warning(f"⚠️ ELEVATED TEMPERATURE: Current: {current_freezer_temp:.1f}°C. Filtering cycle anomalies... ({seconds_persistent}s / {minutes_buffer * 60}s)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Real-Time Temperature Monitoring Matrix")
    # Convert Timestamp strings to datetimes for smooth line chart formatting
    chart_data = data_stream.copy()
    chart_data['Timestamp'] = pd.to_datetime(chart_data['Timestamp'])
    st.line_chart(chart_data.set_index('Timestamp')[['WalkIn_Freezer_Temp_C', 'Display_Counter_Temp_C']])

with col2:
    st.subheader("📱 Encrypted Carrier Communications Feed")
    if st.session_state.sms_log_feed:
        for log in reversed(st.session_state.sms_log_feed[-10:]):
            st.code(log)
    else:
        st.caption("All systems stable. No outbound cellular event logs.")

# Automatic loop refresh cadence execution
time.sleep(2)
st.rerun()