"""
Native Speaker Mode - Single agent conversation
"""
import asyncio
from typing import Optional, Callable
from .base_agent import GeminiLiveAgent
from ..config import AgentConfig, SystemConfig, NYC_BARISTA_CONFIG
from ..audio import AudioManager, AudioProcessor
import numpy as np


class NativeSpeakerMode:
    """
    Native Speaker Mode: Single agent with native slang/pace
    Optimized for low-latency, interruptible dialogue
    """
    
    def __init__(self, 
                 agent_config: Optional[AgentConfig] = None,
                 system_config: Optional[SystemConfig] = None):
        self.system_config = system_config or SystemConfig.from_env()
        self.agent_config = agent_config or NYC_BARISTA_CONFIG
        
        self.agent = GeminiLiveAgent(self.agent_config, self.system_config)
        self.audio_manager = AudioManager(
            sample_rate=self.system_config.sample_rate,
            chunk_size=self.system_config.chunk_size
        )
        self.audio_processor = AudioProcessor()
        
        self.is_running = False
        self.audio_buffer = []
        self.silence_threshold = 0.02
        self.silence_duration = 1.0  # seconds
        self.last_speech_time = 0
        
    async def initialize(self):
        """Initialize the agent"""
        print(f"🎙️  Initializing {self.agent_config.name}...")
        await self.agent.initialize()
        print(f"✅ {self.agent_config.name} ready!")
        
    async def start(self):
        """Start the native speaker mode"""
        await self.initialize()
        
        self.is_running = True
        print(f"\n🎤 Native Speaker Mode Active")
        print(f"👤 Agent: {self.agent_config.name}")
        print(f"🎯 Target latency: {self.system_config.target_latency_ms}ms")
        print(f"💬 Start speaking... (Press Ctrl+C to stop)\n")
        
        # Start audio streams
        self.audio_manager.start_input_stream()
        self.audio_manager.start_output_stream()
        
        try:
            await self._conversation_loop()
        except KeyboardInterrupt:
            print("\n\n👋 Stopping...")
        finally:
            await self.stop()
    
    async def _conversation_loop(self):
        """Main conversation loop with interruption handling"""
        import time
        
        while self.is_running:
            # Get audio chunk
            audio_data = self.audio_manager.get_input_audio(timeout=0.1)
            
            if audio_data:
                # Convert to numpy for processing
                audio_np = self.audio_processor.bytes_to_numpy(audio_data)
                
                # Check for speech
                has_speech = self.audio_processor.detect_speech(audio_np, self.silence_threshold)
                
                if has_speech:
                    self.last_speech_time = time.time()
                    self.audio_buffer.append(audio_data)
                    
                    # If agent is speaking, interrupt
                    if self.agent.is_speaking:
                        self.agent.interrupt()
                        self.audio_manager.clear_queues()
                    
                elif self.audio_buffer:
                    # Check if silence duration reached
                    silence_time = time.time() - self.last_speech_time
                    
                    if silence_time >= self.silence_duration:
                        # Process accumulated audio
                        full_audio = b''.join(self.audio_buffer)
                        self.audio_buffer = []
                        
                        print(f"🎧 Processing audio ({len(full_audio)} bytes)...")
                        
                        # Get response from agent
                        response = await self.agent.process_audio_input(full_audio)
                        
                        if response and response.get("text"):
                            print(f"🤖 {self.agent_config.name}: {response['text']}")
                            
                            # Play audio response if available
                            if response.get("audio"):
                                self.agent.is_speaking = True
                                self.audio_manager.play_audio(response["audio"])
                                # Wait for audio to finish
                                await asyncio.sleep(0.1)
                                self.agent.is_speaking = False
                            
                            # Show latency stats
                            avg_latency = self.agent.get_average_latency()
                            print(f"⚡ Avg latency: {avg_latency:.0f}ms\n")
            
            await asyncio.sleep(0.01)  # Small delay to prevent CPU spinning
    
    async def stop(self):
        """Stop the native speaker mode"""
        self.is_running = False
        self.audio_manager.cleanup()
        
        # Close the agent session
        if hasattr(self.agent, 'close'):
            await self.agent.close()
        
        # Show final stats
        avg_latency = self.agent.get_average_latency()
        if avg_latency > 0:
            print(f"\n📊 Session Stats:")
            print(f"   Average Latency: {avg_latency:.0f}ms")
            print(f"   Target: {self.system_config.target_latency_ms}ms")
            print(f"   Interactions: {len(self.agent.latency_tracker)}")
        
        print(f"✅ Session ended\n")
    
    async def process_text(self, text: str) -> str:
        """Process text input (for testing without audio)"""
        response = await self.agent.process_text_input(text)
        return response.get("text", "")
