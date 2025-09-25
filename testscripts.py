import pyodbc

conn_str = (
    "Driver={SQL Server};Server=tcp:quantumcertify-sqlsrv.database.windows.net,1433;Database=QuantumCertifyDB;Uid=sqladminuser;Pwd=Subhash1234#;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=10;"
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    row = cursor.fetchone()
    print("Connection successful, test value:", row[0])
except Exception as e:
    print("Error:", e)