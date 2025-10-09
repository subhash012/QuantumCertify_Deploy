# 🚂 Railway Environment Variables - REQUIRED

## ⚠️ CRITICAL: Add These to Railway Dashboard

After pushing to GitHub, **immediately add these environment variables** in Railway Dashboard:

### Backend Service Environment Variables

```bash
# Google Gemini AI (REQUIRED)
GEMINI_API_KEY=AIzaSyD4qM8BKQ-dcW1ijr-ckY9BTbgfGGP1kDE

# Azure SQL Server Database (REQUIRED - Your data is here!)
DB_SERVER=quantumcertify-sqlsrv.database.windows.net
DB_NAME=QuantumCertifyDB
DB_USERNAME=sqladminuser
DB_PASSWORD=Subhash1234#
DB_PORT=1433
DB_DRIVER=ODBC Driver 17 for SQL Server

# Application Settings
ENVIRONMENT=production
PORT=8000

# Security (Optional - but recommended)
SECRET_KEY=h3rA4!aCf+qgU7wsaXF58tCJKQIl1BV6AZ4T*3h+LQCeRi&^)#gCjmI-r^zpk^gZ
JWT_SECRET=mbI2YJY-M3SZgkkwiq9ncfRGKR2FsKnpL5ETLLiEqig
```

---

## 📋 Step-by-Step Instructions

### 1. Open Railway Dashboard
Go to: https://railway.app/dashboard

### 2. Select Your Backend Service
Click on your QuantumCertify backend deployment

### 3. Add Variables
1. Click **"Variables"** tab
2. Click **"New Variable"**
3. Add each variable above (copy-paste the values exactly)

### 4. Important Notes

#### ✅ ODBC Driver Change
- Changed from `ODBC Driver 18` → `ODBC Driver 17`
- Reason: Better compatibility with Debian 11 (Railway/Nixpacks)
- Your Azure SQL Server supports both versions

#### ✅ Database Connection
- Railway will connect to your existing Azure SQL Server
- All your existing data will be accessible
- No data migration needed

#### ✅ Firewall Rules
**IMPORTANT**: Check Azure SQL Server firewall settings:
1. Go to Azure Portal → SQL Server → Networking
2. Add rule: **"Allow Azure services and resources to access this server"** = ON
3. Or add specific Railway IP ranges (contact Railway support for IPs)

---

## 🔍 Verify Deployment

After deployment completes:

1. **Check Health Endpoint**
   ```bash
   curl https://your-railway-backend.railway.app/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "services": {
       "database": "available",  ← Should say "available"
       "ai_service": "available"
     }
   }
   ```

2. **Check Logs**
   - Railway Dashboard → Your Service → Logs
   - Look for: "Database connection successful" or "Using SQLite fallback"
   - Should see: "Connected to Azure SQL Server"

3. **Test API**
   - Upload a test certificate
   - Verify data is saved to SQL Server
   - Check Azure SQL Server for new records

---

## 🐛 Troubleshooting

### Issue: "Database connection failed"

**Check 1: Environment Variables**
- Verify all DB_* variables are set correctly in Railway
- No typos in values

**Check 2: Azure Firewall**
- Azure Portal → SQL Server → Networking
- Allow Azure services = ON
- Or add Railway IPs to whitelist

**Check 3: Connection String**
- Railway logs should show connection attempt
- Error will indicate if username/password/server is wrong

### Issue: "ODBC Driver not found"

**Check Build Logs**:
- Railway Dashboard → Deployments → Build Logs
- Should see: "Successfully installed msodbcsql17"
- If not, the install command failed

**Solution**:
- Check nixpacks.toml was updated
- Redeploy from GitHub

---

## ✅ Success Indicators

Your deployment is successful when:

1. ✅ Build completes without errors
2. ✅ Health endpoint shows `"database": "available"`
3. ✅ Logs show "Connected to database"
4. ✅ Certificate upload works
5. ✅ Data appears in Azure SQL Server
6. ✅ AI recommendations working

---

## 📞 Need Help?

If deployment still fails:
1. Check Railway build logs
2. Check Railway runtime logs
3. Verify Azure SQL Server is accessible from internet
4. Test SQL Server connection from your local machine

---

**Last Updated**: October 9, 2025
**ODBC Driver Version**: 17 (for Debian 11 compatibility)
**Database**: Azure SQL Server (existing data preserved)
