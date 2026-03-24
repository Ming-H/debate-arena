"""Extended tests for Moderator functionality."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from debate_arena.core.debater import Stance, Argument, Debater, DEFAULT_PERSONAS
from debate_arena.core.moderator import Moderator


class TestModeratorEdgeCases:
    """Test moderator edge cases."""

    def test_moderator_with_empty_topic(self):
        """Test moderator with empty topic."""
        moderator = Moderator(api_key="test_key")

        with patch('debate_arena.core.moderator._extract_text') as mock_extract:
            mock_extract.return_value = "Welcome to the debate."
            result = moderator.open_debate("", [])
            assert result is not None

    def test_moderator_with_very_long_topic(self):
        """Test moderator with very long topic."""
        moderator = Moderator(api_key="test_key")
        long_topic = "Debate: " + "AI " * 1000

        with patch('debate_arena.core.moderator._extract_text') as mock_extract:
            mock_extract.return_value = "Welcome to this long debate."
            result = moderator.open_debate(long_topic, [])
            assert result is not None

    def test_summarize_round_with_many_arguments(self):
        """Test summarizing round with many arguments."""
        moderator = Moderator(api_key="test_key")

        args = [
            Argument(f"Argument {i}", Stance.PRO if i % 2 == 0 else Stance.CON, f"Speaker {i}", 1)
            for i in range(10)
        ]

        with patch('debate_arena.core.moderator._extract_text') as mock_extract:
            mock_extract.return_value = "Summary: Many good points made."
            result = moderator.summarize_round("Test topic", 1, args)
            assert result is not None

    def test_close_debate_with_no_arguments(self):
        """Test closing debate with no arguments."""
        moderator = Moderator(api_key="test_key")

        with patch('debate_arena.core.moderator._extract_text') as mock_extract:
            mock_extract.return_value = "Debate concludes with no arguments."
            result = moderator.close_debate("Test topic", [])
            assert result is not None


class TestModeratorWithDifferentDebaterCombinations:
    """Test moderator with different debater configurations."""

    def test_moderator_with_single_debater(self):
        """Test moderator with only one debater."""
        moderator = Moderator(api_key="test_key")
        debater = Debater(Stance.PRO, api_key="test_key")

        with patch('debate_arena.core.moderator._extract_text') as mock_extract:
            mock_extract.return_value = "Solo debate begins."
            result = moderator.open_debate("Topic", [debater])
            assert result is not None

    def test_moderator_with_three_debaters(self):
        """Test moderator with three debaters."""
        moderator = Moderator(api_key="test_key")
        debaters = [
            Debater(Stance.PRO, api_key="test_key"),
            Debater(Stance.CON, api_key="test_key"),
            Debater(Stance.NEUTRAL, api_key="test_key"),
        ]

        with patch('debate_arena.core.moderator._extract_text') as mock_extract:
            mock_extract.return_value = "Three-way debate begins."
            result = moderator.open_debate("Topic", debaters)
            assert result is not None


class TestModeratorPrompts:
    """Test moderator prompt generation."""

    def test_open_debate_prompt_structure(self):
        """Test that open_debate creates properly structured prompt."""
        moderator = Moderator(api_key="test_key")

        # We can't directly access the prompt, but we can test the method
        with patch.object(moderator.client.messages, 'create') as mock_create:
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="Welcome!")]
            mock_create.return_value = mock_response

            result = moderator.open_debate("AI Safety", [])

            # Verify the API was called
            assert mock_create.called
            call_args = mock_create.call_args
            prompt = call_args[1]['messages'][0]['content']

            assert "AI Safety" in prompt

    def test_summarize_round_prompt_includes_topic(self):
        """Test that summarize_round includes topic in prompt."""
        moderator = Moderator(api_key="test_key")

        with patch.object(moderator.client.messages, 'create') as mock_create:
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="Round summary")]
            mock_create.return_value = mock_response

            args = [Argument("Test arg", Stance.PRO, "Speaker", 1)]

            result = moderator.summarize_round("Climate Change", 2, args)

            call_args = mock_create.call_args
            prompt = call_args[1]['messages'][0]['content']

            assert "Climate Change" in prompt
            assert "2" in prompt  # Round number should be included

    def test_close_debate_prompt_includes_topic(self):
        """Test that close_debate includes topic in prompt."""
        moderator = Moderator(api_key="test_key")

        with patch.object(moderator.client.messages, 'create') as mock_create:
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="Debate closed")]
            mock_create.return_value = mock_response

            result = moderator.close_debate("Space Exploration", [])

            call_args = mock_create.call_args
            prompt = call_args[1]['messages'][0]['content']

            assert "Space Exploration" in prompt


class TestModeratorWithSpecialTopics:
    """Test moderator with special topic formats."""

    def test_moderator_with_question_topic(self):
        """Test moderator with question-formatted topic."""
        moderator = Moderator(api_key="test_key")

        with patch('debate_arena.core.moderator._extract_text') as mock_extract:
            mock_extract.return_value = "Let's explore this question."
            result = moderator.open_debate("Should AI have rights?", [])
            assert result is not None

    def test_moderator_with_statement_topic(self):
        """Test moderator with statement-formatted topic."""
        moderator = Moderator(api_key="test_key")

        with patch('debate_arena.core.moderator._extract_text') as mock_extract:
            mock_extract.return_value = "Let's discuss this statement."
            result = moderator.open_debate("AI will transform society.", [])
            assert result is not None

    def test_moderator_with_multiline_topic(self):
        """Test moderator with multiline topic."""
        moderator = Moderator(api_key="test_key")

        multiline_topic = """Debate Topic:
AI Ethics and Safety
Question: Should we pause AI development?"""

        with patch('debate_arena.core.moderator._extract_text') as mock_extract:
            mock_extract.return_value = "Multiline topic debate begins."
            result = moderator.open_debate(multiline_topic, [])
            assert result is not None
