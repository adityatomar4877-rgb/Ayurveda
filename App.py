import streamlit as st
import sqlite3
import pandas as pd
import random
from pathlib import Path

# ----------------------------
# Dataset Setup
# ----------------------------
CSV_PATH = Path(__file__).parent / "ayurvedic_health_dataset_large.csv"
try:
    food_df = pd.read_csv(CSV_PATH)
except Exception:
    st.warning("⚠ Dataset not found. Default meals will be used.")
    food_df = pd.DataFrame(columns=["Food", "Category", "Calories", "Protein", "Carbs", "Fat", "Micronutrients", "SafeFor"])

# ----------------------------
# Database Setup
# ----------------------------
DB_FILE = Path(__file__).parent / "ayurdiet.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Patients
    c.execute("""
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
    c.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    # Diet Plans
    c.execute("""
        CREATE TABLE IF NOT EXISTS diet_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            plan TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    """)

    # Default Doctor
    c.execute("SELECT * FROM doctors WHERE email=?", ("doctor@ayur.com",))
    if not c.fetchone():
        c.execute("INSERT INTO doctors (name,email,password) VALUES (?,?,?)", ("Dr. Smith", "doctor@ayur.com", "1234"))

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

    safe_foods = food_df
    if disease:
        disease = disease.lower()
        filtered = food_df[food_df["SafeFor"].str.contains(disease, case=False, na=False)]
        if not filtered.empty:
            safe_foods = filtered

    def pick_food(category):
        items = safe_foods[safe_foods["Category"] == category]
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
        "Fats (g)": fat
    }

    return plan, nutrients

# ----------------------------
# Streamlit Config
# ----------------------------
st.set_page_config(page_title="🌿 AyurDiet", page_icon="🌱", layout="wide")

# ----------------------------
# Session State Init
# ----------------------------
for key in ["page", "user_role", "user_id", "user_name"]:
    if key not in st.session_state:
        st.session_state[key] = None

if st.session_state.page is None:
    st.session_state.page = "landing"

# ----------------------------
# Pages
# ----------------------------
def landing_page():
    st.markdown("<h1 style='text-align:center; color:green;'>🌿 AyurDiet</h1>", unsafe_allow_html=True)
    st.subheader("Personalized Ayurvedic Diets")

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

    email_or_phone = st.text_input("Email or Phone")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        if role == "doctor":
            c.execute("SELECT * FROM doctors WHERE email=? AND password=?", (email_or_phone, password))
        else:
            c.execute("SELECT * FROM patients WHERE (email=? OR phone=?) AND password=?", (email_or_phone, email_or_phone, password))
        user = c.fetchone()
        conn.close()

        if user:
            st.session_state.user_id = user[0]
            st.session_state.user_name = user[1]
            st.session_state.page = "dashboard"
            st.success("✅ Login successful!")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid credentials")

    if role == "patient":
        if st.button("📝 Register Now"):
            st.session_state.page = "register"
            st.experimental_rerun()

def register_page():
    st.header("📝 Patient Registration")
    full_name = st.text_input("Full Name")
    phone = st.text_input("Phone")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    height = st.number_input("Height (cm)", 50, 250)
    weight = st.number_input("Weight (kg)", 20, 200)
    working_days = st.selectbox("Working Days / Week", list(range(1,8)))
    diseases = st.text_area("Diseases (if any)")

    if st.button("Register"):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        try:
            c.execute("""INSERT INTO patients
                (full_name, phone, email, password, height, weight, working_days, diseases)
                VALUES (?,?,?,?,?,?,?,?)""",
                (full_name, phone, email, password, height, weight, working_days, diseases))
            conn.commit()
            st.success("✅ Registration successful! Please login.")
            st.session_state.page = "login"
            st.experimental_rerun()
        except sqlite3.IntegrityError:
            st.error("⚠ Email or phone already registered.")
        finally:
            conn.close()

def doctor_dashboard():
    st.header(f"👨‍⚕ Doctor Dashboard ({st.session_state.user_name})")

    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT id, full_name, email, phone, height, weight, diseases FROM patients", conn)
    conn.close()

    st.subheader("Patient List")
    st.dataframe(df, use_container_width=True)

    if st.button("🚪 Logout"):
        st.session_state.page = "landing"
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.experimental_rerun()

def patient_dashboard():
    st.header(f"👤 Patient Dashboard ({st.session_state.user_name})")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT height, weight, diseases FROM patients WHERE id=?", (st.session_state.user_id,))
    patient = c.fetchone()
    conn.close()

    if patient:
        height, weight, disease = patient
        st.subheader(f"Welcome, {st.session_state.user_name} 🌱")

        plan, nutrients = generate_diet(weight, height, disease)
        st.subheader("🥗 Your Personalized Diet Plan")
        for meal, desc in plan.items():
            st.markdown(f"**{meal}:** {desc}")

        st.subheader("📊 Nutritional Breakdown")
        st.table(pd.DataFrame([nutrients]))

    if st.button("🚪 Logout"):
        st.session_state.page = "landing"
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.experimental_rerun()

# ----------------------------
# Main
# ----------------------------
def main():
    if st.session_state.page == "landing":
        landing_page()
    elif st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "register":
        register_page()
    elif st.session_state.page == "dashboard":
        if st.session_state.user_role == "doctor":
            doctor_dashboard()
        else:
            patient_dashboard()

if __name__ == "__main__":
    main()
