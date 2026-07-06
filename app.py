import streamlit as st
import requests
from PIL import Image
import io
import base64

# ===== تنظیمات =====
HF_TOKEN = "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"  # 
MODEL_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-11B-Vision-Instruct"

# ===== عنوان صفحه =====
st.set_page_config(page_title="تحلیلگر آزمایشگاه", page_icon="🩺")
st.title("🩺 تحلیلگر هوشمند آزمایشگاه (عکس و PDF)")
st.warning("⚠️ این تحلیل فقط راهنمایی است و جایگزین نظر پزشک نیست.")

# ===== آپلود فایل =====
uploaded_file = st.file_uploader("فایل آزمایش (PDF) یا عکس (JPG/PNG) را آپلود کنید", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file is not None:
    file_type = uploaded_file.type
    
    # اگر عکس بود
    if file_type.startswith('image'):
        st.image(uploaded_file, caption="عکس آپلود شده", use_container_width=True)
        prompt = "تو یک پزشک هستی. لطفاً این عکس آزمایشگاه را تحلیل کن. موارد غیرنرمال را با هشدار مشخص کن و توصیه‌های کلی بده. در پایان بگو که این تحلیل جایگزین نظر پزشک نیست."
        
    # اگر PDF بود
    elif file_type == 'application/pdf':
        # برای PDF، ما نمی‌تونیم مستقیم به هوش مصنوعی بفرستیم (چون مدل Vision فقط عکس می‌فهمه)
        # پس باید متنش رو استخراج کنیم و به مدل متنی معمولی بفرستیم
        # اما برای سادگی و جلوگیری از پیچیدگی زیاد، فعلاً فقط عکس رو پردازش می‌کنیم
        # اگر اصرار داری PDF هم کار کنه، بگو تا کد پیچیده‌ترش رو بدم
        st.error("⚠️ در این نسخه، فقط آپلود عکس پشتیبانی می‌شود. لطفاً از آزمایش عکس بگیرید.")
        st.stop()
        
    # ===== تحلیل با هوش مصنوعی =====
    if file_type.startswith('image'):
        if st.button("🔍 تحلیل کن"):
            with st.spinner("در حال تحلیل تصویر..."):
                # خواندن عکس
                image = Image.open(uploaded_file)
                
                # تبدیل عکس به فرمت Base64
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                
                # آماده‌سازی درخواست
                headers = {
                    "Authorization": f"Bearer {HF_TOKEN}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "inputs": [
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{img_base64}"
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                    "parameters": {"max_new_tokens": 500, "temperature": 0.3}
                }
                
                try:
                    response = requests.post(MODEL_URL, headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()[0]["generated_text"]
                        st.markdown("### 📋 نتیجه تحلیل:")
                        st.write(result)
                    else:
                        st.error(f"خطا در ارتباط با هوش مصنوعی: {response.status_code}")
                        st.error(response.text)
                        
                except Exception as e:
                    st.error(f"خطا: {e}")
