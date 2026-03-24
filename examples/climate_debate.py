#!/usr/bin/env python3
"""Example: Climate change policy debate."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from debate_arena import Arena

# Load API key from environment
load_dotenv()


def progress_callback(message: str) -> None:
    """Print progress updates."""
    print(f"\n>>> Progress: {message[:100]}...")


def main():
    """Run a sample climate change debate."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Create a .env file with your API key:")
        print("  echo 'ANTHROPIC_API_KEY=your_key_here' > .env")
        return

    print("=" * 60)
    print("DEBATE ARENA: Climate Change Policy")
    print("=" * 60)

    arena = Arena(
        topic="Should governments implement aggressive carbon taxes to combat climate change?",
        rounds=3,
        api_key=api_key,
        on_progress=progress_callback,
    )

    result = arena.run()

    print("\n" + "=" * 60)
    print("DEBATE COMPLETE")
    print("=" * 60)

    # Print the full report
    print(result.report)

    # Save to file
    output_file = "/tmp/climate_debate_report.txt"
    with open(output_file, "w") as f:
        f.write(result.report)
    print(f"\nReport saved to: {output_file}")


if __name__ == "__main__":
    main()
