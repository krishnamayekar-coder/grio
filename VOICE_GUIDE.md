# Real-time Voice Interaction with Wake Word Detection

Now Griot listens for the wake word "griot" just like Alexa! 🎤

## How It Works

1. **Always Listening**: The application listens to your microphone continuously
2. **Wake Word Detection**: When you say "griot", it activates
3. **Process Query**: Once activated, it listens to your question
4. **Generate Response**: Griot thinks about your question
5. **Speak Response**: Griot speaks back the answer as audio

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note for PyAudio on Mac:**
```bash
brew install portaudio
pip install pyaudio
```

### 2. Start the Backend Server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Run the Voice Client

In a new terminal:

```bash
python voice_listener_client.py
```

You'll see:
```
🎭 Griot Voice Client
==================================================
Say 'Griot' to activate, then ask your question
Press Ctrl+C to exit
==================================================

🎤 Recording started...
📡 🎤 Listening for 'Griot'... say 'Griot' to activate
```

### 4. Interact with Griot

1. **Say "Griot"** → The client will respond with "✨ Hello! I'm listening... what would you like to know?"
2. **Ask your question** → e.g., "Tell me a story about Mali"
3. **Listen to response** → Griot will speak back with the answer
4. Response is saved as `griot_response.mp3`

## Example Interaction

```
🎤 Recording started...

📡 🎤 Listening for 'Griot'... say 'Griot' to activate

   Heard: 'griot tell me a story' (keep saying 'Griot')

✨ Hello! I'm listening... what would you like to know?

🎤 Listening for your question...

⏳ 📖 Processing your query...

🎤 Griot: Once upon a time in the great Mali Empire, there lived a griot 
named Mamadou who carried the stories of his people...

💾 Response saved to griot_response.mp3

🎤 Ready for next question...
```

## Troubleshooting

### PyAudio Not Working
```bash
# On Mac
brew install portaudio
pip uninstall pyaudio
pip install pyaudio

# On Linux
sudo apt-get install portaudio19-dev
pip install pyaudio

# On Windows - use pre-built wheel
pip install pipwin
pipwin install pyaudio
```

### No Microphone Access
- Check system microphone permissions
- Test with: `python -c "import pyaudio; p = pyaudio.PyAudio(); print(p.get_device_info_by_index(0))"`

### WebSocket Connection Error
- Make sure the server is running on `http://localhost:8000`
- Check firewall settings

### Transcription Errors
- Ensure `OPENAI_API_KEY` is set in `.env`
- Check that you have OpenAI credits

## Files

- [app/services/wake_word_service.py](app/services/wake_word_service.py) - Wake word detection
- [app/api/v1/realtime.py](app/api/v1/realtime.py) - WebSocket endpoint
- [voice_listener_client.py](voice_listener_client.py) - Python client for testing

## API Details

### WebSocket Endpoint
```
ws://localhost:8000/api/v1/ws/voice
```

### Message Types
- `status` - Server status updates
- `wake_word_detected` - Wake word was detected
- `processing` - Server is processing query
- `response` - Server response with text and audio
- `error` - Error occurred

## Customization

### Change Wake Word
Edit [app/services/wake_word_service.py](app/services/wake_word_service.py):
```python
wake_word_detector = WakeWordDetector(wake_word="your_word_here")
```

### Change Voice
Edit [app/api/v1/realtime.py](app/api/v1/realtime.py):
```python
response_audio = await voice_service.text_to_speech(
    response.message,
    voice="alloy"  # or echo, fable, onyx, nova, shimmer
)
```

## Next Steps

- [ ] Add local wake word detection (for privacy) using PocketSphinx
- [ ] Add conversation memory to remember context
- [ ] Support multiple languages
- [ ] Add noise cancellation
- [ ] Deploy as standalone app

Enjoy your Alexa-like experience with Griot! 🎭✨
