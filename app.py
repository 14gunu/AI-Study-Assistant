import streamlit as st
import google.generativeai as genai
from PIL import Image
from pypdf import PdfReader
from streamlit_mic_recorder import mic_recorder
from datetime import datetime
import random

# Page Configuration
st.set_page_config(page_title="AI Study Hub", page_icon="🎓", layout="wide")

# Theme Definitions
bg_themes = {
    "Starry Hearts": "radial-gradient(circle, #ff9a9e 1px, transparent 1px), radial-gradient(circle, #fad0c4 1px, transparent 1px)",
    "Floral Pink": "linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%)",
    "Midnight Sparkle": "radial-gradient(circle at center, #2e1065, #0e1117)"
}

# Sidebar
st.sidebar.title("🎓 AI Study Hub")
selected_theme = st.sidebar.selectbox("🎨 Choose Vibe", list(bg_themes.keys()))

# Applying Dynamic CSS
st.markdown(f"""
<style>
    .stApp {{ background-image: {bg_themes[selected_theme]}; background-size: 50px 50px; background-color: #0e1117; }}
    .motivation {{ text-align: center; font-size: 24px; color: #ff9a9e; font-family: 'cursive'; margin-bottom: 20px; }}
    .welcome-text {{ font-size: 18px; color: #ff9a9e; font-weight: bold; }}
    .stButton>button {{ 
        background: linear-gradient(90deg, #ff9a9e, #fad0c4); 
        color: white; border-radius: 25px; border: none; height: 50px; width: 100%;
        transition: 0.4s; font-weight: bold;
    }}
    .stButton>button:hover {{ transform: scale(1.03); box-shadow: 0 4px 15px rgba(255,154,158,0.5); }}
    [data-testid="stSidebar"] {{ background-color: rgba(30, 30, 46, 0.8) !important; }}
    div[data-testid="stExpander"] {{ background-color: #1e1e2e; border: 1px solid #ff9a9e; border-radius: 15px; }}
</style>
""", unsafe_allow_html=True)

# Sidebar Details
hour = datetime.now().hour
greeting = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 18 else "Good Evening"
st.sidebar.markdown(f"<p class='welcome-text'>{greeting}, Scholar! 🌟</p>", unsafe_allow_html=True)
st.sidebar.metric("🔥 Study Streak", "3 Days", "Keep going! 💖")

# Main Interface
st.title("🎓 AI Study Assistant")
quotes = ["✨ Dream big, study hard, achieve more!", "🌸 Believe in yourself.", "🎀 Small progress is still progress.", "💖 Your potential is endless."]
st.markdown(f"<div class='motivation'>{random.choice(quotes)}</div>", unsafe_allow_html=True)

# Session State
if 'content' not in st.session_state: st.session_state.content = ""
if 'audio_data' not in st.session_state: st.session_state.audio_data = None

# API Setup
with st.expander("🔑 Setup API Key"):
    api_key = st.text_input("Enter Gemini API Key", type="password")

# Content Input Area
col1, col2 = st.columns(2)
with col1:
    uploaded_files = st.file_uploader("📂 Upload Materials", accept_multiple_files=True)
    st.subheader("🎤 Record Voice Notes")
    audio = mic_recorder(start_prompt="🎙️ Record", stop_prompt="⏹️ Stop", just_once=True)
    if audio: st.session_state.audio_data = audio["bytes"]
    if st.session_state.audio_data:
        st.audio(st.session_state.audio_data)
        if st.button("🗑️ Clear Recording"): st.session_state.audio_data = None; st.rerun()

with col2:
    notes = st.text_area("📝 Type your notes here...", height=250)
    full_content = notes + "\n"
    if uploaded_files:
        for file in uploaded_files:
            if file.type == "application/pdf":
                reader = PdfReader(file)
                for page in reader.pages:
                    if page.extract_text(): full_content += page.extract_text() + "\n"

# Generator Logic
def generate(task):
    if not api_key: return st.error("Add your API Key first!")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    with st.status("✨ Crafting your content...", expanded=True) as status:
        response = model.generate_content(f"Task: {task}. Context: {full_content}")
        status.update(label="Done!", state="complete")
        st.info(response.text)
        st.download_button("Download", response.text, file_name="study_material.txt")

# Tabs
tabs = st.tabs(["📝 Summary", "❓ Questions", "✅ Quiz", "🃏 Flashcards"])
with tabs[0]: 
    if st.button("Generate Summary"): generate("Summary")
with tabs[1]: 
    if st.button("Generate Questions"): generate("5 Key Questions")
with tabs[2]: 
    if st.button("Start Quiz"): generate("10 MCQs with answers")
with tabs[3]: 
    if st.button("Make Flashcards"): generate("10 Flashcards")