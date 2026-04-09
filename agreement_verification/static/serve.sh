#!/bin/bash
# Simple server script for the frontend

PORT=${1:-8080}

echo "Starting Agreement Verification Frontend on port $PORT..."
echo "Access at: http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop"

# Try Python 3, then Python 2
if command -v python3 &> /dev/null; then
    python3 -m http.server $PORT
elif command -v python &> /dev/null; then
    python -m SimpleHTTPServer $PORT
else
    echo "Error: Python not found. Please install Python or use another HTTP server."
    exit 1
fi
