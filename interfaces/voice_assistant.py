import os
import sounddevice as sd
import numpy as np
from elevenlabs import generate, play
from whispercpp import Whisper
from dotenv import load_dotenv
from typing import Optional
from ..core.logger import get_logger

logger = get_logger(__name__)

class VoiceAssistant:
    def __init__(self):
        load_dotenv()
        self.enabled = os.getenv('ENABLE_VOICE', 'false').lower() == 'true'
        self.whisper = None
        self.sample_rate = 16000
        self.initialize_components()

    def initialize_components(self):
        if not self.enabled:
            return
            
        try:
            # Initialize Whisper
            model = os.getenv('WHISPER_MODEL', 'base.en')
            self.whisper = Whisper(model)
            
            # Verify ElevenLabs config
            if not os.getenv('ELEVENLABS_API_KEY'):
                logger.warning("ElevenLabs API key not configured")
                self.enabled = False
                
        except Exception as e:
            logger.error(f"Voice initialization failed: {str(e)}")
            self.enabled = False

    def listen(self) -> Optional[str]:
        """Record and transcribe audio input"""
        if not self.enabled:
            return None
            
        try:
            logger.info("Listening...")
            recording = sd.rec(int(2 * self.sample_rate), samplerate=self.sample_rate, channels=1)
            sd.wait()
            audio = np.squeeze(recording)
            text = self.whisper.transcribe(audio)
            return text if text else None
        except Exception as e:
            logger.error(f"Listening failed: {str(e)}")
            return None

    def speak(self, text: str):
        """Convert text to speech and play it"""
        if not self.enabled or not text:
            return
            
        try:
            audio = generate(
                text=text,
                voice=os.getenv('ELEVENLABS_VOICE_ID'),
                api_key=os.getenv('ELEVENLABS_API_KEY')
            )
            play(audio)
        except Exception as e:
            logger.error(f"Speech synthesis failed: {str(e)}")

    def run_cycle(self):
        """Main interaction cycle"""
        if not self.enabled:
            return
            
        while True:
            text = self.listen()
            if text:
                # Process text through AGI core
                response = "Response from AGI"  # Replace with actual AGI call
                self.speak(response)