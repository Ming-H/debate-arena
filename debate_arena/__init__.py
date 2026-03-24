"""DebateArena - AI-powered multi-agent debate system."""

from debate_arena.core.arena import Arena
from debate_arena.core.debater import Debater, Stance
from debate_arena.core.moderator import Moderator
from debate_arena.core.judge import Judge

__all__ = [
    "Arena",
    "Debater",
    "Stance",
    "Moderator",
    "Judge",
]

__version__ = "0.1.0"
