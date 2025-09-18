import streamlit as st
import sqlite3
import pandas as pd
import random

# -------------------------
# Embedded Sample Dataset
# -------------------------
food_data = [
    {"Food": "Oats", "Category": "Breakfast", "SafeFor": "None"},
    {"Food": "Poha", "Category": "Breakfast", "SafeFor": "None"},
    {"Food": "Sprout Salad", "Category": "Lunch", "SafeFor": "None"},
    {"Food": "Dal & Rice", "Category": "Lunch", "SafeFor": "Diabetes"},
    {"Food": "Steamed Veggies", "Category": "Dinner", "SafeFor": "None"},
    {"Food": "Grilled Paneer", "Category": "Dinner", "SafeFor": "None"},
    {"Food": "Apple", "Category": "Snack", "SafeFor": "None"},
    {"Food": "Walnuts", "Category": "Snack", "SafeFor": "Heart"}
]

food_df = pd.DataFrame(food_data)

# -------------------------
# Database Setup
# -------------------------
DB_FILE = "ayurdiet.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def create_tables():
    conn = get_connection()
    cur = conn.cursor()
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
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS diet_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        breakfast TEXT,
        lunch TEXT,
        dinner TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )""")
    conn.commit()
    conn.close()

create_tables()

# -------------------------
# Default Users
# -------------------------
def add_default_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM doctors WHERE email='doctor@ayur.com'")
    if not cur.fetchone():
        cur.execute("INSERT INTO doctors (name,email,password) VALUES (?,?,?)",
                    ("Dr. Smith","doctor@ayur.com","1234"))
    cur.execute("SELECT * FROM patients WHERE email='test@pat.com'")
    if not cur.fetchone():
        cur.execute("""INSERT INTO patients
            (full_name, phone, email, height, weight, working_days, diseases, password)
            VALUES (?,?,?,?,?,?,?,?)""",
            ("Test Patient","9999999999","test@pat.com",170,70,5,"None","1234"))
    conn.commit()
    conn.close()

add_default_users()

# -------------------------
# DB Helpers
# -------------------------
def add_patient(full_name, phone, email, height, weight, working_days, diseases, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""INSERT INTO patients
        (full_name, phone, email, height, weight, working_days, diseases, password)
        VALUES (?,?,?,?,?,?,?,?)""",
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
    cur.execute("SELECT * FROM doctors WHERE email=? AND password=?", (email,password))
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
    cur.execute("DELETE FROM diet_plans WHERE patient_id=?",(patient_id,))
    cur.execute("INSERT INTO diet_plans (patient_id, breakfast, lunch, dinner) VALUES (?,?,?,?)",
                (patient_id, breakfast, lunch, dinner))
    conn.commit()
    conn.close()

def get_diet_plan(patient_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT breakfast, lunch, dinner FROM diet_plans WHERE patient_id=?",(patient_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"Breakfast": row[0], "Lunch": row[1], "Dinner": row[2]}
    return None

# -------------------------
# Diet Generator
# -------------------------
def generate_diet(weight, height, disease=None):
    def pick_food(category):
        items = food_df[food_df["Category"]==category]
        if disease:
            items = items[items["SafeFor"].str.contains(disease,case=False,na=False)]
        if not items.empty:
            return random.choice(items["Food"].tolist())
        return f"Recommended {category}"
    plan = {
        "Breakfast": pick_food("Breakfast"),
        "Lunch": pick_food("Lunch"),
        "Dinner": pick_food("Dinner")
    }
    return plan

# -------------------------
# Streamlit Config
# -------------------------
st.set_page_config(page_title="AyurDiet", page_icon="🌿", layout="wide")
if "logged_in" not in st.session_state:
    st.session_state.logged_in=False
if "user_role" not in st.session_state:
    st.session_state.user_role=None
if "user_data" not in st.session_state:
    st.session_state.user_data=None
if "page" not in st.session_state:
    st.session_state.page="login"

# -------------------------
# Pages
# -------------------------
def login_page():
    st.title("🌿 AyurDiet Login")
    role = st.radio("Login as",["Doctor","Patient"])
    login_input = st.text_input("Email or Phone")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if role=="Doctor":
            doctor = get_doctor(login_input,password)
            if doctor:
                st.session_state.logged_in=True
                st.session_state.user_role="doctor"
                st.session_state.user_data={"id":doctor[0],"name":doctor[1]}
                st.success("Doctor logged in")
                st.session_state.page="dashboard"
                st.experimental_rerun()
            else:
                st.error("Invalid Doctor credentials")
        else:
            patient=get_patient_by_email_or_phone(login_input,password)
            if patient:
                st.session_state.logged_in=True
                st.session_state.user_role="patient"
                st.session_state.user_data={"id":patient[0],"name":patient[1],"weight":patient[5],"height":patient[4],"diseases":patient[7]}
                st.success("Patient logged in")
                st.session_state.page="dashboard"
                st.experimental_rerun()
            else:
                st.error("Invalid Patient credentials")
    st.markdown("---")
    if role=="Patient":
        if st.button("New user? Register"):
            st.session_state.page="register"
            st.experimental_rerun()

def patient_registration_page():
    st.title("🌿 Patient Registration")
    full_name=st.text_input("Full Name")
    phone=st.text_input("Phone Number")
    email=st.text_input("Email")
    height=st.number_input("Height (cm)",1,300)
    weight=st.number_input("Weight (kg)",1,500)
    working_days=st.selectbox("Working Days per Week",[1,2,3,4,5,6,7])
    diseases=st.text_area("Past or Present Diseases")
    password=st.text_input("Password",type="password")
    if st.button("Register"):
        try:
            add_patient(full_name,phone,email,height,weight,working_days,diseases,password)
            st.success("Registration successful! Please login.")
            st.session_state.page="login"
            st.experimental_rerun()
        except sqlite3.IntegrityError:
            st.error("Email or phone already exists")

def doctor_dashboard():
    st.title("🩺 Doctor Dashboard")
    df=get_all_patients()
    st.dataframe(df)
    if not df.empty:
        pid=st.selectbox("Select Patient ID",df["id"].tolist())
        breakfast=st.text_area("Breakfast Plan")
        lunch=st.text_area("Lunch Plan")
        dinner=st.text_area("Dinner Plan")
        if st.button("Save Diet Plan"):
            set_diet_plan(pid,breakfast,lunch,dinner)
            st.success("Diet plan saved")
    if st.button("Logout"):
        st.session_state.logged_in=False
        st.session_state.page="login"
        st.session_state.user_role=None
        st.session_state.user_data=None
        st.experimental_rerun()

def patient_dashboard():
    st.title("👤 Patient Dashboard")
    user=st.session_state.user_data
    st.write(f"Welcome {user.get('name')}")
    plan=get_diet_plan(user.get("id"))
    if not plan:
        plan=generate_diet(user.get("weight"),user.get("height"),user.get("diseases"))
    st.subheader("Your Diet Plan")
    for meal,desc in plan.items():
        st.markdown(f"**{meal}:** {desc}")
    if st.button("Logout"):
        st.session_state.logged_in=False
        st.session_state.page="login"
        st.session_state.user_role=None
        st.session_state.user_data=None
        st.experimental_rerun()

# -------------------------
# Main
# -------------------------
def main():
    if not st.session_state.logged_in:
        if st.session_state.page=="login":
            login_page()
        else:
            patient_registration_page()
    else:
        if st.session_state.user_role=="doctor":
            doctor_dashboard()
        else:
            patient_dashboard()

if __name__=="__main__":
    main()
