import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import time
from datetime import datetime, timedelta

# 1. SESSION STATE INITIALIZATION
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Security States
if "attempts_left" not in st.session_state:
    st.session_state.attempts_left = 3  # Start with 3 lives
if "lockout_end" not in st.session_state:
    st.session_state.lockout_end = None # Walang lockout sa simula
if "penalty_add" not in st.session_state:
    st.session_state.penalty_add = 0    # Walang dagdag na oras sa simula

# 2. LOGIN SCREEN CONTROLLER
if not st.session_state.logged_in:
    st.set_page_config(page_title="Secure Login", page_icon="🔒")
    
    st.markdown("""
        <style>
        .stApp { background-color: #0f0c29; color: white; text-align: center; }
        .error-box { background-color: #ff4b4b; padding: 10px; border-radius: 10px; color: white; }
        .timer-box { font-size: 24px; font-weight: bold; color: #ffd700; }
        </style>
        """, unsafe_allow_html=True)

    st.title("🔒 Academic Hub Access")
    st.write("Authorized Personnel Only (Misaki)")

    # CHECK LOCKOUT STATUS
    if st.session_state.lockout_end:
        remaining = (st.session_state.lockout_end - datetime.now()).total_seconds()
        
        if remaining > 0:
            # Show Countdown
            st.error("⚠️ SYSTEM LOCKED: Too many failed attempts.")
            st.markdown(f"<div class='timer-box'>Try again in {int(remaining)} seconds</div>", unsafe_allow_html=True)
            time.sleep(1) # Live countdown effect
            st.rerun()    # Refresh page every second
        else:
            # Lockout Expired - Reset for 1 attempt only
            st.session_state.lockout_end = None
            st.session_state.attempts_left = 1 # "GANG MAGING 1 NA LANG" rule
            st.info("System unlocked. You have 1 attempt remaining.")

    # LOGIN FORM
    with st.form("login_form"):
        # Credentials from Secrets
        correct_user = st.secrets["LOGIN_USER"]
        correct_pass = st.secrets["LOGIN_PASS"]
        
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Unlock System")

        if submitted:
            if user == correct_user and password == correct_pass:
                st.session_state.logged_in = True
                st.session_state.attempts_left = 3 # Reset attempts on success
                st.session_state.penalty_add = 0   # Reset penalty
                st.success("Access Granted! Welcome back.")
                time.sleep(1)
                st.rerun()
            else:
                # DEDUCT ATTEMPT
                st.session_state.attempts_left -= 1
                
                if st.session_state.attempts_left <= 0:
                    # TRIGGER LOCKOUT
                    base_time = 30
                    total_lockout = base_time + st.session_state.penalty_add
                    
                    st.session_state.lockout_end = datetime.now() + timedelta(seconds=total_lockout)
                    st.session_state.penalty_add += 10 # "+10 SECS PER MALI" rule
                    
                    st.error(f"❌ Locked out for {total_lockout} seconds!")
                    st.rerun()
                else:
                    st.warning(f"❌ Access Denied. {st.session_state.attempts_left} attempts remaining.")

    st.stop() # Stop here if not logged in

# ==========================================
# 3. MAIN APP (PLV REVIEWER NI MISAKI)
# ==========================================
st.set_page_config(page_title="PLV MM Reviewer", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f0c29; color: white; }
    .stChatMessage { background: rgba(255, 255, 255, 0.05) !important; border-radius: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎓 Academic Hub")
    if st.button("🔒 Logout"):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown("---")
    mode = st.radio("Priority Subject:", ["Law of ObliCon", "Business Research"])
    uploaded_files = st.file_uploader("Upload Notes (PDF)", type="pdf", accept_multiple_files=True)
    if st.button("✨ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# PDF Logic
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

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": f"Hi Misaki! Ready for {mode}? No nosebleed review tayo! ✨"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask PLV Buddy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            sys_msg = f"""
            Role: Tutor for Misaki (PLV Marketing Student).
            Topic: {mode}. Context: {context_text}.
            Rules: Simple Taglish, No big words, Shopee/Lazada analogies.
            """
            
            response = model.generate_content([sys_msg, prompt])
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"System Error: {str(e)}")
