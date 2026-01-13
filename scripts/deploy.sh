#!/bin/bash

echo "Deploying Civil Complaint Management System..."

# Build Docker images
echo "Building Docker images..."
docker-compose build

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Health checks
echo "Checking service health..."
curl -s http://localhost:8080/health || echo "Gateway not ready"
curl -s http://localhost:8001/health || echo "ML Service not ready"
curl -s http://localhost:8002/health || echo "LLM Service not ready"

echo "Deployment complete!"
echo "Services available at:"
echo "- Gateway: http://localhost:8080"
echo "- ML Service: http://localhost:8001"
echo "- LLM Service: http://localhost:8002"
echo "- Frontend: http://localhost:3000"
