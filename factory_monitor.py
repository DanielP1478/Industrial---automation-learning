import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time
import os
import json

def save_telemetry_permanently(payload):
    """Appends incoming sensor readings to a permanent background data file."""
    try:
        log_file = "telemetry_log.json"
        existing_data = []

        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                try:
                    existing_data = json.load(f)
                except Exception:
                    existing_data = []

        existing_data.append(payload)
        existing_data = existing_data[-10000:]

        with open(log_file, "w") as f:
            json.dump(existing_data, f, indent=4)
    except Exception:
        pass

# Set page configuration layout
st.set_page_config(page_title="Butcher Cold-Chain Protection Center", layout="wide")

# ==========================================
# 1. LIVE COLD-CHAIN STATE INITIALIZATION
# ==========================================
if 'telemetry_buffer' not in st.session_state:
    now = datetime.datetime.now()
    timestamps = pd.date_range(end=now, periods=60, freq='min')
    st.session_state.telemetry_buffer = pd.DataFrame({
        'Timestamp': timestamps,
        'WalkIn_Freezer_Temp_C': np.random.normal(loc=-19.5, scale=0.5, size=60),
        'Display_Counter_Temp_C': np.random.normal(loc=2.2, scale=0.3, size=60)
    })

if 'consecutive_breach_ticks' not in st.session_state:
    st.session_state.consecutive_breach_ticks = 0
if 'sms_sent_latch' not in st.session_state:
    st.session_state.sms_sent_latch = False
if 'sms_log_feed' not in st.session_state:
    st.session_state.sms_log_feed = []

# Simulate live incoming freezer data ticks
def simulate_live_sensor_tick():
    df_current = st.session_state.telemetry_buffer
    last_row = df_current.iloc[-1]
    new_row = {
        'Timestamp': datetime.datetime.now(),
        'WalkIn_Freezer_Temp_C': float(last_row['WalkIn_Freezer_Temp_C'] + np.random.normal(loc=0.0, scale=0.4)),
        'Display_Counter_Temp_C': float(last_row['Display_Counter_Temp_C'] + np.random.normal(loc=0.0, scale=0.1))
    }
    save_telemetry_permanently(new_row)
    st.session_state.telemetry_buffer = pd.concat([df_current, pd.DataFrame([new_row])], ignore_index=True).iloc[-300:]

simulate_live_sensor_tick()

data_stream = st.session_state.telemetry_buffer
current_freezer_temp = data_stream.iloc[-1]['WalkIn_Freezer_Temp_C']

# ==========================================
# 2. CONTROL PANEL SIDEBAR SETUP
# ==========================================
st.sidebar.title("🎛️ Shop Control Panel")
safety_threshold = st.sidebar.slider("Critical Freezer Threshold (°C)", -25, -2, -10)
minutes_buffer = st.sidebar.slider("Defrost Delay Filter (Minutes)", 1, 60, 45)

# ✨ NEW FEATURE: FRONT-END CLIENT PHONE CONFIGURATION BOXES ✨
st.sidebar.markdown("---")
st.sidebar.subheader("📱 Client Phone Setup")
st.sidebar.caption("Type the customer's numbers directly here. No code changes needed.")

client_phone = st.sidebar.text_input("Butcher's Mobile Number", value="+447123456789")
twilio_sid = st.sidebar.text_input("Twilio Account SID (From your account)", value="ACxxxxxxxxxxxxxxxx")
twilio_token = st.sidebar.text_input("Twilio Auth Token", value="xxxxxxxxxxxxxxxx", type="password")
twilio_number = st.sidebar.text_input("Your Twilio System Number", value="+15552223333")

# ==========================================
# 3. ALARM ENGINE & TEXT MESSAGE ROUTING
# ==========================================
is_breached = current_freezer_temp > safety_threshold

if is_breached:
    st.session_state.consecutive_breach_ticks += 1
else:
    st.session_state.consecutive_breach_ticks = 0
    st.session_state.sms_sent_latch = False

seconds_persistent = st.session_state.consecutive_breach_ticks * 2
duration_met = seconds_persistent >= (minutes_buffer * 60)

# Trigger text message routing logic safely
if duration_met and not st.session_state.sms_sent_latch:
    alert_msg = f"ALERT: Freezer temperature breach! Current: {current_freezer_temp:.1f}°C. Limit: {safety_threshold}°C."
    timestamp_now = datetime.datetime.now().strftime('%H:%M:%S')

    # If the user hasn't typed in real Twilio keys on the screen yet, run sandbox mode
    if twilio_sid.startswith("ACxxxx"):
        st.session_state.sms_log_feed.append(
            f"🧪 [{timestamp_now}] SANDBOX TEST: If live, a text message would now be sent to {client_phone}."
        )
    else:
        # Live Carrier Outbound Integration Engine
        try:
            from twilio.rest import Client as TwilioClient
            client = TwilioClient(twilio_sid, twilio_token)
            message = client.messages.create(body=alert_msg, from_=twilio_number, to=client_phone)
            st.session_state.sms_log_feed.append(f"📡 [{timestamp_now}] LIVE SMS SENT TO {client_phone}! SID: {message.sid}")
        except Exception as e:
            st.session_state.sms_log_feed.append(f"❌ [{timestamp_now}] ROUTING ERROR: {str(e)}")

    st.session_state.sms_sent_latch = True

# ==========================================
# 4. APP RENDERING LAYOUT HEADERS
# ==========================================
st.title("🥩 Butcher Cold-Chain Asset Protection Engine")
st.caption(f"Ref Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if is_breached:
    if duration_met:
        st.error(f"🛑 CRITICAL HEAT EXPOSURE: Freezer has been unsafe for {seconds_persistent // 60} minutes!")
    else:
        st.warning(f"⚠️ ELEVATED TEMPERATURE: Current: {current_freezer_temp:.1f}°C. Waiting for defrost buffer... ({seconds_persistent}s / {minutes_buffer * 60}s)")

layout_col1, layout_col2 = st.columns(2)

with layout_col1:
    st.subheader("📈 Real-Time Temperature Monitoring Matrix")
    st.line_chart(data_stream.set_index('Timestamp')[['WalkIn_Freezer_Temp_C', 'Display_Counter_Temp_C']])

with layout_col2:
    st.subheader("📱 Active Outbound Message Feed")
    if st.session_state.sms_log_feed:
        for log in reversed(st.session_state.sms_log_feed[-10:]):
            st.code(log)
    else:
        st.caption("No message activity logged yet.")

# Automatic page reload sequence loop
time.sleep(2)
st.rerun()