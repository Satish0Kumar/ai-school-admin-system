"""
Demo Presentation Script
Automated demonstration of Module 1 capabilities
"""
import requests
import json
import time

API_BASE_URL = "http://127.0.0.1:5000"

def print_divider():
    print("\n" + "="*70 + "\n")

def demo_intro():
    """Introduction"""
    print_divider()
    print("🎓 AI-BASED SMART SCHOOL ADMINISTRATION SYSTEM")
    print("   Module 1: Early Warning System for Student Risk Detection")
    print_divider()
    print("\n📊 System Overview:")
    print("  • Model: Gradient Boosting Classifier")
    print("  • Accuracy: 98.00%")
    print("  • Risk Levels: 4 (Low, Medium, High, Critical)")
    print("  • Features: 17 comprehensive parameters")
    print_divider()
    time.sleep(2)

def demo_model_info():
    """Show model information"""
    print("📈 Fetching Model Performance Metrics...")
    print_divider()
    
    response = requests.get(f"{API_BASE_URL}/api/risk/model-info")
    if response.status_code == 200:
        data = response.json()
        info = data.get('model_info', {})
        
        print(f"  Model Type: {info.get('model_name')}")
        print(f"  Accuracy: {info.get('accuracy')}")
        print(f"  Precision: {info.get('precision')}")
        print(f"  Recall: {info.get('recall')}")
        print(f"  F1-Score: {info.get('f1_score')}")
        print(f"  Trained: {info.get('trained_date')}")
    
    print_divider()
    time.sleep(2)

def demo_low_risk_student():
    """Demo: Low Risk Student"""
    print("📝 DEMO 1: Excellence Profile - Low Risk Student")
    print_divider()
    
    student = {
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
    
    print("Student Profile:")
    print(f"  • GPA: {student['current_gpa']} (Improving from {student['previous_gpa']})")
    print(f"  • Attendance: {student['attendance_percentage']}%")
    print(f"  • Assignment Completion: {student['assignment_submission_rate']}%")
    print(f"  • Behavioral Issues: {student['disciplinary_incidents']}")
    
    print("\n🔮 Making Prediction...")
    response = requests.post(f"{API_BASE_URL}/api/risk/predict", json=student)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ PREDICTION: {result['prediction']}")
        print(f"   Confidence: {result['confidence']:.1f}%")
        print("\n💡 Recommendations:")
        for rec in result.get('recommendations', []):
            print(f"   • {rec}")
    
    print_divider()
    time.sleep(3)

def demo_critical_risk_student():
    """Demo: Critical Risk Student"""
    print("🚨 DEMO 2: Urgent Intervention - Critical Risk Student")
    print_divider()
    
    student = {
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
    }
    
    print("Student Profile:")
    print(f"  • GPA: {student['current_gpa']} (Declining from {student['previous_gpa']})")
    print(f"  • Attendance: {student['attendance_percentage']}% (Chronic absenteeism)")
    print(f"  • Failed Subjects: {student['failed_subjects']}")
    print(f"  • Behavioral Issues: {student['disciplinary_incidents']}")
    
    print("\n🔮 Making Prediction...")
    response = requests.post(f"{API_BASE_URL}/api/risk/predict", json=student)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n⚠️  PREDICTION: {result['prediction']}")
        print(f"   Confidence: {result['confidence']:.1f}%")
        print("\n🚨 IMMEDIATE ACTIONS REQUIRED:")
        for rec in result.get('recommendations', []):
            print(f"   • {rec}")
    
    print_divider()
    time.sleep(3)

def demo_batch_prediction():
    """Demo: Batch Processing"""
    print("📊 DEMO 3: Batch Processing - Analyzing Multiple Students")
    print_divider()
    
    batch = {
        "students": [
            {
                "student_id": "STU001",
                "age": 16, "gender": "Male", "grade": 10,
                "socioeconomic_status": "Low", "parent_education": "High School",
                "current_gpa": 45.0, "previous_gpa": 50.0,
                "attendance_percentage": 65.0, "failed_subjects": 3,
                "assignment_submission_rate": 55.0, "disciplinary_incidents": 4
            },
            {
                "student_id": "STU002",
                "age": 15, "gender": "Female", "grade": 10,
                "socioeconomic_status": "High", "parent_education": "Post-Graduate",
                "current_gpa": 88.0, "previous_gpa": 85.0,
                "attendance_percentage": 95.0, "failed_subjects": 0,
                "assignment_submission_rate": 98.0, "disciplinary_incidents": 0
            },
            {
                "student_id": "STU003",
                "age": 16, "gender": "Male", "grade": 11,
                "socioeconomic_status": "Medium", "parent_education": "Graduate",
                "current_gpa": 70.0, "previous_gpa": 72.0,
                "attendance_percentage": 82.0, "failed_subjects": 1,
                "assignment_submission_rate": 80.0, "disciplinary_incidents": 1
            }
        ]
    }
    
    print(f"Processing {len(batch['students'])} students simultaneously...")
    
    response = requests.post(f"{API_BASE_URL}/api/risk/predict-batch", json=batch)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Successfully processed {result['successful_predictions']} students")
        print("\nResults:")
        
        for pred in result['predictions']:
            sid = pred.get('student_id')
            risk = pred['prediction']
            conf = pred['confidence']
            
            icon = "🔴" if "Critical" in risk else "🟠" if "High" in risk else "🟡" if "Medium" in risk else "🟢"
            print(f"  {icon} {sid}: {risk} (Confidence: {conf:.1f}%)")
    
    print_divider()
    time.sleep(2)

def demo_conclusion():
    """Conclusion"""
    print("✨ DEMONSTRATION COMPLETE")
    print_divider()
    print("\n🎯 Key Achievements:")
    print("  ✅ Real-time risk assessment with 98% accuracy")
    print("  ✅ 4-level risk classification (Low/Medium/High/Critical)")
    print("  ✅ Confidence scores for transparency")
    print("  ✅ Actionable intervention recommendations")
    print("  ✅ Batch processing capability")
    print("  ✅ RESTful API for easy integration")
    print("  ✅ Beautiful Streamlit web interface")
    
    print("\n📚 Next Modules (Planned):")
    print("  ⏳ Module 2: Behavioral Pattern Analysis")
    print("  ⏳ Module 3: Attendance & Dropout Prediction")
    print("  ⏳ Module 4: Institutional Performance Dashboard")
    
    print("\n🙏 Thank you for your attention!")
    print_divider()

def run_demo():
    """Run complete demonstration"""
    try:
        demo_intro()
        demo_model_info()
        demo_low_risk_student()
        demo_critical_risk_student()
        demo_batch_prediction()
        demo_conclusion()
        
        print("\n✅ Demo completed successfully!\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API!")
        print("Please start the Flask server: python backend/api.py\n")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  AI SCHOOL ADMINISTRATION SYSTEM - LIVE DEMO")
    print("="*70 + "\n")
    print("This will demonstrate all capabilities of Module 1.")
    print("Make sure the API server is running.")
    print("\n")
    
    input("Press Enter to start the demo...")
    run_demo()
