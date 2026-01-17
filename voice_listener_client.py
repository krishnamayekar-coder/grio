"""Real-time Voice Client - Listen for wake word "Griot" and respond to queries"""
import asyncio
import websockets
import json
import pyaudio
import wave
import io
from pathlib import Path
from typing import Optional
import base64

# Audio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000


def create_wav_from_bytes(audio_bytes: bytes) -> bytes:
    """Convert raw PCM audio bytes to WAV format."""
    wav_buffer = io.BytesIO()
    
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)  # 16-bit = 2 bytes
        wav_file.setframerate(RATE)
        wav_file.writeframes(audio_bytes)
    
    return wav_buffer.getvalue()


class GriotVoiceClient:
    """Client for real-time voice interaction with Griot."""
    
    def __init__(self, uri: str = "ws://localhost:8000/api/v1/ws/voice"):
        """Initialize the voice client."""
        self.uri = uri
        self.recording = False
        self.audio = pyaudio.PyAudio()
    
    async def run(self):
        """Start the real-time voice interaction."""
        print("🎭 Griot Voice Client")
        print("=" * 50)
        print("Say 'Griot' to activate, then ask your question")
        print("Press Ctrl+C to exit")
        print("=" * 50 + "\n")
        
        try:
            async with websockets.connect(self.uri) as websocket:
                # Start recording task
                record_task = asyncio.create_task(
                    self._record_and_send(websocket)
                )
                
                # Start receiving task
                receive_task = asyncio.create_task(
                    self._receive_responses(websocket)
                )
                
                # Wait for tasks
                await asyncio.gather(record_task, receive_task)
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.audio.terminate()
    
    async def _record_and_send(self, websocket):
        """Record audio from microphone and send to server."""
        try:
            stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            print("🎤 Recording started...\n")
            
            audio_buffer = b""
            chunk_count = 0
            
            try:
                while True:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    audio_buffer += data
                    chunk_count += 1
                    
                    # Send audio every 2 seconds (32 chunks at CHUNK=1024, RATE=16000)
                    if chunk_count >= 32:
                        # Convert to WAV format
                        wav_audio = create_wav_from_bytes(audio_buffer)
                        await websocket.send(wav_audio)
                        audio_buffer = b""
                        chunk_count = 0
                    
                    await asyncio.sleep(0.01)
            finally:
                # Send remaining audio
                if audio_buffer:
                    wav_audio = create_wav_from_bytes(audio_buffer)
                    await websocket.send(wav_audio)
                
                stream.stop_stream()
                stream.close()
        except Exception as e:
            print(f"❌ Recording error: {e}")
    
    async def _receive_responses(self, websocket):
        """Receive and handle responses from server."""
        wake_word_detected = False
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")
                    
                    if msg_type == "status":
                        print(f"📡 {data.get('message')}")
                    
                    elif msg_type == "waiting":
                        heard = data.get('heard', '')
                        if heard:
                            print(f"   Heard: '{heard}' (say 'Griot' - try pronouncing it 'GREE-oh')")
                    
                    elif msg_type == "wake_word_detected":
                        wake_word_detected = True
                        print(f"\n✨ {data.get('message')}\n")
                        # Signal server to listen for query
                        # The client will continue sending audio
                    
                    elif msg_type == "processing":
                        print(f"⏳ {data.get('message')}")
                    
                    elif msg_type == "response":
                        text = data.get('text', '')
                        audio_b64 = data.get('audio', '')
                        
                        print(f"\n🎤 Griot: {text}\n")
                        
                        # Save and play audio response
                        if audio_b64:
                            audio_bytes = base64.b64decode(audio_b64)
                            output_file = Path("griot_response.mp3")
                            output_file.write_bytes(audio_bytes)
                            print(f"💾 Response saved to {output_file}")
                            print(f"   Play with: open {output_file}\n")
                        
                        # Signal ready for next interaction
                        print("🎤 Ready for next question...\n")
                    
                    elif msg_type == "error":
                        print(f"❌ Error: {data.get('message')}\n")
                
                except json.JSONDecodeError:
                    pass  # Ignore non-JSON messages
        
        except websockets.exceptions.ConnectionClosed:
            print("❌ Connection closed")
        except Exception as e:
            print(f"❌ Receive error: {e}")


async def main():
    """Main entry point."""
    client = GriotVoiceClient()
    await client.run()


if __name__ == "__main__":
    try:
        import pyaudio
    except ImportError:
        print("❌ PyAudio not installed. Install with:")
        print("   pip install pyaudio")
        exit(1)
    
    print("Starting Griot Voice Client...\n")
    asyncio.run(main())
