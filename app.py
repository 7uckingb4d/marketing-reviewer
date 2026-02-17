import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import time
from datetime import datetime, timedelta

# ==========================================
# 1. SERVER-SIDE SECURITY (Anti-Refresh Exploit)
# ==========================================
# Ito ang magic. Kahit i-refresh ang page, naka-save sa RAM ng server ang attempts.
@st.cache_resource
class LoginManager:
    def __init__(self):
        self.attempts = {}  # {username: failed_count}
        self.lockouts = {}  # {username: lockout_end_time}

    def check_status(self, user):
        # Clean up expired lockouts
        if user in self.lockouts:
            if datetime.now() > self.lockouts[user]:
                del self.lockouts[user]
                self.attempts[user] = 2 # Pagbalik, 1 attempt na lang (3-2=1)
                return "unlocked", 1
            else:
                remaining = (self.lockouts[user] - datetime.now()).total_seconds()
                return "locked", int(remaining)
        
        # Check attempts
        fails = self.attempts.get(user, 0)
        return "active", 3 - fails

    def record_fail(self, user):
        self.attempts[user] = self.attempts.get(user, 0) + 1
        
        # Logic: Pag naka-3 mali, LOCKOUT AGAD.
        if self.attempts[user] >= 3:
            # Exponential Backoff: 30s, 60s, 120s...
            penalty_level = self.attempts[user] - 3
            wait_time = 30 + (penalty_level * 10) 
            self.lockouts[user] = datetime.now() + timedelta(seconds=wait_time)
            return True # Locked out
        return False

    def reset(self, user):
        if user in self.attempts: del self.attempts[user]
        if user in self.lockouts: del self.lockouts[user]

# Initialize Manager
security = LoginManager()

# ==========================================
# 2. LOGIN PAGE (Clean & Anonymous)
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.set_page_config(page_title="Authorized Access", page_icon="🔒")
    
    st.markdown("""
        <style>
        .stApp { background-color: #1a1a2e; color: white; text-align: center; }
        .timer { color: #e94560; font-size: 20px; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)

    st.title("🔒 Restricted System")
    st.write("Please enter credentials to continue.")

    # Form
    with st.form("entry_form"):
        # Sa secrets, palitan mo na lang yung LOGIN_USER ng generic kung gusto mo
        sys_user = st.secrets["LOGIN_USER"]
        sys_pass = st.secrets["LOGIN_PASS"]
        
        # Status Check bago mag-login
        status, value = security.check_status(sys_user)
        
        user_in = st.text_input("Username")
        pass_in = st.text_input("Password", type="password")
        submit = st.form_submit_button("Authenticate")

        if submit:
            # 1. Check kung LOCKED
            if status == "locked":
                st.error(f"⚠️ Account Temporarily Locked.")
                st.markdown(f"<p class='timer'>Try again in {value} seconds</p>", unsafe_allow_html=True)
            
            # 2. Verify Credentials
            elif user_in == sys_user and pass_in == sys_pass:
                security.reset(sys_user) # Reset counter pag tama
                st.session_state.logged_in = True
                st.success("Access Granted.")
                time.sleep(0.5)
                st.rerun()
                
            # 3. Handle Wrong Password
            else:
                # Record failure sa GLOBAL manager
                is_locked = security.record_fail(sys_user)
                
                if is_locked:
                    st.error("❌ Maximum attempts reached. Locking system...")
                    time.sleep(1)
                    st.rerun()
                else:
                    # Re-check status para makuha remaining attempts
                    _, left = security.check_status(sys_user)
                    st.warning(f"❌ Invalid Credentials. {left} attempt(s) remaining.")

    st.stop()

# ==========================================
# 3. MAIN APP (Generic & Safe)
# ==========================================
st.set_page_config(page_title="PLV Reviewer", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    .stChatMessage { background: rgba(255, 255, 255, 0.05) !important; border-radius: 15px !important; }
    #MainMenu, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📚 Reviewer Hub")
    if st.button("🔒 Logout"):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown("---")
    mode = st.radio("Select Subject:", ["Law of ObliCon", "Business Research"])
    uploaded_files = st.file_uploader("Upload Materials (PDF)", type="pdf", accept_multiple_files=True)
    if st.button("🧹 Clear Chat"):
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
context = get_pdf_text(uploaded_files) if uploaded_files else ""

# Chat Logic
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": f"Hello! Ready to review **{mode}**? Simple terms lang tayo. Let's go! 🚀"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # GENERIC PERSONA (Walang pangalan)
            sys_msg = f"""
            You are a helpful Academic Tutor for a Marketing Management student at PLV.
            Topic: {mode}. 
            Context: {context}
            
            RULES:
            - Speak in casual, supportive Taglish.
            - NO BIG WORDS. Explain like a friend.
            - Use relatable analogies (online shopping, daily life).
            - For ObliCon: Focus on mnemonics.
            - For Research: Focus on simple structures.
            """
            
            response = model.generate_content([sys_msg, prompt])
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"Connection Error: {str(e)}")
