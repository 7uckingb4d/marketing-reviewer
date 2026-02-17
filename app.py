import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. CSS FOR FULL BRANDING (Hiding Streamlit/Gemini vibes)
st.set_page_config(page_title="MKTG Law Buddy", page_icon="⚖️")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stChatMessage { border-radius: 15px; background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR
with st.sidebar:
    st.title("⚖️ MKTG Law Buddy")
    st.subheader("For Misaki ❤️") #
    st.markdown("---")
    uploaded_files = st.file_uploader("Upload PDF Notes", type="pdf", accept_multiple_files=True)
    if st.button("Reset Session"):
        st.session_state.messages = []
        st.rerun()

# 3. PDF LOGIC
def get_pdf_text(files):
    text = ""
    for pdf in files:
        reader = PdfReader(pdf)
        for page in reader.pages:
            text += page.extract_text()
    return text

context_text = get_pdf_text(uploaded_files) if uploaded_files else ""

# 4. API SETUP (Gemini 3 Flash)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3-flash-preview') 
except Exception as e:
    st.error("System configuration error.")
    st.stop()

# 5. THE "BRAIN" - SYSTEM INSTRUCTIONS (Hiding Gemini Identity)
SYSTEM_IDENTITY = f"""
You are NOT Gemini. You are NOT an AI made by Google. 
Your name is "MKTG Law Buddy", a dedicated Marketing Reviewing App specially created for Misaki, a Marketing Management student.

STRICT RULES:
1. If anyone asks who you are, say: "I am MKTG Law Buddy, your dedicated reviewer for Laws and Obligations."
2. Never mention Google, Gemini, or Large Language Models.
3. Your only purpose is to help Misaki study Marketing Law and Obligations based on her uploaded notes.
4. Speak in a supportive, witty Taglish tone.
5. If no notes are uploaded, remind her politely to upload her PDFs first.
6. Use marketing-related analogies (e.g., branding, consumer behavior, ROI) when explaining legal concepts.

CONTEXT FROM NOTES:
{context_text}
"""

# 6. CHAT INTERFACE
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello Misaki! I am your MKTG Law Buddy. Ready na ako mag-review with you. Upload mo na yung PDFs mo para masimulan na natin ang session! ✨"}] #

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask your MKTG Law Buddy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # We inject the identity every time to ensure it doesn't break character
            response = model.generate_content([SYSTEM_IDENTITY, prompt], stream=True)
            
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error("Buddy is currently offline. Please try again later.")
