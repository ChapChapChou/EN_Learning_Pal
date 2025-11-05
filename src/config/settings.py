"""
Configuration management for voice agent system
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class VoiceConfig:
    """Voice configuration for agents"""
    voice_name: str
    pitch: float = 0.0
    speed: float = 1.0
    language: str = "en-US"


@dataclass
class AgentConfig:
    """Configuration for a single agent"""
    name: str
    persona: str
    voice: VoiceConfig
    system_prompt: str
    temperature: float = 0.9
    max_tokens: int = 1024


@dataclass
class SystemConfig:
    """System-wide configuration"""
    api_key: str
    model_name: str = "gemini-2.0-flash-exp"
    target_latency_ms: int = 500
    sample_rate: int = 16000
    chunk_size: int = 1024
    
    @classmethod
    def from_env(cls) -> "SystemConfig":
        """Load configuration from environment variables"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        return cls(
            api_key=api_key,
            model_name=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
            target_latency_ms=int(os.getenv("TARGET_LATENCY_MS", "500")),
            sample_rate=int(os.getenv("SAMPLE_RATE", "16000")),
            chunk_size=int(os.getenv("CHUNK_SIZE", "1024"))
        )


# Predefined agent configurations
NYC_BARISTA_CONFIG = AgentConfig(
    name="NYC Barista",
    persona="native_speaker",
    voice=VoiceConfig(
        voice_name="Kore",
        pitch=0.0,
        speed=1.1,
        language="en-US"
    ),
    system_prompt="""You are a NYC barista named Alex working at a busy coffee shop in Manhattan. 
You speak with authentic New York slang, fast-paced, friendly, and slightly sarcastic. 
Use contractions, casual language, and phrases like "yo", "what's good", "no worries", "lemme", etc.
Keep responses short and natural - like you're juggling multiple orders.
Be helpful but maintain that authentic NYC energy and pace.
You're interruptible - if someone cuts you off mid-sentence, just roll with it.""",
    temperature=0.95,
    max_tokens=150
)

PODCAST_HOST_CONFIG = AgentConfig(
    name="Podcast Host",
    persona="podcast_host",
    voice=VoiceConfig(
        voice_name="Puck",
        pitch=0.0,
        speed=1.0,
        language="en-US"
    ),
    system_prompt="""You are the host of an engaging educational podcast about language learning.
You're enthusiastic, curious, and great at asking follow-up questions.
Keep your segments conversational and engaging - aim for 2-3 sentences at a time.
Your role is to guide the conversation, ask interesting questions, and make the expert's 
knowledge accessible to listeners. Use phrases like "That's fascinating!", "Tell us more about...", 
"So what you're saying is...". Be warm and professional.""",
    temperature=0.85,
    max_tokens=200
)

PODCAST_EXPERT_CONFIG = AgentConfig(
    name="Language Expert",
    persona="podcast_expert",
    voice=VoiceConfig(
        voice_name="Charon",
        pitch=0.0,
        speed=0.95,
        language="en-US"
    ),
    system_prompt="""You are a linguistics expert and language learning specialist on a podcast.
You're knowledgeable but approachable, sharing insights about language acquisition and culture.
Provide interesting facts, research-backed tips, and practical advice.
Keep explanations clear and concise - 2-4 sentences per turn.
Be conversational, not lecturing. Use examples and anecdotes to illustrate points.
When the host asks questions, give thoughtful, engaging answers.""",
    temperature=0.8,
    max_tokens=250
)
