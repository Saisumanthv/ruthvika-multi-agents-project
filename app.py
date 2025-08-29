import os
import streamlit as st
from agents import MasterAgent

st.set_page_config(page_title="Multi-Agent Chat", page_icon="🤖", layout="centered")

# --- Load secrets safely ---
try:
    HF_TOKEN = st.secrets.get("HF_TOKEN") or os.getenv("HF_TOKEN")
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    TOMORROW_API_KEY = st.secrets.get("TOMORROW_API_KEY") or os.getenv("TOMORROW_API_KEY")
except Exception:
    # Fallback to environment variables if secrets.toml is not found
    HF_TOKEN = os.getenv("HF_TOKEN")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    TOMORROW_API_KEY = os.getenv("TOMORROW_API_KEY")

# Check if required tokens are available
missing_tokens = []
if not HF_TOKEN:
    missing_tokens.append("HF_TOKEN")
if not GROQ_API_KEY:
    missing_tokens.append("GROQ_API_KEY")
if not TOMORROW_API_KEY:
    missing_tokens.append("TOMORROW_API_KEY")

if missing_tokens:
    st.error(f"Missing required API tokens: {', '.join(missing_tokens)}")
    st.info("Please add them to `.streamlit/secrets.toml` or set as environment variables.")
    st.stop()

# --- Init agent router ---
try:
    agent = MasterAgent(weather_api_key=TOMORROW_API_KEY, hf_token=HF_TOKEN, groq_api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"Failed to initialize agent: {str(e)}")
    st.stop()

# --- UI ---
if "history" not in st.session_state:
    st.session_state.history = []

st.title("🤖 Multi-Agent Conversational Web App")

# Display chat history
if st.session_state.history:
    st.subheader("Chat History")
    for role, msg in st.session_state.history:
        if role == "user":
            st.markdown(f"🧑 **You:** {msg}")
        else:
            st.markdown(f"🤖 **Bot:** {msg}")
else:
    st.info("Start a conversation by typing a message below!")

# Input section
st.subheader("Send a Message")
user_input = st.text_input("Type your query:", placeholder="Ask me anything...")

# Button section
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Send", type="primary", use_container_width=True) and user_input.strip():
        st.session_state.history.append(("user", user_input))
        
        # Show spinner while processing
        with st.spinner("Thinking..."):
            try:
                response = agent.route(user_input)
                st.session_state.history.append(("bot", response))
            except Exception as e:
                st.error(f"Error processing your request: {str(e)}")
                st.session_state.history.append(("bot", f"Sorry, I encountered an error: {str(e)}"))
        
        st.rerun()

with col2:
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.history = []
        st.rerun()

with col3:
    if st.session_state.history:
        chat_text = "\n".join([f"{role}: {msg}" for role, msg in st.session_state.history])
        st.download_button(
            "Export Chat", 
            chat_text, 
            file_name="chat_export.txt", 
            mime="text/plain",
            use_container_width=True
        )

# Status section
with st.expander("API Status"):
    col_status1, col_status2, col_status3 = st.columns(3)
    
    with col_status1:
        groq_status = "✅ Connected" if GROQ_API_KEY else "❌ Missing"
        st.metric("Groq API", groq_status)
    
    with col_status2:
        hf_status = "✅ Connected" if HF_TOKEN else "❌ Missing"
        st.metric("Hugging Face", hf_status)
        
    with col_status3:
        weather_status = "✅ Connected" if TOMORROW_API_KEY else "❌ Missing"
        st.metric("Tomorrow.io API", weather_status)