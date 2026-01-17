"""Voice Client - Test Griot's voice interaction capabilities"""
import asyncio
import httpx
import json
from pathlib import Path


async def test_text_to_speech():
    """Test text-to-speech endpoint."""
    print("🎤 Testing Text-to-Speech...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Ask Griot to tell a story
            message = "Tell me a brief story about the griot tradition in West Africa"
            
            response = await client.post(
                "http://localhost:8000/api/v1/voice/text",
                params={
                    "text": message,
                    "voice": "nova"
                }
            )
            
            if response.status_code == 200:
                # Save the audio
                audio_path = Path("griot_story.mp3")
                audio_path.write_bytes(response.content)
                print(f"✅ Audio saved to {audio_path}")
                print(f"   Play with: open {audio_path} (Mac) or mpg123 {audio_path} (Linux)")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   {response.text}")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            print("   Make sure the server is running!")
            return False


async def test_full_voice_interaction(audio_file_path: str):
    """
    Test full voice interaction (speech-to-text + generation + text-to-speech).
    
    Args:
        audio_file_path: Path to an audio file to send
    """
    print(f"🎤 Testing Full Voice Interaction with {audio_file_path}...")
    
    audio_path = Path(audio_file_path)
    if not audio_path.exists():
        print(f"❌ Audio file not found: {audio_file_path}")
        return False
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            with open(audio_path, "rb") as f:
                files = {"audio": (audio_path.name, f, "audio/wav")}
                response = await client.post(
                    "http://localhost:8000/api/v1/voice",
                    files=files
                )
            
            if response.status_code == 200:
                output_path = Path("griot_answer.mp3")
                output_path.write_bytes(response.content)
                print(f"✅ Griot's response saved to {output_path}")
                print(f"   Play with: open {output_path} (Mac) or mpg123 {output_path} (Linux)")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   {response.text}")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            print("   Make sure the server is running!")
            return False


if __name__ == "__main__":
    import sys
    
    print("🎭 Griot Voice Interaction Test Client\n")
    
    if len(sys.argv) > 1:
        # Test with provided audio file
        asyncio.run(test_full_voice_interaction(sys.argv[1]))
    else:
        # Test text-to-speech only
        print("Usage:")
        print("  1. Test text-to-speech: python voice_client.py")
        print("  2. Test full voice interaction: python voice_client.py <audio_file.wav>\n")
        asyncio.run(test_text_to_speech())
