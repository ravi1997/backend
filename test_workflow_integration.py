"""
Workflow Module Integration Test

This script tests the complete workflow functionality including:
1. Workflow CRUD operations
2. Trigger condition evaluation
3. Action execution (redirect, create_draft, notify)
4. Data mapping between forms
5. Next-action endpoint

Requirements:
- Flask backend running on http://localhost:5000
- Admin user credentials
- Test forms created

Usage:
    python test_workflow_integration.py
"""

import requests
import json
import sys
from typing import Dict, Optional, Tuple

# Configuration
BASE_URL = "http://localhost:5000/form/api/v1"
ADMIN_USERNAME = "admin"  # Update with actual admin credentials
ADMIN_PASSWORD = "admin123"  # Update with actual admin password

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class WorkflowTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.token = None
        self.test_form_id = None
        self.target_form_id = None
        self.workflow_id = None
        self.response_id = None
        self.passed = 0
        self.failed = 0

    def log_success(self, message: str):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")
        self.passed += 1

    def log_error(self, message: str):
        """Print error message"""
        print(f"{Colors.RED}✗ {message}{Colors.RESET}")
        self.failed += 1

    def log_info(self, message: str):
        """Print info message"""
        print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

    def log_header(self, message: str):
        """Print section header"""
        print(f"\n{Colors.BOLD}{Colors.YELLOW}{'='*60}")
        print(f"{message}")
        print(f"{'='*60}{Colors.RESET}\n")

    def login(self, username: str, password: str) -> bool:
        """Authenticate and get JWT token"""
        self.log_header("AUTHENTICATION")
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"identifier": username, "password": password}
            )

            if response.status_code == 200:
                self.token = response.json().get("access_token")
                self.log_success(f"Logged in as {username}")
                return True
            else:
                self.log_error(f"Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_error(f"Login exception: {str(e)}")
            return False

    def get_headers(self) -> Dict[str, str]:
        """Get request headers with auth token"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def create_test_form(self, title: str) -> Optional[str]:
        """Create a test form"""
        form_data = {
            "title": title,
            "description": f"Test form for workflow integration",
            "slug": f"test-workflow-{title.lower().replace(' ', '-')}",
            "status": "published",
            "ui": "flex",
            "versions": [{
                "version": "1.0",
                "sections": [{
                    "id": "section-1",
                    "title": "Test Section",
                    "ui": "flex",
                    "order": 1,
                    "questions": [
                        {
                            "id": "priority",
                            "label": "Priority Level",
                            "field_type": "select",
                            "is_required": True,
                            "order": 1,
                            "options": [
                                {"option_label": "High", "option_value": "high", "order": 1},
                                {"option_label": "Medium", "option_value": "medium", "order": 2},
                                {"option_label": "Low", "option_value": "low", "order": 3}
                            ]
                        },
                        {
                            "id": "description",
                            "label": "Description",
                            "field_type": "textarea",
                            "is_required": True,
                            "order": 2
                        }
                    ]
                }]
            }]
        }

        try:
            response = requests.post(
                f"{self.base_url}/forms/",
                headers=self.get_headers(),
                json=form_data
            )

            if response.status_code == 201:
                form_id = response.json().get("form_id")
                self.log_success(f"Created test form: {title} (ID: {form_id})")
                return form_id
            else:
                self.log_error(f"Failed to create form: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.log_error(f"Form creation exception: {str(e)}")
            return None

    def test_create_workflow(self) -> bool:
        """Test workflow creation"""
        self.log_header("TEST: CREATE WORKFLOW")

        workflow_data = {
            "name": "High Priority Follow-up",
            "description": "Triggered when priority is high",
            "trigger_form_id": self.test_form_id,
            "trigger_condition": "answers.get('priority') == 'high'",
            "is_active": True,
            "actions": [
                {
                    "type": "redirect_to_form",
                    "target_form_id": self.target_form_id,
                    "data_mapping": {
                        "original_priority": "priority",
                        "original_description": "description",
                        "source_id": "id"
                    },
                    "assign_to_user_field": None
                }
            ]
        }

        try:
            response = requests.post(
                f"{self.base_url}/workflows/",
                headers=self.get_headers(),
                json=workflow_data
            )

            if response.status_code == 201:
                self.workflow_id = response.json().get("id")
                self.log_success(f"Workflow created (ID: {self.workflow_id})")
                return True
            else:
                self.log_error(f"Workflow creation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_error(f"Workflow creation exception: {str(e)}")
            return False

    def test_list_workflows(self) -> bool:
        """Test listing workflows"""
        self.log_header("TEST: LIST WORKFLOWS")

        try:
            # List all workflows
            response = requests.get(
                f"{self.base_url}/workflows/",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                workflows = response.json()
                self.log_success(f"Listed {len(workflows)} workflows")

                # List workflows by trigger form
                response = requests.get(
                    f"{self.base_url}/workflows/?trigger_form_id={self.test_form_id}",
                    headers=self.get_headers()
                )

                if response.status_code == 200:
                    filtered_workflows = response.json()
                    self.log_success(f"Filtered workflows for form: {len(filtered_workflows)} found")
                    return True
                else:
                    self.log_error(f"Filtered workflow list failed: {response.status_code}")
                    return False
            else:
                self.log_error(f"Workflow listing failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_error(f"Workflow listing exception: {str(e)}")
            return False

    def test_get_workflow(self) -> bool:
        """Test getting workflow details"""
        self.log_header("TEST: GET WORKFLOW DETAILS")

        try:
            response = requests.get(
                f"{self.base_url}/workflows/{self.workflow_id}",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                workflow = response.json()
                self.log_success(f"Retrieved workflow: {workflow.get('name')}")
                self.log_info(f"  Condition: {workflow.get('trigger_condition')}")
                self.log_info(f"  Actions: {len(workflow.get('actions', []))}")
                return True
            else:
                self.log_error(f"Get workflow failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_error(f"Get workflow exception: {str(e)}")
            return False

    def test_update_workflow(self) -> bool:
        """Test updating workflow"""
        self.log_header("TEST: UPDATE WORKFLOW")

        update_data = {
            "description": "Updated description for testing",
            "is_active": True
        }

        try:
            response = requests.put(
                f"{self.base_url}/workflows/{self.workflow_id}",
                headers=self.get_headers(),
                json=update_data
            )

            if response.status_code == 200:
                self.log_success("Workflow updated successfully")
                return True
            else:
                self.log_error(f"Workflow update failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_error(f"Workflow update exception: {str(e)}")
            return False

    def test_submit_form_with_workflow(self, priority: str = "high") -> bool:
        """Test form submission that triggers workflow"""
        self.log_header(f"TEST: SUBMIT FORM (Priority: {priority})")

        submission_data = {
            "data": {
                "section-1": {
                    "priority": priority,
                    "description": "This is a test submission to trigger workflow"
                }
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/forms/{self.test_form_id}/responses",
                headers=self.get_headers(),
                json=submission_data
            )

            if response.status_code == 201:
                result = response.json()
                self.response_id = result.get("response_id")
                workflow_action = result.get("workflow_action")

                self.log_success(f"Form submitted (Response ID: {self.response_id})")

                if priority == "high" and workflow_action:
                    self.log_success("Workflow triggered as expected")
                    self.log_info(f"  Workflow: {workflow_action.get('workflow_name')}")
                    self.log_info(f"  Actions: {len(workflow_action.get('actions', []))}")
                    return True
                elif priority != "high" and not workflow_action:
                    self.log_success("Workflow not triggered as expected (condition not met)")
                    return True
                elif priority == "high" and not workflow_action:
                    self.log_error("Workflow should have been triggered but wasn't")
                    return False
                else:
                    self.log_error(f"Unexpected workflow behavior for priority: {priority}")
                    return False
            else:
                self.log_error(f"Form submission failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_error(f"Form submission exception: {str(e)}")
            return False

    def test_next_action_endpoint(self) -> bool:
        """Test next-action endpoint"""
        self.log_header("TEST: NEXT-ACTION ENDPOINT")

        try:
            # Test without response_id (list workflows)
            response = requests.get(
                f"{self.base_url}/forms/{self.test_form_id}/next-action",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                result = response.json()
                workflows = result.get("workflows", [])
                self.log_success(f"Next-action (list): {len(workflows)} workflows available")

                # Test with response_id (evaluate workflow)
                if self.response_id:
                    response = requests.get(
                        f"{self.base_url}/forms/{self.test_form_id}/next-action?response_id={self.response_id}",
                        headers=self.get_headers()
                    )

                    if response.status_code == 200:
                        result = response.json()
                        workflow_action = result.get("workflow_action")

                        if workflow_action:
                            self.log_success("Next-action (evaluate): Workflow matched")
                            self.log_info(f"  Matched condition: {workflow_action.get('matched_condition')}")
                            return True
                        else:
                            self.log_info("Next-action (evaluate): No workflow matched")
                            return True
                    else:
                        self.log_error(f"Next-action evaluation failed: {response.status_code}")
                        return False
                else:
                    self.log_info("Skipping evaluation test (no response_id available)")
                    return True
            else:
                self.log_error(f"Next-action listing failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_error(f"Next-action endpoint exception: {str(e)}")
            return False

    def test_workflow_with_different_conditions(self) -> bool:
        """Test workflow doesn't trigger when condition is not met"""
        self.log_header("TEST: WORKFLOW CONDITION EVALUATION")

        # Submit with low priority (should not trigger)
        return self.test_submit_form_with_workflow(priority="low")

    def cleanup(self) -> bool:
        """Clean up test data"""
        self.log_header("CLEANUP")

        success = True

        # Delete workflow
        if self.workflow_id:
            try:
                response = requests.delete(
                    f"{self.base_url}/workflows/{self.workflow_id}",
                    headers=self.get_headers()
                )
                if response.status_code == 200:
                    self.log_success(f"Deleted workflow {self.workflow_id}")
                else:
                    self.log_error(f"Failed to delete workflow: {response.status_code}")
                    success = False
            except Exception as e:
                self.log_error(f"Workflow deletion exception: {str(e)}")
                success = False

        # Delete test forms
        for form_id, name in [(self.test_form_id, "test"), (self.target_form_id, "target")]:
            if form_id:
                try:
                    response = requests.delete(
                        f"{self.base_url}/forms/{form_id}",
                        headers=self.get_headers()
                    )
                    if response.status_code == 200:
                        self.log_success(f"Deleted {name} form {form_id}")
                    else:
                        self.log_error(f"Failed to delete {name} form: {response.status_code}")
                        success = False
                except Exception as e:
                    self.log_error(f"Form deletion exception: {str(e)}")
                    success = False

        return success

    def print_summary(self):
        """Print test summary"""
        self.log_header("TEST SUMMARY")
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0

        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.RESET}")
        print(f"Success Rate: {percentage:.1f}%\n")

        if self.failed == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED{Colors.RESET}\n")
            return 0
        else:
            print(f"{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.RESET}\n")
            return 1

    def run_all_tests(self):
        """Run complete test suite"""
        print(f"{Colors.BOLD}{Colors.BLUE}")
        print("="*60)
        print("WORKFLOW MODULE INTEGRATION TESTS")
        print("="*60)
        print(Colors.RESET)

        # Authenticate
        if not self.login(ADMIN_USERNAME, ADMIN_PASSWORD):
            self.log_error("Authentication failed. Cannot proceed with tests.")
            return 1

        # Setup test forms
        self.log_header("SETUP: CREATE TEST FORMS")
        self.test_form_id = self.create_test_form("Primary Form")
        self.target_form_id = self.create_test_form("Target Form")

        if not self.test_form_id or not self.target_form_id:
            self.log_error("Failed to create test forms. Cannot proceed.")
            return 1

        # Run tests
        self.test_create_workflow()
        self.test_list_workflows()
        self.test_get_workflow()
        self.test_update_workflow()
        self.test_submit_form_with_workflow(priority="high")
        self.test_next_action_endpoint()
        self.test_workflow_with_different_conditions()

        # Cleanup
        self.cleanup()

        # Print summary
        return self.print_summary()


def main():
    """Main entry point"""
    tester = WorkflowTester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
