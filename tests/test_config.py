"""
Unit tests for configuration management
"""
import unittest
from src.config import (
    SystemConfig,
    AgentConfig,
    VoiceConfig,
    NYC_BARISTA_CONFIG,
    PODCAST_HOST_CONFIG,
    PODCAST_EXPERT_CONFIG
)


class TestVoiceConfig(unittest.TestCase):
    """Test VoiceConfig dataclass"""
    
    def test_voice_config_creation(self):
        """Test creating a voice configuration"""
        voice = VoiceConfig(
            voice_name="TestVoice",
            pitch=0.5,
            speed=1.2,
            language="en-US"
        )
        
        self.assertEqual(voice.voice_name, "TestVoice")
        self.assertEqual(voice.pitch, 0.5)
        self.assertEqual(voice.speed, 1.2)
        self.assertEqual(voice.language, "en-US")
    
    def test_voice_config_defaults(self):
        """Test default values for voice config"""
        voice = VoiceConfig(voice_name="TestVoice")
        
        self.assertEqual(voice.pitch, 0.0)
        self.assertEqual(voice.speed, 1.0)
        self.assertEqual(voice.language, "en-US")


class TestAgentConfig(unittest.TestCase):
    """Test AgentConfig dataclass"""
    
    def test_agent_config_creation(self):
        """Test creating an agent configuration"""
        voice = VoiceConfig(voice_name="TestVoice")
        agent = AgentConfig(
            name="Test Agent",
            persona="test",
            voice=voice,
            system_prompt="Test prompt",
            temperature=0.8,
            max_tokens=100
        )
        
        self.assertEqual(agent.name, "Test Agent")
        self.assertEqual(agent.persona, "test")
        self.assertEqual(agent.voice.voice_name, "TestVoice")
        self.assertEqual(agent.system_prompt, "Test prompt")
        self.assertEqual(agent.temperature, 0.8)
        self.assertEqual(agent.max_tokens, 100)


class TestPredefinedConfigs(unittest.TestCase):
    """Test predefined agent configurations"""
    
    def test_nyc_barista_config(self):
        """Test NYC Barista configuration"""
        self.assertEqual(NYC_BARISTA_CONFIG.name, "NYC Barista")
        self.assertEqual(NYC_BARISTA_CONFIG.persona, "native_speaker")
        self.assertEqual(NYC_BARISTA_CONFIG.voice.voice_name, "Kore")
        self.assertIn("NYC barista", NYC_BARISTA_CONFIG.system_prompt)
        self.assertGreater(NYC_BARISTA_CONFIG.temperature, 0.9)
    
    def test_podcast_host_config(self):
        """Test Podcast Host configuration"""
        self.assertEqual(PODCAST_HOST_CONFIG.name, "Podcast Host")
        self.assertEqual(PODCAST_HOST_CONFIG.persona, "podcast_host")
        self.assertEqual(PODCAST_HOST_CONFIG.voice.voice_name, "Puck")
        self.assertIn("podcast", PODCAST_HOST_CONFIG.system_prompt.lower())
    
    def test_podcast_expert_config(self):
        """Test Language Expert configuration"""
        self.assertEqual(PODCAST_EXPERT_CONFIG.name, "Language Expert")
        self.assertEqual(PODCAST_EXPERT_CONFIG.persona, "podcast_expert")
        self.assertEqual(PODCAST_EXPERT_CONFIG.voice.voice_name, "Charon")
        self.assertIn("expert", PODCAST_EXPERT_CONFIG.system_prompt.lower())


class TestSystemConfig(unittest.TestCase):
    """Test SystemConfig"""
    
    def test_system_config_defaults(self):
        """Test system config with defaults"""
        config = SystemConfig(api_key="test_key")
        
        self.assertEqual(config.api_key, "test_key")
        self.assertEqual(config.model_name, "gemini-2.0-flash-exp")
        self.assertEqual(config.target_latency_ms, 500)
        self.assertEqual(config.sample_rate, 16000)
        self.assertEqual(config.chunk_size, 1024)


if __name__ == "__main__":
    unittest.main()
