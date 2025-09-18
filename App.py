import streamlit as st
import sqlite3
import json

# ----------------------------- PAGE CONFIG -----------------------------
st.set_page_config(
    page_title="AyurDiet - Ayurvedic Diet Management",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------- CSS Styling -----------------------------
st.markdown("""
<style>
/* Background Gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #f0f4ec 0%, #e0dfd5 100%);
}

/* Sidebar transparency */
[data-testid="stSidebar"] {background-color: rgba(255,255,255,0.95); backdrop-filter: blur(5px);}

/* Card Styling */
.card {
    background: #ffffffcc;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease, background 0.3s ease;
}
.card:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0px 8px 25px rgba(0,0,0,0.2);
    background: #f4f9f4;
}

/* Button Styling */
.stButton>button {
    background: linear-gradient(135deg, #4a7c59 0%, #2d5016 100%);
    color: white;
    border-radius: 10px;
    padding: 0.5rem 1rem;
    font-weight: 500;
}

/* Meal card text */
.meal-title {
    font-size: 1.3rem;
    color: #2d5016;
    font-weight: 600;
}
.meal-info {
    font-size: 0.95rem;
    color: #4a4a4a;
}
</style>
""", unsafe_allow_html=True)
# ----------------------------- SESSION STATE -----------------------------
for key in ['user_role','logged_in','current_page','user_id','patient_data']:
    if key not in st.session_state:
        st.session_state[key] = None
if st.session_state.current_page is None:
    st.session_state.current_page = 'role_selection'
# ----------------------------- DATABASE -----------------------------
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
# ----------------------------- DIET PLAN GENERATOR -----------------------------
def generate_diet_plan(height, weight, diseases, working_days):
    bmi = round(weight / ((height/100)**2), 1)
    plan = {'Breakfast': {}, 'Lunch': {}, 'Dinner': {}}

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
# ----------------------------- ROLE SELECTION PAGE -----------------------------
def role_selection_page():
    st.markdown("<h1 style='text-align:center; color:#2d5016;'>🌿 AyurDiet</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#4a4a4a;'>Harmonizing Ayurveda & modern nutrition for your wellness</p>", unsafe_allow_html=True)
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
# ----------------------------- LOGIN PAGE -----------------------------
def login_page():
    st.markdown(f"<h2 style='text-align:center; color:#2d5016;'>🌿 {st.session_state.user_role.title()} Login</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                conn = sqlite3.connect('ayurdiet.db')
                c = conn.cursor()
                if st.session_state.user_role == "patient":
                    c.execute("SELECT id, full_name, phone, email, height, weight, working_days, diseases FROM patients WHERE email=?",(email,))
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
                    # For simplicity, allow any doctor login
                    st.session_state.logged_in = True
                    st.session_state.user_id = 0
                    st.session_state.current_page = "dashboard"
                    st.experimental_rerun()
                conn.close()
        if st.session_state.user_role=="patient":
            if st.button("New Patient? Register Here"):
                st.session_state.current_page="registration"
                st.experimental_rerun()
# ----------------------------- PATIENT REGISTRATION PAGE -----------------------------
def patient_registration_page():
    st.markdown("<h2 style='text-align:center; color:#2d5016;'>🌿 Patient Registration</h2>", unsafe_allow_html=True)
    
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
# ----------------------------- PATIENT DASHBOARD -----------------------------
def patient_dashboard():
    if not st.session_state.logged_in:
        st.session_state.current_page="role_selection"
        st.experimental_rerun()

    patient_name = st.session_state.patient_data.get('full_name','Patient')
    st.markdown(f"<h2 style='color:#2d5016;'>👤 Welcome {patient_name}</h2>", unsafe_allow_html=True)
    
    if st.button("Logout"):
        for key in ['user_role','logged_in','current_page','user_id','patient_data']:
            st.session_state[key] = None
        st.experimental_rerun()
    
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
# ----------------------------- MAIN APP -----------------------------
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
            st.markdown("<h2 style='color:#2d5016;'>🩺 Doctor Dashboard Coming Soon!</h2>", unsafe_allow_html=True)

if __name__=="__main__":
    main()
