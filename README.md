# QuantumCertify

AI-Powered Post-Quantum Cryptography Certificate Analysis Tool

## 🚀 Quick Start

### 1. Environment Configuration

Copy the environment template and configure your credentials:

```bash
# Backend configuration
cd backend
cp .env.example .env
# Edit .env with your database credentials and API keys
```

**Required Environment Variables:**
- `GEMINI_API_KEY`: Google Gemini API key for AI features
- `DB_SERVER`: Your Azure SQL Server hostname
- `DB_NAME`: Database name  
- `DB_USERNAME`: Database username
- `DB_PASSWORD`: Database password
- `DB_PORT`: Database port (default: 1433)
- `DB_DRIVER`: Database driver (default: SQL+Server)
- `CONTACT_EMAIL`: Your support email
- `DEVELOPER_NAME`: Developer name
- `PROJECT_VERSION`: Application version (e.g., 2.0.0)
- `SECRET_KEY`: Application secret key for security
- `ALLOWED_ORIGINS`: CORS allowed origins
- `DEBUG`: Debug mode (true/false)

See `SECURITY.md` for detailed security configuration guidelines.

### 2. Installation & Setup

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies  
cd ../frontend
npm install
```

### 3. Run the Application

```bash
# Start backend (from backend directory)
python run_server.py

# Start frontend (from frontend directory)
npm start
```

## ✨ Features

- **Certificate Analysis**: Upload and analyze X.509 certificates with detailed quantum safety assessment
- **Quantum Safety Assessment**: Identify quantum-safe vs classical cryptographic algorithms
- **AI-Powered Analysis**: Uses Google's Gemini AI for intelligent certificate analysis and recommendations
- **Multi-Page Frontend**: React SPA with routing (Dashboard, Upload, About pages)
- **Real-time Dashboard**: View live certificate statistics with auto-refresh functionality
- **Interactive Upload**: Drag-and-drop certificate upload with progress indicators
- **RESTful API**: Complete API with interactive Swagger documentation
- **Database Integration**: Persistent storage with SQL Server and connection pooling
- **Environment-Based Security**: Comprehensive environment variable configuration
- **Production Ready**: Docker containerization and Azure deployment scripts

## 🔒 Security

All sensitive credentials are now stored in environment variables. Never commit your `.env` file to version control. See `SECURITY.md` for complete security guidelines.