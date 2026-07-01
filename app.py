import streamlit as st
import pandas as pd
import numpy as np
import uuid
import os
from datetime import date, timedelta

# ==================== 1. Security (Fixed) ====================
KEY_FILE = "license.key"

def get_machine_id():
    return hex(uuid.getnode())

def generate_password(mid):
    digits = ''.join(filter(str.isdigit, mid))
    num = int(digits[:8]) if digits else int(mid.encode().hex(), 16)
    return str(round(abs(num / 2 * 3.14)))[:6]

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = os.path.exists(KEY_FILE)

if not st.session_state['authenticated']:
    st.set_page_config(page_title="Security", layout="centered")
    st.title("Security Activation - Ask the programmer for your password")
    st.warning("Send your Machine ID to programmer email : mulham81ahmed@gmail.com ")

    mid = get_machine_id()
    st.info(f"Machine ID: {mid}")
    pwd = st.text_input("Enter Activation Key:", type="password")
    if st.button("Activate"):
        if pwd == generate_password(mid):
            with open(KEY_FILE, "w") as f: f.write(pwd)
            st.session_state['authenticated'] = True
            st.rerun()
        else:
            st.error("Invalid Activation Key.")
    st.stop()

# Metadata & UI Setup
st.set_page_config(page_title="Neptune-Haumea-Eris Personal Radar", layout="wide")
st.title("Neptune-Haumea-Eris Personal Radar")
st.markdown("### Developed By Mulham Ahmad.")

def run_usm_engine_daily(birth_date):
    homo_k = 6.18
    eris_k = 9.3
    neptune_k = 10.77
    tolerance = 0.3
    
    data = []
    
    # التكرار لـ 84 سنة
    for i in range(1, 85):
        # 1. حساب الانحرافات (المعادلة الأصلية تعتمد على العمر i)
        homo_dev = abs((i / homo_k) - round(i / homo_k))
        eris_dev = abs((i / eris_k) - round(i / eris_k))
        neptune_dev = abs((i / neptune_k) - round(i / neptune_k))
        
        status = "CRITICAL" if (homo_dev <= tolerance and eris_dev <= tolerance and neptune_dev <= tolerance) else "Normal"
        
        # 2. تطبيق منطق الجمع المركب:
        # تاريخ الخطر = (تاريخ الميلاد) + (انحرافات المعادلة)
        # نحول الانحرافات إلى أيام وشهور لإضافتها لتاريخ الميلاد
        offset_day = int(eris_dev * 30)
        offset_month = int(homo_dev * 12)
        
        # حساب السنة المستهدفة
        target_year = birth_date.year + i
        
        # الجمع المركب مع الترحيل (Carry-over)
        new_day = birth_date.day + offset_day
        new_month = birth_date.month + offset_month
        new_year = target_year
        
        # معالجة الفائض (أيام لأشهر، وأشهر لسنوات)
        while new_day > 30: # تبسيط الحساب للأيام
            new_day -= 30
            new_month += 1
        
        while new_month > 12:
            new_month -= 12
            new_year += 1
            
        risk_date_str = f"{new_year}-{new_month:02d}-{new_day:02d}"
        
        data.append([risk_date_str, i, round(homo_dev, 4), round(eris_dev, 4), round(neptune_dev, 4), status])
        
    return pd.DataFrame(data, columns=["Risk Date", "Age (Year)", "Homo Dev", "Eris Dev", "Neptune Dev", "Status"])

# UI Layout
birth_date = st.date_input("Select Inception/Birth Date", value=date(1981, 4, 17), min_value=date(1900, 1, 1), max_value=date(2099, 12, 31))

if st.button("Execute Daily Radar Analysis"):
    df = run_usm_engine_daily(birth_date)
    
    # تنسيق النتائج
    def color_status(val):
        return 'background-color: red; color: white' if val == 'CRITICAL' else 'background-color: green; color: white'
    
    styled_df = df.style.map(color_status, subset=['Status'])
    
    if not df.empty:
        st.dataframe(styled_df, use_container_width=True, height=500)
    else:
        st.warning("No CRITICAL dates found in 84-year horizon.")
