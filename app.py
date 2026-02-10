import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. Page Configuration (Para mukhang legit na app)
st.set_page_config(
    page_title="Ms. AIki",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Marketing Law Reviewer AI")
st.caption("Upload your PDF Lecture Notes on the left to start.")

# 2. Sidebar para sa Upload
with st.sidebar:
    st.header("📂 Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload Lecture Notes (PDF)", 
        type="pdf", 
        accept_multiple_files=True
    )
    
    # Button para burahin ang chat pag may bagong topic
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# 3. Function para basahin ang PDF
def get_pdf_text(files):
    text = ""
    for pdf in files:
        reader = PdfReader(pdf)
        for page in reader.pages:
            text += page.extract_text()
    return text

# 4. Load Context (Yung laman ng PDF)
if uploaded_files:
    with st.spinner("Reading notes..."):
        context_text = get_pdf_text(uploaded_files)
    st.sidebar.success(f"Notes Loaded! ✅")
else:
    context_text = ""
    st.sidebar.warning("No PDF uploaded yet.")

# 5. API Key Setup (Kukunin nito yung susi sa Settings ng Streamlit)
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-pro')
    else:
        st.error("⚠️ Wala pang API Key. Ilagay ito sa Streamlit Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Error sa API Key: {e}")

# 6. Chat History (Para hindi mawala ang usapan)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! Upload mo muna yung PDF notes mo sa kaliwa, tapos tanungin mo ako. Pwede rin kitang i-quiz!"}
    ]

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. Main Chat Logic (Ang Utak ng AI)
if user_input := st.chat_input("Ask a question about the law..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Check kung may PDF na
    if not context_text:
        response_text = "Please upload a PDF first so I know what to review!"
    else:
        # System Prompt (Dito natin utusan yung AI)
        system_prompt = f"""
        ROLE: You are an expert Marketing Law Tutor.
        
        INSTRUCTIONS:
        - Answer based ONLY on the provided CONTEXT TEXT.
        - If the user asks for a quiz, give a situational problem relevant to Marketing (Ads, Sales, etc).
        - Use Taglish (Tagalog-English) to be approachable.
        - Cite specific Articles if mentioned in the text.
        
        CONTEXT TEXT:
        {context_text}
        
        USER QUESTION:
        {user_input}
        """
        
        # Generate Answer
# ... (ibang code sa taas)

try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Gamitin natin ito, ito ang pinaka-stable at mabilis
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("⚠️ Wala pang API Key. Ilagay sa Streamlit Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Error sa API Key: {e}")

# ... (ibang code sa baba)
    # Display AI Message
    with st.chat_message("assistant"):
        st.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
