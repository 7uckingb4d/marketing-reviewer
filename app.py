import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from twilio.rest import Client
import random
import datetime # Para sa 4-hour check

# 1. AUTHENTICATION & SECURITY SETUP
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "attempts" not in st.session_state:
    st.session_state.attempts = 0
if "generated_pin" not in st.session_state:
    st.session_state.generated_pin = None
if "pin_time" not in st.session_state:
    st.session_state.pin_time = None

def send_pin():
    try:
        # Generate random 4-digit PIN
        pin = str(random.randint(1000, 9999))
        st.session_state.generated_pin = pin
        st.session_state.pin_time = datetime.datetime.now() # Record time sent
        st.session_state.attempts = 0 # Reset attempts for new PIN
        
        # Twilio SMS
        client = Client(st.secrets["TWILIO_SID"], st.secrets["TWILIO_TOKEN"])
        client.messages.create(
            body=f"Law Buddy PIN: {pin}. Valid for 4 hours only. ❤️",
            from_=st.secrets["TWILIO_FROM"],
            to=st.secrets["MISAKI_NUMBER"]
        )
        st.success("PIN sent to Misaki's number! Check your messages. 📱")
    except Exception as e:
        st.error(f"Failed to send SMS: {e}")

# 2. LOGIN SCREEN
if not st.session_state.logged_in:
    st.set_page_config(page_title="Secure Login", page_icon="🔒")
    st.title("🔒 Law Buddy Pro: Login")
    
    # 3-Attempt Lockout
    if st.session_state.attempts >= 3:
        st.error("Too many failed attempts. Please refresh the page and request a new PIN.")
        st.stop()

    st.info("Academic Hub for PLV Marketing Management. Request a PIN to continue.") #
    
    if st.button("Request New PIN"):
        send_pin()

    user_pin = st.text_input("Enter 4-Digit PIN", type="password")
    
    if st.button("Verify PIN"):
        if st.session_state.generated_pin and st.session_state.pin_time:
            # Check Time Validity (4 Hours)
            current_time = datetime.datetime.now()
            time_diff = current_time - st.session_state.pin_time
            
            # 4 hours = 14400 seconds
            if time_diff.total_seconds() > 14400:
                st.error("Expired na 'yung PIN. Request ka ulet ng bago, Misaki. ⏰")
                st.session_state.generated_pin = None
            elif user_pin == st.session_state.generated_pin:
                st.session_state.logged_in = True
                st.success("Access Granted! Welcome back! ✨")
                st.rerun()
            else:
                st.session_state.attempts += 1
                st.error(f"Wrong PIN. {3 - st.session_state.attempts} tries left.")
        else:
            st.warning("Please request a PIN first.")
    st.stop()

# 3. MAIN APP (PLV MM REVIEWER)
st.set_page_config(page_title="PLV MM Reviewer", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f0c29; color: white; }
    .stChatMessage { background: rgba(255, 255, 255, 0.05) !important; border-radius: 15px !important; }
    .stButton>button { background: #d4af37; color: black; font-weight: bold; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎓 Academic Hub")
    mode = st.radio("Choose Priority:", ["Law of ObliCon", "Business Research"])
    st.markdown("---")
    uploaded_files = st.file_uploader("Upload Notes (PDF)", type="pdf", accept_multiple_files=True)
    if st.button("✨ Reset Session"):
        st.session_state.messages = []
        st.rerun()

# (Rest of the Gemini 2.5 Flash chat code goes here...)
