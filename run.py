#!/usr/bin/env python3
"""
Faith Dive Development Server
Simple script to run the FastAPI development server
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import build script
from build_frontend import build_frontend

def main():
    """Run the development server"""
    # Build frontend first
    print("🔨 Building frontend...")
    build_frontend()
    print()
    
    print("🚀 Starting Faith Dive development server...")
    print("📖 API Documentation available at: http://localhost:8000/docs")
    print("🎯 Application available at: http://localhost:8000")
    print("✨ Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["backend", "frontend"]
    )

if __name__ == "__main__":
    main()