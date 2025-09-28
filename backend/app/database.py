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
        f"?driver={DB_DRIVER}&Encrypt=yes&TrustServerCertificate=no"
    )

    # Create SQLAlchemy engine with additional security configurations
    engine = create_engine(
        odbc_str,
        pool_pre_ping=True,  # Enable connection health checks
        pool_recycle=3600,   # Recycle connections every hour
        echo=os.getenv('DEBUG', 'false').lower() == 'true',  # Log SQL queries in debug mode
        # SQL Server specific configurations
        connect_args={
            "driver": "ODBC Driver 17 for SQL Server",
            "TrustServerCertificate": "no",
            "Encrypt": "yes"
        }
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()