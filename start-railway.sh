#!/bin/bash
# Railway startup script with ODBC driver installation
set -e

echo "🔧 Installing Microsoft ODBC Driver 18 for SQL Server..."

# Add Microsoft repository
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg
echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/ubuntu/22.04/prod jammy main" | tee /etc/apt/sources.list.d/mssql-release.list

# Update and install
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev

echo "✅ ODBC Driver installed successfully!"
echo "🚀 Starting QuantumCertify application..."

# Start the application
cd backend && python run_server.py
