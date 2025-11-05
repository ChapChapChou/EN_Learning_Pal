#!/usr/bin/env python3
"""
Text-based testing for voice agents (no audio required)
Useful for development and testing without microphone/speakers
"""
import asyncio
from src.agents import NativeSpeakerMode, PodcastMode
from src.config import SystemConfig


async def test_native_speaker_text():
    """Test Native Speaker Mode with text input"""
    print("\n" + "="*70)
    print("🧪 TESTING NATIVE SPEAKER MODE (Text-based)")
    print("="*70 + "\n")
    
    mode = NativeSpeakerMode()
    await mode.initialize()
    
    # Test conversations
    test_inputs = [
        "Hey, can I get a large coffee?",
        "What's your recommendation for someone who likes it strong?",
        "Sounds good, I'll take that. How much?"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n[Turn {i}]")
        print(f"👤 User: {user_input}")
        
        response = await mode.process_text(user_input)
        print(f"🤖 {mode.agent_config.name}: {response}")
        
        # Show latency
        if mode.agent.latency_tracker:
            print(f"⚡ Latency: {mode.agent.latency_tracker[-1]:.0f}ms")
    
    # Final stats
    avg_latency = mode.agent.get_average_latency()
    print(f"\n📊 Average Latency: {avg_latency:.0f}ms (Target: {mode.system_config.target_latency_ms}ms)")
    
    await mode.stop()


async def test_podcast_text():
    """Test Podcast Mode with text orchestration"""
    print("\n" + "="*70)
    print("🧪 TESTING PODCAST MODE (Text-based)")
    print("="*70 + "\n")
    
    mode = PodcastMode()
    
    topic = "Common English Pronunciation Mistakes"
    duration = 2  # Short test
    
    await mode.start_podcast(topic, duration)


async def main():
    """Run all tests"""
    print("\n🚀 Starting Voice Agent Tests\n")
    
    # Test 1: Native Speaker
    await test_native_speaker_text()
    
    print("\n" + "="*70 + "\n")
    
    # Test 2: Podcast
    await test_podcast_text()
    
    print("\n✅ All tests complete!\n")


if __name__ == "__main__":
    asyncio.run(main())
