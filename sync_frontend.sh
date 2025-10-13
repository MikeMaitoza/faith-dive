#!/bin/bash

# Faith Dive Frontend Sync Script
# This script syncs the public directory to the build directory
# and ensures the correct paths are used for the build environment

echo "🔄 Syncing Faith Dive frontend..."

# Copy index.html from public to build
cp frontend/public/index.html frontend/build/index.html
echo "✅ Copied index.html"

# Copy app.js from public to build/static
cp frontend/public/app.js frontend/build/static/app.js
echo "✅ Copied app.js"

# Fix the JavaScript path in build/index.html to use /static/app.js
sed -i 's|src="/app.js"|src="/static/app.js"|g' frontend/build/index.html
echo "✅ Fixed JavaScript path in build/index.html"

# Ensure Twitter icon uses the standard fa-twitter class
sed -i 's|fa-x-twitter|fa-twitter|g' frontend/build/index.html
echo "✅ Fixed Twitter icon class"

echo "🎉 Frontend sync complete! The build directory is now up to date."
echo "🌐 Your Faith Dive app at http://localhost:8000 should now show the latest changes."