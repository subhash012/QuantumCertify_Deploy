from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="QuantumCertify API",
    description="Certificate analysis and quantum-safe cryptography validation",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "QuantumCertify API is running", "version": "1.0.0"}

@app.post("/upload-certificate")
async def upload_certificate(file: UploadFile = File(...)):
    """
    Upload and analyze a certificate file (PEM or DER format)
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    try:
        cert_bytes = await file.read()
        
        # Try to parse the certificate
        try:
            # Try PEM first
            cert = x509.load_pem_x509_certificate(cert_bytes, default_backend())
        except Exception:
            try:
                # Fallback to DER
                cert = x509.load_der_x509_certificate(cert_bytes, default_backend())
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid certificate format: {str(e)}")

        # Extract certificate details
        issuer = cert.issuer.rfc4514_string()
        subject = cert.subject.rfc4514_string()
        public_key = cert.public_key()
        key_type = public_key.__class__.__name__
        key_size = getattr(public_key, "key_size", None)
        sig_algo = cert.signature_algorithm_oid._name
        expiry_date = cert.not_valid_after
        
        # Determine if the algorithm is quantum-safe
        is_quantum_safe = "dilithium" in sig_algo.lower() or "kyber" in sig_algo.lower() or "falcon" in sig_algo.lower()

        return {
            "file_name": file.filename,
            "issuer": issuer,
            "subject": subject,
            "key_type": key_type,
            "key_size": key_size,
            "signature_algorithm": sig_algo,
            "expiry_date": expiry_date.isoformat(),
            "is_quantum_safe": is_quantum_safe,
            "status": "Certificate parsed successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing certificate: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "QuantumCertify API"}
