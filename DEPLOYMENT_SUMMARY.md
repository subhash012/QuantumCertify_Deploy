# 🚀 QuantumCertify Azure Deployment - Comple### 1. Prepare Environment
```powershell
# In PowerShell, set your environment variables
$env:GEMINI_API_KEY = "your_actual_gemini_api_key_here"
$env:CONTACT_EMAIL = "your.email@example.com"
$env:DEVELOPER_NAME = "Your Name"

# Navigate to your project directory
cd C:\Users\VSubhash\QuantumCertify
```

## 📋 What I've Prepared for You

I've created a complete Docker-based deployment solution for QuantumCertify on Azure. Here's everything that's ready:

### ✅ Docker Configuration Files
- `backend/Dockerfile` - Production-ready Python FastAPI container
- `frontend/Dockerfile` - Nginx-based React container with multi-stage build
- `frontend/nginx.conf` - Optimized Nginx configuration
- `docker-compose.yml` - Local development setup
- `docker-compose.prod.yml` - Production deployment configuration

### ✅ Azure Deployment Scripts
- `deploy-azure.ps1` - Complete PowerShell deployment script
- `deploy-azure.sh` - Bash deployment script for Linux/macOS
- `.github/workflows/deploy-azure.yml` - GitHub Actions CI/CD pipeline

### ✅ Documentation
- `AZURE_SETUP.md` - Step-by-step Azure setup instructions
- `DEPLOYMENT.md` - Comprehensive deployment guide
- `.env.azure.template` - Environment variables template

## 🛠️ What You Need to Install

### 1. Docker Desktop
**Download and Install:**
- Go to [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
- Download Docker Desktop for Windows
- Install and restart your computer
- Start Docker Desktop

### 2. Azure CLI
**Download and Install:**
- Go to [https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows)
- Download the MSI installer
- Install and restart PowerShell

### 3. Azure Account
**If you don't have one:**
- Sign up at [https://azure.microsoft.com/free](https://azure.microsoft.com/free)
- Get $200 free credits for new accounts

## 🚀 Deployment Steps You Need to Do

### Step 1: Prepare Environment
```powershell
# In PowerShell, set your Gemini API key
$env:GEMINI_API_KEY = "your_actual_gemini_api_key_here"

# Navigate to your project directory
cd C:\Users\VSubhash\QuantumCertify
```

### Step 2: Login to Azure
```powershell
# Login to Azure (will open browser)
az login

# Verify login
az account show
```

### Step 3: Run Deployment
```powershell
# Run the automated deployment script
.\deploy-azure.ps1
```

**The script will automatically:**
1. ✅ Create resource group `quantumcertify-rg`
2. ✅ Create Azure Container Registry
3. ✅ Build and push Docker images
4. ✅ Create Azure SQL Database
5. ✅ Deploy containers to Azure Container Instances
6. ✅ Configure networking and DNS

## 💰 Expected Azure Costs

**Monthly costs (approximate):**
- Container Instances: $30-50
- SQL Database (Basic): $5-15
- Container Registry: $5
- Total: ~$40-70/month

## 📱 Alternative: Manual Azure Portal Setup

If you prefer using Azure Portal instead of scripts:

### 1. Create Resources in Azure Portal
1. **Resource Group**: Create `quantumcertify-rg` in East US
2. **Container Registry**: Create with Basic SKU, enable admin access
3. **SQL Database**: Create with Basic pricing tier
4. **Container Instances**: Create two - one for frontend, one for backend

### 2. Upload Images to Registry
You'll need to build and push images manually using Docker commands.

## 🔧 Azure Resources the Script Creates

### Resource Group: `quantumcertify-rg`
- **Location**: East US
- **Contains**: All QuantumCertify resources

### Container Registry: `quantumcertifyregistry[timestamp]`
- **SKU**: Basic
- **Images**: quantumcertify-frontend, quantumcertify-backend
- **Admin Access**: Enabled

### SQL Database
- **Server**: `quantumcertify-sql-[timestamp].database.windows.net`
- **Database**: `QuantumCertifyDB`
- **Pricing**: Basic tier
- **Firewall**: Allows Azure services

### Container Instances
- **Frontend**: `quantumcertify-app` (Port 80)
- **Backend**: `quantumcertify-app-backend` (Port 8000)
- **DNS**: Unique labels generated automatically

## 🌐 After Deployment

### Your URLs will be:
- **Frontend**: `http://quantumcertify-[timestamp].eastus.azurecontainer.io`
- **Backend API**: `http://quantumcertify-[timestamp]-api.eastus.azurecontainer.io:8000`
- **API Docs**: `http://quantumcertify-[timestamp]-api.eastus.azurecontainer.io:8000/docs`

### Initialize Database
```powershell
# Run this after deployment to create database tables
az container exec `
  --resource-group quantumcertify-rg `
  --name quantumcertify-app-backend `
  --exec-command "python init_db.py"
```

## 🔐 Security Configuration

### Database Security
- Server firewall allows only Azure services
- Strong generated passwords
- Connection encrypted in transit

### Container Security
- Non-root users in containers
- Environment variables for secrets
- Health checks enabled

### Network Security
- CORS properly configured
- Security headers in Nginx
- HTTPS ready (certificate needed)

## 📊 Monitoring Your Deployment

### Check Container Status
```powershell
# Check if containers are running
az container show --resource-group quantumcertify-rg --name quantumcertify-app
az container show --resource-group quantumcertify-rg --name quantumcertify-app-backend

# View container logs
az container logs --resource-group quantumcertify-rg --name quantumcertify-app-backend
```

### Test Deployment
```powershell
# Test backend health
curl http://your-backend-url/health

# Test frontend
curl http://your-frontend-url
```

## 🚨 Troubleshooting Guide

### Common Issues

#### 1. "Docker not found"
**Solution**: Install Docker Desktop and ensure it's running

#### 2. "Azure CLI not found"  
**Solution**: Install Azure CLI and restart PowerShell

#### 3. "Container failed to start"
**Solution**: Check container logs with `az container logs`

#### 4. "Database connection failed"
**Solution**: Verify database firewall allows Azure services

#### 5. "Image pull failed"
**Solution**: Check container registry credentials

### Getting Logs
```powershell
# Backend logs
az container logs --resource-group quantumcertify-rg --name quantumcertify-app-backend

# Frontend logs  
az container logs --resource-group quantumcertify-rg --name quantumcertify-app
```

## 🔄 Updating Your Application

### For Code Changes
1. Make changes to your code
2. Run deployment script again
3. New images will be built and deployed

### For Configuration Changes
1. Update environment variables in deployment script
2. Restart containers or redeploy

## 🎯 Next Steps After Deployment

### 1. Custom Domain (Optional)
- Register a domain name
- Create CNAME records
- Configure SSL certificates

### 2. CI/CD Pipeline
- Use the provided GitHub Actions workflow
- Set up automated deployments on code changes

### 3. Monitoring
- Set up Application Insights
- Configure alerts for errors
- Monitor costs and usage

### 4. Scaling
- Consider Azure Container Apps for auto-scaling
- Upgrade database tier as needed
- Implement load balancing

## 📞 Support

**If you encounter issues:**
1. Check the troubleshooting section above
2. Review Azure Portal for error messages
3. Check container logs for detailed error information
4. Verify all environment variables are set correctly

**The deployment script includes detailed logging, so you'll see exactly what's happening at each step.**

## 📚 Additional Resources

- [Azure Container Instances Pricing](https://azure.microsoft.com/pricing/details/container-instances/)
- [Azure SQL Database Pricing](https://azure.microsoft.com/pricing/details/sql-database/)
- [Docker Documentation](https://docs.docker.com/)
- [Azure CLI Reference](https://docs.microsoft.com/en-us/cli/azure/)

---

**Ready to Deploy?** Just follow the steps above, and your QuantumCertify application will be running on Azure in about 15-20 minutes! 🚀