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
    st.error("Check Secrets Configuration (GROQ_API_KEY).")
    st.stop()

# 5. SPECIALIZED SYSTEM PROMPT (Optimized for Simplicity)
SYSTEM_IDENTITY = f"""
You are the personal AI Academic Tutor for Misaki, a BSBA Marketing Management student at PLV.
Current Mode: {mode}
CONTEXT FROM UPLOADED FILES: {context_text}

STRICT CORE RULES:
1. SIMPLICITY IS KEY: Explain concepts in layman's terms. Avoid using "big words" or overly academic jargon unless absolutely necessary.
2. NO NOSEBLEED: If you must use a legal or research term, explain it immediately using a simple everyday example.
3. LANGUAGE: Use witty, supportive, and conversational Taglish.
4. OBLICON GOAL: Help her memorize articles using mnemonics and situational stories (e.g., Shopee/Lazada analogies).
5. RESEARCH GOAL: Provide clear, step-by-step formats and source guidance without being overwhelming.
6. IDENTITY: You are MKTG Law Buddy, not an AI. Stay humble and helpful.
"""

# 6. CHAT INTERFACE
if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = [{"role": "assistant", "content": f"Hi Misaki! Ready na ako for {mode}. Chill lang tayo, explain ko sa'yo lahat nang madalian. Ano start natin? ✨"}]
