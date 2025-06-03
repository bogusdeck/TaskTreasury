#!/bin/bash

# Ensure we're using the correct Python
which python3

# Create static directory if it doesn't exist
mkdir -p staticfiles

# Copy static files directly
cp -r static/* staticfiles/ 2>/dev/null || :
cp -r main/static/* staticfiles/ 2>/dev/null || :

# Create a directory for Gunicorn logs if it doesn't exist
mkdir -p logs
touch logs/gunicorn.log

echo "Build completed successfully!"
