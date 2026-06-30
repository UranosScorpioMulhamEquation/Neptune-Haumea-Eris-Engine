import streamlit as st
import pandas as pd
import numpy as np
import hashlib
from datetime import date, timedelta

# --- الثوابت ---
HOMO_D, ERIS_D, NEPTUNE_D = 2257.245, 3396.825, 3933.645
DAYS_PER_YEAR = 365.25
MAX_TOLERANCE = 0.003

# --- نظام الحماية (بصمة المتصفح) ---
def get_browser_fingerprint():
    # استخراج معلومات المتصفح من رأس الطلب
    ua = st.context.headers.get("User-Agent", "unknown")
    # إنشاء بصمة مشفرة بناءً على المتصفح
    return hashlib.sha256(ua.encode()).hexdigest()[:12].upper()

def generate_password(mid):
    digits = ''.join(filter(str.isdigit, mid))
    if not digits: digits = str(int(mid.encode().hex(), 16))
    num = int(digits[:8]) # أخذ أول 8 أرقام لتجنب الأرقام الضخمة
    result = round(abs(num / 2 * 3.14))
    return str(result)[:6]

# --- منطق الرادار ---
def get_forced_change_events(start_date, horizon_years, tolerance):
    effective_tolerance = min(tolerance, MAX_TOLERANCE)
    total_days = int(horizon_years * DAYS_PER_YEAR)
    days = np.arange(1, total_days + 1)
    
    h_dev = np.abs((days / HOMO_D) - np.round(days / HOMO_D))
    e_dev = np.abs((days / ERIS_D) - np.round(days / ERIS_D))
    n_dev = np.abs((days / NEPTUNE_D) - np.round(days / NEPTUNE_D))
    
    mask = (h_dev <= effective_tolerance) & (e_dev <= effective_tolerance) & (n_dev <= effective_tolerance)
    return [start_date + timedelta(int(d)) for d in days[mask]]

# --- الواجهة ---
st.set_page_config(page_title="NE Engine - Secure", layout="centered")

mid = get_browser_fingerprint()
expected_pwd = generate_password(mid)

if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False

if not st.session_state.is_authenticated:
    st.title("🔒 نظام الحماية")
    st.write("للدخول، يرجى تزويد المبرمج بهذا المعرف:")
    st.code(mid)
    
    user_input = st.text_input("أدخل كلمة مرور التفعيل:", type="password")
    if st.button("تفعيل"):
        if user_input == expected_pwd:
            st.session_state.is_authenticated = True
            st.rerun()
        else:
            st.error("كلمة المرور غير صحيحة.")
    st.stop()

# --- الرادار (يعمل بعد التفعيل) ---
st.title("🌍 Neptune-Haumea-Eris Engine")
inception_date = st.date_input("تاريخ التأسيس:", value=date(1981, 4, 17))
mode = st.selectbox("نطاق التحليل:", ["سنة واحدة", "نطاق زمني (أكثر من سنة)"])

if mode == "سنة واحدة":
    target_year = st.number_input("السنة المراد توقعها:", min_value=1900, max_value=2100, value=2026)
    horizon, tolerance = (target_year - inception_date.year), 0.0
else:
    horizon, tolerance = st.slider("نطاق البحث (سنوات):", 1, 99, 46), 0.0008

if st.button("تفعيل الرادار"):
    with st.spinner('جاري المسح...'):
        all_events = get_forced_change_events(inception_date, horizon + 1, tolerance)
        events = [d for d in all_events if d.year == target_year] if mode == "سنة واحدة" else all_events
        
        if events:
            df = pd.DataFrame({"تاريخ التغيير القسري": [d.strftime('%d / %m / %Y') for d in events]})
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("لم يتم العثور على محطات حتمية.")
