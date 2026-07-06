import streamlit as st
import requests
from PIL import Image
import io
import base64

# ===== تنظیمات =====
API_KEY = "sk-DrwzWv7lPqCFIvKVIdD2jmWCQ4tUUO5JuYbsGitSNrv8PlRZ"  
API_URL = "https://api.gapgpt.ir/v1/chat/completions"  # آدرس API گپ‌جی‌پی‌تی
MODEL_NAME = "gpt-4o-mini"  # یا هر مدلی که گپ‌جی‌پی‌تی داره


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
                    # تبدیل عکس به Base64
                    image = Image.open(uploaded_file)
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    
                    # آماده‌سازی درخواست
                    headers = {
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "model": MODEL_NAME,
                        "messages": [
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
                        "max_tokens": 1000
                    }
                    
                    response = requests.post(API_URL, headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()["choices"][0]["message"]["content"]
                        st.markdown("### 📋 نتیجه تحلیل:")
                        st.write(result)
                    else:
                        st.error(f"خطا: {response.status_code}")
                        st.error(response.text)
                        
                except Exception as e:
                    st.error(f"خطا: {e}")
    
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
                    headers = {
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "model": MODEL_NAME,
                        "messages": [
                            {
                                "role": "user",
                                "content": f"تو یک پزشک متخصص هستی. لطفاً این نتایج آزمایش را تحلیل کن:\n\n{text}\n\nموارد نرمال و غیرنرمال را مشخص کن. اگر مورد غیرنرمال دیدی با ⚠️ هشدار بده. در پایان بگو که این تحلیل جایگزین نظر پزشک نیست."
                            }
                        ],
                        "max_tokens": 1000
                    }
                    
                    response = requests.post(API_URL, headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()["choices"][0]["message"]["content"]
                        st.markdown("### 📋 نتیجه تحلیل:")
                        st.write(result)
                    else:
                        st.error(f"خطا: {response.status_code}")
                        st.error(response.text)
                        
        except Exception as e:
        st.error(f"خطا در پردازش PDF: {e}")
