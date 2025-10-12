import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration from environment variables
DB_SERVER = os.getenv('DB_SERVER', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'quantumcertify')
DB_USERNAME = os.getenv('DB_USERNAME', 'admin')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_PORT = os.getenv('DB_PORT', '1433')
DB_DRIVER = os.getenv('DB_DRIVER', 'sqlite')

# Create connection string based on driver type
if DB_DRIVER.lower() == 'sqlite':
    # SQLite connection for local development
    database_url = f"sqlite:///{DB_NAME}"
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},  # SQLite specific
        echo=os.getenv('DEBUG', 'false').lower() == 'true'
    )
else:
    # SQL Server connection for production
    # Validate required environment variables for SQL Server
    if not all([DB_SERVER, DB_NAME, DB_USERNAME, DB_PASSWORD]):
        raise ValueError(
            "Missing required database environment variables. "
            "Please check your .env file for DB_SERVER, DB_NAME, DB_USERNAME, and DB_PASSWORD"
        )
    
    # ODBC connection string format with environment variables
    odbc_str = (
        f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"
        f"?driver={DB_DRIVER}&Encrypt=yes&TrustServerCertificate=no&MultipleActiveResultSets=False"
    )

    # Create SQLAlchemy engine with optimized settings for Azure SQL Database
    engine = create_engine(
        odbc_str,
        pool_pre_ping=True,  # Enable connection health checks before using
        pool_recycle=1800,   # Recycle connections every 30 minutes (Azure SQL idle timeout is 30 min)
        pool_timeout=120,    # Wait up to 120 seconds for a connection from the pool (increased from 60)
        pool_size=5,         # Maintain 5 persistent connections in the pool (increased from 3)
        max_overflow=10,     # Allow up to 10 additional connections (total max: 15)
        echo=os.getenv('DEBUG', 'false').lower() == 'true',  # Log SQL queries in debug mode
        # SQL Server specific configurations - Optimized for Railway to Azure SQL cross-region
        connect_args={
            "driver": DB_DRIVER,  # Use environment variable (ODBC Driver 17/18 for SQL Server)
            "TrustServerCertificate": "no",
            "Encrypt": "yes",
            "Connection Timeout": "90",  # Increased to 90 seconds for cross-region reliability
            "Login Timeout": "90",       # Increased to 90 seconds for initial connection
            "Pooling": "True",           # Enable connection pooling at ODBC level
            "MultipleActiveResultSets": "False",
            "ApplicationIntent": "ReadWrite",
            "ConnectRetryCount": "3",    # Retry connection 3 times on failure
            "ConnectRetryInterval": "10" # Wait 10 seconds between retries
        }
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()