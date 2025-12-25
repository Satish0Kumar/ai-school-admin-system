"""
Integration Test Suite - End-to-End Testing
Tests the complete flow from Frontend → API → Model → Response
"""
import requests
import json
import time

API_BASE_URL = "http://127.0.0.1:5000"

class Colors:
    """Terminal colors for better output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

# Test counters
tests_passed = 0
tests_failed = 0
tests_total = 0

def run_test(test_name, test_func):
    """Run a single test and track results"""
    global tests_passed, tests_failed, tests_total
    tests_total += 1
    
    try:
        result = test_func()
        if result:
            print_success(f"TEST {tests_total}: {test_name}")
            tests_passed += 1
            return True
        else:
            print_error(f"TEST {tests_total}: {test_name}")
            tests_failed += 1
            return False
    except Exception as e:
        print_error(f"TEST {tests_total}: {test_name} - Exception: {str(e)}")
        tests_failed += 1
        return False

# ==================== TEST FUNCTIONS ====================

def test_api_connectivity():
    """Test if API is accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_health_endpoint():
    """Test health check endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        data = response.json()
        return response.status_code == 200 and data.get('status') == 'healthy'
    except:
        return False

def test_model_info():
    """Test model info endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/risk/model-info", timeout=5)
        data = response.json()
        return (response.status_code == 200 and 
                data.get('success') and 
                'model_info' in data)
    except:
        return False

def test_low_risk_prediction():
    """Test Low Risk prediction accuracy"""
    student_data = {
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
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/risk/predict",
            json=student_data,
            timeout=5
        )
        data = response.json()
        return (response.status_code == 200 and 
                data.get('success') and 
                data.get('prediction') == 'Low Risk' and
                data.get('confidence') > 95)
    except:
        return False

def test_critical_risk_prediction():
    """Test Critical Risk prediction accuracy"""
    student_data = {
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
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/risk/predict",
            json=student_data,
            timeout=5
        )
        data = response.json()
        return (response.status_code == 200 and 
                data.get('success') and 
                data.get('prediction') == 'Critical Risk' and
                data.get('confidence') > 95)
    except:
        return False

def test_medium_risk_prediction():
    """Test Medium Risk prediction"""
    student_data = {
        "age": 16,
        "gender": "Male",
        "grade": 10,
        "socioeconomic_status": "Medium",
        "parent_education": "Graduate",
        "current_gpa": 65.0,
        "previous_gpa": 68.0,
        "attendance_percentage": 78.0,
        "failed_subjects": 1,
        "assignment_submission_rate": 75.0,
        "disciplinary_incidents": 1
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/risk/predict",
            json=student_data,
            timeout=5
        )
        data = response.json()
        return (response.status_code == 200 and 
                data.get('success') and
                data.get('prediction') in ['Medium Risk', 'Low Risk', 'High Risk'])
    except:
        return False

def test_missing_required_fields():
    """Test validation for missing fields"""
    student_data = {
        "age": 16,
        "gender": "Male"
        # Missing required fields
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/risk/predict",
            json=student_data,
            timeout=5
        )
        return response.status_code == 400  # Should return bad request
    except:
        return False

def test_invalid_gender():
    """Test validation for invalid gender"""
    student_data = {
        "age": 16,
        "gender": "InvalidGender",
        "grade": 10,
        "socioeconomic_status": "Medium",
        "parent_education": "Graduate",
        "current_gpa": 70.0,
        "previous_gpa": 68.0,
        "attendance_percentage": 80.0,
        "failed_subjects": 0,
        "assignment_submission_rate": 85.0,
        "disciplinary_incidents": 0
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/risk/predict",
            json=student_data,
            timeout=5
        )
        return response.status_code == 400
    except:
        return False

def test_invalid_gpa_range():
    """Test validation for GPA out of range"""
    student_data = {
        "age": 16,
        "gender": "Male",
        "grade": 10,
        "socioeconomic_status": "Medium",
        "parent_education": "Graduate",
        "current_gpa": 150.0,  # Invalid (> 100)
        "previous_gpa": 68.0,
        "attendance_percentage": 80.0,
        "failed_subjects": 0,
        "assignment_submission_rate": 85.0,
        "disciplinary_incidents": 0
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/risk/predict",
            json=student_data,
            timeout=5
        )
        return response.status_code == 400
    except:
        return False

def test_batch_prediction():
    """Test batch prediction with multiple students"""
    batch_data = {
        "students": [
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
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/risk/predict-batch",
            json=batch_data,
            timeout=10
        )
        data = response.json()
        return (response.status_code == 200 and 
                data.get('success') and 
                data.get('successful_predictions') == 2)
    except:
        return False

def test_response_time():
    """Test API response time (should be < 1 second)"""
    student_data = {
        "age": 16,
        "gender": "Male",
        "grade": 10,
        "socioeconomic_status": "Medium",
        "parent_education": "Graduate",
        "current_gpa": 70.0,
        "previous_gpa": 68.0,
        "attendance_percentage": 80.0,
        "failed_subjects": 0,
        "assignment_submission_rate": 85.0,
        "disciplinary_incidents": 0
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/api/risk/predict",
            json=student_data,
            timeout=5
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"    Response time: {response_time:.3f} seconds")
        
        return response.status_code == 200 and response_time < 1.0
    except:
        return False

def test_confidence_scores():
    """Test that confidence scores are within valid range"""
    student_data = {
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
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/risk/predict",
            json=student_data,
            timeout=5
        )
        data = response.json()
        
        if not data.get('success'):
            return False
        
        confidence = data.get('confidence', 0)
        probabilities = data.get('probabilities', {})
        
        # Check confidence is 0-100
        if not (0 <= confidence <= 100):
            return False
        
        # Check all probabilities sum to ~100
        total_prob = sum(probabilities.values())
        if not (99 <= total_prob <= 101):  # Allow small floating point errors
            return False
        
        return True
    except:
        return False

def test_recommendations_present():
    """Test that recommendations are provided"""
    student_data = {
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
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/risk/predict",
            json=student_data,
            timeout=5
        )
        data = response.json()
        
        recommendations = data.get('recommendations', [])
        return len(recommendations) > 0
    except:
        return False

# ==================== MAIN TEST RUNNER ====================

def run_all_tests():
    """Run all integration tests"""
    print_header("MODULE 1 - INTEGRATION TEST SUITE")
    print(f"Testing API at: {API_BASE_URL}")
    print(f"Date: Thursday, December 25, 2025")
    print("\n")
    
    # Connectivity Tests
    print_header("1. CONNECTIVITY TESTS")
    run_test("API Server Connectivity", test_api_connectivity)
    run_test("Health Check Endpoint", test_health_endpoint)
    run_test("Model Info Endpoint", test_model_info)
    
    # Prediction Accuracy Tests
    print_header("2. PREDICTION ACCURACY TESTS")
    run_test("Low Risk Student Prediction", test_low_risk_prediction)
    run_test("Critical Risk Student Prediction", test_critical_risk_prediction)
    run_test("Medium Risk Student Prediction", test_medium_risk_prediction)
    
    # Validation Tests
    print_header("3. INPUT VALIDATION TESTS")
    run_test("Missing Required Fields Validation", test_missing_required_fields)
    run_test("Invalid Gender Validation", test_invalid_gender)
    run_test("Invalid GPA Range Validation", test_invalid_gpa_range)
    
    # Functional Tests
    print_header("4. FUNCTIONAL TESTS")
    run_test("Batch Prediction Processing", test_batch_prediction)
    run_test("API Response Time (<1s)", test_response_time)
    run_test("Confidence Scores Valid Range", test_confidence_scores)
    run_test("Recommendations Present", test_recommendations_present)
    
    # Final Summary
    print_header("TEST SUMMARY")
    print(f"Total Tests: {tests_total}")
    print_success(f"Passed: {tests_passed}")
    if tests_failed > 0:
        print_error(f"Failed: {tests_failed}")
    print(f"\nSuccess Rate: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! MODULE 1 IS READY FOR DEPLOYMENT!{Colors.END}\n")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ Some tests failed. Please review the errors above.{Colors.END}\n")
    
    return tests_failed == 0


if __name__ == "__main__":
    print("\n")
    print(f"{Colors.BOLD}AI School Administration System - Module 1{Colors.END}")
    print(f"{Colors.BOLD}Integration Test Suite{Colors.END}")
    print("\n")
    print("Make sure the API server is running before testing:")
    print(f"{Colors.BLUE}  python backend/api.py{Colors.END}")
    print("\n")
    
    input("Press Enter to start testing...")
    
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.END}\n")
        exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}Test suite error: {str(e)}{Colors.END}\n")
        exit(1)
