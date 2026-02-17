import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. PREMIUM UI
st.set_page_config(page_title="MKTG Law Buddy Pro", page_icon="💎")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    .stChatMessage { background: rgba(255, 255, 255, 0.05) !important; border-radius: 15px !important; }
    .stButton>button { background: #d4af37; color: black; font-weight: bold; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR
with st.sidebar:
    st.title("⚖️ Law Buddy Pro")
    st.write("Specialized for **Misaki** ❤️")
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

# 4. STABLE API SETUP (Gemini 2.0 Flash)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Ginamit natin ang 2.0 Flash dahil ito ang pinaka-stable sa listahan mo
    model = genai.GenerativeModel('gemini-2.0-flash') 
except Exception as e:
    st.error("Connection Error.")

# 5. CHAT ENGINE
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome, Misaki. Ready na ako mag-review. Upload mo lang notes mo! ✨"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask Law Buddy Pro..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Simple but Effective Persona
            full_prompt = f"System: You are Law Buddy Pro for Misaki (Marketing student). Context: {context_text}\n\nQuestion: {prompt}\nAnswer in Taglish:"
            
            # Non-streaming for stability
            response = model.generate_content(full_prompt)
            
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.error("Empty response. Try again.")
                
        except Exception as e:
            # Ipinapakita na ang TUNAY na error para ma-debug natin
            st.error(f"❌ Error Detail: {e}")
