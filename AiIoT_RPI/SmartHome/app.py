import streamlit as st, requests, pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

from config import RPI_API_KEY,RPI_API_URL, GENERATIVE_ENGINE_API_KEY_2
from api.llm_client import GenerativeEngineClient
from api.thingspeak_client import ThingspeakClient


#------------------------------------------------------
#       SETUP
#------------------------------------------------------

st.set_page_config(page_title="MCP IoT Dashboard",layout="wide")
st.title("🤖 MCP-Controlled IoT Dashboard 🤖")

llm_client = GenerativeEngineClient()

HEADERS = {"X-API-KEY":RPI_API_KEY}
# Make sure to provide the correct API key and base URL for ThingspeakClient if required
Thingspeak = ThingspeakClient()  # e.g., ThingspeakClient(api_key=YOUR_API_KEY, base_url=YOUR_BASE_URL)
#------------------------------------------------------
#       SESSION STATE
#------------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "monitoring" not in st.session_state:
    st.session_state.monitoring = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []



#------------------------------------------------------
#       Helper : Execute MCP
#------------------------------------------------------

def execute_mcp(action,params={}):
    r = requests.post(
        f"{RPI_API_URL}/execute",
        headers=HEADERS,
        json={"action":action,"params":params},
        timeout=5
    )
    try:
        return r.json()
    except Exception as e:
        st.error(f"Non-Json response from RPI: {e}")
        st.code(r.text)
        return {}

def get_status():
    return execute_mcp("system_status")


#------------------------------------------------------
#       SIDEBAR LAYOUT : (About & Tools)
#------------------------------------------------------
with st.sidebar:
    st.header("ℹ️ About")
    st.write("AI-Based IoT Control System")

    st.subheader("Available Tools : ")
    tools = llm_client._fetch_mcp_tools()
    for d in tools:
        st.markdown(f"**• {d['name']}**")
        st.markdown(
            f"<div style='margin-left: 20px; margin-top: -15px; margin-bottom: 10px; font-size: 12px; color: gray;'>"
            f"{d['description']}</div>",
            unsafe_allow_html=True
        )
    threshold = st.slider("Temp Threshold",10,60,30)
    execute_mcp("set_temp_threshold",{"value":threshold})

    # --- Auto Refresh Bar ---
    st.subheader("Auto Refresh")
    auto_refresh_enabled = st.checkbox("Enable Auto Refresh", value=st.session_state.get("auto_refresh_enabled", False))
    auto_refresh_interval = st.slider("Refresh Interval (sec)", 2, 60, st.session_state.get("auto_refresh_interval", 10))
    st.session_state.auto_refresh_enabled = auto_refresh_enabled
    st.session_state.auto_refresh_interval = auto_refresh_interval

    if auto_refresh_enabled:
        st_autorefresh(interval=auto_refresh_interval * 1000, key="auto_refresh",limit=100)

#------------------------------------------------------
#       MAIN LAYOUT: Chat 
#------------------------------------------------------
left, center = st.columns([0.1, 0.9], gap="large")

with center:
    with st.expander("💬 Chat History", expanded=False):
        if st.session_state.chat_history:
            for chat in st.session_state.chat_history:
                st.markdown(f"**User** : {chat['user']}")
                st.markdown("**LLM Output:**")
                st.json(chat["llm_output"])
        else:
            st.info("No chat history yet.")

    st.subheader("Command Center")
    user_input = st.chat_input(f"Enter your command : ")
    if user_input:
        mcp_command = llm_client.process_command(user_input)
        st.session_state.chat_history.append({
            "user": user_input,
            "llm_output": mcp_command
        })
        with st.chat_message("user"):
            st.write(f"{user_input}")
        with st.chat_message("assistant"):
            st.json(mcp_command)
        execute_mcp(mcp_command["action"], mcp_command.get("params", {}))
    # Plot temperature, humidity, and lux readings
    data = execute_mcp("get_buffers")
    frames = []
    # Send latest sensor data to Thingspeak
    latest_temp = None
    latest_humidity = None
    latest_lux = None
    latest_motion = None

    # Get latest DHT data
    dht_records = data.get("dht", [])
    if isinstance(dht_records, dict):
        dht_records = [dht_records]
    if dht_records and isinstance(dht_records, list) and len(dht_records) > 0:
        latest_dht = dht_records[-1]
        latest_temp = latest_dht.get("temperature")
        latest_humidity = latest_dht.get("humidity")
    else:
        latest_temp = None
        latest_humidity = None

    # Get latest Light data
    light_records = data.get("light", [])
    if isinstance(light_records, dict):
        light_records = [light_records]
    if light_records and isinstance(light_records, list) and len(light_records) > 0:
        latest_light = light_records[-1]
        latest_lux = latest_light.get("lux")
    else:
        latest_lux = None

    # Get latest Motion data
    motion_records = data.get("motion", [])
    if isinstance(motion_records, dict):
        motion_records = [motion_records]
    if motion_records and isinstance(motion_records, list) and len(motion_records) > 0:
        latest_motion_record = motion_records[-1]
        latest_motion = latest_motion_record.get("motion")
    else:
        latest_motion = None
    
    try:
        print(f"Sending to Thingspeak: Temp={latest_temp}, Humidity={latest_humidity}, Lux={latest_lux}")
        Thingspeak.send_data(latest_temp, latest_humidity, latest_lux)
    except Exception as e:
        st.error(f"Failed to send data to Thingspeak: {e}")

    for sensor, records in data.items():
        if not records:
            continue
        if isinstance(records, dict):
            records = [records]
        if not isinstance(records, list):
            continue
        df = pd.DataFrame(records)
        if "timestamp" not in df.columns:
            continue
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        # Flatten columns: e.g., temperature -> dht.temperature
        if sensor == "dht":
            if "temperature" in df.columns:
                df = df.rename(columns={"temperature": "dht.temperature"})
            if "humidity" in df.columns:
                df = df.rename(columns={"humidity": "dht.humidity"})
        if sensor == "light":
            if "lux" in df.columns:
                df = df.rename(columns={"lux": "light.lux"})
        frames.append(df)

    # System Status with Latest Readings
    status = get_status()
    st.subheader("🖥️ System Status")
    
    # DHT11 Status with readings
    dht_status = "ON" if status.get("dht") else "OFF"
    temp_str = f"{latest_temp:.1f}°C" if latest_temp is not None else "0"
    humidity_str = f"{latest_humidity:.1f}%" if latest_humidity is not None else "0"
    st.metric("DHT11 Sensor", f"{dht_status} :: Temp : {temp_str} | Humidity : {humidity_str}")
    
    # Light Sensor Status with readings
    light_status = "ON" if status.get("light") else "OFF"
    lux_str = f"{latest_lux:.2f}" if latest_lux is not None else "0"
    st.metric("Light Sensor", f"{light_status} :: Lux : {lux_str}")
    
    # Motion Sensor Status with readings
    motion_status = "ON" if status.get("motion") else "OFF"
    motion_str = "Detected" if latest_motion else "Not Detected"
    st.metric("Motion Sensor", f"{motion_status} :: Motion : {motion_str}")

    #------------------------------------------------------
    #      GRAPHS
    #------------------------------------------------------

    if frames:
        df_all = pd.concat(frames, ignore_index=True)
        st.subheader("📈 Sensor Graphs")
        # Only keep relevant columns
        plot_cols = []
        if "dht.temperature" in df_all.columns:
            plot_cols.append("dht.temperature")
        if "dht.humidity" in df_all.columns:
            plot_cols.append("dht.humidity")
        if "light.lux" in df_all.columns:
            plot_cols.append("light.lux")
        if plot_cols:
            df_plot = df_all[["timestamp"] + plot_cols].dropna()
            # Melt the dataframe for multi-line plot
            df_melt = df_plot.melt(id_vars=["timestamp"], value_vars=plot_cols, var_name="sensor", value_name="value")
            # Debug output to help diagnose graph issues
            st.write("Plot columns:", plot_cols)
            with open ("./logs/data_sheet.txt","w") as xls:
                xls.write(str(df_melt))
            fig = px.line(
                df_melt,
                x="timestamp",
                y="value",
                color="sensor",
                title="Sensor Readings Over Time",
                line_shape="spline"
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No Temperature, Humidity, or Lux Data Available Yet...")
    else:
        st.info("No Sensor Data Available Yet...")
    st.subheader("💡LED Status")
    led_mode = status.get("led_mode", "unknown")
    if led_mode == "idle":
        st.success("LED : OFF")
    elif led_mode == "manual":
        st.success("LED : ON (Manual Control)")
    elif led_mode == "pattern":
        st.success("LED : ON (RGB Pattern Running)")
    elif led_mode == "sensor":
        st.success("LED : AUTO (Sensor Controlled)")
    else:
        st.error("LED : Unknown State")


if __name__ == '__main__':
    pass