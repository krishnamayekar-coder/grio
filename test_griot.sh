#!/bin/bash
# Quick test script using curl to verify Griot responses

echo "🏥 Testing Health Endpoint..."
curl -X GET http://localhost:8000/api/v1/health -H "Content-Type: application/json"
echo -e "\n\n"

echo "🎭 Testing Griot Chat - Request 1: Storytelling"
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "Tell me a short story about an ancient civilization"
  }'
echo -e "\n\n"

echo "🎭 Testing Griot Chat - Request 2: Knowledge Sharing"
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "What is the role of a griot in West African culture?"
  }'
echo -e "\n\n"

echo "🎭 Testing Griot Chat - Request 3: Historical Inquiry"
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "Teach me about the Mali Empire"
  }'
echo -e "\n\n"

echo "✅ Tests complete!"
