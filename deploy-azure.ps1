# QuantumCertify Azure Deployment Script (PowerShell)
# This script automates the deployment to Azure Container Instances

param(
    [string]$ResourceGroup = "quantumcertify-rg",
    [string]$Location = "eastus",
    [string]$RegistryName = "quantumcertifyregistry",
    [string]$ContainerGroupName = "quantumcertify-app",
    [string]$DnsNameLabel = "quantumcertify-$(Get-Date -Format 'yyyyMMddHHmm')"
)

# Function to write colored output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Step($message) {
    Write-ColorOutput Blue "==> $message"
}

function Write-Success($message) {
    Write-ColorOutput Green "✓ $message"
}

function Write-Warning($message) {
    Write-ColorOutput Yellow "⚠ $message"
}

function Write-Error($message) {
    Write-ColorOutput Red "✗ $message"
}

# Check if Azure CLI is installed
function Test-AzureCLI {
    Write-Step "Checking Azure CLI installation..."
    try {
        $null = az --version
        Write-Success "Azure CLI found"
        return $true
    }
    catch {
        Write-Error "Azure CLI is not installed. Please install it first:"
        Write-Output "https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        return $false
    }
}

# Check Azure login status
function Test-AzureLogin {
    Write-Step "Checking Azure login status..."
    try {
        $account = az account show 2>$null | ConvertFrom-Json
        if ($account) {
            Write-Success "Logged in to subscription: $($account.name) ($($account.id))"
            return $true
        }
    }
    catch {
        Write-Warning "Not logged in to Azure. Please log in:"
        az login
        return $true
    }
    return $false
}

# Create resource group
function New-ResourceGroup {
    Write-Step "Creating resource group: $ResourceGroup"
    az group create --name $ResourceGroup --location $Location --output table
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Resource group created"
    }
    else {
        Write-Error "Failed to create resource group"
        exit 1
    }
}

# Create Azure Container Registry
function New-ContainerRegistry {
    Write-Step "Creating Azure Container Registry: $RegistryName"
    az acr create `
        --resource-group $ResourceGroup `
        --name $RegistryName `
        --sku Basic `
        --admin-enabled true `
        --output table
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Container registry created"
    }
    else {
        Write-Error "Failed to create container registry"
        exit 1
    }
}

# Build and push Docker images
function Build-AndPushImages {
    Write-Step "Building and pushing Docker images..."
    
    # Get ACR login server
    $acrLoginServer = az acr show --name $RegistryName --resource-group $ResourceGroup --query "loginServer" -o tsv
    
    # Login to ACR
    az acr login --name $RegistryName
    
    # Build and push backend image
    Write-Step "Building backend image..."
    docker build -t "$acrLoginServer/quantumcertify-backend:latest" ./backend
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to build backend image"
        exit 1
    }
    
    docker push "$acrLoginServer/quantumcertify-backend:latest"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to push backend image"
        exit 1
    }
    
    # Build and push frontend image
    Write-Step "Building frontend image..."
    docker build -t "$acrLoginServer/quantumcertify-frontend:latest" ./frontend
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to build frontend image"
        exit 1
    }
    
    docker push "$acrLoginServer/quantumcertify-frontend:latest"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to push frontend image"
        exit 1
    }
    
    Write-Success "Images built and pushed successfully"
    return $acrLoginServer
}

# Create Azure SQL Database
function New-SqlDatabase {
    Write-Step "Creating Azure SQL Database..."
    
    $sqlServerName = "quantumcertify-sql-$(Get-Date -Format 'yyyyMMddHHmm')"
    $sqlDatabaseName = "QuantumCertifyDB"
    $sqlAdminUsername = "quantumadmin"
    
    # Generate secure password
    $sqlAdminPassword = [System.Web.Security.Membership]::GeneratePassword(24, 4)
    
    # Create SQL Server
    az sql server create `
        --resource-group $ResourceGroup `
        --name $sqlServerName `
        --location $Location `
        --admin-user $sqlAdminUsername `
        --admin-password $sqlAdminPassword `
        --output table
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create SQL Server"
        exit 1
    }
    
    # Create database
    az sql db create `
        --resource-group $ResourceGroup `
        --server $sqlServerName `
        --name $sqlDatabaseName `
        --edition Basic `
        --output table
    
    # Configure firewall to allow Azure services
    az sql server firewall-rule create `
        --resource-group $ResourceGroup `
        --server $sqlServerName `
        --name "AllowAzureServices" `
        --start-ip-address "0.0.0.0" `
        --end-ip-address "0.0.0.0"
    
    Write-Success "Database created successfully"
    Write-Warning "Save these database credentials:"
    Write-Output "Server: $sqlServerName.database.windows.net"
    Write-Output "Database: $sqlDatabaseName"
    Write-Output "Username: $sqlAdminUsername"
    Write-Output "Password: $sqlAdminPassword"
    
    return @{
        Server = "$sqlServerName.database.windows.net"
        Database = $sqlDatabaseName
        Username = $sqlAdminUsername
        Password = $sqlAdminPassword
    }
}

# Deploy containers to Azure Container Instances
function Deploy-Containers {
    param($acrLoginServer, $dbConfig)
    
    Write-Step "Deploying containers to Azure Container Instances..."
    
    # Get ACR credentials
    $acrUsername = az acr credential show --name $RegistryName --resource-group $ResourceGroup --query "username" -o tsv
    $acrPassword = az acr credential show --name $RegistryName --resource-group $ResourceGroup --query "passwords[0].value" -o tsv
    
    # Check if GEMINI_API_KEY is set
    $geminiApiKey = $env:GEMINI_API_KEY
    if (-not $geminiApiKey) {
        Write-Error "GEMINI_API_KEY environment variable is not set"
        Write-Output "Please set it before running deployment:"
        Write-Output "`$env:GEMINI_API_KEY = 'your_gemini_api_key'"
        exit 1
    }
    
    # Deploy frontend container
    Write-Step "Deploying frontend container..."
    az container create `
        --resource-group $ResourceGroup `
        --name $ContainerGroupName `
        --image "$acrLoginServer/quantumcertify-frontend:latest" `
        --registry-login-server $acrLoginServer `
        --registry-username $acrUsername `
        --registry-password $acrPassword `
        --dns-name-label $DnsNameLabel `
        --ports 80 443 `
        --cpu 1 `
        --memory 1.5 `
        --environment-variables "REACT_APP_API_URL=http://$DnsNameLabel-api.eastus.azurecontainer.io:8000" `
        --output table
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to deploy frontend container"
        exit 1
    }
    
    # Deploy backend container
    Write-Step "Deploying backend container..."
    az container create `
        --resource-group $ResourceGroup `
        --name "$ContainerGroupName-backend" `
        --image "$acrLoginServer/quantumcertify-backend:latest" `
        --registry-login-server $acrLoginServer `
        --registry-username $acrUsername `
        --registry-password $acrPassword `
        --dns-name-label "$DnsNameLabel-api" `
        --ports 8000 `
        --cpu 1 `
        --memory 1.5 `
        --secure-environment-variables `
            "DB_SERVER=$($dbConfig.Server)" `
            "DB_NAME=$($dbConfig.Database)" `
            "DB_USERNAME=$($dbConfig.Username)" `
            "DB_PASSWORD=$($dbConfig.Password)" `
            "GEMINI_API_KEY=$geminiApiKey" `
        --environment-variables `
            "ALLOWED_ORIGINS=http://$DnsNameLabel.eastus.azurecontainer.io,https://$DnsNameLabel.eastus.azurecontainer.io" `
            "LOG_LEVEL=INFO" `
        --output table
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to deploy backend container"
        exit 1
    }
    
    Write-Success "Containers deployed successfully"
}

# Show deployment information
function Show-DeploymentInfo {
    Write-Step "Deployment Information"
    
    Write-Output "Frontend URL: http://$DnsNameLabel.eastus.azurecontainer.io"
    Write-Output "Backend API URL: http://$DnsNameLabel-api.eastus.azurecontainer.io:8000"
    Write-Output "API Documentation: http://$DnsNameLabel-api.eastus.azurecontainer.io:8000/docs"
    
    Write-Warning "Important Notes:"
    Write-Output "1. It may take a few minutes for the containers to start and be accessible"
    Write-Output "2. Make sure your database allows connections from Azure services"
    Write-Output "3. Update DNS records if you want to use a custom domain"
}

# Main deployment function
function Main {
    Write-ColorOutput Cyan "🚀 QuantumCertify Azure Deployment"
    Write-ColorOutput Cyan "=================================="
    
    if (-not (Test-AzureCLI)) {
        exit 1
    }
    
    if (-not (Test-AzureLogin)) {
        exit 1
    }
    
    try {
        New-ResourceGroup
        New-ContainerRegistry
        $acrLoginServer = Build-AndPushImages
        $dbConfig = New-SqlDatabase
        Deploy-Containers -acrLoginServer $acrLoginServer -dbConfig $dbConfig
        Show-DeploymentInfo
        
        Write-Success "Deployment completed successfully! 🎉"
    }
    catch {
        Write-Error "Deployment failed: $_"
        exit 1
    }
}

# Run main function
Main