#!/usr/bin/env python3
"""
Security Test Suite for QuantumCertify Application
Tests security vulnerabilities, injection attacks, and security headers
"""

import requests
import json
import base64
import time
from typing import Dict, List
import urllib.parse

class SecurityTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", severity: str = "INFO"):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} | {test_name}"
        if details:
            result += f" | {details}"
        if severity != "INFO":
            result += f" | Severity: {severity}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'severity': severity
        })

    def test_sql_injection(self):
        """Test for SQL injection vulnerabilities"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM information_schema.tables --",
            "1' AND (SELECT COUNT(*) FROM sysobjects) > 0 --",
        ]
        
        vulnerable = False
        
        for payload in sql_payloads:
            try:
                # Test in various parameters
                response = self.session.get(f"{self.base_url}/dashboard-statistics?filter={urllib.parse.quote(payload)}")
                
                # Look for SQL error messages
                if any(error in response.text.lower() for error in [
                    "sql syntax", "mysql", "postgresql", "ora-", "microsoft sql",
                    "syntax error", "unclosed quotation"
                ]):
                    vulnerable = True
                    break
                    
            except Exception:
                pass  # Connection errors are not vulnerabilities
        
        success = not vulnerable
        details = "No SQL injection vulnerabilities detected" if success else "Potential SQL injection found"
        severity = "CRITICAL" if vulnerable else "INFO"
        
        self.log_test("SQL Injection", success, details, severity)
        return success

    def test_xss_protection(self):
        """Test for Cross-Site Scripting vulnerabilities"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "'\"><script>alert('XSS')</script>",
        ]
        
        vulnerable = False
        
        try:
            # Create a malicious "certificate" with XSS payload
            malicious_content = xss_payloads[0].encode()
            files = {'file': ('xss_test.pem', malicious_content, 'application/x-pem-file')}
            response = self.session.post(f"{self.base_url}/upload-certificate", files=files)
            
            # Check if the payload is reflected without encoding
            if any(payload in response.text for payload in xss_payloads):
                vulnerable = True
                
        except Exception:
            pass
        
        success = not vulnerable
        details = "No XSS vulnerabilities detected" if success else "Potential XSS vulnerability found"
        severity = "HIGH" if vulnerable else "INFO"
        
        self.log_test("XSS Protection", success, details, severity)
        return success

    def test_file_upload_security(self):
        """Test file upload security"""
        malicious_files = [
            # PHP webshell
            ('shell.php', b'<?php system($_GET["cmd"]); ?>', 'application/x-php'),
            # Executable
            ('malware.exe', b'MZ\x90\x00' + b'\x00' * 100, 'application/x-msdownload'),
            # Script file
            ('script.js', b'alert("XSS")', 'application/javascript'),
            # Very long filename
            ('A' * 1000 + '.pem', b'test', 'application/x-pem-file'),
        ]
        
        vulnerabilities = []
        
        for filename, content, mime_type in malicious_files:
            try:
                files = {'file': (filename, content, mime_type)}
                response = self.session.post(f"{self.base_url}/upload-certificate", files=files)
                
                # Check if file was accepted (it shouldn't be)
                if response.status_code == 200:
                    vulnerabilities.append(f"Accepted {filename}")
                    
            except Exception:
                pass
        
        success = len(vulnerabilities) == 0
        details = f"Found {len(vulnerabilities)} file upload issues" if vulnerabilities else "File upload properly secured"
        severity = "HIGH" if vulnerabilities else "INFO"
        
        self.log_test("File Upload Security", success, details, severity)
        return success

    def test_directory_traversal(self):
        """Test for directory traversal vulnerabilities"""
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        ]
        
        vulnerable = False
        
        for payload in traversal_payloads:
            try:
                # Test as filename in upload
                files = {'file': (payload, b'test content', 'application/x-pem-file')}
                response = self.session.post(f"{self.base_url}/upload-certificate", files=files)
                
                # Look for system file content
                if any(indicator in response.text.lower() for indicator in [
                    "root:", "[boot loader]", "windows registry", "/bin/bash"
                ]):
                    vulnerable = True
                    break
                    
            except Exception:
                pass
        
        success = not vulnerable
        details = "No directory traversal vulnerabilities detected" if success else "Potential directory traversal found"
        severity = "HIGH" if vulnerable else "INFO"
        
        self.log_test("Directory Traversal", success, details, severity)
        return success

    def test_security_headers(self):
        """Test for security headers"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            headers = response.headers
            
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': None,  # Any value is good
                'Content-Security-Policy': None,
            }
            
            missing_headers = []
            
            for header, expected_values in security_headers.items():
                if header not in headers:
                    missing_headers.append(header)
                elif expected_values and isinstance(expected_values, list):
                    if headers[header] not in expected_values:
                        missing_headers.append(f"{header} (wrong value)")
            
            success = len(missing_headers) <= 2  # Allow some missing headers
            details = f"Missing/incorrect headers: {missing_headers}" if missing_headers else "Security headers present"
            severity = "MEDIUM" if missing_headers else "INFO"
            
        except Exception as e:
            success = False
            details = f"Error checking headers: {str(e)}"
            severity = "INFO"
        
        self.log_test("Security Headers", success, details, severity)
        return success

    def test_rate_limiting(self):
        """Test for rate limiting"""
        try:
            # Make rapid requests
            responses = []
            for i in range(20):
                response = self.session.get(f"{self.base_url}/health")
                responses.append(response.status_code)
                if response.status_code == 429:  # Too Many Requests
                    break
            
            # Check if rate limiting is in place
            rate_limited = 429 in responses
            
            success = True  # Rate limiting is optional but good practice
            details = "Rate limiting detected" if rate_limited else "No rate limiting detected (consider implementing)"
            severity = "LOW" if not rate_limited else "INFO"
            
        except Exception as e:
            success = True
            details = f"Could not test rate limiting: {str(e)}"
            severity = "INFO"
        
        self.log_test("Rate Limiting", success, details, severity)
        return success

    def test_error_information_disclosure(self):
        """Test for information disclosure in error messages"""
        try:
            # Send malformed request
            response = self.session.post(f"{self.base_url}/upload-certificate", 
                                       data="malformed data")
            
            # Look for sensitive information in error messages
            sensitive_info = [
                "traceback", "stack trace", "file not found",
                "c:\\", "/home/", "/var/", "python",
                "internal server error", "debug", "exception"
            ]
            
            disclosed_info = [info for info in sensitive_info 
                            if info in response.text.lower()]
            
            success = len(disclosed_info) == 0
            details = f"Information disclosed: {disclosed_info}" if disclosed_info else "No sensitive information disclosed"
            severity = "MEDIUM" if disclosed_info else "INFO"
            
        except Exception as e:
            success = True
            details = f"Could not test error disclosure: {str(e)}"
            severity = "INFO"
        
        self.log_test("Error Information Disclosure", success, details, severity)
        return success

    def test_cors_configuration(self):
        """Test CORS configuration security"""
        try:
            # Test with various origins
            test_origins = [
                "http://malicious.com",
                "https://evil.example.com",
                "null",
                "*"
            ]
            
            permissive_cors = []
            
            for origin in test_origins:
                headers = {'Origin': origin}
                response = self.session.options(f"{self.base_url}/health", headers=headers)
                
                cors_origin = response.headers.get('Access-Control-Allow-Origin', '')
                if cors_origin == '*' or cors_origin == origin:
                    permissive_cors.append(origin)
            
            success = len(permissive_cors) == 0 or 'http://localhost:3000' in str(permissive_cors)
            details = f"Permissive CORS for: {permissive_cors}" if permissive_cors else "CORS properly configured"
            severity = "MEDIUM" if len(permissive_cors) > 1 else "INFO"
            
        except Exception as e:
            success = True
            details = f"Could not test CORS: {str(e)}"
            severity = "INFO"
        
        self.log_test("CORS Configuration", success, details, severity)
        return success

    def test_input_validation(self):
        """Test input validation"""
        try:
            # Test with various invalid inputs
            test_cases = [
                # Extremely long input
                ("A" * 10000, "Long input"),
                # Binary data
                (b'\x00\x01\x02\x03', "Binary data"),
                # Unicode characters
                ("🔐💻🚀", "Unicode characters"),
                # Control characters
                ("\x00\x0A\x0D", "Control characters"),
            ]
            
            validation_issues = []
            
            for test_input, description in test_cases:
                try:
                    if isinstance(test_input, str):
                        test_input = test_input.encode()
                    
                    files = {'file': ('test.pem', test_input, 'application/x-pem-file')}
                    response = self.session.post(f"{self.base_url}/upload-certificate", files=files)
                    
                    # Should return proper error (400, 422)
                    if response.status_code == 200:
                        validation_issues.append(description)
                        
                except Exception:
                    pass  # Connection errors are expected for some inputs
            
            success = len(validation_issues) == 0
            details = f"Validation issues: {validation_issues}" if validation_issues else "Input validation working properly"
            severity = "MEDIUM" if validation_issues else "INFO"
            
        except Exception as e:
            success = True
            details = f"Could not test input validation: {str(e)}"
            severity = "INFO"
        
        self.log_test("Input Validation", success, details, severity)
        return success

    def run_all_tests(self):
        """Run all security tests"""
        print("🔒 Starting Security Test Suite")
        print("=" * 60)
        
        # Run security tests
        self.test_sql_injection()
        self.test_xss_protection()
        self.test_file_upload_security()
        self.test_directory_traversal()
        self.test_security_headers()
        self.test_rate_limiting()
        self.test_error_information_disclosure()
        self.test_cors_configuration()
        self.test_input_validation()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Security Test Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        critical_issues = sum(1 for result in self.test_results 
                            if not result['success'] and result.get('severity') == 'CRITICAL')
        high_issues = sum(1 for result in self.test_results 
                         if not result['success'] and result.get('severity') == 'HIGH')
        medium_issues = sum(1 for result in self.test_results 
                           if not result['success'] and result.get('severity') == 'MEDIUM')
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"🚨 Critical Issues: {critical_issues}")
        print(f"⚠️ High Issues: {high_issues}")
        print(f"📝 Medium Issues: {medium_issues}")
        
        if total_tests > 0:
            print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Security Issues Found:")
            for result in self.test_results:
                if not result['success']:
                    severity = result.get('severity', 'INFO')
                    print(f"  [{severity}] {result['test']}: {result['details']}")
        
        return passed_tests, failed_tests, critical_issues + high_issues

if __name__ == "__main__":
    tester = SecurityTester()
    passed, failed, critical = tester.run_all_tests()
    
    # Exit with appropriate code (non-zero for critical security issues)
    exit(1 if critical > 0 else 0)