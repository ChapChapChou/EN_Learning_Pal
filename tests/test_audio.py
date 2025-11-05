"""
Unit tests for audio manager
"""
import unittest
import numpy as np

try:
    from src.audio import AudioProcessor
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False


@unittest.skipIf(not AUDIO_AVAILABLE, "Audio dependencies not available")
class TestAudioProcessor(unittest.TestCase):
    """Test AudioProcessor utility functions"""
    
    def test_normalize_audio(self):
        """Test audio normalization"""
        # Create test audio data
        audio = np.array([0.1, 0.5, -0.3, 0.8], dtype=np.float32)
        
        normalized = AudioProcessor.normalize_audio(audio)
        
        # Check that max absolute value is 1.0
        self.assertAlmostEqual(np.max(np.abs(normalized)), 1.0, places=5)
    
    def test_normalize_zero_audio(self):
        """Test normalization of silent audio"""
        audio = np.zeros(100, dtype=np.float32)
        
        normalized = AudioProcessor.normalize_audio(audio)
        
        # Should return zeros unchanged
        np.testing.assert_array_equal(normalized, audio)
    
    def test_detect_speech(self):
        """Test speech detection"""
        # Loud audio (speech)
        loud_audio = np.random.randn(1000).astype(np.float32) * 0.5
        self.assertTrue(AudioProcessor.detect_speech(loud_audio, threshold=0.02))
        
        # Quiet audio (no speech)
        quiet_audio = np.random.randn(1000).astype(np.float32) * 0.001
        self.assertFalse(AudioProcessor.detect_speech(quiet_audio, threshold=0.02))
    
    def test_apply_noise_gate(self):
        """Test noise gate application"""
        # Create audio with both loud and quiet samples
        audio = np.array([0.5, 0.001, -0.4, 0.0001, 0.3], dtype=np.float32)
        threshold = 0.01
        
        filtered = AudioProcessor.apply_noise_gate(audio, threshold)
        
        # Loud samples should remain
        self.assertAlmostEqual(filtered[0], 0.5, places=5)
        self.assertAlmostEqual(filtered[2], -0.4, places=5)
        
        # Quiet samples should be zeroed
        self.assertAlmostEqual(filtered[1], 0.0, places=5)
        self.assertAlmostEqual(filtered[3], 0.0, places=5)
    
    def test_bytes_to_numpy(self):
        """Test conversion from bytes to numpy"""
        # Create test bytes (16-bit PCM)
        audio_bytes = np.array([100, 200, -100, -200], dtype=np.int16).tobytes()
        
        audio_np = AudioProcessor.bytes_to_numpy(audio_bytes)
        
        # Check shape and type
        self.assertEqual(audio_np.shape[0], 4)
        self.assertEqual(audio_np.dtype, np.float32)
        
        # Check values are normalized
        self.assertLessEqual(np.max(np.abs(audio_np)), 1.0)
    
    def test_numpy_to_bytes(self):
        """Test conversion from numpy to bytes"""
        # Create test numpy array
        audio_np = np.array([0.5, -0.5, 0.25, -0.25], dtype=np.float32)
        
        audio_bytes = AudioProcessor.numpy_to_bytes(audio_np)
        
        # Convert back and check
        recovered = AudioProcessor.bytes_to_numpy(audio_bytes)
        
        # Should be approximately equal (allowing for conversion precision)
        np.testing.assert_array_almost_equal(audio_np, recovered, decimal=4)
    
    def test_roundtrip_conversion(self):
        """Test bytes -> numpy -> bytes roundtrip"""
        # Original bytes
        original = np.random.randint(-30000, 30000, size=100, dtype=np.int16).tobytes()
        
        # Convert to numpy and back
        as_numpy = AudioProcessor.bytes_to_numpy(original)
        back_to_bytes = AudioProcessor.numpy_to_bytes(as_numpy)
        
        # Should be very close (allowing for float precision)
        original_np = np.frombuffer(original, dtype=np.int16)
        recovered_np = np.frombuffer(back_to_bytes, dtype=np.int16)
        
        # Check correlation is very high
        correlation = np.corrcoef(original_np.astype(float), recovered_np.astype(float))[0, 1]
        self.assertGreater(correlation, 0.99)


if __name__ == "__main__":
    unittest.main()
