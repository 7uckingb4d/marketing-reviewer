import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. Page Config
st.set_page_config(page_title="Marketing Law Reviewer", page_icon="⚖️")
st.title("⚖️ Marketing Law Reviewer")

# 2. Sidebar Upload
with st.sidebar:
    st.header("Upload PDF Notes")
    uploaded_files = st.file_uploader("Drop PDF here", type="pdf", accept_multiple_files=True)
    if st.button("Clear Chat"):
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

# 4. Load Context
if uploaded_files:
    context_text = get_pdf_text(uploaded_files)
    st.sidebar.success("✅ Notes Loaded!")
else:
    context_text = ""

# 5. API Key Setup
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # FIX: Gamitin ang 'gemini-pro' (Mas stable ito kaysa flash)
        model = genai.GenerativeModel('gemini-pro')
    else:
        st.error("⚠️ Error: Wala pang API Key sa Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Connection Error: {e}")

# 6. Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Upload ka ng PDF o magtanong ka na."}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. Main Logic
if user_input := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Show "Thinking..." spinner
    with st.spinner("Nag-iisip si AI..."):
        try:
            # Fallback logic: Kung walang PDF, sasagot pa rin siya (General Knowledge)
            if not context_text:
                system_prompt = f"You are a helpful tutor. User asks: {user_input}"
            else:
                system_prompt = f"""
                ROLE: Marketing Tutor.
                CONTEXT: {context_text}
                QUESTION: {user_input}
                """
            
            # Generate Reply
            response = model.generate_content(system_prompt)
            response_text = response.text
            
        except Exception as e:
            response_text = f"❌ Error: {e}"

    with st.chat_message("assistant"):
        st.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
