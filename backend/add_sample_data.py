#!/usr/bin/env python3
"""
Add sample analytics data to demonstrate real dashboard statistics
"""

import os
import sys
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database import engine
from app.models import AnalyticsSummary, CertificateAnalysis

def add_sample_analytics():
    """Add sample analytics data to show real numbers"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Update the analytics summary with sample data
        summary = db.query(AnalyticsSummary).first()
        
        if summary:
            # Update existing record with sample data
            summary.total_analyzed = 25
            summary.quantum_safe_count = 8
            summary.classical_count = 17
            summary.last_updated = datetime.utcnow()
        else:
            # Create new record with sample data
            summary = AnalyticsSummary(
                total_analyzed=25,
                quantum_safe_count=8,
                classical_count=17
            )
            db.add(summary)
        
        # Add some sample certificate analysis records
        existing_analyses = db.query(CertificateAnalysis).count()
        
        if existing_analyses == 0:
            sample_analyses = [
                CertificateAnalysis(
                    file_name="example-rsa-cert.pem",
                    subject="CN=Example RSA Certificate",
                    issuer="CN=Example CA",
                    public_key_algorithm="RSA",
                    signature_algorithm="RSA with SHA-256",
                    is_quantum_safe=False,
                    overall_risk_level="HIGH",
                    ai_powered=True
                ),
                CertificateAnalysis(
                    file_name="example-ecc-cert.pem",
                    subject="CN=Example ECC Certificate",
                    issuer="CN=Example CA",
                    public_key_algorithm="ECDSA",
                    signature_algorithm="ECDSA with SHA-256",
                    is_quantum_safe=False,
                    overall_risk_level="HIGH",
                    ai_powered=True
                ),
                CertificateAnalysis(
                    file_name="example-pqc-cert.pem",
                    subject="CN=Example PQC Certificate",
                    issuer="CN=PQC CA",
                    public_key_algorithm="CRYSTALS-Kyber",
                    signature_algorithm="CRYSTALS-Dilithium",
                    is_quantum_safe=True,
                    overall_risk_level="LOW",
                    ai_powered=True
                )
            ]
            
            for analysis in sample_analyses:
                db.add(analysis)
        
        db.commit()
        print("✅ Sample analytics data added successfully!")
        print(f"📊 Total Analyzed: {summary.total_analyzed}")
        print(f"🔒 Quantum Safe: {summary.quantum_safe_count}")
        print(f"⚠️  Classical: {summary.classical_count}")
        print(f"🕒 Last Updated: {summary.last_updated}")
        
    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("📊 Adding sample analytics data...")
    add_sample_analytics()