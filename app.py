import streamlit as st
from openai import OpenAI
from PIL import Image
import io
import base64
import requests

# ===== تنظیمات =====
API_KEY = "sk-DrwzWv7lPqCFIvKVIdD2jmWCQ4tUUO5JuYbsGitSNrv8PlRZ" 
BASE_URL = "https://api.gapgpt.app/v1"
MODEL_NAME = "gpt-4o-mini"

# ===== عنوان صفحه =====
st.set_page_config(page_title="تحلیلگر آزمایشگاه", page_icon="🩺")
st.title("🩺 تحلیلگر هوشمند آزمایشگاه (عکس و PDF)")
st.warning("⚠️ این تحلیل فقط راهنمایی است و جایگزین نظر پزشک نیست.")

# ===== اتصال به API =====
client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    timeout=60.0,
    max_retries=2
)

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
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    
                    response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{img_base64}"
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": "تو یک پزشک متخصص هستی. لطفاً این عکس آزمایشگاه را تحلیل کن. موارد نرمال و غیرنرمال را مشخص کن. اگر مورد غیرنرمال دیدی با ⚠️ هشدار بده. در پایان بگو که این تحلیل جایگزین نظر پزشک نیست."
                                    }
                                ]
                            }
                        ],
                        max_tokens=1000
                    )
                    
                    result = response.choices[0].message.content
                    st.markdown("### 📋 نتیجه تحلیل:")
                    st.write(result)
                        
                except Exception as e:
                    st.error("⏱️ درخواست زمان‌بر شد. لطفاً دوباره تلاش کنید.")
                    if st.button("🔄 تلاش مجدد"):
                        st.rerun()
    
    # اگر PDF بود
    elif file_type == 'application/pdf':
        st.info("📄 فایل PDF دریافت شد. در حال استخراج متن...")
        
        try:
            from PyPDF2 import PdfReader
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            st.success("✅ متن استخراج شد.")
            
            if st.button("🔍 تحلیل کن"):
                with st.spinner("در حال تحلیل..."):
                    try:
                        response = client.chat.completions.create(
                            model=MODEL_NAME,
                            messages=[
                                {
                                    "role": "user",
                                    "content": f"تو یک پزشک متخصص هستی. لطفاً این نتایج آزمایش را تحلیل کن:\n\n{text}\n\nموارد نرمال و غیرنرمال را مشخص کن. اگر مورد غیرنرمال دیدی با ⚠️ هشدار بده. در پایان بگو که این تحلیل جایگزین نظر پزشک نیست."
                                }
                            ],
                            max_tokens=1000
                        )
                        
                        result = response.choices[0].message.content
                        st.markdown("### 📋 نتیجه تحلیل:")
                        st.write(result)
                        
                    except Exception as e:
                        st.error(f"خطا: {e}")
                        
        except Exception as e:
            st.error(f"خطا در پردازش PDF: {e}")
