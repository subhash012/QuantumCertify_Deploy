#!/usr/bin/env python3
"""
Database initialization script for QuantumCertify
Creates all necessary tables and sets up initial data
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database tables and data"""
    try:
        # Import after path setup
        from app.database import engine, Base, DB_SERVER, DB_NAME
        from app.models import PublicKeyAlgorithm, SignatureAlgorithm, CertificateAnalysis, AnalyticsSummary
        
        logger.info(f"Connecting to database: {DB_SERVER}/{DB_NAME}")
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ All tables created successfully!")
        
        # Test database connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("✅ Database connection test successful!")
        
        logger.info("🎉 Database initialization completed successfully!")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"❌ Database error: {e}")
        return False
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Make sure you're running this from the backend directory and .env file is properly configured")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

def check_tables():
    """Check if all required tables exist"""
    try:
        from app.database import engine
        
        with engine.connect() as connection:
            # Check for our tables
            tables_to_check = [
                'public_key_algorithms',
                'signature_algorithms', 
                'certificate_analyses',
                'analytics_summary'
            ]
            
            for table_name in tables_to_check:
                result = connection.execute(text(f"""
                    SELECT COUNT(*) as count 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = '{table_name}'
                """))
                count = result.fetchone()[0]
                
                if count > 0:
                    logger.info(f"✅ Table '{table_name}' exists")
                else:
                    logger.warning(f"❌ Table '{table_name}' does not exist")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error checking tables: {e}")
        return False

def seed_initial_data():
    """Insert initial analytics summary record if it doesn't exist"""
    try:
        from app.database import SessionLocal
        from app.models import AnalyticsSummary
        
        db = SessionLocal()
        
        # Check if analytics summary exists
        existing = db.query(AnalyticsSummary).first()
        
        if not existing:
            # Create initial summary record
            initial_summary = AnalyticsSummary(
                total_analyzed=0,
                quantum_safe_count=0,
                classical_count=0
            )
            db.add(initial_summary)
            db.commit()
            logger.info("✅ Initial analytics summary record created")
        else:
            logger.info("✅ Analytics summary already exists")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error seeding initial data: {e}")
        return False

if __name__ == "__main__":
    print("🚀 QuantumCertify Database Initialization")
    print("=" * 50)
    
    # Initialize database
    if init_database():
        print("\n📊 Checking database tables...")
        check_tables()
        
        print("\n🌱 Seeding initial data...")
        seed_initial_data()
        
        print("\n🎉 Database setup completed successfully!")
        print("\nYou can now start the QuantumCertify server with:")
        print("python run_server.py")
    else:
        print("\n❌ Database initialization failed!")
        print("Please check your database configuration in .env file")
        sys.exit(1)