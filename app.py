import streamlit as st
from groq import Groq
from pypdf import PdfReader

# 1. PREMIUM UI (Panatilihin ang branding para kay Misaki)
st.set_page_config(page_title="MKTG Law Buddy Pro", page_icon="⚖️")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460); color: white; }
    .stChatMessage { background: rgba(255, 255, 255, 0.05) !important; border-radius: 15px !important; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR
with st.sidebar:
    st.title("⚖️ Law Buddy Pro")
    st.write("Powered by Llama 3.3 (Non-Gemini) 🚀")
    st.write("For **Misaki** ❤️")
    st.markdown("---")
    uploaded_files = st.file_uploader("Upload Notes (PDF)", type="pdf", accept_multiple_files=True)
    if st.button("Reset Session"):
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

# 4. GROQ API SETUP
try:
    # Palitan mo yung pangalan ng secret sa Streamlit settings: GROQ_API_KEY
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("API Connection failed. Check your Groq Key.")

# 5. CHAT ENGINE
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi Misaki! Law Buddy Pro is back and faster than ever. No more lags! ✨"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask Law Buddy anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Super Persona Logic
        system_input = f"""
        Identity: You are MKTG Law Buddy, an elite reviewer app for Misaki. 
        Context: {context_text}
        Rules: 
        1. Answer in witty Taglish.
        2. Focus on Marketing Management applications.
        3. Never mention you are an AI or Llama. You are 'The Buddy'.
        """

        try:
            # GROQ Inference (Insanely fast)
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_input},
                    {"role": "user", "content": prompt}
                ],
                stream=True,
            )
            
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error("Wait lang, nagre-refresh lang ang system. Try again in a few seconds!")
