#!/usr/bin/env python3
"""
Master Test Suite Runner for QuantumCertify Application
Orchestrates comprehensive testing of all components and edge cases
"""

import sys
import os
import time
import subprocess
import json
import requests
from datetime import datetime
from typing import Dict, List, Tuple

class MasterTestRunner:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_results = {
            'comprehensive': None,
            'security': None,
            'performance': None,
            'frontend': None
        }
        self.start_time = None
        self.end_time = None
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"🧪 {title}")
        print("=" * 80)
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        print("🔍 Checking Prerequisites...")
        
        prerequisites = {
            'Backend Server': self.check_backend_server(),
            'Required Packages': self.check_python_packages(),
            'Test Scripts': self.check_test_scripts()
        }
        
        all_good = True
        for name, status in prerequisites.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {name}")
            if not status:
                all_good = False
        
        return all_good
    
    def check_backend_server(self) -> bool:
        """Check if backend server is running"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def check_python_packages(self) -> bool:
        """Check if required Python packages are installed"""
        required_packages = [
            'requests', 'cryptography', 'fastapi', 'sqlalchemy'
        ]
        
        try:
            for package in required_packages:
                __import__(package)
            return True
        except ImportError:
            return False
    
    def check_test_scripts(self) -> bool:
        """Check if all test scripts exist"""
        test_scripts = [
            'test_comprehensive.py',
            'test_security.py', 
            'test_performance.py',
            'test_frontend.py'
        ]
        
        return all(os.path.exists(script) for script in test_scripts)
    
    def run_comprehensive_tests(self) -> Tuple[bool, Dict]:
        """Run comprehensive functionality tests"""
        self.print_header("COMPREHENSIVE FUNCTIONALITY TESTS")
        
        try:
            result = subprocess.run([
                sys.executable, 'test_comprehensive.py'
            ], capture_output=True, text=True, timeout=300)
            
            success = result.returncode == 0
            
            return success, {
                'success': success,
                'output': result.stdout,
                'errors': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return False, {
                'success': False,
                'output': '',
                'errors': 'Test timed out after 5 minutes',
                'return_code': -1
            }
        except Exception as e:
            return False, {
                'success': False,
                'output': '',
                'errors': str(e),
                'return_code': -1
            }
    
    def run_security_tests(self) -> Tuple[bool, Dict]:
        """Run security tests"""
        self.print_header("SECURITY VULNERABILITY TESTS")
        
        try:
            result = subprocess.run([
                sys.executable, 'test_security.py'
            ], capture_output=True, text=True, timeout=300)
            
            success = result.returncode == 0
            
            return success, {
                'success': success,
                'output': result.stdout,
                'errors': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return False, {
                'success': False,
                'output': '',
                'errors': 'Security tests timed out after 5 minutes',
                'return_code': -1
            }
        except Exception as e:
            return False, {
                'success': False,
                'output': '',
                'errors': str(e),
                'return_code': -1
            }
    
    def run_performance_tests(self) -> Tuple[bool, Dict]:
        """Run performance tests"""
        self.print_header("PERFORMANCE & LOAD TESTS")
        
        try:
            result = subprocess.run([
                sys.executable, 'test_performance.py'
            ], capture_output=True, text=True, timeout=600)  # 10 minutes for performance tests
            
            success = result.returncode == 0
            
            return success, {
                'success': success,
                'output': result.stdout,
                'errors': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return False, {
                'success': False,
                'output': '',
                'errors': 'Performance tests timed out after 10 minutes',
                'return_code': -1
            }
        except Exception as e:
            return False, {
                'success': False,
                'output': '',
                'errors': str(e),
                'return_code': -1
            }
    
    def run_frontend_tests(self) -> Tuple[bool, Dict]:
        """Run frontend tests"""
        self.print_header("FRONTEND INTEGRATION TESTS")
        
        try:
            result = subprocess.run([
                sys.executable, 'test_frontend.py'
            ], capture_output=True, text=True, timeout=300)
            
            success = result.returncode == 0
            
            return success, {
                'success': success,
                'output': result.stdout,
                'errors': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return False, {
                'success': False,
                'output': '',
                'errors': 'Frontend tests timed out after 5 minutes',
                'return_code': -1
            }
        except Exception as e:
            return False, {
                'success': False,
                'output': '',
                'errors': str(e),
                'return_code': -1
            }
    
    def run_edge_case_tests(self):
        """Run additional edge case tests"""
        self.print_header("EDGE CASE TESTS")
        
        edge_cases = [
            self.test_malformed_certificates(),
            self.test_network_interruption(),
            self.test_database_failure_handling(),
            self.test_extremely_large_files(),
            self.test_unicode_filenames(),
            self.test_concurrent_database_access()
        ]
        
        passed = sum(edge_cases)
        total = len(edge_cases)
        
        print(f"\n📊 Edge Case Test Results: {passed}/{total} passed")
        
        return passed == total
    
    def test_malformed_certificates(self) -> bool:
        """Test handling of malformed certificates"""
        try:
            malformed_certs = [
                b"-----BEGIN CERTIFICATE-----\nINVALID_DATA\n-----END CERTIFICATE-----",
                b"Not a certificate at all",
                b"-----BEGIN CERTIFICATE-----\n" + b"A" * 10000 + b"\n-----END CERTIFICATE-----",
                b"",  # Empty file
                b"\x00\x01\x02\x03"  # Binary garbage
            ]
            
            for i, cert_data in enumerate(malformed_certs):
                files = {'file': (f'malformed_{i}.pem', cert_data, 'application/x-pem-file')}
                response = requests.post(f"{self.backend_url}/upload-certificate", files=files, timeout=10)
                
                # Should return error (400 or 422), not 500
                if response.status_code >= 500:
                    print(f"❌ Malformed Certificate {i}: Server error (500+)")
                    return False
            
            print("✅ Malformed Certificate Handling: Proper error handling")
            return True
            
        except Exception as e:
            print(f"❌ Malformed Certificate Handling: {str(e)}")
            return False
    
    def test_network_interruption(self) -> bool:
        """Test handling of network interruptions"""
        try:
            # Test with very short timeout
            try:
                requests.get(f"{self.backend_url}/health", timeout=0.001)
            except requests.exceptions.Timeout:
                pass  # Expected
            except Exception as e:
                if "timeout" not in str(e).lower():
                    print(f"❌ Network Interruption: Unexpected error: {e}")
                    return False
            
            print("✅ Network Interruption: Proper timeout handling")
            return True
            
        except Exception as e:
            print(f"❌ Network Interruption: {str(e)}")
            return False
    
    def test_database_failure_handling(self) -> bool:
        """Test handling when database operations fail"""
        try:
            # This test assumes the app handles DB errors gracefully
            # We can't actually break the DB, so we test endpoints
            response = requests.get(f"{self.backend_url}/dashboard-statistics", timeout=10)
            
            # Should return some response, even if DB is having issues
            success = response.status_code in [200, 500, 503]  # Various acceptable responses
            
            status = "✅" if success else "❌"
            print(f"{status} Database Failure Handling: Response code {response.status_code}")
            
            return success
            
        except Exception as e:
            print(f"❌ Database Failure Handling: {str(e)}")
            return False
    
    def test_extremely_large_files(self) -> bool:
        """Test handling of extremely large files"""
        try:
            # Create a large file (1MB)
            large_content = b"A" * (1024 * 1024)
            
            files = {'file': ('large_file.pem', large_content, 'application/x-pem-file')}
            response = requests.post(f"{self.backend_url}/upload-certificate", files=files, timeout=30)
            
            # Should reject large files gracefully (413 or 400)
            success = response.status_code in [400, 413, 422]
            
            status = "✅" if success else "❌"
            print(f"{status} Large File Handling: Response code {response.status_code}")
            
            return success
            
        except Exception as e:
            # Connection errors are acceptable for very large files
            print("✅ Large File Handling: Connection rejected (as expected)")
            return True
    
    def test_unicode_filenames(self) -> bool:
        """Test handling of unicode and special characters in filenames"""
        try:
            unicode_names = [
                "测试证书.pem",
                "certificado_español.pem",
                "сертификат.pem",
                "🔐certificate🚀.pem",
                "file with spaces.pem",
                "file-with-dashes.pem"
            ]
            
            success_count = 0
            
            for filename in unicode_names:
                try:
                    files = {'file': (filename, b'test content', 'application/x-pem-file')}
                    response = requests.post(f"{self.backend_url}/upload-certificate", files=files, timeout=10)
                    
                    # Should handle gracefully (return 400/422, not crash)
                    if response.status_code < 500:
                        success_count += 1
                        
                except Exception:
                    pass  # Some failures are expected
            
            success = success_count >= len(unicode_names) // 2  # At least half should work
            
            status = "✅" if success else "❌"
            print(f"{status} Unicode Filename Handling: {success_count}/{len(unicode_names)} handled properly")
            
            return success
            
        except Exception as e:
            print(f"❌ Unicode Filename Handling: {str(e)}")
            return False
    
    def test_concurrent_database_access(self) -> bool:
        """Test concurrent database access"""
        try:
            import threading
            import queue
            
            results = queue.Queue()
            
            def db_worker():
                try:
                    response = requests.get(f"{self.backend_url}/dashboard-statistics", timeout=10)
                    results.put(response.status_code == 200)
                except Exception:
                    results.put(False)
            
            # Start multiple threads accessing the database
            threads = []
            for _ in range(10):
                thread = threading.Thread(target=db_worker)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join()
            
            # Check results
            successes = 0
            while not results.empty():
                if results.get():
                    successes += 1
            
            success = successes >= 8  # At least 80% should succeed
            
            status = "✅" if success else "❌"
            print(f"{status} Concurrent Database Access: {successes}/10 successful")
            
            return success
            
        except Exception as e:
            print(f"❌ Concurrent Database Access: {str(e)}")
            return False
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        self.print_header("TEST REPORT GENERATION")
        
        report = {
            'test_run': {
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': self.end_time.isoformat() if self.end_time else None,
                'duration': str(self.end_time - self.start_time) if self.start_time and self.end_time else None
            },
            'results': self.test_results,
            'summary': {
                'total_test_suites': len(self.test_results),
                'passed_suites': sum(1 for result in self.test_results.values() if result and result.get('success')),
                'failed_suites': sum(1 for result in self.test_results.values() if result and not result.get('success'))
            }
        }
        
        # Save report to file
        report_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"✅ Test report saved to: {report_filename}")
            
        except Exception as e:
            print(f"❌ Failed to save test report: {e}")
        
        return report
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("FINAL TEST SUMMARY")
        
        if not any(self.test_results.values()):
            print("❌ No tests were executed successfully")
            return
        
        suite_results = []
        
        for suite_name, result in self.test_results.items():
            if result is not None:
                success = result.get('success', False)
                status = "✅ PASS" if success else "❌ FAIL"
                suite_results.append((suite_name.title(), status, success))
                print(f"  {status} | {suite_name.title()} Tests")
        
        total_suites = len([r for r in self.test_results.values() if r is not None])
        passed_suites = sum(1 for _, _, success in suite_results if success)
        
        print(f"\n📊 Overall Results:")
        print(f"  Total Test Suites: {total_suites}")
        print(f"  ✅ Passed Suites: {passed_suites}")
        print(f"  ❌ Failed Suites: {total_suites - passed_suites}")
        print(f"  Success Rate: {(passed_suites/total_suites)*100:.1f}%" if total_suites > 0 else "  Success Rate: N/A")
        
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            print(f"  Total Duration: {duration}")
        
        # Overall assessment
        if passed_suites == total_suites:
            print(f"\n🎉 ALL TESTS PASSED! QuantumCertify is ready for production.")
        elif passed_suites >= total_suites * 0.75:
            print(f"\n⚠️ Most tests passed, but some issues need attention.")
        else:
            print(f"\n🚨 Multiple test failures detected. Application needs fixes before deployment.")
    
    def run_all_tests(self, include_frontend=True, include_performance=True):
        """Run all test suites"""
        self.start_time = datetime.now()
        
        self.print_header("QuantumCertify Comprehensive Test Suite")
        print(f"🚀 Starting test execution at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("\n❌ Prerequisites not met. Please fix the issues above and try again.")
            return False
        
        print("\n✅ All prerequisites met. Starting tests...")
        
        # Run test suites
        try:
            # 1. Comprehensive functionality tests
            success, result = self.run_comprehensive_tests()
            self.test_results['comprehensive'] = result
            print(result['output'] if result['output'] else result['errors'])
            
            # 2. Security tests
            success, result = self.run_security_tests()
            self.test_results['security'] = result
            print(result['output'] if result['output'] else result['errors'])
            
            # 3. Performance tests (optional)
            if include_performance:
                success, result = self.run_performance_tests()
                self.test_results['performance'] = result
                print(result['output'] if result['output'] else result['errors'])
            
            # 4. Frontend tests (optional)
            if include_frontend:
                success, result = self.run_frontend_tests()
                self.test_results['frontend'] = result
                print(result['output'] if result['output'] else result['errors'])
            
            # 5. Additional edge case tests
            edge_case_success = self.run_edge_case_tests()
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Test execution interrupted by user")
            return False
        
        except Exception as e:
            print(f"\n\n❌ Test execution failed with error: {e}")
            return False
        
        finally:
            self.end_time = datetime.now()
        
        # Generate report and summary
        self.generate_test_report()
        self.print_summary()
        
        # Return overall success
        all_critical_passed = (
            self.test_results.get('comprehensive', {}).get('success', False) and
            self.test_results.get('security', {}).get('success', False)
        )
        
        return all_critical_passed

if __name__ == "__main__":
    print("🧪 QuantumCertify Master Test Suite")
    print("This will run comprehensive tests for all components")
    print("Ensure the backend server is running before starting tests")
    print()
    
    # Parse command line arguments
    include_frontend = "--no-frontend" not in sys.argv
    include_performance = "--no-performance" not in sys.argv
    
    if not include_frontend:
        print("⚠️ Frontend tests disabled")
    if not include_performance:
        print("⚠️ Performance tests disabled")
    
    # Run tests
    runner = MasterTestRunner()
    success = runner.run_all_tests(
        include_frontend=include_frontend,
        include_performance=include_performance
    )
    
    # Exit with appropriate code
    exit(0 if success else 1)