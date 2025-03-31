# Voice Interface Documentation

The Hohenheim AGI system includes voice interaction capabilities, allowing users to interact with the system using speech-to-text (STT) and text-to-speech (TTS) functionality.

## Features

- **Speech-to-Text (STT)**: Convert spoken commands to text using OpenAI's Whisper model
- **Text-to-Speech (TTS)**: Convert system responses to speech using ElevenLabs API
- **Voice Commands**: Trigger voice input mode with simple commands
- **Voice Mode Toggle**: Enable/disable voice response mode

## Requirements

- **OpenAI Whisper**: For speech-to-text conversion
- **ElevenLabs API Key**: For high-quality text-to-speech
- **Audio Hardware**: Microphone for input, speakers for output
- **FFmpeg**: Required for audio processing

## CLI Voice Commands

The following commands are available in the CLI interface:

- `voice on`: Enable voice mode (responses will be spoken)
- `voice off`: Disable voice mode
- `voice`: Toggle voice mode on/off
- `listen`: Start listening for a voice command

## Web GUI Voice Controls

The web interface includes buttons for:

- **Voice**: Toggle voice mode on/off
- **Record**: Start/stop recording a voice command

## Configuration

Voice settings can be configured in the settings tab of the web interface or by setting the following environment variables:

```
ELEVENLABS_API_KEY=your_api_key_here
VOICE_ENABLED=true
VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Default is Adam
```

## Testing Voice Functionality

Two test scripts are provided to verify voice functionality:

1. `tests/test_voice.py`: Tests basic audio, Whisper, and ElevenLabs functionality
2. `tests/test_voice_interface.py`: Tests the VoiceInterface implementation

To run the tests:

```bash
# Test basic voice components
python tests/test_voice.py --test-all --elevenlabs-key YOUR_API_KEY

# Test voice interface implementation
python tests/test_voice_interface.py --test-all --elevenlabs-key YOUR_API_KEY
```

## Troubleshooting

### No audio input detected

- Check if your microphone is properly connected and recognized by your system
- Run `python tests/test_voice.py --test-devices` to list available audio devices
- Make sure you have the necessary permissions to access the microphone

### Text-to-speech not working

- Verify your ElevenLabs API key is correct
- Check your internet connection
- Run `python tests/test_voice.py --test-tts --elevenlabs-key YOUR_API_KEY` to test TTS functionality

### Speech recognition issues

- Ensure you have a quiet environment for better recognition
- Check if Whisper model is properly installed
- Run `python tests/test_voice.py --test-whisper` to verify Whisper functionality

### Missing dependencies

Install all required dependencies with:

```bash
pip install -r requirements.txt
```

Additionally, make sure FFmpeg is installed on your system:

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```
