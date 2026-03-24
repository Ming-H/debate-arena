"""Tests for Debater functionality."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from anthropic.types import TextBlock
from debate_arena.core.debater import (
    Debater,
    Stance,
    Argument,
    Persona,
    DEFAULT_PERSONAS,
)


def test_debater_initialization():
    """Test Debater initialization with default persona."""
    debater = Debater(
        stance=Stance.PRO,
        api_key="test_key",
    )

    assert debater.stance == Stance.PRO
    assert debater.persona == DEFAULT_PERSONAS["pro"]
    assert debater.client is not None


def test_debater_custom_persona():
    """Test Debater with custom persona."""
    custom_persona = Persona(
        name="Custom Debater",
        description="Custom description",
        background="Custom background",
        argument_style="Custom style"
    )

    debater = Debater(
        stance=Stance.CON,
        persona=custom_persona,
        api_key="test_key",
    )

    assert debater.stance == Stance.CON
    assert debater.persona == custom_persona
    assert debater.persona.name == "Custom Debater"


def test_debater_neutral_stance():
    """Test Debater with neutral stance requires custom persona."""
    custom_persona = Persona(
        name="Dr. Neutral",
        description="Neutral mediator",
        background="PhD in Mediation",
        argument_style="Balanced and objective"
    )

    debater = Debater(
        stance=Stance.NEUTRAL,
        persona=custom_persona,
        api_key="test_key",
    )

    assert debater.stance == Stance.NEUTRAL
    assert debater.persona.name == "Dr. Neutral"


@patch("debate_arena.core.debater.Anthropic")
def test_generate_opening_statement(mock_anthropic):
    """Test opening statement generation."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Create a proper TextBlock mock
    text_block = Mock(spec=TextBlock)
    text_block.text = "This is my opening statement on the topic."
    mock_response.content = [text_block]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    debater = Debater(
        stance=Stance.PRO,
        api_key="test_key",
    )

    argument = debater.generate_opening_statement("Test topic")

    assert isinstance(argument, Argument)
    assert argument.content == "This is my opening statement on the topic."
    assert argument.stance == Stance.PRO
    assert argument.round_num == 1
    assert argument.is_rebuttal is False
    assert argument.debater_name == debater.persona.name


@patch("debate_arena.core.debater.Anthropic")
def test_generate_rebuttal(mock_anthropic):
    """Test rebuttal generation."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Create a proper TextBlock mock
    text_block = Mock(spec=TextBlock)
    text_block.text = "I disagree with your points."
    mock_response.content = [text_block]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    debater = Debater(
        stance=Stance.PRO,
        api_key="test_key",
    )

    opponent_args = [
        Argument(
            content="Opponent argument",
            stance=Stance.CON,
            debater_name="Opponent",
            round_num=1,
        )
    ]

    rebuttal = debater.generate_rebuttal("Test topic", opponent_args, 2)

    assert isinstance(rebuttal, Argument)
    assert rebuttal.content == "I disagree with your points."
    assert rebuttal.stance == Stance.PRO
    assert rebuttal.round_num == 2
    assert rebuttal.is_rebuttal is True
    assert rebuttal.target_stance == Stance.CON


@patch("debate_arena.core.debater.Anthropic")
def test_generate_closing_statement(mock_anthropic):
    """Test closing statement generation."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Create a proper TextBlock mock
    text_block = Mock(spec=TextBlock)
    text_block.text = "In conclusion, my position stands."
    mock_response.content = [text_block]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    debater = Debater(
        stance=Stance.PRO,
        api_key="test_key",
    )

    my_args = [
        Argument(
            content="My argument",
            stance=Stance.PRO,
            debater_name=debater.persona.name,
            round_num=1,
        )
    ]
    opponent_args = []

    closing = debater.generate_closing_statement("Test topic", my_args, opponent_args)

    assert isinstance(closing, Argument)
    assert closing.content == "In conclusion, my position stands."
    assert closing.stance == Stance.PRO
    assert closing.round_num == 999  # Special value for closing
    assert closing.is_rebuttal is False


def test_build_opening_prompt():
    """Test opening prompt building for different stances."""
    pro_debater = Debater(stance=Stance.PRO, api_key="test_key")
    pro_prompt = pro_debater._build_opening_prompt("Test topic")
    assert "in support of" in pro_prompt
    assert "Test topic" in pro_prompt

    con_debater = Debater(stance=Stance.CON, api_key="test_key")
    con_prompt = con_debater._build_opening_prompt("Test topic")
    assert "in opposition to" in con_prompt

    # Test neutral stance with custom persona (since no default for neutral)
    neutral_persona = Persona(
        name="Dr. Neutral",
        description="Neutral mediator",
        background="PhD",
        argument_style="Balanced"
    )
    neutral_debater = Debater(stance=Stance.NEUTRAL, persona=neutral_persona, api_key="test_key")
    neutral_prompt = neutral_debater._build_opening_prompt("Test topic")
    assert "regarding" in neutral_prompt


def test_build_rebuttal_prompt():
    """Test rebuttal prompt building."""
    debater = Debater(stance=Stance.PRO, api_key="test_key")

    opponent_args = [
        Argument(
            content="Opponent's argument",
            stance=Stance.CON,
            debater_name="Opponent",
            round_num=1,
        )
    ]

    prompt = debater._build_rebuttal_prompt("Test topic", opponent_args, 2)

    assert "Test topic" in prompt
    assert "supporting" in prompt
    assert "Opponent" in prompt
    assert "Opponent's argument" in prompt
    assert "Round 2" not in prompt  # round_num not in prompt directly


def test_build_closing_prompt():
    """Test closing prompt building."""
    debater = Debater(stance=Stance.PRO, api_key="test_key")

    my_args = [
        Argument(
            content="My argument",
            stance=Stance.PRO,
            debater_name="Me",
            round_num=1,
        )
    ]
    opponent_args = [
        Argument(
            content="Their argument",
            stance=Stance.CON,
            debater_name="Them",
            round_num=1,
        )
    ]

    prompt = debater._build_closing_prompt("Test topic", my_args, opponent_args)

    assert "Test topic" in prompt
    assert "in favor of" in prompt


def test_debater_custom_model():
    """Test Debater with custom model."""
    debater = Debater(
        stance=Stance.PRO,
        model="claude-3-opus-20240229",
        api_key="test_key",
    )

    assert debater.model == "claude-3-opus-20240229"
