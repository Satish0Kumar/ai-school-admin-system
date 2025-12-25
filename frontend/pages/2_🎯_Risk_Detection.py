"""
Risk Detection Page - Main prediction interface
"""
import streamlit as st
import sys
from pathlib import Path

# Add frontend to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.api_client import api_client
from utils.visualizations import create_confidence_chart, create_gauge_chart

# Page configuration
st.set_page_config(
    page_title="Risk Detection",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .prediction-box {
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }
    .low-risk {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border: 3px solid #4caf50;
    }
    .medium-risk {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border: 3px solid #ff9800;
    }
    .high-risk {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border: 3px solid #f44336;
    }
    .critical-risk {
        background: linear-gradient(135deg, #fce4ec 0%, #f8bbd0 100%);
        border: 3px solid #c62828;
    }
    .prediction-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .confidence-score {
        font-size: 1.5rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🎯 Student Risk Detection")
st.markdown("Enter student information to predict their risk level")

# Check API connection
with st.spinner("Checking API connection..."):
    is_healthy, _ = api_client.health_check()

if not is_healthy:
    st.error("⚠️ **API Server is not running!**")
    st.info("Please start the Flask API server:")
    st.code("python backend/api.py", language="bash")
    st.stop()

st.divider()

# Create tabs for single and batch prediction
tab1, tab2 = st.tabs(["📝 Single Student", "📊 Batch Prediction"])

# ==================== SINGLE STUDENT PREDICTION ====================
with tab1:
    st.subheader("Enter Student Information")
    
    # Create form columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 Demographics")
        
        age = st.number_input(
            "Age",
            min_value=14,
            max_value=20,
            value=16,
            help="Student's age (14-20 years)"
        )
        
        gender = st.selectbox(
            "Gender",
            options=["Male", "Female"],
            help="Student's gender"
        )
        
        grade = st.selectbox(
            "Grade",
            options=[9, 10, 11, 12],
            index=1,
            help="Current grade level"
        )
        
        ses = st.selectbox(
            "Socioeconomic Status",
            options=["Low", "Medium", "High"],
            index=1,
            help="Family's socioeconomic status"
        )
        
        parent_edu = st.selectbox(
            "Parent Education",
            options=["None", "High School", "Graduate", "Post-Graduate"],
            index=2,
            help="Highest parent education level"
        )
    
    with col2:
        st.markdown("### 📚 Academic & Behavioral")
        
        current_gpa = st.slider(
            "Current GPA (0-100)",
            min_value=0,
            max_value=100,
            value=70,
            help="Current semester GPA"
        )
        
        previous_gpa = st.slider(
            "Previous GPA (0-100)",
            min_value=0,
            max_value=100,
            value=72,
            help="Previous semester GPA"
        )
        
        attendance = st.slider(
            "Attendance Percentage",
            min_value=0,
            max_value=100,
            value=85,
            help="Overall attendance rate"
        )
        
        failed_subjects = st.number_input(
            "Failed Subjects",
            min_value=0,
            max_value=10,
            value=0,
            help="Number of failed subjects"
        )
        
        assignment_rate = st.slider(
            "Assignment Submission Rate (%)",
            min_value=0,
            max_value=100,
            value=85,
            help="Percentage of assignments submitted"
        )
        
        incidents = st.number_input(
            "Disciplinary Incidents",
            min_value=0,
            max_value=20,
            value=0,
            help="Number of disciplinary incidents"
        )
    
    # Calculate derived features (will be calculated by backend, but shown for transparency)
    grade_trend = current_gpa - previous_gpa
    
    st.divider()
    
    # Show quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        trend_icon = "📈" if grade_trend > 0 else "📉" if grade_trend < 0 else "➡️"
        st.metric("Grade Trend", f"{grade_trend:+.1f}", delta=None)
    
    with col2:
        st.metric("Attendance", f"{attendance}%")
    
    with col3:
        st.metric("Failed Subjects", failed_subjects)
    
    with col4:
        st.metric("Incidents", incidents)
    
    st.divider()
    
    # Predict button
    if st.button("🎯 Predict Risk Level", type="primary", use_container_width=True):
        
        # Prepare student data
        student_data = {
            "age": age,
            "gender": gender,
            "grade": grade,
            "socioeconomic_status": ses,
            "parent_education": parent_edu,
            "current_gpa": float(current_gpa),
            "previous_gpa": float(previous_gpa),
            "attendance_percentage": float(attendance),
            "failed_subjects": failed_subjects,
            "assignment_submission_rate": float(assignment_rate),
            "disciplinary_incidents": incidents,
            # Derived features (backend will calculate these too)
            "counseling_visits": 1 if incidents > 2 else 0,
            "consecutive_absences": int((100 - attendance) / 10),
            "late_arrivals": int((100 - attendance) / 15),
            "library_visits": 5 if current_gpa > 75 else 2,
            "extracurricular_participation": 1 if current_gpa > 70 else 0
        }
        
        # Make prediction
        with st.spinner("🔮 Analyzing student data..."):
            result = api_client.predict_risk(student_data)
        
        if result and result.get('success'):
            # Get prediction details
            prediction = result['prediction']
            confidence = result['confidence']
            probabilities = result['probabilities']
            recommendations = result.get('recommendations', [])
            
            # Determine CSS class based on risk level
            risk_class_map = {
                'Low Risk': 'low-risk',
                'Medium Risk': 'medium-risk',
                'High Risk': 'high-risk',
                'Critical Risk': 'critical-risk'
            }
            risk_class = risk_class_map.get(prediction, 'low-risk')
            
            # Display prediction box
            st.markdown(f"""
            <div class="prediction-box {risk_class}">
                <div class="prediction-title">{prediction}</div>
                <div class="confidence-score">Confidence: {confidence:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Create two columns for visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Confidence distribution chart
                fig_bars = create_confidence_chart(probabilities)
                st.plotly_chart(fig_bars, use_container_width=True)
            
            with col2:
                # Gauge chart
                fig_gauge = create_gauge_chart(confidence, prediction)
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Recommendations
            st.divider()
            st.subheader("📋 Intervention Recommendations")
            
            if prediction == "Critical Risk":
                st.error("🚨 **IMMEDIATE ACTION REQUIRED**")
            elif prediction == "High Risk":
                st.warning("⚠️ **Intervention Recommended**")
            elif prediction == "Medium Risk":
                st.info("ℹ️ **Monitoring Suggested**")
            else:
                st.success("✅ **Student Performing Well**")
            
            for rec in recommendations:
                st.markdown(f"- {rec}")
            
            # Show probability details
            with st.expander("📊 Detailed Probability Breakdown"):
                st.json(probabilities)

# ==================== BATCH PREDICTION ====================
with tab2:
    st.subheader("📊 Batch Student Risk Analysis")
    
    st.info("💡 **Tip**: Upload a CSV file or enter multiple students manually for batch predictions")
    
    # Option 1: Quick test with sample data
    st.markdown("### 🧪 Quick Test with Sample Data")
    
    if st.button("Run Sample Batch Prediction (2 Students)", type="secondary"):
        
        sample_students = [
            {
                "student_id": "STU001",
                "age": 16,
                "gender": "Male",
                "grade": 10,
                "socioeconomic_status": "Low",
                "parent_education": "High School",
                "current_gpa": 45.0,
                "previous_gpa": 50.0,
                "attendance_percentage": 65.0,
                "failed_subjects": 3,
                "assignment_submission_rate": 55.0,
                "disciplinary_incidents": 4
            },
            {
                "student_id": "STU002",
                "age": 15,
                "gender": "Female",
                "grade": 10,
                "socioeconomic_status": "High",
                "parent_education": "Post-Graduate",
                "current_gpa": 88.0,
                "previous_gpa": 85.0,
                "attendance_percentage": 95.0,
                "failed_subjects": 0,
                "assignment_submission_rate": 98.0,
                "disciplinary_incidents": 0
            }
        ]
        
        with st.spinner("🔮 Analyzing batch of students..."):
            result = api_client.predict_batch(sample_students)
        
        if result and result.get('success'):
            st.success(f"✅ Successfully processed {result['successful_predictions']} out of {result['total_students']} students")
            
            # Display results in table format
            predictions = result['predictions']
            
            for pred in predictions:
                student_id = pred.get('student_id', 'Unknown')
                risk = pred['prediction']
                conf = pred['confidence']
                
                # Color code based on risk
                if risk == "Critical Risk":
                    st.error(f"**{student_id}**: {risk} (Confidence: {conf:.1f}%)")
                elif risk == "High Risk":
                    st.warning(f"**{student_id}**: {risk} (Confidence: {conf:.1f}%)")
                elif risk == "Medium Risk":
                    st.info(f"**{student_id}**: {risk} (Confidence: {conf:.1f}%)")
                else:
                    st.success(f"**{student_id}**: {risk} (Confidence: {conf:.1f}%)")
                
                with st.expander(f"View details for {student_id}"):
                    st.json(pred)
    
    st.divider()
    
    # Option 2: CSV Upload (placeholder for future)
    st.markdown("### 📁 Upload CSV File (Coming Soon)")
    st.info("CSV upload functionality will be added in future updates")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        disabled=True,
        help="Upload a CSV file with student data"
    )

# Footer
st.divider()
st.caption("💡 **Tip**: All predictions are made in real-time using the 98% accuracy Gradient Boosting model")
