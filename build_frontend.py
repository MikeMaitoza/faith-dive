#!/usr/bin/env python3
"""
Frontend Build Script for Faith Dive
Copies frontend files from public to build directory for serving
"""

import os
import shutil
from pathlib import Path

def build_frontend():
    """Build the frontend by copying files to the build directory"""
    
    # Define paths
    project_root = Path(__file__).parent
    public_dir = project_root / "frontend" / "public"
    build_dir = project_root / "frontend" / "build"
    static_dir = build_dir / "static"
    
    print("🚀 Building Faith Dive frontend...")
    
    # Create build directories
    build_dir.mkdir(exist_ok=True)
    static_dir.mkdir(exist_ok=True)
    
    # Copy main HTML file
    shutil.copy2(public_dir / "index.html", build_dir / "index.html")
    print("✅ Copied index.html")
    
    # Copy JavaScript to static directory
    shutil.copy2(public_dir / "app.js", static_dir / "app.js")
    print("✅ Copied app.js to static/")
    
    # Copy PWA files
    shutil.copy2(public_dir / "manifest.json", build_dir / "manifest.json")
    print("✅ Copied manifest.json")
    
    shutil.copy2(public_dir / "sw.js", build_dir / "sw.js")
    print("✅ Copied service worker")
    
    # Update HTML to reference static JS file
    html_file = build_dir / "index.html"
    content = html_file.read_text()
    content = content.replace('src="/app.js"', 'src="/static/app.js"')
    html_file.write_text(content)
    print("✅ Updated HTML script references")
    
    print("🎉 Frontend build complete!")
    print(f"📁 Build output: {build_dir}")

if __name__ == "__main__":
    build_frontend()