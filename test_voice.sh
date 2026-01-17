#!/bin/bash
# Test script for Griot voice features

echo "🎤 Testing Voice Text-to-Speech Endpoint"
echo "Asking Griot to tell a story and getting audio response..."

curl -X POST "http://localhost:8000/api/v1/voice/text?text=Once%20upon%20a%20time%20in%20the%20great%20Mali%20Empire&voice=nova" \
  -o griot_response.mp3

if [ -f griot_response.mp3 ]; then
    echo "✅ Audio file saved as griot_response.mp3"
    echo "   Play it with: open griot_response.mp3 (Mac) or mpg123 griot_response.mp3 (Linux)"
else
    echo "❌ Failed to generate audio"
fi

echo -e "\n🎤 Testing Full Voice Interaction (speech-to-text + generation + text-to-speech)"
echo "   To test, you need an audio file. Example:"
echo "   curl -X POST http://localhost:8000/api/v1/voice -F 'audio=@your_audio_file.wav' -o griot_answer.mp3"
