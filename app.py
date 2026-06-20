import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="AI Refund Agent", layout="wide")

# FIX: AI Chatbot Theme with Centered 24/7 Text
st.markdown("""
    <style>
        /* Center Light, Borders Dark (Vignette Effect) */
        [data-testid="stAppViewContainer"] {
            background-image: radial-gradient(circle at center, rgba(45, 75, 120, 0.65) 0%, rgba(5, 10, 25, 0.95) 100%), url("https://images.unsplash.com/photo-1531746790731-6c08cd263438?q=80&w=2500&auto=format&fit=crop"); 
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        
        [data-testid="stAppViewContainer"]::before {
            content: "24/7 SUPPORT";
            position: fixed;
            top: 45%; 
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 8vw;
            font-weight: 900;
            font-family: 'Arial', sans-serif;
            color: rgba(100, 160, 240, 0.15); 
            text-shadow: 0px 0px 20px rgba(100, 160, 240, 0.4);
            z-index: 0;
            pointer-events: none;
            white-space: nowrap;
        }

        .block-container {
            position: relative;
            z-index: 1;
            background: rgba(20, 35, 65, 0.3); /* Lighter middle container */
            padding: 2rem;
            border-radius: 20px;
        }

        p, h1, h2, h3, h4, h5, li, label, .stTextInput input {
            color: #FFFFFF !important;
        }

        [data-testid="stChatMessage"] {
            background-color: rgba(30, 45, 75, 0.85) !important; /* Lighter chat bubbles */
            border-radius: 15px !important;
            padding: 15px !important;
            border: 1px solid #5A9DE2 !important;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2) !important;
        }

        [data-testid="stChatMessage"] p {
            color: #FFFFFF !important;
        }

        .stButton>button {
            border-radius: 20px !important;
            background-color: rgba(30, 45, 75, 0.7) !important;
            color: #7AB4F5 !important;
            border: 2px solid #5A9DE2 !important;
            font-weight: bold !important;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #5A9DE2 !important;
            color: #FFFFFF !important;
            box-shadow: 0 0 15px #5A9DE2 !important;
        }

        [data-testid="stExpander"] {
            background-color: rgba(30, 45, 75, 0.85) !important;
            border-radius: 15px !important;
            border: 1px solid #5A9DE2 !important;
        }
        
        [data-testid="stHeader"], [data-testid="stChatInput"] {
            background: transparent !important;
        }
    </style>
    """, unsafe_allow_html=True)

st.title("🛍️ E-Commerce AI Refund Agent (Voice Enabled 🎙️)")
with st.sidebar:
    st.header("🧪 Test Credentials")
    st.write("Use these mock Order IDs to test different scenarios:")
    st.code("ORD-101", language="text") # Valid refund
    st.code("ORD-201", language="text") # Past 30 days policy 
    st.code("ORD-301", language="text") # Non-refundable item
    st.code("ORD-401", language="text") # Order not delivered yet

API_URL = "https://ai-customer-support-agent-caru.onrender.com/chat"
WHISPER_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

DEFAULT_GREETING = "Hi there! 👋 I am your AI Support Agent. How can I help you today? You can provide your Order ID to check its status or request a refund."

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": DEFAULT_GREETING}]
if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []
if "audio_key" not in st.session_state:
    st.session_state.audio_key = 0 

def transcribe_audio(audio_bytes):
    files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
    data = {"model": "whisper-large-v3", "response_format": "json"}
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    
    response = requests.post(WHISPER_URL, headers=headers, files=files, data=data)
    if response.status_code == 200:
        return response.json().get("text", "")
    return None

col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("Customer Support Chat")
    
    # FIX: Using st.container() to keep the spinner above the buttons
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    user_input = None

    st.write("💡 **Quick Options:**")
    q1, q2, q3 = st.columns(3)
    if q1.button("📦 Check Order Status"):
        user_input = "I want to know the status of my order."
    if q2.button("💸 Request Refund"):
        user_input = "I want a refund for my order."
    if q3.button("📜 Refund Policy"):
        user_input = "What is the company refund policy?"

    prompt = st.chat_input("Type your message here...")
    audio_value = st.audio_input("Or speak to the agent:", key=f"mic_{st.session_state.audio_key}")
    
    if st.button("Clear Conversation / Reset"):
        st.session_state.messages = [{"role": "assistant", "content": DEFAULT_GREETING}]
        st.session_state.agent_logs = []
        st.session_state.audio_key += 1
        st.rerun()

    if audio_value:
        with chat_container: # Spinner rendered inside chat container
            with st.spinner("Transcribing your voice..."):
                user_input = transcribe_audio(audio_value.getvalue())
                st.session_state.audio_key += 1 
    elif prompt:
        user_input = prompt

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container: # User message and AI spinner rendered inside chat container
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.spinner("Agent is checking policy and CRM..."):
                try:
                    response = requests.post(API_URL, json={
                        "message": user_input, 
                        "history": st.session_state.messages[:-1] 
                    })
                    data = response.json()
                    
                    bot_reply = data.get("reply", "Error getting response.")
                    st.session_state.agent_logs = data.get("logs", [])

                    with st.chat_message("assistant"):
                        st.markdown(bot_reply)
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                    
                    st.rerun() 
                except Exception as e:
                    st.error(f"Backend connection failed: {e}")

with col2:
    st.subheader("⚙️ Admin Dashboard Logs")
    
    if st.session_state.agent_logs:
        for log in st.session_state.agent_logs:
            if log['role'] == 'system': 
                continue
            with st.expander(f"Type: {log['role'].upper()}", expanded=True):
                st.write(log['content'])
    else:
        st.info("No activity yet. Start chatting!")