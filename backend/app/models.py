from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

# Public Key Algorithms Table
class PublicKeyAlgorithm(Base):
    __tablename__ = "public_key_algorithms"

    id = Column(Integer, primary_key=True, index=True)
    public_key_algorithm_name = Column(String(255), nullable=False)
    public_key_algorithm_oid = Column(String(255), nullable=True)
    category = Column(String(50), nullable=False)
    is_pqc = Column(Boolean, nullable=True)

# Signature Algorithms Table
class SignatureAlgorithm(Base):
    __tablename__ = "signature_algorithms"

    id = Column(Integer, primary_key=True, index=True)
    signature_algorithm_name = Column(String(255), nullable=False)
    signature_algorithm_oid = Column(String(255), nullable=True)
    category = Column(String(50), nullable=False)
    is_pqc = Column(Boolean, nullable=False)
