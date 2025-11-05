"""
Base voice agent implementation using Google ADK (google-genai)
"""
import asyncio
import time
from typing import Optional, Callable, List, Dict, Any
from abc import ABC, abstractmethod
from google import genai
from ..config import AgentConfig, SystemConfig


class BaseVoiceAgent(ABC):
    """Base class for voice agents using Google ADK"""
    
    def __init__(self, config: AgentConfig, system_config: SystemConfig):
        self.config = config
        self.system_config = system_config
        self.client = None
        self.model_id = None
        self.conversation_history: List[Dict[str, str]] = []
        self.is_speaking = False
        self.is_listening = True
        self.latency_tracker = []
        
    async def initialize(self):
        """Initialize the agent with Google ADK"""
        # Initialize Google ADK client
        self.client = genai.Client(api_key=self.system_config.api_key)
        self.model_id = self.system_config.model_name
        
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
    """Google ADK Live API agent implementation"""
    
    def __init__(self, config: AgentConfig, system_config: SystemConfig):
        super().__init__(config, system_config)
        self.session = None
        
    async def initialize(self):
        """Initialize with live session"""
        await super().initialize()
        
        # Create live session configuration
        config = {
            "generation_config": {
                "temperature": self.config.temperature,
                "max_output_tokens": self.config.max_tokens,
                "response_modalities": ["AUDIO", "TEXT"],
            },
            "speech_config": {
                "voice_config": {
                    "prebuilt_voice_config": {
                        "voice_name": self.config.voice.voice_name
                    }
                }
            },
            "system_instruction": self.config.system_prompt
        }
        
        # Initialize live session using Google ADK
        self.session = self.client.aio.live.connect(
            model=self.model_id,
            config=config
        )
        
    async def _generate_response(self, audio_data: bytes) -> Dict[str, Any]:
        """Generate response using Google ADK Live API"""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        result = {
            "text": "",
            "audio": None,
            "agent": self.config.name
        }
        
        try:
            # Send audio to live session
            await self.session.send(audio_data, mime_type="audio/pcm")
            
            # Receive response from live session
            async for response in self.session.receive():
                # Extract text if available
                if hasattr(response, 'text') and response.text:
                    result["text"] += response.text
                
                # Extract audio if available
                if hasattr(response, 'data') and response.data:
                    if result["audio"] is None:
                        result["audio"] = response.data
                    else:
                        result["audio"] += response.data
                
                # Break after first complete response
                if hasattr(response, 'server_content') and response.server_content:
                    break
            
            # Add to history
            if result["text"]:
                self.add_to_history("assistant", result["text"])
        
        except Exception as e:
            print(f"❌ Error in live session: {e}")
            result["text"] = ""
        
        return result
    
    async def process_text_input(self, text: str) -> Dict[str, Any]:
        """Process text input using Google ADK"""
        start_time = time.time()
        
        try:
            # Use standard generate_content for text-only interaction
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_id,
                contents=text,
                config={
                    "temperature": self.config.temperature,
                    "max_output_tokens": self.config.max_tokens,
                    "system_instruction": self.config.system_prompt
                }
            )
            
            latency = (time.time() - start_time) * 1000
            self.latency_tracker.append(latency)
            
            result = {
                "text": response.text if hasattr(response, 'text') else "",
                "audio": None,
                "agent": self.config.name
            }
            
            if result["text"]:
                self.add_to_history("user", text)
                self.add_to_history("assistant", result["text"])
            
            return result
            
        except Exception as e:
            print(f"❌ Error processing text: {e}")
            return {"text": "", "audio": None, "agent": self.config.name}
    
    async def close(self):
        """Close the live session"""
        if self.session:
            try:
                await self.session.close()
            except Exception as e:
                print(f"⚠️  Error closing session: {e}")
            self.session = None
