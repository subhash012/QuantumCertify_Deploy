# 🎯 QuantumCertify Deployment Quick Reference

## 📱 One-Page Navigation Guide

### 🏁 Quick Start (30 seconds)
```powershell
# 1. Set your variables
$env:GEMINI_API_KEY = "your-api-key-here"
$env:CONTACT_EMAIL = "your.email@example.com" 
$env:DEVELOPER_NAME = "Your Name"
$env:SECRET_KEY = "your-secret-123"

# 2. Deploy
cd "C:\Users\VSubhash\QuantumCertify"
az login
.\deploy-azure.ps1
```

### 🎯 What You Need Right Now
| Item | Where to Get It | Time Needed |
|------|----------------|-------------|
| Azure Account | [azure.microsoft.com/free](https://azure.microsoft.com/free/) | 10 min |
| Gemini API Key | [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey) | 5 min |
| Azure CLI | [aka.ms/installazurecliwindows](https://aka.ms/installazurecliwindows) | 10 min |
| Docker Desktop | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) | 15 min |

### 📋 Pre-Flight Checklist
- [ ] Azure account created with $200 free credits
- [ ] Gemini API key copied to notepad
- [ ] Azure CLI installed and computer restarted
- [ ] Docker Desktop installed and running
- [ ] PowerShell can run `az --version` and `docker --version`

### 🚀 Deployment Status Tracker
**Phase 1: Setup (30 min)**
- [ ] Azure account ✓
- [ ] Tools installed ✓
- [ ] API keys ready ✓

**Phase 2: Deploy (20 min)**
- [ ] Environment variables set ✓
- [ ] Azure login successful ✓
- [ ] Script running ✓

**Phase 3: Test (5 min)**
- [ ] URLs received ✓
- [ ] Frontend loads ✓
- [ ] Application works ✓

### 🎉 Success URLs
After deployment, look for:
```
Frontend: http://quantumcertify-app-[random].eastus.azurecontainer.io
Backend:  http://quantumcertify-api-[random].eastus.azurecontainer.io:8000
```

### 🔧 Essential Commands
```powershell
# Check status
az container list --resource-group quantumcertify-rg --output table

# View logs
az container logs --resource-group quantumcertify-rg --name quantumcertify-frontend

# Restart app
az container restart --resource-group quantumcertify-rg --name quantumcertify-frontend

# Stop to save money
az container stop --resource-group quantumcertify-rg --name quantumcertify-frontend

# Delete everything
az group delete --name quantumcertify-rg --yes
```

### 🚨 Quick Fixes
| Problem | Solution |
|---------|----------|
| "az not found" | Restart computer, reinstall Azure CLI |
| "Docker not running" | Start Docker Desktop, wait for green light |
| "API key invalid" | Get new key from Google Gemini |
| "Container failed" | Check logs, restart container |
| "Can't access app" | Wait 5 minutes, try again |

### 💰 Cost Monitor
- **Daily**: ~$2-4 while running
- **Monthly**: ~$50-80 if left running 24/7
- **Save money**: Stop containers when not needed

### 📞 Emergency Contacts
- **Azure Status**: [status.azure.com](https://status.azure.com/)
- **Azure Support**: Azure Portal → Help + Support
- **Documentation**: See `COMPLETE_DEPLOYMENT_GUIDE.md`

---

## 🎓 What You Just Built

You deployed a **professional-grade cloud application** with:
- ✅ **React Frontend** - Modern web interface
- ✅ **FastAPI Backend** - High-performance API server  
- ✅ **SQL Database** - Secure data storage
- ✅ **AI Integration** - Google Gemini AI features
- ✅ **Container Orchestration** - Docker + Azure
- ✅ **Production Security** - Encrypted connections, secrets management
- ✅ **Scalable Architecture** - Can handle thousands of users

**This is enterprise-level infrastructure!** 🏆

---

*Keep this page bookmarked for quick reference! 📌*