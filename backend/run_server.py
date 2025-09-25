#!/usr/bin/env python3
"""
FastAPI server startup script
"""
import uvicorn
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["."]
    )