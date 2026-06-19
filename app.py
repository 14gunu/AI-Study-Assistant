import streamlit as st
import google.generativeai as genai
from PIL import Image
from pypdf import PdfReader

# 1. Page Configuration (Must be first)
st.set_page_config(page_title="AI Study Assistant", page_icon="📚", layout="wide")

# 2. Styling
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stTextArea, .stFileUploader { background-color: #262730; }
    .stButton>button { background-color: #ff4b4b; color: white; border-radius: 8px; border: none; }
    div[data-testid="stExpander"] { background-color: #1e1e2e; border: none; }
</style>
""", unsafe_allow_html=True)

# 3. Session State
if 'content' not in st.session_state: st.session_state.content = ""

# 4. Main Interface
st.title("📚 AI Study Assistant")
st.caption("Upload notes, PDFs, or images and instantly generate summaries, MCQs, questions, and flashcards.")

with st.expander("🔑 Gemini API Settings"):
    api_key = st.text_input("Enter Gemini API Key", type="password")

st.markdown("### Upload your study materials")
col1, col2 = st.columns(2)
with col1:
    uploaded_files = st.file_uploader("📸 Upload Multiple Images or PDFs", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)
with col2:
    notes = st.text_area("📝 Or paste your notes here", height=150)

# 5. Content Logic
combined_text = notes + "\n"
if uploaded_files:
    for file in uploaded_files:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            for page in reader.pages:
                text = page.extract_text()
                if text: combined_text += text + "\n"
    st.success("✅ Files processed successfully")

st.session_state.content = combined_text

# 6. Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📝 Summary", "❓ Questions", "✅ MCQs", "🃏 Flashcards"])

def generate_ai_content(prompt_type):
    if not api_key:
        st.error("Please enter your Gemini API Key in the settings expander above.")
        return
    
    try:
        genai.configure(api_key=api_key)
        # Using the most stable model identifier
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        contents = [f"""
        Task: Generate {prompt_type}.
        Context: {st.session_state.content}
        IMPORTANT: Return the output as CLEAN PLAIN TEXT. 
        Do NOT use Markdown, bold asterisks, or headings.
        """]
        
        if uploaded_files:
            for file in uploaded_files:
                if file.type.startswith("image"):
                    contents.append(Image.open(file))
        
        response = model.generate_content(contents)
        st.success("✨ Content generated successfully!")
        st.info(response.text)
        st.download_button("Download Result", response.text, file_name=f"{prompt_type.replace(' ', '_')}.txt")
        
    except Exception as e:
        if "429" in str(e):
            st.error("🚫 API limit reached. Wait a while or check your key.")
        else:
            st.error(f"Error: {e}")

with tab1:
    if st.button("Generate Summary"): generate_ai_content("a simple summary")
with tab2:
    if st.button("Generate 5 Important Questions"): generate_ai_content("5 important questions")
with tab3:
    if st.button("Generate MCQs"): generate_ai_content("10 MCQs with 4 options each and correct answers")
with tab4:
    if st.button("Generate Flashcards"): generate_ai_content("10 flashcards in Question : Answer format")

# 7. Footer
st.markdown("---")
st.caption("Built with Streamlit + Gemini AI")