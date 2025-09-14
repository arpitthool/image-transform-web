#!/bin/bash

# Build TypeScript files
echo "Building TypeScript files..."
npm run build

# Start the Flask application
echo "Starting Flask application..."
python3 app.py
