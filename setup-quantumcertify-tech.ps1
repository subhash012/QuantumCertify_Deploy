# 🚀 Quick Setup Script for QuantumCertify.tech
# This script generates secure keys and deploys your application

Write-Host ""
Write-Host "🌐 QuantumCertify.tech Quick Setup" -ForegroundColor Cyan -BackgroundColor DarkBlue
Write-Host "=================================" -ForegroundColor Cyan -BackgroundColor DarkBlue
Write-Host ""

# Check prerequisites
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow

# Check Azure CLI
try {
    $azVersion = az --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Azure CLI is installed" -ForegroundColor Green
    } else {
        throw "Azure CLI not found"
    }
} catch {
    Write-Host "❌ Azure CLI is required. Install from: https://docs.microsoft.com/cli/azure/install-azure-cli" -ForegroundColor Red
    exit 1
}

# Generate secure keys
Write-Host ""
Write-Host "🔐 Generating secure keys..." -ForegroundColor Yellow

# Generate 64-character secret key with mixed case letters, numbers, and symbols
$secretKeyChars = (65..90) + (97..122) + (48..57) + (33,35,36,37,38,42,43,45,61,63,64,95)
$SecretKey = -join ($secretKeyChars | Get-Random -Count 64 | ForEach-Object {[char]$_})

# Generate secure SQL password (16 characters)
$sqlPasswordChars = (65..90) + (97..122) + (48..57) + (35,36,37,38,42,43,45,61,63,64)
$SqlPassword = -join ($sqlPasswordChars | Get-Random -Count 16 | ForEach-Object {[char]$_})

Write-Host "✅ Secure keys generated" -ForegroundColor Green

# Display generated keys
Write-Host ""
Write-Host "📋 Generated Configuration:" -ForegroundColor Cyan
Write-Host "Secret Key: $SecretKey" -ForegroundColor Yellow
Write-Host "SQL Password: $SqlPassword" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️ IMPORTANT: Save these keys securely!" -ForegroundColor Red -BackgroundColor Yellow
Write-Host ""

# Prompt for Gemini API key
$GeminiApiKey = Read-Host "🤖 Enter your Google Gemini API Key"

if ([string]::IsNullOrWhiteSpace($GeminiApiKey)) {
    Write-Host "❌ Gemini API Key is required for AI features" -ForegroundColor Red
    Write-Host "📖 Get your key at: https://makersuite.google.com/app/apikey" -ForegroundColor Yellow
    exit 1
}

# Confirm deployment
Write-Host ""
Write-Host "🚀 Ready to deploy QuantumCertify to quantumcertify.tech" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Deployment Details:" -ForegroundColor Cyan
Write-Host "   Domain: quantumcertify.tech" -ForegroundColor White
Write-Host "   Resource Group: quantumcertify-prod" -ForegroundColor White  
Write-Host "   App Service: quantumcertify-app" -ForegroundColor White
Write-Host "   SQL Server: quantumcertify-sqlserver" -ForegroundColor White
Write-Host "   Estimated Cost: ~$104/month" -ForegroundColor White
Write-Host ""

$confirmation = Read-Host "Continue with deployment? (y/N)"

if ($confirmation -ne "y" -and $confirmation -ne "Y") {
    Write-Host "❌ Deployment cancelled" -ForegroundColor Yellow
    exit 0
}

# Run the deployment
Write-Host ""
Write-Host "🚀 Starting Azure deployment..." -ForegroundColor Green
Write-Host "⏱️ This will take 5-10 minutes..." -ForegroundColor Yellow
Write-Host ""

try {
    # Execute the deployment script
    $deploymentScript = ".\deploy-quantumcertify-tech.ps1"
    
    if (-not (Test-Path $deploymentScript)) {
        throw "Deployment script not found: $deploymentScript"
    }
    
    & $deploymentScript -SqlAdminPassword $SqlPassword -SecretKey $SecretKey -GeminiApiKey $GeminiApiKey
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green -BackgroundColor DarkGreen
        Write-Host ""
        Write-Host "📋 NEXT STEPS:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1️⃣ Configure DNS records in your .TECH domain panel:" -ForegroundColor White
        Write-Host "   Add CNAME records pointing to: quantumcertify-app.azurewebsites.net" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "2️⃣ Wait 24-48 hours for DNS propagation" -ForegroundColor White
        Write-Host ""
        Write-Host "3️⃣ Add custom domains to Azure App Service" -ForegroundColor White
        Write-Host ""
        Write-Host "4️⃣ Deploy your application code" -ForegroundColor White
        Write-Host ""
        Write-Host "📖 Full instructions: QUANTUMCERTIFY_TECH_DEPLOYMENT_GUIDE.md" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🌐 Temporary URL (available now): https://quantumcertify-app.azurewebsites.net" -ForegroundColor Yellow
        Write-Host "🎯 Final URL (after DNS): https://quantumcertify.tech" -ForegroundColor Green
        
        # Save configuration
        $config = @{
            "deployment_date" = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            "domain" = "quantumcertify.tech"
            "azure_app" = "quantumcertify-app.azurewebsites.net"
            "resource_group" = "quantumcertify-prod"
            "sql_server" = "quantumcertify-sqlserver.database.windows.net"
            "sql_admin_user" = "quantumadmin"
            "sql_admin_password" = $SqlPassword
            "secret_key" = $SecretKey
            "gemini_api_key" = $GeminiApiKey
        }
        
        $config | ConvertTo-Json | Out-File "deployment-config.json"
        Write-Host ""
        Write-Host "💾 Configuration saved to: deployment-config.json" -ForegroundColor Green
        Write-Host "🔐 Keep this file secure - it contains sensitive keys!" -ForegroundColor Red
        
    } else {
        throw "Deployment script failed with exit code: $LASTEXITCODE"
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ DEPLOYMENT FAILED!" -ForegroundColor Red -BackgroundColor DarkRed
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check Azure CLI is logged in: az login" -ForegroundColor White
    Write-Host "2. Verify Azure subscription permissions" -ForegroundColor White
    Write-Host "3. Check internet connectivity" -ForegroundColor White
    Write-Host "4. Review error messages above" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "🏁 Setup script completed!" -ForegroundColor Green