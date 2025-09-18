import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="AyurDiet - Ayurvedic Diet Management",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Ayurvedic styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #2d5016 0%, #8b4513 100%);
        margin: -1rem -1rem 2rem -1rem;
        color: white;
        border-radius: 0 0 20px 20px;
    }
    .ayur-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
    .role-button {
        background: linear-gradient(135deg, #2d5016 0%, #4a7c59 100%);
        color: white;
        padding: 1rem 2rem;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s;
        width: 100%;
        margin: 0.5rem 0;
    }
    .patient-button {
        background: linear-gradient(135deg, #8b4513 0%, #daa520 100%);
    }
    .feature-card {
        text-align: center;
        padding: 1.5rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #2d5016 0%, #4a7c59 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'role_selection'

def reset_app():
    """Reset application to initial state"""
    st.session_state.user_role = None
    st.session_state.logged_in = False
    st.session_state.current_page = 'role_selection'
    st.rerun()

def role_selection_page():
    """Main role selection page"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌿 AyurDiet</h1>
        <p>Harmonizing ancient Ayurvedic wisdom with modern nutrition science for personalized wellness</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Choose Your Portal")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Doctor Portal Card
        st.markdown("""
        <div class="ayur-card">
            <div style="text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🩺</div>
                <h3 style="color: #2d5016; margin-bottom: 0.5rem;">Doctor Portal</h3>
                <p style="color: #666; margin-bottom: 1.5rem;">Manage patient diet charts with Ayurvedic principles</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Login as Doctor", key="doctor_btn"):
            st.session_state.user_role = 'doctor'
            st.session_state.current_page = 'login'
            st.rerun()
        
        st.markdown("""
            <div style="text-align: center; margin-top: 1rem; font-size: 0.9rem; color: #666;">
                • Create personalized diet plans<br/>
                • Track patient progress<br/>
                • Apply Ayurvedic food properties
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Patient Portal Card
        st.markdown("""
        <div class="ayur-card">
            <div style="text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">👤</div>
                <h3 style="color: #8b4513; margin-bottom: 0.5rem;">Patient Portal</h3>
                <p style="color: #666; margin-bottom: 1.5rem;">Access your personalized Ayurvedic diet plan</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Login as Patient", key="patient_btn"):
            st.session_state.user_role = 'patient'
            st.session_state.current_page = 'login'
            st.rerun()
        
        st.markdown("""
            <div style="text-align: center; margin-top: 1rem; font-size: 0.9rem; color: #666;">
                • View your diet chart<br/>
                • Track food intake<br/>
                • Monitor wellness progress
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Features Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🌿</div>
            <h4 style="color: #2d5016; margin-bottom: 0.5rem;">Six Tastes (Rasa)</h4>
            <p style="font-size: 0.9rem; color: #666;">Balance sweet, sour, salty, bitter, pungent, and astringent</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔥</div>
            <h4 style="color: #d2691e; margin-bottom: 0.5rem;">Food Properties</h4>
            <p style="font-size: 0.9rem; color: #666;">Hot/Cold nature and digestibility analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">⚖️</div>
            <h4 style="color: #daa520; margin-bottom: 0.5rem;">Modern Metrics</h4>
            <p style="font-size: 0.9rem; color: #666;">Caloric values with traditional wisdom</p>
        </div>
        """, unsafe_allow_html=True)

def login_page():
    """Login page for both doctors and patients"""
    
    st.markdown(f"""
    <div class="main-header">
        <h2>🌿 {st.session_state.user_role.title()} Login</h2>
        <p>Welcome back to AyurDiet</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.markdown('<div class="ayur-card">', unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### Login to Your Account")
            
            if st.session_state.user_role == 'doctor':
                email = st.text_input("Doctor ID / Email", placeholder="Enter your doctor ID or email")
            else:
                email = st.text_input("Email Address", placeholder="Enter your email address")
            
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_login, col_back = st.columns(2)
            
            with col_login:
                if st.form_submit_button("Login", use_container_width=True):
                    if email and password:
                        st.session_state.logged_in = True
                        st.session_state.current_page = 'dashboard'
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Please enter both email and password")
            
            with col_back:
                if st.form_submit_button("Back", use_container_width=True):
                    st.session_state.current_page = 'role_selection'
                    st.rerun()
        
        if st.session_state.user_role == 'patient':
            st.markdown("---")
            st.markdown("### New Patient?")
            if st.button("Register Now", use_container_width=True):
                st.session_state.current_page = 'registration'
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def patient_registration_page():
    """Patient registration page"""
    
    st.markdown("""
    <div class="main-header">
        <h2>🌿 Patient Registration</h2>
        <p>Please fill in your details to create your personalized Ayurvedic diet profile</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.5, 2, 0.5])
    
    with col2:
        st.markdown('<div class="ayur-card">', unsafe_allow_html=True)
        
        with st.form("registration_form"):
            st.markdown("### Personal Information")
            
            # Full Name
            full_name = st.text_input("Full Name *", placeholder="Enter your full name")
            
            # Phone and Email
            col_phone, col_email = st.columns(2)
            with col_phone:
                phone = st.text_input("Phone Number *", placeholder="10-digit number", max_chars=10)
            with col_email:
                email = st.text_input("Email Address *", placeholder="Enter your email")
            
            # Height and Weight
            col_height, col_weight = st.columns(2)
            with col_height:
                height = st.number_input("Height (cm) *", min_value=1, max_value=300, step=1)
            with col_weight:
                weight = st.number_input("Weight (kg) *", min_value=1.0, max_value=500.0, step=0.1)
            
            # Working Days
            working_days = st.selectbox("Working Days per Week *", 
                                      options=[1, 2, 3, 4, 5, 6, 7],
                                      format_func=lambda x: f"{x} day{'s' if x > 1 else ''}")
            
            # Diseases
            diseases = st.text_area("Past or Present Diseases (Optional)", 
                                  placeholder="Please mention any past or current health conditions, allergies, or medical history...")
            
            # Buttons
            col_back, col_submit = st.columns(2)
            
            with col_back:
                if st.form_submit_button("Back", use_container_width=True):
                    st.session_state.current_page = 'login'
                    st.rerun()
            
            with col_submit:
                if st.form_submit_button("Complete Registration", use_container_width=True):
                    # Validation
                    errors = []
                    if not full_name or len(full_name) < 2:
                        errors.append("Full name must be at least 2 characters")
                    if not phone or len(phone) != 10 or not phone.isdigit():
                        errors.append("Phone number must be exactly 10 digits")
                    if not email or '@' not in email:
                        errors.append("Please enter a valid email address")
                    if not height or height <= 0:
                        errors.append("Height must be a positive number")
                    if not weight or weight <= 0:
                        errors.append("Weight must be a positive number")
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        # Save registration data
                        st.session_state.patient_data = {
                            'full_name': full_name,
                            'phone': phone,
                            'email': email,
                            'height': height,
                            'weight': weight,
                            'working_days': working_days,
                            'diseases': diseases
                        }
                        st.success("Registration successful!")
                        st.session_state.logged_in = True
                        st.session_state.current_page = 'dashboard'
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def doctor_dashboard():
    """Doctor dashboard"""
    
    # Header with logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 🩺 Doctor Dashboard")
        st.markdown("**Welcome back, Dr. Smith** | Ayurvedic Diet Specialist")
    with col2:
        if st.button("Logout", type="secondary"):
            reset_app()
    
    st.markdown("---")
    
    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Patients", "127", delta="5")
    with col2:
        st.metric("Diet Plans Created", "89", delta="12")
    with col3:
        st.metric("This Month Consultations", "45", delta="8")
    with col4:
        st.metric("Success Rate", "94%", delta="2%")
    
    st.markdown("---")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Patient Management", "📅 Appointments", "🥗 Diet Plans", "📊 Analytics"])
    
    with tab1:
        st.markdown("### Patient List")
        
        # Sample patient data
        patients_data = {
            'Patient ID': ['P001', 'P002', 'P003', 'P004', 'P005'],
            'Name': ['Rajesh Kumar', 'Priya Sharma', 'Amit Patel', 'Sunita Devi', 'Rohit Singh'],
            'Age': [45, 32, 28, 38, 52],
            'Constitution': ['Vata-Pitta', 'Kapha-Vata', 'Pitta', 'Vata', 'Kapha-Pitta'],
            'Last Visit': ['2024-01-15', '2024-01-14', '2024-01-12', '2024-01-10', '2024-01-08'],
            'Status': ['Active', 'Active', 'Follow-up', 'Active', 'Completed']
        }
        
        df_patients = pd.DataFrame(patients_data)
        st.dataframe(df_patients, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("➕ Add New Patient", use_container_width=True)
        with col2:
            st.button("📊 View Patient Details", use_container_width=True)
    
    with tab2:
        st.markdown("### Today's Appointments")
        
        appointments_data = {
            'Time': ['09:00 AM', '10:30 AM', '02:00 PM', '03:30 PM', '05:00 PM'],
            'Patient': ['Rajesh Kumar', 'New Patient', 'Priya Sharma', 'Amit Patel', 'Follow-up Call'],
            'Type': ['Consultation', 'Initial Assessment', 'Follow-up', 'Diet Review', 'Virtual'],
            'Duration': ['30 min', '45 min', '20 min', '25 min', '15 min']
        }
        
        df_appointments = pd.DataFrame(appointments_data)
        st.dataframe(df_appointments, use_container_width=True)
    
    with tab3:
        st.markdown("### Create Diet Plan")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox("Select Patient", ['Rajesh Kumar', 'Priya Sharma', 'Amit Patel'])
            st.selectbox("Constitution Type", ['Vata', 'Pitta', 'Kapha', 'Vata-Pitta', 'Pitta-Kapha', 'Vata-Kapha'])
            st.selectbox("Primary Health Concern", ['Weight Management', 'Digestive Issues', 'Energy Levels', 'Sleep Problems'])
        
        with col2:
            st.multiselect("Six Tastes to Emphasize", ['Sweet', 'Sour', 'Salty', 'Bitter', 'Pungent', 'Astringent'])
            st.selectbox("Food Temperature Preference", ['Warm/Hot', 'Cool/Cold', 'Room Temperature'])
            st.selectbox("Meal Frequency", ['2 meals/day', '3 meals/day', '4-5 small meals/day'])
        
        st.text_area("Additional Notes & Restrictions")
        st.button("🥗 Generate Diet Plan", use_container_width=True)
    
    with tab4:
        st.markdown("### Analytics Dashboard")
        
        # Sample chart data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        patients = [20, 25, 30, 35, 40, 45]
        
        fig = px.line(x=months, y=patients, title="Patient Growth Over Time")
        fig.update_layout(xaxis_title="Month", yaxis_title="Number of Patients")
        st.plotly_chart(fig, use_container_width=True)
        
        # Constitution distribution
        constitution_data = {'Constitution': ['Vata', 'Pitta', 'Kapha', 'Vata-Pitta', 'Pitta-Kapha', 'Vata-Kapha'],
                           'Count': [15, 18, 12, 25, 20, 10]}
        
        fig2 = px.pie(constitution_data, values='Count', names='Constitution', 
                     title="Patient Constitution Distribution")
        st.plotly_chart(fig2, use_container_width=True)

def patient_dashboard():
    """Patient dashboard"""
    
    # Header with logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 👤 Patient Dashboard")
        patient_name = st.session_state.get('patient_data', {}).get('full_name', 'Patient')
        st.markdown(f"**Welcome back, {patient_name}** | Your Ayurvedic Wellness Journey")
    with col2:
        if st.button("Logout", type="secondary"):
            reset_app()
    
    st.markdown("---")
    
    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Weight", "68.5 kg", delta="-1.2 kg")
    with col2:
        st.metric("Days on Plan", "28", delta="7")
    with col3:
        st.metric("Meals Completed", "84/90", delta="6")
    with col4:
        st.metric("Wellness Score", "87%", delta="5%")
    
    st.markdown("---")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🥗 Today's Meals", "📊 Progress", "🧘 Constitution", "💡 Tips"])
    
    with tab1:
        st.markdown("### Today's Ayurvedic Diet Plan")
        st.markdown("*Based on your Vata-Pitta constitution*")
        
        # Breakfast
        with st.expander("🌅 Breakfast - 8:00 AM", expanded=True):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("""
                **Warm Oats with Almonds & Dates**
                - 1 cup oats cooked with milk
                - 5 soaked almonds, chopped
                - 2 dates, pitted and chopped
                - 1 tsp ghee
                - Pinch of cinnamon
                """)
            with col2:
                st.markdown("**Calories:** 350")
                st.markdown("**Tastes:** Sweet, Astringent")
                st.markdown("**Nature:** Warm")
                st.button("✓ Mark Complete", key="breakfast")
        
        # Lunch
        with st.expander("🌞 Lunch - 1:00 PM"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("""
                **Quinoa Bowl with Seasonal Vegetables**
                - 1 cup cooked quinoa
                - Mixed vegetables (carrots, peas, beans)
                - 1 tbsp ghee
                - Cumin and coriander seasoning
                - Fresh mint chutney
                """)
            with col2:
                st.markdown("**Calories:** 450")
                st.markdown("**Tastes:** Sweet, Bitter, Pungent")
                st.markdown("**Nature:** Warm")
                st.button("✓ Mark Complete", key="lunch")
        
        # Dinner
        with st.expander("🌙 Dinner - 7:00 PM"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("""
                **Light Khichdi with Vegetables**
                - 1/2 cup rice and moong dal
                - Seasonal vegetables
                - 1 tsp ghee
                - Ginger and turmeric
                - Side of yogurt
                """)
            with col2:
                st.markdown("**Calories:** 320")
                st.markdown("**Tastes:** Sweet, Salty, Sour")
                st.markdown("**Nature:** Warm")
                st.button("✓ Mark Complete", key="dinner")
    
    with tab2:
        st.markdown("### Your Wellness Progress")
        
        # Weight tracking
        weight_data = {
            'Date': pd.date_range('2024-01-01', periods=30, freq='D'),
            'Weight': [70 - i*0.05 + (i%7)*0.02 for i in range(30)]
        }
        df_weight = pd.DataFrame(weight_data)
        
        fig = px.line(df_weight, x='Date', y='Weight', title='Weight Progress Over Time')
        st.plotly_chart(fig, use_container_width=True)
        
        # Meal completion
        meal_completion = [90, 85, 95, 88, 92, 87, 93]
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        fig2 = px.bar(x=days, y=meal_completion, title='Weekly Meal Completion Rate (%)')
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        st.markdown("### Your Ayurvedic Constitution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### Primary Constitution: **Vata-Pitta**
            
            **Vata Characteristics (60%):**
            - Quick thinking and movement
            - Tendency towards dry skin
            - Variable appetite
            - Light sleeper
            
            **Pitta Characteristics (40%):**
            - Good digestion
            - Warm body temperature  
            - Goal-oriented nature
            - Moderate build
            """)
        
        with col2:
            st.markdown("""
            #### Dietary Guidelines:
            
            **Favor:**
            - Warm, cooked foods
            - Sweet, sour, salty tastes
            - Regular meal times
            - Adequate hydration
            
            **Minimize:**
            - Cold, raw foods
            - Spicy, bitter foods
            - Irregular eating
            - Excessive caffeine
            """)
        
        st.info("💡 Your constitution determines your dietary needs and helps create personalized meal plans.")
    
    with tab4:
        st.markdown("### Daily Wellness Tips")
        
        tips = [
            "🌅 **Morning Routine:** Start your day with warm water and lemon to kindle digestive fire",
            "🥗 **Mindful Eating:** Eat in a calm environment, chew slowly, and avoid distractions",
            "⏰ **Meal Timing:** Eat your largest meal at lunch when digestive fire is strongest",
            "🌿 **Herbal Tea:** Sip ginger tea after meals to aid digestion",
            "🧘 **Stress Management:** Practice deep breathing before meals to enhance digestion",
            "💧 **Hydration:** Drink room temperature or warm water throughout the day",
            "🌙 **Evening Routine:** Have a light dinner 3 hours before bedtime"
        ]
        
        for tip in tips:
            st.markdown(tip)
            st.markdown("")

# Main app logic
def main():
    """Main application logic"""
    
    if st.session_state.current_page == 'role_selection':
        role_selection_page()
    
    elif st.session_state.current_page == 'login':
        login_page()
    
    elif st.session_state.current_page == 'registration':
        patient_registration_page()
    
    elif st.session_state.current_page == 'dashboard' and st.session_state.logged_in:
        if st.session_state.user_role == 'doctor':
            doctor_dashboard()
        elif st.session_state.user_role == 'patient':
            patient_dashboard()

if __name__ == "__main__":
    main()