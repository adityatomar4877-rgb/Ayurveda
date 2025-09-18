import streamlit as st
import pandas as pd
import sqlite3

# -------------------------
# Database Setup
# -------------------------
DB_FILE = "ayurdiet.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    # Patients table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        phone TEXT,
        email TEXT UNIQUE,
        height REAL,
        weight REAL,
        working_days INTEGER,
        diseases TEXT,
        password TEXT
    )
    """)

    # Doctors table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    # Diet Plans
    cur.execute("""
    CREATE TABLE IF NOT EXISTS diet_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        breakfast TEXT,
        lunch TEXT,
        dinner TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    """)

    conn.commit()
    conn.close()

create_tables()

# -------------------------
# Session State Initialization
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# -------------------------
# DB Helper Functions
# -------------------------
def add_patient(full_name, phone, email, height, weight, working_days, diseases, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO patients (full_name, phone, email, height, weight, working_days, diseases, password)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (full_name, phone, email, height, weight, working_days, diseases, password))
    conn.commit()
    conn.close()

def get_patient(email, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients WHERE email=? AND password=?", (email, password))
    row = cur.fetchone()
    conn.close()
    return row

def add_doctor(name, email, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO doctors (name, email, password) VALUES (?, ?, ?)", (name, email, password))
    conn.commit()
    conn.close()

def get_doctor(email, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM doctors WHERE email=? AND password=?", (email, password))
    row = cur.fetchone()
    conn.close()
    return row

def get_all_patients():
    conn = get_connection()
    df = pd.read_sql_query("SELECT id, full_name, email, phone, height, weight, working_days, diseases FROM patients", conn)
    conn.close()
    return df

def set_diet_plan(patient_id, breakfast, lunch, dinner):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM diet_plans WHERE patient_id=?", (patient_id,))
    cur.execute("INSERT INTO diet_plans (patient_id, breakfast, lunch, dinner) VALUES (?, ?, ?, ?)",
                (patient_id, breakfast, lunch, dinner))
    conn.commit()
    conn.close()

def get_diet_plan(patient_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT breakfast, lunch, dinner FROM diet_plans WHERE patient_id=?", (patient_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"Breakfast": row[0], "Lunch": row[1], "Dinner": row[2]}
    return None

# Add default doctor for testing
add_doctor("Dr. Smith", "doctor@ayur.com", "1234")

# -------------------------
# UI Styling
# -------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(to bottom right, #f0f9f0, #d0efdc);
}
.main-header {
    text-align:center;
    padding:1rem;
    color:white;
    background: linear-gradient(135deg, #2d5016 0%, #4a7c59 100%);
    border-radius:10px;
}
.card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    margin-bottom:1rem;
}
.stButton>button {
    background: linear-gradient(135deg, #2d5016 0%, #4a7c59 100%);
    color:white;
    border-radius: 8px;
    padding:0.5rem;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Pages
# -------------------------
def login_page():
    st.markdown('<div class="main-header"><h2>🌿 AyurDiet Login</h2></div>', unsafe_allow_html=True)
    role = st.radio("Login as", ["Doctor", "Patient"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if role=="Doctor":
            doctor = get_doctor(email, password)
            if doctor:
                st.session_state.logged_in = True
                st.session_state.user_role = "doctor"
                st.session_state.user_data = {"id": doctor[0], "name": doctor[1]}
                st.success("Doctor logged in!")
            else:
                st.error("Invalid credentials!")
        else:
            patient = get_patient(email, password)
            if patient:
                st.session_state.logged_in = True
                st.session_state.user_role = "patient"
                st.session_state.user_data = {"id": patient[0], "full_name": patient[1]}
                st.success("Patient logged in!")
            else:
                st.error("Invalid credentials!")

    st.markdown("---")
    if role=="Patient":
        st.markdown("New user? Register below.")
        if st.button("Register"):
            patient_registration_page()

def patient_registration_page():
    st.markdown('<div class="main-header"><h2>🌿 Patient Registration</h2></div>', unsafe_allow_html=True)
    with st.form("register_form"):
        full_name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")
        height = st.number_input("Height (cm)", min_value=1, max_value=300)
        weight = st.number_input("Weight (kg)", min_value=1, max_value=500)
        working_days = st.selectbox("Working Days per Week", [1,2,3,4,5,6,7])
        diseases = st.text_area("Past or Present Diseases")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Register")
        if submitted:
            add_patient(full_name, phone, email, height, weight, working_days, diseases, password)
            st.success("Registration successful! Please login.")

def doctor_dashboard():
    st.markdown('<div class="main-header"><h2>🩺 Doctor Dashboard</h2></div>', unsafe_allow_html=True)
    df = get_all_patients()
    st.subheader("Patient List")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("Assign Diet Plan")
    if not df.empty:
        selected_id = st.selectbox("Select Patient ID", df["id"].tolist())
        breakfast = st.text_area("Breakfast Plan")
        lunch = st.text_area("Lunch Plan")
        dinner = st.text_area("Dinner Plan")
        if st.button("Save Diet Plan"):
            set_diet_plan(selected_id, breakfast, lunch, dinner)
            st.success("Diet plan saved!")

def patient_dashboard():
    st.markdown(f'<div class="main-header"><h2>👤 Welcome {st.session_state.user_data["full_name"]}</h2></div>', unsafe_allow_html=True)
    st.subheader("Your Assigned Diet Plan")
    plan = get_diet_plan(st.session_state.user_data["id"])
    if plan:
        for meal, desc in plan.items():
            st.markdown(f"**{meal}:** {desc}")
    else:
        st.info("No diet plan assigned yet. Please wait for your doctor.")

# -------------------------
# Main
# -------------------------
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        if st.session_state.user_role=="doctor":
            doctor_dashboard()
        elif st.session_state.user_role=="patient":
            patient_dashboard()

if __name__=="__main__":
    main()
