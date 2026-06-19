import streamlit as st
import google.generativeai as genai
from PIL import Image
from pypdf import PdfReader

# Page Setup
st.set_page_config(page_title="AI Study Assistant", page_icon="🎓", layout="wide")

# Styling: Added dotted floral background and motivation title style
st.markdown("""
<style>
    .stApp { 
        background-color: #0e1117; 
        color: #ffffff;
        background-image: radial-gradient(#262730 1px, transparent 1px), 
                          radial-gradient(#262730 1px, transparent 1px);
        background-size: 40px 40px;
        background-position: 0 0, 20px 20px;
    }
    .stApp::before {
        content: "✿";
        position: fixed; top: 10px; right: 20px; font-size: 30px; color: #ff4b4b; opacity: 0.3;
    }
    .motivation-title {
        text-align: center; color: #ff4b4b; font-style: italic; margin-bottom: 20px;
    }
    .stButton>button { background-color: #ff4b4b; color: white; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# Session State
if 'content' not in st.session_state: st.session_state.content = ""

# Sidebar
st.sidebar.title("🎓 AI Study Hub")
difficulty = st.sidebar.select_slider("Select Difficulty", options=["Easy", "Medium", "Hard"])
st.sidebar.write("---")
st.sidebar.write("📊 **Progress Tracker**")
st.sidebar.progress(0.4)
st.sidebar.write("🔥 Streak: 3 Days")

# Main Interface
st.title("🎓 AI Study Assistant")
# ADDED: Motivation Title
st.markdown("<h3 class='motivation-title'>✨ Dream Big, Study Hard, Achieve More! ✨</h3>", unsafe_allow_html=True)

st.caption("Upload notes, PDFs, or images and instantly generate study materials.")

with st.expander("🔑 Gemini API Settings"):
    api_key = st.text_input("Enter Gemini API Key", type="password")

# Upload and Input
col1, col2 = st.columns(2)
with col1:
    uploaded_files = st.file_uploader("📸 Upload Materials", type=["jpg", "png", "pdf"], accept_multiple_files=True)
with col2:
    notes = st.text_area("📝 Or paste notes here", height=100)

# Process Content
combined_text = notes + "\n"
if uploaded_files:
    for file in uploaded_files:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            for page in reader.pages:
                text = page.extract_text()
                if text: combined_text += text + "\n"
st.session_state.content = combined_text

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📝 Summary", "❓ Questions", "✅ Quiz Mode", "🃏 Flashcards"])

def generate_ai_content(prompt_type):
    if not api_key:
        st.error("Please enter your API Key in the settings expander.")
        return
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        with st.spinner(f"🤖 AI is crafting your {prompt_type}..."):
            contents = [f"""
            Task: Generate {prompt_type}.
            Difficulty Level: {difficulty}.
            Context/Notes: {st.session_state.content}
            IMPORTANT: Return as CLEAN PLAIN TEXT. No Markdown or bold asterisks.
            """]
            
            if uploaded_files:
                for file in uploaded_files:
                    if file.type.startswith("image"):
                        file.seek(0)
                        contents.append(Image.open(file))
            
            response = model.generate_content(contents)
            st.success("✨ Content generated successfully!")
            st.info(response.text)
            st.download_button("Download Result", response.text, file_name="study_material.txt")
            
    except Exception as e:
        if "429" in str(e):
            st.error("🚫 API limit reached. Please wait a moment.")
        else:
            st.error(f"Error: {e}")

with tab1:
    if st.button("Generate Summary"): generate_ai_content("a simple summary")
with tab2:
    if st.button("Generate Important Questions"): generate_ai_content("5 key study questions")
with tab3:
    st.write("### 🧠 AI Quiz Mode")
    if st.button("Start Quiz"): generate_ai_content("10 MCQs with answers")
with tab4:
    if st.button("Generate Flashcards"): generate_ai_content("10 Flashcards")

st.markdown("---")
st.caption("Built with Streamlit + Gemini AI")