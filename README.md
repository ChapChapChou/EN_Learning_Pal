# EN Learning Pal 🎤

Real-time voice agent system for English learning using Google ADK & Gemini Live API.

## Features

### 🗣️ Native Speaker Mode
- **Single Agent**: NYC Barista persona with authentic slang and fast-paced dialogue
- **Low-latency**: Optimized for sub-500ms response times
- **Interruptible**: Natural conversation flow with interruption handling
- **Real-time Audio**: Live voice interaction with immediate feedback

### 🎧 Podcast Mode
- **Two Agents**: Host & Expert with distinct voices and roles
- **Orchestrated Dialogue**: Natural back-and-forth conversation
- **Configurable Topics**: Generate podcasts on any language learning topic
- **Transcript Export**: Save conversation transcripts for review

## Technology Stack

- **Google ADK (google-genai)**: Official Google AI Python SDK with LiveSession API for real-time interactions
- **Gemini Live API**: Real-time multimodal AI with audio support
- **PyAudio**: Real-time audio input/output
- **Async/Await**: Non-blocking I/O for optimal performance

## Installation

### Prerequisites
- Python 3.8+
- Google Gemini API key
- Microphone and speakers (for live audio mode)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/ChapChapChou/EN_Learning_Pal.git
cd EN_Learning_Pal
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API key**
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

## Usage

### Quick Start

**Native Speaker Mode (NYC Barista):**
```bash
python main.py native
```

**Podcast Mode:**
```bash
python main.py podcast --topic "English Pronunciation Tips" --duration 5
```

### Examples

Run example scripts from the `examples/` directory:

```bash
# Native speaker conversation demo
python examples/native_speaker_demo.py

# Podcast conversation demo
python examples/podcast_demo.py

# Text-based testing (no audio required)
python examples/test_text_mode.py
```

## Configuration

### Environment Variables

Create a `.env` file with the following:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
TARGET_LATENCY_MS=500
SAMPLE_RATE=16000
CHUNK_SIZE=1024
```

### Agent Personas

#### NYC Barista (Native Speaker)
- **Voice**: Kore (energetic, conversational)
- **Style**: Fast-paced NYC slang, casual language
- **Use Case**: Practicing everyday conversational English

#### Podcast Host
- **Voice**: Puck (engaging, clear)
- **Style**: Professional but warm, asks great questions
- **Use Case**: Structured learning conversations

#### Language Expert
- **Voice**: Charon (authoritative, friendly)
- **Style**: Educational, clear explanations
- **Use Case**: In-depth language learning insights

## Project Structure

```
EN_Learning_Pal/
├── src/
│   ├── agents/
│   │   ├── base_agent.py       # Base agent implementation
│   │   ├── native_speaker.py   # Native Speaker Mode
│   │   └── podcast.py          # Podcast Mode
│   ├── audio/
│   │   └── manager.py          # Audio I/O handling
│   └── config/
│       └── settings.py         # Configuration management
├── examples/
│   ├── native_speaker_demo.py  # Native speaker example
│   ├── podcast_demo.py         # Podcast example
│   └── test_text_mode.py       # Text-based testing
├── main.py                     # Main entry point
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Performance

### Latency Optimization

The system is optimized for sub-500ms latency:

- **Streaming Audio**: Real-time audio processing with minimal buffering
- **Async Processing**: Non-blocking I/O for concurrent operations
- **Voice Activity Detection**: Smart silence detection to minimize delays
- **Interruption Handling**: Immediate response to user input

### Latency Tracking

The system automatically tracks and reports latency:
```
⚡ Avg latency: 347ms
Target: 500ms
```

## Development

### Adding Custom Agents

Create custom agent configurations in `src/config/settings.py`:

```python
CUSTOM_AGENT_CONFIG = AgentConfig(
    name="Custom Agent",
    persona="custom_persona",
    voice=VoiceConfig(
        voice_name="VoiceName",
        pitch=0.0,
        speed=1.0,
        language="en-US"
    ),
    system_prompt="Your custom system prompt...",
    temperature=0.9,
    max_tokens=200
)
```

### Testing

Run text-based tests without audio hardware:
```bash
python examples/test_text_mode.py
```

## Troubleshooting

### Common Issues

**"GEMINI_API_KEY not found"**
- Ensure `.env` file exists with your API key
- Check that python-dotenv is installed

**Audio device errors**
- Verify microphone/speaker permissions
- Check PyAudio installation: `python -c "import pyaudio"`
- On Linux: Install PortAudio: `sudo apt-get install portaudio19-dev`

**High latency**
- Check internet connection
- Reduce `chunk_size` in configuration
- Verify Gemini API quota/limits

## API Reference

### NativeSpeakerMode

```python
from src.agents import NativeSpeakerMode

mode = NativeSpeakerMode()
await mode.initialize()
await mode.start()  # Start live audio conversation
```

### PodcastMode

```python
from src.agents import PodcastMode

mode = PodcastMode()
await mode.start_podcast("Topic Name", duration_minutes=5)
mode.save_transcript("transcript.txt")
```

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

See [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google Gemini API for advanced multimodal AI capabilities
- PyAudio for real-time audio processing
- The open-source community for inspiration and tools

## Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for English learners worldwide**