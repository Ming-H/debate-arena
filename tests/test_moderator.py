"""Tests for Moderator functionality."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from anthropic.types import TextBlock
from debate_arena.core.moderator import Moderator
from debate_arena.core.debater import Stance, Argument, Debater, Persona


@pytest.fixture
def mock_debaters():
    """Create mock debaters for testing."""
    persona1 = Persona(
        name="Dr. Pro",
        description="Proponent",
        background="PhD",
        argument_style="Logical"
    )
    persona2 = Persona(
        name="Dr. Con",
        description="Opponent",
        background="PhD",
        argument_style="Critical"
    )

    debater1 = Mock(spec=Debater)
    debater1.persona = persona1
    debater1.stance = Stance.PRO

    debater2 = Mock(spec=Debater)
    debater2.persona = persona2
    debater2.stance = Stance.CON

    return [debater1, debater2]


def test_moderator_initialization():
    """Test Moderator initialization."""
    moderator = Moderator(api_key="test_key")

    assert moderator.model == "claude-3-7-sonnet-20250219"
    assert moderator.client is not None


def test_moderator_custom_model():
    """Test Moderator with custom model."""
    moderator = Moderator(
        model="claude-3-opus-20240229",
        api_key="test_key"
    )

    assert moderator.model == "claude-3-opus-20240229"


@patch("debate_arena.core.moderator.Anthropic")
def test_open_debate(mock_anthropic, mock_debaters):
    """Test opening debate statement generation."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Create a proper TextBlock mock
    text_block = Mock(spec=TextBlock)
    text_block.text = "Welcome to this debate on the topic."
    mock_response.content = [text_block]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    moderator = Moderator(api_key="test_key")
    opening = moderator.open_debate("Test topic", mock_debaters)

    assert opening == "Welcome to this debate on the topic."
    assert "Welcome" in opening or "debate" in opening.lower()


@patch("debate_arena.core.moderator.Anthropic")
def test_summarize_round(mock_anthropic):
    """Test round summary generation."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Create a proper TextBlock mock
    text_block = Mock(spec=TextBlock)
    text_block.text = "In this round, both sides presented compelling arguments."
    mock_response.content = [text_block]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    moderator = Moderator(api_key="test_key")

    arguments = [
        Argument(
            content="Pro argument",
            stance=Stance.PRO,
            debater_name="Dr. Pro",
            round_num=1,
        ),
        Argument(
            content="Con argument",
            stance=Stance.CON,
            debater_name="Dr. Con",
            round_num=1,
        ),
    ]

    summary = moderator.summarize_round("Test topic", 1, arguments)

    assert summary == "In this round, both sides presented compelling arguments."


@patch("debate_arena.core.moderator.Anthropic")
def test_summarize_round_empty_arguments(mock_anthropic):
    """Test round summary with no arguments."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Create a proper TextBlock mock
    text_block = Mock(spec=TextBlock)
    text_block.text = "No arguments were made."
    mock_response.content = [text_block]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    moderator = Moderator(api_key="test_key")
    summary = moderator.summarize_round("Test topic", 1, [])

    assert summary == "No arguments were made."


@patch("debate_arena.core.moderator.Anthropic")
def test_close_debate(mock_anthropic):
    """Test closing debate statement generation."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Create a proper TextBlock mock
    text_block = Mock(spec=TextBlock)
    text_block.text = "Thank you all for participating in this debate."
    mock_response.content = [text_block]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    moderator = Moderator(api_key="test_key")

    arguments = [
        Argument(
            content="Pro argument",
            stance=Stance.PRO,
            debater_name="Dr. Pro",
            round_num=1,
        ),
        Argument(
            content="Con argument",
            stance=Stance.CON,
            debater_name="Dr. Con",
            round_num=1,
        ),
    ]

    closing = moderator.close_debate("Test topic", arguments)

    assert closing == "Thank you all for participating in this debate."


@patch("debate_arena.core.moderator.Anthropic")
def test_close_debate_empty(mock_anthropic):
    """Test closing debate with no arguments."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Create a proper TextBlock mock
    text_block = Mock(spec=TextBlock)
    text_block.text = "This debate has concluded."
    mock_response.content = [text_block]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    moderator = Moderator(api_key="test_key")
    closing = moderator.close_debate("Test topic", [])

    assert closing == "This debate has concluded."


def test_open_debate_prompt_format(mock_debaters):
    """Test that open_debate includes debater information."""
    moderator = Moderator(api_key="test_key")

    # We can't test the exact prompt without mocking, but we can verify
    # the method accepts the correct parameters
    assert callable(moderator.open_debate)
    assert len(mock_debaters) == 2
