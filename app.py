import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import time

# 1. PREMIUM UI CONFIGURATION
st.set_page_config(page_title="MKTG Law Buddy Pro", page_icon="💎", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #ffffff;
    }
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    /* Chat Message Bubbles */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    /* Gold Accent for Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #d4af37, #f9d423);
        color: #000;
        font-weight: bold;
        border: none;
        border-radius: 25px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px #f9d423;
    }
    /* Input Bar */
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR - PERSONALIZED
with st.sidebar:
    st.title("⚖️ Law Buddy Pro")
    st.markdown("### *Exclusive for Misaki*") #
    st.write("Specialized AI for **Marketing Management** studies.")
    st.markdown("---")
    uploaded_files = st.file_uploader("Upload Case Studies or Notes (PDF)", type="pdf", accept_multiple_files=True)
    if st.button("✨ Refresh Session"):
        st.session_state.messages = []
        st.rerun()

# 3. PDF PROCESSING
def get_pdf_text(files):
    text = ""
    for pdf in files:
        reader = PdfReader(pdf)
        for page in reader.pages:
            text += page.extract_text()
    return text

context_text = get_pdf_text(uploaded_files) if uploaded_files else ""

# 4. THE ULTIMATE BRAIN (Gemini 3 Pro)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Using the most powerful model from your scan
    model = genai.GenerativeModel('gemini-3-pro-preview') 
except Exception as e:
    st.error("System connection error. Check API configuration.")
    st.stop()

# 5. CHAT ENGINE
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to your premium review experience, Misaki. I am Law Buddy Pro, optimized for your Marketing Management modules. How can I assist you today? ✨"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask your expert tutor..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Expert System Instruction
        identity = f"""
        IDENTITY: You are Law Buddy Pro, a world-class Legal & Marketing Consultant. 
        PURPOSE: Assist Misaki, a Marketing Management student, in mastering Laws and Obligations.
        TONE: Sophisticated, insightful, and supportive Taglish.
        SOURCE: Use this provided context: {context_text}
        
        INSTRUCTIONS:
        - Provide deep analysis, not just definitions.
        - Relate every legal article to marketing strategy, consumer behavior, or branding.
        - If Misaki asks for a quiz, give a "Harvard Business Case" style situational problem.
        - NEVER identify as Gemini or Google. You are a bespoke tutor created for Misaki.
        """

        try:
            # High-speed streaming
            response = model.generate_content([identity, prompt], stream=True)
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error("The system is busy analyzing complex data. Please try again.")
