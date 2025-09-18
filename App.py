import streamlit as st
import sqlite3
import json

# ----------------------------- PAGE CONFIG -----------------------------
st.set_page_config(
    page_title="AyurDiet - Ayurvedic Diet",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------- CSS -----------------------------
st.markdown("""
<style>
/* App background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #d8e6d3 0%, #a3c293 100%);
    color: #2d5016;
}

/* Card styling */
.card {
    background: #ffffffcc;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(135deg, #4a7c59 0%, #2d5016 100%);
    color: white;
    border-radius: 10px;
    padding: 8px;
    font-weight: bold;
}

/* Headers */
h1, h2, h3, h4 {
    color: #2d5016;
}
</style>
""", unsafe_allow_html=True)
# ----------------------------- SESSION STATE -----------------------------
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'role_selection'
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {}
# ----------------------------- DATABASE -----------------------------
def init_db():
    conn = sqlite3.connect('ayurdiet.db')
    c = conn.cursor()
    
    # Patients table
    c.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        height REAL NOT NULL,
        weight REAL NOT NULL,
        working_days INTEGER NOT NULL,
        diseases TEXT
    )
    """)
    
    # Diet plans table
    c.execute("""
    CREATE TABLE IF NOT EXISTS diet_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        plan TEXT NOT NULL,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    """)
    
    conn.commit()
    conn.close()

init_db()
# ----------------------------- DIET PLAN GENERATOR -----------------------------
def generate_diet_plan(height, weight, diseases, working_days):
    """Generate a simple diet plan based on user data"""
    plan = {
        "Breakfast": {
            "description": "Warm oatmeal with almonds and honey",
            "calories": 350,
            "tastes": "Sweet, Astringent",
            "nature": "Warm"
        },
        "Lunch": {
            "description": "Quinoa bowl with mixed vegetables and ghee",
            "calories": 450,
            "tastes": "Sweet, Bitter, Pungent",
            "nature": "Warm"
        },
        "Dinner": {
            "description": "Light khichdi with seasonal vegetables and yogurt",
            "calories": 320,
            "tastes": "Sweet, Salty, Sour",
            "nature": "Warm"
        }
    }
    return plan

def save_diet_plan(patient_id, plan):
    conn = sqlite3.connect('ayurdiet.db')
    c = conn.cursor()
    c.execute("INSERT INTO diet_plans (patient_id, plan) VALUES (?,?)", (patient_id, json.dumps(plan)))
    conn.commit()
    conn.close()
# ----------------------------- ROLE SELECTION -----------------------------
def role_selection_page():
    st.markdown("<h1 style='text-align:center;'>🌿 AyurDiet</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Harmonizing Ayurveda & modern nutrition for your wellness</p>", unsafe_allow_html=True)
    
    st.markdown("### Choose Your Portal")
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        if st.button("🩺 Doctor Portal"):
            st.session_state.user_role = "doctor"
            st.session_state.current_page = "login"
            st.experimental_rerun()
        
        if st.button("👤 Patient Portal"):
            st.session_state.user_role = "patient"
            st.session_state.current_page = "login"
            st.experimental_rerun()
# ----------------------------- LOGIN -----------------------------
def login_page():
    st.markdown(f"<h2 style='text-align:center;'>🌿 {st.session_state.user_role.title()} Login</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                conn = sqlite3.connect('ayurdiet.db')
                c = conn.cursor()
                if st.session_state.user_role=="patient":
                    c.execute("SELECT id, full_name, phone, email, height, weight, working_days, diseases FROM patients WHERE email=?", (email,))
                    user = c.fetchone()
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user[0]
                        st.session_state.patient_data = {
                            'full_name': user[1],
                            'phone': user[2],
                            'email': user[3],
                            'height': user[4],
                            'weight': user[5],
                            'working_days': user[6],
                            'diseases': user[7]
                        }
                        st.session_state.current_page = "dashboard"
                        st.experimental_rerun()
                    else:
                        st.error("Invalid patient email")
                else:
                    # For simplicity, doctor login allowed
                    st.session_state.logged_in = True
                    st.session_state.user_id = 0
                    st.session_state.current_page = "dashboard"
                    st.experimental_rerun()
                conn.close()
        if st.session_state.user_role=="patient":
            if st.button("New Patient? Register Here"):
                st.session_state.current_page="registration"
                st.experimental_rerun()
# ----------------------------- REGISTRATION -----------------------------
def patient_registration_page():
    st.markdown("<h2 style='text-align:center;'>🌿 Patient Registration</h2>", unsafe_allow_html=True)
    
    with st.form("registration_form"):
        full_name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")
        height = st.number_input("Height (cm)", min_value=1, max_value=300)
        weight = st.number_input("Weight (kg)", min_value=1.0, max_value=500.0)
        working_days = st.selectbox("Working Days per Week", [1,2,3,4,5,6,7])
        diseases = st.text_area("Past or Present Diseases (Optional)")
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if full_name and phone and email and height>0 and weight>0:
                conn = sqlite3.connect('ayurdiet.db')
                c = conn.cursor()
                try:
                    c.execute('INSERT INTO patients (full_name, phone, email, height, weight, working_days, diseases) VALUES (?,?,?,?,?,?,?)',
                              (full_name, phone, email, height, weight, working_days, diseases))
                    conn.commit()
                    patient_id = c.lastrowid
                    plan = generate_diet_plan(height, weight, diseases, working_days)
                    save_diet_plan(patient_id, plan)
                    st.success("Registration successful!")
                    st.session_state.logged_in = True
                    st.session_state.user_id = patient_id
                    st.session_state.patient_data = {
                        'full_name': full_name,
                        'phone': phone,
                        'email': email,
                        'height': height,
                        'weight': weight,
                        'working_days': working_days,
                        'diseases': diseases
                    }
                    st.session_state.current_page = "dashboard"
                    st.experimental_rerun()
                except sqlite3.IntegrityError:
                    st.error("Email already exists")
                conn.close()
            else:
                st.error("Please fill all required fields")
# ----------------------------- DASHBOARD -----------------------------
def patient_dashboard():
    if not st.session_state.logged_in:
        st.session_state.current_page="role_selection"
        st.experimental_rerun()

    patient_name = st.session_state.patient_data.get('full_name','Patient')
    st.markdown(f"<h2>👤 Welcome {patient_name}</h2>", unsafe_allow_html=True)
    
    if st.button("Logout"):
        for key in ['user_role','logged_in','current_page','user_id','patient_data']:
            st.session_state[key] = None
        st.experimental_rerun()
    
    # Fetch diet plan
    conn = sqlite3.connect('ayurdiet.db')
    c = conn.cursor()
    c.execute("SELECT plan FROM diet_plans WHERE patient_id=?",(st.session_state.user_id,))
    plan_data = c.fetchone()
    conn.close()

    if plan_data:
        plan = json.loads(plan_data[0])
        for meal, info in plan.items():
            st.markdown(f"""
            <div class='card'>
                <div class='meal-title'>🌿 {meal}</div>
                <div class='meal-info'>{info['description']}</div>
                <div class='meal-info'><b>Calories:</b> {info['calories']}, <b>Tastes:</b> {info['tastes']}, <b>Nature:</b> {info['nature']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Your diet plan will appear here after registration")
# ----------------------------- MAIN -----------------------------
def main():
    if st.session_state.current_page=="role_selection":
        role_selection_page()
    elif st.session_state.current_page=="login":
        login_page()
    elif st.session_state.current_page=="registration":
        patient_registration_page()
    elif st.session_state.current_page=="dashboard":
        if st.session_state.user_role=="patient":
            patient_dashboard()
        else:
            st.markdown("<h2>🩺 Doctor Dashboard Coming Soon!</h2>", unsafe_allow_html=True)

if __name__=="__main__":
    main()
