#!/usr/bin/env python3
"""
Simple database initialization for local development using SQLite
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database import engine, Base
from app.models import PublicKeyAlgorithm, SignatureAlgorithm, CertificateAnalysis, AnalyticsSummary

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database with tables and sample data"""
    try:
        logger.info("Creating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        
        # Add some sample PQC algorithm data
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Check if we already have data
            existing_pqc = db.query(PublicKeyAlgorithm).first()
            if not existing_pqc:
                logger.info("Adding sample PQC algorithm data...")
                
                # Add some post-quantum algorithms
                pqc_algorithms = [
                    PublicKeyAlgorithm(
                        public_key_algorithm_name="CRYSTALS-Kyber",
                        public_key_algorithm_oid="2.16.840.1.101.3.4.1.1",
                        is_pqc=True
                    ),
                    PublicKeyAlgorithm(
                        public_key_algorithm_name="CRYSTALS-Dilithium",
                        public_key_algorithm_oid="2.16.840.1.101.3.4.1.2",
                        is_pqc=True
                    ),
                    PublicKeyAlgorithm(
                        public_key_algorithm_name="RSA",
                        public_key_algorithm_oid="1.2.840.113549.1.1.1",
                        is_pqc=False
                    ),
                    PublicKeyAlgorithm(
                        public_key_algorithm_name="ECDSA",
                        public_key_algorithm_oid="1.2.840.10045.2.1",
                        is_pqc=False
                    )
                ]
                
                for alg in pqc_algorithms:
                    db.add(alg)
                
                # Add signature algorithms
                sig_algorithms = [
                    SignatureAlgorithm(
                        signature_algorithm_name="CRYSTALS-Dilithium",
                        signature_algorithm_oid="2.16.840.1.101.3.4.1.2",
                        is_pqc=True
                    ),
                    SignatureAlgorithm(
                        signature_algorithm_name="RSA with SHA-256",
                        signature_algorithm_oid="1.2.840.113549.1.1.11",
                        is_pqc=False
                    ),
                    SignatureAlgorithm(
                        signature_algorithm_name="ECDSA with SHA-256",
                        signature_algorithm_oid="1.2.840.10045.4.3.2",
                        is_pqc=False
                    )
                ]
                
                for alg in sig_algorithms:
                    db.add(alg)
                
                # Initialize analytics summary
                summary = AnalyticsSummary(
                    total_analyzed=0,
                    quantum_safe_count=0,
                    classical_count=0
                )
                db.add(summary)
                
                db.commit()
                logger.info("✅ Sample data added successfully")
            else:
                logger.info("✅ Database already contains data")
                
        except Exception as e:
            logger.error(f"Error adding sample data: {e}")
            db.rollback()
        finally:
            db.close()
            
        logger.info("🎉 Database initialization completed successfully!")
        logger.info("Your QuantumCertify application is ready to use with SQLite database.")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Initializing QuantumCertify Database...")
    success = init_database()
    if success:
        print("✅ Database setup complete! You can now run your application.")
    else:
        print("❌ Database setup failed. Please check the logs above.")
        sys.exit(1)