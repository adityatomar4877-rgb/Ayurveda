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

    # Patients
    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        phone TEXT,
        email TEXT,
        height REAL,
        weight REAL,
        working_days INTEGER,
        diseases TEXT,
        password TEXT
    )
    """)

    # Doctors
    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
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
# DB Helper Functions
# -------------------------
def add_patient(full_name, phone, email, height, weight, working_days, diseases, password="1234"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO patients (full_name, phone, email, height, weight, working_days, diseases, password)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (full_name, phone, email, height, weight, working_days, diseases, password))
    conn.commit()
    conn.close()

def get_patient_by_email(email, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients WHERE email=? AND password=?", (email, password))
    row = cur.fetchone()
    conn.close()
    return row

def add_doctor(name, email, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO doctors (name, email, password) VALUES (?, ?, ?)", (name, email, password))
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
    cur.execute("""
        INSERT INTO diet_plans (patient_id, breakfast, lunch, dinner)
        VALUES (?, ?, ?, ?)
    """, (patient_id, breakfast, lunch, dinner))
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

# -------------------------
# Streamlit Config
# -------------------------
st.set_page_config(page_title="AyurDiet - Ayurvedic Diet Management", page_icon="🌿", layout="wide")

# -------------------------
# Custom CSS for UI & Animation
# -------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(270deg, #f0f8e9, #e2f0d9, #f0f8e9);
    background-size: 600% 600%;
    animation: gradientBG 30s ease infinite;
    font-family: 'Arial', sans-serif;
}
@keyframes gradientBG {
    0%{background-position:0% 50%}
    50%{background-position:100% 50%}
    100%{background-position:0% 50%}
}
.card {
    background-color: rgba(255,255,255,0.85);
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 12px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}
.stButton>button {
    padding: 10px 20px;
    border-radius: 8px;
    background: linear-gradient(135deg, #2d5016, #4a7c59);
    color: white;
    font-weight: bold;
}
h1, h2, h3 {
    color: #2d5016;
}
h4, h5 {
    color: #3e6b35;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Initialize session
# -------------------------
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# -------------------------
# Pages
# -------------------------
def login_page():
    st.title("🌿 AyurDiet Login")
    role = st.radio("Login as", ["Doctor", "Patient"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if role == "Doctor":
            doctor = get_doctor(email, password)
            if doctor:
                st.session_state.logged_in = True
                st.session_state.user_role = "doctor"
                st.session_state.user_data = {"id": doctor[0], "name": doctor[1]}
                st.success("Doctor logged in!")
            else:
                st.error("Invalid Doctor credentials")
        else:
            patient = get_patient_by_email(email, password)
            if patient:
                st.session_state.logged_in = True
                st.session_state.user_role = "patient"
                st.session_state.user_data = {"id": patient[0], "full_name": patient[1], "email": patient[3]}
                st.success("Patient logged in!")
            else:
                st.error("Invalid Patient credentials")

    st.markdown("---")
    if role == "Patient":
        st.markdown("New user?")
        if st.button("Register"):
            patient_registration_page()

def patient_registration_page():
    st.title("🌿 Patient Registration")
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
    st.title("🩺 Doctor Dashboard")
    df = get_all_patients()
    st.subheader("Patient List")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("Assign Diet Plan")
    patient_ids = df["id"].tolist()
    if patient_ids:
        selected_id = st.selectbox("Select Patient ID", patient_ids)
        breakfast = st.text_area("🥞 Breakfast Plan")
        lunch = st.text_area("🥗 Lunch Plan")
        dinner = st.text_area("🌙 Dinner Plan")

        if st.button("Save Diet Plan"):
            set_diet_plan(selected_id, breakfast, lunch, dinner)
            st.success("Diet plan saved successfully!")

def patient_dashboard():
    st.title("👤 Patient Dashboard")
    st.write(f"Welcome, {st.session_state.user_data['full_name']}")

    st.markdown("---")
    st.subheader("Your Assigned Diet Plan")
    plan = get_diet_plan(st.session_state.user_data["id"])
    if plan:
        for meal, desc in plan.items():
            st.markdown(f"""
            <div class='card'>
                <h4>{meal}</h4>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No diet plan assigned yet. Please wait for your doctor.")

# -------------------------
# Main App
# -------------------------
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        if st.session_state.user_role == "doctor":
            doctor_dashboard()
        elif st.session_state.user_role == "patient":
            patient_dashboard()

if __name__ == "__main__":
    main()
