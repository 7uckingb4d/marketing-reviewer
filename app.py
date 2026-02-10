import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# Page Setup
st.set_page_config(page_title="Marketing Law Reviewer", page_icon="⚖️")
st.title("⚖️ Marketing Law Reviewer")

# Sidebar
with st.sidebar:
    st.header("Upload PDF Notes")
    uploaded_files = st.file_uploader("Drop PDF here", type="pdf", accept_multiple_files=True)

# PDF Logic
def get_pdf_text(files):
    text = ""
    for pdf in files:
        reader = PdfReader(pdf)
        for page in reader.pages:
            text += page.extract_text()
    return text

if uploaded_files:
    context_text = get_pdf_text(uploaded_files)
    st.sidebar.success("✅ Notes Loaded!")
else:
    context_text = ""

# API Setup
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Eto ang gagamitin natin, sureball sa latest library
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("⚠️ Wala pang API Key.")
        st.stop()
except Exception as e:
    st.error(f"Connection Error: {e}")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Upload ka ng notes o magtanong ka na."}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI Reply
    if not context_text:
        # Fallback kung walang PDF
        full_prompt = f"User Question: {user_input}"
    else:
        full_prompt = f"Context: {context_text}\n\nQuestion: {user_input}\nAnswer in Taglish:"

    try:
        response = model.generate_content(full_prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        with st.chat_message("assistant"):
            st.markdown(response.text)
    except Exception as e:
        st.error(f"Error: {e}")
