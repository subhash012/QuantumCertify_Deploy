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
- `DB_SERVER`: Your Azure SQL Server hostname
- `DB_NAME`: Database name  
- `DB_USERNAME`: Database username
- `DB_PASSWORD`: Database password
- `GEMINI_API_KEY`: Google Gemini API key for AI features
- `CONTACT_EMAIL`: Your support email

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

## 🔒 Security

All sensitive credentials are now stored in environment variables. Never commit your `.env` file to version control. See `SECURITY.md` for complete security guidelines.