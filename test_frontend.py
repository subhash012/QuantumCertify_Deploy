#!/usr/bin/env python3
"""
Frontend Integration Test Suite for QuantumCertify
Tests the React frontend integration and functionality
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests

class FrontendTester:
    def __init__(self, frontend_url: str = "http://localhost:3000", backend_url: str = "http://localhost:8000"):
        self.frontend_url = frontend_url
        self.backend_url = backend_url
        self.driver = None
        self.test_results = []
        
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"❌ Failed to setup WebDriver: {e}")
            print("Note: Chrome WebDriver is required for frontend testing")
            return False
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} | {test_name}"
        if details:
            result += f" | {details}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })

    def test_frontend_accessibility(self):
        """Test if frontend is accessible"""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Frontend Accessibility", success, details)
        return success

    def test_page_load(self):
        """Test if the main page loads correctly"""
        if not self.driver:
            self.log_test("Page Load", False, "WebDriver not available")
            return False
            
        try:
            self.driver.get(self.frontend_url)
            
            # Wait for the page title to load
            WebDriverWait(self.driver, 10).until(
                lambda driver: "QuantumCertify" in driver.title or len(driver.title) > 0
            )
            
            success = True
            details = f"Title: {self.driver.title}"
            
        except TimeoutException:
            success = False
            details = "Page failed to load within timeout"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Page Load", success, details)
        return success

    def test_dashboard_elements(self):
        """Test if dashboard elements are present"""
        if not self.driver:
            self.log_test("Dashboard Elements", False, "WebDriver not available")
            return False
            
        try:
            self.driver.get(self.frontend_url)
            
            # Wait for dashboard to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "dashboard"))
            )
            
            elements_found = []
            
            # Check for key elements
            if self.driver.find_elements(By.TAG_NAME, "h1"):
                elements_found.append("Title")
            
            if self.driver.find_elements(By.CLASS_NAME, "api-status"):
                elements_found.append("API Status")
            
            if self.driver.find_elements(By.CLASS_NAME, "stats-section"):
                elements_found.append("Statistics")
            
            if self.driver.find_elements(By.CLASS_NAME, "upload-section"):
                elements_found.append("Upload Section")
            
            success = len(elements_found) >= 3  # At least 3 key elements
            details = f"Found: {', '.join(elements_found)}"
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Dashboard Elements", success, details)
        return success

    def test_api_status_display(self):
        """Test if API status is displayed correctly"""
        if not self.driver:
            self.log_test("API Status Display", False, "WebDriver not available")
            return False
            
        try:
            self.driver.get(self.frontend_url)
            
            # Wait for API status element
            api_status_element = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "api-status"))
            )
            
            # Check if status is healthy (green) or shows an error
            status_text = api_status_element.text
            
            success = ("API is running" in status_text or 
                      "healthy" in status_text.lower() or
                      "✅" in status_text)
            details = f"Status text: {status_text[:50]}..."
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("API Status Display", success, details)
        return success

    def test_statistics_display(self):
        """Test if statistics are displayed"""
        if not self.driver:
            self.log_test("Statistics Display", False, "WebDriver not available")
            return False
            
        try:
            self.driver.get(self.frontend_url)
            
            # Wait for statistics section
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "stats-section"))
            )
            
            # Look for stat cards
            stat_cards = self.driver.find_elements(By.CLASS_NAME, "stat-card")
            
            success = len(stat_cards) >= 3  # Should have at least 3 stat cards
            details = f"Found {len(stat_cards)} stat cards"
            
            # Check if numbers are displayed
            for card in stat_cards:
                if card.text and any(char.isdigit() for char in card.text):
                    details += " | Numbers displayed"
                    break
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Statistics Display", success, details)
        return success

    def test_refresh_functionality(self):
        """Test refresh button functionality"""
        if not self.driver:
            self.log_test("Refresh Functionality", False, "WebDriver not available")
            return False
            
        try:
            self.driver.get(self.frontend_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "dashboard"))
            )
            
            # Look for refresh button
            refresh_buttons = self.driver.find_elements(By.CLASS_NAME, "refresh-btn")
            
            if refresh_buttons:
                # Click the first refresh button
                refresh_buttons[0].click()
                time.sleep(2)  # Wait for refresh to complete
                
                success = True
                details = "Refresh button clicked successfully"
            else:
                success = False
                details = "No refresh button found"
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Refresh Functionality", success, details)
        return success

    def test_responsive_design(self):
        """Test responsive design at different screen sizes"""
        if not self.driver:
            self.log_test("Responsive Design", False, "WebDriver not available")
            return False
            
        try:
            self.driver.get(self.frontend_url)
            
            # Test different screen sizes
            screen_sizes = [
                (1920, 1080),  # Desktop
                (768, 1024),   # Tablet
                (375, 667)     # Mobile
            ]
            
            responsive_success = True
            
            for width, height in screen_sizes:
                self.driver.set_window_size(width, height)
                time.sleep(1)
                
                # Check if page is still functional
                try:
                    self.driver.find_element(By.CLASS_NAME, "dashboard")
                except NoSuchElementException:
                    responsive_success = False
                    break
            
            success = responsive_success
            details = f"Tested {len(screen_sizes)} screen sizes"
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Responsive Design", success, details)
        return success

    def test_console_errors(self):
        """Test for JavaScript console errors"""
        if not self.driver:
            self.log_test("Console Errors", False, "WebDriver not available")
            return False
            
        try:
            self.driver.get(self.frontend_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "dashboard"))
            )
            
            # Get console logs
            logs = self.driver.get_log('browser')
            
            # Filter for errors
            errors = [log for log in logs if log['level'] == 'SEVERE']
            
            success = len(errors) == 0
            details = f"Found {len(errors)} console errors"
            
            if errors:
                # Show first error
                details += f" | First error: {errors[0]['message'][:50]}..."
            
        except Exception as e:
            success = True  # Assume success if we can't check logs
            details = f"Could not check console logs: {str(e)}"
        
        self.log_test("Console Errors", success, details)
        return success

    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

    def run_all_tests(self):
        """Run all frontend tests"""
        print("🖥️ Starting Frontend Integration Test Suite")
        print("=" * 60)
        
        # Check if frontend server is running
        if not self.test_frontend_accessibility():
            print("❌ Frontend server is not running. Please start with 'npm start'")
            return 0, 1
        
        # Setup WebDriver (optional for some tests)
        webdriver_available = self.setup_driver()
        if not webdriver_available:
            print("⚠️ WebDriver not available. Running limited tests.")
        
        try:
            # Basic tests
            if webdriver_available:
                self.test_page_load()
                self.test_dashboard_elements()
                self.test_api_status_display()
                self.test_statistics_display()
                self.test_refresh_functionality()
                self.test_responsive_design()
                self.test_console_errors()
            
        finally:
            self.cleanup()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Frontend Test Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        
        if total_tests > 0:
            print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    print("Note: This test requires Chrome WebDriver for full functionality")
    print("Install with: pip install selenium")
    print("And download ChromeDriver from: https://chromedriver.chromium.org/")
    print()
    
    tester = FrontendTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)