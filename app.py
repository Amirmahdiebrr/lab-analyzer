import streamlit as st
import requests
from PyPDF2 import PdfReader
import io

# ===== تنظیمات =====
HF_TOKEN = "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"  
MODEL_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
# ===== عنوان صفحه =====
st.set_page_config(page_title="تحلیلگر آزمایش", page_icon="🩺")
st.title("🩺 تحلیلگر هوشمند آزمایش پزشکی")
st.warning("⚠️ این تحلیل فقط راهنمایی است و جایگزین نظر پزشک نیست.")

# ===== آپلود فایل =====
uploaded_file = st.file_uploader("فایل آزمایش خود را آپلود کنید (PDF)", type=["pdf"])

if uploaded_file is not None:
    # خواندن فایل PDF
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    st.success("✅ فایل با موفقیت خوانده شد.")
    
    # نمایش متن استخراج شده (اختیاری)
    with st.expander("متن استخراج شده از فایل"):
        st.write(text)
    
    # ===== تحلیل با هوش مصنوعی =====
    if st.button("🔍 تحلیل کن"):
        with st.spinner("در حال تحلیل..."):
            # آماده‌سازی سوال
            prompt = f"""
            تو یک پزشک متخصص هستی. لطفاً نتایج آزمایش زیر را تحلیل کن:
            
            {text}
            
            لطفاً موارد زیر را مشخص کن:
            1. موارد نرمال
            2. موارد غیرنرمال (با هشدار)
            3. توصیه‌های کلی
            
            در پایان بگو که این تحلیل جایگزین نظر پزشک نیست.
            """
            
            # ارسال به Hugging Face
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            payload = {
                "inputs": prompt,
                "parameters": {"max_new_tokens": 500, "temperature": 0.3}
            }
            
            response = requests.post(MODEL_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()[0]["generated_text"]
                st.markdown("### 📋 نتیجه تحلیل:")
                st.write(result)
            else:
                st.error(f"خطا در ارتباط با هوش مصنوعی: {response.status_code}")
