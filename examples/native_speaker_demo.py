#!/usr/bin/env python3
"""
Example: Native Speaker Mode
NYC Barista conversation with low-latency, interruptible dialogue
"""
import asyncio
from src.agents import NativeSpeakerMode
from src.config import SystemConfig


async def main():
    """Run Native Speaker Mode example"""
    print("\n" + "="*70)
    print("🎤 NATIVE SPEAKER MODE EXAMPLE")
    print("   NYC Barista with authentic slang and fast-paced conversation")
    print("="*70 + "\n")
    
    # Create and start native speaker mode
    mode = NativeSpeakerMode()
    
    try:
        await mode.start()
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for chatting!")


if __name__ == "__main__":
    asyncio.run(main())
