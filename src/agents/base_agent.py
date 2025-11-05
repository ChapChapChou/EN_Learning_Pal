"""
Base voice agent implementation using Gemini Live API
"""
import asyncio
import time
from typing import Optional, Callable, List, Dict, Any
from abc import ABC, abstractmethod
import google.generativeai as genai
from ..config import AgentConfig, SystemConfig


class BaseVoiceAgent(ABC):
    """Base class for voice agents using Gemini Live API"""
    
    def __init__(self, config: AgentConfig, system_config: SystemConfig):
        self.config = config
        self.system_config = system_config
        self.model = None
        self.conversation_history: List[Dict[str, str]] = []
        self.is_speaking = False
        self.is_listening = True
        self.latency_tracker = []
        
    async def initialize(self):
        """Initialize the agent with Gemini API"""
        genai.configure(api_key=self.system_config.api_key)
        
        # Configure model for live conversation
        generation_config = {
            "temperature": self.config.temperature,
            "max_output_tokens": self.config.max_tokens,
            "response_modalities": ["AUDIO", "TEXT"],
            "speech_config": {
                "voice_config": {
                    "prebuilt_voice_config": {
                        "voice_name": self.config.voice.voice_name
                    }
                }
            }
        }
        
        self.model = genai.GenerativeModel(
            model_name=self.system_config.model_name,
            generation_config=generation_config,
            system_instruction=self.config.system_prompt
        )
        
    async def process_audio_input(self, audio_data: bytes) -> Optional[Dict[str, Any]]:
        """Process audio input and generate response"""
        if not self.is_listening or self.is_speaking:
            return None
            
        start_time = time.time()
        
        try:
            # Create live session for real-time interaction
            response = await self._generate_response(audio_data)
            
            latency = (time.time() - start_time) * 1000  # Convert to ms
            self.latency_tracker.append(latency)
            
            if latency > self.system_config.target_latency_ms:
                print(f"⚠️  Latency warning: {latency:.0f}ms (target: {self.system_config.target_latency_ms}ms)")
            
            return response
            
        except Exception as e:
            print(f"❌ Error processing audio: {e}")
            return None
    
    @abstractmethod
    async def _generate_response(self, audio_data: bytes) -> Dict[str, Any]:
        """Generate response from audio input - to be implemented by subclasses"""
        pass
    
    def interrupt(self):
        """Handle interruption - stop speaking immediately"""
        self.is_speaking = False
        print(f"🛑 {self.config.name} interrupted")
    
    def get_average_latency(self) -> float:
        """Get average response latency"""
        if not self.latency_tracker:
            return 0.0
        return sum(self.latency_tracker) / len(self.latency_tracker)
    
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.latency_tracker = []


class GeminiLiveAgent(BaseVoiceAgent):
    """Gemini Live API agent implementation"""
    
    def __init__(self, config: AgentConfig, system_config: SystemConfig):
        super().__init__(config, system_config)
        self.chat_session = None
        
    async def initialize(self):
        """Initialize with chat session"""
        await super().initialize()
        self.chat_session = self.model.start_chat(history=[])
        
    async def _generate_response(self, audio_data: bytes) -> Dict[str, Any]:
        """Generate response using Gemini Live API"""
        # For Gemini Live, we send audio directly
        # Note: Using audio/pcm as MIME type for raw PCM data
        # Gemini API may also accept audio/wav or audio/x-wav
        response = await asyncio.to_thread(
            self.chat_session.send_message,
            {
                "mime_type": "audio/pcm",
                "data": audio_data
            }
        )
        
        result = {
            "text": response.text if hasattr(response, 'text') else "",
            "audio": None,
            "agent": self.config.name
        }
        
        # Extract audio if available
        if hasattr(response, 'candidates') and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data.mime_type.startswith('audio'):
                        result["audio"] = part.inline_data.data
        
        # Add to history
        if result["text"]:
            self.add_to_history("assistant", result["text"])
        
        return result
    
    async def process_text_input(self, text: str) -> Dict[str, Any]:
        """Process text input (for testing or fallback)"""
        start_time = time.time()
        
        try:
            response = await asyncio.to_thread(
                self.chat_session.send_message,
                text
            )
            
            latency = (time.time() - start_time) * 1000
            self.latency_tracker.append(latency)
            
            result = {
                "text": response.text if hasattr(response, 'text') else "",
                "audio": None,
                "agent": self.config.name
            }
            
            # Extract audio if available
            if hasattr(response, 'candidates') and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data.mime_type.startswith('audio'):
                            result["audio"] = part.inline_data.data
            
            if result["text"]:
                self.add_to_history("user", text)
                self.add_to_history("assistant", result["text"])
            
            return result
            
        except Exception as e:
            print(f"❌ Error processing text: {e}")
            return {"text": "", "audio": None, "agent": self.config.name}
