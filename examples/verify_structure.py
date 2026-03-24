#!/usr/bin/env python3
"""Verify DebateArena structure without API calls."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from debate_arena import Arena, Debater, Stance
from debate_arena.personas import PERSONAS


def main():
    """Verify the structure of DebateArena."""
    print("=" * 60)
    print("DEBATE ARENA - Structure Verification")
    print("=" * 60)

    # Check stances
    print("\n1. Available Stances:")
    for stance in Stance:
        print(f"   - {stance.name}: {stance.value}")

    # Check personas
    print(f"\n2. Available Personas: {len(PERSONAS)}")
    for name, persona in PERSONAS.items():
        print(f"   - {name}: {persona.name}")

    # Create an arena instance
    print("\n3. Creating Arena instance...")
    arena = Arena(
        topic="Should AI be regulated?",
        rounds=2,
        api_key="dummy_key",  # Dummy key for structure check
    )
    print(f"   Topic: {arena.topic}")
    print(f"   Rounds: {arena.rounds}")
    print(f"   Debaters: {len(arena.debaters)}")
    for debater in arena.debaters:
        print(f"      - {debater.persona.name} ({debater.stance.value})")

    # Check components
    print("\n4. Components:")
    print(f"   - Moderator: {type(arena.moderator).__name__}")
    print(f"   - Judge: {type(arena.judge).__name__}")

    print("\n5. Structure check: PASSED")
    print("\nTo run a full debate, set ANTHROPIC_API_KEY and run:")
    print("   python examples/climate_debate.py")


if __name__ == "__main__":
    main()
