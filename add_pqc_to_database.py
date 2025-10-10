"""
Add PQC (Post-Quantum Cryptography) algorithms to the database
Includes ML-DSA, ML-KEM, and other NIST-standardized PQC algorithms
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.database import SessionLocal, engine
from backend.app.models import Base, PublicKeyAlgorithm, SignatureAlgorithm
from sqlalchemy.exc import IntegrityError

def add_pqc_algorithms():
    """Add PQC algorithms to the database"""
    print("Adding PQC algorithms to database...")
    print("=" * 60)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # PQC Public Key Algorithms
        pqc_public_key_algorithms = [
            {
                "public_key_algorithm_name": "ML-KEM-512 (CRYSTALS-Kyber)",
                "public_key_algorithm_oid": "2.16.840.1.101.3.4.4.1",
                "category": "PQC",
                "is_pqc": True
            },
            {
                "public_key_algorithm_name": "ML-KEM-768 (CRYSTALS-Kyber)",
                "public_key_algorithm_oid": "2.16.840.1.101.3.4.4.2",
                "category": "PQC",
                "is_pqc": True
            },
            {
                "public_key_algorithm_name": "ML-KEM-1024 (CRYSTALS-Kyber)",
                "public_key_algorithm_oid": "2.16.840.1.101.3.4.4.3",
                "category": "PQC",
                "is_pqc": True
            },
            {
                "public_key_algorithm_name": "CRYSTALS-Kyber512",
                "public_key_algorithm_oid": "1.3.6.1.4.1.2.267.7.6.5",
                "category": "PQC",
                "is_pqc": True
            },
            {
                "public_key_algorithm_name": "CRYSTALS-Kyber768",
                "public_key_algorithm_oid": "1.3.6.1.4.1.2.267.7.6.6",
                "category": "PQC",
                "is_pqc": True
            },
            {
                "public_key_algorithm_name": "CRYSTALS-Kyber1024",
                "public_key_algorithm_oid": "1.3.6.1.4.1.2.267.7.6.7",
                "category": "PQC",
                "is_pqc": True
            },
        ]
        
        # PQC Signature Algorithms
        pqc_signature_algorithms = [
            {
                "signature_algorithm_name": "ML-DSA-44 (CRYSTALS-Dilithium)",
                "signature_algorithm_oid": "2.16.840.1.101.3.4.3.17",
                "category": "PQC",
                "is_pqc": True
            },
            {
                "signature_algorithm_name": "ML-DSA-65 (CRYSTALS-Dilithium)",
                "signature_algorithm_oid": "2.16.840.1.101.3.4.3.17",
                "category": "PQC",
                "is_pqc": True
            },
            {
                "signature_algorithm_name": "ML-DSA-87 (CRYSTALS-Dilithium)",
                "signature_algorithm_oid": "2.16.840.1.101.3.4.3.18",
                "category": "PQC",
                "is_pqc": True
            },
            {
                "signature_algorithm_name": "CRYSTALS-Dilithium2",
                "signature_algorithm_oid": "1.3.6.1.4.1.2.267.7.8.7",
                "category": "PQC",
                "is_pqc": True
            },
            {
                "signature_algorithm_name": "CRYSTALS-Dilithium3",
                "signature_algorithm_oid": "1.3.6.1.4.1.2.267.7.8.8",
                "category": "PQC",
                "is_pqc": True
            },
            {
                "signature_algorithm_name": "CRYSTALS-Dilithium5",
                "signature_algorithm_oid": "1.3.6.1.4.1.2.267.7.8.9",
                "category": "PQC",
                "is_pqc": True
            },
            {
                "signature_algorithm_name": "FALCON-512",
                "signature_algorithm_oid": "1.3.9999.3.1",
                "category": "PQC",
                "is_pqc": True
            },
            {
                "signature_algorithm_name": "FALCON-1024",
                "signature_algorithm_oid": "1.3.9999.3.4",
                "category": "PQC",
                "is_pqc": True
            },
            {
                "signature_algorithm_name": "SPHINCS+-SHA256-128s",
                "signature_algorithm_oid": "1.3.9999.6.7.4",
                "category": "PQC",
                "is_pqc": True
            },
            {
                "signature_algorithm_name": "SPHINCS+-SHAKE256-128s",
                "signature_algorithm_oid": "1.3.9999.6.7.10",
                "category": "PQC",
                "is_pqc": True
            },
        ]
        
        # Add public key algorithms
        print("\nAdding Public Key Algorithms:")
        print("-" * 60)
        added_pk = 0
        for alg in pqc_public_key_algorithms:
            try:
                # Check if already exists
                existing = db.query(PublicKeyAlgorithm).filter_by(
                    public_key_algorithm_oid=alg["public_key_algorithm_oid"]
                ).first()
                
                if not existing:
                    pk_algo = PublicKeyAlgorithm(**alg)
                    db.add(pk_algo)
                    db.commit()
                    print(f"✅ Added: {alg['public_key_algorithm_name']}")
                    print(f"   OID: {alg['public_key_algorithm_oid']}")
                    added_pk += 1
                else:
                    print(f"⏭️  Skipped (exists): {alg['public_key_algorithm_name']}")
                    
            except IntegrityError:
                db.rollback()
                print(f"⚠️  Already exists: {alg['public_key_algorithm_name']}")
            except Exception as e:
                db.rollback()
                print(f"❌ Error adding {alg['public_key_algorithm_name']}: {e}")
        
        # Add signature algorithms
        print("\nAdding Signature Algorithms:")
        print("-" * 60)
        added_sig = 0
        for alg in pqc_signature_algorithms:
            try:
                # Check if already exists
                existing = db.query(SignatureAlgorithm).filter_by(
                    signature_algorithm_oid=alg["signature_algorithm_oid"],
                    signature_algorithm_name=alg["signature_algorithm_name"]
                ).first()
                
                if not existing:
                    sig_algo = SignatureAlgorithm(**alg)
                    db.add(sig_algo)
                    db.commit()
                    print(f"✅ Added: {alg['signature_algorithm_name']}")
                    print(f"   OID: {alg['signature_algorithm_oid']}")
                    added_sig += 1
                else:
                    print(f"⏭️  Skipped (exists): {alg['signature_algorithm_name']}")
                    
            except IntegrityError:
                db.rollback()
                print(f"⚠️  Already exists: {alg['signature_algorithm_name']}")
            except Exception as e:
                db.rollback()
                print(f"❌ Error adding {alg['signature_algorithm_name']}: {e}")
        
        print("\n" + "=" * 60)
        print(f"✅ Summary:")
        print(f"   Public Key Algorithms added: {added_pk}")
        print(f"   Signature Algorithms added: {added_sig}")
        print(f"   Total: {added_pk + added_sig}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔐 PQC Algorithm Database Populator")
    print("=" * 60)
    print("This script adds NIST-standardized PQC algorithms")
    print("including ML-DSA, ML-KEM, FALCON, and SPHINCS+")
    print("=" * 60)
    
    add_pqc_algorithms()
    
    print("\n✅ Done! Your database now includes PQC algorithms.")
