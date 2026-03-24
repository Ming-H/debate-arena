"""Core components for DebateArena."""

from debate_arena.core.debater import Debater, Stance
from debate_arena.core.moderator import Moderator
from debate_arena.core.judge import Judge
from debate_arena.core.arena import Arena

__all__ = [
    "Debater",
    "Stance",
    "Moderator",
    "Judge",
    "Arena",
]
