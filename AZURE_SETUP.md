# Azure Deployment Setup Instructions

Follow these steps to set up QuantumCertify deployment on Microsoft Azure.

## 🚀 Quick Setup (Automated)

### Prerequisites
1. **Azure Subscription** with sufficient credits
2. **Azure CLI** installed and configured
3. **Docker Desktop** installed and running
4. **Gemini API Key** from Google AI Studio

### Step 1: Clone and Setup
```bash
git clone https://github.com/yourusername/QuantumCertify.git
cd QuantumCertify
```

### Step 2: Set Environment Variables
```powershell
# Windows PowerShell
$env:GEMINI_API_KEY = "your_gemini_api_key_here"
```

### Step 3: Run Deployment Script
```powershell
# Windows
.\deploy-azure.ps1

# Linux/macOS
chmod +x deploy-azure.sh
./deploy-azure.sh
```

The script will automatically:
- Create Azure resource group
- Set up Container Registry
- Build and push Docker images
- Create Azure SQL Database
- Deploy containers to Azure Container Instances

## 📋 Manual Setup Instructions

If you need to set up Azure resources manually, follow the detailed guide in `DEPLOYMENT.md`.

## 🔧 Azure Resources You Need to Create

### 1. Azure Account Setup
- **Azure Subscription**: Sign up at [azure.microsoft.com](https://azure.microsoft.com)
- **Resource Group**: Container for all QuantumCertify resources
- **Location**: Choose region (recommended: East US, West Europe)

### 2. Container Registry
- **Name**: `quantumcertifyregistry` (must be globally unique)
- **SKU**: Basic (for development) or Standard (for production)
- **Admin Access**: Enabled

### 3. SQL Database
- **Server Name**: `quantumcertify-sql-[timestamp]`
- **Database Name**: `QuantumCertifyDB`
- **Pricing Tier**: Basic (DTU-based) or S0 (for development)
- **Firewall**: Allow Azure services

### 4. Container Instances
- **Backend Container**: 1 vCPU, 1.5GB memory
- **Frontend Container**: 0.5 vCPU, 1GB memory
- **Networking**: Public IP with DNS labels

## 🔑 Required Secrets and Environment Variables

### For Local Development
Create `.env` file in backend directory:
```
DB_SERVER=your-server.database.windows.net
DB_NAME=QuantumCertifyDB
DB_USERNAME=your-username
DB_PASSWORD=your-password
GEMINI_API_KEY=your-gemini-api-key
```

### For GitHub Actions (if using CI/CD)
Add these secrets to your GitHub repository:
- `AZURE_CREDENTIALS`: Service principal credentials JSON
- `DB_SERVER`: Azure SQL server name
- `DB_NAME`: Database name
- `DB_USERNAME`: Database username
- `DB_PASSWORD`: Database password
- `GEMINI_API_KEY`: Google AI API key

## 💰 Cost Estimation

Approximate monthly costs (USD):
- **Container Instances**: $30-50
- **SQL Database (Basic)**: $5-15
- **Container Registry**: $5
- **Storage**: $2-5
- **Total**: ~$40-75/month

## 🛠️ What You Need to Do in Azure Portal

### 1. Create Service Principal (for GitHub Actions)
```bash
az ad sp create-for-rbac \
  --name "quantumcertify-deploy" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/quantumcertify-rg \
  --sdk-auth
```

### 2. Configure Database Firewall
1. Go to Azure Portal > SQL databases
2. Select your database > Firewalls and virtual networks
3. Add your IP address for management access
4. Ensure "Allow Azure services" is enabled

### 3. Monitor Resources
1. Set up billing alerts
2. Configure monitoring and logs
3. Review security recommendations

## 🔧 Post-Deployment Configuration

### 1. Initialize Database
After deployment, run database initialization:
```bash
# Using Azure CLI
az container exec \
  --resource-group quantumcertify-rg \
  --name quantumcertify-backend \
  --exec-command "python init_db.py"
```

### 2. Test Deployment
- **Frontend**: Visit your container instance URL
- **Backend API**: Test `/health` endpoint
- **Database**: Verify connection through API

### 3. Configure Custom Domain (Optional)
1. Register domain name
2. Create CNAME record pointing to container instance
3. Configure SSL certificate

## 🚨 Important Security Notes

### 1. Environment Variables
- Never commit secrets to git
- Use Azure Key Vault for production
- Rotate API keys regularly

### 2. Network Security
- Consider private networks for production
- Implement proper firewall rules
- Use Azure Front Door for DDoS protection

### 3. Database Security
- Use strong passwords
- Enable encryption at rest
- Configure backup policies
- Limit database access to Azure services only

## 📞 Support and Troubleshooting

### Common Issues
1. **Container won't start**: Check logs in Azure Portal
2. **Database connection failed**: Verify firewall rules
3. **Image pull failed**: Check registry credentials

### Getting Help
1. Check `DEPLOYMENT.md` for detailed troubleshooting
2. Review Azure documentation
3. Create issue in GitHub repository

### Useful Commands
```bash
# Check container logs
az container logs --resource-group quantumcertify-rg --name quantumcertify-backend

# Restart container
az container restart --resource-group quantumcertify-rg --name quantumcertify-backend

# Check resource status
az resource list --resource-group quantumcertify-rg --output table
```

## 🔄 Updates and Maintenance

### 1. Application Updates
- Use GitHub Actions for automated deployments
- Tag images with version numbers
- Test in staging environment first

### 2. Security Updates
- Regularly update base images
- Monitor for security vulnerabilities
- Apply OS and dependency patches

### 3. Scaling
- Monitor resource usage
- Consider Azure Container Apps for auto-scaling
- Upgrade database tier as needed

## 📚 Additional Resources

- [Azure Container Instances Documentation](https://docs.microsoft.com/en-us/azure/container-instances/)
- [Azure SQL Database Documentation](https://docs.microsoft.com/en-us/azure/sql-database/)
- [Azure Container Registry Documentation](https://docs.microsoft.com/en-us/azure/container-registry/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)