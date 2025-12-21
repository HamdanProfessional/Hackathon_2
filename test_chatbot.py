#!/usr/bin/env python3
"""
Comprehensive Chatbot Testing Script
Tests the deployed Todo AI Assistant with both mock and real AI functionality
"""

import requests
import json
import time
import uuid
from typing import Dict, Any, List

class ChatbotTester:
    def __init__(self):
        self.frontend_url = "https://frontend-hamdanprofessionals-projects.vercel.app"
        self.backend_url = "https://backend-hamdanprofessionals-projects.vercel.app"
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []

    def log_result(self, test_name: str, status: str, details: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        status_icon = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WARN]"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")

    def test_backend_connectivity(self):
        """Test if backend is accessible"""
        try:
            response = self.session.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Backend Health Check", "PASS", f"Status: {data.get('status')}")
                return True
            else:
                self.log_result("Backend Health Check", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Backend Health Check", "FAIL", str(e))
            return False

    def test_frontend_connectivity(self):
        """Test if frontend is accessible"""
        try:
            response = self.session.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                self.log_result("Frontend Connectivity", "PASS", f"HTTP {response.status_code}")
                # Check if it contains chat interface
                if "chat" in response.text.lower() or "conversation" in response.text.lower():
                    self.log_result("Chat Interface Present", "PASS", "Chat UI detected in frontend")
                else:
                    self.log_result("Chat Interface Present", "FAIL", "No chat UI detected")
                return True
            else:
                self.log_result("Frontend Connectivity", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Frontend Connectivity", "FAIL", str(e))
            return False

    def register_test_user(self):
        """Register a test user for testing"""
        test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        payload = {
            "email": test_email,
            "password": "TestPassword123!",
            "name": "Test User"
        }

        try:
            response = self.session.post(f"{self.backend_url}/api/auth/register",
                                       json=payload, timeout=10)
            if response.status_code in [200, 201]:
                data = response.json()
                self.user_id = data.get("id")
                self.log_result("User Registration", "PASS", f"User ID: {self.user_id}")
                return test_email
            else:
                self.log_result("User Registration", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_result("User Registration", "FAIL", str(e))
            return None

    def login_user(self, email: str):
        """Login and get auth token"""
        payload = {
            "email": email,
            "password": "TestPassword123!"
        }

        try:
            response = self.session.post(f"{self.backend_url}/api/auth/login",
                                       json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_result("User Login", "PASS", "Authentication successful")
                return True
            else:
                self.log_result("User Login", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("User Login", "FAIL", str(e))
            return False

    def test_task_operations(self):
        """Test all task CRUD operations"""
        if not self.auth_token:
            self.log_result("Task Operations", "SKIP", "No auth token")
            return

        # Test creating a task
        task_payload = {
            "title": "Test Task from Chatbot",
            "description": "This is a test task created during automated testing",
            "priority_id": 1  # High priority
        }

        try:
            # Create task
            response = self.session.post(f"{self.backend_url}/api/tasks/",
                                       json=task_payload, timeout=10)
            if response.status_code in [200, 201]:
                task_data = response.json()
                task_id = task_data.get("id")
                self.log_result("Task Creation", "PASS", f"Task ID: {task_id}")

                # List tasks
                response = self.session.get(f"{self.backend_url}/api/tasks/", timeout=10)
                if response.status_code == 200:
                    tasks = response.json()
                    self.log_result("Task Listing", "PASS", f"Found {len(tasks)} tasks")
                else:
                    self.log_result("Task Listing", "FAIL", f"HTTP {response.status_code}")

                # Update task
                update_payload = {"completed": True}
                response = self.session.patch(f"{self.backend_url}/api/tasks/{task_id}/complete",
                                            json=update_payload, timeout=10)
                if response.status_code == 200:
                    self.log_result("Task Update", "PASS", "Task marked as completed")
                else:
                    self.log_result("Task Update", "FAIL", f"HTTP {response.status_code}")

                # Delete task
                response = self.session.delete(f"{self.backend_url}/api/tasks/{task_id}", timeout=10)
                if response.status_code == 204:
                    self.log_result("Task Deletion", "PASS", "Task deleted successfully")
                else:
                    self.log_result("Task Deletion", "FAIL", f"HTTP {response.status_code}")

            else:
                self.log_result("Task Creation", "FAIL", f"HTTP {response.status_code}: {response.text}")

        except Exception as e:
            self.log_result("Task Operations", "FAIL", str(e))

    def test_chat_endpoint(self):
        """Test the chat endpoint with various messages"""
        if not self.auth_token:
            self.log_result("Chat Endpoint", "SKIP", "No auth token")
            return

        test_messages = [
            "Hello, can you help me manage my tasks?",
            "Create a new task called 'Review project documentation'",
            "Show me all my tasks",
            "What tasks do I have pending?",
            "Mark the first task as completed",
            "Help me organize my work"
        ]

        for i, message in enumerate(test_messages):
            try:
                payload = {"message": message}
                response = self.session.post(f"{self.backend_url}/api/chat/",
                                           json=payload, timeout=30)

                if response.status_code == 200:
                    chat_response = response.json()
                    if "response" in chat_response or "message" in chat_response:
                        response_text = chat_response.get("response", chat_response.get("message", ""))
                        self.log_result(f"Chat Message {i+1}", "PASS",
                                      f"Response length: {len(response_text)} chars")

                        # Check if response is intelligent (not just a generic message)
                        if len(response_text) > 20 and "task" in response_text.lower():
                            self.log_result(f"Chat Intelligence {i+1}", "PASS",
                                          "Response seems contextual")
                        else:
                            self.log_result(f"Chat Intelligence {i+1}", "WARN",
                                          "Response might be generic")
                    else:
                        self.log_result(f"Chat Message {i+1}", "FAIL",
                                      "No response field in API response")
                else:
                    self.log_result(f"Chat Message {i+1}", "FAIL",
                                  f"HTTP {response.status_code}: {response.text}")

                # Small delay between messages
                time.sleep(1)

            except Exception as e:
                self.log_result(f"Chat Message {i+1}", "FAIL", str(e))

    def test_ai_configuration(self):
        """Test if AI is properly configured"""
        if not self.auth_token:
            self.log_result("AI Configuration", "SKIP", "No auth token")
            return

        try:
            # Try to infer AI type from chat responses
            payload = {"message": "What AI model are you using?"}
            response = self.session.post(f"{self.backend_url}/api/chat/",
                                       json=payload, timeout=15)

            if response.status_code == 200:
                chat_response = response.json()
                response_text = chat_response.get("response", chat_response.get("message", ""))

                self.log_result("AI Chat Response", "PASS", f"Response received: {len(response_text)} chars")

                if "gemini" in response_text.lower() or "google" in response_text.lower():
                    self.log_result("AI Detection", "PASS", "Gemini AI detected from response")
                elif "mock" in response_text.lower() or "demo" in response_text.lower() or "test" in response_text.lower():
                    self.log_result("AI Detection", "PASS", "Mock AI detected from response")
                else:
                    self.log_result("AI Detection", "WARN", "Could not determine AI type from response")
            else:
                self.log_result("AI Configuration", "FAIL", f"Could not reach chat endpoint: HTTP {response.status_code}")

        except Exception as e:
            self.log_result("AI Configuration", "FAIL", str(e))

    def test_cors_configuration(self):
        """Test CORS configuration between frontend and backend"""
        try:
            # Make a request from frontend origin
            headers = {"Origin": self.frontend_url}
            response = self.session.options(f"{self.backend_url}/health",
                                          headers=headers, timeout=10)

            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
            }

            if cors_headers["Access-Control-Allow-Origin"]:
                self.log_result("CORS Configuration", "PASS",
                              f"Origin allowed: {cors_headers['Access-Control-Allow-Origin']}")
            else:
                self.log_result("CORS Configuration", "WARN", "No CORS headers detected")

        except Exception as e:
            self.log_result("CORS Configuration", "FAIL", str(e))

    def run_all_tests(self):
        """Run all tests and generate report"""
        print("Starting Comprehensive Chatbot Testing")
        print("=" * 50)

        # Connectivity tests
        self.test_backend_connectivity()
        self.test_frontend_connectivity()
        self.test_cors_configuration()

        # Authentication tests
        print("\nAuthentication Tests")
        print("-" * 30)
        test_email = self.register_test_user()
        if test_email:
            self.login_user(test_email)

        # Task management tests
        print("\nTask Management Tests")
        print("-" * 30)
        self.test_task_operations()

        # Chat functionality tests
        print("\nChat Functionality Tests")
        print("-" * 30)
        self.test_chat_endpoint()
        self.test_ai_configuration()

        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        warned_tests = len([r for r in self.test_results if r["status"] == "WARN"])

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Warnings: {warned_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")

        if failed_tests > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['details']}")

        if warned_tests > 0:
            print("\nWarnings:")
            for result in self.test_results:
                if result["status"] == "WARN":
                    print(f"  - {result['test']}: {result['details']}")

        # Save detailed report
        with open("chatbot_test_report.json", "w") as f:
            json.dump({
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "warned": warned_tests,
                    "success_rate": passed_tests/total_tests*100
                },
                "results": self.test_results
            }, f, indent=2)

        print(f"\nDetailed report saved to: chatbot_test_report.json")

if __name__ == "__main__":
    tester = ChatbotTester()
    tester.run_all_tests()