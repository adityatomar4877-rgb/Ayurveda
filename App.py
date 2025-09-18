import streamlit as st
import pandas as pd
import sqlite3
import traceback

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
        phone TEXT UNIQUE,
        email TEXT UNIQUE,
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
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    # Diet Plans
    cur.execute("""
    CREATE TABLE IF NOT EXISTS diet_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER UNIQUE,
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
# Insert default users
# -------------------------
def add_default_users():
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Default Doctor
        cur.execute("SELECT * FROM doctors WHERE email='doctor@ayur.com'")
        if not cur.fetchone():
            cur.execute("INSERT INTO doctors (name, email, password) VALUES (?, ?, ?)",
                        ("Dr. Smith", "doctor@ayur.com", "1234"))

        # Default Patient
        cur.execute("SELECT * FROM patients WHERE email='test@pat.com'")
        if not cur.fetchone():
            cur.execute("""INSERT INTO patients
                (full_name, phone, email, height, weight, working_days, diseases, password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                ("Test Patient", "9999999999", "test@pat.com", 170, 70, 5, "None", "1234")
            )
        conn.commit()
    except:
        pass
    finally:
        conn.close()

add_default_users()

# -------------------------
# DB Helper Functions
# -------------------------
def add_patient(full_name, phone, email, height, weight, working_days, diseases, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""INSERT INTO patients
        (full_name, phone, email, height, weight, working_days, diseases, password)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (full_name, phone, email, height, weight, working_days, diseases, password))
    conn.commit()
    conn.close()

def get_patient_by_email_or_phone(login_input, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients WHERE (email=? OR phone=?) AND password=?", 
                (login_input, login_input, password))
    row = cur.fetchone()
    conn.close()
    return row

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

# -------------------------
# Streamlit Config & Session
# -------------------------
st.set_page_config(page_title="AyurDiet", page_icon="🌿", layout="wide")

if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "page" not in st.session_state:
    st.session_state.page = "login"

# -------------------------
# UI Styling
# -------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(to right, #f0fdf4, #e6f4ea);
}
.stButton>button {
    background: linear-gradient(135deg, #2d5016, #4a7c59);
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Pages
# -------------------------
def login_page():
    st.title("🌿 AyurDiet Login")
    role = st.radio("Login as", ["Doctor", "Patient"])
    login_input = st.text_input("Email or Phone")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if role == "Doctor":
            doctor = get_doctor(login_input, password)
            if doctor:
                st.session_state.logged_in = True
                st.session_state.user_role = "doctor"
                st.session_state.user_data = {"id": doctor[0], "name": doctor[1]}
                st.success("Doctor logged in!")
                st.experimental_rerun()
            else:
                st.error("Invalid Doctor credentials")
        else:
            patient = get_patient_by_email_or_phone(login_input, password)
            if patient:
                st.session_state.logged_in = True
                st.session_state.user_role = "patient"
                st.session_state.user_data = {"id": patient[0], "name": patient[1]}
                st.success("Patient logged in!")
                st.experimental_rerun()
            else:
                st.error("Invalid Patient credentials")

    if role == "Patient":
        if st.button("New user? Register here"):
            st.session_state.page = "register"
            st.experimental_rerun()

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
            try:
                add_patient(full_name, phone, email, height, weight, working_days, diseases, password)
                st.success("Registration successful! Please login.")
                st.session_state.page = "login"
                st.experimental_rerun()
            except sqlite3.IntegrityError:
                st.error("Email or phone already exists!")
            except Exception:
                st.error("Registration failed.")
                st.text(traceback.format_exc())

def doctor_dashboard():
    st.title("🩺 Doctor Dashboard")
    df = get_all_patients()
    st.subheader("Patient List")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("Assign Diet Plan")
    patient_ids = df["id"].tolist() if not df.empty else []
    if patient_ids:
        selected_id = st.selectbox("Select Patient ID", patient_ids)
        breakfast = st.text_area("Breakfast Plan")
        lunch = st.text_area("Lunch Plan")
        dinner = st.text_area("Dinner Plan")
        if st.button("Save Diet Plan"):
            try:
                set_diet_plan(selected_id, breakfast, lunch, dinner)
                st.success("Diet plan saved successfully!")
            except Exception:
                st.error("Failed to save diet plan.")
                st.text(traceback.format_exc())
    else:
        st.info("No patients available yet.")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.session_state.user_role = None
        st.session_state.user_data = None
        st.experimental_rerun()

def patient_dashboard():
    st.title("👤 Patient Dashboard")
    name = st.session_state.user_data.get("name") if st.session_state.user_data else "Patient"
    st.subheader(f"Welcome, {name} 🌱")
    
    user_id = st.session_state.user_data.get("id") if st.session_state.user_data else None
    if user_id:
        plan = get_diet_plan(user_id)
        st.subheader("Your Assigned Diet Plan")
        if plan:
            for meal, desc in plan.items():
                st.markdown(f"**{meal}:** {desc}")
        else:
            st.info("No diet plan assigned yet. Please wait for your doctor.")
    else:
        st.error("No user id found. Please log in again.")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.session_state.user_role = None
        st.session_state.user_data = None
        st.experimental_rerun()

# -------------------------
# Main App
# -------------------------
def main():
    if not st.session_state.logged_in:
        if st.session_state.page == "login":
            login_page()
        elif st.session_state.page == "register":
            patient_registration_page()
    else:
        if st.session_state.user_role == "doctor":
            doctor_dashboard()
        elif st.session_state.user_role == "patient":
            patient_dashboard()
        else:
            st.error("Unknown user role. Please log out and log in again.")

if __name__ == "__main__":
    main()
