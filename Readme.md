# AyurDiet - Ayurvedic Diet Management System

A comprehensive Ayurvedic diet management application built with Streamlit, designed to help doctors create personalized diet plans and patients track their wellness journey based on Ayurvedic principles.

## Features

### Doctor Portal
- Patient management dashboard
- Appointment scheduling
- Ayurvedic diet plan creation based on constitution
- Analytics and progress tracking
- Integration of six tastes (Rasa) and food properties

### Patient Portal  
- Personalized daily meal plans
- Progress tracking (weight, meal completion)
- Constitution-based dietary guidelines
- Wellness tips and recommendations
- Interactive meal logging

## Installation & Setup

### Local Development

1. **Clone or download the application files**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the application**
   - Open your browser to `http://localhost:8501`

### Streamlit Cloud Deployment

1. **Upload to GitHub**
   - Create a new GitHub repository
   - Upload `app.py` and `requirements.txt`

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select the main branch and `app.py` as the main file
   - Click "Deploy"

3. **Access your deployed app**
   - Your app will be available at `https://[your-app-name].streamlit.app`

## Usage

### Getting Started

1. **Choose Your Role**
   - Select either "Doctor Portal" or "Patient Portal" from the main page

2. **Doctor Login**
   - Use any email/password combination (demo mode)
   - Access patient management, appointments, and diet plan creation tools

3. **Patient Registration/Login**
   - New patients can register with their personal information
   - Existing patients can login with their credentials
   - Access personalized meal plans and progress tracking

### Key Features

- **Ayurvedic Constitution Integration**: Diet plans based on Vata, Pitta, Kapha principles
- **Six Tastes (Rasa)**: Balanced incorporation of sweet, sour, salty, bitter, pungent, astringent
- **Food Properties**: Hot/Cold nature and digestibility considerations
- **Modern Metrics**: Caloric values alongside traditional wisdom

## Technical Details

### Built With
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive charts and visualizations
- **Python**: Core programming language

### File Structure
```
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # Documentation
```

## Demo Credentials

Since this is a frontend-only demo application:

**Doctor Login**: Any email and password combination  
**Patient Login**: Register as new patient or use any email/password

## Customization

The application can be easily customized by modifying:

- **Colors and Styling**: Update the CSS in the `st.markdown()` sections
- **Data**: Replace mock data with real database connections
- **Features**: Add new tabs, forms, or functionality as needed

## Future Enhancements

- Database integration for persistent data storage
- User authentication system
- Advanced Ayurvedic assessment questionnaires
- Meal photo uploads and analysis
- Integration with fitness trackers
- Seasonal diet recommendations

## Support

This is a demonstration application showcasing Ayurvedic diet management concepts. For production use, consider adding:

- Proper user authentication
- Database backend
- Security measures
- Professional medical oversight

---

**Note**: This application is for educational and demonstration purposes. Always consult qualified healthcare professionals for medical advice.