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
import tempfile
import os

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
        self.pause_recording = False  # Flag to pause recording during playback
        self.audio = pyaudio.PyAudio()
        self._init_audio_player()
    
    def _init_audio_player(self):
        """Initialize audio player for TTS responses."""
        try:
            import pygame
            pygame.mixer.init()
            self.use_pygame = True
        except ImportError:
            try:
                # Try pydub with simpleaudio as fallback
                from pydub import AudioSegment
                from pydub.playback import play
                self.use_pydub = True
                self.AudioSegment = AudioSegment
                self.play = play
            except ImportError:
                # Last resort: use system command
                self.use_system = True
                self.use_pygame = False
                self.use_pydub = False
    
    async def _play_audio(self, audio_bytes: bytes):
        """Play audio bytes (MP3 format) automatically."""
        try:
            if hasattr(self, 'use_pygame') and self.use_pygame:
                import pygame
                # Use temporary file for pygame
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                    tmp_file.write(audio_bytes)
                    tmp_file.flush()
                    pygame.mixer.music.load(tmp_file.name)
                    pygame.mixer.music.play()
                    # Wait for playback to finish
                    while pygame.mixer.music.get_busy():
                        await asyncio.sleep(0.1)
                    os.unlink(tmp_file.name)
            
            elif hasattr(self, 'use_pydub') and self.use_pydub:
                # Use pydub for playback
                audio = self.AudioSegment.from_mp3(io.BytesIO(audio_bytes))
                # Play in a thread to avoid blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.play, audio)
            
            elif hasattr(self, 'use_system') and self.use_system:
                # Fallback to system command
                import platform
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                    tmp_file.write(audio_bytes)
                    tmp_file.flush()
                    
                    system = platform.system()
                    if system == "Darwin":  # macOS
                        os.system(f"afplay {tmp_file.name} &")
                    elif system == "Linux":
                        os.system(f"mpg123 -q {tmp_file.name} &")
                    elif system == "Windows":
                        os.system(f"start {tmp_file.name}")
                    
                    # Wait a bit for playback to start
                    await asyncio.sleep(0.5)
                    # Note: We can't easily wait for completion with system commands
                    # So we'll just delete after a delay
                    await asyncio.sleep(len(audio_bytes) / 16000)  # Rough estimate
                    try:
                        os.unlink(tmp_file.name)
                    except:
                        pass
        
        except Exception as e:
            print(f"⚠️  Could not play audio automatically: {e}")
            print("   Audio response saved to griot_response.mp3")
    
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
                    # Skip recording if paused (during playback)
                    if self.pause_recording:
                        await asyncio.sleep(0.1)
                        continue
                    
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
                        
                        # Save and automatically play audio response
                        if audio_b64:
                            audio_bytes = base64.b64decode(audio_b64)
                            output_file = Path("griot_response.mp3")
                            output_file.write_bytes(audio_bytes)
                            
                            # Pause recording during playback to avoid feedback
                            self.pause_recording = True
                            
                            # Automatically play the audio response
                            print("🔊 Playing response...")
                            await self._play_audio(audio_bytes)
                            print("✅ Response played\n")
                            
                            # Resume recording after playback
                            self.pause_recording = False
                        
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
    
    # Check for audio playback libraries
    try:
        import pygame
        print("✅ Using pygame for audio playback")
    except ImportError:
        try:
            from pydub import AudioSegment
            from pydub.playback import play
            print("✅ Using pydub for audio playback")
        except ImportError:
            print("⚠️  No audio playback library found. Install one of:")
            print("   pip install pygame")
            print("   pip install pydub simpleaudio")
            print("   (Audio will be saved but not played automatically)")
    
    print("\nStarting Griot Voice Client...\n")
    asyncio.run(main())
