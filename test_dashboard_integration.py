#!/usr/bin/env python3
"""
Dashboard Module Integration Test
Tests all dashboard endpoints including widget data fetching
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/form/api/v1"
AUTH_URL = f"{BASE_URL}/auth"
DASHBOARD_URL = f"{BASE_URL}/dashboards"
FORM_URL = f"{BASE_URL}/forms"

class DashboardTester:
    def __init__(self):
        self.admin_token = None
        self.deo_token = None
        self.test_form_id = None
        self.test_dashboard_id = None
        self.results = []

    def log(self, test_name, status, message=""):
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        status_symbol = "✅" if status == "PASS" else "❌"
        print(f"{status_symbol} {test_name}: {message}")

    def register_and_login_admin(self):
        """Register and login admin user"""
        try:
            # Register
            register_payload = {
                "username": "test_admin_dashboard",
                "email": "test_admin_dashboard@test.com",
                "password": "Admin123!",
                "employee_id": "ADMIN_DASH_001",
                "user_type": "employee",
                "mobile": "9999999901",
                "roles": ["admin", "superadmin"]
            }

            resp = requests.post(f"{AUTH_URL}/register", json=register_payload)

            # Login
            login_payload = {
                "email": "test_admin_dashboard@test.com",
                "password": "Admin123!"
            }

            resp = requests.post(f"{AUTH_URL}/login", json=login_payload)

            if resp.status_code == 200:
                self.admin_token = resp.json().get("access_token")
                self.log("Admin Login", "PASS", "Admin authenticated successfully")
                return True
            else:
                self.log("Admin Login", "FAIL", f"Status: {resp.status_code}, Response: {resp.text}")
                return False

        except Exception as e:
            self.log("Admin Login", "FAIL", str(e))
            return False

    def register_and_login_deo(self):
        """Register and login DEO user"""
        try:
            # Register
            register_payload = {
                "username": "test_deo_dashboard",
                "email": "test_deo_dashboard@test.com",
                "password": "Deo123!",
                "employee_id": "DEO_DASH_001",
                "user_type": "employee",
                "mobile": "9999999902",
                "roles": ["deo"]
            }

            resp = requests.post(f"{AUTH_URL}/register", json=register_payload)

            # Login
            login_payload = {
                "email": "test_deo_dashboard@test.com",
                "password": "Deo123!"
            }

            resp = requests.post(f"{AUTH_URL}/login", json=login_payload)

            if resp.status_code == 200:
                self.deo_token = resp.json().get("access_token")
                self.log("DEO Login", "PASS", "DEO user authenticated successfully")
                return True
            else:
                self.log("DEO Login", "FAIL", f"Status: {resp.status_code}, Response: {resp.text}")
                return False

        except Exception as e:
            self.log("DEO Login", "FAIL", str(e))
            return False

    def create_test_form(self):
        """Create a test form for dashboard widgets"""
        try:
            form_payload = {
                "title": "Test Dashboard Form",
                "slug": "test-dashboard-form",
                "description": "Form for testing dashboard widgets",
                "ui": "flex",
                "versions": [{
                    "version": "1.0",
                    "sections": [{
                        "title": "Test Section",
                        "ui": "flex",
                        "questions": [{
                            "label": "Test Question",
                            "field_type": "input",
                            "is_required": True
                        }]
                    }]
                }]
            }

            headers = {"Authorization": f"Bearer {self.admin_token}"}
            resp = requests.post(FORM_URL, json=form_payload, headers=headers)

            if resp.status_code == 201:
                self.test_form_id = resp.json().get("form_id")
                self.log("Create Test Form", "PASS", f"Form ID: {self.test_form_id}")
                return True
            else:
                self.log("Create Test Form", "FAIL", f"Status: {resp.status_code}, Response: {resp.text}")
                return False

        except Exception as e:
            self.log("Create Test Form", "FAIL", str(e))
            return False

    def publish_test_form(self):
        """Publish the test form"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            resp = requests.patch(f"{FORM_URL}/{self.test_form_id}/publish", headers=headers)

            if resp.status_code == 200:
                self.log("Publish Test Form", "PASS", "Form published successfully")
                return True
            else:
                self.log("Publish Test Form", "FAIL", f"Status: {resp.status_code}, Response: {resp.text}")
                return False

        except Exception as e:
            self.log("Publish Test Form", "FAIL", str(e))
            return False

    def submit_test_responses(self, count=5):
        """Submit multiple test responses"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}

            for i in range(count):
                response_payload = {
                    "data": {
                        "test_question_id": f"Test Response {i+1}"
                    }
                }

                resp = requests.post(
                    f"{FORM_URL}/{self.test_form_id}/responses",
                    json=response_payload,
                    headers=headers
                )

                if resp.status_code not in [200, 201]:
                    self.log("Submit Test Responses", "FAIL", f"Failed on response {i+1}")
                    return False

            self.log("Submit Test Responses", "PASS", f"Submitted {count} responses")
            return True

        except Exception as e:
            self.log("Submit Test Responses", "FAIL", str(e))
            return False

    def test_create_dashboard(self):
        """Test: POST /api/v1/dashboards/"""
        try:
            dashboard_payload = {
                "title": "Test Dashboard",
                "slug": "test-dashboard-001",
                "description": "Dashboard for integration testing",
                "roles": ["admin", "deo"],
                "layout": "grid",
                "widgets": [
                    {
                        "title": "Response Counter",
                        "type": "counter",
                        "form_id": self.test_form_id,
                        "size": "medium",
                        "refresh_interval": 300
                    },
                    {
                        "title": "Recent Submissions",
                        "type": "list_view",
                        "form_id": self.test_form_id,
                        "size": "large",
                        "display_columns": ["id", "submitted_at"]
                    },
                    {
                        "title": "Quick Actions",
                        "type": "shortcut",
                        "target_link": "/forms/new",
                        "size": "small"
                    }
                ]
            }

            headers = {"Authorization": f"Bearer {self.admin_token}"}
            resp = requests.post(DASHBOARD_URL, json=dashboard_payload, headers=headers)

            if resp.status_code == 201:
                data = resp.json()
                self.test_dashboard_id = data.get("id")
                self.log("Create Dashboard", "PASS", f"Dashboard ID: {self.test_dashboard_id}")
                return True
            else:
                self.log("Create Dashboard", "FAIL", f"Status: {resp.status_code}, Response: {resp.text}")
                return False

        except Exception as e:
            self.log("Create Dashboard", "FAIL", str(e))
            return False

    def test_list_dashboards(self):
        """Test: GET /api/v1/dashboards/"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            resp = requests.get(DASHBOARD_URL, headers=headers)

            if resp.status_code == 200:
                dashboards = resp.json()
                found = any(d.get("slug") == "test-dashboard-001" for d in dashboards)

                if found:
                    self.log("List Dashboards", "PASS", f"Found {len(dashboards)} dashboards")
                    return True
                else:
                    self.log("List Dashboards", "FAIL", "Created dashboard not found in list")
                    return False
            else:
                self.log("List Dashboards", "FAIL", f"Status: {resp.status_code}, Response: {resp.text}")
                return False

        except Exception as e:
            self.log("List Dashboards", "FAIL", str(e))
            return False

    def test_get_dashboard_data(self):
        """Test: GET /api/v1/dashboards/{slug}"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            resp = requests.get(f"{DASHBOARD_URL}/test-dashboard-001", headers=headers)

            if resp.status_code == 200:
                data = resp.json()

                # Validate structure
                if "title" not in data or "widgets" not in data:
                    self.log("Get Dashboard Data", "FAIL", "Missing required fields in response")
                    return False

                # Validate widgets
                widgets = data.get("widgets", [])
                if len(widgets) != 3:
                    self.log("Get Dashboard Data", "FAIL", f"Expected 3 widgets, got {len(widgets)}")
                    return False

                # Check counter widget data
                counter_widget = next((w for w in widgets if w["type"] == "counter"), None)
                if counter_widget:
                    if "data" not in counter_widget:
                        self.log("Get Dashboard Data", "FAIL", "Counter widget missing data field")
                        return False

                    count = counter_widget.get("data")
                    if count != 5:
                        self.log("Get Dashboard Data", "WARN", f"Expected 5 responses, got {count}")
                    else:
                        self.log("Counter Widget Data", "PASS", f"Count: {count}")

                # Check list_view widget data
                list_widget = next((w for w in widgets if w["type"] == "list_view"), None)
                if list_widget:
                    if "data" not in list_widget:
                        self.log("Get Dashboard Data", "FAIL", "List widget missing data field")
                        return False

                    list_data = list_widget.get("data", [])
                    self.log("List Widget Data", "PASS", f"Retrieved {len(list_data)} records")

                self.log("Get Dashboard Data", "PASS", f"Dashboard: {data['title']}, Widgets: {len(widgets)}")
                return True
            else:
                self.log("Get Dashboard Data", "FAIL", f"Status: {resp.status_code}, Response: {resp.text}")
                return False

        except Exception as e:
            self.log("Get Dashboard Data", "FAIL", str(e))
            return False

    def test_update_dashboard(self):
        """Test: PUT /api/v1/dashboards/{id}"""
        try:
            update_payload = {
                "title": "Updated Test Dashboard",
                "description": "Updated description for testing"
            }

            headers = {"Authorization": f"Bearer {self.admin_token}"}
            resp = requests.put(
                f"{DASHBOARD_URL}/{self.test_dashboard_id}",
                json=update_payload,
                headers=headers
            )

            if resp.status_code == 200:
                # Verify update
                verify_resp = requests.get(f"{DASHBOARD_URL}/test-dashboard-001", headers=headers)

                if verify_resp.status_code == 200:
                    data = verify_resp.json()
                    if data.get("title") == "Updated Test Dashboard":
                        self.log("Update Dashboard", "PASS", "Dashboard updated successfully")
                        return True
                    else:
                        self.log("Update Dashboard", "FAIL", "Update not reflected")
                        return False

            else:
                self.log("Update Dashboard", "FAIL", f"Status: {resp.status_code}, Response: {resp.text}")
                return False

        except Exception as e:
            self.log("Update Dashboard", "FAIL", str(e))
            return False

    def test_role_based_access(self):
        """Test: Role-based access control"""
        try:
            # DEO should be able to access
            headers = {"Authorization": f"Bearer {self.deo_token}"}
            resp = requests.get(f"{DASHBOARD_URL}/test-dashboard-001", headers=headers)

            if resp.status_code == 200:
                self.log("DEO Access Control", "PASS", "DEO can access dashboard")
            else:
                self.log("DEO Access Control", "FAIL", f"DEO cannot access: {resp.status_code}")
                return False

            return True

        except Exception as e:
            self.log("Role-based Access", "FAIL", str(e))
            return False

    def test_duplicate_slug_validation(self):
        """Test: Duplicate slug validation"""
        try:
            dashboard_payload = {
                "title": "Duplicate Slug Test",
                "slug": "test-dashboard-001",  # Same slug as existing
                "roles": ["admin"]
            }

            headers = {"Authorization": f"Bearer {self.admin_token}"}
            resp = requests.post(DASHBOARD_URL, json=dashboard_payload, headers=headers)

            if resp.status_code == 409:
                self.log("Duplicate Slug Validation", "PASS", "Duplicate slug rejected")
                return True
            else:
                self.log("Duplicate Slug Validation", "FAIL", f"Expected 409, got {resp.status_code}")
                return False

        except Exception as e:
            self.log("Duplicate Slug Validation", "FAIL", str(e))
            return False

    def run_all_tests(self):
        """Run all dashboard integration tests"""
        print("\n" + "="*60)
        print("Dashboard Module Integration Test Suite")
        print("="*60 + "\n")

        # Setup
        if not self.register_and_login_admin():
            print("\n❌ Admin authentication failed. Stopping tests.")
            return False

        if not self.register_and_login_deo():
            print("\n⚠️  DEO authentication failed. Some tests will be skipped.")

        # Create test data
        if not self.create_test_form():
            print("\n❌ Test form creation failed. Stopping tests.")
            return False

        if not self.publish_test_form():
            print("\n❌ Test form publishing failed. Stopping tests.")
            return False

        if not self.submit_test_responses(5):
            print("\n⚠️  Response submission failed. Widget tests may fail.")

        print("\n--- Dashboard CRUD Tests ---\n")

        # Dashboard tests
        self.test_create_dashboard()
        self.test_list_dashboards()
        self.test_get_dashboard_data()
        self.test_update_dashboard()

        print("\n--- Dashboard Access Control Tests ---\n")

        self.test_role_based_access()

        print("\n--- Dashboard Validation Tests ---\n")

        self.test_duplicate_slug_validation()

        # Summary
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60 + "\n")

        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        total = len(self.results)

        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%\n")

        # Detailed results
        if failed > 0:
            print("Failed Tests:")
            for r in self.results:
                if r["status"] == "FAIL":
                    print(f"  ❌ {r['test']}: {r['message']}")

        return failed == 0

if __name__ == "__main__":
    tester = DashboardTester()
    success = tester.run_all_tests()

    exit(0 if success else 1)
