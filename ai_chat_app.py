import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import json
import os

import random

# Load environment variables
load_dotenv()
# Page config
st.set_page_config(page_title="AI Pro Chat", page_icon="⚡", layout="wide")

# Suggestion Pool
SUGGESTION_POOL = [
    "Explain quantum computing simply",
    "Write a Python script for a Pomodoro timer",
    "Suggest a 3-day trip to Tokyo",
    "How do I implement a binary search in Python?",
    "What are the benefits of using LangChain?",
    "Give me a recipe for a healthy breakfast",
    "Explain the difference between SQL and NoSQL",
    "Write a poem about artificial intelligence",
    "How do I optimize a React application?",
    "Explain PCA (Principal Component Analysis)",
    "How to make a simple web scraper in Python?",
    "Best practices for Git branch management"
]

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None
if "initial_suggestions" not in st.session_state:
    st.session_state.initial_suggestions = random.sample(SUGGESTION_POOL, 3)
if "last_follow_up" not in st.session_state:
    st.session_state.last_follow_up = None

# Custom CSS for "White & Grey Shard" premium look
st.markdown("""
    <style>
    /* Main app background */
    .stApp {
        background-color: #ffffff;
        color: #1a1a1a;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Sidebar styling - Geometric & Sharp */
    section[data-testid="stSidebar"] {
        background-color: #f4f4f5 !important;
        border-right: 1px solid #e2e2e7;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
    }
    
    /* User message bubble (Sharp Grey) */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #f7f7f8 !important;
        border-radius: 0px; 
        border-left: 3px solid #d1d5db;
    }
    
    /* Button styling - Shard */
    div.stButton > button {
        background-color: #ffffff;
        color: #1a1a1a;
        border: 1px solid #e2e2e7;
        border-radius: 0px; 
        padding: 0.6rem 1.2rem;
        transition: all 0.1s ease;
        font-weight: 500;
        text-align: left;
    }
    div.stButton > button:hover {
        background-color: #f4f4f5 !important;
        border-color: #1a1a1a !important;
    }

    /* Follow up button specifically */
    div.follow-up-container {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    div.follow-up-container button {
        background-color: #f9fafb !important;
        color: #4b5563 !important;
        border: 1px solid #e5e7eb !important;
        font-weight: 400 !important;
        font-size: 0.9rem !important;
        padding: 0.4rem 1rem !important;
        border-radius: 0px !important;
    }
    div.follow-up-container button:hover {
        background-color: #f3f4f6 !important;
        border-color: #d1d5db !important;
    }
    
    /* Input field styling */
    .stChatInputContainer {
        border: 1px solid #e2e2e7;
        background-color: #ffffff;
        border-radius: 8px;
        margin-bottom: 2rem;
    }
    
    /* Headers - Strong & Sharp */
    h1, h2, h3 {
        color: #000000;
        letter-spacing: -0.025em;
        font-weight: 800;
    }

    /* Info boxes */
    .stAlert {
        border-radius: 0px;
        border: 1px solid #e2e2e7;
        background-color: #f9f9fb;
    }
    
    /* Center greeting */
    .center-greeting {
        text-align: center;
        margin-top: 15vh;
        margin-bottom: 5vh;
    }
    .center-greeting h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.title("Settings")
    
    provider = st.selectbox("LLM Provider", ["Groq", "Gemini"])
    
    if provider == "Groq":
        model_options = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
        user_key = st.text_input("Groq API Key", placeholder="gsk_...", type="password")
        model_name = st.selectbox("Model", model_options)
        model_id = f"groq:{model_name}"
        api_key_param = "groq_api_key"
    else:
        # Verified working models from your environment
        model_options = [
            "gemini-2.0-flash", 
            "gemini-2.0-flash-lite", 
            "gemini-2.5-flash", 
            "gemini-2.5-pro",
            "gemini-flash-latest"
        ]
        user_key = st.text_input("Gemini API Key", placeholder="AIza...", type="password")
        model_name = st.selectbox("Model", model_options)
        model_id = f"google_genai:{model_name}"
        api_key_param = "google_api_key"

    st.divider()
    if st.button("New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.session_state.last_follow_up = None
        st.session_state.initial_suggestions = random.sample(SUGGESTION_POOL, 3)
        st.rerun()

# Main Chat Interface
if not st.session_state.messages:
    # Centered Landing Page
    st.markdown('<div class="center-greeting"><h1>Ready to dive in?</h1></div>', unsafe_allow_html=True)
    
    # Grid for suggestions
    cols = st.columns([1, 2, 1])
    with cols[1]:
        for i, suggestion in enumerate(st.session_state.initial_suggestions):
            if st.button(suggestion, key=f"sug_{i}", use_container_width=True):
                st.session_state.pending_prompt = suggestion
                st.rerun()
else:
    st.title("AI Pro Chat")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Display last follow-up question if available
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant" and st.session_state.last_follow_up:
    with st.container():
        st.markdown('<p style="font-weight:600; margin-top:2rem; font-size:1.1rem; color:#1a1a1a;">Next Questions</p>', unsafe_allow_html=True)
        st.markdown('<div class="follow-up-container">', unsafe_allow_html=True)
        if st.button(f"👉 {st.session_state.last_follow_up}", key="follow_up_btn", use_container_width=True):
            st.session_state.pending_prompt = st.session_state.last_follow_up
            st.session_state.last_follow_up = None # Consumed
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Chat input or pending prompt
chat_input = st.chat_input("Message AI Pro...")
prompt = chat_input
if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if prompt:
    # Priority: 1. User entered key, 2. .env file key
    api_key = user_key or (os.getenv("groq_api-key") if provider == "Groq" else os.getenv("gemini_api-key"))
    
    if not api_key:
        st.error(f"Please provide a {provider} API key to start chatting.")
    else:
        # Clear previous follow-up
        st.session_state.last_follow_up = None
        
        # Log to terminal
        print(f"\n[USER]: {prompt}")
        
        # User message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI response
        with st.chat_message("assistant"):
            try:
                # Initialize model using True BYOK (direct parameter passing)
                kwargs = {api_key_param: api_key}
                
                model = init_chat_model(
                    model_id,
                    streaming=True,
                    **kwargs
                )
                print(f"[SYSTEM]: Initialized {model_id}")
            
                # Convert history to LangChain format
                history = []
                for m in st.session_state.messages[:-1]:
                    if m["role"] == "user":
                        history.append(HumanMessage(content=m["content"]))
                    else:
                        history.append(AIMessage(content=m["content"]))
                
                # Add current prompt
                history.append(HumanMessage(content=prompt))
                
                # Stream response
                response_placeholder = st.empty()
                full_response = ""
                
                for chunk in model.stream(history):
                    full_response += chunk.content
                    response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                # Log to terminal
                print(f"[ASSISTANT]: {full_response}\n" + "-"*50)
                
                # Generate follow-up question in background state
                with st.spinner("Generating suggestions..."):
                    follow_up_prompt = f"Based on our previous conversation, ask a short, engaging, and relevant follow-up question to the user. Just the question, no other text.\n\nUser: {prompt}\nAI: {full_response}"
                    follow_up_message = model.invoke([SystemMessage(content="You are a helpful assistant."), HumanMessage(content=follow_up_prompt)])
                    st.session_state.last_follow_up = follow_up_message.content
                    st.rerun() # Rerun to show the button via the persistent display logic

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
