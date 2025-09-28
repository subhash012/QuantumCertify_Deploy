# QuantumCertify Production Deployment for quantumcertify.tech
# Azure App Service Deployment Script

param(
    [string]$ResourceGroupName = "quantumcertify-prod",
    [string]$AppName = "quantumcertify-app",
    [string]$SqlServerName = "quantumcertify-sqlserver",
    [string]$Location = "East US",
    [string]$DomainName = "quantumcertify.tech",
    [string]$SqlAdminUser = "quantumadmin",
    [Parameter(Mandatory=$true)]
    [string]$SqlAdminPassword,
    [Parameter(Mandatory=$true)]
    [string]$SecretKey,
    [Parameter(Mandatory=$true)]
    [string]$GeminiApiKey
)

Write-Host "🚀 QuantumCertify Production Deployment" -ForegroundColor Green
Write-Host "🌐 Domain: $DomainName" -ForegroundColor Cyan
Write-Host "📦 Resource Group: $ResourceGroupName" -ForegroundColor Yellow
Write-Host "⚙️ App Name: $AppName" -ForegroundColor Yellow

# Validate required parameters
if ([string]::IsNullOrEmpty($SqlAdminPassword) -or $SqlAdminPassword.Length -lt 12) {
    Write-Host "❌ Error: SQL Admin Password must be at least 12 characters" -ForegroundColor Red
    exit 1
}

if ([string]::IsNullOrEmpty($SecretKey) -or $SecretKey.Length -lt 32) {
    Write-Host "❌ Error: Secret Key must be at least 32 characters" -ForegroundColor Red
    exit 1
}

if ([string]::IsNullOrEmpty($GeminiApiKey)) {
    Write-Host "❌ Error: Gemini API Key is required" -ForegroundColor Red
    exit 1
}

try {
    # Step 1: Login to Azure
    Write-Host "🔐 Logging into Azure..." -ForegroundColor Yellow
    $loginResult = az login --output json | ConvertFrom-Json
    if ($LASTEXITCODE -ne 0) {
        throw "Azure login failed"
    }
    Write-Host "✅ Logged in as: $($loginResult.user.name)" -ForegroundColor Green

    # Step 2: Create Resource Group
    Write-Host "📦 Creating resource group: $ResourceGroupName..." -ForegroundColor Yellow
    az group create --name $ResourceGroupName --location $Location --output none
    if ($LASTEXITCODE -ne 0) {
        throw "Resource group creation failed"
    }
    Write-Host "✅ Resource group created successfully" -ForegroundColor Green

    # Step 3: Create App Service Plan (Production P1V2)
    Write-Host "⚙️ Creating App Service Plan..." -ForegroundColor Yellow
    az appservice plan create `
        --name "$AppName-plan" `
        --resource-group $ResourceGroupName `
        --location $Location `
        --sku P1V2 `
        --is-linux `
        --output none
    
    if ($LASTEXITCODE -ne 0) {
        throw "App Service Plan creation failed"
    }
    Write-Host "✅ App Service Plan created successfully" -ForegroundColor Green

    # Step 4: Create Web App
    Write-Host "🐍 Creating Web App with Python runtime..." -ForegroundColor Yellow
    az webapp create `
        --resource-group $ResourceGroupName `
        --plan "$AppName-plan" `
        --name $AppName `
        --runtime "PYTHON|3.11" `
        --output none
    
    if ($LASTEXITCODE -ne 0) {
        throw "Web App creation failed"
    }
    Write-Host "✅ Web App created successfully" -ForegroundColor Green

    # Step 5: Create SQL Server
    Write-Host "🗄️ Creating SQL Server..." -ForegroundColor Yellow
    az sql server create `
        --name $SqlServerName `
        --resource-group $ResourceGroupName `
        --location $Location `
        --admin-user $SqlAdminUser `
        --admin-password $SqlAdminPassword `
        --output none
    
    if ($LASTEXITCODE -ne 0) {
        throw "SQL Server creation failed"
    }
    Write-Host "✅ SQL Server created successfully" -ForegroundColor Green

    # Step 6: Create SQL Database
    Write-Host "💾 Creating SQL Database..." -ForegroundColor Yellow
    az sql db create `
        --resource-group $ResourceGroupName `
        --server $SqlServerName `
        --name "quantumcertify" `
        --service-objective S2 `
        --output none
    
    if ($LASTEXITCODE -ne 0) {
        throw "SQL Database creation failed"
    }
    Write-Host "✅ SQL Database created successfully" -ForegroundColor Green

    # Step 7: Configure SQL Server Firewall
    Write-Host "🔥 Configuring SQL Server firewall..." -ForegroundColor Yellow
    
    # Allow Azure services
    az sql server firewall-rule create `
        --resource-group $ResourceGroupName `
        --server $SqlServerName `
        --name "AllowAzureServices" `
        --start-ip-address 0.0.0.0 `
        --end-ip-address 0.0.0.0 `
        --output none
    
    # Allow your current IP
    $myIp = (Invoke-RestMethod -Uri "https://api.ipify.org").Trim()
    az sql server firewall-rule create `
        --resource-group $ResourceGroupName `
        --server $SqlServerName `
        --name "AllowCurrentIP" `
        --start-ip-address $myIp `
        --end-ip-address $myIp `
        --output none
    
    Write-Host "✅ SQL Server firewall configured" -ForegroundColor Green

    # Step 8: Enable HTTPS Only
    Write-Host "🔒 Enabling HTTPS-only access..." -ForegroundColor Yellow
    az webapp update `
        --resource-group $ResourceGroupName `
        --name $AppName `
        --https-only true `
        --output none
    
    if ($LASTEXITCODE -ne 0) {
        throw "HTTPS configuration failed"
    }
    Write-Host "✅ HTTPS-only enabled" -ForegroundColor Green

    # Step 9: Configure App Settings
    Write-Host "⚙️ Configuring application settings..." -ForegroundColor Yellow
    
    $dbConnectionString = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:$SqlServerName.database.windows.net,1433;Database=quantumcertify;Uid=$SqlAdminUser;Pwd=$SqlAdminPassword;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    
    az webapp config appsettings set `
        --resource-group $ResourceGroupName `
        --name $AppName `
        --settings `
            "DOMAIN_NAME=$DomainName" `
            "FRONTEND_URL=https://$DomainName" `
            "BACKEND_URL=https://api.$DomainName" `
            "API_BASE_URL=https://api.$DomainName" `
            "DB_SERVER=$SqlServerName.database.windows.net" `
            "DB_NAME=quantumcertify" `
            "DB_USERNAME=$SqlAdminUser" `
            "DB_PASSWORD=$SqlAdminPassword" `
            "DB_PORT=1433" `
            "DB_DRIVER=ODBC Driver 18 for SQL Server" `
            "SECRET_KEY=$SecretKey" `
            "GEMINI_API_KEY=$GeminiApiKey" `
            "ENVIRONMENT=production" `
            "DEBUG=false" `
            "FORCE_HTTPS=true" `
            "SSL_REDIRECT=true" `
            "SECURE_COOKIES=true" `
            "ALLOWED_ORIGINS=https://$DomainName,https://www.$DomainName,https://api.$DomainName" `
            "LOG_LEVEL=INFO" `
            "PYTHONPATH=/home/site/wwwroot" `
        --output none
    
    if ($LASTEXITCODE -ne 0) {
        throw "App settings configuration failed"
    }
    Write-Host "✅ Application settings configured" -ForegroundColor Green

    # Step 10: Configure Custom Domains (these will need DNS setup)
    Write-Host "🌐 Preparing custom domain configuration..." -ForegroundColor Yellow
    Write-Host "⚠️ Note: Custom domain binding requires DNS records to be set up first" -ForegroundColor Yellow

    # Get the default domain for DNS setup instructions
    $defaultDomain = "$AppName.azurewebsites.net"

    Write-Host ""
    Write-Host "✅ 🎉 DEPLOYMENT COMPLETED SUCCESSFULLY! 🎉" -ForegroundColor Green -BackgroundColor DarkGreen
    Write-Host ""
    Write-Host "📋 NEXT STEPS - DNS Configuration:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1️⃣ Configure DNS records in your .TECH domain panel:" -ForegroundColor White
    Write-Host "   Record Type: CNAME" -ForegroundColor Gray
    Write-Host "   Name: @" -ForegroundColor Gray
    Write-Host "   Value: $defaultDomain" -ForegroundColor Yellow
    Write-Host "   TTL: 300" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   Record Type: CNAME" -ForegroundColor Gray
    Write-Host "   Name: www" -ForegroundColor Gray
    Write-Host "   Value: $defaultDomain" -ForegroundColor Yellow
    Write-Host "   TTL: 300" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   Record Type: CNAME" -ForegroundColor Gray
    Write-Host "   Name: api" -ForegroundColor Gray
    Write-Host "   Value: $defaultDomain" -ForegroundColor Yellow
    Write-Host "   TTL: 300" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2️⃣ After DNS propagation (24-48 hours), add custom domains:" -ForegroundColor White
    Write-Host "   az webapp config hostname add --webapp-name $AppName --resource-group $ResourceGroupName --hostname $DomainName" -ForegroundColor Gray
    Write-Host "   az webapp config hostname add --webapp-name $AppName --resource-group $ResourceGroupName --hostname www.$DomainName" -ForegroundColor Gray
    Write-Host "   az webapp config hostname add --webapp-name $AppName --resource-group $ResourceGroupName --hostname api.$DomainName" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3️⃣ Deploy your application code to:" -ForegroundColor White
    Write-Host "   https://$defaultDomain" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📊 DEPLOYMENT SUMMARY:" -ForegroundColor Cyan
    Write-Host "   🌐 App Service: $AppName" -ForegroundColor White
    Write-Host "   🗄️ SQL Server: $SqlServerName.database.windows.net" -ForegroundColor White
    Write-Host "   📦 Resource Group: $ResourceGroupName" -ForegroundColor White
    Write-Host "   🔒 HTTPS: Enabled" -ForegroundColor White
    Write-Host "   🤖 AI: Gemini Integration Ready" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Your QuantumCertify application will be available at:" -ForegroundColor Green
    Write-Host "   https://$DomainName (after DNS setup)" -ForegroundColor Cyan
    Write-Host "   https://www.$DomainName (after DNS setup)" -ForegroundColor Cyan
    Write-Host "   https://api.$DomainName (after DNS setup)" -ForegroundColor Cyan
    Write-Host "   https://$defaultDomain (available now)" -ForegroundColor Yellow
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "❌ DEPLOYMENT FAILED!" -ForegroundColor Red -BackgroundColor DarkRed
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check Azure CLI is installed and updated" -ForegroundColor White
    Write-Host "2. Verify you have sufficient Azure permissions" -ForegroundColor White
    Write-Host "3. Ensure all required parameters are provided" -ForegroundColor White
    Write-Host "4. Check Azure subscription has available quota" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Optional: Test deployment
Write-Host "🧪 Testing deployment..." -ForegroundColor Yellow
try {
    $healthCheck = Invoke-RestMethod -Uri "https://$AppName.azurewebsites.net/health" -TimeoutSec 30
    Write-Host "✅ Health check passed: $($healthCheck.status)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Health check failed (this is normal if app code is not deployed yet)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 DEPLOYMENT COMPLETED! Ready for quantumcertify.tech configuration!" -ForegroundColor Green