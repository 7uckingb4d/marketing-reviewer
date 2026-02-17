import streamlit as st
from groq import Groq
from pypdf import PdfReader

# 1. INITIALIZE SESSION (Gawin muna ito para hindi mag-blank)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. UI & CLEAN CSS
st.set_page_config(page_title="PLV MM Reviewer", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f0c29; color: white; }
    #MainMenu, footer, header { visibility: hidden; }
    .stChatMessage { background: rgba(255, 255, 255, 0.05) !important; border-radius: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. SIDEBAR
with st.sidebar:
    st.markdown("### 🎓 Academic Hub")
    mode = st.radio("Choose Priority:", ["Law of ObliCon", "Business Research"])
    st.markdown("---")
    uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
    if st.button("✨ Clear Session"):
        st.session_state.messages = []
        st.rerun()

# 4. GREETING (Para laging may laman ang screen)
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant", 
        "content": f"Hi Misaki! Law Buddy is here. Ready na for **{mode}**. Chill lang tayo, no nosebleed promises! Ano'ng aaralin natin? ✨"
    })

# 5. DISPLAY MESSAGES (Dito na lalabas yung chat bubbles)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. PDF TEXT EXTRACTION (Lazy)
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

# 7. AI INTERACTION (Sa dulo para hindi maka-block)
if prompt := st.chat_input("Ask your PLV Buddy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_res = ""
        
        try:
            # Check API Key inside the interaction to avoid blocking the UI
            if "GROQ_API_KEY" not in st.secrets:
                st.error("❌ Error: Missing 'GROQ_API_KEY' in Streamlit Secrets.")
                st.stop()
            
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            # System instructions focused on simplicity
            system_prompt = f"""
            You are MKTG Law Buddy, a supportive tutor for Misaki, a PLV Marketing student.
            Mode: {mode}. 
            Context: {context_text}
            
            STRICT RULES:
            - AVOID BIG WORDS. Explain like you're talking to a friend.
            - Use simple Taglish.
            - Use Shopee, Lazada, or TikTok analogies for Law and Research.
            - Help her memorize ObliCon articles using witty shortcuts.
            """

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                stream=True,
            )
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    full_res += content
                    placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
        except Exception as e:
            st.error(f"⚠️ May problem sa connection: {str(e)}")
