import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. Page Config
st.set_page_config(page_title="Marketing Law Reviewer", page_icon="⚖️")
st.title("⚖️ Marketing Law Reviewer")
st.caption("Powered by Gemini 2.5 Flash")

# 2. Sidebar Upload
with st.sidebar:
    st.header("Upload PDF Notes")
    uploaded_files = st.file_uploader("Drop PDF here", type="pdf", accept_multiple_files=True)
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# 3. PDF Logic
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

# 4. API Setup (Using your available model)
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # GINAMIT NATIN YUNG NASA LISTAHAN MO:
        model = genai.GenerativeModel('gemini-2.5-flash') 
    else:
        st.error("⚠️ Error: Wala pang API Key sa Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Connection Error: {e}")

# 5. Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Upload ka ng notes sa gilid, tapos start na tayo mag-review."}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Main Chat Logic
if user_input := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Show "Thinking..." spinner
    with st.spinner("Analyzing..."):
        try:
            # Fallback logic
            if not context_text:
                full_prompt = f"User Question: {user_input}"
            else:
                full_prompt = f"""
                ROLE: Marketing Law Tutor.
                CONTEXT: {context_text}
                QUESTION: {user_input}
                INSTRUCTION: Answer concisely in Taglish based on the context.
                """
            
            # Generate Reply
            response = model.generate_content(full_prompt)
            response_text = response.text
            
        except Exception as e:
            response_text = f"❌ Error: {e}"

    with st.chat_message("assistant"):
        st.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
