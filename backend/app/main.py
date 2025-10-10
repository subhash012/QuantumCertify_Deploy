from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request, Body
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
from typing import Dict, List, Optional
from pydantic import BaseModel
import json
import re
import time
import asyncio

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

# Import TLS scanner module
try:
    from .scanner import scan_domain
    SCANNER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Scanner module import error: {e}. Domain scanning unavailable.")
    SCANNER_AVAILABLE = False

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

# Log DEBUG_MODE setting
logging.info(f"🔧 DEBUG_MODE is set to: {DEBUG_MODE}")

# Google Gemini AI Integration
try:
    import google.generativeai as genai
    
    # Configure Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        # Use the latest stable Gemini 2.5 Flash model with optimized settings
        # This is the mid-size multimodal model that supports up to 1 million tokens
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,  # Limit response size for faster generation
        }
        model = genai.GenerativeModel('gemini-2.5-flash', generation_config=generation_config)
        AI_AVAILABLE = True
        logging.info("Gemini AI initialized successfully with gemini-2.5-flash (optimized for speed)")
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
        'ntru', 'bike', 'crystals', 'sphincs', 'picnic', 'rainbow',
        'ml-dsa', 'ml-kem', 'slh-dsa'  # NIST standardized names
    ]
    algorithm_lower = algorithm_name.lower()
    return any(keyword in algorithm_lower for keyword in pqc_keywords)

def _get_classical_to_pqc_mapping() -> Dict[str, Dict]:
    """
    Comprehensive mapping of classical algorithms to recommended PQC alternatives with detailed migration paths
    """
    return {
        "RSA": {
            "type": "Asymmetric Encryption & Digital Signature",
            "quantum_threat": "CRITICAL - Completely broken by Shor's algorithm",
            "recommended_pqc": {
                "key_exchange": ["CRYSTALS-Kyber", "FrodoKEM", "BIKE", "Classic McEliece", "SIKE"],
                "digital_signature": ["CRYSTALS-Dilithium", "FALCON", "SPHINCS+", "Picnic"]
            },
            "primary_recommendation": "CRYSTALS-Kyber for key exchange, CRYSTALS-Dilithium for signatures (NIST Standards)",
            "security_level": "NIST Level 1/3/5 (128/192/256-bit equivalent security)",
            "performance": "Kyber: Excellent speed, small keys; Dilithium: Fast signing/verification; FrodoKEM: Conservative security",
            "migration_priority": "CRITICAL - Immediate action required",
            "timeline": "Start migration NOW - Target completion within 12-24 months",
            "hybrid_approach": "Recommended: RSA + Kyber for transition period, dual signatures (RSA + Dilithium)",
            "key_size_comparison": "RSA-2048: 2048 bits → Kyber-768: 1184 bytes public key, Dilithium2: 1312 bytes public key",
            "use_cases": {
                "TLS/SSL": "CRYSTALS-Kyber for key exchange, Dilithium for certificates",
                "Email_Encryption": "Kyber + Classic McEliece hybrid",
                "Code_Signing": "CRYSTALS-Dilithium or FALCON",
                "VPN": "Kyber for key exchange, Dilithium for authentication"
            },
            "transition_steps": [
                "1. Inventory all RSA usage (certificates, keys, APIs)",
                "2. Deploy hybrid RSA+Kyber for backward compatibility",
                "3. Update client libraries to support PQC algorithms",
                "4. Gradual rollout: Test → Staging → Production",
                "5. Monitor performance and compatibility",
                "6. Complete migration to pure PQC"
            ]
        },
        "ECDSA": {
            "type": "Elliptic Curve Digital Signature",
            "quantum_threat": "CRITICAL - Completely broken by Shor's algorithm",
            "recommended_pqc": {
                "digital_signature": ["CRYSTALS-Dilithium", "FALCON", "SPHINCS+", "Picnic", "Rainbow"]
            },
            "primary_recommendation": "CRYSTALS-Dilithium (fastest, NIST standard) or FALCON (smallest signatures)",
            "security_level": "NIST Level 1/2/3/5 - Multiple security categories available",
            "performance": "Dilithium: Fastest overall; FALCON: 40% smaller signatures; SPHINCS+: Stateless hash-based (most conservative)",
            "migration_priority": "CRITICAL - Immediate action required",
            "timeline": "Start migration NOW - Complete within 12-18 months",
            "hybrid_approach": "ECDSA + Dilithium dual signatures for transition",
            "key_size_comparison": "ECDSA P-256: 256 bits → Dilithium2: 1312 bytes public key, FALCON-512: 897 bytes",
            "use_cases": {
                "Blockchain": "SPHINCS+ (stateless) or Dilithium",
                "IoT_Devices": "FALCON (compact signatures)",
                "Enterprise_PKI": "CRYSTALS-Dilithium",
                "High_Security": "SPHINCS+ (conservative, hash-based)"
            },
            "transition_steps": [
                "1. Identify all ECDSA certificate usage",
                "2. Test PQC algorithms in dev environment",
                "3. Issue hybrid ECDSA+Dilithium certificates",
                "4. Update certificate validation logic",
                "5. Deploy to production with monitoring",
                "6. Retire ECDSA-only certificates"
            ]
        },
        "ECDH": {
            "type": "Elliptic Curve Diffie-Hellman Key Exchange",
            "quantum_threat": "CRITICAL - Completely broken by Shor's algorithm",
            "recommended_pqc": {
                "key_exchange": ["CRYSTALS-Kyber", "FrodoKEM", "BIKE", "Classic McEliece", "HQC", "SIKE"]
            },
            "primary_recommendation": "CRYSTALS-Kyber (NIST standard, excellent performance)",
            "security_level": "NIST Level 1/3/5 with multiple parameter sets",
            "performance": "Kyber: Fastest; FrodoKEM: Conservative LWE security; Classic McEliece: Largest keys but proven security",
            "migration_priority": "CRITICAL - Immediate action required",
            "timeline": "Start migration NOW - Complete within 12-18 months",
            "hybrid_approach": "X25519 + Kyber hybrid KEM (widely supported in TLS)",
            "key_size_comparison": "ECDH X25519: 32 bytes → Kyber-768: 1184 bytes public key; Classic McEliece: 261KB",
            "use_cases": {
                "TLS_1.3": "Hybrid X25519+Kyber or pure Kyber",
                "VPN_Tunnels": "CRYSTALS-Kyber",
                "SSH": "Kyber or FrodoKEM",
                "Secure_Messaging": "Kyber for session keys"
            },
            "transition_steps": [
                "1. Audit all ECDH implementations",
                "2. Deploy hybrid X25519+Kyber in TLS",
                "3. Update key exchange protocols",
                "4. Test interoperability",
                "5. Monitor key exchange performance",
                "6. Full migration to Kyber"
            ]
        },
        "DSA": {
            "type": "Digital Signature Algorithm",
            "quantum_threat": "CRITICAL - Completely broken by Shor's algorithm",
            "recommended_pqc": {
                "digital_signature": ["CRYSTALS-Dilithium", "FALCON", "SPHINCS+"]
            },
            "primary_recommendation": "CRYSTALS-Dilithium (NIST standard, best overall performance)",
            "security_level": "NIST Level 2/3/5 (128/192/256-bit equivalent)",
            "performance": "Dilithium: Fastest signing/verification; FALCON: Compact; SPHINCS+: Hash-based security",
            "migration_priority": "CRITICAL - Immediate migration required",
            "timeline": "Start migration NOW - Complete within 12 months",
            "hybrid_approach": "DSA + Dilithium dual signatures during transition",
            "key_size_comparison": "DSA-2048: 2048-bit → Dilithium3: 1952 bytes public key",
            "use_cases": {
                "Document_Signing": "CRYSTALS-Dilithium",
                "Software_Updates": "SPHINCS+ (stateless)",
                "Authentication": "FALCON (compact)",
                "Legacy_Systems": "Hybrid DSA+Dilithium"
            },
            "transition_steps": [
                "1. Map all DSA key usage",
                "2. Generate Dilithium key pairs",
                "3. Implement dual-signature validation",
                "4. Update signature verification code",
                "5. Gradual key rotation",
                "6. Decommission DSA keys"
            ]
        },
        "DH": {
            "type": "Diffie-Hellman Key Exchange",
            "quantum_threat": "CRITICAL - Completely broken by Shor's algorithm",
            "recommended_pqc": {
                "key_exchange": ["CRYSTALS-Kyber", "FrodoKEM", "Classic McEliece", "BIKE", "HQC"]
            },
            "primary_recommendation": "CRYSTALS-Kyber with hybrid DH+Kyber approach initially",
            "security_level": "NIST Level 1/3/5 with proven IND-CCA2 security",
            "performance": "Kyber: Excellent speed; FrodoKEM: 2-3x slower but conservative; McEliece: Very large keys",
            "migration_priority": "CRITICAL - Immediate action required",
            "timeline": "Start migration NOW - Complete within 12-18 months",
            "hybrid_approach": "Classical DH + Kyber KEM combination (backward compatible)",
            "key_size_comparison": "DH-2048: 2048-bit → Kyber-1024: 1568 bytes; FrodoKEM-976: 15KB",
            "use_cases": {
                "TLS_Handshake": "Hybrid DH+Kyber",
                "IKE_VPN": "CRYSTALS-Kyber",
                "Secure_Channels": "FrodoKEM for high security",
                "IoT": "Kyber-512 (lighter variant)"
            },
            "transition_steps": [
                "1. Identify all DH key exchange protocols",
                "2. Implement hybrid DH+Kyber support",
                "3. Update protocol negotiation",
                "4. Test with legacy clients",
                "5. Monitor key exchange overhead",
                "6. Transition to pure Kyber"
            ]
        },
        "ED25519": {
            "type": "Edwards-curve Digital Signature",
            "quantum_threat": "CRITICAL - Completely broken by Shor's algorithm",
            "recommended_pqc": {
                "digital_signature": ["CRYSTALS-Dilithium", "FALCON", "SPHINCS+"]
            },
            "primary_recommendation": "CRYSTALS-Dilithium or FALCON (both offer excellent performance)",
            "security_level": "NIST Level 1/2/3/5",
            "performance": "Similar or better than Ed25519; Dilithium: fastest; FALCON: smallest signatures",
            "migration_priority": "HIGH - Begin migration within 6-12 months",
            "timeline": "Start planning NOW - Complete within 18-24 months",
            "hybrid_approach": "Ed25519 + Dilithium dual signatures",
            "key_size_comparison": "Ed25519: 32 bytes → Dilithium2: 1312 bytes; FALCON-512: 897 bytes",
            "use_cases": {
                "SSH_Keys": "CRYSTALS-Dilithium",
                "Git_Commits": "FALCON (compact)",
                "Cryptocurrencies": "SPHINCS+ (stateless)",
                "API_Authentication": "Dilithium"
            },
            "transition_steps": [
                "1. Audit Ed25519 key usage",
                "2. Test Dilithium/FALCON in dev",
                "3. Implement dual-signature support",
                "4. Roll out hybrid authentication",
                "5. Update client applications",
                "6. Complete PQC migration"
            ]
        },
        "AES": {
            "type": "Symmetric Encryption",
            "quantum_threat": "LOW - Grover's algorithm reduces key strength by half",
            "recommended_pqc": {
                "symmetric": ["AES-256", "ChaCha20", "AES-192"]
            },
            "primary_recommendation": "AES-256 (doubles security margin against Grover's algorithm)",
            "security_level": "AES-256 provides 128-bit quantum security (equivalent to AES-128 classical)",
            "performance": "No performance penalty - AES hardware acceleration widely available",
            "migration_priority": "MEDIUM - Upgrade AES-128 to AES-256",
            "timeline": "Migrate within 3-5 years as part of regular key rotation",
            "hybrid_approach": "Not required - direct upgrade to AES-256",
            "key_size_comparison": "AES-128: 128-bit → AES-256: 256-bit (same algorithm, longer key)",
            "use_cases": {
                "Data_Encryption": "AES-256-GCM",
                "File_Encryption": "AES-256-CTR",
                "Database_Encryption": "AES-256-CBC",
                "Disk_Encryption": "AES-256-XTS"
            },
            "transition_steps": [
                "1. Identify all AES-128 usage",
                "2. Update key generation to 256-bit",
                "3. Re-encrypt sensitive data with AES-256",
                "4. Update configuration files",
                "5. Verify encryption mode (GCM preferred)",
                "6. Complete transition during key rotation"
            ]
        },
        "SHA256": {
            "type": "Cryptographic Hash Function",
            "quantum_threat": "LOW - Grover's algorithm reduces collision resistance by half",
            "recommended_pqc": {
                "hash": ["SHA-384", "SHA-512", "SHA3-256", "SHA3-512", "BLAKE2", "BLAKE3"]
            },
            "primary_recommendation": "SHA-384 or SHA-512 for enhanced quantum resistance",
            "security_level": "SHA-384: 192-bit quantum security; SHA-512: 256-bit quantum security",
            "performance": "SHA-512 is faster on 64-bit systems; SHA3 offers different security properties",
            "migration_priority": "LOW-MEDIUM - Upgrade within 5-10 years",
            "timeline": "Migrate during normal hash function updates",
            "hybrid_approach": "Not required - direct upgrade to longer hash",
            "key_size_comparison": "SHA-256: 256-bit output → SHA-384: 384-bit; SHA-512: 512-bit",
            "use_cases": {
                "Digital_Signatures": "Use with Dilithium/FALCON (includes hash)",
                "Data_Integrity": "SHA-384 or SHA3-256",
                "Password_Hashing": "Argon2 (already quantum-resistant)",
                "Blockchain": "SHA-512 or SHA3-512"
            },
            "transition_steps": [
                "1. Review all SHA-256 usage",
                "2. Update hash function calls to SHA-384/512",
                "3. Regenerate hash-based identifiers",
                "4. Update verification logic",
                "5. Maintain backward compatibility temporarily",
                "6. Complete migration over time"
            ]
        }
    }

def _flatten_nested_dict(obj, indent=0):
    """
    Convert nested dictionaries/objects to readable string format for React display
    """
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, list):
        if all(isinstance(item, str) for item in obj):
            return obj  # Return string arrays as-is
        return "\n".join([f"• {_flatten_nested_dict(item, indent)}" for item in obj])
    elif isinstance(obj, dict):
        lines = []
        for key, value in obj.items():
            formatted_key = key.replace('_', ' ').title()
            if isinstance(value, dict):
                lines.append(f"\n{formatted_key}:")
                lines.append(_flatten_nested_dict(value, indent + 2))
            elif isinstance(value, list):
                lines.append(f"\n{formatted_key}:")
                lines.append(_flatten_nested_dict(value, indent + 2))
            else:
                lines.append(f"{formatted_key}: {value}")
        return "\n".join(lines)
    else:
        return str(obj)

async def _get_gemini_recommendations(algorithm_name: str, algorithm_type: str, context: Dict) -> Dict:
    """
    Get AI-powered recommendations using Google Gemini
    """
    if not AI_AVAILABLE:
        return _get_rule_based_recommendations(algorithm_name, algorithm_type)
    
    try:
        prompt = f"""Analyze {algorithm_name} ({algorithm_type}) for quantum safety. Provide concise JSON:

{{
    "quantum_vulnerability": "HIGH/MEDIUM/LOW assessment",
    "recommended_pqc_algorithms": ["ML-KEM-768", "ML-DSA-65"],
    "primary_recommendation": "Main recommendation with reasoning",
    "security_assessment": "Security implications summary",
    "performance_comparison": "Performance impact summary",
    "migration_strategy": "Step-by-step migration approach",
    "implementation_considerations": "Key technical requirements",
    "compliance_notes": "NIST/regulatory compliance info",
    "risk_timeline": "Timeline recommendations",
    "cost_benefit_analysis": "Costs vs benefits summary"
}}

Context: {json.dumps(context)}

CRITICAL: Return ONLY valid JSON with string values. Be concise."""

        # Add timeout to prevent long waits
        logging.info(f"🤖 Calling Gemini AI for {algorithm_name}...")
        start_time = asyncio.get_event_loop().time()
        
        # Generate content with timeout
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(model.generate_content, prompt),
                timeout=30.0  # 30 second timeout
            )
            
            elapsed = asyncio.get_event_loop().time() - start_time
            logging.info(f"✅ Gemini AI responded in {elapsed:.2f} seconds")
            
        except asyncio.TimeoutError:
            logging.error("⏱️ Gemini AI timeout after 30 seconds - using rule-based fallback")
            return _get_rule_based_recommendations(algorithm_name, algorithm_type)
        
        ai_response = response.text
        
        # Clean up the response to extract JSON
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                parsed_response = json.loads(json_str)
                
                # Flatten any nested objects that AI might have returned anyway
                flattened_response = {}
                for key, value in parsed_response.items():
                    if key == "recommended_pqc_algorithms" and isinstance(value, list):
                        # Keep array of strings as-is
                        flattened_response[key] = value if all(isinstance(v, str) for v in value) else [str(v) for v in value]
                    elif isinstance(value, (dict, list)) and key != "recommended_pqc_algorithms":
                        # Flatten nested structures to string
                        flattened_response[key] = _flatten_nested_dict(value)
                    else:
                        # Keep simple strings as-is
                        flattened_response[key] = value
                
                logging.info("✅ Gemini AI response flattened successfully")
                return flattened_response
                
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
    Enhanced rule-based recommendations with comprehensive migration guidance
    """
    mapping = _get_classical_to_pqc_mapping()
    
    # Clean algorithm name for matching
    clean_name = algorithm_name.upper().replace("WITH", "").replace("ENCRYPTION", "").replace("-", "").strip()
    
    # Find matching algorithm
    recommendation = None
    matched_alg = None
    for classical_alg, pqc_info in mapping.items():
        if classical_alg.replace("-", "") in clean_name or clean_name.startswith(classical_alg.replace("-", "")):
            recommendation = pqc_info
            matched_alg = classical_alg
            break
    
    if not recommendation:
        return {
            "quantum_vulnerability": "MEDIUM - Requires manual cryptographic assessment",
            "recommended_pqc_algorithms": ["CRYSTALS-Kyber (KEM)", "CRYSTALS-Dilithium (Signatures)", "FALCON", "SPHINCS+"],
            "primary_recommendation": "Comprehensive evaluation needed - Consider NIST-standardized CRYSTALS suite for general quantum-resistance",
            "security_assessment": "Algorithm not in standard mapping - requires expert cryptographic analysis. Consult with security team to determine quantum vulnerability.",
            "performance_comparison": "Performance impact varies: Kyber/Dilithium offer excellent speed; FALCON has compact signatures; SPHINCS+ is conservative but slower",
            "migration_strategy": "1. Conduct security audit of current cryptographic usage\n2. Evaluate applicable NIST PQC standards\n3. Test PQC algorithms in development environment\n4. Implement hybrid classical+PQC approach\n5. Gradual rollout with monitoring\n6. Complete migration to pure PQC",
            "implementation_considerations": "Consult with cryptography experts, conduct thorough compatibility testing, plan for increased key/signature sizes, update cryptographic libraries",
            "compliance_notes": "Verify compliance with NIST Post-Quantum Cryptography standards (FIPS 203/204/205), organizational security policies, and industry regulations",
            "risk_timeline": "Evaluate within 2-5 years based on quantum computing developments and organizational risk tolerance",
            "cost_benefit_analysis": "Migration costs (development, testing, deployment) must be weighed against quantum threat timeline and potential security breach costs",
            "hybrid_approach": "Recommended: Combine classical and PQC algorithms during transition period for backward compatibility",
            "transition_steps": ["1. Inventory cryptographic assets", "2. Assess PQC readiness", "3. Pilot PQC implementation", "4. Deploy hybrid solution", "5. Monitor and optimize", "6. Complete PQC migration"],
            "use_cases": {"General": "Evaluate specific use case to determine optimal PQC algorithm"}
        }
    
    # Collect all PQC algorithms
    all_pqc_algs = []
    for key in ["key_exchange", "digital_signature", "symmetric", "hash"]:
        if key in recommendation["recommended_pqc"]:
            all_pqc_algs.extend(recommendation["recommended_pqc"][key])
    
    # Build comprehensive response with all available details
    response = {
        "quantum_vulnerability": recommendation["quantum_threat"],
        "recommended_pqc_algorithms": list(set(all_pqc_algs)),
        "primary_recommendation": recommendation["primary_recommendation"],
        "security_assessment": f"⚠️ {matched_alg} vulnerability: {recommendation['quantum_threat']}\n\n🔐 Security Level: {recommendation['security_level']}\n\nMigration Priority: {recommendation['migration_priority']}",
        "performance_comparison": f"📊 Performance Analysis:\n{recommendation['performance']}\n\n📏 Key Size Impact:\n{recommendation.get('key_size_comparison', 'Contact cryptography team for details')}",
        "migration_strategy": f"🎯 Migration Priority: {recommendation['migration_priority']}\n\n⏱️ Timeline: {recommendation['timeline']}\n\n🔄 Hybrid Approach:\n{recommendation.get('hybrid_approach', 'Hybrid deployment recommended during transition')}", 
        "implementation_considerations": f"🔧 Algorithm Type: {recommendation['type']}\n\n💡 Implementation Notes:\n{recommendation.get('hybrid_approach', 'Consider phased deployment approach')}",
        "compliance_notes": "✅ NIST Post-Quantum Cryptography Standards (FIPS 203: ML-KEM, FIPS 204: ML-DSA, FIPS 205: SLH-DSA)\n✅ Ensure organizational policy compliance\n✅ Consider industry-specific regulations",
        "risk_timeline": recommendation["timeline"],
        "cost_benefit_analysis": f"💰 Migration Investment Required: {recommendation['migration_priority']} priority\n\n⚖️ Risk vs Cost: Immediate action justified for CRITICAL threats to prevent future quantum attacks\n\n📈 Long-term Benefits: Future-proof security, regulatory compliance, competitive advantage"
    }
    
    # Add transition steps if available
    if "transition_steps" in recommendation:
        response["transition_steps"] = recommendation["transition_steps"]
        response["migration_strategy"] += f"\n\n📋 Detailed Transition Steps:\n" + "\n".join(recommendation["transition_steps"])
    
    # Add use cases if available
    if "use_cases" in recommendation:
        use_case_text = "\n\n🎯 Recommended Use Cases:\n"
        for use_case, algo in recommendation["use_cases"].items():
            use_case_text += f"• {use_case.replace('_', ' ')}: {algo}\n"
        response["implementation_considerations"] += use_case_text
    
    return response

# Production security configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
SSL_ENABLED = os.getenv("SSL_ENABLED", "false").lower() == "true"
FORCE_HTTPS = os.getenv("FORCE_HTTPS", "false").lower() == "true"
SECURE_COOKIES = os.getenv("SECURE_COOKIES", "false").lower() == "true"

# Pydantic models for domain scanner
class DomainScanRequest(BaseModel):
    host: str
    ports: Optional[List[int]] = None

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
    pass  # Placeholder for production-specific middleware
    
# Trusted host middleware for production domains only
# Disable in DEBUG mode to allow localhost development
if not DEBUG_MODE:
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
    logging.info("🔒 TrustedHostMiddleware enabled for production")
else:
    logging.info("🔓 TrustedHostMiddleware disabled for DEBUG mode")

# Enhanced CORS middleware with environment configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
cors_origins = ["*"] if DEBUG_MODE else ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Allow all origins in debug mode
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["X-Process-Time"],
)
logging.info(f"🌐 CORS configured with origins: {cors_origins}")

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
        
        # Try to extract public key info (may fail for PQC certificates)
        try:
            public_key = cert.public_key()
            key_type = public_key.__class__.__name__
            key_size = getattr(public_key, "key_size", None)
            pubkey_oid = getattr(getattr(public_key, "oid", None), "dotted_string", None)
        except ValueError as e:
            # Handle PQC certificates where cryptography library doesn't recognize the key type
            # Extract OID from error message: "Unknown key type: 2.16.840.1.101.3.4.3.18"
            error_msg = str(e)
            logging.warning(f"Could not parse public key (likely PQC): {error_msg}")
            
            if "Unknown key type:" in error_msg:
                pubkey_oid = error_msg.split("Unknown key type:")[-1].strip()
                key_type = "Unknown (PQC)"
                key_size = None
                
                # Detect specific PQC algorithms from OID
                pqc_oids = {
                    "2.16.840.1.101.3.4.3.17": "ML-DSA-65",  # Dilithium3
                    "2.16.840.1.101.3.4.3.18": "ML-DSA-87",  # Dilithium5
                    "2.16.840.1.101.3.4.4.1": "ML-KEM-512",  # Kyber512
                    "2.16.840.1.101.3.4.4.2": "ML-KEM-768",  # Kyber768
                    "2.16.840.1.101.3.4.4.3": "ML-KEM-1024", # Kyber1024
                }
                
                if pubkey_oid in pqc_oids:
                    key_type = pqc_oids[pubkey_oid]
                    logging.info(f"Detected PQC algorithm: {key_type} (OID: {pubkey_oid})")
            else:
                raise
        except Exception as e:
            logging.error(f"Unexpected error parsing public key: {e}")
            key_type = "Unknown"
            key_size = None
            pubkey_oid = None

        # Signature algorithm (OID + name)
        # Handle cases where cryptography library doesn't recognize the OID
        try:
            sig_oid = cert.signature_algorithm_oid.dotted_string
            sig_name = cert.signature_algorithm_oid._name
            
            # Detect PQC signature algorithms from OID
            pqc_sig_oids = {
                "2.16.840.1.101.3.4.3.17": "ML-DSA-65 (Dilithium3)",
                "2.16.840.1.101.3.4.3.18": "ML-DSA-87 (Dilithium5)",
            }
            
            if sig_oid in pqc_sig_oids:
                sig_name = pqc_sig_oids[sig_oid]
                logging.info(f"Detected PQC signature: {sig_name} (OID: {sig_oid})")
                
        except Exception as e:
            logging.warning(f"Could not parse signature algorithm OID: {e}")
            sig_oid = "unknown"
            sig_name = "Unknown Signature Algorithm"

        # Public key algorithm (name only — OIDs depend on key type)
        pubkey_name = key_type

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
        
        # Additional PQC detection from certificate subject/issuer
        # Check if certificate explicitly mentions PQC algorithms in CN or O fields
        cert_text = f"{subject} {issuer}".lower()
        if any(keyword in cert_text for keyword in ['ml-dsa', 'ml-kem', 'dilithium', 'kyber', 'falcon', 'sphincs']):
            # If certificate mentions PQC in subject/issuer, it's likely a PQC cert
            if 'ml-dsa' in cert_text or 'dilithium' in cert_text:
                sig_is_pqc = True
                if sig_algorithm_name == "Unknown Signature Algorithm":
                    sig_algorithm_name = "ML-DSA (CRYSTALS-Dilithium)"
            if 'ml-kem' in cert_text or 'kyber' in cert_text:
                pubkey_is_pqc = True
                if pubkey_algorithm_name == key_type:
                    pubkey_algorithm_name = "ML-KEM (CRYSTALS-Kyber)"

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
                "expiry_date": cert.not_valid_after_utc.isoformat(),
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
                "expiry_date": cert.not_valid_after_utc.isoformat(),
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
                "valid_from": cert.not_valid_before_utc.isoformat(),
                "valid_until": cert.not_valid_after_utc.isoformat(),
                "expiry_date": cert.not_valid_after_utc.isoformat(),
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

@app.post("/scan-domain")
async def scan_domain_endpoint(scan_request: DomainScanRequest):
    """
    Scan a domain or IP address for TLS certificates on specified or all common ports
    
    Request body:
    {
        "host": "example.com",  # Required: domain or IP
        "ports": [443, 8443]    # Optional: specific ports to scan (defaults to all common TLS ports)
    }
    
    Returns:
    {
        "scan_info": {
            "host": "example.com",
            "scanned_ports": [443, 8443, ...],
            "timestamp": "2024-01-01T00:00:00Z"
        },
        "successful_ports": [
            {"port": 443, "cert_count": 3}
        ],
        "failed_ports": [
            {"port": 8443, "error": "Connection timeout"}
        ],
        "certificates": [
            {
                "port": 443,
                "position": 1,
                "subject": "CN=example.com",
                "analysis": {...}  # Full certificate analysis
            }
        ]
    }
    """
    start_time = time.time()
    
    # Check if scanner is available
    if not SCANNER_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Domain scanning service is not available"
        )
    
    # Create database session manually
    db = None
    if DATABASE_AVAILABLE:
        db = SessionLocal()
    
    try:
        # Get host and ports from request
        host = scan_request.host
        ports = scan_request.ports
        
        if not host:
            raise HTTPException(
                status_code=400,
                detail="Missing required field: 'host'"
            )
        
        # Validate host
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9.-]+[a-zA-Z0-9]$|^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', host):
            raise HTTPException(
                status_code=400,
                detail="Invalid host format. Must be a valid domain or IP address."
            )
        
        # Validate ports if provided
        if ports is not None:
            for port in ports:
                if port < 1 or port > 65535:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid port number: {port}. Must be between 1 and 65535."
                    )
        
        # Log scan request
        logging.info(f"Domain scan requested - Host: {host}, Ports: {ports or 'all common'}")
        
        # Perform the scan
        scan_result = scan_domain(host, ports)
        
        # Prepare response structure
        response = {
            "scan_info": {
                "host": host,
                "scanned_ports": scan_result["ports_scanned"],
                "timestamp": datetime.utcnow().isoformat(),
                "scan_duration_ms": int((time.time() - start_time) * 1000)
            },
            "successful_ports": [],
            "failed_ports": [],
            "certificates": []
        }
        
        # Process successful port scans
        for port_data in scan_result["successful_ports"]:
            port = port_data["port"]
            
            response["successful_ports"].append({
                "port": port,
                "cert_count": port_data["num_certificates"]
            })
        
        # Get all certificates and analyze them
        for cert_data in scan_result.get("certificates", []):
            port = cert_data["port"]
            position = cert_data["chain_position"] + 1  # 1-indexed
            cert_der = cert_data["der_bytes"]
            
            try:
                # Parse certificate from DER bytes
                cert = x509.load_der_x509_certificate(cert_der, default_backend())
                
                # Extract basic certificate info
                subject = cert.subject.rfc4514_string()
                issuer = cert.issuer.rfc4514_string()
                
                # Analyze the certificate with AI (async)
                analysis = await analyze_certificate_data(cert, db)
                
                # Add to response
                response["certificates"].append({
                    "port": port,
                    "position": position,
                    "subject": subject,
                    "issuer": issuer,
                    "analysis": analysis
                })
                
            except Exception as cert_error:
                logging.error(f"Error analyzing certificate from port {port}, position {position}: {cert_error}")
                response["certificates"].append({
                    "port": port,
                    "position": position,
                    "error": f"Certificate analysis failed: {str(cert_error)}"
                })
        
        # Process failed port scans
        for port_data in scan_result["failed_ports"]:
            response["failed_ports"].append({
                "port": port_data["port"],
                "error": port_data["error"]
            })
        
        # Log performance
        duration_ms = int((time.time() - start_time) * 1000)
        logging.info(
            f"Domain scan completed - Host: {host}, "
            f"Successful: {len(response['successful_ports'])}, "
            f"Failed: {len(response['failed_ports'])}, "
            f"Duration: {duration_ms}ms"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Domain scan error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Domain scan failed: {str(e)}"
        )
    finally:
        # Close database session
        if db is not None:
            db.close()


async def analyze_certificate_data(cert: x509.Certificate, db: Session) -> Dict:
    """
    Analyze a certificate object and return detailed analysis with AI recommendations
    (Extracted from the main analyze_certificate endpoint for reuse)
    
    Args:
        cert: x509.Certificate object
        db: Database session
        
    Returns:
        Dict containing complete certificate analysis
    """
    try:
        # Extract certificate information
        subject = cert.subject.rfc4514_string()
        issuer = cert.issuer.rfc4514_string()
        serial_number = format(cert.serial_number, 'x')
        
        # Get validity dates using UTC-aware methods
        valid_from = cert.not_valid_before_utc
        valid_until = cert.not_valid_after_utc
        
        # Check if certificate is currently valid
        now = datetime.now(valid_from.tzinfo)
        is_valid = valid_from <= now <= valid_until
        
        # Extract public key algorithm
        public_key_algo = None
        public_key_size = None
        is_pqc = False
        pqc_algorithm = None
        public_key_oid = None
        
        try:
            public_key = cert.public_key()
            
            # Try to get algorithm from public key
            try:
                from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519, ed448, dsa
                
                if isinstance(public_key, rsa.RSAPublicKey):
                    public_key_algo = "RSA"
                    public_key_size = public_key.key_size
                elif isinstance(public_key, ec.EllipticCurvePublicKey):
                    public_key_algo = f"EC-{public_key.curve.name}"
                    public_key_size = public_key.curve.key_size
                elif isinstance(public_key, ed25519.Ed25519PublicKey):
                    public_key_algo = "Ed25519"
                    public_key_size = 256
                elif isinstance(public_key, ed448.Ed448PublicKey):
                    public_key_algo = "Ed448"
                    public_key_size = 448
                elif isinstance(public_key, dsa.DSAPublicKey):
                    public_key_algo = "DSA"
                    public_key_size = public_key.key_size
                else:
                    public_key_algo = "Unknown"
                    
            except ValueError as ve:
                # This is where we catch PQC algorithms that cryptography doesn't recognize
                error_msg = str(ve)
                logging.info(f"Public key parsing error (might be PQC): {error_msg}")
                
                # Try to extract OID from error message
                # Error format: "Unknown key type: 2.16.840.1.101.3.4.3.18"
                oid_match = re.search(r'Unknown key type: ([\d.]+)', error_msg)
                if oid_match:
                    public_key_oid = oid_match.group(1)
                    logging.info(f"Detected public key OID: {public_key_oid}")
                    
                    # Map known PQC OIDs to algorithm names
                    pqc_oid_map = {
                        "2.16.840.1.101.3.4.3.17": "ML-DSA-65",
                        "2.16.840.1.101.3.4.3.18": "ML-DSA-87",
                        "2.16.840.1.101.3.4.4.1": "ML-KEM-512",
                        "2.16.840.1.101.3.4.4.2": "ML-KEM-768",
                        "2.16.840.1.101.3.4.4.3": "ML-KEM-1024",
                        "1.3.6.1.4.1.2.267.7.4.4": "CRYSTALS-Dilithium",
                        "1.3.6.1.4.1.2.267.7.6.5": "CRYSTALS-Kyber",
                    }
                    
                    if public_key_oid in pqc_oid_map:
                        pqc_algorithm = pqc_oid_map[public_key_oid]
                        public_key_algo = pqc_algorithm
                        is_pqc = True
                        logging.info(f"Mapped OID to PQC algorithm: {pqc_algorithm}")
                    else:
                        public_key_algo = f"Unknown PQC (OID: {public_key_oid})"
                        is_pqc = True
                        logging.warning(f"Unknown PQC OID: {public_key_oid}")
                else:
                    public_key_algo = "Unknown"
                    
        except Exception as pk_error:
            logging.error(f"Error extracting public key: {pk_error}")
            public_key_algo = "Error extracting public key"
        
        # Extract signature algorithm and OID
        signature_algo = None
        signature_oid = None
        try:
            if hasattr(cert.signature_algorithm_oid, '_name'):
                signature_algo = cert.signature_algorithm_oid._name
            signature_oid = str(cert.signature_algorithm_oid.dotted_string) if hasattr(cert.signature_algorithm_oid, 'dotted_string') else str(cert.signature_algorithm_oid)
            if not signature_algo:
                signature_algo = signature_oid
        except Exception as sig_error:
            logging.error(f"Error extracting signature algorithm: {sig_error}")
            signature_algo = "Unknown"
        
        # Query database for algorithm information
        # PRIORITY 1: Try OID-based lookup FIRST
        public_key_info = None
        signature_info = None
        
        if DATABASE_AVAILABLE and db:
            try:
                # Try OID-based lookup for public key algorithm
                if public_key_oid:
                    logging.info(f"Attempting OID-based lookup for public key: {public_key_oid}")
                    public_key_info = db.query(PublicKeyAlgorithm).filter(
                        PublicKeyAlgorithm.public_key_algorithm_oid == public_key_oid
                    ).first()
                    
                    if public_key_info:
                        logging.info(f"✅ Found public key algorithm in DB by OID: {public_key_info.public_key_algorithm_name}")
                        # Update algorithm name from database
                        public_key_algo = public_key_info.public_key_algorithm_name
                        if public_key_info.is_pqc:
                            is_pqc = True
                            pqc_algorithm = public_key_algo
                        db_key_size = getattr(public_key_info, 'key_size', None)
                        if db_key_size:
                            public_key_size = db_key_size
                
                # FALLBACK: If OID lookup failed, try name-based lookup
                if not public_key_info and public_key_algo:
                    logging.info(f"OID lookup failed, trying name-based lookup: {public_key_algo}")
                    public_key_info = db.query(PublicKeyAlgorithm).filter(
                        PublicKeyAlgorithm.public_key_algorithm_name.ilike(f"%{public_key_algo}%")
                    ).first()
                    
                    if public_key_info:
                        logging.info(f"✅ Found public key algorithm in DB by name: {public_key_info.public_key_algorithm_name}")
                        if public_key_info.is_pqc:
                            is_pqc = True
                            pqc_algorithm = public_key_info.public_key_algorithm_name
                
                # Try OID-based lookup for signature algorithm
                if signature_oid:
                    logging.info(f"Attempting OID-based lookup for signature: {signature_oid}")
                    signature_info = db.query(SignatureAlgorithm).filter(
                        SignatureAlgorithm.signature_algorithm_oid == signature_oid
                    ).first()
                    
                    if signature_info:
                        logging.info(f"✅ Found signature algorithm in DB by OID: {signature_info.signature_algorithm_name}")
                        # Update algorithm name from database
                        signature_algo = signature_info.signature_algorithm_name
                        if signature_info.is_pqc:
                            is_pqc = True
                
                # FALLBACK: If OID lookup failed, try name-based lookup for signature
                if not signature_info and signature_algo:
                    logging.info(f"OID lookup failed, trying name-based lookup: {signature_algo}")
                    signature_info = db.query(SignatureAlgorithm).filter(
                        SignatureAlgorithm.signature_algorithm_name.ilike(f"%{signature_algo}%")
                    ).first()
                    
                    if signature_info:
                        logging.info(f"✅ Found signature algorithm in DB by name: {signature_info.signature_algorithm_name}")
                        if signature_info.is_pqc:
                            is_pqc = True
                            
            except Exception as db_error:
                logging.error(f"Database query error: {db_error}")
        
        # If not detected as PQC yet, check subject/issuer for PQC keywords
        if not is_pqc:
            pqc_keywords = ['dilithium', 'kyber', 'falcon', 'sphincs', 'ntru', 'saber', 
                           'mceliece', 'rainbow', 'picnic', 'crystals', 'pqc', 'post-quantum',
                           'ml-dsa', 'ml-kem', 'slh-dsa']
            
            subject_lower = subject.lower()
            issuer_lower = issuer.lower()
            
            for keyword in pqc_keywords:
                if keyword in subject_lower or keyword in issuer_lower:
                    is_pqc = True
                    pqc_algorithm = keyword.upper()
                    break
        
        # Determine quantum safety
        quantum_safe = False
        quantum_safe_reason = []
        
        if is_pqc or (public_key_info and getattr(public_key_info, 'is_quantum_safe', False)):
            quantum_safe = True
            quantum_safe_reason.append("Uses post-quantum cryptography")
        
        if signature_info and getattr(signature_info, 'is_quantum_safe', False):
            quantum_safe = True
            quantum_safe_reason.append("Signature algorithm is quantum-resistant")
        
        # Get AI recommendation if available
        ai_recommendation = None
        if AI_AVAILABLE:
            try:
                # Generate enriched context for AI with database information
                context = {
                    "algorithm_type": "certificate_analysis",
                    "key_size": public_key_size,
                    "certificate_type": "X.509",
                    "expiry_date": valid_until.isoformat(),
                    "issuer": issuer,
                    "is_pqc": is_pqc,
                    "quantum_safe": quantum_safe,
                    "current_usage": "TLS/SSL Certificate"
                }
                
                # Add database information to context for better AI analysis
                if public_key_info:
                    context["public_key_details"] = {
                        "name": public_key_info.public_key_algorithm_name,
                        "description": getattr(public_key_info, 'description', None),
                        "security_level": getattr(public_key_info, 'security_level', None),
                        "is_quantum_safe": getattr(public_key_info, 'is_quantum_safe', False),
                        "is_pqc": public_key_info.is_pqc,
                        "key_size": getattr(public_key_info, 'key_size', None),
                        "oid": public_key_info.public_key_algorithm_oid
                    }
                    logging.info(f"Added public key DB details to AI context: {public_key_info.public_key_algorithm_name}")
                
                if signature_info:
                    context["signature_details"] = {
                        "name": signature_info.signature_algorithm_name,
                        "description": getattr(signature_info, 'description', None),
                        "security_level": getattr(signature_info, 'security_level', None),
                        "is_quantum_safe": getattr(signature_info, 'is_quantum_safe', False),
                        "is_pqc": signature_info.is_pqc,
                        "oid": signature_info.signature_algorithm_oid
                    }
                    logging.info(f"Added signature DB details to AI context: {signature_info.signature_algorithm_name}")
                
                # Use the REAL Gemini AI for non-quantum-safe algorithms
                if not quantum_safe:
                    ai_recommendation = await _get_gemini_recommendations(
                        public_key_algo or "Unknown", 
                        "public_key",
                        context
                    )
                else:
                    # For quantum-safe certificates, provide positive feedback
                    ai_recommendation = {
                        "quantum_vulnerability": "SECURE - Already using quantum-safe algorithms",
                        "recommended_pqc_algorithms": [pqc_algorithm] if pqc_algorithm else [],
                        "primary_recommendation": f"✅ Certificate is already using quantum-safe cryptography ({pqc_algorithm or 'PQC'})",
                        "security_assessment": "🔐 This certificate uses post-quantum cryptographic algorithms that are resistant to quantum computer attacks.",
                        "performance_comparison": "No migration needed - already using optimal PQC algorithms",
                        "migration_strategy": "No action required - certificate is quantum-safe",
                        "implementation_considerations": "Continue using current PQC implementation. Monitor for updated NIST standards.",
                        "compliance_notes": "✅ Compliant with NIST Post-Quantum Cryptography standards",
                        "risk_timeline": "No immediate risk - quantum-safe implementation in place",
                        "cost_benefit_analysis": "No migration costs - already future-proofed against quantum threats"
                    }
            except Exception as ai_error:
                logging.error(f"AI recommendation error: {ai_error}")
                # Fallback to rule-based if AI fails
                if not quantum_safe:
                    ai_recommendation = _get_rule_based_recommendations(
                        public_key_algo or "Unknown",
                        "public_key"
                    )
        else:
            # Fallback to rule-based recommendations if AI not available
            if not quantum_safe:
                ai_recommendation = _get_rule_based_recommendations(
                    public_key_algo or "Unknown",
                    "public_key"
                )
            else:
                ai_recommendation = {
                    "quantum_vulnerability": "SECURE - Already using quantum-safe algorithms",
                    "recommended_pqc_algorithms": [pqc_algorithm] if pqc_algorithm else [],
                    "primary_recommendation": f"✅ Certificate uses quantum-safe cryptography ({pqc_algorithm or 'PQC'})",
                    "security_assessment": "This certificate uses post-quantum cryptographic algorithms.",
                    "performance_comparison": "No migration needed",
                    "migration_strategy": "No action required",
                    "implementation_considerations": "Continue monitoring NIST standards",
                    "compliance_notes": "Compliant with PQC standards",
                    "risk_timeline": "No immediate risk",
                    "cost_benefit_analysis": "No migration costs needed"
                }
        
        # CRITICAL: Ensure ai_recommendation is NEVER None
        if ai_recommendation is None:
            logging.warning("⚠️ ai_recommendation is None - generating fallback")
            if not quantum_safe:
                ai_recommendation = _get_rule_based_recommendations(
                    public_key_algo or "Unknown",
                    "public_key"
                )
                logging.info("✅ Generated rule-based recommendations as fallback")
            else:
                ai_recommendation = {
                    "quantum_vulnerability": "SECURE - Already using quantum-safe algorithms",
                    "recommended_pqc_algorithms": [pqc_algorithm] if pqc_algorithm else [],
                    "primary_recommendation": f"✅ Certificate uses quantum-safe cryptography ({pqc_algorithm or 'PQC'})",
                    "security_assessment": "This certificate uses post-quantum cryptographic algorithms.",
                    "performance_comparison": "No migration needed",
                    "migration_strategy": "No action required",
                    "implementation_considerations": "Continue monitoring NIST standards",
                    "compliance_notes": "Compliant with PQC standards",
                    "risk_timeline": "No immediate risk",
                    "cost_benefit_analysis": "No migration costs needed"
                }
                logging.info("✅ Generated quantum-safe message as fallback")
        
        # Build response
        analysis = {
            "subject": subject,
            "issuer": issuer,
            "serial_number": serial_number,
            "valid_from": valid_from.isoformat(),
            "valid_until": valid_until.isoformat(),
            "is_valid": is_valid,
            "public_key_algorithm": public_key_algo,
            "public_key_size": public_key_size,
            "signature_algorithm": signature_algo,
            "is_quantum_safe": quantum_safe,
            "quantum_safe_reason": quantum_safe_reason,
            "is_pqc": is_pqc,
            "pqc_algorithm": pqc_algorithm,
            "ai_recommendation": ai_recommendation
        }
        
        # Add database info if available
        if public_key_info:
            analysis["public_key_info"] = {
                "name": public_key_info.public_key_algorithm_name,
                "description": getattr(public_key_info, 'description', None),
                "key_size": getattr(public_key_info, 'key_size', None),
                "security_level": getattr(public_key_info, 'security_level', None),
                "is_quantum_safe": getattr(public_key_info, 'is_quantum_safe', False)
            }
        
        if signature_info:
            analysis["signature_info"] = {
                "name": signature_info.signature_algorithm_name,
                "description": getattr(signature_info, 'description', None),
                "security_level": getattr(signature_info, 'security_level', None),
                "is_quantum_safe": getattr(signature_info, 'is_quantum_safe', False)
            }
        
        return analysis
        
    except Exception as e:
        logging.error(f"Certificate analysis error: {e}")
        raise


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