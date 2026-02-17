import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. Branding & UI
st.set_page_config(page_title="MKTG Law Buddy", page_icon="⚖️")

# Itatago natin ang menu para mukhang app talaga
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar
with st.sidebar:
    st.title("⚖️ MKTG Law Buddy")
    st.subheader("For Misaki ❤️")
    st.markdown("---")
    uploaded_files = st.file_uploader("Upload PDF Notes", type="pdf", accept_multiple_files=True)
    if st.button("Reset Session"):
        st.session_state.messages = []
        st.rerun()

# 3. PDF Reader
def get_pdf_text(files):
    text = ""
    for pdf in files:
        reader = PdfReader(pdf)
        for page in reader.pages:
            text += page.extract_text()
    return text

context_text = get_pdf_text(uploaded_files) if uploaded_files else ""

# 4. API Setup
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Gamitin natin ang gemini-1.5-flash dahil ito ang pinaka-stable sa PDF
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction="You are MKTG Law Buddy, a dedicated Marketing Reviewer for Misaki. You are NOT Gemini or an AI from Google. Answer in supportive Taglish using marketing analogies."
        )
    else:
        st.error("Missing API Key in Secrets.")
        st.stop()
except Exception as e:
    st.error("System configuration error.")
    st.stop()

# 5. Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello Misaki! I am your MKTG Law Buddy. Upload mo na yung PDFs mo para masimulan na natin ang session! ✨"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Chat Logic (Simplified)
if prompt := st.chat_input("Ask your MKTG Law Buddy..."):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                # Isama ang PDF context sa prompt
                full_prompt = f"Context from notes: {context_text}\n\nUser Question: {prompt}"
                response = model.generate_content(full_prompt)
                
                if response.text:
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                else:
                    st.error("Buddy is shy. Please try rephrasing.")
            except Exception as e:
                st.error("Buddy had a small hiccup. Try again!")
