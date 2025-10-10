# QuantumCertify - Complete Code Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Backend Deep Dive](#backend-deep-dive)
4. [Frontend Deep Dive](#frontend-deep-dive)
5. [Database Schema](#database-schema)
6. [API Endpoints](#api-endpoints)
7. [Deployment](#deployment)
8. [Code Flow](#code-flow)

---

## 🎯 Project Overview

**QuantumCertify** is an AI-powered certificate analysis tool that:
- Analyzes X.509 digital certificates
- Detects quantum-safe cryptographic algorithms
- Provides AI-powered migration recommendations using Google Gemini
- Helps organizations prepare for post-quantum cryptography (PQC)

### Technology Stack
```
Backend:  Python 3.12 + FastAPI + SQLAlchemy + Google Gemini AI
Frontend: React 18 + Axios + CSS3
Database: Azure SQL Server (with file-based fallback)
Deployment: Railway.app (with automatic CI/CD)
```

---

## 🏗️ Architecture

```
┌─────────────────┐
│   React App     │  (Frontend - Port 3000 dev, 8080 prod)
│  Certificate    │
│    Upload       │
└────────┬────────┘
         │
         │ HTTP POST /upload-certificate
         │
         ▼
┌─────────────────┐
│  FastAPI Server │  (Backend - Port 8000)
│   main.py       │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    │         │          │          │
    ▼         ▼          ▼          ▼
┌───────┐ ┌──────┐ ┌────────┐ ┌──────────┐
│Crypto │ │ DB   │ │ Gemini │ │  File    │
│Parser │ │Logic │ │  AI    │ │ Fallback │
└───────┘ └──────┘ └────────┘ └──────────┘
              │
              ▼
      ┌──────────────┐
      │  Azure SQL   │
      │   Database   │
      └──────────────┘
```

---

## 🔧 Backend Deep Dive

### File Structure
```
backend/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI app + routes (841 lines) ⭐ CORE
│   ├── database.py          # Database connection setup
│   ├── models.py            # SQLAlchemy ORM models
│   ├── deps.py              # Dependency injection
│   ├── logging_config.py    # Production logging setup
│   └── utils.py             # Utility functions
├── requirements.txt         # Python dependencies
├── run_server.py           # Production server startup
└── Dockerfile              # Container configuration
```

### 1️⃣ main.py - The Heart of the Application

#### Imports & Configuration (Lines 1-50)
```python
from fastapi import FastAPI, UploadFile, File
from cryptography import x509
from sqlalchemy.orm import Session
import google.generativeai as genai

# Environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
APP_VERSION = os.getenv("PROJECT_VERSION", "2.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
```

**Key Components:**
- **FastAPI**: Modern web framework for building APIs
- **Cryptography**: Parses X.509 certificates
- **SQLAlchemy**: ORM for database operations
- **Google Gemini**: AI recommendations

#### AI Configuration (Lines 51-67)
```python
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    AI_AVAILABLE = True
else:
    AI_AVAILABLE = False
```

**What happens here:**
- Tries to initialize Gemini AI
- Sets `AI_AVAILABLE` flag
- Falls back to rule-based analysis if AI unavailable

#### PQC Algorithm Analysis (Lines 68-86)
```python
def _analyze_pqc_algorithm(algorithm_name: str) -> bool:
    pqc_keywords = [
        'dilithium', 'kyber', 'falcon', 'mceliece', 
        'frodo', 'saber', 'ntru', 'bike', 'crystals', 
        'sphincs', 'picnic', 'rainbow'
    ]
    algorithm_lower = algorithm_name.lower()
    return any(keyword in algorithm_lower for keyword in pqc_keywords)
```

**Purpose:** 
- Fallback detection when database is unavailable
- Searches for PQC algorithm keywords in algorithm names
- Returns `True` if quantum-safe, `False` otherwise

#### Classical to PQC Mapping (Lines 87-150)
```python
def _get_classical_to_pqc_mapping() -> Dict[str, Dict]:
    return {
        "RSA": {
            "quantum_threat": "HIGH - Broken by Shor's algorithm",
            "recommended_pqc": {
                "key_exchange": ["CRYSTALS-Kyber", "FrodoKEM"],
                "digital_signature": ["CRYSTALS-Dilithium", "FALCON"]
            },
            "primary_recommendation": "CRYSTALS-Kyber for key exchange..."
        },
        # ... more algorithms
    }
```

**Contains:**
- Mapping of classical algorithms (RSA, ECDSA, DSA, DH, ECDH)
- Quantum threat assessment
- Recommended PQC alternatives
- Migration timelines and priorities

#### Gemini AI Recommendations (Lines 151-220)
```python
async def _get_gemini_recommendations(
    algorithm_name: str, 
    algorithm_type: str, 
    context: Dict
) -> Dict:
    prompt = f"""
    You are a post-quantum cryptography expert...
    
    ANALYSIS TARGET:
    - Algorithm: {algorithm_name}
    - Type: {algorithm_type}
    
    Provide analysis in JSON format:
    {{
        "quantum_vulnerability": "...",
        "recommended_pqc_algorithms": [...],
        "primary_recommendation": "...",
        ...
    }}
    """
    
    response = model.generate_content(prompt)
    # Parse JSON from response
    return json.loads(response.text)
```

**How it works:**
1. Builds a detailed prompt with algorithm context
2. Sends to Gemini AI model
3. Receives AI-generated JSON response
4. Parses and returns structured recommendations
5. Falls back to rule-based if AI fails

#### Rule-based Recommendations (Lines 221-280)
```python
def _get_rule_based_recommendations(
    algorithm_name: str, 
    algorithm_type: str
) -> Dict:
    mapping = _get_classical_to_pqc_mapping()
    
    # Find matching algorithm
    for classical_alg, pqc_info in mapping.items():
        if classical_alg in clean_name:
            recommendation = pqc_info
            break
    
    # Return structured recommendations
    return {
        "quantum_vulnerability": recommendation["quantum_threat"],
        "recommended_pqc_algorithms": [...],
        ...
    }
```

**Fallback logic:**
- Uses hardcoded expert knowledge
- Matches algorithm against known patterns
- Returns same structure as AI recommendations
- Ensures app works even without AI

#### FastAPI App Initialization (Lines 281-310)
```python
app = FastAPI(
    title="QuantumCertify API - AI-Powered PQC Analysis",
    description="...",
    version=APP_VERSION,
    docs_url="/docs" if DEBUG_MODE else None,  # Security
    redoc_url="/redoc" if DEBUG_MODE else None
)
```

**Features:**
- Auto-generates API documentation at `/docs`
- Disables docs in production for security
- Version tracking
- Contact information

#### Security Middleware (Lines 311-375)
```python
# CORS - Cross-Origin Resource Sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", ...]
)

# Security Headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    if ENVIRONMENT == "production":
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "..."
        response.headers["Content-Security-Policy"] = "..."
    
    return response
```

**Security features:**
- CORS protection
- XSS prevention
- Clickjacking protection
- HTTPS enforcement
- CSP (Content Security Policy)

#### Database Session Management (Lines 376-395)
```python
def get_db():
    if not DATABASE_AVAILABLE:
        yield None
        return
    
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        yield None
    finally:
        if 'db' in locals() and db:
            db.close()
```

**How it works:**
- Dependency injection pattern
- Creates new DB session per request
- Automatically closes connection
- Returns `None` if DB unavailable

#### File-based Statistics (Lines 396-440)
```python
STATS_FILE_PATH = "statistics.json"

def load_statistics_from_file():
    if os.path.exists(STATS_FILE_PATH):
        with open(STATS_FILE_PATH, 'r') as f:
            return json.load(f)
    else:
        default_stats = {
            "total_analyzed": 0,
            "quantum_safe_count": 0,
            "classical_count": 0
        }
        save_statistics_to_file(default_stats)
        return default_stats
```

**Fallback mechanism:**
- Works when database is unavailable
- Stores stats in JSON file
- Persistent across restarts
- Automatic initialization

#### Certificate Analysis Saving (Lines 441-510)
```python
def save_certificate_analysis(db: Session, analysis_data: dict):
    # Determine quantum safety
    is_quantum_safe = (
        analysis_data['cryptographic_analysis']['public_key']['is_quantum_safe'] and
        analysis_data['cryptographic_analysis']['signature']['is_quantum_safe']
    )
    
    # Try database first
    if db and DATABASE_AVAILABLE:
        try:
            certificate_record = CertificateAnalysis(
                file_name=analysis_data.get('file_name'),
                subject=analysis_data.get('certificate_info', {}).get('subject'),
                is_quantum_safe=is_quantum_safe,
                ...
            )
            db.add(certificate_record)
            db.commit()
            update_analytics_summary(db, is_quantum_safe)
            return
        except Exception as e:
            logging.error(f"Database error: {e}")
            db.rollback()
    
    # Fallback to file
    stats = load_statistics_from_file()
    stats["total_analyzed"] += 1
    if is_quantum_safe:
        stats["quantum_safe_count"] += 1
    else:
        stats["classical_count"] += 1
    save_statistics_to_file(stats)
```

**Dual-mode operation:**
1. **Primary**: Save to Azure SQL Database
2. **Fallback**: Save to local JSON file
3. **Graceful degradation**: App works in both modes

#### Main Endpoint: Certificate Upload (Lines 560-730)
```python
@app.post("/upload-certificate")
async def upload_certificate(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    # Step 1: Read uploaded file
    cert_bytes = await file.read()
    
    # Step 2: Parse certificate (try PEM, then DER)
    try:
        cert = x509.load_pem_x509_certificate(cert_bytes, default_backend())
    except:
        cert = x509.load_der_x509_certificate(cert_bytes, default_backend())
    
    # Step 3: Extract certificate information
    issuer = cert.issuer.rfc4514_string()
    subject = cert.subject.rfc4514_string()
    public_key = cert.public_key()
    key_type = public_key.__class__.__name__
    key_size = getattr(public_key, "key_size", None)
    
    # Step 4: Get signature algorithm
    sig_oid = cert.signature_algorithm_oid.dotted_string
    sig_name = cert.signature_algorithm_oid._name
    
    # Step 5: Database lookup for algorithms
    if db and DATABASE_AVAILABLE:
        pubkey_algo = db.query(PublicKeyAlgorithm).filter_by(
            public_key_algorithm_oid=pubkey_oid
        ).first()
        sig_algo = db.query(SignatureAlgorithm).filter_by(
            signature_algorithm_oid=sig_oid
        ).first()
    
    # Step 6: Determine quantum safety
    pubkey_is_pqc = pubkey_algo.is_pqc if pubkey_algo else _analyze_pqc_algorithm(pubkey_name)
    sig_is_pqc = sig_algo.is_pqc if sig_algo else _analyze_pqc_algorithm(sig_name)
    
    # Step 7: Get AI recommendations for vulnerable algorithms
    recommendations = {}
    if not pubkey_is_pqc:
        context = {
            "algorithm_type": "public_key",
            "key_size": key_size,
            "certificate_type": "X.509",
            "expiry_date": cert.not_valid_after_utc.isoformat()
        }
        recommendations["public_key"] = await _get_gemini_recommendations(
            pubkey_algorithm_name, "public_key", context
        )
    
    if not sig_is_pqc:
        recommendations["signature"] = await _get_gemini_recommendations(
            sig_algorithm_name, "digital_signature", context
        )
    
    # Step 8: Build response
    response_data = {
        "file_name": file.filename,
        "certificate_info": {
            "issuer": issuer,
            "subject": subject,
            "valid_from": cert.not_valid_before_utc.isoformat(),
            "valid_until": cert.not_valid_after_utc.isoformat(),
            "serial_number": str(cert.serial_number)
        },
        "cryptographic_analysis": {
            "public_key": {
                "algorithm": pubkey_algorithm_name,
                "type": key_type,
                "size": key_size,
                "is_quantum_safe": pubkey_is_pqc
            },
            "signature": {
                "algorithm": sig_algorithm_name,
                "is_quantum_safe": sig_is_pqc
            }
        },
        "security_assessment": {
            "overall_quantum_safety": "SAFE" if (pubkey_is_pqc and sig_is_pqc) else "VULNERABLE",
            "risk_level": "LOW" if (pubkey_is_pqc and sig_is_pqc) else "HIGH"
        },
        "ai_recommendations": recommendations,
        "system_info": {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "ai_powered": AI_AVAILABLE,
            "database_connected": DATABASE_AVAILABLE and db is not None
        }
    }
    
    # Step 9: Save to database/file for statistics
    save_certificate_analysis(db, response_data)
    
    # Step 10: Return results
    return JSONResponse(content=response_data)
```

**Complete Flow:**
1. Receive uploaded certificate file
2. Parse with cryptography library (PEM or DER)
3. Extract metadata (issuer, subject, dates, serial)
4. Extract cryptographic algorithms
5. Query database for algorithm details
6. Determine quantum safety
7. Get AI recommendations if vulnerable
8. Build comprehensive response
9. Save to database for analytics
10. Return JSON response to frontend

#### Other Endpoints (Lines 731-843)

**Dashboard Statistics:**
```python
@app.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    stats = get_dashboard_statistics(db)
    return JSONResponse(content={"statistics": stats})
```

**Health Check:**
```python
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "services": {
            "database": "available" if DATABASE_AVAILABLE else "unavailable",
            "ai_service": "available" if AI_AVAILABLE else "unavailable"
        }
    }
```

**PQC Algorithms Info:**
```python
@app.get("/algorithms/pqc")
def get_pqc_algorithms():
    return {
        "nist_standardized": {
            "key_exchange": ["CRYSTALS-Kyber"],
            "digital_signatures": ["CRYSTALS-Dilithium", "FALCON", "SPHINCS+"]
        },
        "hybrid_approaches": {...},
        "migration_timeline": {...}
    }
```

---

### 2️⃣ database.py - Database Connection

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get database credentials from environment
DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_NAME = os.getenv("DB_NAME", "quantumcertify")
DB_USERNAME = os.getenv("DB_USERNAME", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Build connection string
SQLALCHEMY_DATABASE_URL = (
    f"mssql+pymssql://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"
)

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600    # Recycle connections every hour
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
```

**Key concepts:**
- **Engine**: Connection pool manager
- **SessionLocal**: Factory for creating database sessions
- **Base**: Parent class for all ORM models
- **pymssql**: Pure Python SQL Server driver (no ODBC needed)

---

### 3️⃣ models.py - Database Tables

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from .database import Base

class PublicKeyAlgorithm(Base):
    __tablename__ = "public_key_algorithms"
    
    id = Column(Integer, primary_key=True, index=True)
    public_key_algorithm_name = Column(String(255), nullable=False)
    public_key_algorithm_oid = Column(String(255), nullable=True)
    category = Column(String(50), nullable=False, default="Unknown")
    is_pqc = Column(Boolean, nullable=True, default=False)

class SignatureAlgorithm(Base):
    __tablename__ = "signature_algorithms"
    
    id = Column(Integer, primary_key=True, index=True)
    signature_algorithm_name = Column(String(255), nullable=False)
    signature_algorithm_oid = Column(String(255), nullable=True)
    category = Column(String(50), nullable=False, default="Unknown")
    is_pqc = Column(Boolean, nullable=False, default=False)

class CertificateAnalysis(Base):
    __tablename__ = "certificate_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    subject = Column(Text, nullable=True)
    issuer = Column(Text, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    public_key_algorithm = Column(String(255), nullable=True)
    signature_algorithm = Column(String(255), nullable=True)
    is_quantum_safe = Column(Boolean, nullable=False, default=False)
    overall_risk_level = Column(String(50), nullable=True)
    analysis_timestamp = Column(DateTime, server_default=func.now())
    ai_powered = Column(Boolean, default=False)

class AnalyticsSummary(Base):
    __tablename__ = "analytics_summary"
    
    id = Column(Integer, primary_key=True, index=True)
    total_analyzed = Column(Integer, default=0)
    quantum_safe_count = Column(Integer, default=0)
    classical_count = Column(Integer, default=0)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

**Table purposes:**
1. **public_key_algorithms**: Reference data for known public key algorithms
2. **signature_algorithms**: Reference data for signature algorithms
3. **certificate_analyses**: Audit trail of all analyzed certificates
4. **analytics_summary**: Aggregated statistics for dashboard

---

### 4️⃣ logging_config.py - Production Logging

```python
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_production_logging():
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Access log (HTTP requests)
    access_logger = logging.getLogger('access')
    access_handler = RotatingFileHandler(
        'logs/access.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    access_logger.addHandler(access_handler)
    
    # Security log
    security_logger = logging.getLogger('security')
    security_handler = RotatingFileHandler(
        'logs/security.log',
        maxBytes=10485760,
        backupCount=5
    )
    security_logger.addHandler(security_handler)
    
    # Performance log
    performance_logger = logging.getLogger('performance')
    performance_handler = RotatingFileHandler(
        'logs/performance.log',
        maxBytes=10485760,
        backupCount=5
    )
    performance_logger.addHandler(performance_handler)
```

**Features:**
- Separate logs for access, security, performance
- Automatic rotation at 10MB
- Keeps 5 backup files
- Structured logging format

---

### 5️⃣ run_server.py - Production Startup

```python
import os
import sys
import logging
from pathlib import Path

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Environment validation
required_vars = ["GEMINI_API_KEY", "DB_SERVER", "DB_NAME", "DB_USERNAME", "DB_PASSWORD"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    logging.warning(f"Missing environment variables: {missing_vars}")

# Import app
from app.main import app

# Get port from Railway or default
PORT = int(os.getenv("PORT", 8080))

if __name__ == "__main__":
    import uvicorn
    
    logging.info(f"🚀 Starting QuantumCertify server for Railway.app")
    logging.info(f"🌐 Server: 0.0.0.0:{PORT}")
    logging.info(f"🔧 Environment: {os.getenv('ENVIRONMENT', 'production')}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info",
        access_log=True
    )
```

**Purpose:**
- Production-ready server startup
- Environment variable validation
- Railway.app integration (PORT detection)
- Proper logging configuration

---

## 🎨 Frontend Deep Dive

### File Structure
```
frontend/
├── public/
│   ├── index.html          # Main HTML template
│   ├── favicon.ico         # Browser icon
│   └── manifest.json       # PWA configuration
├── src/
│   ├── index.js            # React entry point
│   ├── App.js              # Main app component
│   ├── components/
│   │   ├── CertificateUpload.js  # Certificate upload & analysis ⭐
│   │   ├── CertificateUpload.css # Styling
│   │   ├── Dashboard.js          # Analytics dashboard
│   │   └── About.js              # About page
│   └── services/
│       └── api.js          # API client
├── package.json            # NPM dependencies
└── server.js              # Production server (Express)
```

### 1️⃣ index.js - React Entry Point

```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

**What it does:**
- Entry point for React application
- Renders `<App />` component into DOM
- `StrictMode` for development warnings

---

### 2️⃣ App.js - Main Application

```javascript
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import CertificateUpload from './components/CertificateUpload';
import Dashboard from './components/Dashboard';
import About from './components/About';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-brand">
            <h1>🔐 QuantumCertify</h1>
          </div>
          <ul className="nav-menu">
            <li><Link to="/">Analyze</Link></li>
            <li><Link to="/dashboard">Dashboard</Link></li>
            <li><Link to="/about">About</Link></li>
          </ul>
        </nav>
        
        <Routes>
          <Route path="/" element={<CertificateUpload />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
```

**Features:**
- Client-side routing with React Router
- Navigation bar with links
- Three routes: Analyze, Dashboard, About

---

### 3️⃣ api.js - API Client

```javascript
import axios from 'axios';

// Determine API base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 
                     'https://your-backend-railway-url.up.railway.app';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,  // 30 seconds
  headers: {
    'Content-Type': 'multipart/form-data'
  }
});

export const apiService = {
  // Upload certificate for analysis
  uploadCertificate: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/upload-certificate', formData);
  },
  
  // Get dashboard statistics
  getDashboardStats: () => {
    return apiClient.get('/dashboard/stats');
  },
  
  // Health check
  healthCheck: () => {
    return apiClient.get('/health');
  }
};
```

**Purpose:**
- Centralized API communication
- Automatic header configuration
- Timeout handling
- Environment-based URL configuration

---

### 4️⃣ CertificateUpload.js - Main Analysis Component

#### State Management
```javascript
const [file, setFile] = useState(null);              // Selected file
const [loading, setLoading] = useState(false);       // Loading state
const [result, setResult] = useState(null);          // Analysis results
const [error, setError] = useState(null);            // Error messages
```

#### File Selection
```javascript
const handleFileChange = (e) => {
  const selectedFile = e.target.files[0];
  setFile(selectedFile);
  setResult(null);   // Clear previous results
  setError(null);    // Clear previous errors
};
```

#### Form Submission
```javascript
const handleSubmit = async (e) => {
  e.preventDefault();
  
  if (!file) {
    setError('Please select a certificate file');
    return;
  }

  setLoading(true);
  setError(null);

  try {
    const response = await apiService.uploadCertificate(file);
    console.log('Certificate analysis result:', response.data);
    setResult(response.data);
  } catch (err) {
    console.error('Upload error:', err);
    setError(err.message || 'An error occurred');
  } finally {
    setLoading(false);
  }
};
```

**Flow:**
1. User selects file
2. Form submitted
3. Show loading state
4. Call API
5. Display results or error
6. Hide loading state

#### Results Display Structure
```javascript
{result && (
  <div className="result-section">
    {/* 1. Certificate Information */}
    <div className="result-card">
      <h3>📝 Certificate Information</h3>
      <div className="info-grid">
        <div className="info-row">
          <span className="info-label">Subject:</span>
          <span className="info-value">{result.certificate_info?.subject}</span>
        </div>
        <div className="info-row">
          <span className="info-label">Issuer:</span>
          <span className="info-value">{result.certificate_info?.issuer}</span>
        </div>
        <div className="info-row">
          <span className="info-label">Valid From:</span>
          <span className="info-value">
            {formatDate(result.certificate_info?.valid_from)}
          </span>
        </div>
        <div className="info-row">
          <span className="info-label">Valid Until:</span>
          <span className="info-value">
            {formatDate(result.certificate_info?.valid_until)}
          </span>
        </div>
      </div>
    </div>
    
    {/* 2. Cryptographic Analysis */}
    <div className="result-card">
      <h3>🔐 Cryptographic Analysis</h3>
      
      {/* Public Key */}
      <div className="algorithm-item">
        <div className="algorithm-header">
          <span className="algorithm-name">
            Public Key: {result.cryptographic_analysis.public_key.algorithm}
          </span>
          <span className={`status ${
            result.cryptographic_analysis.public_key.is_quantum_safe 
              ? 'safe' 
              : 'vulnerable'
          }`}>
            {result.cryptographic_analysis.public_key.is_quantum_safe 
              ? 'Quantum Safe' 
              : 'Quantum Vulnerable'}
          </span>
        </div>
        <div className="algorithm-details">
          <p><strong>Type:</strong> {result.cryptographic_analysis.public_key.type}</p>
          <p><strong>Key Size:</strong> {result.cryptographic_analysis.public_key.size} bits</p>
        </div>
      </div>
      
      {/* Signature */}
      <div className="algorithm-item">
        {/* Similar structure */}
      </div>
    </div>
    
    {/* 3. Security Assessment */}
    <div className="result-card">
      <h3>🛡️ Security Assessment</h3>
      <div className="security-assessment">
        <div className="overall-risk">
          <span className="risk-label">Quantum Safety:</span>
          <span className="risk-badge">
            {result.security_assessment.overall_quantum_safety}
          </span>
        </div>
        <div className="overall-risk">
          <span className="risk-label">Risk Level:</span>
          <span className="risk-badge">
            {result.security_assessment.risk_level}
          </span>
        </div>
      </div>
    </div>
    
    {/* 4. AI Recommendations */}
    {result.ai_recommendations && (
      <div className="result-card ai-recommendations">
        <h3>🤖 AI-Powered Migration Recommendations</h3>
        
        {/* Public Key Recommendations */}
        {result.ai_recommendations.public_key && (
          <div className="recommendation-section">
            <h4>🔑 Public Key Migration</h4>
            <div className="vulnerability-assessment">
              <strong>Quantum Vulnerability:</strong>
              <span>{result.ai_recommendations.public_key.quantum_vulnerability}</span>
            </div>
            <div className="primary-recommendation">
              <strong>Primary Recommendation:</strong>
              <p>{result.ai_recommendations.public_key.primary_recommendation}</p>
            </div>
            <div className="recommended-algorithms">
              <strong>Recommended PQC Algorithms:</strong>
              <ul>
                {result.ai_recommendations.public_key.recommended_pqc_algorithms.map(
                  (alg, index) => <li key={index}>{alg}</li>
                )}
              </ul>
            </div>
            <div className="security-details">
              <p><strong>Security:</strong> {result.ai_recommendations.public_key.security_assessment}</p>
              <p><strong>Performance:</strong> {result.ai_recommendations.public_key.performance_comparison}</p>
              <p><strong>Migration Strategy:</strong> {result.ai_recommendations.public_key.migration_strategy}</p>
              <p><strong>Timeline:</strong> {result.ai_recommendations.public_key.risk_timeline}</p>
            </div>
          </div>
        )}
        
        {/* Signature Recommendations - similar structure */}
      </div>
    )}
    
    {/* 5. System Information */}
    <div className="result-card">
      <h3>ℹ️ Analysis Information</h3>
      <div className="system-info">
        <div className="info-row">
          <span className="info-label">AI Powered:</span>
          <span className="info-value">
            {result.system_info.ai_powered ? '✓ Yes' : '✗ Rule-based'}
          </span>
        </div>
        <div className="info-row">
          <span className="info-label">Database:</span>
          <span className="info-value">
            {result.system_info.database_connected ? '✓ Connected' : '✗ Disconnected'}
          </span>
        </div>
      </div>
    </div>
  </div>
)}
```

**Display sections:**
1. Certificate metadata
2. Cryptographic analysis with safety indicators
3. Security risk assessment
4. AI-powered migration recommendations
5. System information

---

### 5️⃣ Dashboard.js - Analytics Dashboard

```javascript
import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await apiService.getDashboardStats();
      setStats(response.data.statistics);
    } catch (err) {
      setError('Failed to load dashboard statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="error">{error}</div>;

  const quantumSafePercentage = stats.total_analyzed > 0
    ? Math.round((stats.quantum_safe_count / stats.total_analyzed) * 100)
    : 0;

  return (
    <div className="dashboard">
      <h1>📊 Analytics Dashboard</h1>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Analyzed</h3>
          <p className="stat-number">{stats.total_analyzed}</p>
        </div>
        
        <div className="stat-card safe">
          <h3>Quantum Safe</h3>
          <p className="stat-number">{stats.quantum_safe_count}</p>
        </div>
        
        <div className="stat-card vulnerable">
          <h3>Classical/Vulnerable</h3>
          <p className="stat-number">{stats.classical_count}</p>
        </div>
        
        <div className="stat-card">
          <h3>Quantum Safety Rate</h3>
          <p className="stat-number">{quantumSafePercentage}%</p>
        </div>
      </div>
      
      <div className="data-source">
        Data source: {stats.data_source === 'database' ? 'Azure SQL Database' : 'Local File'}
      </div>
    </div>
  );
};
```

**Features:**
- Auto-loads statistics on mount
- Calculates percentage
- Color-coded cards
- Data source indicator

---

### 6️⃣ server.js - Production Server

```javascript
const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;

// Serve static files from React build
app.use(express.static(path.join(__dirname, 'build')));

// API proxy (if needed)
// app.use('/api', proxy('https://backend-url.railway.app'));

// Serve index.html for all routes (SPA)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`✅ Server running on http://localhost:${PORT}`);
});
```

**Purpose:**
- Serves React production build
- Handles SPA routing (all routes → index.html)
- Railway.app integration

---

## 💾 Database Schema

### Visual Schema
```
┌─────────────────────────────┐
│  public_key_algorithms      │
├─────────────────────────────┤
│ id (PK)                     │
│ public_key_algorithm_name   │
│ public_key_algorithm_oid    │
│ category                    │
│ is_pqc                      │
└─────────────────────────────┘

┌─────────────────────────────┐
│  signature_algorithms       │
├─────────────────────────────┤
│ id (PK)                     │
│ signature_algorithm_name    │
│ signature_algorithm_oid     │
│ category                    │
│ is_pqc                      │
└─────────────────────────────┘

┌─────────────────────────────┐
│  certificate_analyses       │
├─────────────────────────────┤
│ id (PK)                     │
│ file_name                   │
│ subject                     │
│ issuer                      │
│ expiry_date                 │
│ public_key_algorithm        │
│ signature_algorithm         │
│ is_quantum_safe             │
│ overall_risk_level          │
│ analysis_timestamp          │
│ ai_powered                  │
└─────────────────────────────┘

┌─────────────────────────────┐
│  analytics_summary          │
├─────────────────────────────┤
│ id (PK)                     │
│ total_analyzed              │
│ quantum_safe_count          │
│ classical_count             │
│ last_updated                │
└─────────────────────────────┘
```

### Sample Data

**public_key_algorithms:**
```sql
INSERT INTO public_key_algorithms VALUES
(1, 'RSA', '1.2.840.113549.1.1.1', 'Classical', 0),
(2, 'ECDSA', '1.2.840.10045.2.1', 'Classical', 0),
(3, 'CRYSTALS-Kyber', '1.3.6.1.4.1.2.267.7.6.5', 'PQC', 1),
(4, 'CRYSTALS-Dilithium', '1.3.6.1.4.1.2.267.7.8.7', 'PQC', 1);
```

**signature_algorithms:**
```sql
INSERT INTO signature_algorithms VALUES
(1, 'sha256WithRSAEncryption', '1.2.840.113549.1.1.11', 'Classical', 0),
(2, 'ecdsa-with-SHA256', '1.2.840.10045.4.3.2', 'Classical', 0),
(3, 'CRYSTALS-Dilithium2', '1.3.6.1.4.1.2.267.7.8.7', 'PQC', 1);
```

---

## 🔌 API Endpoints

### Complete API Reference

#### 1. Root Endpoint
```http
GET /
```

**Response:**
```json
{
  "message": "QuantumCertify API - AI-Powered PQC Analysis",
  "version": "2.0.0",
  "features": [
    "X.509 Certificate Analysis",
    "Quantum-Safe Algorithm Detection",
    "Google Gemini AI Recommendations",
    "PQC Migration Strategies",
    "Security Risk Assessment"
  ],
  "ai_status": "Gemini AI Enabled",
  "contact": "support@quantumcertify.com",
  "developer": "QuantumCertify Team"
}
```

#### 2. Upload Certificate
```http
POST /upload-certificate
Content-Type: multipart/form-data

file: <certificate.pem>
```

**Response:**
```json
{
  "file_name": "certificate.pem",
  "certificate_info": {
    "issuer": "CN=Example CA,O=Example Corp",
    "subject": "CN=example.com,O=Example Inc",
    "valid_from": "2024-01-01T00:00:00+00:00",
    "valid_until": "2025-01-01T00:00:00+00:00",
    "serial_number": "123456789",
    "version": "v3"
  },
  "cryptographic_analysis": {
    "public_key": {
      "algorithm": "RSA",
      "type": "RSAPublicKey",
      "size": 2048,
      "is_quantum_safe": false,
      "oid": "1.2.840.113549.1.1.1"
    },
    "signature": {
      "algorithm": "sha256WithRSAEncryption",
      "is_quantum_safe": false,
      "oid": "1.2.840.113549.1.1.11"
    }
  },
  "security_assessment": {
    "overall_quantum_safety": "VULNERABLE",
    "risk_level": "HIGH",
    "migration_urgency": "High Priority"
  },
  "ai_recommendations": {
    "public_key": {
      "quantum_vulnerability": "HIGH - Broken by Shor's algorithm",
      "recommended_pqc_algorithms": ["CRYSTALS-Kyber", "FrodoKEM"],
      "primary_recommendation": "CRYSTALS-Kyber for key exchange...",
      "security_assessment": "RSA is highly vulnerable...",
      "performance_comparison": "Kyber offers excellent performance...",
      "migration_strategy": "Begin migration within 2-3 years...",
      "risk_timeline": "2-3 years",
      "implementation_considerations": "...",
      "compliance_notes": "...",
      "cost_benefit_analysis": "..."
    },
    "signature": {
      // Similar structure
    }
  },
  "system_info": {
    "analysis_timestamp": "2025-10-09T13:00:00.000000Z",
    "database_connected": true,
    "ai_powered": true,
    "ai_provider": "Google Gemini",
    "api_version": "2.0.0"
  },
  "status": "Certificate analysis completed successfully"
}
```

#### 3. Dashboard Statistics
```http
GET /dashboard/stats
```

**Response:**
```json
{
  "statistics": {
    "total_analyzed": 150,
    "quantum_safe_count": 25,
    "classical_count": 125,
    "last_updated": "2025-10-09T13:00:00.000000Z",
    "data_source": "database"
  },
  "status": "Statistics retrieved successfully"
}
```

#### 4. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-09T13:00:00.000000Z",
  "version": "2.0.0",
  "services": {
    "database": "available",
    "ai_service": "available",
    "ai_provider": "Google Gemini"
  },
  "contact": "support@quantumcertify.com",
  "developer": "QuantumCertify Team"
}
```

#### 5. PQC Algorithms Information
```http
GET /algorithms/pqc
```

**Response:**
```json
{
  "pqc_algorithms": {
    "nist_standardized": {
      "key_exchange": [{
        "name": "CRYSTALS-Kyber",
        "security_levels": ["Kyber-512", "Kyber-768", "Kyber-1024"],
        "type": "Lattice-based",
        "status": "NIST Standard",
        "characteristics": "Fast key generation..."
      }],
      "digital_signatures": [{
        "name": "CRYSTALS-Dilithium",
        "security_levels": ["Dilithium2", "Dilithium3", "Dilithium5"],
        "type": "Lattice-based",
        "status": "NIST Standard",
        "characteristics": "Fast signing..."
      }]
    },
    "hybrid_approaches": {
      "description": "Combine classical and post-quantum...",
      "examples": ["RSA + Kyber", "ECDSA + Dilithium"]
    },
    "migration_timeline": {
      "immediate": "Begin evaluation and planning",
      "short_term": "Implement hybrid solutions (1-2 years)",
      "medium_term": "Full PQC migration (3-5 years)",
      "long_term": "Complete quantum-safe infrastructure (5-10 years)"
    }
  },
  "last_updated": "2025-10-09T13:00:00.000000Z",
  "status": "PQC algorithm information retrieved successfully"
}
```

---

## 🚀 Deployment

### Environment Variables

**Backend (Railway):**
```bash
# Database
DB_SERVER=quantumcertify-sqlsrv.database.windows.net
DB_NAME=QuantumCertifyDB
DB_USERNAME=your-username
DB_PASSWORD=your-password

# AI Service
GEMINI_API_KEY=your-gemini-api-key

# Application
ENVIRONMENT=production
PROJECT_VERSION=2.0.0
CONTACT_EMAIL=support@quantumcertify.com
DEVELOPER_NAME=QuantumCertify Team

# Security
ALLOWED_ORIGINS=https://your-frontend-url.railway.app
SSL_ENABLED=true
FORCE_HTTPS=false  # Railway handles HTTPS at edge
SECURE_COOKIES=true

# Railway (auto-provided)
PORT=8080
```

**Frontend (Railway):**
```bash
REACT_APP_API_URL=https://your-backend-url.railway.app
PORT=8080
NODE_ENV=production
```

### Railway Deployment Files

**nixpacks.toml (Backend):**
```toml
[phases.install]
cmds = [
  "apt-get update",
  "apt-get install -y python3 python3-pip"
]

[phases.build]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "python3 run_server.py"
```

**Dockerfile (Backend):**
```dockerfile
FROM python:3.12-slim

WORKDIR /app/backend

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8080

# Start server
CMD ["python3", "run_server.py"]
```

### Deployment Flow

```
1. Code Push to GitHub
   │
   ├─► Railway detects push
   │
   ├─► Build phase
   │   ├─ Install Python/Node
   │   ├─ Install dependencies
   │   └─ Build application
   │
   ├─► Deploy phase
   │   ├─ Start container
   │   ├─ Health check
   │   └─ Route traffic
   │
   └─► Live! 🚀
```

---

## 🔄 Complete Code Flow

### Certificate Analysis Flow

```
1. USER ACTION
   └─► Selects certificate file (.pem/.crt/.cer/.der)
   └─► Clicks "Analyze Certificate"

2. FRONTEND (CertificateUpload.js)
   └─► handleSubmit() called
   └─► Creates FormData with file
   └─► apiService.uploadCertificate(file)
   └─► Shows loading spinner

3. API CLIENT (api.js)
   └─► axios.post('/upload-certificate', formData)
   └─► Sends multipart/form-data request

4. BACKEND (main.py)
   └─► @app.post("/upload-certificate") receives request
   └─► Reads file bytes
   └─► Parses certificate (PEM or DER)
        ├─► x509.load_pem_x509_certificate()
        └─► x509.load_der_x509_certificate()
   
5. CERTIFICATE PARSING
   └─► Extract metadata
        ├─► issuer, subject
        ├─► valid_from, valid_until
        ├─► serial_number
        └─► version
   └─► Extract cryptographic info
        ├─► public_key (type, size, algorithm)
        └─► signature_algorithm (OID, name)

6. DATABASE LOOKUP (if available)
   └─► Query public_key_algorithms table
        └─► Match by OID or name
        └─► Get is_pqc flag
   └─► Query signature_algorithms table
        └─► Match by OID or name
        └─► Get is_pqc flag

7. FALLBACK ANALYSIS (if DB unavailable)
   └─► _analyze_pqc_algorithm()
        └─► Search for PQC keywords
        └─► Return is_pqc boolean

8. SECURITY ASSESSMENT
   └─► Determine overall quantum safety
        └─► Both algorithms PQC? → SAFE
        └─► Either classical? → VULNERABLE
   └─► Calculate risk level
        └─► SAFE → LOW risk
        └─► VULNERABLE → HIGH risk

9. AI RECOMMENDATIONS (for vulnerable algorithms)
   └─► If public_key not PQC:
        ├─► Build context (key_size, expiry, etc.)
        ├─► _get_gemini_recommendations()
        │    ├─► Build detailed prompt
        │    ├─► Call Gemini API
        │    ├─► Parse JSON response
        │    └─► Return recommendations
        └─► Fallback to _get_rule_based_recommendations()
   
   └─► If signature not PQC:
        └─► Same process for signature algorithm

10. BUILD RESPONSE
    └─► Combine all data:
         ├─► Certificate info
         ├─► Cryptographic analysis
         ├─► Security assessment
         ├─► AI recommendations
         └─► System info

11. SAVE TO DATABASE/FILE
    └─► save_certificate_analysis()
         ├─► Try database first
         │    ├─► Insert into certificate_analyses
         │    └─► Update analytics_summary
         └─► Fallback to JSON file
              └─► Update statistics.json

12. RETURN RESPONSE
    └─► JSONResponse(content=response_data)
    └─► Send to frontend

13. FRONTEND RENDERING
    └─► setResult(response.data)
    └─► Display results:
         ├─► Certificate Information card
         ├─► Cryptographic Analysis card
         ├─► Security Assessment card
         ├─► AI Recommendations card
         └─► System Information card

14. USER SEES RESULTS ✨
```

### Dashboard Statistics Flow

```
1. USER NAVIGATES
   └─► Clicks "Dashboard" link

2. FRONTEND (Dashboard.js)
   └─► useEffect() triggers on mount
   └─► fetchStats() called
   └─► apiService.getDashboardStats()

3. API CLIENT
   └─► axios.get('/dashboard/stats')

4. BACKEND
   └─► @app.get("/dashboard/stats")
   └─► get_dashboard_statistics(db)
        ├─► Try database query first
        │    └─► SELECT * FROM analytics_summary
        └─► Fallback to file
             └─► Read statistics.json

5. RETURN DATA
   └─► {
        total_analyzed: 150,
        quantum_safe_count: 25,
        classical_count: 125,
        last_updated: "...",
        data_source: "database"
       }

6. FRONTEND RENDERING
   └─► Calculate percentage
   └─► Display stat cards:
        ├─► Total Analyzed
        ├─► Quantum Safe (green)
        ├─► Classical/Vulnerable (red)
        └─► Quantum Safety Rate (%)

7. USER SEES DASHBOARD 📊
```

---

## 🎓 Key Concepts Explained

### 1. Post-Quantum Cryptography (PQC)
**Problem**: Quantum computers can break RSA, ECDSA, DH, ECDH using Shor's algorithm

**Solution**: New algorithms resistant to quantum attacks:
- **CRYSTALS-Kyber**: Key exchange
- **CRYSTALS-Dilithium**: Digital signatures
- **FALCON**: Compact signatures
- **SPHINCS+**: Hash-based signatures

### 2. X.509 Certificates
Digital documents that:
- Prove identity (subject)
- Contain public key
- Signed by Certificate Authority (issuer)
- Have validity period
- Use cryptographic algorithms

### 3. Quantum Safety Analysis
Certificate is quantum-safe ONLY if:
- ✅ Public key algorithm is PQC
- ✅ Signature algorithm is PQC
- ❌ If either is classical → VULNERABLE

### 4. Hybrid Approach
During migration period:
- Use BOTH classical AND PQC algorithms
- Example: RSA + Kyber for key exchange
- Provides backward compatibility
- Ensures quantum resistance

### 5. AI-Powered Recommendations
Google Gemini provides:
- Threat assessment
- Specific PQC algorithm recommendations
- Migration timelines
- Performance comparisons
- Implementation guidance
- Cost-benefit analysis

---

## 📚 Learning Path

### For Beginners
1. **Start with Frontend**:
   - Understand React components
   - Follow data flow in CertificateUpload.js
   - See how state management works

2. **Learn API Communication**:
   - Study api.js
   - Understand axios requests
   - See how errors are handled

3. **Explore Backend Basics**:
   - Read main.py endpoints
   - Understand request/response cycle
   - See how files are processed

### For Intermediate
1. **Database Integration**:
   - Study models.py
   - Understand SQLAlchemy ORM
   - See fallback mechanisms

2. **Certificate Parsing**:
   - Learn cryptography library
   - Understand X.509 structure
   - See OID lookups

3. **AI Integration**:
   - Study Gemini API calls
   - Understand prompt engineering
   - See JSON parsing

### For Advanced
1. **Security**:
   - Middleware implementation
   - CORS configuration
   - CSP headers
   - Input validation

2. **Performance**:
   - Database connection pooling
   - Async/await patterns
   - Error handling strategies

3. **Deployment**:
   - Railway.app configuration
   - Environment management
   - CI/CD pipeline

---

## 🛠️ Common Tasks

### Add a New Algorithm
```python
# 1. Add to database
INSERT INTO public_key_algorithms VALUES
(5, 'NewPQC', '1.2.3.4.5', 'PQC', 1);

# 2. Add to mapping (if needed)
"NewPQC": {
    "quantum_threat": "LOW - Quantum resistant",
    "recommended_pqc": {...}
}
```

### Modify AI Prompt
```python
# In _get_gemini_recommendations()
prompt = f"""
Your updated instructions here...

ANALYSIS TARGET:
- Algorithm: {algorithm_name}
- New field: {new_data}

Focus on:
1. Your new requirement
2. Additional analysis
...
"""
```

### Add New Endpoint
```python
@app.get("/new-endpoint")
def new_endpoint(db: Session = Depends(get_db)):
    # Your logic here
    return {"result": "data"}
```

### Add Frontend Feature
```javascript
// In CertificateUpload.js
const [newState, setNewState] = useState(null);

const handleNewAction = async () => {
  try {
    const response = await apiService.newEndpoint();
    setNewState(response.data);
  } catch (err) {
    setError(err.message);
  }
};
```

---

## 🐛 Debugging Tips

### Backend Issues
```python
# Add logging
import logging
logging.info(f"Debug: {variable}")

# Check database connection
if db is None:
    logging.error("Database unavailable")

# Print response before returning
print(json.dumps(response_data, indent=2))
```

### Frontend Issues
```javascript
// Use console.log
console.log('State:', result);
console.log('Error:', error);

// Check API response
.then(response => {
  console.log('Raw response:', response);
  return response.data;
})
```

### Railway Logs
- View deployment logs in Railway dashboard
- Check for build errors
- Monitor runtime logs
- Check environment variables

---

## 🎯 Next Steps

1. **Enhance AI Prompts**: Fine-tune Gemini recommendations
2. **Add More Algorithms**: Expand PQC algorithm database
3. **Improve UI/UX**: Better visualizations, charts
4. **Add Authentication**: User accounts, API keys
5. **Batch Processing**: Upload multiple certificates
6. **Export Reports**: PDF/CSV generation
7. **Email Notifications**: Alert on vulnerable certificates
8. **API Rate Limiting**: Prevent abuse
9. **Caching**: Improve performance
10. **Testing**: Unit tests, integration tests

---

**Happy coding! 🚀 If you have questions about any specific part, let me know!**
