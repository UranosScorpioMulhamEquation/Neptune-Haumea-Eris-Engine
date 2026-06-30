import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
from streamlit_browser_fingerprint import st_browser_fingerprint

# --- الثوابت الكونية ---
HOMO_D = 2257.245
ERIS_D = 3396.825
NEPTUNE_D = 3933.645
DAYS_PER_YEAR = 365.25
MAX_TOLERANCE = 0.003  # 0.30% الصرامة المطلوبة

# --- منطق حساب الرنين ---
def get_forced_change_events(start_date, horizon_years, tolerance):
    # استخدام المعامل الأقل بين ما يختاره المستخدم وبين حد الـ 0.30%
    effective_tolerance = min(tolerance, MAX_TOLERANCE)
    
    total_days = int(horizon_years * DAYS_PER_YEAR)
    days = np.arange(1, total_days + 1)
    
    # حساب الانحرافات
    h_dev = np.abs((days / HOMO_D) - np.round(days / HOMO_D))
    e_dev = np.abs((days / ERIS_D) - np.round(days / ERIS_D))
    n_dev = np.abs((days / NEPTUNE_D) - np.round(days / NEPTUNE_D))
    
    # شرط الرنين الثلاثي
    mask = (h_dev <= effective_tolerance) & (e_dev <= effective_tolerance) & (n_dev <= effective_tolerance)
    forced_days = days[mask]
    
    return [start_date + timedelta(int(d)) for d in forced_days]

# --- منطق الحماية ---
def generate_password(mid):
    digits = ''.join(filter(str.isdigit, mid))
    num = int(digits) if digits else int(mid.encode().hex(), 16)
    result = round(abs(num / 2 * 3.14))
    return str(result)[:6]

# --- واجهة Streamlit ---
st.set_page_config(page_title="NE Engine - Secure", layout="centered")

# الحصول على بصمة المتصفح (معرف ثابت للمستخدم)
fingerprint = st_browser_fingerprint()

if fingerprint:
    expected_pwd = generate_password(fingerprint)
    
    # إدارة حالة التفعيل
    if "is_activated" not in st.session_state:
        st.session_state.is_activated = False

    if not st.session_state.is_activated:
        st.title("🔒 نظام الحماية")
        st.write("المعرف الفريد للجهاز:")
        st.code(fingerprint)
        user_input = st.text_input("أدخل كلمة مرور التفعيل:", type="password")
        if st.button("تفعيل"):
            if user_input == expected_pwd:
                st.session_state.is_activated = True
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة.")
        st.stop()

    # --- الرادار الرئيسي ---
    st.title("🌍 Neptune-Haumea-Eris Engine")
    st.markdown("---")
    
    inception_date = st.date_input("تاريخ التأسيس / الميلاد:", value=date(1981, 4, 17))
    mode = st.selectbox("نطاق التحليل:", ["سنة واحدة", "نطاق زمني (أكثر من سنة)"])

    if mode == "سنة واحدة":
        target_year = st.number_input("السنة المراد توقعها:", min_value=1900, max_value=2100, value=2026)
        horizon = target_year - inception_date.year
        tolerance = 0.0 # دقة مطلقة للسنة الواحدة
    else:
        horizon = st.slider("نطاق البحث (سنوات من التأسيس):", 1, 99, 46)
        tolerance = 0.0008

    if st.button("تفعيل الرادار"):
        with st.spinner('جاري المسح الرياضي الدقيق...'):
            all_events = get_forced_change_events(inception_date, horizon + 1, tolerance)
            
            if mode == "سنة واحدة":
                events = [d for d in all_events if d.year == target_year]
            else:
                events = all_events
                
            if events:
                df = pd.DataFrame({"تاريخ التغيير القسري": [d.strftime('%d / %m / %Y') for d in events]})
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("لم يتم العثور على محطات ضمن معيار الـ 0.30%.")
else:
    st.info("يتم الآن استخراج بصمة الجهاز... الرجاء الانتظار.")
