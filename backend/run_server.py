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
    
    print(f"🚀 Starting QuantumCertify server for Railway.app")
    print(f"🌐 Server: {host}:{port}")
    print(f"🔧 Environment: {environment}")
    print(f"📁 Working Directory: {os.getcwd()}")
    print(f"🐍 Python Path: {sys.path}")
    
    # Test critical environment variables
    required_env_vars = ['GEMINI_API_KEY', 'DB_SERVER', 'DB_NAME', 'DB_USERNAME', 'DB_PASSWORD', 'DB_DRIVER']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  Warning: Missing environment variables: {missing_vars}")
    else:
        print("✅ All required environment variables are set")
    
    # Import the FastAPI app with detailed error reporting
    try:
        print("📦 Importing FastAPI application...")
        from app.main import app
        print("✅ FastAPI application imported successfully")
        
        # Test that the app is properly configured
        print(f"📋 App title: {app.title}")
        print(f"📋 App version: {app.version}")
        
        # Test health endpoint exists
        routes = [route.path for route in app.routes]
        if "/health" in routes:
            print("✅ Health endpoint found in routes")
        else:
            print("⚠️  Health endpoint not found in routes")
        
    except ImportError as e:
        print(f"❌ Failed to import FastAPI app: {e}")
        print(f"🔍 Full traceback:")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error during app import: {e}")
        import traceback
        traceback.print_exc()
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
            "log_level": "info",  # Keep info level for better debugging
            "access_log": True,   # Keep access logs for debugging
        })
    
    print(f"⚙️  Starting uvicorn with config:")
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    try:
        print("🎯 Starting uvicorn server...")
        uvicorn.run(**config)
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
