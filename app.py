import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# ===== تنظیمات =====
GEMINI_KEY = "AQ.Ab8RN6Jyjb1kIa4skOfRve9nri15jTaYAAiztOxXD_HhAn2sJQ" 
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.0-pro')
# ===== عنوان صفحه =====
st.set_page_config(page_title="تحلیلگر آزمایشگاه", page_icon="🩺")
st.title("🩺 تحلیلگر هوشمند آزمایشگاه (عکس و PDF)")
st.warning("⚠️ این تحلیل فقط راهنمایی است و جایگزین نظر پزشک نیست.")

# ===== آپلود فایل =====
uploaded_file = st.file_uploader("فایل آزمایش (عکس یا PDF) را آپلود کنید", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file is not None:
    file_type = uploaded_file.type
    
    # اگر عکس بود
    if file_type.startswith('image'):
        st.image(uploaded_file, caption="عکس آپلود شده", use_container_width=True)
        
        if st.button("🔍 تحلیل کن"):
            with st.spinner("در حال تحلیل..."):
                try:
                    image = Image.open(uploaded_file)
                    response = model.generate_content([
                        "تو یک پزشک متخصص هستی. لطفاً این عکس آزمایشگاه را تحلیل کن. موارد نرمال و غیرنرمال را مشخص کن. اگر مورد غیرنرمال دیدی با ⚠️ هشدار بده. در پایان بگو که این تحلیل جایگزین نظر پزشک نیست.",
                        image
                    ])
                    st.markdown("### 📋 نتیجه تحلیل:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"خطا: {e}")
    
    # اگر PDF بود
    elif file_type == 'application/pdf':
        st.info("📄 فایل PDF دریافت شد. در حال استخراج متن...")
        
        # برای PDF از PyPDF2 استفاده می‌کنیم
        from PyPDF2 import PdfReader
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        st.success("✅ متن استخراج شد.")
        
        if st.button("🔍 تحلیل کن"):
            with st.spinner("در حال تحلیل..."):
                try:
                    response = model.generate_content(
                        f"تو یک پزشک متخصص هستی. لطفاً این نتایج آزمایش را تحلیل کن:\n\n{text}\n\nموارد نرمال و غیرنرمال را مشخص کن. اگر مورد غیرنرمال دیدی با ⚠️ هشدار بده. در پایان بگو که این تحلیل جایگزین نظر پزشک نیست."
                    )
                    st.markdown("### 📋 نتیجه تحلیل:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"خطا: {e}")
