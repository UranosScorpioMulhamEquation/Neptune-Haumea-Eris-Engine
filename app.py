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
# ==================== 2. Radar Engine ====================
Y_HOMO, Y_ERIS, Y_NEPTUNE = 6.18, 9.3, 10.77
D_HOMO, D_ERIS, D_NEPTUNE = 2257.245, 3396.825, 3933.645

def get_precise_day(target_year, inception_date):
    start_anchor = date(target_year, inception_date.month, inception_date.day)
    days_from_inception = (start_anchor - inception_date).days
    
    best_day = start_anchor
    min_error = float('inf')
    
    for d in range(-182, 183):
        current_age_days = days_from_inception + d
        h_dev = abs((current_age_days / D_HOMO) - round(current_age_days / D_HOMO))
        e_dev = abs((current_age_days / D_ERIS) - round(current_age_days / D_ERIS))
        n_dev = abs((current_age_days / D_NEPTUNE) - round(current_age_days / D_NEPTUNE))
        total_error = h_dev + e_dev + n_dev
        
        if total_error < min_error:
            min_error = total_error
            best_day = start_anchor + timedelta(days=d)
    return best_day

# ==================== 3. Interface ====================
st.set_page_config(page_title="Neptune-Haumea-Eris Radar", layout="wide")
st.title("Neptune-Haumea-Eris Precision Radar")

# تحديث النطاق من 1900 إلى 2100 كما طلبت
inception_date = st.date_input(
    "Full Inception Date:", 
    value=date(1981, 4, 17),
    min_value=date(1900, 1, 1),
    max_value=date(2100, 12, 31)
)
horizon = st.slider("Forecast Horizon (Years):", 10, 100, 50)

if st.button("Execute Radar Analysis"):
    results = []
    inception_year = inception_date.year
    
    for i in range(1, horizon + 1):
        age = i
        h_dev = abs((age / Y_HOMO) - round(age / Y_HOMO))
        e_dev = abs((age / Y_ERIS) - round(age / Y_ERIS))
        n_dev = abs((age / Y_NEPTUNE) - round(age / Y_NEPTUNE))
        
        if h_dev <= 0.3 and e_dev <= 0.3 and n_dev <= 0.3:
            target_year = inception_year + i
            critical_date = get_precise_day(target_year, inception_date)
            results.append({
                "Age": age,
                "Critical Date": critical_date.strftime('%d/%m/%Y')
            })
            
    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
    else:
        st.warning("No critical resonance found.")
