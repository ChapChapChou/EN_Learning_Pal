#!/usr/bin/env python3
"""
Example: Podcast Mode
Two agents (Host & Expert) in orchestrated conversation
"""
import asyncio
from src.agents import PodcastMode


async def main():
    """Run Podcast Mode example"""
    print("\n" + "="*70)
    print("🎧 PODCAST MODE EXAMPLE")
    print("   Two agents in conversation about language learning")
    print("="*70 + "\n")
    
    # Create podcast mode
    mode = PodcastMode()
    
    # Define podcast topic
    topic = "Tips for Learning English as a Second Language"
    duration = 3  # minutes
    
    try:
        await mode.start_podcast(topic, duration)
        
        # Save transcript
        mode.save_transcript("/tmp/podcast_transcript.txt")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Podcast stopped")


if __name__ == "__main__":
    asyncio.run(main())
