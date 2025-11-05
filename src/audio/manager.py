"""
Audio input/output handling for voice agents
"""
import asyncio
import pyaudio
import numpy as np
from typing import Optional, Callable
import queue
import threading


class AudioManager:
    """Manages audio input/output streams"""
    
    # Audio format constants
    AUDIO_FORMAT = pyaudio.paInt16  # 16-bit audio
    BYTES_PER_SAMPLE = 2  # 16-bit = 2 bytes per sample
    
    def __init__(self, sample_rate: int = 16000, chunk_size: int = 1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio = pyaudio.PyAudio()
        self.input_stream: Optional[pyaudio.Stream] = None
        self.output_stream: Optional[pyaudio.Stream] = None
        self.is_recording = False
        self.is_playing = False
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        
    def start_input_stream(self, callback: Optional[Callable] = None):
        """Start capturing audio input"""
        if self.input_stream is not None:
            return
            
        def audio_callback(in_data, frame_count, time_info, status):
            if self.is_recording:
                self.input_queue.put(in_data)
                if callback:
                    callback(in_data)
            return (None, pyaudio.paContinue)
        
        self.input_stream = self.audio.open(
            format=self.AUDIO_FORMAT,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=audio_callback
        )
        self.is_recording = True
        self.input_stream.start_stream()
        
    def stop_input_stream(self):
        """Stop capturing audio input"""
        self.is_recording = False
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            self.input_stream = None
            
    def start_output_stream(self):
        """Start audio output stream"""
        if self.output_stream is not None:
            return
            
        def audio_callback(in_data, frame_count, time_info, status):
            if not self.output_queue.empty():
                data = self.output_queue.get()
                return (data, pyaudio.paContinue)
            else:
                # Return silence: frame_count frames * BYTES_PER_SAMPLE
                return (b'\x00' * frame_count * self.BYTES_PER_SAMPLE, pyaudio.paContinue)
        
        self.output_stream = self.audio.open(
            format=self.AUDIO_FORMAT,
            channels=1,
            rate=self.sample_rate,
            output=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=audio_callback
        )
        self.is_playing = True
        self.output_stream.start_stream()
        
    def stop_output_stream(self):
        """Stop audio output stream"""
        self.is_playing = False
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            self.output_stream = None
            
    def play_audio(self, audio_data: bytes):
        """Queue audio data for playback"""
        self.output_queue.put(audio_data)
        
    def get_input_audio(self, timeout: float = 0.1) -> Optional[bytes]:
        """Get captured audio data"""
        try:
            return self.input_queue.get(timeout=timeout)
        except queue.Empty:
            return None
            
    def clear_queues(self):
        """Clear all audio queues"""
        while not self.input_queue.empty():
            self.input_queue.get()
        while not self.output_queue.empty():
            self.output_queue.get()
            
    def cleanup(self):
        """Clean up audio resources"""
        self.stop_input_stream()
        self.stop_output_stream()
        self.audio.terminate()


class AudioProcessor:
    """Process audio data for optimal latency"""
    
    @staticmethod
    def apply_noise_gate(audio_data: np.ndarray, threshold: float = 0.01) -> np.ndarray:
        """Apply noise gate to reduce background noise"""
        mask = np.abs(audio_data) > threshold
        return audio_data * mask
    
    @staticmethod
    def normalize_audio(audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio levels"""
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val
        return audio_data
    
    @staticmethod
    def detect_speech(audio_data: np.ndarray, threshold: float = 0.02) -> bool:
        """Simple speech detection based on energy"""
        energy = np.mean(np.abs(audio_data))
        return energy > threshold
    
    @staticmethod
    def bytes_to_numpy(audio_bytes: bytes) -> np.ndarray:
        """Convert audio bytes to numpy array"""
        return np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    
    @staticmethod
    def numpy_to_bytes(audio_array: np.ndarray) -> bytes:
        """Convert numpy array to audio bytes"""
        return (audio_array * 32768.0).astype(np.int16).tobytes()
