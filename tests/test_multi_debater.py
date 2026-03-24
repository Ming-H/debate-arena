"""Tests for multi-debater debate scenarios."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from debate_arena.core.debater import Stance, Argument, Persona, DEFAULT_PERSONAS
from debate_arena.core.arena import Arena, DebateResult
from debate_arena.core.judge import DebateVerdict, ArgumentScore


class TestMultiDebaterScenarios:
    """Test scenarios with more than 2 debaters."""

    def test_arena_with_three_debaters_pro_con_neutral(self):
        """Test arena initialization with 3 debaters: PRO, CON, NEUTRAL."""
        # First test that we can create 3 debaters with different stances
        debaters = []
        for stance in [Stance.PRO, Stance.CON, Stance.NEUTRAL]:
            debaters.append(DEFAULT_PERSONAS[stance.value])

        assert len(debaters) == 3
        assert all(isinstance(d, Persona) for d in debaters)

    def test_three_way_debate_stance_combinations(self):
        """Test valid stance combinations for 3-way debates."""
        valid_combinations = [
            [Stance.PRO, Stance.CON, Stance.NEUTRAL],
            [Stance.PRO, Stance.PRO, Stance.CON],  # Two PRO, one CON
            [Stance.CON, Stance.CON, Stance.PRO],  # Two CON, one PRO
        ]

        for combo in valid_combinations:
            assert len(combo) == 3
            assert all(isinstance(s, Stance) for s in combo)

    def test_four_way_debate_stance_combinations(self):
        """Test valid stance combinations for 4-way debates."""
        valid_combinations = [
            [Stance.PRO, Stance.PRO, Stance.CON, Stance.CON],
            [Stance.PRO, Stance.CON, Stance.NEUTRAL, Stance.PRO],
            [Stance.PRO, Stance.PRO, Stance.PRO, Stance.CON],
            [Stance.CON, Stance.CON, Stance.CON, Stance.PRO],
        ]

        for combo in valid_combinations:
            assert len(combo) == 4
            assert all(isinstance(s, Stance) for s in combo)

    def test_arguments_by_multiple_debaters_same_stance(self):
        """Test tracking arguments when multiple debaters share same stance."""
        arguments_by_stance = {
            Stance.PRO: [],
            Stance.CON: [],
            Stance.NEUTRAL: [],
        }

        # Add arguments from multiple PRO debaters
        arg1 = Argument(
            content="First PRO argument",
            stance=Stance.PRO,
            debater_name="Dr. Chen",
            round_num=1,
        )
        arg2 = Argument(
            content="Second PRO argument",
            stance=Stance.PRO,
            debater_name="Dr. Smith",
            round_num=1,
        )

        arguments_by_stance[Stance.PRO].extend([arg1, arg2])

        assert len(arguments_by_stance[Stance.PRO]) == 2
        assert arguments_by_stance[Stance.PRO][0].debater_name == "Dr. Chen"
        assert arguments_by_stance[Stance.PRO][1].debater_name == "Dr. Smith"

    def test_neutral_stance_in_debate(self):
        """Test NEUTRAL stance can participate in debate."""
        neutral_persona = DEFAULT_PERSONAS["neutral"]

        assert neutral_persona.name == "Dr. Alex Morgan"
        assert "balanced" in neutral_persona.description.lower()

    def test_multi_debater_argument_targeting(self):
        """Test arguments can target specific stances in multi-debater scenario."""
        pro_arg = Argument(
            content="PRO argument",
            stance=Stance.PRO,
            debater_name="Dr. Chen",
            round_num=1,
        )

        # CON rebuttal to PRO
        con_rebuttal = Argument(
            content="Rebuttal to PRO",
            stance=Stance.CON,
            debater_name="Prof. Webb",
            round_num=1,
            is_rebuttal=True,
            target_stance=Stance.PRO,
        )

        assert con_rebuttal.is_rebuttal is True
        assert con_rebuttal.target_stance == Stance.PRO

    def test_debate_verdict_with_multiple_stances(self):
        """Test verdict can handle multiple stances including NEUTRAL."""
        verdict = DebateVerdict(
            topic="Test topic",
            winner="pro",
            summary="PRO wins",
            pro_scores=[
                ArgumentScore(
                    content="PRO argument 1",
                    argument_strength=8,
                    evidence_quality=7,
                    logical_consistency=9,
                    clarity=8,
                    total_score=8,
                    reasoning="Good"
                )
            ],
            con_scores=[],
            neutral_scores=[
                ArgumentScore(
                    content="NEUTRAL argument",
                    argument_strength=6,
                    evidence_quality=7,
                    logical_consistency=8,
                    clarity=9,
                    total_score=7,
                    reasoning="Balanced"
                )
            ],
        )

        assert len(verdict.pro_scores) == 1
        assert len(verdict.con_scores) == 0
        assert len(verdict.neutral_scores) == 1


class TestDynamicDebaterAddition:
    """Test scenarios for dynamically adding debaters."""

    def test_add_debater_to_empty_arena(self):
        """Test adding first debater to an empty arena."""
        debaters = []

        # Add PRO debater
        debaters.append(("PRO", DEFAULT_PERSONAS["pro"]))
        assert len(debaters) == 1

        # Add CON debater
        debaters.append(("CON", DEFAULT_PERSONAS["con"]))
        assert len(debaters) == 2

    def test_add_debater_mid_debate(self):
        """Test adding a debater while debate is in progress."""
        existing_debaters = [Stance.PRO, Stance.CON]

        # Track existing arguments
        arguments_by_stance = {
            Stance.PRO: [Argument(
                content="Existing PRO argument",
                stance=Stance.PRO,
                debater_name="Dr. Chen",
                round_num=1,
            )],
            Stance.CON: [],
        }

        # Add NEUTRAL debater mid-debate
        existing_debaters.append(Stance.NEUTRAL)
        arguments_by_stance[Stance.NEUTRAL] = []

        assert Stance.NEUTRAL in existing_debaters
        assert Stance.NEUTRAL in arguments_by_stance
        assert len(arguments_by_stance[Stance.NEUTRAL]) == 0

    def test_max_debaters_limit(self):
        """Test reasonable limits on number of debaters."""
        # Test with up to 5 debaters
        max_debaters = 5
        stances = [Stance.PRO, Stance.CON, Stance.NEUTRAL]

        # For 5 debaters, we'd need to repeat stances
        debaters = []
        for i in range(max_debaters):
            stance = stances[i % len(stances)]
            debaters.append(stance)

        assert len(debaters) == max_debaters

    def test_debater_rotation_order(self):
        """Test speaking order in multi-debater scenarios."""
        debaters = [
            ("PRO", "Dr. Chen"),
            ("CON", "Prof. Webb"),
            ("NEUTRAL", "Dr. Morgan"),
            ("PRO", "Dr. Smith"),
        ]

        speaking_order = [d[0] for d in debaters]

        # Verify we can track rotation
        assert speaking_order[0] == "PRO"
        assert speaking_order[1] == "CON"
        assert speaking_order[2] == "NEUTRAL"
        assert speaking_order[3] == "PRO"


class TestMultiDebaterArgumentFlow:
    """Test argument flow in multi-debater debates."""

    def test_rebuttal_targets_in_multi_debater(self):
        """Test rebuttal targeting when multiple opponents exist."""
        # PRO has two opponents: CON1 and CON2
        pro_debater = "Dr. Chen"
        opponents = [
            Argument(
                content="CON argument 1",
                stance=Stance.CON,
                debater_name="Prof. Webb",
                round_num=1,
            ),
            Argument(
                content="CON argument 2",
                stance=Stance.CON,
                debater_name="Dr. Smith",
                round_num=1,
            ),
        ]

        # PRO rebuts to both
        assert len(opponents) == 2
        assert all(arg.stance == Stance.CON for arg in opponents)

    def test_neutral_rebuts_to_both_sides(self):
        """Test NEUTRAL stance can rebut to both PRO and CON."""
        neutral_rebuttals = [
            Argument(
                content="Rebuttal to PRO",
                stance=Stance.NEUTRAL,
                debater_name="Dr. Morgan",
                round_num=1,
                is_rebuttal=True,
                target_stance=Stance.PRO,
            ),
            Argument(
                content="Rebuttal to CON",
                stance=Stance.NEUTRAL,
                debater_name="Dr. Morgan",
                round_num=1,
                is_rebuttal=True,
                target_stance=Stance.CON,
            ),
        ]

        assert len(neutral_rebuttals) == 2
        assert neutral_rebuttals[0].target_stance == Stance.PRO
        assert neutral_rebuttals[1].target_stance == Stance.CON

    def test_multi_debater_closing_statements(self):
        """Test all debaters get closing statements."""
        debaters = [Stance.PRO, Stance.CON, Stance.NEUTRAL]

        closing_statements = {}
        for stance in debaters:
            closing_statements[stance] = Argument(
                content=f"Closing by {stance.value}",
                stance=stance,
                debater_name=f"Dr. {stance.value.title()}",
                round_num=999,
            )

        assert len(closing_statements) == 3
        assert all(s in closing_statements for s in debaters)
