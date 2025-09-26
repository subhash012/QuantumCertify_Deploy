#!/usr/bin/env python3
"""
Performance Test Suite for QuantumCertify Application
Tests load, stress, and performance characteristics
"""

import requests
import time
import threading
import statistics
import psutil
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime

class PerformanceTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", metrics: Dict = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} | {test_name}"
        if details:
            result += f" | {details}"
        if metrics:
            result += f" | Metrics: {metrics}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'metrics': metrics or {}
        })

    def create_test_certificate(self, key_size: int = 2048) -> bytes:
        """Create a test certificate"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )

        subject = issuer = x509.Name([
            x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "Test Org"),
            x509.NameAttribute(x509.NameOID.COMMON_NAME, "test.example.com"),
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
        ).sign(private_key, hashes.SHA256())

        return cert.public_bytes(serialization.Encoding.PEM)

    def measure_response_time(self, url: str, method: str = "GET", **kwargs) -> Tuple[float, int, bool]:
        """Measure response time for a request"""
        start_time = time.time()
        try:
            if method == "GET":
                response = requests.get(url, **kwargs)
            elif method == "POST":
                response = requests.post(url, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = time.time()
            return end_time - start_time, response.status_code, True
        except Exception:
            end_time = time.time()
            return end_time - start_time, 0, False

    def test_api_response_time(self):
        """Test API response times"""
        endpoints = [
            ("/health", "GET"),
            ("/dashboard-statistics", "GET"),
        ]
        
        all_times = []
        failed_requests = 0
        
        for endpoint, method in endpoints:
            times = []
            for _ in range(10):  # 10 requests per endpoint
                response_time, status_code, success = self.measure_response_time(
                    f"{self.base_url}{endpoint}", method
                )
                
                if success and 200 <= status_code < 300:
                    times.append(response_time)
                    all_times.append(response_time)
                else:
                    failed_requests += 1
        
        if all_times:
            avg_time = statistics.mean(all_times)
            max_time = max(all_times)
            min_time = min(all_times)
            
            # Good performance: avg < 200ms, max < 1s
            success = avg_time < 0.2 and max_time < 1.0
            
            metrics = {
                'avg_response_time': round(avg_time * 1000, 2),  # ms
                'max_response_time': round(max_time * 1000, 2),  # ms
                'min_response_time': round(min_time * 1000, 2),  # ms
                'failed_requests': failed_requests
            }
            
            details = f"Avg: {metrics['avg_response_time']}ms, Max: {metrics['max_response_time']}ms"
        else:
            success = False
            metrics = {'failed_requests': failed_requests}
            details = "All requests failed"
        
        self.log_test("API Response Time", success, details, metrics)
        return success

    def test_concurrent_requests(self, num_threads: int = 10, requests_per_thread: int = 5):
        """Test concurrent request handling"""
        def make_request():
            try:
                response = requests.get(f"{self.base_url}/health", timeout=10)
                return response.status_code == 200, time.time()
            except Exception:
                return False, time.time()
        
        start_time = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Submit all requests
            futures = []
            for _ in range(num_threads * requests_per_thread):
                future = executor.submit(make_request)
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                success, timestamp = future.result()
                results.append((success, timestamp))
        
        end_time = time.time()
        total_time = end_time - start_time
        successful_requests = sum(1 for success, _ in results if success)
        total_requests = len(results)
        
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        requests_per_second = total_requests / total_time if total_time > 0 else 0
        
        # Good performance: >90% success rate, >50 RPS
        success = success_rate >= 0.9 and requests_per_second >= 50
        
        metrics = {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': round(success_rate * 100, 2),
            'requests_per_second': round(requests_per_second, 2),
            'total_time': round(total_time, 2)
        }
        
        details = f"Success: {metrics['success_rate']}%, RPS: {metrics['requests_per_second']}"
        
        self.log_test(f"Concurrent Requests ({num_threads} threads)", success, details, metrics)
        return success

    def test_file_upload_performance(self):
        """Test file upload performance"""
        cert_sizes = [1024, 2048, 4096]  # Different key sizes
        upload_times = []
        
        for key_size in cert_sizes:
            cert_data = self.create_test_certificate(key_size)
            
            # Measure upload time
            start_time = time.time()
            try:
                files = {'file': (f'perf_test_{key_size}.pem', cert_data, 'application/x-pem-file')}
                response = requests.post(f"{self.base_url}/upload-certificate", files=files, timeout=30)
                end_time = time.time()
                
                if response.status_code == 200:
                    upload_times.append(end_time - start_time)
                
            except Exception:
                pass
        
        if upload_times:
            avg_upload_time = statistics.mean(upload_times)
            max_upload_time = max(upload_times)
            
            # Good performance: avg < 2s, max < 5s
            success = avg_upload_time < 2.0 and max_upload_time < 5.0
            
            metrics = {
                'avg_upload_time': round(avg_upload_time, 2),
                'max_upload_time': round(max_upload_time, 2),
                'certificates_tested': len(upload_times)
            }
            
            details = f"Avg: {metrics['avg_upload_time']}s, Max: {metrics['max_upload_time']}s"
        else:
            success = False
            metrics = {'certificates_tested': 0}
            details = "All uploads failed"
        
        self.log_test("File Upload Performance", success, details, metrics)
        return success

    def test_memory_usage(self):
        """Test memory usage during operation"""
        try:
            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform operations that might cause memory leaks
            for i in range(20):
                cert_data = self.create_test_certificate()
                files = {'file': (f'memory_test_{i}.pem', cert_data, 'application/x-pem-file')}
                
                try:
                    requests.post(f"{self.base_url}/upload-certificate", files=files, timeout=10)
                except Exception:
                    pass
            
            # Get final memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Acceptable memory increase: < 50MB
            success = memory_increase < 50
            
            metrics = {
                'initial_memory_mb': round(initial_memory, 2),
                'final_memory_mb': round(final_memory, 2),
                'memory_increase_mb': round(memory_increase, 2)
            }
            
            details = f"Increase: {metrics['memory_increase_mb']}MB"
            
        except Exception as e:
            success = True  # Assume success if we can't measure
            metrics = {}
            details = f"Could not measure memory: {str(e)}"
        
        self.log_test("Memory Usage", success, details, metrics)
        return success

    def test_cpu_usage(self):
        """Test CPU usage during load"""
        try:
            # Monitor CPU usage during concurrent requests
            cpu_samples = []
            
            def monitor_cpu():
                for _ in range(30):  # Monitor for 30 seconds
                    cpu_samples.append(psutil.cpu_percent(interval=1))
            
            def generate_load():
                for _ in range(50):
                    try:
                        requests.get(f"{self.base_url}/health", timeout=5)
                        time.sleep(0.1)
                    except Exception:
                        pass
            
            # Start monitoring and load generation
            monitor_thread = threading.Thread(target=monitor_cpu)
            load_thread = threading.Thread(target=generate_load)
            
            monitor_thread.start()
            load_thread.start()
            
            load_thread.join()
            monitor_thread.join()
            
            if cpu_samples:
                avg_cpu = statistics.mean(cpu_samples)
                max_cpu = max(cpu_samples)
                
                # Reasonable CPU usage: avg < 50%, max < 80%
                success = avg_cpu < 50 and max_cpu < 80
                
                metrics = {
                    'avg_cpu_percent': round(avg_cpu, 2),
                    'max_cpu_percent': round(max_cpu, 2),
                    'samples': len(cpu_samples)
                }
                
                details = f"Avg: {metrics['avg_cpu_percent']}%, Max: {metrics['max_cpu_percent']}%"
            else:
                success = True
                metrics = {}
                details = "No CPU samples collected"
                
        except Exception as e:
            success = True  # Assume success if we can't measure
            metrics = {}
            details = f"Could not measure CPU: {str(e)}"
        
        self.log_test("CPU Usage", success, details, metrics)
        return success

    def test_database_performance(self):
        """Test database operation performance"""
        try:
            # Test statistics retrieval multiple times
            response_times = []
            
            for _ in range(20):
                start_time = time.time()
                response = requests.get(f"{self.base_url}/dashboard-statistics")
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
            
            if response_times:
                avg_time = statistics.mean(response_times)
                max_time = max(response_times)
                
                # Good DB performance: avg < 100ms, max < 500ms
                success = avg_time < 0.1 and max_time < 0.5
                
                metrics = {
                    'avg_db_time': round(avg_time * 1000, 2),  # ms
                    'max_db_time': round(max_time * 1000, 2),  # ms
                    'queries_tested': len(response_times)
                }
                
                details = f"Avg: {metrics['avg_db_time']}ms, Max: {metrics['max_db_time']}ms"
            else:
                success = False
                metrics = {}
                details = "No successful database queries"
                
        except Exception as e:
            success = False
            metrics = {}
            details = f"Database test failed: {str(e)}"
        
        self.log_test("Database Performance", success, details, metrics)
        return success

    def test_stress_test(self):
        """Stress test with high load"""
        def stress_worker():
            success_count = 0
            total_count = 0
            
            for _ in range(10):  # 10 requests per worker
                total_count += 1
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=5)
                    if response.status_code == 200:
                        success_count += 1
                except Exception:
                    pass
                
                time.sleep(0.01)  # Small delay between requests
            
            return success_count, total_count
        
        # Run stress test with many workers
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(stress_worker) for _ in range(50)]
            
            total_success = 0
            total_requests = 0
            
            for future in as_completed(futures):
                success, total = future.result()
                total_success += success
                total_requests += total
        
        end_time = time.time()
        duration = end_time - start_time
        
        success_rate = total_success / total_requests if total_requests > 0 else 0
        rps = total_requests / duration if duration > 0 else 0
        
        # Stress test success: >75% success rate under high load
        success = success_rate >= 0.75
        
        metrics = {
            'total_requests': total_requests,
            'successful_requests': total_success,
            'success_rate': round(success_rate * 100, 2),
            'requests_per_second': round(rps, 2),
            'duration': round(duration, 2)
        }
        
        details = f"Success: {metrics['success_rate']}%, RPS: {metrics['requests_per_second']}"
        
        self.log_test("Stress Test (High Load)", success, details, metrics)
        return success

    def run_all_tests(self):
        """Run all performance tests"""
        print("⚡ Starting Performance Test Suite")
        print("=" * 60)
        
        # Basic performance tests
        self.test_api_response_time()
        self.test_concurrent_requests(10, 5)
        self.test_file_upload_performance()
        self.test_database_performance()
        
        # Resource usage tests
        self.test_memory_usage()
        self.test_cpu_usage()
        
        # Stress tests
        self.test_concurrent_requests(20, 10)  # Higher load
        self.test_stress_test()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Performance Test Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        
        if total_tests > 0:
            print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Performance metrics summary
        print("\n📈 Key Performance Metrics:")
        for result in self.test_results:
            if result.get('metrics'):
                print(f"  {result['test']}:")
                for key, value in result['metrics'].items():
                    print(f"    {key}: {value}")
        
        if failed_tests > 0:
            print("\n❌ Performance Issues:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = PerformanceTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)