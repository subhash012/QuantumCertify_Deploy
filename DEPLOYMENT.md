# QuantumCertify Azure Deployment Guide

This guide will help you deploy QuantumCertify to Microsoft Azure using Docker containers.

## Prerequisites

### 0. Local Development Environment
Before deploying to Azure, ensure your application works locally:
```bash
# Backend setup
cd backend
cp .env.template .env
# Edit .env with your local configuration
pip install -r requirements.txt
python run_server.py

# Frontend setup (in another terminal)
cd frontend
npm install
npm start
```

### 1. Install Required Tools
- **Azure CLI**: [Download and install](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Docker Desktop**: [Download and install](https://www.docker.com/products/docker-desktop)
- **PowerShell 5.1+ or Bash** (depending on your preferred script)

### 2. Azure Account Setup
1. **Azure Subscription**: Ensure you have an active Azure subscription
2. **Sufficient Credits**: The deployment will create several Azure resources that incur costs
3. **Permissions**: You need Owner or Contributor permissions on the subscription

### 3. Environment Variables
Set the following environment variables before deployment:
```bash
# For Bash/Linux
export GEMINI_API_KEY="your_gemini_api_key_here"
export CONTACT_EMAIL="your.email@example.com"
export DEVELOPER_NAME="Your Name"
export SECRET_KEY="your-production-secret-key"

# For PowerShell/Windows
$env:GEMINI_API_KEY = "your_gemini_api_key_here"
$env:CONTACT_EMAIL = "your.email@example.com"
$env:DEVELOPER_NAME = "Your Name"
$env:SECRET_KEY = "your-production-secret-key"
```

## Quick Deployment

### Option 1: PowerShell Script (Windows)
```powershell
# Navigate to project directory
cd C:\Users\YourName\QuantumCertify

# Set environment variables
$env:GEMINI_API_KEY = "your_gemini_api_key_here"
$env:CONTACT_EMAIL = "your.email@example.com"
$env:DEVELOPER_NAME = "Your Name"
$env:SECRET_KEY = "your-production-secret-key"

# Run deployment script
.\deploy-azure.ps1
```

### Option 2: Bash Script (Linux/macOS/WSL)
```bash
# Navigate to project directory
cd /path/to/QuantumCertify

# Set environment variables
export GEMINI_API_KEY="your_gemini_api_key_here"
export CONTACT_EMAIL="your.email@example.com"
export DEVELOPER_NAME="Your Name"
export SECRET_KEY="your-production-secret-key"

# Make script executable and run
chmod +x deploy-azure.sh
./deploy-azure.sh
```

## Manual Step-by-Step Deployment

If you prefer to deploy manually or need more control:

### Step 1: Login to Azure
```bash
az login
```

### Step 2: Create Resource Group
```bash
az group create --name quantumcertify-rg --location eastus
```

### Step 3: Create Container Registry
```bash
az acr create \
    --resource-group quantumcertify-rg \
    --name quantumcertifyregistry \
    --sku Basic \
    --admin-enabled true
```

### Step 4: Build and Push Images
```bash
# Login to registry
az acr login --name quantumcertifyregistry

# Get login server
ACR_LOGIN_SERVER=$(az acr show --name quantumcertifyregistry --query loginServer -o tsv)

# Build and push backend
docker build -t $ACR_LOGIN_SERVER/quantumcertify-backend:latest ./backend
docker push $ACR_LOGIN_SERVER/quantumcertify-backend:latest

# Build and push frontend
docker build -t $ACR_LOGIN_SERVER/quantumcertify-frontend:latest ./frontend
docker push $ACR_LOGIN_SERVER/quantumcertify-frontend:latest
```

### Step 5: Create Azure SQL Database
```bash
# Create SQL Server
az sql server create \
    --resource-group quantumcertify-rg \
    --name quantumcertify-sql \
    --location eastus \
    --admin-user quantumadmin \
    --admin-password "YourSecurePassword123!"

# Create database
az sql db create \
    --resource-group quantumcertify-rg \
    --server quantumcertify-sql \
    --name QuantumCertifyDB \
    --edition Basic

# Allow Azure services
az sql server firewall-rule create \
    --resource-group quantumcertify-rg \
    --server quantumcertify-sql \
    --name AllowAzureServices \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0
```

### Step 6: Deploy Container Instances
```bash
# Deploy backend
az container create \
    --resource-group quantumcertify-rg \
    --name quantumcertify-backend \
    --image $ACR_LOGIN_SERVER/quantumcertify-backend:latest \
    --registry-login-server $ACR_LOGIN_SERVER \
    --registry-username $(az acr credential show --name quantumcertifyregistry --query username -o tsv) \
    --registry-password $(az acr credential show --name quantumcertifyregistry --query passwords[0].value -o tsv) \
    --dns-name-label quantumcertify-api \
    --ports 8000 \
    --secure-environment-variables \
        GEMINI_API_KEY=$GEMINI_API_KEY \
        DB_SERVER=quantumcertify-sql.database.windows.net \
        DB_NAME=QuantumCertifyDB \
        DB_USERNAME=quantumadmin \
        DB_PASSWORD=YourSecurePassword123! \
        DB_PORT=1433 \
        DB_DRIVER=SQL+Server \
        SECRET_KEY=$SECRET_KEY \
    --environment-variables \
        CONTACT_EMAIL=$CONTACT_EMAIL \
        DEVELOPER_NAME=$DEVELOPER_NAME \
        PROJECT_VERSION=2.0.0 \
        ALLOWED_ORIGINS=http://quantumcertify-app.eastus.azurecontainer.io \
        DEBUG=false

# Deploy frontend
az container create \
    --resource-group quantumcertify-rg \
    --name quantumcertify-frontend \
    --image $ACR_LOGIN_SERVER/quantumcertify-frontend:latest \
    --registry-login-server $ACR_LOGIN_SERVER \
    --registry-username $(az acr credential show --name quantumcertifyregistry --query username -o tsv) \
    --registry-password $(az acr credential show --name quantumcertifyregistry --query passwords[0].value -o tsv) \
    --dns-name-label quantumcertify-app \
    --ports 80 \
    --environment-variables \
        REACT_APP_API_URL=http://quantumcertify-api.eastus.azurecontainer.io:8000
```

## Alternative Deployment Options

### Option A: Azure Container Apps (Recommended for Production)
Azure Container Apps provides better scalability and features:
```bash
az containerapp env create \
    --name quantumcertify-env \
    --resource-group quantumcertify-rg \
    --location eastus

az containerapp create \
    --name quantumcertify-backend \
    --resource-group quantumcertify-rg \
    --environment quantumcertify-env \
    --image $ACR_LOGIN_SERVER/quantumcertify-backend:latest \
    --registry-server $ACR_LOGIN_SERVER \
    --target-port 8000 \
    --ingress external
```

### Option B: Azure Kubernetes Service (AKS)
For enterprise-grade deployments:
1. Create AKS cluster
2. Deploy using Kubernetes manifests
3. Configure ingress and scaling

### Option C: Azure App Service
Deploy as web applications:
1. Create App Service plans
2. Deploy containers to App Service
3. Configure application settings

## Environment Configuration

### Local Development Environment Variables
Create a `.env` file in the `backend` directory:
```properties
# Google Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key-here

# Database Configuration
DB_SERVER=localhost
DB_NAME=QuantumCertifyDB
DB_USERNAME=sa
DB_PASSWORD=your-secure-password
DB_PORT=1433
DB_DRIVER=SQL+Server

# Application Configuration
CONTACT_EMAIL=your.email@example.com
DEVELOPER_NAME=Your Name
PROJECT_VERSION=2.0.0

# Security Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DEBUG=true
```

### Production Environment Variables
For Azure deployment, ensure all environment variables are properly set in your deployment scripts.

## Post-Deployment Configuration

### 1. Database Setup
After deployment, initialize the database tables:
```bash
# Connect to your container and run initialization
az container exec \
    --resource-group quantumcertify-rg \
    --name quantumcertify-backend \
    --exec-command "python init_db.py"
```

### 2. Custom Domain (Optional)
To use a custom domain:
1. Configure DNS records
2. Set up SSL/TLS certificates
3. Update CORS settings

### 3. Monitoring and Logging
Enable Application Insights:
```bash
az monitor app-insights component create \
    --app quantumcertify-insights \
    --location eastus \
    --resource-group quantumcertify-rg
```

## Security Considerations

### 1. Environment Variables
- Never commit sensitive data to git
- Use Azure Key Vault for production secrets
- Rotate API keys regularly

### 2. Network Security
- Configure private networks for production
- Use Azure Front Door for DDoS protection
- Implement proper firewall rules

### 3. Database Security
- Use strong passwords
- Enable encryption at rest
- Configure backup policies

## Cost Optimization

### 1. Resource Sizing
- Start with Basic SKUs for development
- Scale up as needed for production
- Use Azure Cost Management to monitor expenses

### 2. Scheduled Scaling
- Scale down during off-hours
- Use Azure Automation for scheduled operations

## Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check container logs
az container logs --resource-group quantumcertify-rg --name quantumcertify-backend

# Check container events
az container show --resource-group quantumcertify-rg --name quantumcertify-backend
```

#### Database Connection Issues
- Verify firewall rules allow Azure services
- Check connection string format with all required parameters (DB_SERVER, DB_PORT, DB_DRIVER)
- Ensure credentials are correct (DB_USERNAME, DB_PASSWORD)
- Verify environment variables are properly set in container
- Check database connection pooling configuration

#### Image Pull Errors
- Verify registry credentials
- Check image exists in registry
- Ensure container has permission to pull

### Health Checks
```bash
# Test backend health
curl http://your-backend-url/health

# Test frontend
curl http://your-frontend-url/health
```

## Scaling and Performance

### 1. Container Instance Scaling
Azure Container Instances don't auto-scale. Consider:
- Multiple container groups
- Load balancers
- Container Apps for auto-scaling

### 2. Database Performance
- Monitor DTU usage
- Consider higher service tiers
- Implement connection pooling

## Backup and Recovery

### 1. Database Backups
Azure SQL Database provides automatic backups

### 2. Container Images
- Tag images with versions
- Keep multiple versions in registry
- Implement CI/CD for updates

## Monitoring

### 1. Application Monitoring
- Enable Application Insights
- Set up alerts for failures
- Monitor performance metrics
- Track certificate analysis requests
- Monitor database connection health
- Track API response times and error rates
- Monitor Gemini AI API usage and costs

### 2. Infrastructure Monitoring
- Use Azure Monitor
- Set up resource health alerts
- Monitor costs

## Next Steps

1. **Set up CI/CD pipeline** using Azure DevOps or GitHub Actions
2. **Configure auto-scaling** with Azure Container Apps
3. **Implement proper logging** and monitoring
4. **Set up staging environment** for testing
5. **Configure backup and disaster recovery**

## Support

For issues with this deployment:
1. Check the troubleshooting section
2. Review Azure documentation
3. Create an issue in the project repository