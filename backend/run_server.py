#!/usr/bin/env python3
"""
QuantumCertify FastAPI Server - Railway.app Compatible
Optimized for Railway.app deployment with environment variable support
"""
import uvicorn
import os
import sys
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    # Railway.app provides PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"  # Important: Railway requires binding to 0.0.0.0
    
    # Environment detection
    environment = os.environ.get("RAILWAY_ENVIRONMENT", "development")
    
    print(f"?? Starting QuantumCertify server for Railway.app")
    print(f"?? Server: {host}:{port}")
    print(f"?? Environment: {environment}")
    print(f"?? Working Directory: {os.getcwd()}")
    
    # Import the FastAPI app
    try:
        from app.main import app
        print("? FastAPI application imported successfully")
    except ImportError as e:
        print(f"? Failed to import FastAPI app: {e}")
        sys.exit(1)
    
    # Configure uvicorn for Railway
    config = {
        "app": "app.main:app",
        "host": host,
        "port": port,
        "reload": False,  # Disable reload in production
        "access_log": True,
        "log_level": "info",
        "workers": 1,  # Railway free tier works best with 1 worker
        "timeout_keep_alive": 65,
        "timeout_graceful_shutdown": 30,
    }
    
    # Additional Railway-specific configuration
    if environment == "production":
        config.update({
            "log_level": "warning",
            "access_log": False,  # Reduce log noise in production
        })
    
    print(f"?? Starting uvicorn with config: {config}")
    
    try:
        uvicorn.run(**config)
    except Exception as e:
        print(f"? Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
