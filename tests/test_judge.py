"""Tests for Judge functionality."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from anthropic.types import TextBlock
from debate_arena.core.judge import Judge, ArgumentScore, DebateVerdict
from debate_arena.core.debater import Stance, Argument


def test_judge_initialization():
    """Test Judge initialization."""
    judge = Judge(api_key="test_key")

    assert judge.model == "claude-3-7-sonnet-20250219"
    assert judge.client is not None


def test_judge_custom_model():
    """Test Judge with custom model."""
    judge = Judge(
        model="claude-3-opus-20240229",
        api_key="test_key"
    )

    assert judge.model == "claude-3-opus-20240229"


def test_argument_score_dataclass():
    """Test ArgumentScore creation."""
    score = ArgumentScore(
        content="Test argument",
        argument_strength=8,
        evidence_quality=7,
        logical_consistency=9,
        clarity=8,
        total_score=8,
        reasoning="Good argument"
    )

    assert score.content == "Test argument"
    assert score.argument_strength == 8
    assert score.evidence_quality == 7
    assert score.logical_consistency == 9
    assert score.clarity == 8
    assert score.total_score == 8
    assert score.reasoning == "Good argument"


def test_debate_verdict_dataclass():
    """Test DebateVerdict creation."""
    verdict = DebateVerdict(
        topic="Test topic",
        winner="pro",
        summary="Pro wins",
        pro_scores=[],
        con_scores=[],
    )

    assert verdict.topic == "Test topic"
    assert verdict.winner == "pro"
    assert verdict.summary == "Pro wins"


@patch("debate_arena.core.judge.Anthropic")
def test_evaluate_argument(mock_anthropic):
    """Test argument evaluation."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Create a proper TextBlock mock
    text_block = Mock(spec=TextBlock)
    text_block.text = """ARGUMENT_STRENGTH: 8
EVIDENCE_QUALITY: 7
LOGICAL_CONSISTENCY: 9
CLARITY: 8
TOTAL: 8
REASONING: This is a well-reasoned argument with good evidence."""
    mock_response.content = [text_block]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    judge = Judge(api_key="test_key")

    argument = Argument(
        content="This is a test argument about the topic.",
        stance=Stance.PRO,
        debater_name="Dr. Pro",
        round_num=1,
    )

    score = judge.evaluate_argument(argument)

    assert isinstance(score, ArgumentScore)
    assert score.argument_strength == 8
    assert score.evidence_quality == 7
    assert score.logical_consistency == 9
    assert score.clarity == 8
    assert score.total_score == 8
    assert score.reasoning == "This is a well-reasoned argument with good evidence."
    assert score.content == "This is a test argument about the topic."
    assert score.weighted_score is not None  # Default is None


@patch("debate_arena.core.judge.Anthropic")
def test_evaluate_argument_con_stance(mock_anthropic):
    """Test argument evaluation for CON stance."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Create a proper TextBlock mock
    text_block = Mock(spec=TextBlock)
    text_block.text = """ARGUMENT_STRENGTH: 7
EVIDENCE_QUALITY: 6
LOGICAL_CONSISTENCY: 8
CLARITY: 7
TOTAL: 7
REASONING: Decent argument but could use more evidence."""
    mock_response.content = [text_block]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    judge = Judge(api_key="test_key")

    argument = Argument(
        content="This is a counter argument.",
        stance=Stance.CON,
        debater_name="Dr. Con",
        round_num=1,
    )

    score = judge.evaluate_argument(argument)

    assert score.argument_strength == 7
    assert score.total_score == 7


@patch("debate_arena.core.judge.Anthropic")
def test_parse_score_spaces_in_keys(mock_anthropic):
    """Test score parsing with spaces in keys."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Create a proper TextBlock mock
    text_block = Mock(spec=TextBlock)
    text_block.text = """Argument Strength: 8
Evidence Quality: 7
Logical Consistency: 9
Clarity: 8
Total: 8
Reasoning: Test reasoning"""
    mock_response.content = [text_block]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    judge = Judge(api_key="test_key")

    argument = Argument(
        content="Test",
        stance=Stance.PRO,
        debater_name="Dr. Test",
        round_num=1,
    )

    score = judge.evaluate_argument(argument)

    assert score.argument_strength == 8
    assert score.evidence_quality == 7
    assert score.logical_consistency == 9
    assert score.clarity == 8
    assert score.total_score == 8


@patch("debate_arena.core.judge.Anthropic")
def test_render_verdict_pro_wins(mock_anthropic):
    """Test verdict rendering with pro winner."""
    mock_client = MagicMock()

    # Create proper TextBlock mocks
    text_block_1 = Mock(spec=TextBlock)
    text_block_1.text = "ARGUMENT_STRENGTH: 8\nEVIDENCE_QUALITY: 7\nLOGICAL_CONSISTENCY: 9\nCLARITY: 8\nTOTAL: 8\nREASONING: Good"

    text_block_2 = Mock(spec=TextBlock)
    text_block_2.text = "ARGUMENT_STRENGTH: 6\nEVIDENCE_QUALITY: 6\nLOGICAL_CONSISTENCY: 7\nCLARITY: 6\nTOTAL: 6\nREASONING: Okay"

    text_block_3 = Mock(spec=TextBlock)
    text_block_3.text = "Final analysis text"

    mock_response_1 = MagicMock()
    mock_response_1.content = [text_block_1]

    mock_response_2 = MagicMock()
    mock_response_2.content = [text_block_2]

    mock_response_3 = MagicMock()
    mock_response_3.content = [text_block_3]

    mock_client.messages.create.side_effect = [
        mock_response_1,  # First pro argument
        mock_response_2,  # First con argument
        mock_response_3,  # Final analysis
    ]
    mock_anthropic.return_value = mock_client

    judge = Judge(api_key="test_key")

    pro_args = [
        Argument(
            content="Pro argument 1",
            stance=Stance.PRO,
            debater_name="Dr. Pro",
            round_num=1,
        ),
    ]

    con_args = [
        Argument(
            content="Con argument 1",
            stance=Stance.CON,
            debater_name="Dr. Con",
            round_num=1,
        ),
    ]

    verdict = judge.render_verdict("Test topic", pro_args, con_args)

    assert verdict.winner == "pro"
    assert len(verdict.pro_scores) == 1
    assert len(verdict.con_scores) == 1
    assert verdict.best_argument is not None
    assert verdict.best_argument.total_score == 8  # Pro's higher score
    assert "Final analysis text" in verdict.final_analysis


@patch("debate_arena.core.judge.Anthropic")
def test_render_verdict_tie(mock_anthropic):
    """Test verdict rendering with a tie."""
    mock_client = MagicMock()

    text_block_1 = Mock(spec=TextBlock)
    text_block_1.text = "ARGUMENT_STRENGTH: 7\nEVIDENCE_QUALITY: 7\nLOGICAL_CONSISTENCY: 7\nCLARITY: 7\nTOTAL: 7\nREASONING: Equal"

    text_block_2 = Mock(spec=TextBlock)
    text_block_2.text = "ARGUMENT_STRENGTH: 7\nEVIDENCE_QUALITY: 7\nLOGICAL_CONSISTENCY: 7\nCLARITY: 7\nTOTAL: 7\nREASONING: Equal"

    text_block_3 = Mock(spec=TextBlock)
    text_block_3.text = "Tie analysis"

    mock_response_1 = MagicMock()
    mock_response_1.content = [text_block_1]

    mock_response_2 = MagicMock()
    mock_response_2.content = [text_block_2]

    mock_response_3 = MagicMock()
    mock_response_3.content = [text_block_3]

    mock_client.messages.create.side_effect = [
        mock_response_1,
        mock_response_2,
        mock_response_3,
    ]
    mock_anthropic.return_value = mock_client

    judge = Judge(api_key="test_key")

    pro_args = [
        Argument(content="Pro 1", stance=Stance.PRO, debater_name="Dr. Pro", round_num=1),
    ]

    con_args = [
        Argument(content="Con 1", stance=Stance.CON, debater_name="Dr. Con", round_num=1),
    ]

    verdict = judge.render_verdict("Test topic", pro_args, con_args)

    # With equal scores and difference < 0.5, should be a tie
    assert verdict.winner is None


@patch("debate_arena.core.judge.Anthropic")
def test_render_verdict_empty_arguments(mock_anthropic):
    """Test verdict rendering with no arguments."""
    mock_client = MagicMock()
    text_block = Mock(spec=TextBlock)
    text_block.text = "No arguments analysis"
    mock_response = MagicMock()
    mock_response.content = [text_block]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    judge = Judge(api_key="test_key")

    verdict = judge.render_verdict("Test topic", [], [])

    assert verdict.winner is None  # No winner when no arguments
    assert len(verdict.pro_scores) == 0
    assert len(verdict.con_scores) == 0
    assert verdict.best_argument is None


@patch("debate_arena.core.judge.Anthropic")
def test_evaluate_argument_default_values(mock_anthropic):
    """Test argument evaluation with parsing failures uses defaults."""
    mock_client = MagicMock()
    text_block = Mock(spec=TextBlock)
    text_block.text = "Invalid response format"
    mock_response = MagicMock()
    mock_response.content = [text_block]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    judge = Judge(api_key="test_key")

    argument = Argument(
        content="Test argument",
        stance=Stance.PRO,
        debater_name="Dr. Test",
        round_num=1,
    )

    score = judge.evaluate_argument(argument)

    # Should default to 5 when parsing fails
    assert score.argument_strength == 5
    assert score.evidence_quality == 5
    assert score.logical_consistency == 5
    assert score.clarity == 5
    assert score.total_score == 5


def test_parse_score_with_missing_fields():
    """Test _parse_score handles missing fields gracefully."""
    judge = Judge(api_key="test_key")

    response = """ARGUMENT_STRENGTH: 8
REASONING: Only some fields provided"""

    score = judge._parse_score("Test content", response)

    assert score.argument_strength == 8
    # Other fields should default to 5
    assert score.evidence_quality == 5
    assert score.logical_consistency == 5
    assert score.clarity == 5
