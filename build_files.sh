#!/bin/bash

# Build the project
echo "Building the project..."
python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear

# Make build_files.sh executable
chmod +x build_files.sh
