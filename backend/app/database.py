from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Replace with your Azure SQL details
server   = "quantumcertify-sqlsrv.database.windows.net"
database = "QuantumCertifyDB"
username = "sqladminuser"
password = "Subhash1234#"

# ODBC connection string format
odbc_str = (
    f"mssql+pyodbc://{username}:{password}@{server}:1433/{database}"
    "?driver=SQL+Server&Encrypt=yes&TrustServerCertificate=no"
)

# Create SQLAlchemy engine
engine = create_engine(odbc_str)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()