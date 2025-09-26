#!/usr/bin/env python3
"""
Alternative database initialization using direct SQL commands
"""

import os
import sys
from sqlalchemy import create_engine, text
import logging

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables_with_sql():
    """Create tables using direct SQL commands"""
    try:
        from app.database import engine
        
        # SQL statements to create tables
        create_tables_sql = [
            """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='public_key_algorithms' AND xtype='U')
            CREATE TABLE public_key_algorithms (
                id INT IDENTITY(1,1) PRIMARY KEY,
                public_key_algorithm_name NVARCHAR(255) NOT NULL,
                public_key_algorithm_oid NVARCHAR(255) NULL,
                category NVARCHAR(50) NOT NULL,
                is_pqc BIT NULL
            )
            """,
            """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='signature_algorithms' AND xtype='U')
            CREATE TABLE signature_algorithms (
                id INT IDENTITY(1,1) PRIMARY KEY,
                signature_algorithm_name NVARCHAR(255) NOT NULL,
                signature_algorithm_oid NVARCHAR(255) NULL,
                category NVARCHAR(50) NOT NULL,
                is_pqc BIT NOT NULL
            )
            """,
            """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='certificate_analyses' AND xtype='U')
            CREATE TABLE certificate_analyses (
                id INT IDENTITY(1,1) PRIMARY KEY,
                file_name NVARCHAR(255) NOT NULL,
                subject NVARCHAR(1000) NULL,
                issuer NVARCHAR(1000) NULL,
                expiry_date DATETIME NULL,
                public_key_algorithm NVARCHAR(255) NULL,
                signature_algorithm NVARCHAR(255) NULL,
                is_quantum_safe BIT NOT NULL,
                overall_risk_level NVARCHAR(50) NULL,
                analysis_timestamp DATETIME DEFAULT GETDATE(),
                ai_powered BIT DEFAULT 0
            )
            """,
            """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='analytics_summary' AND xtype='U')
            CREATE TABLE analytics_summary (
                id INT IDENTITY(1,1) PRIMARY KEY,
                total_analyzed INT DEFAULT 0,
                quantum_safe_count INT DEFAULT 0,
                classical_count INT DEFAULT 0,
                last_updated DATETIME DEFAULT GETDATE()
            )
            """
        ]
        
        logger.info("Creating database tables with direct SQL...")
        
        with engine.connect() as connection:
            # Start transaction
            trans = connection.begin()
            
            try:
                for sql in create_tables_sql:
                    logger.info(f"Executing SQL statement...")
                    connection.execute(text(sql))
                
                # Commit transaction
                trans.commit()
                logger.info("✅ All tables created successfully!")
                
                # Insert initial analytics record if it doesn't exist
                check_and_insert_sql = """
                IF NOT EXISTS (SELECT 1 FROM analytics_summary)
                BEGIN
                    INSERT INTO analytics_summary (total_analyzed, quantum_safe_count, classical_count)
                    VALUES (0, 0, 0)
                END
                """
                
                connection.execute(text(check_and_insert_sql))
                logger.info("✅ Initial analytics record created!")
                
                return True
                
            except Exception as e:
                trans.rollback()
                logger.error(f"❌ Error creating tables: {e}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")
        return False

def verify_tables():
    """Verify that all tables were created successfully"""
    try:
        from app.database import engine
        
        table_check_sql = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        AND TABLE_NAME IN ('public_key_algorithms', 'signature_algorithms', 'certificate_analyses', 'analytics_summary')
        """
        
        with engine.connect() as connection:
            result = connection.execute(text(table_check_sql))
            tables = [row[0] for row in result.fetchall()]
            
            expected_tables = ['public_key_algorithms', 'signature_algorithms', 'certificate_analyses', 'analytics_summary']
            
            for table in expected_tables:
                if table in tables:
                    logger.info(f"✅ Table '{table}' exists")
                else:
                    logger.warning(f"❌ Table '{table}' not found")
            
            return len(tables) == len(expected_tables)
            
    except Exception as e:
        logger.error(f"❌ Error verifying tables: {e}")
        return False

if __name__ == "__main__":
    print("🚀 QuantumCertify Database Setup (Direct SQL)")
    print("=" * 50)
    
    if create_tables_with_sql():
        print("\n📊 Verifying database tables...")
        if verify_tables():
            print("\n🎉 Database setup completed successfully!")
            print("\nYou can now start the QuantumCertify server with:")
            print("python run_server.py")
        else:
            print("\n⚠️  Some tables may not have been created properly")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)