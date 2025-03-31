"""
Voice Interface - Speech-to-Text and Text-to-Speech for Hohenheim AGI
Provides voice interaction capabilities for the CLI interface
"""

import os
import time
import logging
import numpy as np
import queue
import sounddevice as sd
import soundfile as sf
from typing import Optional, Dict, Any, List
from elevenlabs import text_to_speech, play, stream
from elevenlabs.client import ElevenLabs

class VoiceInterface:
    """Voice interface for Hohenheim AGI"""
    
    def __init__(self, agi_core: Any, config: Dict[str, Any] = None):
        self.agi_core = agi_core
        self.logger = logging.getLogger("Hohenheim.VoiceInterface")
        self.config = config or {}
        
        # Voice settings
        self.voice_enabled = False
        self.recording = False
        self.audio_queue = queue.Queue()
        self.audio_data = []
        self.stream = None
        
        # Initialize Whisper model
        try:
            import whisper
            self.whisper_model = whisper.load_model("base")
            self.logger.info("Whisper model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {str(e)}")
            self.whisper_model = None
        
        # Initialize ElevenLabs API if key is available
        elevenlabs_key = self.config.get("ELEVENLABS_API_KEY", "")
        if elevenlabs_key:
            self.eleven_labs = ElevenLabs(api_key=elevenlabs_key)
            self.logger.info("ElevenLabs API initialized")
        else:
            self.logger.warning("ElevenLabs API key not found")
        
        self.voice_settings = {
            "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Default voice ID (Adam)
            "model": "eleven_monolingual_v1"
        }
    
    def start_recording(self):
        """Start recording audio from microphone"""
        if self.recording:
            return
        
        self.recording = True
        self.audio_data = []
        
        def audio_callback(indata, frames, time, status):
            if status:
                self.logger.warning(f"Audio recording status: {status}")
            self.audio_queue.put(indata.copy())
        
        try:
            self.stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=16000)
            self.stream.start()
            self.logger.info("Started audio recording")
            print("Recording... (Press Ctrl+C to stop)")
        except Exception as e:
            self.logger.error(f"Failed to start recording: {str(e)}")
            self.recording = False
            print(f"Error starting recording: {str(e)}")
    
    def stop_recording(self) -> str:
        """Stop recording and transcribe audio"""
        if not self.recording:
            return ""
        
        self.recording = False
        
        try:
            self.stream.stop()
            self.stream.close()
            
            # Get all audio data from queue
            audio_data = []
            while not self.audio_queue.empty():
                audio_data.append(self.audio_queue.get())
            
            if not audio_data:
                self.logger.warning("No audio data captured")
                return ""
            
            # Convert to numpy array and save as WAV
            audio_array = np.concatenate(audio_data, axis=0)
            temp_wav = "temp_recording.wav"
            sf.write(temp_wav, audio_array, 16000)
            
            print("Transcribing audio...")
            
            # Transcribe with Whisper
            if self.whisper_model:
                result = self.whisper_model.transcribe(temp_wav)
                os.remove(temp_wav)
                transcribed_text = result["text"].strip()
                self.logger.info(f"Transcribed: {transcribed_text}")
                return transcribed_text
            else:
                self.logger.error("Whisper model not available")
                return ""
                
        except Exception as e:
            self.logger.error(f"Transcription error: {str(e)}")
            return ""
    
    def text_to_speech(self, text: str) -> None:
        """Convert text to speech using ElevenLabs"""
        if not text.strip():
            return
            
        try:
            # Check if API key is available
            api_key = self.config.get("ELEVENLABS_API_KEY", "")
            if not api_key:
                self.logger.warning("ElevenLabs API key not found")
                return
            
            # Limit text length if needed
            if len(text) > 1000:
                self.logger.info("Text too long, truncating for TTS")
                text = text[:1000] + "..."
                
            print("Converting text to speech...")
                
            # Generate audio using ElevenLabs
            audio = text_to_speech(
                text=text,
                voice_id=self.voice_settings["voice_id"],
                model_id=self.voice_settings["model"]
            )
            
            # Play audio directly
            play(audio)
            
        except Exception as e:
            self.logger.error(f"Text-to-speech error: {str(e)}")
    
    def toggle_voice(self) -> bool:
        """Toggle voice mode on/off"""
        self.voice_enabled = not self.voice_enabled
        status = "enabled" if self.voice_enabled else "disabled"
        print(f"Voice mode {status}")
        return self.voice_enabled
    
    def process_voice_command(self) -> Optional[str]:
        """Record and process a voice command"""
        try:
            self.start_recording()
            
            # Wait for user to stop recording (Ctrl+C)
            try:
                while self.recording:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\nStopping recording...")
                transcribed_text = self.stop_recording()
                
                if transcribed_text:
                    print(f"You said: {transcribed_text}")
                    return transcribed_text
                else:
                    print("No speech detected or transcription failed")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error processing voice command: {str(e)}")
            print(f"Error: {str(e)}")
            return None
    
    def speak_response(self, response: Dict[str, Any]) -> None:
        """Speak the response using TTS"""
        if not self.voice_enabled:
            return
            
        # Extract just the main response without metadata
        text = response.get('message', '')
        if text:
            self.text_to_speech(text)
