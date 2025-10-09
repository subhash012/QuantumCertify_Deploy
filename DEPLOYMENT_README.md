# 🚀 QuantumCertify - Production Deployment Guide

## Overview
QuantumCertify is an AI-powered X.509 certificate analyzer that provides post-quantum cryptography (PQC) migration recommendations using Google Gemini AI.

## ✅ Prerequisites

### Backend Requirements
- Python 3.11+
- Google Gemini API Key
- PostgreSQL (production) or SQLite (development)

### Frontend Requirements
- Node.js 16+
- npm or yarn

## 📦 Project Structure

```
QuantumCertify/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # Main API application
│   │   ├── models.py       # Database models
│   │   ├── routes.py       # API routes
│   │   ├── database.py     # Database configuration
│   │   └── utils.py        # Utility functions
│   ├── .env                # Environment variables (create this)
│   ├── requirements.txt    # Python dependencies
│   └── run_server.py       # Server startup script
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   └── App.js          # Main app
│   ├── package.json        # Node dependencies
│   └── server.js           # Production server
│
└── README.md               # This file
```

## 🔧 Environment Setup

### Backend Environment Variables

Create `backend/.env`:

```bash
# Google Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

# Database (Production - PostgreSQL)
DB_SERVER=your-database-server.com
DB_NAME=quantumcertify
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_DRIVER=ODBC Driver 18 for SQL Server

# Database (Development - SQLite)
# Leave DB_* variables empty to use SQLite fallback

# Server Configuration
PORT=8000
ENVIRONMENT=production
```

### Getting a Gemini API Key

1. Visit: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy and paste into `.env`

**Important Notes:**
- Free tier: 250 requests/day
- Each certificate analysis = 2 AI calls
- Consider paid tier for production ($0.0004/request)

## 📥 Installation

### Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the server
python run_server.py
```

Server will start at: `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Development mode
npm start

# Production build
npm run build
```

Development server: `http://localhost:3000`

## 🌐 Deployment Options

### Option 1: Railway.app (Recommended)

#### Backend Deployment

1. **Create Railway Project**
   ```bash
   railway init
   ```

2. **Add Environment Variables**
   - Go to Railway Dashboard
   - Add all variables from `backend/.env`
   - Add: `PORT=8000`

3. **Deploy**
   ```bash
   railway up
   ```

4. **Configure Domain** (optional)
   - Settings → Networking → Custom Domain
   - Add your domain (e.g., `api.quantumcertify.tech`)

#### Frontend Deployment

1. **Create Separate Service**
   ```bash
   railway init
   ```

2. **Add Environment Variables**
   ```bash
   REACT_APP_API_URL=https://your-backend-url.railway.app
   NODE_ENV=production
   ```

3. **Deploy**
   ```bash
   railway up
   ```

### Option 2: Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build individually
docker build -t quantumcertify-backend ./backend
docker build -t quantumcertify-frontend ./frontend

docker run -p 8000:8000 quantumcertify-backend
docker run -p 3000:3000 quantumcertify-frontend
```

### Option 3: Azure App Service

See `AZURE_SETUP.md` for detailed Azure deployment instructions.

## 🧪 Testing

### Test Backend

```bash
# Health check
curl http://localhost:8000/health

# Interactive API docs
# Open: http://localhost:8000/docs
```

### Test Frontend

1. Open: `http://localhost:3000`
2. Upload a certificate (.pem, .crt, .cer, .der)
3. Wait for AI analysis (30-90 seconds)
4. View detailed PQC recommendations

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check & system status |
| `/upload-certificate` | POST | Analyze certificate |
| `/algorithms/pqc` | GET | List PQC algorithms |
| `/dashboard/stats` | GET | Get statistics |

## 🔒 Security Features

- ✅ HTTPS enforcement (production)
- ✅ CORS configuration
- ✅ Security headers (X-Frame-Options, CSP, etc.)
- ✅ Input validation
- ✅ SQL injection prevention
- ✅ File upload validation

## ⚡ Performance Optimization

### Backend
- AI response caching (planned)
- Database connection pooling
- Graceful AI fallback (rule-based)
- File-based statistics (when DB unavailable)

### Frontend
- Code splitting
- Lazy loading
- Production build optimization
- API timeout: 180s for AI analysis

## 🐛 Troubleshooting

### Backend Issues

**AI Quota Exceeded**
- Error: "429 You exceeded your current quota"
- Solution: Wait 24h or upgrade to paid tier
- Falls back to rule-based recommendations

**Database Connection Failed**
- Automatically falls back to SQLite
- Check DB credentials in `.env`
- Ensure ODBC driver installed (if using SQL Server)

**Port Already in Use**
- Change `PORT` in `.env`
- Or kill process: `netstat -ano | findstr :8000`

### Frontend Issues

**API Timeout**
- AI analysis takes 30-90 seconds
- Timeout set to 180 seconds
- Be patient, don't refresh

**CORS Errors**
- Update `REACT_APP_API_URL` in frontend `.env`
- Check backend CORS settings in `main.py`

## 📈 Monitoring

### Check System Health

```bash
curl http://your-domain.com/health
```

Response:
```json
{
  "status": "healthy",
  "services": {
    "database": "available",
    "ai_service": "available",
    "ai_provider": "Google Gemini"
  },
  "version": "2.0.0"
}
```

### View Statistics

```bash
curl http://your-domain.com/dashboard/stats
```

## 🔄 Updates

### Backend Update

```bash
cd backend
git pull
pip install -r requirements.txt --upgrade
python run_server.py
```

### Frontend Update

```bash
cd frontend
git pull
npm install
npm run build
```

## 📞 Support

- **Documentation**: See `docs/` folder
- **Issues**: Create GitHub issue
- **Email**: subhashsubu106@gmail.com

## 📝 License

This project is licensed under the MIT License.

## 🎯 Key Features

- ✅ AI-Powered Certificate Analysis (Google Gemini)
- ✅ Quantum Safety Assessment
- ✅ NIST-Compliant PQC Recommendations
- ✅ Migration Strategies & Timelines
- ✅ Cost-Benefit Analysis
- ✅ Compliance Notes (GDPR, HIPAA, PCI DSS)
- ✅ Interactive Dashboard
- ✅ RESTful API
- ✅ Graceful Fallback (rule-based)

## 🚦 Production Checklist

Before deploying to production:

- [ ] Set `GEMINI_API_KEY` in environment
- [ ] Configure production database
- [ ] Update `REACT_APP_API_URL` in frontend
- [ ] Enable HTTPS
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test all endpoints
- [ ] Review security headers
- [ ] Set up error logging
- [ ] Configure rate limiting (optional)

## 📚 Additional Documentation

- `DEPLOYMENT.md` - General deployment guide
- `RAILWAY_DEPLOYMENT_GUIDE.md` - Railway-specific guide
- `AZURE_SETUP.md` - Azure deployment guide
- `SECURITY.md` - Security best practices

---

**Built with ❤️ using FastAPI, React, and Google Gemini AI**
