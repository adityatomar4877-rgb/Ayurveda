import streamlit as st
import sqlite3
import pandas as pd
import json

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(page_title="AyurDiet - Ayurvedic Diet Management",
                   page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

# -----------------------------
# CSS Styling & Background
# -----------------------------
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://img.freepik.com/free-vector/herbal-medicine-background_23-2148709874.jpg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
[data-testid="stHeader"] {background: rgba(0,0,0,0);}
[data-testid="stSidebar"] {background-color: rgba(255,255,255,0.85); backdrop-filter: blur(5px);}
.diet-card {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
    transition: transform 0.3s;
}
.diet-card:hover {transform: scale(1.02);}
.stButton>button {transition: all 0.3s;}
.stButton>button:hover {transform: scale(1.02);}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# -----------------------------
# Initialize session state
# -----------------------------
for key in ['user_role','logged_in','current_page','user_id','patient_data']:
    if key not in st.session_state:
        st.session_state[key] = None

if st.session_state.current_page is None:
    st.session_state.current_page = 'role_selection'

# -----------------------------
# Database setup
# -----------------------------
def init_db():
    conn = sqlite3.connect('ayurdiet.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT,
                phone TEXT,
                email TEXT UNIQUE,
                height REAL,
                weight REAL,
                working_days INTEGER,
                diseases TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT,
                email TEXT UNIQUE,
                password TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS diet_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                plan TEXT,
                FOREIGN KEY(patient_id) REFERENCES patients(id)
                )''')
    conn.commit()
    conn.close()

init_db()

# -----------------------------
# Utility functions
# -----------------------------
def generate_diet_plan(height, weight, diseases, working_days):
    bmi = round(weight / ((height/100)**2), 1)
    plan = {'Breakfast': {}, 'Lunch': {}, 'Dinner': {}}

    # Default based on BMI
    if bmi < 18.5:
        plan['Breakfast'] = {'description':'Warm milk with almonds, oats porridge, fruits','calories':350,'tastes':'Sweet, Astringent','nature':'Warm'}
        plan['Lunch'] = {'description':'Rice, dal, ghee, leafy vegetables','calories':500,'tastes':'Sweet, Bitter','nature':'Warm'}
        plan['Dinner'] = {'description':'Khichdi with moong dal and veggies','calories':400,'tastes':'Sweet, Salty','nature':'Warm'}
    elif 18.5 <= bmi < 24.9:
        plan['Breakfast'] = {'description':'Idli/dosa with chutney, herbal tea','calories':300,'tastes':'Sweet, Sour','nature':'Warm'}
        plan['Lunch'] = {'description':'Chapati, sabzi, dal, salad','calories':450,'tastes':'Sweet, Bitter','nature':'Warm'}
        plan['Dinner'] = {'description':'Light dal soup with roti','calories':350,'tastes':'Sweet, Salty','nature':'Warm'}
    else:
        plan['Breakfast'] = {'description':'Green smoothie, sprouts, herbal tea','calories':250,'tastes':'Bitter, Pungent','nature':'Cool'}
        plan['Lunch'] = {'description':'Multigrain chapati, sabzi, dal (less oil)','calories':400,'tastes':'Sweet, Bitter','nature':'Warm'}
        plan['Dinner'] = {'description':'Vegetable soup, steamed veggies','calories':300,'tastes':'Bitter, Salty','nature':'Warm'}

    # Adjust for diseases
    diseases_lower = diseases.lower() if diseases else ''
    if 'diabetes' in diseases_lower:
        plan['Breakfast']['description'] = 'Methi paratha, sugar-free herbal tea'
        plan['Lunch']['description'] = 'Chapati, karela/tinda sabzi, dal'
        plan['Dinner']['description'] = 'Bajra roti with lauki sabzi'
    if 'bp' in diseases_lower or 'blood pressure' in diseases_lower:
        plan['Breakfast']['description'] = 'Oats, fruits, tulsi tea'
        plan['Lunch']['description'] = 'Brown rice, dal, salad (less salt)'
        plan['Dinner']['description'] = 'Vegetable stew with roti'

    return plan

def save_diet_plan(patient_id, plan_dict):
    conn = sqlite3.connect('ayurdiet.db')
    c = conn.cursor()
    plan_json = json.dumps(plan_dict)
    c.execute('SELECT id FROM diet_plans WHERE patient_id=?', (patient_id,))
    if c.fetchone():
        c.execute('UPDATE diet_plans SET plan=? WHERE patient_id=?', (plan_json, patient_id))
    else:
        c.execute('INSERT INTO diet_plans (patient_id, plan) VALUES (?,?)', (patient_id, plan_json))
    conn.commit()
    conn.close()

# -----------------------------
# Pages
# -----------------------------
def role_selection_page():
    st.title("🌿 AyurDiet")
    st.subheader("Choose your portal")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Doctor Portal"):
            st.session_state.user_role = 'doctor'
            st.session_state.current_page = 'login'
            st.experimental_rerun()
    with col2:
        if st.button("Patient Portal"):
            st.session_state.user_role = 'patient'
            st.session_state.current_page = 'login'
            st.experimental_rerun()

def login_page():
    st.subheader(f"{st.session_state.user_role.title()} Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            conn = sqlite3.connect('ayurdiet.db')
            c = conn.cursor()
            if st.session_state.user_role == 'doctor':
                c.execute('SELECT id FROM doctors WHERE email=? AND password=?',(email,password))
            else:
                c.execute('SELECT id, full_name, height, weight, diseases, working_days FROM patients WHERE email=?',(email,))
            result = c.fetchone()
            conn.close()
            if result:
                st.session_state.logged_in = True
                st.session_state.current_page = 'dashboard'
                if st.session_state.user_role == 'patient':
                    st.session_state.user_id = result[0]
                    st.session_state.patient_data = {
                        'full_name':result[1],'height':result[2],'weight':result[3],'diseases':result[4],'working_days':result[5]
                    }
                    # Generate diet plan automatically if not exists
                    conn = sqlite3.connect('ayurdiet.db')
                    c = conn.cursor()
                    c.execute('SELECT plan FROM diet_plans WHERE patient_id=?', (st.session_state.user_id,))
                    if not c.fetchone():
                        plan = generate_diet_plan(result[2], result[3], result[4], result[5])
                        save_diet_plan(st.session_state.user_id, plan)
                    conn.close()
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")

def patient_registration_page():
    st.subheader("Patient Registration")
    with st.form("reg_form"):
        full_name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")
        height = st.number_input("Height (cm)", min_value=1)
        weight = st.number_input("Weight (kg)", min_value=1.0)
        working_days = st.selectbox("Working days per week", [1,2,3,4,5,6,7])
        diseases = st.text_area("Diseases")
        submitted = st.form_submit_button("Register")
        if submitted:
            conn = sqlite3.connect('ayurdiet.db')
            c = conn.cursor()
            try:
                c.execute('INSERT INTO patients (full_name, phone, email, height, weight, working_days, diseases) VALUES (?,?,?,?,?,?,?)',
                          (full_name, phone, email, height, weight, working_days, diseases))
                conn.commit()
                st.success("Registration successful! Please login.")
                st.session_state.current_page='login'
                st.experimental_rerun()
            except sqlite3.IntegrityError:
                st.error("Email already registered.")
            conn.close()

def patient_dashboard():
    st.header(f"👤 Welcome {st.session_state.patient_data['full_name']}")
    conn = sqlite3.connect('ayurdiet.db')
    c = conn.cursor()
    c.execute('SELECT plan FROM diet_plans WHERE patient_id=?', (st.session_state.user_id,))
    plan_data = c.fetchone()
    conn.close()

    if plan_data:
        plan = json.loads(plan_data[0])
        for meal, info in plan.items():
            st.markdown(f"<div class='diet-card'><h3>{meal}</h3><p>{info['description']}</p><p>Calories: {info['calories']}, Tastes: {info['tastes']}, Nature: {info['nature']}</p></div>", unsafe_allow_html=True)

# -----------------------------
# Main app logic
# -----------------------------
def main():
    if st.session_state.current_page=='role_selection':
        role_selection_page()
    elif st.session_state.current_page=='login':
        login_page()
    elif st.session_state.current_page=='registration':
        patient_registration_page()
    elif st.session_state.current_page=='dashboard' and st.session_state.logged_in:
        if st.session_state.user_role=='patient':
            patient_dashboard()

if __name__=='__main__':
    main()
