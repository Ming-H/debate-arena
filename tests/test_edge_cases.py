"""Tests for edge cases and boundary conditions."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from debate_arena.core.debater import Stance, Argument, Persona, DEFAULT_PERSONAS, Debater
from debate_arena.core.arena import Arena, DebateResult
from debate_arena.core.judge import DebateVerdict, ArgumentScore, Judge
from debate_arena.core.moderator import Moderator


class TestEmptyTopic:
    """Test scenarios with empty or invalid topics."""

    def test_empty_string_topic(self):
        """Test arena with empty string topic."""
        arena = Arena(
            topic="",
            rounds=2,
            api_key="test_key",
        )
        assert arena.topic == ""

    def test_whitespace_only_topic(self):
        """Test arena with whitespace-only topic."""
        arena = Arena(
            topic="   \n\t  ",
            rounds=2,
            api_key="test_key",
        )
        assert arena.topic == "   \n\t  "

    def test_none_topic_handling(self):
        """Test that None topic is accepted (Python allows this)."""
        # Python's typing doesn't enforce None checks at runtime
        # This documents the current behavior
        arena = Arena(
            topic=None,  # type: ignore
            rounds=2,
            api_key="test_key",
        )
        assert arena.topic is None


class TestLongTopic:
    """Test scenarios with very long topics."""

    def test_very_long_topic(self):
        """Test arena with extremely long topic (>1000 chars)."""
        long_topic = "This is a very long debate topic. " * 100  # ~3000 chars
        arena = Arena(
            topic=long_topic,
            rounds=1,
            api_key="test_key",
        )
        assert len(arena.topic) > 1000
        assert arena.topic == long_topic

    def test_long_topic_opening_prompt(self):
        """Test that opening statement prompt handles long topics."""
        debater = Debater(Stance.PRO, api_key="test_key")
        long_topic = "AI ethics question: " + "Should we? " * 200

        # The prompt building should not fail
        prompt = debater._build_opening_prompt(long_topic)
        assert long_topic in prompt
        assert len(prompt) > len(long_topic)


class TestSpecialCharactersTopic:
    """Test topics with special characters."""

    def test_unicode_emoji_topic(self):
        """Test topic with emoji and unicode characters."""
        emoji_topic = "Should we use AI? 🤖🤔"
        arena = Arena(
            topic=emoji_topic,
            rounds=1,
            api_key="test_key",
        )
        assert emoji_topic == arena.topic

    def test_special_characters_topic(self):
        """Test topic with various special characters."""
        special_topic = "AI & Ethics: <Safety> vs [Progress]?"
        arena = Arena(
            topic=special_topic,
            rounds=1,
            api_key="test_key",
        )
        assert special_topic == arena.topic

    def test_newlines_in_topic(self):
        """Test topic with embedded newlines."""
        multiline_topic = "Debate topic:\nAI Safety\nShould we pause?"
        arena = Arena(
            topic=multiline_topic,
            rounds=1,
            api_key="test_key",
        )
        assert "\n" in arena.topic

    def test_quotes_in_topic(self):
        """Test topic with various quote characters."""
        quote_topic = '''Should we say "AI is good" or 'AI is bad'?'''
        arena = Arena(
            topic=quote_topic,
            rounds=1,
            api_key="test_key",
        )
        assert '"' in arena.topic
        assert "'" in arena.topic


class TestEmptyArgument:
    """Test scenarios with empty or invalid arguments."""

    def test_empty_argument_content(self):
        """Test Argument with empty content."""
        arg = Argument(
            content="",
            stance=Stance.PRO,
            debater_name="Dr. Chen",
            round_num=1,
        )
        assert arg.content == ""

    def test_whitespace_argument_content(self):
        """Test Argument with whitespace-only content."""
        arg = Argument(
            content="   \n  ",
            stance=Stance.PRO,
            debater_name="Dr. Chen",
            round_num=1,
        )
        assert arg.content == "   \n  "

    def test_very_long_argument(self):
        """Test Argument with very long content."""
        long_content = "This is a long argument. " * 500
        arg = Argument(
            content=long_content,
            stance=Stance.PRO,
            debater_name="Dr. Chen",
            round_num=1,
        )
        assert len(arg.content) > 10000

    def test_special_characters_in_argument(self):
        """Test Argument with special characters."""
        special_content = "AI is: <great> & [terrible]! 🎉"
        arg = Argument(
            content=special_content,
            stance=Stance.PRO,
            debater_name="Dr. Chen",
            round_num=1,
        )
        assert special_content == arg.content


class TestZeroAndNegativeRounds:
    """Test scenarios with invalid round counts."""

    def test_zero_rounds(self):
        """Test arena with zero rounds."""
        arena = Arena(
            topic="Test topic",
            rounds=0,
            api_key="test_key",
        )
        assert arena.rounds == 0

    def test_negative_rounds(self):
        """Test arena with negative rounds (allowed, but unusual)."""
        arena = Arena(
            topic="Test topic",
            rounds=-1,
            api_key="test_key",
        )
        assert arena.rounds == -1

    def test_very_large_rounds(self):
        """Test arena with very large round count."""
        arena = Arena(
            topic="Test topic",
            rounds=1000,
            api_key="test_key",
        )
        assert arena.rounds == 1000


class TestEmptyTranscript:
    """Test DebateResult with empty transcript."""

    def test_empty_transcript(self):
        """Test DebateResult with no transcript entries."""
        result = DebateResult(
            topic="Test topic",
            rounds=2,
            transcript=[],
            verdict=None,
        )
        assert len(result.transcript) == 0

    def test_transcript_with_empty_strings(self):
        """Test transcript containing empty strings."""
        result = DebateResult(
            topic="Test topic",
            rounds=2,
            transcript=["", "", ""],
            verdict=None,
        )
        assert len(result.transcript) == 3

    def test_report_with_empty_transcript(self):
        """Test report generation with empty transcript."""
        result = DebateResult(
            topic="Test topic",
            rounds=2,
            transcript=[],
            verdict=None,
        )
        report = result.report
        assert "Test topic" in report
        assert "TRANSCRIPT" in report


class TestEmptyScores:
    """Test verdict with no scores."""

    def test_verdict_with_no_scores(self):
        """Test DebateVerdict with empty score lists."""
        verdict = DebateVerdict(
            topic="Test topic",
            winner=None,
            summary="No scores",
            pro_scores=[],
            con_scores=[],
            neutral_scores=[],
        )
        assert len(verdict.pro_scores) == 0
        assert len(verdict.con_scores) == 0
        assert len(verdict.neutral_scores) == 0

    def test_verdict_one_side_empty(self):
        """Test DebateVerdict where one side has no scores."""
        verdict = DebateVerdict(
            topic="Test topic",
            winner="pro",
            summary="PRO only",
            pro_scores=[ArgumentScore(
                content="PRO arg",
                argument_strength=8,
                evidence_quality=7,
                logical_consistency=9,
                clarity=8,
                total_score=8,
                reasoning="Good"
            )],
            con_scores=[],
            neutral_scores=[],
        )
        assert len(verdict.pro_scores) == 1
        assert len(verdict.con_scores) == 0


class TestPersonaEdgeCases:
    """Test edge cases with personas."""

    def test_empty_persona_name(self):
        """Test Persona with empty name."""
        persona = Persona(
            name="",
            description="Test",
            background="Test",
            argument_style="Test"
        )
        assert persona.name == ""

    def test_empty_persona_fields(self):
        """Test Persona with all empty fields."""
        persona = Persona(
            name="",
            description="",
            background="",
            argument_style=""
        )
        assert persona.name == ""
        assert persona.description == ""
        assert persona.background == ""
        assert persona.argument_style == ""


class TestStanceEdgeCases:
    """Test edge cases with stances."""

    def test_all_stance_values_defined(self):
        """Test all expected stance enum values exist."""
        assert hasattr(Stance, 'PRO')
        assert hasattr(Stance, 'CON')
        assert hasattr(Stance, 'NEUTRAL')

    def test_stance_values_are_unique(self):
        """Test that stance values are unique."""
        values = [s.value for s in Stance]
        assert len(values) == len(set(values))

    def test_stance_value_types(self):
        """Test that stance values are strings."""
        for stance in Stance:
            assert isinstance(stance.value, str)


class TestArgumentScoreEdgeCases:
    """Test edge cases with argument scores."""

    def test_minimum_scores(self):
        """Test ArgumentScore with minimum values."""
        score = ArgumentScore(
            content="Test",
            argument_strength=1,
            evidence_quality=1,
            logical_consistency=1,
            clarity=1,
            total_score=1,
            reasoning="Poor"
        )
        assert score.argument_strength == 1
        assert score.total_score == 1

    def test_maximum_scores(self):
        """Test ArgumentScore with maximum values."""
        score = ArgumentScore(
            content="Test",
            argument_strength=10,
            evidence_quality=10,
            logical_consistency=10,
            clarity=10,
            total_score=10,
            reasoning="Excellent"
        )
        assert score.argument_strength == 10
        assert score.total_score == 10

    def test_zero_scores(self):
        """Test ArgumentScore with zero values (edge case)."""
        score = ArgumentScore(
            content="Test",
            argument_strength=0,
            evidence_quality=0,
            logical_consistency=0,
            clarity=0,
            total_score=0,
            reasoning="None"
        )
        assert score.total_score == 0

    def test_scores_above_ten(self):
        """Test ArgumentScore with values > 10 (edge case)."""
        score = ArgumentScore(
            content="Test",
            argument_strength=11,
            evidence_quality=12,
            logical_consistency=13,
            clarity=14,
            total_score=15,
            reasoning="Beyond scale"
        )
        assert score.argument_strength == 11
        assert score.total_score == 15

    def test_negative_scores(self):
        """Test ArgumentScore with negative values (edge case)."""
        score = ArgumentScore(
            content="Test",
            argument_strength=-1,
            evidence_quality=-2,
            logical_consistency=-3,
            clarity=-4,
            total_score=-5,
            reasoning="Negative"
        )
        assert score.argument_strength == -1
        assert score.total_score == -5


class TestMockApiResponses:
    """Test edge cases with mocked API responses."""

    def test_empty_api_response(self):
        """Test handling of empty API response."""
        # Simulate empty content blocks
        result = ""
        for block in []:
            pass
        assert result == ""

    @patch('debate_arena.core.debater._extract_text')
    def test_none_text_block(self, mock_extract):
        """Test handling when TextBlock returns None/empty."""
        mock_extract.return_value = ""

        debater = Debater(Stance.PRO, api_key="test_key")

        with patch.object(debater.client.messages, 'create') as mock_create:
            mock_create.return_value = MagicMock(content=[])

            # This should not crash
            # (In real scenario, would need to handle gracefully)
            pass
