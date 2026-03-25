"""
API Testing Script
Tests all endpoints of the Risk Detection API
"""
import requests
import json
import sys

API_BASE_URL = "http://127.0.0.1:5000"


def print_section(title):
    """Print section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_health():
    """Test health check endpoint"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✓ Health check passed!")
            return True
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False


def test_model_info():
    """Test model info endpoint"""
    print_section("TEST 2: Model Information")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/risk/model-info", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✓ Model info retrieved successfully!")
            return True
    except Exception as e:
        print(f"❌ Model info failed: {str(e)}")
        return False


def test_single_prediction_low_risk():
    """Test single prediction - Low Risk student"""
    print_section("TEST 3: Single Prediction (Low Risk Student)")
    
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
        "disciplinary_incidents": 0,
        "counseling_visits": 0,
        "consecutive_absences": 0,
        "late_arrivals": 0,
        "library_visits": 8,
        "extracurricular_participation": 1
    }
    
    print("\nInput Data:")
    print(json.dumps(student_data, indent=2))
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/risk/predict",
            json=student_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Prediction Result:")
        result = response.json()
        print(json.dumps(result, indent=2))
        
        if response.status_code == 200 and result.get('success'):
            print(f"\n✓ Prediction: {result['prediction']}")
            print(f"✓ Confidence: {result['confidence']:.1f}%")
            return True
    except Exception as e:
        print(f"❌ Single prediction failed: {str(e)}")
        return False


def test_single_prediction_critical_risk():
    """Test single prediction - Critical Risk student"""
    print_section("TEST 4: Single Prediction (Critical Risk Student)")
    
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
        "disciplinary_incidents": 4,
        "counseling_visits": 2,
        "consecutive_absences": 5,
        "late_arrivals": 8,
        "library_visits": 1,
        "extracurricular_participation": 0
    }
    
    print("\nInput Data:")
    print(json.dumps(student_data, indent=2))
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/risk/predict",
            json=student_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Prediction Result:")
        result = response.json()
        print(json.dumps(result, indent=2))
        
        if response.status_code == 200 and result.get('success'):
            print(f"\n✓ Prediction: {result['prediction']}")
            print(f"✓ Confidence: {result['confidence']:.1f}%")
            return True
    except Exception as e:
        print(f"❌ Single prediction failed: {str(e)}")
        return False


def test_batch_prediction():
    """Test batch prediction"""
    print_section("TEST 5: Batch Prediction (2 Students)")
    
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
    
    print(f"\nPredicting for {len(batch_data['students'])} students...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/risk/predict-batch",
            json=batch_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Batch Prediction Results:")
        result = response.json()
        print(json.dumps(result, indent=2))
        
        if response.status_code == 200 and result.get('success'):
            print(f"\n✓ Processed {result['successful_predictions']} students successfully")
            return True
    except Exception as e:
        print(f"❌ Batch prediction failed: {str(e)}")
        return False


def test_invalid_input():
    """Test with invalid input"""
    print_section("TEST 6: Invalid Input Validation")
    
    invalid_data = {
        "age": 16,
        "gender": "InvalidGender",  # Invalid
        "grade": 10,
        "current_gpa": 150  # Invalid (> 100)
    }
    
    print("\nSending invalid data (should fail validation):")
    print(json.dumps(invalid_data, indent=2))
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/risk/predict",
            json=invalid_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("✓ Validation correctly rejected invalid input!")
            return True
    except Exception as e:
        print(f"❌ Invalid input test failed: {str(e)}")
        return False


def run_all_tests():
    """Run all API tests"""
    print("\n" + "="*70)
    print("  API TESTING SUITE - RISK DETECTION MODULE")
    print("="*70)
    print("\nMake sure the API server is running:")
    print("  python backend/api.py")
    print("\nPress Enter to start testing...")
    input()
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Model Info", test_model_info()))
    results.append(("Single Prediction (Low Risk)", test_single_prediction_low_risk()))
    results.append(("Single Prediction (Critical Risk)", test_single_prediction_critical_risk()))
    results.append(("Batch Prediction", test_batch_prediction()))
    results.append(("Invalid Input", test_invalid_input()))
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! API is working correctly!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check the output above.")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite error: {str(e)}")
