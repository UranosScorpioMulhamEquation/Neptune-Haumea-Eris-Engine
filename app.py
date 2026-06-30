import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
import uuid
import os

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Neptune-Haumea-Eris Engine", layout="centered")

# --- الثوابت الكونية ---
HOMO_D = 2257.245
ERIS_D = 3396.825
NEPTUNE_D = 3933.645

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

# --- منطق الحساب ---
def get_forced_change_events(start_date, horizon_years, tolerance):
    total_days = horizon_years * 365
    days = np.arange(1, total_days + 1)
    h_dev = np.abs((days / HOMO_D) - np.round(days / HOMO_D))
    e_dev = np.abs((days / ERIS_D) - np.round(days / ERIS_D))
    n_dev = np.abs((days / NEPTUNE_D) - np.round(days / NEPTUNE_D))
    mask = (h_dev <= tolerance) & (e_dev <= tolerance) & (n_dev <= tolerance)
    return [start_date + timedelta(int(d)) for d in days[mask]]

# --- الواجهة ---
machine_id = get_machine_id()
expected_pwd = generate_expected_password(machine_id)
saved_key = check_activation()

if saved_key != expected_pwd:
    st.title("🔒 نظام الحماية")
    st.info("راسل المبرمج بالمعرف الخاص بك للحصول على كلمة مرور:")
    st.code(machine_id, language=None)
    user_input = st.text_input("أدخل كلمة مرور التفعيل:", type="password")
    if st.button("تفعيل"):
        if user_input == expected_pwd:
            save_key(user_input)
            st.success("تم التفعيل بنجاح! يرجى تحديث الصفحة.")
        else:
            st.error("كلمة المرور غير صحيحة.")
    st.stop()

# --- البرنامج الرئيسي ---
st.title("🌍 Neptune-Haumea-Eris Engine")
st.markdown("---")

inception_date = st.date_input("تاريخ التأسيس / الميلاد:", value=date(1981, 4, 17))
mode = st.selectbox("نطاق التحليل:", ["سنة واحدة", "نطاق زمني (أكثر من سنة)"])

if mode == "سنة واحدة":
    target_year = st.number_input("أدخل السنة المراد توقعها:", min_value=1900, max_value=2100, value=2026)
    horizon, tolerance = (target_year - inception_date.year), 0.0
else:
    horizon, tolerance = st.slider("نطاق البحث (سنوات من تاريخ التأسيس):", 1, 99, 46), 0.0008

if st.button("تفعيل الرادار"):
    with st.spinner('جاري المسح الرياضي...'):
        all_events = get_forced_change_events(inception_date, horizon + 1 if mode=="سنة واحدة" else horizon, tolerance)
        if mode == "سنة واحدة":
            events = [d for d in all_events if d.year == target_year]
        else:
            events = all_events
            
        if events:
            df = pd.DataFrame({"تاريخ التغيير القسري": [d.strftime('%d / %m / %Y') for d in events]})
            st.success(f"تم العثور على {len(events)} محطة حتمية.")
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("تحميل التقرير (CSV)", csv, "report.csv", "text/csv")
        else:
            st.warning("لم يتم العثور على محطات ضمن النطاق المختار.")