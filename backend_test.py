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
    def __init__(self, base_url="https://flavor-match-11.preview.emergentagent.com"):
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

    def test_collection_batch_all_products(self):
        """Test batch taste-fit for all 6 collection products"""
        try:
            # Ensure profile exists first
            self.test_create_profile()
            
            # All 6 products from mockProducts.js
            payload = {
                "session_id": self.session_id,
                "products": [
                    {
                        "product_id": "papayo-natural-8001",
                        "sensory": {"aroma": 7, "flavor": 8, "aftertaste": 7, "acidity": 6, "sweetness": 8, "mouthfeel": 7}
                    },
                    {
                        "product_id": "geisha-honey-8002", 
                        "sensory": {"aroma": 8, "flavor": 9, "aftertaste": 8, "acidity": 7, "sweetness": 8, "mouthfeel": 6}
                    },
                    {
                        "product_id": "red-bourbon-8003",
                        "sensory": {"aroma": 7, "flavor": 7, "aftertaste": 7, "acidity": 5, "sweetness": 7, "mouthfeel": 8}
                    },
                    {
                        "product_id": "caturra-washed-8004",
                        "sensory": {"aroma": 8, "flavor": 7, "aftertaste": 6, "acidity": 8, "sweetness": 6, "mouthfeel": 5}
                    },
                    {
                        "product_id": "tabi-anaerobic-8005",
                        "sensory": {"aroma": 9, "flavor": 9, "aftertaste": 8, "acidity": 5, "sweetness": 7, "mouthfeel": 8}
                    },
                    {
                        "product_id": "castillo-dark-8006",
                        "sensory": {"aroma": 6, "flavor": 6, "aftertaste": 8, "acidity": 3, "sweetness": 5, "mouthfeel": 9}
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
                    len(data["scores"]) == 6 and
                    all("product_id" in score and "score" in score and "label" in score and "breakdown" in score
                        for score in data["scores"])
                )
                if success:
                    # Verify scores are properly ranked
                    scores = [s["score"] for s in data["scores"]]
                    print(f"   Collection scores: {scores}")
            self.log_test("Collection Batch All 6 Products", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Collection Batch All 6 Products", False, str(e))
            return False

    # ============================================================
    # NEW: QUIZ ENDPOINTS TESTS
    # ============================================================

    def test_submit_quiz(self):
        """Test submitting quiz profile"""
        try:
            payload = {
                "session_id": self.session_id,
                "acidity_pref": 3.5,
                "bitterness_pref": 2.0,
                "body_pref": "balanced",
                "roast_pref": "medium",
                "budget_band": "20_30",
                "brew_methods": ["pour_over", "espresso"],
                "drink_style": "black",
                "flavor_love_tags": ["chocolate", "caramel", "nutty"],
                "consent_analytics": True,
                "consent_marketing": False
            }
            response = requests.post(
                f"{self.base_url}/api/quiz/submit",
                json=payload,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = data.get("status") == "ok"
            self.log_test("Submit Quiz Profile", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Submit Quiz Profile", False, str(e))
            return False

    def test_get_quiz_profile(self):
        """Test getting quiz profile"""
        try:
            response = requests.get(
                f"{self.base_url}/api/quiz/profile?session_id={self.session_id}",
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = "profile" in data and data["profile"] is not None
                if success:
                    profile = data["profile"]
                    # Verify key fields are present
                    required_fields = ["acidity_pref", "bitterness_pref", "body_pref", "roast_pref", "budget_band"]
                    success = all(field in profile for field in required_fields)
            self.log_test("Get Quiz Profile", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Get Quiz Profile", False, str(e))
            return False

    def test_quiz_validation(self):
        """Test quiz validation with invalid data"""
        try:
            payload = {
                "session_id": self.session_id,
                "acidity_pref": 6.0,  # Invalid: should be 1-5
                "bitterness_pref": 2.0,
                "body_pref": "invalid_body",  # Invalid body preference
                "roast_pref": "medium",
                "budget_band": "invalid_budget",  # Invalid budget band
                "brew_methods": ["pour_over"],
                "drink_style": "black",
                "flavor_love_tags": ["chocolate"]
            }
            response = requests.post(
                f"{self.base_url}/api/quiz/submit",
                json=payload,
                timeout=10
            )
            success = response.status_code == 422  # Validation error expected
            self.log_test("Quiz Validation (Invalid Data)", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Quiz Validation (Invalid Data)", False, str(e))
            return False

    # ============================================================
    # NEW: RECOMMENDATIONS ENDPOINT TESTS
    # ============================================================

    def test_recommendations_with_quiz(self):
        """Test recommendations endpoint when quiz profile exists"""
        try:
            # Ensure quiz profile exists first
            self.test_submit_quiz()
            
            payload = {
                "session_id": self.session_id,
                "limit": 6
            }
            response = requests.post(
                f"{self.base_url}/api/recommendations",
                json=payload,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = (
                    data.get("mode") == "personalized" and
                    data.get("model_version") == "rules_v1" and
                    data.get("quiz_completed") == True and
                    "recommendations" in data and
                    isinstance(data["recommendations"], list) and
                    len(data["recommendations"]) > 0
                )
                if success:
                    # Verify recommendation structure
                    rec = data["recommendations"][0]
                    success = (
                        "lot" in rec and
                        "score" in rec and
                        "explanation" in rec and
                        isinstance(rec["explanation"], list) and
                        len(rec["explanation"]) > 0
                    )
                    if success:
                        print(f"   First recommendation score: {rec['score']}")
                        print(f"   First explanation: {rec['explanation'][0]}")
            self.log_test("Recommendations (With Quiz)", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Recommendations (With Quiz)", False, str(e))
            return False

    def test_recommendations_cold_start(self):
        """Test recommendations endpoint when no quiz profile exists (cold start)"""
        try:
            # Use a different session ID without quiz profile
            new_session_id = str(uuid.uuid4())
            payload = {
                "session_id": new_session_id,
                "limit": 6
            }
            response = requests.post(
                f"{self.base_url}/api/recommendations",
                json=payload,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = (
                    data.get("mode") == "editors_picks" and
                    data.get("model_version") == "rules_v1" and
                    data.get("quiz_completed") == False and
                    "recommendations" in data and
                    isinstance(data["recommendations"], list) and
                    len(data["recommendations"]) > 0
                )
                if success:
                    # Verify editor's picks structure
                    rec = data["recommendations"][0]
                    success = (
                        "lot" in rec and
                        rec.get("score") is None and  # No score for editor's picks
                        "explanation" in rec and
                        isinstance(rec["explanation"], list)
                    )
            self.log_test("Recommendations (Cold Start)", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Recommendations (Cold Start)", False, str(e))
            return False

    def test_recommendations_budget_filter(self):
        """Test recommendations with budget filtering"""
        try:
            # Create quiz with under_15 budget to test hard filtering
            budget_session_id = str(uuid.uuid4())
            quiz_payload = {
                "session_id": budget_session_id,
                "acidity_pref": 3.0,
                "bitterness_pref": 2.0,
                "body_pref": "balanced",
                "roast_pref": "medium",
                "budget_band": "under_15",  # Max $15
                "brew_methods": ["pour_over"],
                "drink_style": "black",
                "flavor_love_tags": ["chocolate"],
                "consent_analytics": True,
                "consent_marketing": False
            }
            
            # Submit quiz first
            quiz_response = requests.post(
                f"{self.base_url}/api/quiz/submit",
                json=quiz_payload,
                timeout=10
            )
            
            if quiz_response.status_code != 200:
                self.log_test("Recommendations (Budget Filter)", False, "Failed to create quiz profile")
                return False
            
            # Get recommendations
            rec_payload = {
                "session_id": budget_session_id,
                "limit": 6
            }
            response = requests.post(
                f"{self.base_url}/api/recommendations",
                json=rec_payload,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = (
                    data.get("mode") == "personalized" and
                    "recommendations" in data and
                    isinstance(data["recommendations"], list)
                )
                if success:
                    # Verify all recommendations are within budget ($15 max)
                    for rec in data["recommendations"]:
                        lot_price = rec["lot"].get("price", 0)
                        if lot_price > 15:
                            success = False
                            print(f"   Found over-budget lot: ${lot_price}")
                            break
                    if success:
                        print(f"   All {len(data['recommendations'])} recommendations within $15 budget")
            self.log_test("Recommendations (Budget Filter)", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Recommendations (Budget Filter)", False, str(e))
            return False

    def test_recommendations_scoring_order(self):
        """Test that recommendations are sorted by score descending"""
        try:
            # Ensure quiz profile exists first
            self.test_submit_quiz()
            
            payload = {
                "session_id": self.session_id,
                "limit": 6
            }
            response = requests.post(
                f"{self.base_url}/api/recommendations",
                json=payload,
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                if data.get("mode") == "personalized" and "recommendations" in data:
                    recommendations = data["recommendations"]
                    if len(recommendations) > 1:
                        # Verify scores are in descending order
                        scores = [rec.get("score", 0) for rec in recommendations if rec.get("score") is not None]
                        success = scores == sorted(scores, reverse=True)
                        if success:
                            print(f"   Recommendation scores in order: {scores}")
                        else:
                            print(f"   Scores not properly sorted: {scores}")
                    else:
                        success = True  # Single recommendation is trivially sorted
                else:
                    success = False
            self.log_test("Recommendations (Score Ordering)", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Recommendations (Score Ordering)", False, str(e))
            return False

    # ============================================================
    # NEW: LOT ENDPOINTS TESTS
    # ============================================================

    def test_get_all_lots(self):
        """Test getting all published lots"""
        try:
            response = requests.get(
                f"{self.base_url}/api/lots",
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = (
                    "lots" in data and
                    isinstance(data["lots"], list) and
                    len(data["lots"]) == 6  # Should have 6 seeded lots
                )
                if success:
                    # Verify lot structure
                    lot = data["lots"][0]
                    required_fields = ["lot_id", "title", "producer", "price", "roast_rec", "expected_flavor_tags"]
                    success = all(field in lot for field in required_fields)
                    if success:
                        print(f"   Found {len(data['lots'])} published lots")
            self.log_test("Get All Lots", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Get All Lots", False, str(e))
            return False

    def test_get_specific_lot(self):
        """Test getting specific lot by ID"""
        try:
            # Test with known lot ID from seeded data
            lot_id = "papayo-natural-8001"
            response = requests.get(
                f"{self.base_url}/api/lots/{lot_id}",
                timeout=10
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                success = (
                    "lot" in data and
                    data["lot"]["lot_id"] == lot_id and
                    "title" in data["lot"] and
                    "producer" in data["lot"]
                )
                if success:
                    print(f"   Retrieved lot: {data['lot']['title']}")
            self.log_test("Get Specific Lot", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Get Specific Lot", False, str(e))
            return False

    def test_get_nonexistent_lot(self):
        """Test getting non-existent lot"""
        try:
            response = requests.get(
                f"{self.base_url}/api/lots/nonexistent-lot-id",
                timeout=10
            )
            success = response.status_code == 404  # Not found expected
            self.log_test("Get Non-existent Lot", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Get Non-existent Lot", False, str(e))
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
        
        # NEW: Collection page specific tests
        self.test_collection_batch_all_products()

        # NEW: Quiz endpoints tests
        print("\n🧪 Testing Quiz Endpoints...")
        self.test_submit_quiz()
        self.test_get_quiz_profile()
        self.test_quiz_validation()

        # NEW: Recommendations endpoint tests
        print("\n🎯 Testing Recommendations Engine...")
        self.test_recommendations_with_quiz()
        self.test_recommendations_cold_start()
        self.test_recommendations_budget_filter()
        self.test_recommendations_scoring_order()

        # NEW: Lot endpoints tests
        print("\n☕ Testing Lot Endpoints...")
        self.test_get_all_lots()
        self.test_get_specific_lot()
        self.test_get_nonexistent_lot()

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