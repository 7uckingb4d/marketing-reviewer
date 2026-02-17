import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. Branding
st.set_page_config(page_title="MKTG Law Buddy", page_icon="⚖️")

# 2. Sidebar
with st.sidebar:
    st.title("⚖️ MKTG Law Buddy")
    st.subheader("For Misaki ❤️")
    uploaded_files = st.file_uploader("Upload PDF Notes", type="pdf", accept_multiple_files=True)
    if st.button("Reset Session"):
        st.session_state.messages = []
        st.rerun()

# 3. PDF Function
def get_pdf_text(files):
    text = ""
    for pdf in files:
        reader = PdfReader(pdf)
        for page in reader.pages:
            text += page.extract_text()
    return text

context_text = get_pdf_text(uploaded_files) if uploaded_files else ""

# 4. API Setup (Using confirmed model from your scan)
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Ginamit natin yung model na lumabas sa listahan mo kanina
        model = genai.GenerativeModel('gemini-3-flash-preview') 
    else:
        st.error("Missing API Key in Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Config Error: {e}")

# 5. Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi Misaki! Ready na ako. Upload mo na yung notes mo para makapagsimula tayo! ✨"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Chat Logic with Debugging
if prompt := st.chat_input("Ask your MKTG Law Buddy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Prompt Engineering to hide Gemini identity
                system_instruction = f"""
                You are MKTG Law Buddy, a marketing reviewer app for Misaki. 
                Answer using this context: {context_text}
                Speak in supportive Taglish. Be witty.
                """
                
                response = model.generate_content([system_instruction, prompt])
                
                if response.text:
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                else:
                    st.warning("No response generated. Safety filters might be blocking this.")
                    
            except Exception as e:
                # Ito yung magsasabi sa atin kung bakit may 'hiccup'
                st.error(f"❌ Real Error: {e}") 
                st.info("Check if your API Key is still valid or if the model name is correct.")
