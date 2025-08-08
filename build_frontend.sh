#!/bin/bash
set -e

echo "Building frontend..."

# Change to frontend directory
cd frontend

# Install dependencies if package-lock.json exists
if [ -f "package-lock.json" ]; then
    echo "Installing frontend dependencies..."
    npm ci
else
    echo "Installing frontend dependencies (no package-lock found)..."
    npm install
fi

# Build the frontend
echo "Building Next.js application..."
npm run build

echo "Frontend build completed successfully!"
ls -la dist/

echo "Checking if index.html exists..."
if [ -f "dist/index.html" ]; then
    echo "✅ Frontend build successful - index.html found"
else
    echo "❌ Frontend build failed - index.html not found"
    exit 1
fi