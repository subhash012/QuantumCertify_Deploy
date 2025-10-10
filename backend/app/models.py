from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from .database import Base

# Public Key Algorithms Table
class PublicKeyAlgorithm(Base):
    __tablename__ = "public_key_algorithms"

    id = Column(Integer, primary_key=True, index=True)
    public_key_algorithm_name = Column(String(255), nullable=False)
    public_key_algorithm_oid = Column(String(255), nullable=True)
    category = Column(String(50), nullable=False, default="Unknown")
    is_pqc = Column(Boolean, nullable=True, default=False)
    description = Column(Text, nullable=True)
    security_level = Column(String(50), nullable=True)
    is_quantum_safe = Column(Boolean, nullable=True, default=False)
    key_size = Column(Integer, nullable=True)

# Signature Algorithms Table
class SignatureAlgorithm(Base):
    __tablename__ = "signature_algorithms"

    id = Column(Integer, primary_key=True, index=True)
    signature_algorithm_name = Column(String(255), nullable=False)
    signature_algorithm_oid = Column(String(255), nullable=True)
    category = Column(String(50), nullable=False, default="Unknown")
    is_pqc = Column(Boolean, nullable=False, default=False)
    description = Column(Text, nullable=True)
    security_level = Column(String(50), nullable=True)
    is_quantum_safe = Column(Boolean, nullable=True, default=False)

# Certificate Analysis Records
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

# Analytics Summary Table (for dashboard stats)
class AnalyticsSummary(Base):
    __tablename__ = "analytics_summary"

    id = Column(Integer, primary_key=True, index=True)
    total_analyzed = Column(Integer, default=0)
    quantum_safe_count = Column(Integer, default=0)
    classical_count = Column(Integer, default=0)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
