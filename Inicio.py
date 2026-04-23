import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# ⚠️ ESTO SIEMPRE VA PRIMERO
st.set_page_config(
    page_title="Lector de Sensor MQTT",
    page_icon="📡",
    layout="centered"
)

# --- ESTILO VISUAL (ROSADO CLARO) ---
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #ffd6e7, #ffeaf4);
        color: #5a2a4d;
    }
    h1, h2, h3 {
        color: #b03060;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Variables de estado
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None

def get_mqtt_message(broker, port, topic, client_id):
    message_received = {"received": False, "payload": None}
    
    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            message_received["payload"] = payload
            message_received["received"] = True
        except:
            message_received["payload"] = message.payload.decode()
            message_received["received"] = True
    
    try:
        client = mqtt.Client(client_id=client_id)
        client.on_message = on_message
        client.connect(broker, port, 60)
        client.subscribe(topic)
        client.loop_start()
        
        timeout = time.time() + 5
        while not message_received["received"] and time.time() < timeout:
            time.sleep(0.1)
        
        client.loop_stop()
        client.disconnect()
        
        return message_received["payload"]
    
    except Exception as e:
        return {"error": str(e)}

# Sidebar
with st.sidebar:
    st.subheader('⚙️ Configuración')
    broker = st.text_input('🌐 Broker MQTT', value='broker.mqttdashboard.com')
    port = st.number_input('🔌 Puerto', value=1883, min_value=1, max_value=65535)
    topic = st.text_input('📡 Tópico', value='Sensor/THP2')
    client_id = st.text_input('🆔 ID Cliente', value='streamlit_client')

# Título
st.title('🌸 Lector de Sensor MQTT')
st.subheader('📡 Datos en tiempo real')

st.divider()

# Botón
if st.button('🔄 Obtener Datos', use_container_width=True):
    with st.spinner('⏳ Conectando...'):
        sensor_data = get_mqtt_message(broker, int(port), topic, client_id)
        st.session_state.sensor_data = sensor_data

# Resultados
if st.session_state.sensor_data:
    st.divider()
    st.subheader('📊 Datos Recibidos')
    
    data = st.session_state.sensor_data
    
    if isinstance(data, dict) and 'error' in data:
        st.error(f"❌ Error: {data['error']}")
    else:
        st.success('✅ Datos correctos')
        
        if isinstance(data, dict):
            cols = st.columns(len(data))
            for i, (key, value) in enumerate(data.items()):
                with cols[i]:
                    st.metric(label=f"🌷 {key}", value=value)
            
            with st.expander('🧾 JSON completo'):
                st.json(data)
        else:
            st.code(data)
