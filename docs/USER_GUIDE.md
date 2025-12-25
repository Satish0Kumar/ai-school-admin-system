# User Guide - AI School Administration System

## Module 1: Early Warning System

### Getting Started

1. Activate environment  
2. Start backend:
   python backend/api.py

3. Start frontend:
   streamlit run frontend/app.py

### Using the System
- Enter student data
- Click "Predict Risk Level"
- View results with confidence, charts, and recommendations

### Risk Levels
🟢 Low Risk  
🟡 Medium Risk  
🟠 High Risk  
🔴 Critical Risk

### Troubleshooting
If API not connecting:
- Ensure backend is running
- Restart Streamlit
- Check ports 5000 & 8501
