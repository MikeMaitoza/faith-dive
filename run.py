#!/usr/bin/env python3
"""
Faith Dive Development Server
Simple script to run the FastAPI development server
"""

import uvicorn
import os
import sys

# Add backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def main():
    """Run the development server"""
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