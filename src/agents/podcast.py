"""
Podcast Mode - Two agents in conversation
"""
import asyncio
from typing import Optional, List, Dict, Any
from .base_agent import GeminiLiveAgent
from ..config import (
    AgentConfig, 
    SystemConfig, 
    PODCAST_HOST_CONFIG, 
    PODCAST_EXPERT_CONFIG
)
from ..audio import AudioManager, AudioProcessor


class PodcastMode:
    """
    Podcast Mode: Two agents (Host & Expert) with orchestrated conversation
    Distinct voices and roles for engaging dialogue
    """
    
    def __init__(self,
                 host_config: Optional[AgentConfig] = None,
                 expert_config: Optional[AgentConfig] = None,
                 system_config: Optional[SystemConfig] = None):
        self.system_config = system_config or SystemConfig.from_env()
        self.host_config = host_config or PODCAST_HOST_CONFIG
        self.expert_config = expert_config or PODCAST_EXPERT_CONFIG
        
        self.host = GeminiLiveAgent(self.host_config, self.system_config)
        self.expert = GeminiLiveAgent(self.expert_config, self.system_config)
        
        self.audio_manager = AudioManager(
            sample_rate=self.system_config.sample_rate,
            chunk_size=self.system_config.chunk_size
        )
        
        self.is_running = False
        self.conversation_log: List[Dict[str, Any]] = []
        
    async def initialize(self):
        """Initialize both agents"""
        print(f"🎙️  Initializing Podcast Mode...")
        print(f"   Host: {self.host_config.name}")
        print(f"   Expert: {self.expert_config.name}")
        
        await asyncio.gather(
            self.host.initialize(),
            self.expert.initialize()
        )
        
        print(f"✅ Podcast agents ready!\n")
    
    async def start_podcast(self, topic: str, duration_minutes: int = 5):
        """
        Start a podcast conversation on a given topic
        
        Args:
            topic: The topic for the podcast episode
            duration_minutes: Approximate duration in minutes
        """
        await self.initialize()
        
        self.is_running = True
        print(f"🎧 PODCAST MODE - LIVE RECORDING")
        print(f"📝 Topic: {topic}")
        print(f"⏱️  Duration: ~{duration_minutes} minutes")
        print(f"🎯 Target latency: {self.system_config.target_latency_ms}ms")
        print(f"\n{'='*60}\n")
        
        # Start audio output
        self.audio_manager.start_output_stream()
        
        try:
            # Generate the podcast conversation
            turn_count = duration_minutes * 4  # ~4 turns per minute
            await self._orchestrate_conversation(topic, turn_count)
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Recording interrupted...")
        finally:
            await self.stop()
    
    async def _orchestrate_conversation(self, topic: str, max_turns: int):
        """
        Orchestrate the conversation between host and expert
        
        Args:
            topic: The topic to discuss
            max_turns: Maximum number of turns
        """
        # Opening from host
        opening_prompt = f"""You're starting a podcast episode about '{topic}'. 
Give a brief, enthusiastic introduction (2-3 sentences) and introduce your expert guest."""
        
        print(f"🎤 {self.host_config.name}: ", end="", flush=True)
        host_response = await self.host.process_text_input(opening_prompt)
        print(host_response.get("text", ""))
        
        if host_response.get("audio"):
            self._play_audio_sync(host_response["audio"])
        
        self._log_turn("host", host_response.get("text", ""))
        
        print()  # Blank line
        
        # Main conversation loop
        current_speaker = "expert"  # Expert responds first
        
        for turn in range(max_turns - 1):
            if not self.is_running:
                break
            
            if current_speaker == "expert":
                # Expert responds to host
                context = self._get_conversation_context()
                prompt = f"Based on the host's question/comment: '{context}', respond naturally."
                
                print(f"👨‍🏫 {self.expert_config.name}: ", end="", flush=True)
                response = await self.expert.process_text_input(prompt)
                print(response.get("text", ""))
                
                if response.get("audio"):
                    self._play_audio_sync(response["audio"])
                
                self._log_turn("expert", response.get("text", ""))
                current_speaker = "host"
                
            else:
                # Host follows up or transitions
                context = self._get_conversation_context()
                
                if turn < max_turns - 3:
                    prompt = f"Based on the expert's response: '{context}', ask a follow-up question or make an interesting observation."
                else:
                    prompt = f"Start wrapping up the conversation. Thank the expert and provide a brief closing thought."
                
                print(f"🎤 {self.host_config.name}: ", end="", flush=True)
                response = await self.host.process_text_input(prompt)
                print(response.get("text", ""))
                
                if response.get("audio"):
                    self._play_audio_sync(response["audio"])
                
                self._log_turn("host", response.get("text", ""))
                current_speaker = "expert"
            
            print()  # Blank line between turns
            
            # Small delay for pacing
            await asyncio.sleep(0.5)
        
        # Closing from expert
        if self.is_running:
            closing_prompt = "Give a brief final thought and thank the host (1-2 sentences)."
            print(f"👨‍🏫 {self.expert_config.name}: ", end="", flush=True)
            expert_closing = await self.expert.process_text_input(closing_prompt)
            print(expert_closing.get("text", ""))
            
            if expert_closing.get("audio"):
                self._play_audio_sync(expert_closing["audio"])
            
            self._log_turn("expert", expert_closing.get("text", ""))
    
    def _get_conversation_context(self, last_n: int = 2) -> str:
        """Get recent conversation context"""
        if not self.conversation_log:
            return ""
        
        recent = self.conversation_log[-last_n:]
        return " ".join([turn["text"] for turn in recent if turn["text"]])
    
    def _log_turn(self, speaker: str, text: str):
        """Log a conversation turn"""
        self.conversation_log.append({
            "speaker": speaker,
            "text": text,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    def _play_audio_sync(self, audio_data: bytes):
        """Play audio synchronously"""
        self.audio_manager.play_audio(audio_data)
        # Calculate playback duration based on audio format (16-bit = 2 bytes per sample)
        bytes_per_sample = 2  # 16-bit audio = 2 bytes
        duration_seconds = len(audio_data) / (self.system_config.sample_rate * bytes_per_sample)
        # Use asyncio.sleep to avoid blocking the event loop
        import asyncio
        asyncio.create_task(asyncio.sleep(duration_seconds))
    
    async def stop(self):
        """Stop the podcast mode"""
        self.is_running = False
        self.audio_manager.cleanup()
        
        # Show final stats
        print(f"\n{'='*60}")
        print(f"\n📊 PODCAST SESSION STATS:")
        print(f"   Total turns: {len(self.conversation_log)}")
        
        host_latency = self.host.get_average_latency()
        expert_latency = self.expert.get_average_latency()
        
        if host_latency > 0:
            print(f"   {self.host_config.name} avg latency: {host_latency:.0f}ms")
        if expert_latency > 0:
            print(f"   {self.expert_config.name} avg latency: {expert_latency:.0f}ms")
        
        overall_avg = (host_latency + expert_latency) / 2 if (host_latency > 0 and expert_latency > 0) else 0
        if overall_avg > 0:
            print(f"   Overall avg latency: {overall_avg:.0f}ms")
            print(f"   Target: {self.system_config.target_latency_ms}ms")
        
        print(f"\n✅ Podcast recording complete!\n")
    
    def get_transcript(self) -> List[Dict[str, str]]:
        """Get the full conversation transcript"""
        return self.conversation_log
    
    def save_transcript(self, filepath: str):
        """Save transcript to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"PODCAST TRANSCRIPT\n")
            f.write(f"{'='*60}\n\n")
            
            for turn in self.conversation_log:
                speaker_name = self.host_config.name if turn["speaker"] == "host" else self.expert_config.name
                f.write(f"{speaker_name}:\n{turn['text']}\n\n")
        
        print(f"💾 Transcript saved to: {filepath}")
