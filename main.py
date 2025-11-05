"""
Main entry point for EN Learning Pal voice agent system
"""
import asyncio
import argparse
import sys
from src.agents import NativeSpeakerMode, PodcastMode
from src.config import SystemConfig


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="EN Learning Pal - Voice Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Native Speaker Mode (NYC Barista)
  python main.py native
  
  # Podcast Mode 
  python main.py podcast --topic "Language Learning Tips" --duration 5
        """
    )
    
    parser.add_argument(
        "mode",
        choices=["native", "podcast"],
        help="Agent mode: 'native' for single-agent conversation, 'podcast' for two-agent dialogue"
    )
    
    parser.add_argument(
        "--topic",
        type=str,
        help="Topic for podcast mode (required for podcast mode)"
    )
    
    parser.add_argument(
        "--duration",
        type=int,
        default=5,
        help="Duration in minutes for podcast mode (default: 5)"
    )
    
    args = parser.parse_args()
    
    # Validate API key
    try:
        system_config = SystemConfig.from_env()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("💡 Please set GEMINI_API_KEY in your .env file")
        sys.exit(1)
    
    # Run the selected mode
    try:
        if args.mode == "native":
            asyncio.run(run_native_mode())
        elif args.mode == "podcast":
            if not args.topic:
                print("❌ Error: --topic is required for podcast mode")
                sys.exit(1)
            asyncio.run(run_podcast_mode(args.topic, args.duration))
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def run_native_mode():
    """Run Native Speaker Mode"""
    print("\n" + "="*60)
    print("🎤 NATIVE SPEAKER MODE")
    print("="*60 + "\n")
    
    mode = NativeSpeakerMode()
    await mode.start()


async def run_podcast_mode(topic: str, duration: int):
    """Run Podcast Mode"""
    print("\n" + "="*60)
    print("🎧 PODCAST MODE")
    print("="*60 + "\n")
    
    mode = PodcastMode()
    await mode.start_podcast(topic, duration)
    
    # Optionally save transcript
    transcript_path = f"/tmp/podcast_transcript_{topic.replace(' ', '_')}.txt"
    mode.save_transcript(transcript_path)


if __name__ == "__main__":
    main()
