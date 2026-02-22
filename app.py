import streamlit as st
import google.generativeai as genai
import requests
import json
from datetime import datetime

st.set_page_config(page_title="Ewano AI Agent", layout="wide")
st.title("🕷️ ایجنت هوشمند: تستر، مستندساز و نقشه‌کش")

with st.sidebar:
    api_key = st.text_input("Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
    
    st.header("⚙️ استانداردهای ساخت Postman")
    collection_architecture = st.selectbox(
        "معماری فولدرهای Postman:",
        ["Domain-Driven", "Method-Based", "User Journey"]
    )
    st.header("🔑 احراز هویت API")
    token = st.text_input("Token (Bearer):", type="password")

if 'api_logs' not in st.session_state:
    st.session_state['api_logs'] = []

target_url = st.text_input("آدرس API برای بررسی ایجنت:", "https://api.ewano.app/v1/profile")

if st.button("🚀 شروع کار ایجنت"):
    if not api_key:
        st.error("کلید هوش مصنوعی نیاز است.")
    else:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        with st.spinner("ایجنت در حال اجرای تست..."):
            try:
                response = requests.get(target_url, headers=headers, timeout=10)
                
                log_entry = {
                    "time": str(datetime.now()),
                    "url": target_url,
                    "status": response.status_code,
                }
                st.session_state['api_logs'].append(log_entry)
                st.success(f"تست انجام شد. کد وضعیت: {response.status_code}")
                
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                You are an Expert API Architect. I will give you an API response.
                Return a JSON object with TWO main keys:
                1. "postman_item": A valid Postman v2.1 Item JSON. Architecture: {collection_architecture}.
                2. "graph_nodes": Identify core entities for an architectural map.
                API URL: {target_url}
                API Response: {response.text[:2000]}
                Return ONLY valid JSON.
                """
                
                with st.spinner("در حال ساخت کالکشن و نقشه..."):
                    ai_response = model.generate_content(prompt)
                    raw_text = ai_response.text.replace('```json', '').replace('```', '')
                    parsed_data = json.loads(raw_text)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("📦 خروجی Postman")
                        st.json(parsed_data.get("postman_item", {}))
                    with col2:
                        st.subheader("🗺️ دیتای نقشه")
                        st.json(parsed_data.get("graph_nodes", {}))

            except Exception as e:
                st.error(f"خطا در عملکرد ایجنت: {e}")
