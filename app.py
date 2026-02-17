import streamlit as st
from groq import Groq
from pypdf import PdfReader

# 1. CLEAN & PROFESSIONAL UI
st.set_page_config(page_title="PLV MM Reviewer", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    .stChatMessage { background: rgba(255, 255, 255, 0.05) !important; border-radius: 15px !important; }
    .stButton>button { background: #d4af37; color: black; font-weight: bold; border-radius: 20px; border: none; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR - SUBJECT SELECTION
with st.sidebar:
    st.markdown("### 🎓 Academic Hub")
    mode = st.radio("Choose Priority:", ["Law of ObliCon", "Business Research"])
    st.markdown("---")
    uploaded_files = st.file_uploader("Upload PDFs (Notes/Research)", type="pdf", accept_multiple_files=True)
    if st.button("✨ Clear Session"):
        st.session_state.messages = []
        st.rerun()

# 3. PDF PROCESSING
def get_pdf_text(files):
    text = ""
    for pdf in files:
        try:
            reader = PdfReader(pdf)
            for page in reader.pages:
                text += page.extract_text()
        except: continue
    return text

context_text = get_pdf_text(uploaded_files) if uploaded_files else ""

# 4. GROQ ENGINE
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Check Secrets Configuration.")
    st.stop()

# 5. SPECIALIZED SYSTEM PROMPT (The "Brain" Upgrade)
SYSTEM_IDENTITY = f"""
You are the personal AI Academic Tutor for Misaki, a BSBA Marketing Management student at PLV.
Current Mode: {mode}
CONTEXT: {context_text}

STRICT OBJECTIVES:
1. FOR OBLICON: Focus on memorization techniques. Use mnemonics, situational examples (cases), and quizzes to help her memorize articles.
2. FOR BUSINESS RESEARCH: Provide well-structured guidance. Help with sources, APA/MLA formatting, and conceptual frameworks. Ensure all formats are professional and academically sound.
3. TONE: Witty, supportive Taglish. Speak like a senior PLV student helping a junior.
4. MARKETING ANGLE: Always link Law and Research to Marketing Management (e.g., contracts in advertising, consumer behavior research).
"""
