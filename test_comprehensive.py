#!/usr/bin/env python3
"""
Comprehensive Test Suite for QuantumCertify Application
Tests all edge cases, error conditions, and functionality
"""

import requests
import json
import time
import os
import tempfile
import base64
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
import datetime
from typing import Dict, List, Tuple

class QuantumCertifyTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
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

    def test_api_health(self):
        """Test API health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f" | Service: {data.get('service', 'Unknown')}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("API Health Check", success, details)
        return success

    def test_dashboard_statistics(self):
        """Test dashboard statistics endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/dashboard-statistics")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                stats = data.get('statistics', {})
                details += f" | Total: {stats.get('totalCertificatesAnalyzed', 0)}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Dashboard Statistics", success, details)
        return success

    def create_test_certificate(self, key_type: str = "rsa", key_size: int = 2048) -> bytes:
        """Create a test certificate with specified parameters"""
        if key_type == "rsa":
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size
            )
        elif key_type == "ec":
            private_key = ec.generate_private_key(ec.SECP256R1())
        else:
            raise ValueError(f"Unsupported key type: {key_type}")

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Test State"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Test City"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Org"),
            x509.NameAttribute(NameOID.COMMON_NAME, "test.example.com"),
        ])

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("test.example.com"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())

        return cert.public_bytes(serialization.Encoding.PEM)

    def test_certificate_upload_valid(self):
        """Test valid certificate upload"""
        try:
            # Create a test RSA certificate
            cert_data = self.create_test_certificate("rsa", 2048)
            
            files = {'file': ('test_cert.pem', cert_data, 'application/x-pem-file')}
            response = self.session.post(f"{self.base_url}/upload-certificate", files=files)
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f" | Quantum Safe: {data.get('is_quantum_safe', False)}"
                details += f" | Algorithm: {data.get('signature_algorithm', 'Unknown')}"
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Valid Certificate Upload (RSA)", success, details)
        return success

    def test_certificate_upload_ec(self):
        """Test ECC certificate upload"""
        try:
            # Create a test ECC certificate
            cert_data = self.create_test_certificate("ec")
            
            files = {'file': ('test_cert_ec.pem', cert_data, 'application/x-pem-file')}
            response = self.session.post(f"{self.base_url}/upload-certificate", files=files)
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f" | Quantum Safe: {data.get('is_quantum_safe', False)}"
                details += f" | Algorithm: {data.get('signature_algorithm', 'Unknown')}"
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Valid Certificate Upload (ECC)", success, details)
        return success

    def test_certificate_upload_invalid_file(self):
        """Test invalid file upload"""
        try:
            # Upload a non-certificate file
            invalid_data = b"This is not a certificate"
            files = {'file': ('invalid.txt', invalid_data, 'text/plain')}
            response = self.session.post(f"{self.base_url}/upload-certificate", files=files)
            
            success = response.status_code == 400  # Should fail with 400
            details = f"Status: {response.status_code}"
            
            if response.status_code == 400:
                data = response.json()
                details += f" | Error: {data.get('detail', 'Unknown error')}"
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Invalid File Upload", success, details)
        return success

    def test_certificate_upload_no_file(self):
        """Test upload without file"""
        try:
            response = self.session.post(f"{self.base_url}/upload-certificate")
            success = response.status_code == 422  # Should fail with validation error
            details = f"Status: {response.status_code}"
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("No File Upload", success, details)
        return success

    def test_certificate_upload_empty_file(self):
        """Test upload with empty file"""
        try:
            files = {'file': ('empty.pem', b'', 'application/x-pem-file')}
            response = self.session.post(f"{self.base_url}/upload-certificate", files=files)
            
            success = response.status_code == 400  # Should fail
            details = f"Status: {response.status_code}"
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Empty File Upload", success, details)
        return success

    def test_certificate_upload_large_file(self):
        """Test upload with oversized file"""
        try:
            # Create a large file (simulate)
            large_data = b"A" * (10 * 1024 * 1024)  # 10MB
            files = {'file': ('large.pem', large_data, 'application/x-pem-file')}
            response = self.session.post(f"{self.base_url}/upload-certificate", files=files)
            
            success = response.status_code == 413 or response.status_code == 400  # Should fail
            details = f"Status: {response.status_code}"
            
        except Exception as e:
            success = True  # Connection errors are expected for large files
            details = f"Expected error: {str(e)}"
        
        self.log_test("Large File Upload", success, details)
        return success

    def test_cors_headers(self):
        """Test CORS headers"""
        try:
            response = self.session.options(f"{self.base_url}/health")
            success = 'Access-Control-Allow-Origin' in response.headers
            details = f"Status: {response.status_code} | CORS: {success}"
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("CORS Headers", success, details)
        return success

    def test_invalid_endpoints(self):
        """Test invalid endpoints"""
        try:
            response = self.session.get(f"{self.base_url}/nonexistent-endpoint")
            success = response.status_code == 404
            details = f"Status: {response.status_code}"
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Invalid Endpoint", success, details)
        return success

    def test_multiple_concurrent_uploads(self):
        """Test concurrent certificate uploads"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def upload_cert(cert_id):
            try:
                cert_data = self.create_test_certificate("rsa", 2048)
                files = {'file': (f'test_cert_{cert_id}.pem', cert_data, 'application/x-pem-file')}
                response = requests.post(f"{self.base_url}/upload-certificate", files=files)
                results.put((cert_id, response.status_code == 200))
            except Exception as e:
                results.put((cert_id, False))
        
        threads = []
        for i in range(5):  # 5 concurrent uploads
            thread = threading.Thread(target=upload_cert, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        successful = 0
        total = 0
        while not results.empty():
            cert_id, success = results.get()
            total += 1
            if success:
                successful += 1
        
        overall_success = successful >= 3  # At least 3 out of 5 should succeed
        details = f"Successful: {successful}/{total}"
        
        self.log_test("Concurrent Uploads", overall_success, details)
        return overall_success

    def test_statistics_update(self):
        """Test if statistics update after certificate upload"""
        try:
            # Get initial stats
            response1 = self.session.get(f"{self.base_url}/dashboard-statistics")
            if response1.status_code != 200:
                raise Exception("Failed to get initial stats")
            
            initial_stats = response1.json()['statistics']
            initial_total = initial_stats.get('totalCertificatesAnalyzed', 0)
            
            # Upload a certificate
            cert_data = self.create_test_certificate("rsa", 2048)
            files = {'file': ('stats_test.pem', cert_data, 'application/x-pem-file')}
            upload_response = self.session.post(f"{self.base_url}/upload-certificate", files=files)
            
            if upload_response.status_code != 200:
                raise Exception("Certificate upload failed")
            
            # Wait a moment and get updated stats
            time.sleep(1)
            response2 = self.session.get(f"{self.base_url}/dashboard-statistics")
            if response2.status_code != 200:
                raise Exception("Failed to get updated stats")
            
            updated_stats = response2.json()['statistics']
            updated_total = updated_stats.get('totalCertificatesAnalyzed', 0)
            
            success = updated_total > initial_total
            details = f"Initial: {initial_total} | Updated: {updated_total}"
            
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Statistics Update", success, details)
        return success

    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting Comprehensive QuantumCertify Test Suite")
        print("=" * 60)
        
        # Basic API tests
        self.test_api_health()
        self.test_dashboard_statistics()
        self.test_cors_headers()
        self.test_invalid_endpoints()
        
        # Certificate upload tests
        self.test_certificate_upload_valid()
        self.test_certificate_upload_ec()
        self.test_certificate_upload_invalid_file()
        self.test_certificate_upload_no_file()
        self.test_certificate_upload_empty_file()
        self.test_certificate_upload_large_file()
        
        # Advanced tests
        self.test_multiple_concurrent_uploads()
        self.test_statistics_update()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = QuantumCertifyTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)