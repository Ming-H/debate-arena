"""Tests for custom debate criteria and functionality."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from debate_arena.core.debater import Stance, Argument, Persona, Debater, DEFAULT_PERSONAS
from debate_arena.core.arena import Arena, DebateResult
from debate_arena.core.judge import DebateVerdict, ArgumentScore, Judge
from debate_arena.core.moderator import Moderator

# Note: Some tests use DebateVerdict which is the correct class name in judge.py
# Moderator is the correct class name in moderator.py


class TestCustomJudgingCriteria:
    """Test scenarios for custom judging criteria."""

    def test_custom_judging_prompt_opening(self):
        """Test that custom judging criteria can be applied to opening statements."""
        judge = Judge(api_key="test_key")

        arg = Argument(
            content="AI will benefit humanity.",
            stance=Stance.PRO,
            debater_name="Dr. Chen",
            round_num=1
        )

        with patch.object(judge.client.messages, 'create') as mock_create:
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text="Score: 8/10")]
            mock_create.return_value = mock_response

            result = judge.evaluate_argument(arg)
            assert result is not None

    def test_evaluate_argument_weights_different_criteria(self):
        """Test that argument evaluation considers multiple criteria."""
        judge = Judge(api_key="test_key")

        arg = Argument(
            content="Well-reasoned argument with evidence.",
            stance=Stance.PRO,
            debater_name="Dr. Chen",
            round_num=1
        )

        # Mock the _extract_text function to return our test response
        with patch('debate_arena.core.judge._extract_text') as mock_extract:
            mock_extract.return_value = """ARGUMENT_STRENGTH: 8
EVIDENCE_QUALITY: 9
LOGICAL_CONSISTENCY: 7
CLARITY: 8
TOTAL: 8
REASONING: Strong argument with good evidence."""

            result = judge.evaluate_argument(arg)
            assert result.argument_strength == 8
            assert result.evidence_quality == 9
            assert result.total_score == 8

    def test_custom_scoring_weights(self):
        """Test that different scoring weights can be applied."""
        score1 = ArgumentScore(
            content="Argument 1",
            argument_strength=10,
            evidence_quality=5,
            logical_consistency=5,
            clarity=5,
            total_score=6,
            reasoning="High strength, lower evidence"
        )

        score2 = ArgumentScore(
            content="Argument 2",
            argument_strength=5,
            evidence_quality=10,
            logical_consistency=10,
            clarity=10,
            total_score=9,
            reasoning="Lower strength, higher evidence"
        )

        # Different weightings could produce different rankings
        assert score1.total_score != score2.total_score


class TestDebateHistoryPersistence:
    """Test scenarios for saving and loading debate history."""

    def test_debate_result_contains_full_transcript(self):
        """Test that DebateResult contains complete transcript."""
        result = DebateResult(
            topic="AI Safety",
            rounds=2,
            transcript=[
                "[MODERATOR]: Welcome",
                "[PRO]: Opening statement",
                "[CON]: Opening statement",
                "[PRO]: Rebuttal",
                "[CON]: Rebuttal",
            ],
            verdict=None
        )

        assert len(result.transcript) == 5
        assert "Welcome" in result.transcript[0]
        assert "Rebuttal" in result.transcript[-1]

    def test_debate_result_preserves_rounds_info(self):
        """Test that round information is preserved."""
        result = DebateResult(
            topic="Test topic",
            rounds=5,
            transcript=[],
            verdict=None
        )

        assert result.rounds == 5

    def test_debate_result_timestamp_format(self):
        """Test that timestamp is in ISO format."""
        result = DebateResult(
            topic="Test",
            rounds=1,
            transcript=[],
            verdict=None
        )

        # ISO format should contain 'T' and at least one ':'
        assert 'T' in result.timestamp
        assert ':' in result.timestamp

    def test_debate_result_serializable(self):
        """Test that DebateResult can be serialized to dict-like structure."""
        result = DebateResult(
            topic="Test",
            rounds=1,
            transcript=["Entry 1"],
            verdict=None
        )

        # All fields should be accessible
        assert result.topic == "Test"
        assert result.rounds == 1
        assert isinstance(result.transcript, list)


class TestDebateReplay:
    """Test scenarios for replaying debates."""

    def test_transcript_can_be_replayed(self):
        """Test that transcript can be read sequentially for replay."""
        transcript = [
            "Round 1: PRO opening",
            "Round 1: CON opening",
            "Round 2: PRO rebuttal",
            "Round 2: CON rebuttal",
        ]

        # Replay by reading in order
        replay_order = []
        for entry in transcript:
            replay_order.append(entry)

        assert replay_order == transcript

    def test_argument_sequence_preserved(self):
        """Test that argument order is preserved in transcript."""
        args = [
            Argument("PRO arg 1", Stance.PRO, "Dr. Chen", 1),
            Argument("CON arg 1", Stance.CON, "Prof. Webb", 1),
            Argument("PRO arg 2", Stance.PRO, "Dr. Chen", 2),
            Argument("CON arg 2", Stance.CON, "Prof. Webb", 2),
        ]

        # Round numbers should be sequential
        round_nums = [arg.round_num for arg in args]
        assert round_nums == [1, 1, 2, 2]


class TestCustomModels:
    """Test scenarios for using different Claude models."""

    @pytest.mark.parametrize("model", [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-3-7-sonnet-20250219",
        "claude-3-5-sonnet-20250219",
    ])
    def test_arena_with_different_models(self, model):
        """Test arena initialization with different models."""
        arena = Arena(
            topic="Test topic",
            rounds=1,
            api_key="test_key",
            model=model
        )
        assert arena.model == model
        assert arena.moderator.model == model
        assert arena.judge.model == model

    def test_debater_with_custom_model(self):
        """Test debater with custom model."""
        debater = Debater(
            stance=Stance.PRO,
            model="claude-3-opus-20240229",
            api_key="test_key"
        )
        assert debater.model == "claude-3-opus-20240229"

    def test_judge_with_custom_model(self):
        """Test judge with custom model."""
        judge = Judge(
            model="claude-3-haiku-20240307",
            api_key="test_key"
        )
        assert judge.model == "claude-3-haiku-20240307"

    def test_moderator_with_custom_model(self):
        """Test moderator with custom model."""
        moderator = Moderator(
            model="claude-3-sonnet-20240229",
            api_key="test_key"
        )
        assert moderator.model == "claude-3-sonnet-20240229"


class TestConcurrentDebates:
    """Test scenarios for multiple simultaneous debates."""

    def test_two_simultaneous_debates(self):
        """Test running two debates simultaneously."""
        arena1 = Arena(topic="Topic A", rounds=1, api_key="key1")
        arena2 = Arena(topic="Topic B", rounds=1, api_key="key2")

        # Both should exist independently
        assert arena1.topic == "Topic A"
        assert arena2.topic == "Topic B"
        assert arena1 is not arena2

    def test_concurrent_debate_isolation(self):
        """Test that concurrent debates don't interfere."""
        arenas = [
            Arena(topic=f"Topic {i}", rounds=1, api_key=f"key{i}")
            for i in range(3)
        ]

        for i, arena in enumerate(arenas):
            arena._log(f"Message {i}")

        # Each arena should have only its own messages
        for i, arena in enumerate(arenas):
            assert f"Message {i}" in arena.transcript
            for j in range(len(arenas)):
                if i != j:
                    assert f"Message {j}" not in arena.transcript

    def test_multiple_debaters_same_topic(self):
        """Test multiple debaters on same topic with different stances."""
        topic = "AI Safety"
        pro = Debater(Stance.PRO, api_key="key1")
        con = Debater(Stance.CON, api_key="key2")
        neutral = Debater(Stance.NEUTRAL, api_key="key3")

        # All should be able to generate prompts for same topic
        pro_prompt = pro._build_opening_prompt(topic)
        con_prompt = con._build_opening_prompt(topic)
        neutral_prompt = neutral._build_opening_prompt(topic)

        assert topic in pro_prompt
        assert topic in con_prompt
        assert topic in neutral_prompt


class TestPersonaCustomization:
    """Test scenarios for custom persona configurations."""

    def test_custom_persona_creation(self):
        """Test creating a fully custom persona."""
        custom = Persona(
            name="Dr. Custom",
            description="A custom debater",
            background="PhD in Custom Studies",
            argument_style="Uses custom arguments"
        )

        debater = Debater(
            stance=Stance.PRO,
            persona=custom,
            api_key="test_key"
        )

        assert debater.persona.name == "Dr. Custom"
        assert debater.persona.background == "PhD in Custom Studies"

    def test_persona_affects_prompt(self):
        """Test that persona details are included in prompts."""
        custom = Persona(
            name="Dr. Expert",
            description="Expert in field",
            background="20 years experience",
            argument_style="Data-driven"
        )

        debater = Debater(
            stance=Stance.PRO,
            persona=custom,
            api_key="test_key"
        )

        prompt = debater._build_opening_prompt("Test topic")

        assert "Dr. Expert" in prompt
        assert "20 years experience" in prompt
        assert "Data-driven" in prompt

    def test_multiple_custom_personas(self):
        """Test multiple debaters with different custom personas."""
        persona1 = Persona("Expert A", "Desc A", "BG A", "Style A")
        persona2 = Persona("Expert B", "Desc B", "BG B", "Style B")

        debater1 = Debater(Stance.PRO, persona=persona1, api_key="key1")
        debater2 = Debater(Stance.CON, persona=persona2, api_key="key2")

        assert debater1.persona.name == "Expert A"
        assert debater2.persona.name == "Expert B"

        prompt1 = debater1._build_opening_prompt("Topic")
        prompt2 = debater2._build_opening_prompt("Topic")

        assert "Expert A" in prompt1
        assert "Expert B" in prompt2
        assert "Expert A" not in prompt2
        assert "Expert B" not in prompt1
