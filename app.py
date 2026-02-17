import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. INITIALIZE SESSION
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. UI & CLEAN CSS
st.set_page_config(page_title="PLV MM Reviewer", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f0c29; color: white; }
    #MainMenu, footer, header { visibility: hidden; }
    .stChatMessage { background: rgba(255, 255, 255, 0.05) !important; border-radius: 15px !important; }
    .stButton>button { background: #d4af37; color: black; font-weight: bold; border-radius: 20px; border: none; }
    </style>
    """, unsafe_allow_html=True)

# 3. SIDEBAR
with st.sidebar:
    st.markdown("### 🎓 Academic Hub")
    # Choosing priorities for Misaki's BSBA MM subjects
    mode = st.radio("Choose Priority:", ["Law of ObliCon", "Business Research"])
    st.markdown("---")
    uploaded_files = st.file_uploader("Upload PDFs (Notes/Research)", type="pdf", accept_multiple_files=True)
    if st.button("✨ Clear Session"):
        st.session_state.messages = []
        st.rerun()

# 4. GREETING (Laging alive ang screen)
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant", 
        "content": f"Hi Misaki! Law Buddy 2.5 is back. Ready na ako for **{mode}**. No big words, chill review lang tayo! ✨"
    })

# 5. DISPLAY MESSAGES
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. PDF PROCESSING
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

# 7. GEMINI 2.5 INTERACTION
if prompt := st.chat_input("Ask your PLV Buddy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Check for Gemini API Key in Secrets
            if "GEMINI_API_KEY" not in st.secrets:
                st.error("❌ Error: Missing 'GEMINI_API_KEY' in Streamlit Secrets.")
                st.stop()
            
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            # Using Gemini 2.5 Flash as requested
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            system_prompt = f"""
            You are MKTG Law Buddy, the personal tutor for Misaki, a PLV Marketing student.
            Current Mode: {mode}. 
            Context: {context_text}
            
            STRICT RULES:
            - AVOID OVERWHELMING HER. Do not use big words.
            - Explain everything like a friend using simple Taglish.
            - Use Shopee, Lazada, or TikTok examples for ObliCon and Research.
            - Help her memorize Law of Obligations and Contracts using shortcuts.
            - Guide her through Business Research with clear, simple formats.
            """

            response = model.generate_content([system_prompt, prompt])
            
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.warning("Buddy is thinking... try again!")
                
        except Exception as e:
            st.error(f"⚠️ Gemini Error: {str(e)}")
