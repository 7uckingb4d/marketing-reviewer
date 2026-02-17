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
