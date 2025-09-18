import streamlit as st
import sqlite3
import pandas as pd

# ----------------------------
# Database Setup
# ----------------------------
def init_db():
    conn = sqlite3.connect("ayurdiet.db")
    c = conn.cursor()

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

    c.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS diet_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            plan TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    """)

    # Insert default doctor
    c.execute("SELECT * FROM doctors WHERE email=?", ("doctor@ayur.com",))
    if not c.fetchone():
        c.execute("INSERT INTO doctors (email, password) VALUES (?, ?)", ("doctor@ayur.com", "1234"))

    conn.commit()
    conn.close()

init_db()

# ----------------------------
# Streamlit Config
# ----------------------------
st.set_page_config(
    page_title="🌿 AyurDiet",
    page_icon="🌱",
    layout="wide"
)

# ----------------------------
# Custom CSS with Animation
# ----------------------------
st.markdown("""
<style>
    body {
        background: linear-gradient(270deg, #d2f8d2, #fdf7e3, #ffe5b4);
        background-size: 600% 600%;
        animation: gradientBG 20s ease infinite;
    }
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .main-header {
        text-align: center;
        padding: 2rem;
        background: rgba(45, 80, 22, 0.85);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        animation: fadeIn 2s ease;
    }
    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }
    .ayur-card {
        background: rgba(255, 255, 255, 0.92);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        margin: 1rem 0;
        transition: transform 0.3s ease;
    }
    .ayur-card:hover {
        transform: translateY(-5px);
    }
    .stButton > button {
        background: linear-gradient(135deg, #2d5016, #4a7c59);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.7rem 1.2rem;
        font-size: 1rem;
        font-weight: 600;
        transition: 0.3s;
    }
    .stButton > button:hover {
        transform: scale(1.08);
        background: linear-gradient(135deg, #8b4513, #daa520);
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Session State Init
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
    st.markdown("""
    <div class="main-header">
        <h1>🌿 AyurDiet</h1>
        <p>Ancient Ayurvedic Wisdom blended with Modern Nutrition</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="ayur-card">', unsafe_allow_html=True)
        st.write("✨ Welcome to AyurDiet! Choose your role to continue.")
        if st.button("👨‍⚕️ Doctor Portal"):
            st.session_state.user_role = "doctor"
            st.session_state.page = "login"
            st.rerun()
        if st.button("👤 Patient Portal"):
            st.session_state.user_role = "patient"
            st.session_state.page = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def login_page():
    role = st.session_state.user_role
    st.markdown(f"""
    <div class="main-header">
        <h2>🔑 {role.title()} Login</h2>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            conn = sqlite3.connect("ayurdiet.db")
            c = conn.cursor()
            if role == "doctor":
                c.execute("SELECT * FROM doctors WHERE email=? AND password=?", (email, password))
            else:
                c.execute("SELECT * FROM patients WHERE email=? AND password=?", (email, password))
            user = c.fetchone()
            conn.close()

            if user:
                st.session_state.user_id = user[0]
                st.session_state.page = "dashboard"
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

    if role == "patient":
        st.info("New patient? Register below 👇")
        if st.button("📝 Register Now"):
            st.session_state.page = "register"
            st.rerun()

def register_page():
    st.markdown("""
    <div class="main-header">
        <h2>📝 Patient Registration</h2>
    </div>
    """, unsafe_allow_html=True)

    with st.form("reg_form"):
        full_name = st.text_input("Full Name *")
        phone = st.text_input("Phone *")
        email = st.text_input("Email *")
        password = st.text_input("Password *", type="password")
        height = st.number_input("Height (cm) *", min_value=50, max_value=250)
        weight = st.number_input("Weight (kg) *", min_value=20.0, max_value=200.0)
        working_days = st.selectbox("Working Days / Week *", list(range(1,8)))
        diseases = st.text_area("Diseases (optional)")

        submitted = st.form_submit_button("Complete Registration")
        if submitted:
            conn = sqlite3.connect("ayurdiet.db")
            c = conn.cursor()
            try:
                c.execute("""INSERT INTO patients
                    (full_name, phone, email, password, height, weight, working_days, diseases)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (full_name, phone, email, password, height, weight, working_days, diseases))
                conn.commit()
                conn.close()
                st.success("✅ Registration successful! Please log in.")
                st.session_state.page = "login"
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("⚠️ Email or phone already registered.")

def doctor_dashboard():
    st.markdown("""
    <div class="main-header">
        <h2>👨‍⚕️ Doctor Dashboard</h2>
    </div>
    """, unsafe_allow_html=True)

    conn = sqlite3.connect("ayurdiet.db")
    df = pd.read_sql("SELECT id, full_name, email, height, weight FROM patients", conn)
    conn.close()
    st.dataframe(df)

    st.subheader("📋 Assign Diet Plan")
    patient_id = st.selectbox("Select Patient", df["id"].tolist() if not df.empty else [])
    plan_text = st.text_area("Enter Diet Plan")

    if st.button("💾 Save Plan"):
        if patient_id and plan_text:
            conn = sqlite3.connect("ayurdiet.db")
            c = conn.cursor()
            c.execute("INSERT INTO diet_plans (patient_id, plan) VALUES (?, ?)", (patient_id, plan_text))
            conn.commit()
            conn.close()
            st.success("✅ Plan saved successfully!")

    if st.button("🚪 Logout"):
        st.session_state.page = "landing"
        st.session_state.user_id = None
        st.rerun()

def patient_dashboard():
    st.markdown("""
    <div class="main-header">
        <h2>👤 Patient Dashboard</h2>
    </div>
    """, unsafe_allow_html=True)

    conn = sqlite3.connect("ayurdiet.db")
    c = conn.cursor()
    c.execute("SELECT full_name, height, weight, diseases FROM patients WHERE id=?", (st.session_state.user_id,))
    patient = c.fetchone()

    st.subheader(f"Welcome, {patient[0]} 🌱")
    st.write(f"Height: {patient[1]} cm | Weight: {patient[2]} kg")
    st.write(f"Diseases: {patient[3]}")

    c.execute("SELECT plan FROM diet_plans WHERE patient_id=?", (st.session_state.user_id,))
    plan = c.fetchone()
    conn.close()

    if plan:
        st.success("🥗 Your Diet Plan:")
        st.markdown(f"<div class='ayur-card'><p>{plan[0]}</p></div>", unsafe_allow_html=True)
    else:
        st.info("⚠️ No diet plan assigned yet. Please wait for your doctor.")

    if st.button("🚪 Logout"):
        st.session_state.page = "landing"
        st.session_state.user_id = None
        st.rerun()

# ----------------------------
# Main Controller
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
