import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. AUTHENTICATION LOGIC (Simple but Secure)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

# 2. LOGIN SCREEN
if not st.session_state.logged_in:
    st.set_page_config(page_title="PLV Reviewer Login", page_icon="🔒")
    
    # Simple CSS for Login Box
    st.markdown("""
        <style>
        .stApp { background-color: #0f0c29; color: white; text-align: center; }
        .login-box { padding: 50px; border-radius: 20px; background: rgba(255,255,255,0.05); }
        </style>
        """, unsafe_allow_html=True)

    st.title("🔒 Academic Hub Login")
    
    if st.session_state.attempts >= 3:
        st.error("Too many failed attempts. Locked for security. Refresh the page to try again.")
        st.stop()

    with st.container():
        st.write("Specialized Reviewer for **Misaki** (BSBA-MM) ❤️")
        
        # Kunin ang credentials mula sa Secrets para hindi ma-leak sa GitHub
        correct_user = st.secrets["LOGIN_USER"]
        correct_pass = st.secrets["LOGIN_PASS"]
        
        user_input = st.text_input("Username")
        pass_input = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if user_input == correct_user and pass_input == correct_pass:
                st.session_state.logged_in = True
                st.success("Welcome back, Misaki!")
                st.rerun()
            else:
                st.session_state.attempts += 1
                st.error(f"WRONG CREDENTIALS {3 - st.session_state.attempts} attempts left.")
    st.stop()

# 3. MAIN APP (PLV MM REVIEWER) - Dito papasok pag naka-login na
st.set_page_config(page_title="PLV MM Reviewer", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f0c29; color: white; }
    .stChatMessage { background: rgba(255, 255, 255, 0.05) !important; border-radius: 15px !important; }
    .stButton>button { background: #d4af37; color: black; font-weight: bold; border-radius: 20px; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎓 Academic Hub")
    # Priority subjects for Misaki's marketing course
    mode = st.radio("Choose Priority:", ["Law of ObliCon", "Business Research"])
    st.markdown("---")
    uploaded_files = st.file_uploader("Upload Notes (PDF)", type="pdf", accept_multiple_files=True)
    if st.button("✨ Clear Session"):
        st.session_state.messages = []
        st.rerun()

# 4. PDF EXTRACTION
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

# 5. GEMINI 2.5 FLASH ENGINE
if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = [{"role": "assistant", "content": f"Hi Misaki! Ready na ako for {mode}. No nosebleed, chill review lang! ✨"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask your PLV Buddy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Integrated "No Overwhelming Words" policy
            system_prompt = f"""
            You are MKTG Law Buddy for Misaki, a PLV Marketing student.
            Subject: {mode}. 
            Context: {context_text}
            
            RULES:
            - AVOID BIG WORDS. Explain like you're her classmate.
            - Use simple Taglish.
            - Use Shopee/Lazada analogies for Law and Research.
            - Help her memorize Law of Obligations and Contracts via mnemonics.
            - Provide clear, well-structured research formats for Business Research.
            """

            response = model.generate_content([system_prompt, prompt])
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
                
        except Exception as e:
            st.error
