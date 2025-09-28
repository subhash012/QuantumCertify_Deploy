import pyodbc
import os

# Railway environment variables
DB_SERVER = os.getenv("DB_SERVER", "quantumcertify-sqlsrv.database.windows.net")
DB_NAME = os.getenv("DB_NAME", "QuantumCertifyDB")
DB_USERNAME = os.getenv("DB_USERNAME", "sqladminuser")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Connection string for Railway Linux environment
connection_string = f"""Driver={{ODBC Driver 18 for SQL Server}};
                        Server={DB_SERVER};
                        Database={DB_NAME};
                        UID={DB_USERNAME};
                        PWD={DB_PASSWORD};
                        Encrypt=yes;
                        TrustServerCertificate=no;
                        Connection Timeout=30;"""

try:
    conn = pyodbc.connect(connection_string)
    print("? Database connection successful!")
    conn.close()
except Exception as e:
    print(f"? Database connection failed: {e}")
