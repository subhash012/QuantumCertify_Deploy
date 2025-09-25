from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from . import models
from .deps import get_db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="QuantumCertify API",
    description="API for quantum-safe certificate algorithms",
    version="1.0.0"
)

# Initialize database tables
try:
    from .database import engine, Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.warning(f"Database initialization failed: {e}")
    logger.info("API will run in mock mode")

@app.get("/")
def read_root():
    return {"message": "QuantumCertify API is running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    try:
        # Try to get a database session to test connection
        from .database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "healthy", "database": "disconnected", "error": str(e)}

# GET all public key algorithms
@app.get("/public-key-algorithms")
def get_public_key_algorithms(db: Session = Depends(get_db)):
    try:
        algorithms = db.query(models.PublicKeyAlgorithm).all()
        return algorithms
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        # Return mock data when database is unavailable
        return [
            {
                "id": 1,
                "public_key_algorithm_name": "RSA",
                "public_key_algorithm_oid": "1.2.840.113549.1.1.1",
                "category": "Classical",
                "is_pqc": False
            },
            {
                "id": 2,
                "public_key_algorithm_name": "CRYSTALS-Kyber",
                "public_key_algorithm_oid": "2.16.840.1.101.3.4.4.1",
                "category": "Post-Quantum",
                "is_pqc": True
            }
        ]

# GET all signature algorithms
@app.get("/signature-algorithms")
def get_signature_algorithms(db: Session = Depends(get_db)):
    try:
        algorithms = db.query(models.SignatureAlgorithm).all()
        return algorithms
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        # Return mock data when database is unavailable
        return [
            {
                "id": 1,
                "signature_algorithm_name": "RSA-PSS",
                "signature_algorithm_oid": "1.2.840.113549.1.1.10",
                "category": "Classical",
                "is_pqc": False
            },
            {
                "id": 2,
                "signature_algorithm_name": "CRYSTALS-Dilithium",
                "signature_algorithm_oid": "2.16.840.1.101.3.4.3.1",
                "category": "Post-Quantum",
                "is_pqc": True
            }
        ]
