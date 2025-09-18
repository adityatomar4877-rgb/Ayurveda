import streamlit as st
import pandas as pd
import sqlite3
import random

# ----------------------------
# Load Dataset
# ----------------------------
CSV_PATH = r"C:\Users\ashwi\Downloads\ayurvedic_health_dataset_large.csv"
try:
    food_df = pd.read_csv(CSV_PATH)
except:
    st.error("⚠ Unable to load dataset. Please check CSV path.")
    food_df = pd.DataFrame(columns=["Food", "Category", "Calories", "Protein", "Carbs", "Fat", "Micronutrients", "SafeFor"])

# ----------------------------
# Database Setup
# ----------------------------
DB_FILE = "ayurdiet.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # Patients
    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            phone TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            height REAL,
            weight REAL,
            working_days INTEGER,
            diseases TEXT
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
            patient_id INTEGER,
            breakfast TEXT,
            lunch TEXT,
            dinner TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    """)

    # Default doctor
    cur.execute("SELECT * FROM doctors WHERE email=?", ("doctor@ayur.com",))
    if not cur.fetchone():
        cur.execute("INSERT INTO doctors (name,email,password) VALUES (?,?,?)", ("Dr. Smith","doctor@ayur.com","1234"))

    # Default patient
    cur.execute("SELECT * FROM patients WHERE email=?", ("test@pat.com",))
    if not cur.fetchone():
        cur.execute("""INSERT INTO patients
            (full_name, phone, email, password, height, weight, working_days, diseases)
            VALUES (?,?,?,?,?,?,?,?)""",
            ("Test Patient","9999999999","test@pat.com","1234",170,70,5,"None")
        )
    conn.commit()
    conn.close()

init_db()

# ----------------------------
# Diet Generator
# ----------------------------
def generate_diet(weight, height, disease=None):
    calories = round(weight * 30)
    protein = round(weight * 1.2)
    fat = round((0.25 * calories)/9)
    carbs = round((calories - (protein*4 + fat*9))/4)

    if disease:
        disease = disease.lower()
        safe_foods = food_df[food_df["SafeFor"].str.contains(disease, case=False, na=False)]
    else:
        safe_foods = food_df
    if safe_foods.empty:
        safe_foods = food_df

    def pick_food(category):
        items = safe_foods[safe_foods["Category"]==category]
        if not items.empty:
            return random.choice(items["Food"].tolist())
        return "Ayurvedic recommended meal"

    plan = {
        "Breakfast": f"{pick_food('Breakfast')} + Tulsi tea",
        "Mid-morning": f"{pick_food('Snack')} + soaked chia seeds",
        "Lunch": f"{pick_food('Lunch')} + Salad + Buttermilk",
        "Snack": f"{pick_food('Snack')} + Herbal tea",
        "Dinner": f"{pick_food('Dinner')} + Steamed veggies + Triphala water",
        "Bedtime": "Warm turmeric milk with pinch of ashwagandha"
    }

    nutrients = {
        "Calories": calories,
        "Protein (g)": protein,
        "Carbs (g)": carbs,
        "Fats (g)": fat,
        "Fiber (g)": int(25*(calories/2000)),
        "Calcium (mg)": int(600*(calories/2000)),
        "Iron (mg)": int(14*(calories/2000))
    }
    return plan, nutrients

# ----------------------------
# Streamlit Config
# ----------------------------
st.set_page_config(page_title="🌿 AyurDiet", page_icon="🌱", layout="wide")
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to right, #e0f7fa, #f1f8e9);
        color: #004d40;
    }
    .stButton>button {
        background-color: #00bfa5;
        color: white;
        height:3em;
        width:100%;
        border-radius:10px;
    }
    .stTextInput>div>input {
        height:2em;
        border-radius:10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Session State
# ----------------------------
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ----------------------------
# Pages
# ----------------------------
def landing_page():
    st.title("🌿 AyurDiet")
    st.subheader("Personalized Ayurvedic Diets with Modern Nutrition")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👨‍⚕ Doctor Portal"):
            st.session_state.user_role = "doctor"
            st.session_state.page = "login"
            st.experimental_rerun()
    with col2:
        if st.button("👤 Patient Portal"):
            st.session_state.user_role = "patient"
            st.session_state.page = "login"
            st.experimental_rerun()

def login_page():
    role = st.session_state.user_role
    st.header(f"{role.title()} Login")
    login_input = st.text_input("Email or Phone")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        conn = get_connection()
        cur = conn.cursor()
        if role=="doctor":
            cur.execute("SELECT * FROM doctors WHERE email=? AND password=?", (login_input,password))
        else:
            cur.execute("SELECT * FROM patients WHERE (email=? OR phone=?) AND password=?", (login_input,login_input,password))
        user = cur.fetchone()
        conn.close()
        if user:
            st.session_state.user_id = user[0]
            st.session_state.page="dashboard"
            st.success("✅ Login successful!")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid credentials")
    if role=="patient":
        if st.button("📝 Register Now"):
            st.session_state.page="register"
            st.experimental_rerun()

def register_page():
    st.header("📝 Patient Registration")
    full_name = st.text_input("Full Name")
    phone = st.text_input("Phone")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    height = st.number_input("Height (cm)", min_value=50, max_value=250)
    weight = st.number_input("Weight (kg)", min_value=20, max_value=200)
    working_days = st.selectbox("Working Days / Week", list(range(1,8)))
    diseases = st.text_area("Diseases (if any)")
    if st.button("Register"):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""INSERT INTO patients
                (full_name, phone, email, password, height, weight, working_days, diseases)
                VALUES (?,?,?,?,?,?,?,?)""",
                (full_name, phone, email, password, height, weight, working_days, diseases))
            conn.commit()
            conn.close()
            st.success("✅ Registration successful! Please login.")
            st.session_state.page="login"
            st.experimental_rerun()
        except sqlite3.IntegrityError:
            st.error("⚠ Email or phone already registered.")

def doctor_dashboard():
    st.header("👨‍⚕ Doctor Dashboard")
    conn = get_connection()
    df = pd.read_sql("SELECT id, full_name, email, phone, height, weight, diseases FROM patients", conn)
    conn.close()
    st.dataframe(df)
    st.subheader("Assign Diet Plan")
    patient_ids = df["id"].tolist()
    if patient_ids:
        selected_id = st.selectbox("Select Patient ID", patient_ids)
        breakfast = st.text_area("Breakfast Plan")
        lunch = st.text_area("Lunch Plan")
        dinner = st.text_area("Dinner Plan")
        if st.button("Save Diet Plan"):
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM diet_plans WHERE patient_id=?", (selected_id,))
            cur.execute("INSERT INTO diet_plans (patient_id, breakfast, lunch, dinner) VALUES (?,?,?,?)",
                        (selected_id, breakfast, lunch, dinner))
            conn.commit()
            conn.close()
            st.success("Diet plan saved successfully!")
    if st.button("🚪 Logout"):
        st.session_state.page="landing"
        st.session_state.user_id=None
        st.experimental_rerun()

def patient_dashboard():
    st.header("👤 Patient Dashboard")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT full_name, height, weight, diseases FROM patients WHERE id=?", (st.session_state.user_id,))
    patient = cur.fetchone()
    conn.close()
    name, height, weight, disease = patient
    st.subheader(f"Welcome, {name} 🌱")
    plan, nutrients = generate_diet(weight, height, disease)
    st.subheader("🥗 Your Personalized Diet Plan")
    for meal, desc in plan.items():
        st.markdown(f"<div style='background-color:#e0f2f1;padding:10px;border-radius:10px;margin:5px'><b>{meal}:</b> {desc}</div>", unsafe_allow_html=True)
    st.subheader("📊 Nutritional Breakdown")
    st.table(pd.DataFrame([nutrients]))
    if st.button("🚪 Logout"):
        st.session_state.page="landing"
        st.session_state.user_id=None
        st.experimental_rerun()

# ----------------------------
# Main Controller
# ----------------------------
def main():
    if st.session_state.page=="landing":
        landing_page()
    elif st.session_state.page=="login":
        login_page()
    elif st.session_state.page=="register":
        register_page()
    elif st.session_state.page=="dashboard":
        if st.session_state.user_role=="doctor":
            doctor_dashboard()
        else:
            patient_dashboard()

if __name__=="__main__":
    main()
