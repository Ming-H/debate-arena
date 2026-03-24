"""Tests for Arena functionality."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from debate_arena.core.arena import Arena, DebateResult
from debate_arena.core.debater import Stance, Argument, Persona, DEFAULT_PERSONAS
from debate_arena.core.judge import DebateVerdict, ArgumentScore


def test_arena_initialization():
    """Test that Arena initializes correctly."""
    arena = Arena(
        topic="Test topic",
        rounds=2,
        api_key="test_key",
    )

    assert arena.topic == "Test topic"
    assert arena.rounds == 2
    assert len(arena.debaters) == 2
    assert arena.debaters[0].stance == Stance.PRO
    assert arena.debaters[1].stance == Stance.CON
    assert arena.moderator is not None
    assert arena.judge is not None


def test_arena_with_custom_model():
    """Test Arena with custom model selection."""
    arena = Arena(
        topic="Test topic",
        rounds=2,
        api_key="test_key",
        model="claude-3-opus-20240229",
    )

    assert arena.model == "claude-3-opus-20240229"


def test_debate_result_report():
    """Test DebateResult report generation."""
    verdict = DebateVerdict(
        topic="Test topic",
        winner="pro",
        summary="Pro wins",
        pro_scores=[ArgumentScore(
            content="Test argument",
            argument_strength=8,
            evidence_quality=7,
            logical_consistency=9,
            clarity=8,
            total_score=8,
            reasoning="Good argument"
        )],
        con_scores=[],
        best_argument=None,
        final_analysis="Pro side won convincingly"
    )

    result = DebateResult(
        topic="Test topic",
        rounds=2,
        transcript=["Entry 1", "Entry 2"],
        verdict=verdict,
    )

    report = result.report
    assert "Test topic" in report
    assert "Entry 1" in report
    assert "Pro wins" in report
    assert "VERDICT" in report
    assert "DEBATE ARENA REPORT" in report


def test_debate_result_without_verdict():
    """Test DebateResult without a verdict."""
    result = DebateResult(
        topic="Test topic",
        rounds=2,
        transcript=["Entry 1", "Entry 2"],
        verdict=None,
    )

    report = result.report
    assert "Test topic" in report
    assert "Entry 1" in report
    assert "VERDICT" not in report


def test_stance_enum():
    """Test Stance enum values."""
    assert Stance.PRO.value == "pro"
    assert Stance.CON.value == "con"
    assert Stance.NEUTRAL.value == "neutral"


def test_persona_dataclass():
    """Test Persona dataclass."""
    persona = Persona(
        name="Test Persona",
        description="Test description",
        background="Test background",
        argument_style="Test style"
    )

    assert persona.name == "Test Persona"
    assert persona.description == "Test description"
    assert persona.background == "Test background"
    assert persona.argument_style == "Test style"


def test_default_personas():
    """Test default personas exist and have required attributes."""
    assert "pro" in DEFAULT_PERSONAS
    assert "con" in DEFAULT_PERSONAS

    pro_persona = DEFAULT_PERSONAS["pro"]
    assert pro_persona.name
    assert pro_persona.description
    assert pro_persona.background
    assert pro_persona.argument_style


def test_argument_dataclass():
    """Test Argument dataclass."""
    argument = Argument(
        content="Test argument content",
        stance=Stance.PRO,
        debater_name="Test Debater",
        round_num=1,
        is_rebuttal=False,
    )

    assert argument.content == "Test argument content"
    assert argument.stance == Stance.PRO
    assert argument.debater_name == "Test Debater"
    assert argument.round_num == 1
    assert argument.is_rebuttal is False
    assert argument.target_stance is None


def test_argument_score_dataclass():
    """Test ArgumentScore dataclass."""
    score = ArgumentScore(
        content="Test argument",
        argument_strength=8,
        evidence_quality=7,
        logical_consistency=9,
        clarity=8,
        total_score=8,
        reasoning="Good argument"
    )

    assert score.argument_strength == 8
    assert score.evidence_quality == 7
    assert score.logical_consistency == 9
    assert score.clarity == 8
    assert score.total_score == 8
    assert score.reasoning == "Good argument"


def test_debate_verdict_dataclass():
    """Test DebateVerdict dataclass."""
    verdict = DebateVerdict(
        topic="Test topic",
        winner="pro",
        summary="Test summary",
        pro_scores=[],
        con_scores=[],
    )

    assert verdict.topic == "Test topic"
    assert verdict.winner == "pro"
    assert verdict.summary == "Test summary"
    assert verdict.pro_scores == []
    assert verdict.con_scores == []


def test_debate_verdict_tie():
    """Test DebateVerdict with tie result."""
    verdict = DebateVerdict(
        topic="Test topic",
        winner=None,  # Tie
        summary="Tie game",
        pro_scores=[],
        con_scores=[],
    )

    assert verdict.winner is None
    assert verdict.summary == "Tie game"


def test_arena_progress_callback():
    """Test Arena progress callback functionality."""
    messages = []

    def callback(msg: str) -> None:
        messages.append(msg)

    arena = Arena(
        topic="Test topic",
        rounds=1,
        api_key="test_key",
        on_progress=callback,
    )

    # Test that callback is registered
    assert arena.on_progress is not None

    # Test that _log calls the callback
    arena._log("Test message")
    assert "Test message" in messages


def test_debate_result_timestamp():
    """Test that DebateResult has a timestamp."""
    result = DebateResult(
        topic="Test topic",
        rounds=2,
        transcript=[],
        verdict=None,
    )

    assert result.timestamp
    assert isinstance(result.timestamp, str)
