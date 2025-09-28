from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import logging
import os
from typing import Dict
import json
import re
import time

# Import production logging configuration
from .logging_config import setup_production_logging, security_logger, performance_logger

# Initialize production logging
setup_production_logging()

# Import database components with error handling
try:
    from .database import SessionLocal
    from .models import PublicKeyAlgorithm, SignatureAlgorithm, CertificateAnalysis, AnalyticsSummary
    DATABASE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Database import error: {e}. Running without database.")
    DATABASE_AVAILABLE = False

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning("python-dotenv not available. Using system environment variables.")

# Application configuration from environment variables
APP_VERSION = os.getenv("PROJECT_VERSION", "2.0.0")
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "support@quantumcertify.com")
DEVELOPER_NAME = os.getenv("DEVELOPER_NAME", "QuantumCertify Team")
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"

# Google Gemini AI Integration
try:
    import google.generativeai as genai
    
    # Configure Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        AI_AVAILABLE = True
        logging.info("Gemini AI initialized successfully")
    else:
        AI_AVAILABLE = False
        logging.warning("Gemini API key not found")
        
except ImportError as e:
    logging.warning(f"Gemini AI not available: {e}. AI recommendations will be rule-based.")
    AI_AVAILABLE = False

def _analyze_pqc_algorithm(algorithm_name: str) -> bool:
    """
    Basic fallback analysis for PQC algorithms when database is unavailable
    """
    pqc_keywords = [
        'dilithium', 'kyber', 'falcon', 'mceliece', 'frodo', 'saber', 
        'ntru', 'bike', 'crystals', 'sphincs', 'picnic', 'rainbow'
    ]
    algorithm_lower = algorithm_name.lower()
    return any(keyword in algorithm_lower for keyword in pqc_keywords)

def _get_classical_to_pqc_mapping() -> Dict[str, Dict]:
    """
    Comprehensive mapping of classical algorithms to recommended PQC alternatives
    """
    return {
        "RSA": {
            "type": "Asymmetric Encryption & Digital Signature",
            "quantum_threat": "HIGH - Broken by Shor's algorithm",
            "recommended_pqc": {
                "key_exchange": ["CRYSTALS-Kyber", "FrodoKEM", "BIKE"],
                "digital_signature": ["CRYSTALS-Dilithium", "FALCON", "SPHINCS+"]
            },
            "primary_recommendation": "CRYSTALS-Kyber for key exchange, CRYSTALS-Dilithium for signatures",
            "security_level": "NIST Level 1/3/5 (128/192/256-bit equivalent)",
            "performance": "Kyber: Excellent performance, Dilithium: Fast signing/verification",
            "migration_priority": "HIGH",
            "timeline": "Begin migration within 2-3 years"
        },
        "ECDSA": {
            "type": "Digital Signature",
            "quantum_threat": "HIGH - Broken by Shor's algorithm",
            "recommended_pqc": {
                "digital_signature": ["CRYSTALS-Dilithium", "FALCON", "SPHINCS+"]
            },
            "primary_recommendation": "CRYSTALS-Dilithium (fastest) or FALCON (smallest signatures)",
            "security_level": "NIST Level 1/3/5",
            "performance": "Dilithium: Fastest, FALCON: Compact signatures, SPHINCS+: Conservative choice",
            "migration_priority": "HIGH",
            "timeline": "Begin migration within 2-3 years"
        },
        "ECDH": {
            "type": "Key Exchange",
            "quantum_threat": "HIGH - Broken by Shor's algorithm",
            "recommended_pqc": {
                "key_exchange": ["CRYSTALS-Kyber", "FrodoKEM", "BIKE", "Classic McEliece"]
            },
            "primary_recommendation": "CRYSTALS-Kyber for most applications",
            "security_level": "NIST Level 1/3/5",
            "performance": "Excellent key generation and encapsulation performance",
            "migration_priority": "HIGH",
            "timeline": "Begin migration within 2-3 years"
        },
        "DSA": {
            "type": "Digital Signature",
            "quantum_threat": "HIGH - Broken by Shor's algorithm",
            "recommended_pqc": {
                "digital_signature": ["CRYSTALS-Dilithium", "FALCON", "SPHINCS+"]
            },
            "primary_recommendation": "CRYSTALS-Dilithium for general use",
            "security_level": "NIST Level 1/3/5",
            "performance": "Superior signing and verification performance",
            "migration_priority": "HIGH",
            "timeline": "Begin migration within 2-3 years"
        },
        "DH": {
            "type": "Key Exchange",
            "quantum_threat": "HIGH - Broken by Shor's algorithm",
            "recommended_pqc": {
                "key_exchange": ["CRYSTALS-Kyber", "FrodoKEM", "Classic McEliece"]
            },
            "primary_recommendation": "CRYSTALS-Kyber with hybrid approach initially",
            "security_level": "NIST Level 1/3/5",
            "performance": "Moderate increase in key sizes, excellent speed",
            "migration_priority": "HIGH",
            "timeline": "Begin migration within 2-3 years"
        }
    }

async def _get_gemini_recommendations(algorithm_name: str, algorithm_type: str, context: Dict) -> Dict:
    """
    Get AI-powered recommendations using Google Gemini
    """
    if not AI_AVAILABLE:
        return _get_rule_based_recommendations(algorithm_name, algorithm_type)
    
    try:
        prompt = f"""
        You are a post-quantum cryptography expert analyzing certificate algorithms for quantum resistance migration.

        ANALYSIS TARGET:
        - Algorithm: {algorithm_name}
        - Type: {algorithm_type}
        - Context: {json.dumps(context, indent=2)}

        Please provide a comprehensive analysis in the following JSON format:
        {{
            "quantum_vulnerability": "HIGH/MEDIUM/LOW assessment of quantum threat",
            "recommended_pqc_algorithms": ["specific NIST-standardized PQC algorithms"],
            "primary_recommendation": "main recommended algorithm with detailed reasoning",
            "security_assessment": "detailed security implications and quantum threat timeline",
            "performance_comparison": "expected performance changes and optimization strategies",
            "migration_strategy": "step-by-step migration approach including hybrid solutions",
            "implementation_considerations": "key technical implementation requirements and challenges",
            "compliance_notes": "regulatory and standards compliance information",
            "risk_timeline": "specific timeline recommendations based on quantum computing advancement",
            "cost_benefit_analysis": "migration costs vs security benefits assessment"
        }}

        FOCUS AREAS:
        1. Prioritize NIST-standardized algorithms: CRYSTALS-Kyber, CRYSTALS-Dilithium, FALCON, SPHINCS+
        2. Consider hybrid approaches for gradual migration
        3. Address specific use case requirements
        4. Provide actionable, practical recommendations
        5. Include performance benchmarks where relevant

        Provide ONLY the JSON response, no additional text.
        """

        response = model.generate_content(prompt)
        ai_response = response.text
        
        # Clean up the response to extract JSON
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error: {e}")
                return _get_rule_based_recommendations(algorithm_name, algorithm_type)
        else:
            logging.warning("No JSON found in Gemini response")
            return _get_rule_based_recommendations(algorithm_name, algorithm_type)

    except Exception as e:
        logging.error(f"Gemini AI recommendation error: {e}")
        return _get_rule_based_recommendations(algorithm_name, algorithm_type)

def _get_rule_based_recommendations(algorithm_name: str, algorithm_type: str) -> Dict:
    """
    Enhanced rule-based recommendations as fallback
    """
    mapping = _get_classical_to_pqc_mapping()
    
    # Clean algorithm name for matching
    clean_name = algorithm_name.upper().replace("WITH", "").replace("ENCRYPTION", "").strip()
    
    # Find matching algorithm
    recommendation = None
    matched_alg = None
    for classical_alg, pqc_info in mapping.items():
        if classical_alg in clean_name or clean_name.startswith(classical_alg):
            recommendation = pqc_info
            matched_alg = classical_alg
            break
    
    if not recommendation:
        return {
            "quantum_vulnerability": "MEDIUM - Requires manual assessment",
            "recommended_pqc_algorithms": ["CRYSTALS-Kyber", "CRYSTALS-Dilithium"],
            "primary_recommendation": "Comprehensive evaluation needed - Consider CRYSTALS suite for general quantum-resistance",
            "security_assessment": "Algorithm not in standard mapping - requires expert cryptographic analysis",
            "performance_comparison": "Performance impact varies significantly by chosen PQC algorithm and implementation",
            "migration_strategy": "1. Assess current usage patterns 2. Evaluate PQC options 3. Implement hybrid approach 4. Full migration",
            "implementation_considerations": "Consult with cryptography experts and conduct thorough compatibility testing",
            "compliance_notes": "Verify compliance with organizational security policies and regulatory requirements",
            "risk_timeline": "Evaluate within 2-5 years based on quantum computing developments",
            "cost_benefit_analysis": "Migration costs must be weighed against quantum threat timeline and organizational risk tolerance"
        }
    
    all_pqc_algs = []
    if "key_exchange" in recommendation["recommended_pqc"]:
        all_pqc_algs.extend(recommendation["recommended_pqc"]["key_exchange"])
    if "digital_signature" in recommendation["recommended_pqc"]:
        all_pqc_algs.extend(recommendation["recommended_pqc"]["digital_signature"])
    
    return {
        "quantum_vulnerability": recommendation["quantum_threat"],
        "recommended_pqc_algorithms": list(set(all_pqc_algs)),
        "primary_recommendation": recommendation["primary_recommendation"],
        "security_assessment": f"{matched_alg} is {recommendation['quantum_threat']}. {recommendation['security_level']} provides robust quantum resistance.",
        "performance_comparison": recommendation["performance"],
        "migration_strategy": f"Priority: {recommendation['migration_priority']}. Recommended timeline: {recommendation['timeline']}",
        "implementation_considerations": f"Algorithm type: {recommendation['type']}. Consider hybrid deployment initially.",
        "compliance_notes": "Ensure compliance with NIST Post-Quantum Cryptography standards and organizational policies",
        "risk_timeline": recommendation["timeline"],
        "cost_benefit_analysis": f"High priority migration due to {recommendation['migration_priority']} quantum threat level"
    }

# Production security configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
SSL_ENABLED = os.getenv("SSL_ENABLED", "false").lower() == "true"
FORCE_HTTPS = os.getenv("FORCE_HTTPS", "false").lower() == "true"
SECURE_COOKIES = os.getenv("SECURE_COOKIES", "false").lower() == "true"

# Initialize FastAPI app with environment configuration
app = FastAPI(
    title="QuantumCertify API - AI-Powered PQC Analysis",
    description="Advanced certificate analysis with Google Gemini AI recommendations for post-quantum cryptography migration",
    version=APP_VERSION,
    contact={
        "name": DEVELOPER_NAME,
        "email": CONTACT_EMAIL,
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs" if DEBUG_MODE else None,  # Disable docs in production
    redoc_url="/redoc" if DEBUG_MODE else None,  # Disable redoc in production
)

# Production Security Middleware
if ENVIRONMENT == "production":
    # Note: Railway handles HTTPS at the edge, so we don't need HTTPSRedirectMiddleware
    # This prevents healthcheck 307 redirects that cause deployment failures
    # if FORCE_HTTPS:
    #     app.add_middleware(HTTPSRedirectMiddleware)
    
    # Trusted host middleware for production domains
    # Include Railway.app domains and localhost for health checks
    TRUSTED_HOSTS = [
        "quantumcertify.tech", 
        "www.quantumcertify.tech", 
        "api.quantumcertify.tech",
        "web-production-bf0b7.up.railway.app",  # Your specific Railway domain
        "*.railway.app",  # Railway.app domains
        "*.up.railway.app",  # Railway.app internal domains
        "testserver",  # For testing
        "localhost",  # For local health checks
        "127.0.0.1"   # For IP-based health checks
    ]
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=TRUSTED_HOSTS
    )

# Enhanced CORS middleware with environment configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Restrict methods in production
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
    ],
    expose_headers=["X-Process-Time"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Security headers for production
    if ENVIRONMENT == "production":
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.quantumcertify.tech; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
    
    # Performance monitoring header
    import time
    process_time = time.time() - request.state.start_time if hasattr(request.state, 'start_time') else 0
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Request timing and logging middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    request.state.start_time = start_time
    
    # Get client IP
    client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
    
    response = await call_next(request)
    
    # Log request performance
    process_time = time.time() - start_time
    performance_logger.log_request_performance(
        endpoint=str(request.url.path),
        method=request.method,
        duration=process_time,
        status_code=response.status_code,
        ip_address=client_ip
    )
    
    # Log access
    access_logger = logging.getLogger('access')
    access_logger.info(
        f"{request.method} {request.url.path} - {response.status_code}",
        extra={
            'extra_data': {
                'method': request.method,
                'path': request.url.path,
                'status_code': response.status_code,
                'duration': process_time,
                'ip_address': client_ip,
                'user_agent': request.headers.get('User-Agent')
            }
        }
    )
    
    return response

# Dependency to get DB session
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

# File-based Statistics Management (Fallback when database is unavailable)
STATS_FILE_PATH = "statistics.json"

def load_statistics_from_file():
    """Load statistics from JSON file"""
    try:
        if os.path.exists(STATS_FILE_PATH):
            with open(STATS_FILE_PATH, 'r') as f:
                stats = json.load(f)
                return stats
        else:
            # Initialize with default values
            default_stats = {
                "total_analyzed": 0,
                "quantum_safe_count": 0,
                "classical_count": 0,
                "last_updated": None,
                "data_source": "file"
            }
            save_statistics_to_file(default_stats)
            return default_stats
    except Exception as e:
        logging.error(f"Error loading statistics from file: {e}")
        return {
            "total_analyzed": 0,
            "quantum_safe_count": 0,
            "classical_count": 0,
            "last_updated": None,
            "data_source": "error"
        }

def save_statistics_to_file(stats):
    """Save statistics to JSON file"""
    try:
        stats["last_updated"] = datetime.utcnow().isoformat()
        with open(STATS_FILE_PATH, 'w') as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        logging.error(f"Error saving statistics to file: {e}")

# Statistics Management Functions
def save_certificate_analysis(db: Session, analysis_data: dict):
    """Save certificate analysis to database or file for tracking"""
    # Determine if certificate is quantum safe
    is_quantum_safe = False
    if analysis_data.get('cryptographic_analysis'):
        public_key_safe = analysis_data['cryptographic_analysis'].get('public_key', {}).get('is_quantum_safe', False)
        signature_safe = analysis_data['cryptographic_analysis'].get('signature', {}).get('is_quantum_safe', False)
        is_quantum_safe = public_key_safe and signature_safe
    
    # Try database first, then fallback to file
    if db and DATABASE_AVAILABLE:
        try:
            # Save individual analysis record
            certificate_record = CertificateAnalysis(
                file_name=analysis_data.get('file_name', ''),
                subject=analysis_data.get('certificate_info', {}).get('subject', ''),
                issuer=analysis_data.get('certificate_info', {}).get('issuer', ''),
                public_key_algorithm=analysis_data.get('cryptographic_analysis', {}).get('public_key', {}).get('algorithm', ''),
                signature_algorithm=analysis_data.get('cryptographic_analysis', {}).get('signature', {}).get('algorithm', ''),
                is_quantum_safe=is_quantum_safe,
                overall_risk_level=analysis_data.get('security_assessment', {}).get('risk_level', 'UNKNOWN'),
                ai_powered=analysis_data.get('system_info', {}).get('ai_powered', False)
            )
            
            db.add(certificate_record)
            db.commit()
            
            # Update analytics summary
            update_analytics_summary(db, is_quantum_safe)
            return
            
        except Exception as e:
            logging.error(f"Error saving certificate analysis to database: {e}")
            db.rollback()
    
    # Fallback to file-based storage
    try:
        stats = load_statistics_from_file()
        stats["total_analyzed"] += 1
        if is_quantum_safe:
            stats["quantum_safe_count"] += 1
        else:
            stats["classical_count"] += 1
        save_statistics_to_file(stats)
        logging.info(f"Certificate analysis saved to file. Quantum Safe: {is_quantum_safe}")
    except Exception as e:
        logging.error(f"Error saving certificate analysis to file: {e}")

def update_analytics_summary(db: Session, is_quantum_safe: bool):
    """Update the analytics summary table"""
    if not db or not DATABASE_AVAILABLE:
        return
    
    try:
        # Get or create analytics summary record
        summary = db.query(AnalyticsSummary).first()
        
        if not summary:
            summary = AnalyticsSummary(
                total_analyzed=1,
                quantum_safe_count=1 if is_quantum_safe else 0,
                classical_count=0 if is_quantum_safe else 1
            )
            db.add(summary)
        else:
            summary.total_analyzed += 1
            if is_quantum_safe:
                summary.quantum_safe_count += 1
            else:
                summary.classical_count += 1
        
        db.commit()
        
    except Exception as e:
        logging.error(f"Error updating analytics summary: {e}")
        db.rollback()

def get_dashboard_statistics(db: Session):
    """Get dashboard statistics from database or file"""
    # Try database first
    if db and DATABASE_AVAILABLE:
        try:
            summary = db.query(AnalyticsSummary).first()
            
            if summary:
                return {
                    "total_analyzed": summary.total_analyzed,
                    "quantum_safe_count": summary.quantum_safe_count,
                    "classical_count": summary.classical_count,
                    "last_updated": summary.last_updated.isoformat() if summary.last_updated else None,
                    "data_source": "database"
                }
                
        except Exception as e:
            logging.error(f"Error retrieving dashboard statistics from database: {e}")
    
    # Fallback to file-based storage
    try:
        stats = load_statistics_from_file()
        return {
            "total_analyzed": stats["total_analyzed"],
            "quantum_safe_count": stats["quantum_safe_count"],
            "classical_count": stats["classical_count"],
            "last_updated": stats.get("last_updated"),
            "data_source": "file"
        }
    except Exception as e:
        logging.error(f"Error retrieving dashboard statistics from file: {e}")
        return {
            "total_analyzed": 0,
            "quantum_safe_count": 0,
            "classical_count": 0,
            "last_updated": None,
            "data_source": "error"
        }

@app.get("/")
def read_root():
    return {
        "message": "QuantumCertify API - AI-Powered Post-Quantum Cryptography Analysis", 
        "version": APP_VERSION,
        "features": [
            "X.509 Certificate Analysis",
            "Quantum-Safe Algorithm Detection", 
            "Google Gemini AI Recommendations",
            "PQC Migration Strategies",
            "Security Risk Assessment"
        ],
        "ai_status": "Gemini AI Enabled" if AI_AVAILABLE else "Rule-based Analysis",
        "contact": CONTACT_EMAIL,
        "developer": DEVELOPER_NAME
    }

@app.post("/upload-certificate")
async def upload_certificate(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload and analyze a certificate file with AI-powered PQC migration recommendations
    
    Supports PEM and DER formats (.pem, .crt, .cer, .der)
    Returns comprehensive analysis including Gemini AI recommendations for quantum-safe migration
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    try:
        cert_bytes = await file.read()

        # Try to parse the certificate
        try:
            cert = x509.load_pem_x509_certificate(cert_bytes, default_backend())
        except Exception:
            try:
                cert = x509.load_der_x509_certificate(cert_bytes, default_backend())
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid certificate format: {str(e)}")

        # Extract certificate details
        issuer = cert.issuer.rfc4514_string()
        subject = cert.subject.rfc4514_string()
        public_key = cert.public_key()
        key_type = public_key.__class__.__name__
        key_size = getattr(public_key, "key_size", None)

        # Signature algorithm (OID + name)
        sig_oid = cert.signature_algorithm_oid.dotted_string
        sig_name = cert.signature_algorithm_oid._name

        # Public key algorithm (name only — OIDs depend on key type)
        pubkey_name = key_type
        pubkey_oid = getattr(getattr(public_key, "oid", None), "dotted_string", None)

        # --- DB Lookup Logic with fallback ---
        pubkey_algo = None
        sig_algo = None
        
        if db and DATABASE_AVAILABLE:
            try:
                # Public Key Algorithm
                if pubkey_oid:
                    pubkey_algo = db.query(PublicKeyAlgorithm).filter_by(public_key_algorithm_oid=pubkey_oid).first()
                if not pubkey_algo:
                    pubkey_algo = db.query(PublicKeyAlgorithm).filter_by(public_key_algorithm_name=pubkey_name).first()

                # Signature Algorithm
                sig_algo = db.query(SignatureAlgorithm).filter_by(signature_algorithm_oid=sig_oid).first()
                if not sig_algo:
                    sig_algo = db.query(SignatureAlgorithm).filter_by(signature_algorithm_name=sig_name).first()
            except SQLAlchemyError as e:
                logging.error(f"Database query error: {e}")

        # Algorithm analysis with enhanced PQC detection
        pubkey_algorithm_name = pubkey_algo.public_key_algorithm_name if pubkey_algo else pubkey_name
        pubkey_is_pqc = pubkey_algo.is_pqc if pubkey_algo else _analyze_pqc_algorithm(pubkey_name)

        sig_algorithm_name = sig_algo.signature_algorithm_name if sig_algo else sig_name
        sig_is_pqc = sig_algo.is_pqc if sig_algo else _analyze_pqc_algorithm(sig_name)

        # Generate AI recommendations for non-PQC algorithms
        recommendations = {}
        security_assessment = {
            "overall_quantum_safety": "SAFE" if (pubkey_is_pqc and sig_is_pqc) else "VULNERABLE",
            "risk_level": "LOW" if (pubkey_is_pqc and sig_is_pqc) else "HIGH",
            "migration_urgency": "Low Priority" if (pubkey_is_pqc and sig_is_pqc) else "High Priority"
        }
        
        # Get AI recommendations for classical algorithms
        if not pubkey_is_pqc:
            context = {
                "algorithm_type": "public_key",
                "key_size": key_size,
                "certificate_type": "X.509",
                "expiry_date": cert.not_valid_after.isoformat(),
                "issuer": issuer,
                "current_usage": "Certificate Public Key"
            }
            recommendations["public_key"] = await _get_gemini_recommendations(
                pubkey_algorithm_name, "public_key", context
            )
        
        if not sig_is_pqc:
            context = {
                "algorithm_type": "digital_signature", 
                "certificate_type": "X.509",
                "expiry_date": cert.not_valid_after.isoformat(),
                "issuer": issuer,
                "current_usage": "Certificate Digital Signature"
            }
            recommendations["signature"] = await _get_gemini_recommendations(
                sig_algorithm_name, "digital_signature", context
            )

        # Enhanced response with AI insights
        response_data = {
            "file_name": file.filename,
            "certificate_info": {
                "issuer": issuer,
                "subject": subject,
                "expiry_date": cert.not_valid_after.isoformat(),
                "serial_number": str(cert.serial_number),
                "version": cert.version.name if hasattr(cert, 'version') else "Unknown"
            },
            "cryptographic_analysis": {
                "public_key": {
                    "algorithm": pubkey_algorithm_name,
                    "type": key_type,
                    "size": key_size,
                    "is_quantum_safe": pubkey_is_pqc,
                    "oid": pubkey_oid
                },
                "signature": {
                    "algorithm": sig_algorithm_name,
                    "is_quantum_safe": sig_is_pqc,
                    "oid": sig_oid
                }
            },
            "security_assessment": security_assessment,
            "ai_recommendations": recommendations,
            "system_info": {
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "database_connected": DATABASE_AVAILABLE and db is not None,
                "ai_powered": AI_AVAILABLE,
                "ai_provider": "Google Gemini" if AI_AVAILABLE else "Rule-based",
                "api_version": APP_VERSION
            },
            "status": "Certificate analysis completed successfully"
        }

        # Save analysis to database for statistics tracking
        try:
            save_certificate_analysis(db, response_data)
        except Exception as e:
            logging.warning(f"Failed to save certificate analysis statistics: {e}")

        return JSONResponse(content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Certificate processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing certificate: {str(e)}")
        logging.error(f"Certificate processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing certificate: {str(e)}")

@app.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get dashboard statistics for the application
    
    Returns statistics about analyzed certificates including quantum-safe vs classical counts
    """
    try:
        stats = get_dashboard_statistics(db)
        return JSONResponse(content={
            "statistics": stats,
            "status": "Statistics retrieved successfully"
        })
    except Exception as e:
        logging.error(f"Error retrieving dashboard statistics: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error retrieving statistics: {str(e)}"}
        )

@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring
    
    Returns system status including database and AI service availability
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": APP_VERSION,
        "services": {
            "database": "available" if DATABASE_AVAILABLE else "unavailable",
            "ai_service": "available" if AI_AVAILABLE else "unavailable",
            "ai_provider": "Google Gemini" if AI_AVAILABLE else "Rule-based"
        },
        "contact": CONTACT_EMAIL,
        "developer": DEVELOPER_NAME
    }

@app.get("/algorithms/pqc")
def get_pqc_algorithms(db: Session = Depends(get_db)):
    """
    Get list of supported post-quantum cryptography algorithms
    
    Returns information about NIST-standardized PQC algorithms and their characteristics
    """
    try:
        pqc_algorithms = {
            "nist_standardized": {
                "key_exchange": [
                    {
                        "name": "CRYSTALS-Kyber",
                        "security_levels": ["Kyber-512", "Kyber-768", "Kyber-1024"],
                        "type": "Lattice-based",
                        "status": "NIST Standard",
                        "characteristics": "Fast key generation and encapsulation, moderate key sizes"
                    }
                ],
                "digital_signatures": [
                    {
                        "name": "CRYSTALS-Dilithium",
                        "security_levels": ["Dilithium2", "Dilithium3", "Dilithium5"],
                        "type": "Lattice-based",
                        "status": "NIST Standard",
                        "characteristics": "Fast signing and verification, larger signature sizes"
                    },
                    {
                        "name": "FALCON",
                        "security_levels": ["FALCON-512", "FALCON-1024"],
                        "type": "Lattice-based",
                        "status": "NIST Standard",
                        "characteristics": "Compact signatures, complex implementation"
                    },
                    {
                        "name": "SPHINCS+",
                        "security_levels": ["SPHINCS+-128s", "SPHINCS+-192s", "SPHINCS+-256s"],
                        "type": "Hash-based",
                        "status": "NIST Standard",
                        "characteristics": "Conservative security assumptions, large signature sizes"
                    }
                ]
            },
            "hybrid_approaches": {
                "description": "Combine classical and post-quantum algorithms for migration",
                "examples": ["RSA + Kyber", "ECDSA + Dilithium", "ECDH + Kyber"]
            },
            "migration_timeline": {
                "immediate": "Begin evaluation and planning",
                "short_term": "Implement hybrid solutions (1-2 years)",
                "medium_term": "Full PQC migration (3-5 years)",
                "long_term": "Complete quantum-safe infrastructure (5-10 years)"
            }
        }
        
        return JSONResponse(content={
            "pqc_algorithms": pqc_algorithms,
            "last_updated": datetime.utcnow().isoformat(),
            "status": "PQC algorithm information retrieved successfully"
        })
        
    except Exception as e:
        logging.error(f"Error retrieving PQC algorithms: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving PQC information: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=DEBUG_MODE)