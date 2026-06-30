import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
import uuid
import os

# --- الثوابت الكونية ---
HOMO_D = 2257.245
ERIS_D = 3396.825
NEPTUNE_D = 3933.645
DAYS_PER_YEAR = 365.25 # التصحيح الدقيق للسنة

def get_forced_change_events(start_date, horizon_years, tolerance):
    # حساب عدد الأيام بناءً على 365.25
    total_days = int(horizon_years * DAYS_PER_YEAR)
    days = np.arange(1, total_days + 1)
    
    # حساب الانحرافات
    h_dev = np.abs((days / HOMO_D) - np.round(days / HOMO_D))
    e_dev = np.abs((days / ERIS_D) - np.round(days / ERIS_D))
    n_dev = np.abs((days / NEPTUNE_D) - np.round(days / NEPTUNE_D))
    
    # دالة الصفر المطلق عند اختيار سنة واحدة
    actual_tolerance = 0.0000001 if tolerance == 0 else tolerance
        
    mask = (h_dev <= actual_tolerance) & (e_dev <= actual_tolerance) & (n_dev <= actual_tolerance)
    forced_days = days[mask]
    
    # تحويل الأيام إلى تواريخ
    return [start_date + timedelta(int(d)) for d in forced_days]

# --- منطق الحماية ---
def get_machine_id():
    return str(uuid.getnode())

def generate_expected_password(machine_id):
    digits = ''.join(filter(str.isdigit, machine_id))
    if not digits: digits = str(int(machine_id, 16))
    num = int(digits)
    result = round(abs(num / 2 * 3.14))
    return str(result)[:6]

def save_key(password):
    with open("activation.key", "w") as f:
        f.write(password)

def check_activation():
    if os.path.exists("activation.key"):
        with open("activation.key", "r") as f:
            return f.read().strip()
    return None

# --- واجهة Streamlit ---
st.set_page_config(page_title="NE Engine - Secure", layout="centered")

machine_id = get_machine_id()
expected_pwd = generate_expected_password(machine_id)
saved_key = check_activation()

if saved_key != expected_pwd:
    st.title("🔒 نظام الحماية")
    st.code(machine_id, language=None)
    user_input = st.text_input("أدخل كلمة مرور التفعيل:", type="password")
    if st.button("تفعيل"):
        if user_input == expected_pwd:
            save_key(user_input)
            st.rerun()
        else:
            st.error("كلمة المرور غير صحيحة.")
    st.stop()

# --- البرنامج الرئيسي ---
st.title("🌍 Neptune-Haumea-Eris Engine")
inception_date = st.date_input("تاريخ التأسيس:", value=date(1981, 4, 17))
mode = st.selectbox("نطاق التحليل:", ["سنة واحدة", "نطاق زمني (أكثر من سنة)"])

if mode == "سنة واحدة":
    target_year = st.number_input("السنة المراد توقعها:", min_value=1900, max_value=2100, value=2026)
    # نحسب الفرق بالسنوات ثم نستخدم المعامل الصفر
    horizon = target_year - inception_date.year
    tolerance = 0.0
else:
    horizon = st.slider("نطاق البحث (سنوات):", 1, 99, 46)
    tolerance = 0.0008

if st.button("تفعيل الرادار"):
    with st.spinner('جاري المسح الرياضي...'):
        all_events = get_forced_change_events(inception_date, horizon + 1, tolerance)
        
        # تصفية النتائج بناءً على النمط
        if mode == "سنة واحدة":
            events = [d for d in all_events if d.year == target_year]
        else:
            events = all_events
            
        if events:
            df = pd.DataFrame({"تاريخ التغيير القسري": [d.strftime('%d / %m / %Y') for d in events]})
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("لم يتم العثور على محطات حتمية في هذا النطاق.")
