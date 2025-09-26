# QuantumCertify - Manual Testing Guide

This guide provides step-by-step instructions for manually testing all features and edge cases of the QuantumCertify application.

## Prerequisites

1. **Backend Server**: Ensure the FastAPI backend is running on `http://localhost:8000`
2. **Frontend Server** (optional): React frontend on `http://localhost:3000`
3. **Database**: SQL Server database with proper credentials configured
4. **Environment**: All environment variables set in backend/.env

## Test Categories

### 1. Basic Functionality Tests

#### 1.1 API Health Check
- **URL**: `http://localhost:8000/health`
- **Expected**: Status 200, JSON response with service info
- **Test Steps**:
  1. Open browser/Postman
  2. Send GET request to health endpoint
  3. Verify response contains service name and database status

#### 1.2 Dashboard Statistics
- **URL**: `http://localhost:8000/dashboard-statistics`
- **Expected**: Status 200, statistics data
- **Test Steps**:
  1. Send GET request to statistics endpoint
  2. Verify response contains certificate counts
  3. Check data source and last updated timestamp

#### 1.3 API Documentation
- **URL**: `http://localhost:8000/docs`
- **Expected**: Interactive Swagger UI
- **Test Steps**:
  1. Open URL in browser
  2. Verify all endpoints are listed
  3. Try "Try it out" on health endpoint

### 2. Certificate Upload Tests

#### 2.1 Valid Certificate Upload (RSA)
- **Endpoint**: `POST /upload-certificate`
- **Test Steps**:
  1. Create or obtain valid RSA certificate (.pem file)
  2. Upload via API or frontend
  3. Verify successful analysis response
  4. Check if statistics updated

#### 2.2 Valid Certificate Upload (ECC)
- **Test Steps**:
  1. Create or obtain valid ECC certificate
  2. Upload and verify analysis
  3. Compare results with RSA certificate

#### 2.3 Invalid File Upload Tests
- **Test Cases**:
  - Text file (.txt) instead of certificate
  - Empty file
  - Binary file (e.g., image, executable)
  - Malformed PEM data
  - File with no extension
- **Expected**: Proper error messages (400/422 status codes)

#### 2.4 Large File Upload
- **Test Steps**:
  1. Create file larger than expected limit (>10MB)
  2. Attempt upload
  3. Verify proper error handling (413 or 400 status)

#### 2.5 Unicode Filename Test
- **Test Cases**:
  - `证书.pem` (Chinese characters)
  - `сертификат.pem` (Cyrillic)
  - `🔐certificate🚀.pem` (Emoji)
  - `file with spaces.pem`
- **Expected**: Proper handling without server crashes

### 3. Security Tests

#### 3.1 SQL Injection Tests
- **Test Cases**:
  - Add `'; DROP TABLE users; --` in filename
  - Try SQL payloads in URL parameters
- **Expected**: No SQL errors exposed, proper sanitization

#### 3.2 XSS Prevention Tests
- **Test Cases**:
  - Upload file named `<script>alert('XSS')</script>.pem`
  - Try XSS in file content
- **Expected**: Content properly escaped in responses

#### 3.3 File Path Traversal Tests
- **Test Cases**:
  - Filename: `../../../etc/passwd`
  - Filename: `..\\..\\windows\\system32\\hosts`
- **Expected**: No access to system files

#### 3.4 CORS Configuration Test
- **Test Steps**:
  1. Send request with `Origin: http://malicious.com` header
  2. Check `Access-Control-Allow-Origin` response
  3. Verify only allowed origins are permitted

### 4. Performance Tests

#### 4.1 Response Time Test
- **Test Steps**:
  1. Send 10 consecutive requests to `/health`
  2. Measure response times
  3. Verify average < 200ms, max < 1s

#### 4.2 Concurrent Load Test
- **Test Steps**:
  1. Send 50 simultaneous requests
  2. Verify >90% success rate
  3. Check for proper error handling

#### 4.3 Certificate Processing Performance
- **Test Steps**:
  1. Upload certificates of different sizes (1KB, 5KB, 10KB)
  2. Measure processing time
  3. Verify reasonable performance (< 5s per certificate)

### 5. Database Integration Tests

#### 5.1 Statistics Persistence
- **Test Steps**:
  1. Note current statistics
  2. Upload a new certificate
  3. Verify statistics increment correctly
  4. Restart server and check persistence

#### 5.2 Database Connection Handling
- **Test Steps**:
  1. Temporarily break database connection
  2. Try uploading certificate
  3. Verify graceful error handling
  4. Restore connection and test recovery

### 6. Frontend Tests (If Available)

#### 6.1 Page Load Test
- **URL**: `http://localhost:3000`
- **Test Steps**:
  1. Open in browser
  2. Verify all components load
  3. Check for JavaScript errors in console

#### 6.2 API Status Display
- **Test Steps**:
  1. Check API status indicator on dashboard
  2. Stop backend server
  3. Verify error status is shown
  4. Restart server and check recovery

#### 6.3 File Upload UI
- **Test Steps**:
  1. Use drag-and-drop interface
  2. Try file picker
  3. Upload various file types
  4. Verify proper feedback messages

#### 6.4 Statistics Display
- **Test Steps**:
  1. Verify statistics are displayed
  2. Upload certificate and check live update
  3. Use refresh button
  4. Test auto-refresh functionality

### 7. Edge Cases and Error Conditions

#### 7.1 Network Interruption
- **Test Steps**:
  1. Start large file upload
  2. Disconnect network during upload
  3. Verify proper error handling
  4. Reconnect and retry

#### 7.2 Server Restart During Operation
- **Test Steps**:
  1. Start upload
  2. Restart backend server mid-request
  3. Verify client handles connection loss

#### 7.3 Malformed HTTP Requests
- **Test Cases**:
  - Incomplete multipart data
  - Invalid HTTP headers
  - Oversized request headers
- **Expected**: Proper HTTP error responses

#### 7.4 Resource Exhaustion
- **Test Steps**:
  1. Upload many certificates rapidly
  2. Monitor memory/CPU usage
  3. Verify no resource leaks

### 8. Browser Compatibility (Frontend)

#### 8.1 Cross-Browser Testing
- **Browsers to test**:
  - Chrome (latest)
  - Firefox (latest)  
  - Edge (latest)
  - Safari (if available)

#### 8.2 Mobile Responsiveness
- **Test Steps**:
  1. Open in mobile browser or dev tools
  2. Test at different screen sizes
  3. Verify usability on touch devices

### 9. Environment and Configuration Tests

#### 9.1 Environment Variables
- **Test Steps**:
  1. Remove required env var from .env
  2. Restart server
  3. Verify proper error message
  4. Restore and test recovery

#### 9.2 Database Configuration
- **Test Cases**:
  - Invalid database connection string
  - Wrong credentials
  - Database server unavailable
- **Expected**: Clear error messages, graceful degradation

## Testing Checklist

### Critical Features ✓
- [ ] API health endpoint works
- [ ] Certificate upload and analysis
- [ ] Statistics tracking and display
- [ ] Error handling for invalid files
- [ ] Database integration
- [ ] Environment variable configuration

### Security Features ✓
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] File upload validation
- [ ] Path traversal prevention
- [ ] Proper error messages (no info disclosure)
- [ ] CORS configuration

### Performance Features ✓
- [ ] Response times < 200ms average
- [ ] Concurrent request handling
- [ ] Large file rejection
- [ ] Memory usage stable
- [ ] No resource leaks

### User Experience ✓
- [ ] Clear error messages
- [ ] Progress feedback
- [ ] Responsive design
- [ ] Browser compatibility
- [ ] Accessibility features

## Common Issues and Solutions

### Backend Issues
- **Server won't start**: Check .env file and database connection
- **Upload failures**: Verify file permissions and upload size limits
- **Database errors**: Check SQL Server connection and credentials

### Frontend Issues
- **Page won't load**: Check if React dev server is running
- **API errors**: Verify backend server is accessible
- **CORS errors**: Check backend CORS configuration

### Performance Issues
- **Slow responses**: Check database query performance
- **High memory usage**: Look for memory leaks in certificate processing
- **Connection timeouts**: Review server configuration and network

## Test Automation

The automated test suites can be run with:
```bash
python test_comprehensive.py  # Core functionality
python test_security.py       # Security tests
python test_performance.py    # Performance tests
python test_frontend.py       # Frontend integration
python run_all_tests.py       # All tests combined
```

## Reporting Issues

When reporting issues, include:
1. Steps to reproduce
2. Expected vs actual behavior
3. Error messages/logs
4. Browser/environment details
5. Test data used

## Success Criteria

The application is considered production-ready when:
- All critical features work correctly
- No high/critical security vulnerabilities
- Performance meets requirements
- Error handling is robust
- User experience is smooth across browsers
- Automated tests pass consistently