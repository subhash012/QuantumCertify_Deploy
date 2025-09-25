#!/usr/bin/env python3
"""
FastAPI server startup script for QuantumCertify backend
"""
import uvicorn
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

if __name__ == "__main__":
    print("Starting QuantumCertify API server...")
    print("API will be available at: http://127.0.0.1:8000")
    print("API documentation at: http://127.0.0.1:8000/docs")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["."],
        log_level="info"
    )