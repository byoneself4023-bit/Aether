#!/bin/bash

echo "Setting up Civil Complaint Management System..."

# Create virtual environments
echo "Creating Python virtual environments..."

# ML Service
cd ml-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# LLM Service
cd llm-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# Frontend
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "Setup complete!"
