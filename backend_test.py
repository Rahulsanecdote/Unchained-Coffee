#!/usr/bin/env python3
"""
Backend API testing for Unchained Coffee Taste Fit application
"""
import requests
import json
import sys
import uuid
from datetime import datetime


class TasteFitAPITester:
    def __init__(self, base_url="https://402cedbd-e175-4199-9a28-4fff2f6d6800.preview.emergentagent.com"):
        self.base_url = base_url
        self.session_id = str(uuid.uuid4())
        self.admin_token = None
        self.viewer_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failures = []

    def log_test(self, name, passed, details=""):
        """Log test result"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            print(f"✅ {name}: PASSED")
        else:
            self.failures.append(f"{name}: {details}")
            print(f"❌ {name}: FAILED - {details}")

    def test_health(self):
        """Test health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                success = data.get("status") == "ok"
            self.log_test("Health Check", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False

    def test_admin_login(self):
        """Test admin login"""
        try:
            payload = {
                "email": "admin@unchainedcoffee.com",
                "password": "unchained2025"
            }
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=payload,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                if "token" in data and data.get("role") == "admin":
                    self.admin_token = data["token"]
                    self.log_test("Admin Login", True)
                else:
                    self.log_test("Admin Login", False, "Missing token or role")
                    success = False
            else:
                self.log_test("Admin Login", False, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Admin Login", False, str(e))
            return False

    def test_viewer_login(self):
        """Test viewer login"""
        try:
            payload = {
                "email": "viewer@unchainedcoffee.com",
                "password": "viewer2025"
            }
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=payload,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                if "token" in data and data.get("role") == "viewer":
                    self.viewer_token = data["token"]
                    self.log_test("Viewer Login", True)
                else:
                    self.log_test("Viewer Login", False, "Missing token or role")
                    success = False
            else:
                self.log_test("Viewer Login", False, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Viewer Login", False, str(e))
            return False

    def test_invalid_login(self):
        """Test invalid login credentials"""
        try:
            payload = {
                "email": "invalid@test.com",
                "password": "wrongpassword"
            }
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=payload,
                timeout=10
            )
            success = response.status_code == 401
            self.log_test("Invalid Login", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Invalid Login", False, str(e))
            return False

    def test_create_profile(self):
        """Test creating affective profile"""
        try:
            payload = {
                "session_id": self.session_id,
                "aroma_pref_1to9": 7,
                "flavor_pref_1to9": 8,
                "aftertaste_pref_1to9": 6,
                "acidity_pref_1to9": 5,
                "sweetness_pref_1to9": 7,
                "mouthfeel_pref_1to9": 8,
                "consent_analytics": True,
                "consent_marketing": False
            }
            response = requests.post(
                f"{self.base_url}/api/affective/profile",
                json=payload,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = data.get("status") == "ok" and "profile_id" in data
            self.log_test("Create Affective Profile", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Create Affective Profile", False, str(e))
            return False

    def test_get_profile(self):
        """Test getting affective profile"""
        try:
            response = requests.get(
                f"{self.base_url}/api/affective/profile?session_id={self.session_id}",
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = "profile" in data and data["profile"] is not None
            self.log_test("Get Affective Profile", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Get Affective Profile", False, str(e))
            return False

    def test_profile_validation(self):
        """Test profile validation (invalid range)"""
        try:
            payload = {
                "session_id": self.session_id,
                "aroma_pref_1to9": 10,  # Invalid: should be 1-9
                "flavor_pref_1to9": 8,
                "aftertaste_pref_1to9": 6,
                "acidity_pref_1to9": 5,
                "sweetness_pref_1to9": 7,
                "mouthfeel_pref_1to9": 8
            }
            response = requests.post(
                f"{self.base_url}/api/affective/profile",
                json=payload,
                timeout=10
            )
            success = response.status_code == 422  # Validation error expected
            self.log_test("Profile Validation (Invalid Range)", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Profile Validation (Invalid Range)", False, str(e))
            return False

    def test_create_preference_response(self):
        """Test creating preference-only response"""
        try:
            payload = {
                "session_id": self.session_id,
                "product_id": "papayo-natural",
                "variant_id": "papayo-12oz-whole",
                "mode": "preference_only",
                "aroma_1to9": 7,
                "flavor_1to9": 8,
                "aftertaste_1to9": 6,
                "acidity_1to9": 5,
                "sweetness_1to9": 7,
                "mouthfeel_1to9": 8,
                "consent_analytics": True,
                "consent_marketing": False
            }
            response = requests.post(
                f"{self.base_url}/api/affective/response",
                json=payload,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = data.get("status") == "ok" and "response_id" in data
            self.log_test("Create Preference Response", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Create Preference Response", False, str(e))
            return False

    def test_create_tasted_response(self):
        """Test creating tasted response with all required fields"""
        try:
            payload = {
                "session_id": self.session_id,
                "product_id": "papayo-natural",
                "variant_id": "papayo-12oz-whole",
                "mode": "tasted",
                "aroma_1to9": 7,
                "flavor_1to9": 8,
                "aftertaste_1to9": 6,
                "acidity_1to9": 5,
                "sweetness_1to9": 7,
                "mouthfeel_1to9": 8,
                "overall_liking_1to9": 8,
                "notes": "Great coffee with chocolate notes",
                "standout_tags": ["chocolate", "nutty"],
                "fit_tags": ["perfect match"],
                "consent_analytics": True,
                "consent_marketing": False
            }
            response = requests.post(
                f"{self.base_url}/api/affective/response",
                json=payload,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = data.get("status") == "ok" and "response_id" in data
            self.log_test("Create Tasted Response", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Create Tasted Response", False, str(e))
            return False

    def test_tasted_validation(self):
        """Test tasted mode validation (missing required fields)"""
        try:
            payload = {
                "session_id": self.session_id,
                "product_id": "papayo-natural",
                "mode": "tasted",
                "aroma_1to9": 7,
                # Missing other required fields for tasted mode
                "consent_analytics": True
            }
            response = requests.post(
                f"{self.base_url}/api/affective/response",
                json=payload,
                timeout=10
            )
            success = response.status_code == 422  # Validation error expected
            self.log_test("Tasted Mode Validation", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Tasted Mode Validation", False, str(e))
            return False

    def test_create_event(self):
        """Test creating events"""
        try:
            payload = {
                "event_name": "product_viewed",
                "session_id": self.session_id,
                "product_id": "papayo-natural",
                "metadata": {"test": True}
            }
            response = requests.post(
                f"{self.base_url}/api/events",
                json=payload,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = data.get("status") == "ok"
            self.log_test("Create Event", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Create Event", False, str(e))
            return False

    def test_admin_products(self):
        """Test admin products endpoint"""
        if not self.admin_token:
            self.log_test("Admin Products", False, "No admin token available")
            return False
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(
                f"{self.base_url}/api/admin/products",
                headers=headers,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = "products" in data
            self.log_test("Admin Products", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Admin Products", False, str(e))
            return False

    def test_admin_product_summary(self):
        """Test admin product summary endpoint"""
        if not self.admin_token:
            self.log_test("Admin Product Summary", False, "No admin token available")
            return False
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(
                f"{self.base_url}/api/admin/products/summary?product_id=papayo-natural",
                headers=headers,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = "count" in data and "averages" in data
            self.log_test("Admin Product Summary", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Admin Product Summary", False, str(e))
            return False

    def test_admin_segments(self):
        """Test admin segments endpoint"""
        if not self.admin_token:
            self.log_test("Admin Segments", False, "No admin token available")
            return False
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(
                f"{self.base_url}/api/admin/segments",
                headers=headers,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = "segments" in data and "total_profiles" in data
            self.log_test("Admin Segments", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Admin Segments", False, str(e))
            return False

    def test_admin_funnel(self):
        """Test admin funnel endpoint"""
        if not self.admin_token:
            self.log_test("Admin Funnel", False, "No admin token available")
            return False
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(
                f"{self.base_url}/api/admin/funnel",
                headers=headers,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = "funnel" in data
            self.log_test("Admin Funnel", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Admin Funnel", False, str(e))
            return False

    def test_admin_unauthorized(self):
        """Test admin endpoints without token"""
        try:
            response = requests.get(
                f"{self.base_url}/api/admin/products",
                timeout=10
            )
            success = response.status_code == 401  # Unauthorized expected
            self.log_test("Admin Unauthorized Access", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Admin Unauthorized Access", False, str(e))
            return False

    def test_viewer_admin_access(self):
        """Test viewer trying to access admin-only functions"""
        if not self.viewer_token:
            self.log_test("Viewer Admin Access", False, "No viewer token available")
            return False
        try:
            headers = {"Authorization": f"Bearer {self.viewer_token}"}
            response = requests.delete(
                f"{self.base_url}/api/admin/data?session_id=test",
                headers=headers,
                timeout=10
            )
            success = response.status_code == 403  # Forbidden expected
            self.log_test("Viewer Admin Access (Forbidden)", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Viewer Admin Access (Forbidden)", False, str(e))
            return False

    def test_taste_fit_score_with_profile(self):
        """Test taste-fit score endpoint when profile exists"""
        try:
            # Ensure profile exists first
            self.test_create_profile()
            
            # Mock product sensory data (from papayo-natural)
            payload = {
                "session_id": self.session_id,
                "product_sensory": {
                    "aroma": 7,
                    "flavor": 8,
                    "aftertaste": 7,
                    "acidity": 6,
                    "sweetness": 8,
                    "mouthfeel": 7
                }
            }
            response = requests.post(
                f"{self.base_url}/api/affective/taste-fit",
                json=payload,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = (
                    data.get("profile_exists") == True and
                    "score" in data and
                    "label" in data and
                    "breakdown" in data and
                    isinstance(data["score"], int) and
                    0 <= data["score"] <= 100
                )
            self.log_test("Taste-Fit Score (With Profile)", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Taste-Fit Score (With Profile)", False, str(e))
            return False

    def test_taste_fit_score_no_profile(self):
        """Test taste-fit score endpoint when no profile exists"""
        try:
            # Use a different session ID without profile
            new_session_id = str(uuid.uuid4())
            payload = {
                "session_id": new_session_id,
                "product_sensory": {
                    "aroma": 7,
                    "flavor": 8,
                    "aftertaste": 7,
                    "acidity": 6,
                    "sweetness": 8,
                    "mouthfeel": 7
                }
            }
            response = requests.post(
                f"{self.base_url}/api/affective/taste-fit",
                json=payload,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = (
                    data.get("profile_exists") == False and
                    data.get("score") is None
                )
            self.log_test("Taste-Fit Score (No Profile)", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Taste-Fit Score (No Profile)", False, str(e))
            return False

    def test_taste_fit_batch_with_profile(self):
        """Test taste-fit batch endpoint for multiple products"""
        try:
            # Ensure profile exists first
            self.test_create_profile()
            
            # Mock multiple products with sensory data
            payload = {
                "session_id": self.session_id,
                "products": [
                    {
                        "product_id": "papayo-natural",
                        "sensory": {
                            "aroma": 7, "flavor": 8, "aftertaste": 7,
                            "acidity": 6, "sweetness": 8, "mouthfeel": 7
                        }
                    },
                    {
                        "product_id": "geisha-honey",
                        "sensory": {
                            "aroma": 8, "flavor": 9, "aftertaste": 8,
                            "acidity": 7, "sweetness": 8, "mouthfeel": 6
                        }
                    }
                ]
            }
            response = requests.post(
                f"{self.base_url}/api/affective/taste-fit/batch",
                json=payload,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = (
                    data.get("profile_exists") == True and
                    "scores" in data and
                    isinstance(data["scores"], list) and
                    len(data["scores"]) == 2 and
                    all("product_id" in score and "score" in score and "label" in score 
                        for score in data["scores"])
                )
            self.log_test("Taste-Fit Batch (With Profile)", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Taste-Fit Batch (With Profile)", False, str(e))
            return False

    def test_taste_fit_batch_no_profile(self):
        """Test taste-fit batch endpoint when no profile exists"""
        try:
            # Use a different session ID without profile
            new_session_id = str(uuid.uuid4())
            payload = {
                "session_id": new_session_id,
                "products": [
                    {
                        "product_id": "papayo-natural",
                        "sensory": {
                            "aroma": 7, "flavor": 8, "aftertaste": 7,
                            "acidity": 6, "sweetness": 8, "mouthfeel": 7
                        }
                    }
                ]
            }
            response = requests.post(
                f"{self.base_url}/api/affective/taste-fit/batch",
                json=payload,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = (
                    data.get("profile_exists") == False and
                    data.get("scores") == []
                )
            self.log_test("Taste-Fit Batch (No Profile)", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Taste-Fit Batch (No Profile)", False, str(e))
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print(f"🚀 Starting Unchained Coffee Taste Fit API Tests")
        print(f"📍 Backend URL: {self.base_url}")
        print(f"🔄 Session ID: {self.session_id}")
        print("=" * 60)

        # Basic tests
        if not self.test_health():
            print("❌ Health check failed - stopping tests")
            return False

        # Authentication tests
        self.test_admin_login()
        self.test_viewer_login()
        self.test_invalid_login()
        self.test_admin_unauthorized()
        self.test_viewer_admin_access()

        # Profile tests
        self.test_create_profile()
        self.test_get_profile()
        self.test_profile_validation()

        # Response tests
        self.test_create_preference_response()
        self.test_create_tasted_response()
        self.test_tasted_validation()

        # Event tests
        self.test_create_event()

        # Admin dashboard tests (require admin login to be successful)
        if self.admin_token:
            self.test_admin_products()
            self.test_admin_product_summary()
            self.test_admin_segments()
            self.test_admin_funnel()

        # NEW: Taste-Fit Score tests
        self.test_taste_fit_score_with_profile()
        self.test_taste_fit_score_no_profile()
        self.test_taste_fit_batch_with_profile()
        self.test_taste_fit_batch_no_profile()

        # Results
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.failures:
            print("\n❌ Failed Tests:")
            for failure in self.failures:
                print(f"   - {failure}")
        
        return self.tests_passed == self.tests_run


def main():
    """Main test function"""
    tester = TasteFitAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())