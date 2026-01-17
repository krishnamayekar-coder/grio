"""Test script to verify Griot API responses"""
import httpx
import json
import sys


async def test_griot():
    """Test Griot chat endpoint and verify personality."""
    
    # Test messages to verify Griot personality
    test_messages = [
        "Tell me a short story about West Africa",
        "What is a griot?",
        "Teach me something about history",
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # First, test health endpoint
        print("🏥 Testing health endpoint...")
        try:
            response = await client.get("http://localhost:8000/api/v1/health")
            if response.status_code == 200:
                print(f"✅ Health check passed: {response.json()}\n")
            else:
                print(f"❌ Health check failed: {response.status_code}\n")
                return
        except Exception as e:
            print(f"❌ Could not connect to server: {e}")
            print("   Make sure the server is running with: python -m uvicorn app.main:app --reload\n")
            return
        
        # Test chat endpoint with different messages
        print("🎭 Testing Griot personality...\n")
        for msg in test_messages:
            print(f"📤 User: {msg}")
            try:
                response = await client.post(
                    "http://localhost:8000/api/v1/chat",
                    json={
                        "user_id": "test_user",
                        "message": msg
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"🎤 Griot: {data['message'][:200]}...")  # Show first 200 chars
                    print(f"⏰ Model: {data['model']}\n")
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"   {response.text}\n")
            except Exception as e:
                print(f"❌ Request failed: {e}\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_griot())
