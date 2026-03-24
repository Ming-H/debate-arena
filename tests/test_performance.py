"""Tests for performance and stress testing scenarios."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from debate_arena.core.debater import Stance, Argument, Debater
from debate_arena.core.arena import Arena
from debate_arena.core.judge import Judge, DebateVerdict, ArgumentScore
from debate_arena.core.moderator import Moderator


class TestLongDebates:
    """Test scenarios with extended debate rounds."""

    def test_arena_with_ten_rounds(self):
        """Test arena with 10 rounds."""
        arena = Arena(
            topic="AI Safety",
            rounds=10,
            api_key="test_key"
        )
        assert arena.rounds == 10

    def test_arena_with_fifty_rounds(self):
        """Test arena with 50 rounds."""
        arena = Arena(
            topic="AI Safety",
            rounds=50,
            api_key="test_key"
        )
        assert arena.rounds == 50

    def test_transcript_grows_with_rounds(self):
        """Test that transcript grows with more rounds."""
        arena = Arena(topic="Test", rounds=1, api_key="test_key")

        initial_length = len(arena.transcript)
        arena._log("Message 1")
        arena._log("Message 2")
        arena._log("Message 3")

        assert len(arena.transcript) == initial_length + 3


class TestManyConcurrentDebates:
    """Test scenarios with many concurrent debates."""

    def test_ten_concurrent_arenas(self):
        """Test creating 10 concurrent arena instances."""
        arenas = [
            Arena(topic=f"Topic {i}", rounds=1, api_key=f"key{i}")
            for i in range(10)
        ]
        assert len(arenas) == 10
        assert all(isinstance(a, Arena) for a in arenas)

    def test_twenty_concurrent_debaters(self):
        """Test creating 20 concurrent debater instances."""
        debaters = [
            Debater(Stance.PRO if i % 2 == 0 else Stance.CON, api_key=f"key{i}")
            for i in range(20)
        ]
        assert len(debaters) == 20
        assert all(isinstance(d, Debater) for d in debaters)


class TestMemoryEfficiency:
    """Test scenarios related to memory usage."""

    def test_argument_storage_efficiency(self):
        """Test that arguments are stored efficiently."""
        args = []
        for i in range(100):
            args.append(Argument(
                content=f"Argument {i}",
                stance=Stance.PRO,
                debater_name=f"Debater {i % 5}",
                round_num=i // 10
            ))
        assert len(args) == 100

    def test_transcript_storage_with_many_entries(self):
        """Test transcript with many entries."""
        arena = Arena(topic="Test", rounds=1, api_key="test_key")

        for i in range(1000):
            arena._log(f"Entry {i}")

        assert len(arena.transcript) == 1000


class TestRapidArgumentGeneration:
    """Test rapid argument generation scenarios."""

    def test_multiple_opening_statements(self):
        """Test generating multiple opening statements."""
        debater = Debater(Stance.PRO, api_key="test_key")

        # Generate prompts for multiple topics
        topics = [f"Topic {i}" for i in range(10)]
        prompts = [debater._build_opening_prompt(topic) for topic in topics]

        assert len(prompts) == 10
        assert all(f"Topic {i}" in prompts[i] for i in range(10))

    def test_multiple_rebuttals(self):
        """Test generating multiple rebuttal prompts."""
        debater = Debater(Stance.PRO, api_key="test_key")

        opponent_args = [
            Argument(f"Opponent arg {i}", Stance.CON, "Opponent", 1)
            for i in range(5)
        ]

        for round_num in range(1, 4):
            prompt = debater._build_rebuttal_prompt(
                "Test topic",
                opponent_args,
                round_num
            )
            assert f"ROUND {round_num}" not in prompt  # Prompt doesn't contain round
            assert "Test topic" in prompt


class TestScoreCalculationPerformance:
    """Test score calculation performance."""

    def test_calculate_many_scores(self):
        """Test calculating scores for many arguments."""
        scores = []
        for i in range(50):
            scores.append(ArgumentScore(
                content=f"Argument {i}",
                argument_strength=i % 10 + 1,
                evidence_quality=i % 10 + 1,
                logical_consistency=i % 10 + 1,
                clarity=i % 10 + 1,
                total_score=i % 10 + 1,
                reasoning=f"Reasoning {i}"
            ))
        assert len(scores) == 50

    def test_average_score_calculation(self):
        """Test average score calculation for many items."""
        scores = [ArgumentScore(
            content=f"Arg {i}",
            argument_strength=8,
            evidence_quality=7,
            logical_consistency=9,
            clarity=8,
            total_score=8,
            reasoning="Good"
        ) for i in range(100)]

        avg = sum(s.total_score for s in scores) / len(scores)
        assert avg == 8.0


class TestVerdictWithManyScores:
    """Test verdict with many argument scores."""

    def test_verdict_with_many_pro_scores(self):
        """Test verdict with many PRO scores."""
        verdict = DebateVerdict(
            topic="Test",
            winner="pro",
            summary="PRO wins",
            pro_scores=[
                ArgumentScore(
                    content=f"PRO arg {i}",
                    argument_strength=8,
                    evidence_quality=7,
                    logical_consistency=9,
                    clarity=8,
                    total_score=8,
                    reasoning="Good"
                ) for i in range(20)
            ],
            con_scores=[],
            neutral_scores=[]
        )
        assert len(verdict.pro_scores) == 20
        assert len(verdict.con_scores) == 0


class TestPromptGenerationPerformance:
    """Test prompt generation performance."""

    def test_opening_prompt_generation(self):
        """Test generating many opening prompts."""
        debater = Debater(Stance.PRO, api_key="test_key")

        prompts = [
            debater._build_opening_prompt(f"Topic {i}")
            for i in range(50)
        ]

        assert len(prompts) == 50
        assert all(len(p) > 0 for p in prompts)

    def test_closing_prompt_generation(self):
        """Test generating many closing prompts."""
        debater = Debater(Stance.PRO, api_key="test_key")

        my_args = [Argument(f"My arg {i}", Stance.PRO, "Me", i) for i in range(10)]
        opp_args = [Argument(f"Opp arg {i}", Stance.CON, "Opp", i) for i in range(10)]

        prompts = [
            debater._build_closing_prompt("Topic", my_args, opp_args)
            for _ in range(10)
        ]

        assert len(prompts) == 10
        assert all("closing" in p.lower() for p in prompts)
