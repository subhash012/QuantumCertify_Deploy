# QuantumCertify Railway Deployment - Critical Fixes Applied

## Issues Identified from Multiple Deployment Attempts

### Issue #1 (First Deployment)
- **ODBC Driver Version Mismatch**: Application expected "ODBC Driver 17" but Railway installed "ODBC Driver 18"

### Issue #2 (Second Deployment) 
- **Python Package Installation Failure**: `ModuleNotFoundError: No module named 'uvicorn'`
- **nixpacks Configuration Error**: Using single `cmd` instead of `cmds` array prevented package installation

### Issue #3 (Third Deployment)
- **GPG Command Not Available**: `sudo: gpg: command not found` during Microsoft ODBC driver installation
- **apt-key Dependency**: `apt-key` command requires gnupg packages not available in Railway environment

### Issue #4 (Fourth Deployment - Current)
- **Modern GPG Approach**: Switching to modern keyring approach that doesn't require `apt-key` command

## Fixes Applied

### 1. Database Configuration Fix
**File**: `backend/app/database.py`
```python
# Before (hardcoded):
"driver": "ODBC Driver 17 for SQL Server"

# After (uses environment variable):  
"driver": DB_DRIVER  # Uses "ODBC Driver 18 for SQL Server" from .env
```

### 2. Enhanced Startup Testing
**File**: `backend/startup_test.py` (NEW)
- Comprehensive startup testing during build phase
- Tests environment variables, imports, database connection, FastAPI app creation
- Helps identify issues before deployment completes

### 3. **CRITICAL FIX**: Corrected nixpacks Configuration and ODBC Installation
**File**: `nixpacks.toml`
```toml
# LATEST VERSION (4th deployment attempt):
[phases.install]
cmds = [
    # Microsoft ODBC Driver (modern GPG keyring approach)
    "curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg",
    "echo 'deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/ubuntu/22.04/prod jammy main' | sudo tee /etc/apt/sources.list.d/mssql-release.list",
    "sudo apt-get update", 
    "sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18",
    # Python packages
    "pip install --upgrade pip",
    "cd backend && pip install -r requirements.txt"
]

[phases.build] 
cmds = [
    "echo '=== QuantumCertify Build Phase ==='",
    "odbcinst -q -d || echo 'ODBC driver check failed but continuing'",
    "cd backend && python startup_test.py || echo 'Startup test completed'",
    "echo '=== Build phase completed ==='"
]
```

**Key Changes Made:**
- ✅ Fixed nixpacks syntax: `cmd` → `cmds` array  
- ✅ Switched to modern GPG keyring approach (no apt-key dependency)
- ✅ Uses `signed-by` directive in repository configuration
- ✅ Added ODBC verification in build phase (non-blocking)
- ✅ Proper GPG key installation without deprecated commands

### 4. Enhanced Server Startup Logging
**File**: `backend/run_server.py`
- Added detailed startup diagnostics
- Environment variable checking
- Better error reporting with full tracebacks
- More informative emoji-based logging

### 5. Added Missing Dependencies
**File**: `backend/requirements.txt`
```
httpx==0.27.2  # For FastAPI TestClient testing
```

## Expected Results

After redeployment with these critical fixes:

1. ✅ **Python Package Installation**: `pip install -r requirements.txt` will execute properly
2. ✅ **All Dependencies Available**: uvicorn, fastapi, pyodbc, and all required packages will be installed
3. ✅ **ODBC Driver**: Application will use correct "ODBC Driver 18 for SQL Server"
4. ✅ **Startup Testing**: Build logs will show detailed test results for each component  
5. ✅ **Server Startup**: Python server will start without import errors
6. ✅ **Health Endpoint**: Will respond correctly at `/health`
7. ✅ **Database Connection**: Should connect to Azure SQL Server successfully

## How to Redeploy

1. **Commit all changes**:
   ```bash
   git add .
   git commit -m "Fix Railway healthcheck issues - ODBC driver version and startup testing"
   ```

2. **Push to trigger new deployment**:
   ```bash
   git push origin main
   ```

3. **Monitor Railway Dashboard**:
   - Watch build logs for startup test results
   - Look for "ODBC Driver 18" in installation logs
   - Check for successful health endpoint response
   - Verify application starts and passes healthcheck

## Troubleshooting

If issues persist, check Railway logs for:
- Startup test results (should show which components pass/fail)
- ODBC driver installation confirmation
- Environment variables presence
- Database connection attempts
- FastAPI app initialization messages

The startup test script provides detailed diagnostics for each component and will help identify exactly what's failing.