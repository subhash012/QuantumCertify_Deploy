#!/usr/bin/env python3
"""
Test database connection
"""
import sys
import os
sys.path.append('.')

try:
    from app.database import SessionLocal, engine
    from sqlalchemy import text
    import time
    
    print("Testing database connection...")
    
    # Test basic connection
    start_time = time.time()
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            row = result.fetchone()
            connection_time = time.time() - start_time
            
            print(f"✓ Database connection successful!")
            print(f"✓ Connection time: {connection_time:.2f} seconds")
            print(f"✓ Test query result: {row[0] if row else 'No result'}")
    except Exception as e:
        connection_time = time.time() - start_time
        print(f"✗ Database connection failed after {connection_time:.2f} seconds")
        print(f"✗ Error: {e}")
        sys.exit(1)
    
    # Test session creation
    try:
        db = SessionLocal()
        print("✓ Database session created successfully")
        db.close()
    except Exception as e:
        print(f"✗ Database session creation failed: {e}")
        sys.exit(1)
    
    print("\n✓ All database tests passed!")
    
except Exception as e:
    print(f"Error testing database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)