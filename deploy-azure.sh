#!/bin/bash

# QuantumCertify Azure Deployment Script
# This script automates the deployment to Azure Container Instances

set -e  # Exit on error

# Configuration
RESOURCE_GROUP="quantumcertify-rg"
LOCATION="eastus"
REGISTRY_NAME="quantumcertifyregistry"
CONTAINER_GROUP_NAME="quantumcertify-app"
DNS_NAME_LABEL="quantumcertify-$(date +%s)"  # Unique DNS name

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if Azure CLI is installed
check_azure_cli() {
    print_step "Checking Azure CLI installation..."
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI is not installed. Please install it first:"
        echo "https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi
    print_success "Azure CLI found"
}

# Login to Azure
azure_login() {
    print_step "Checking Azure login status..."
    if ! az account show &> /dev/null; then
        print_warning "Not logged in to Azure. Please log in:"
        az login
    fi
    
    SUBSCRIPTION_ID=$(az account show --query id -o tsv)
    SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
    print_success "Logged in to subscription: $SUBSCRIPTION_NAME ($SUBSCRIPTION_ID)"
}

# Create resource group
create_resource_group() {
    print_step "Creating resource group: $RESOURCE_GROUP"
    az group create \
        --name $RESOURCE_GROUP \
        --location $LOCATION \
        --output table
    print_success "Resource group created"
}

# Create Azure Container Registry
create_registry() {
    print_step "Creating Azure Container Registry: $REGISTRY_NAME"
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $REGISTRY_NAME \
        --sku Basic \
        --admin-enabled true \
        --output table
    print_success "Container registry created"
}

# Build and push images
build_and_push() {
    print_step "Building and pushing Docker images..."
    
    # Get ACR login server
    ACR_LOGIN_SERVER=$(az acr show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP --query "loginServer" -o tsv)
    
    # Login to ACR
    az acr login --name $REGISTRY_NAME
    
    # Build and push backend image
    print_step "Building backend image..."
    docker build -t $ACR_LOGIN_SERVER/quantumcertify-backend:latest ./backend
    docker push $ACR_LOGIN_SERVER/quantumcertify-backend:latest
    
    # Build and push frontend image
    print_step "Building frontend image..."
    docker build -t $ACR_LOGIN_SERVER/quantumcertify-frontend:latest ./frontend
    docker push $ACR_LOGIN_SERVER/quantumcertify-frontend:latest
    
    print_success "Images built and pushed successfully"
}

# Create Azure SQL Database
create_database() {
    print_step "Creating Azure SQL Database..."
    
    SQL_SERVER_NAME="quantumcertify-sql-$(date +%s)"
    SQL_DATABASE_NAME="QuantumCertifyDB"
    SQL_ADMIN_USERNAME="quantumadmin"
    
    # Generate secure password
    SQL_ADMIN_PASSWORD=$(openssl rand -base64 32)
    
    # Create SQL Server
    az sql server create \
        --resource-group $RESOURCE_GROUP \
        --name $SQL_SERVER_NAME \
        --location $LOCATION \
        --admin-user $SQL_ADMIN_USERNAME \
        --admin-password "$SQL_ADMIN_PASSWORD" \
        --output table
    
    # Create database
    az sql db create \
        --resource-group $RESOURCE_GROUP \
        --server $SQL_SERVER_NAME \
        --name $SQL_DATABASE_NAME \
        --edition Basic \
        --output table
    
    # Configure firewall to allow Azure services
    az sql server firewall-rule create \
        --resource-group $RESOURCE_GROUP \
        --server $SQL_SERVER_NAME \
        --name "AllowAzureServices" \
        --start-ip-address 0.0.0.0 \
        --end-ip-address 0.0.0.0
    
    print_success "Database created successfully"
    print_warning "Save these database credentials:"
    echo "Server: $SQL_SERVER_NAME.database.windows.net"
    echo "Database: $SQL_DATABASE_NAME"
    echo "Username: $SQL_ADMIN_USERNAME"
    echo "Password: $SQL_ADMIN_PASSWORD"
    
    # Export for container deployment
    export DB_SERVER="$SQL_SERVER_NAME.database.windows.net"
    export DB_NAME="$SQL_DATABASE_NAME"
    export DB_USERNAME="$SQL_ADMIN_USERNAME"
    export DB_PASSWORD="$SQL_ADMIN_PASSWORD"
}

# Deploy containers to Azure Container Instances
deploy_containers() {
    print_step "Deploying containers to Azure Container Instances..."
    
    # Get ACR credentials
    ACR_LOGIN_SERVER=$(az acr show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP --query "loginServer" -o tsv)
    ACR_USERNAME=$(az acr credential show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP --query "username" -o tsv)
    ACR_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP --query "passwords[0].value" -o tsv)
    
    # Create container group with both frontend and backend
    az container create \
        --resource-group $RESOURCE_GROUP \
        --name $CONTAINER_GROUP_NAME \
        --image $ACR_LOGIN_SERVER/quantumcertify-frontend:latest \
        --registry-login-server $ACR_LOGIN_SERVER \
        --registry-username $ACR_USERNAME \
        --registry-password $ACR_PASSWORD \
        --dns-name-label $DNS_NAME_LABEL \
        --ports 80 443 \
        --cpu 1 \
        --memory 1.5 \
        --environment-variables \
            REACT_APP_API_URL=http://$DNS_NAME_LABEL.eastus.azurecontainer.io:8000 \
        --output table
    
    # Deploy backend container (separate group for now)
    az container create \
        --resource-group $RESOURCE_GROUP \
        --name "${CONTAINER_GROUP_NAME}-backend" \
        --image $ACR_LOGIN_SERVER/quantumcertify-backend:latest \
        --registry-login-server $ACR_LOGIN_SERVER \
        --registry-username $ACR_USERNAME \
        --registry-password $ACR_PASSWORD \
        --dns-name-label "${DNS_NAME_LABEL}-api" \
        --ports 8000 \
        --cpu 1 \
        --memory 1.5 \
        --secure-environment-variables \
            GEMINI_API_KEY="$GEMINI_API_KEY" \
            DB_SERVER="$DB_SERVER" \
            DB_NAME="$DB_NAME" \
            DB_USERNAME="$DB_USERNAME" \
            DB_PASSWORD="$DB_PASSWORD" \
            DB_PORT="1433" \
            DB_DRIVER="SQL+Server" \
            CONTACT_EMAIL="$CONTACT_EMAIL" \
            DEVELOPER_NAME="$DEVELOPER_NAME" \
            PROJECT_VERSION="2.0.0" \
            SECRET_KEY="$SECRET_KEY" \
        --environment-variables \
            ALLOWED_ORIGINS="http://$DNS_NAME_LABEL.eastus.azurecontainer.io,https://$DNS_NAME_LABEL.eastus.azurecontainer.io" \
            LOG_LEVEL=INFO \
        --output table
    
    print_success "Containers deployed successfully"
}

# Show deployment information
show_deployment_info() {
    print_step "Deployment Information"
    
    echo "Frontend URL: http://$DNS_NAME_LABEL.eastus.azurecontainer.io"
    echo "Backend API URL: http://${DNS_NAME_LABEL}-api.eastus.azurecontainer.io:8000"
    echo "API Documentation: http://${DNS_NAME_LABEL}-api.eastus.azurecontainer.io:8000/docs"
    
    print_warning "Important: Update your frontend environment to point to the backend URL"
    print_warning "Set GEMINI_API_KEY environment variable before deployment"
}

# Main deployment function
main() {
    echo "🚀 QuantumCertify Azure Deployment"
    echo "=================================="
    
    # Check environment variables
    if [ -z "$GEMINI_API_KEY" ]; then
        print_error "GEMINI_API_KEY environment variable is not set"
        echo "Please set it before running deployment:"
        echo "export GEMINI_API_KEY=your_gemini_api_key"
        exit 1
    fi
    
    check_azure_cli
    azure_login
    create_resource_group
    create_registry
    build_and_push
    create_database
    deploy_containers
    show_deployment_info
    
    print_success "Deployment completed successfully! 🎉"
}

# Run main function
main "$@"