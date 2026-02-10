import streamlit as st
import google.generativeai as genai

st.title("🔍 Model Scanner (System Check)")

# 1. API Key Check
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    st.success("✅ API Key Found!")
except Exception as e:
    st.error(f"❌ API Key Error: {e}")
    st.stop()

# 2. Check Library Version
import importlib.metadata
try:
    version = importlib.metadata.version("google-generativeai")
    st.write(f"📚 Google Library Version: **{version}**")
except:
    st.write("📚 Library Version: Unknown")

# 3. List Available Models
st.write("---")
st.header("📋 Available Models for YOU:")
st.write("Kung walang lumabas dito, ibig sabihin kailangan i-update ang requirements.txt")

try:
    count = 0
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            st.code(m.name) # Kopyahin mo kung ano ang lumabas dito!
            count += 1
    
    if count == 0:
        st.warning("⚠️ Walang nakitang model. Luma ang library.")
        
except Exception as e:
    st.error(f"❌ Error Scanning Models: {e}")
