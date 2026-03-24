"""Extended tests for Debater functionality."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from debate_arena.core.debater import (
    Stance, Argument, Persona, Debater, DEFAULT_PERSONAS
)


class TestDebaterPromptContent:
    """Test debater prompt content and structure."""

    def test_opening_prompt_includes_persona_name(self):
        """Test that opening prompt includes persona name."""
        debater = Debater(Stance.PRO, api_key="test_key")
        prompt = debater._build_opening_prompt("AI Safety")

        assert debater.persona.name in prompt

    def test_opening_prompt_includes_persona_background(self):
        """Test that opening prompt includes persona background."""
        debater = Debater(Stance.PRO, api_key="test_key")
        prompt = debater._build_opening_prompt("AI Safety")

        assert debater.persona.background in prompt

    def test_opening_prompt_includes_argument_style(self):
        """Test that opening prompt includes argument style."""
        debater = Debater(Stance.PRO, api_key="test_key")
        prompt = debater._build_opening_prompt("AI Safety")

        assert debater.persona.argument_style in prompt

    def test_rebuttal_prompt_includes_opponent_arguments(self):
        """Test that rebuttal prompt includes opponent arguments."""
        debater = Debater(Stance.PRO, api_key="test_key")

        opp_args = [
            Argument("Opponent point 1", Stance.CON, "Opponent", 1),
            Argument("Opponent point 2", Stance.CON, "Opponent", 2),
        ]

        prompt = debater._build_rebuttal_prompt("Topic", opp_args, 1)

        assert "Opponent point 1" in prompt
        assert "Opponent point 2" in prompt

    def test_closing_prompt_includes_my_arguments(self):
        """Test that closing prompt includes debater's arguments."""
        debater = Debater(Stance.PRO, api_key="test_key")

        my_args = [
            Argument("My point 1", Stance.PRO, "Me", 1),
            Argument("My point 2", Stance.PRO, "Me", 2),
        ]

        prompt = debater._build_closing_prompt("Topic", my_args, [])

        # The prompt should reference the arguments
        assert "Topic" in prompt

    def test_closing_prompt_includes_opponent_arguments(self):
        """Test that closing prompt includes opponent arguments."""
        debater = Debater(Stance.PRO, api_key="test_key")

        opp_args = [
            Argument("Their point", Stance.CON, "Them", 1),
        ]

        prompt = debater._build_closing_prompt("Topic", [], opp_args)

        assert "Topic" in prompt


class TestDebaterStancePrompts:
    """Test prompts for different stances."""

    def test_pro_stance_opening_prompt(self):
        """Test PRO stance opening prompt."""
        debater = Debater(Stance.PRO, api_key="test_key")
        prompt = debater._build_opening_prompt("AI Safety")

        # Should indicate supporting position
        assert "support" in prompt.lower() or "in favor" in prompt.lower()

    def test_con_stance_opening_prompt(self):
        """Test CON stance opening prompt."""
        debater = Debater(Stance.CON, api_key="test_key")
        prompt = debater._build_opening_prompt("AI Safety")

        # Should indicate opposing position
        assert "oppos" in prompt.lower()

    def test_neutral_stance_opening_prompt(self):
        """Test NEUTRAL stance opening prompt."""
        debater = Debater(Stance.NEUTRAL, api_key="test_key")
        prompt = debater._build_opening_prompt("AI Safety")

        # Should handle neutral position
        assert "regard" in prompt.lower()

    def test_pro_rebuttal_prompt(self):
        """Test PRO rebuttal prompt content."""
        debater = Debater(Stance.PRO, api_key="test_key")
        opp_args = [Argument("CON says no", Stance.CON, "CON", 1)]

        prompt = debater._build_rebuttal_prompt("Topic", opp_args, 1)

        assert "supporting" in prompt.lower()

    def test_con_rebuttal_prompt(self):
        """Test CON rebuttal prompt content."""
        debater = Debater(Stance.CON, api_key="test_key")
        opp_args = [Argument("PRO says yes", Stance.PRO, "PRO", 1)]

        prompt = debater._build_rebuttal_prompt("Topic", opp_args, 1)

        assert "opposing" in prompt.lower()


class TestArgumentCreation:
    """Test Argument object creation and properties."""

    def test_argument_with_all_fields(self):
        """Test creating argument with all fields."""
        arg = Argument(
            content="Full argument content",
            stance=Stance.PRO,
            debater_name="Dr. Expert",
            round_num=5,
            is_rebuttal=True,
            target_stance=Stance.CON
        )

        assert arg.content == "Full argument content"
        assert arg.stance == Stance.PRO
        assert arg.debater_name == "Dr. Expert"
        assert arg.round_num == 5
        assert arg.is_rebuttal is True
        assert arg.target_stance == Stance.CON

    def test_argument_with_minimal_fields(self):
        """Test creating argument with minimal fields."""
        arg = Argument(
            content="Simple argument",
            stance=Stance.PRO,
            debater_name="Speaker",
            round_num=1
        )

        assert arg.content == "Simple argument"
        assert arg.is_rebuttal is False
        assert arg.target_stance is None

    def test_argument_equality(self):
        """Test argument equality based on content."""
        arg1 = Argument("Same content", Stance.PRO, "A", 1)
        arg2 = Argument("Same content", Stance.PRO, "A", 1)

        # These are different objects with same values
        assert arg1.content == arg2.content
        assert arg1.stance == arg2.stance

    def test_argument_round_number_variations(self):
        """Test arguments with various round numbers."""
        for round_num in [1, 5, 10, 100]:
            arg = Argument("Content", Stance.PRO, "Speaker", round_num)
            assert arg.round_num == round_num


class TestPersonaBehavior:
    """Test persona-based behavior differences."""

    def test_different_personas_different_names(self):
        """Test that different personas have different names."""
        pro_debater = Debater(Stance.PRO, api_key="test_key")
        con_debater = Debater(Stance.CON, api_key="test_key")

        assert pro_debater.persona.name != con_debater.persona.name

    def test_custom_persona_overrides_default(self):
        """Test that custom persona overrides default."""
        custom = Persona(
            name="Custom Expert",
            description="Custom description",
            background="Custom background",
            argument_style="Custom style"
        )

        debater = Debater(Stance.PRO, persona=custom, api_key="test_key")

        assert debater.persona.name == "Custom Expert"
        assert debater.persona.description == "Custom description"

    def test_persona_affects_all_prompts(self):
        """Test that persona affects all prompt types."""
        custom = Persona(
            name="Dr. Custom",
            description="Expert",
            background="PhD",
            argument_style="Analytical"
        )

        debater = Debater(Stance.PRO, persona=custom, api_key="test_key")

        opening_prompt = debater._build_opening_prompt("Topic")
        rebuttal_prompt = debater._build_rebuttal_prompt("Topic", [], 1)
        closing_prompt = debater._build_closing_prompt("Topic", [], [])

        # All prompts should include the custom persona name
        assert "Dr. Custom" in opening_prompt
        assert "Dr. Custom" in rebuttal_prompt
        assert "Dr. Custom" in closing_prompt


class TestArgumentTargets:
    """Test argument targeting and rebuttal behavior."""

    def test_rebuttal_targets_correct_stance(self):
        """Test that rebuttal targets the correct stance."""
        debater = Debater(Stance.PRO, api_key="test_key")

        opp_args = [
            Argument("CON point", Stance.CON, "CON", 1),
            Argument("NEUTRAL point", Stance.NEUTRAL, "NEUTRAL", 1),
        ]

        # Generate rebuttal - should target first opponent's stance
        with patch('debate_arena.core.debater._extract_text') as mock_extract:
            mock_extract.return_value = "Here is my rebuttal."

            result = debater.generate_rebuttal("Topic", opp_args, 1)

            assert result.is_rebuttal is True
            # Should target the stance of the first opponent argument
            assert result.target_stance == Stance.CON

    def test_rebuttal_to_empty_list(self):
        """Test rebuttal when no opponent arguments."""
        debater = Debater(Stance.PRO, api_key="test_key")

        with patch('debate_arena.core.debater._extract_text') as mock_extract:
            mock_extract.return_value = "I have no one to rebut."

            result = debater.generate_rebuttal("Topic", [], 1)

            assert result.is_rebuttal is True
            # No target when no opponents
            assert result.target_stance is None


class TestDebaterResponseStructure:
    """Test structure of debater responses."""

    def test_opening_statement_returns_argument(self):
        """Test that opening statement returns an Argument."""
        debater = Debater(Stance.PRO, api_key="test_key")

        with patch('debate_arena.core.debater._extract_text') as mock_extract:
            mock_extract.return_value = "Here is my opening statement."

            result = debater.generate_opening_statement("Topic")

            assert isinstance(result, Argument)
            assert result.stance == Stance.PRO
            assert result.round_num == 1
            assert result.is_rebuttal is False

    def test_rebuttal_returns_argument(self):
        """Test that rebuttal returns an Argument."""
        debater = Debater(Stance.PRO, api_key="test_key")

        with patch('debate_arena.core.debater._extract_text') as mock_extract:
            mock_extract.return_value = "Here is my rebuttal."

            result = debater.generate_rebuttal(
                "Topic",
                [Argument("Opponent", Stance.CON, "Opp", 1)],
                2
            )

            assert isinstance(result, Argument)
            assert result.stance == Stance.PRO
            assert result.round_num == 2
            assert result.is_rebuttal is True

    def test_closing_statement_returns_argument(self):
        """Test that closing statement returns an Argument."""
        debater = Debater(Stance.PRO, api_key="test_key")

        with patch('debate_arena.core.debater._extract_text') as mock_extract:
            mock_extract.return_value = "Here is my closing statement."

            result = debater.generate_closing_statement("Topic", [], [])

            assert isinstance(result, Argument)
            assert result.stance == Stance.PRO
            assert result.round_num == 999  # Special value for closing
            assert result.is_rebuttal is False


class TestStanceEnumBehavior:
    """Test Stance enum behavior."""

    def test_stance_iteration(self):
        """Test iterating over all stances."""
        stances = list(Stance)
        assert len(stances) == 3
        assert Stance.PRO in stances
        assert Stance.CON in stances
        assert Stance.NEUTRAL in stances

    def test_stance_from_string(self):
        """Test getting stance from string value."""
        assert Stance("pro") == Stance.PRO
        assert Stance("con") == Stance.CON
        assert Stance("neutral") == Stance.NEUTRAL

    def test_stance_string_conversion(self):
        """Test converting stance to string."""
        assert str(Stance.PRO) == "Stance.PRO"
        assert Stance.PRO.value == "pro"


class TestDefaultPersonas:
    """Test default persona configurations."""

    def test_pro_persona_exists(self):
        """Test that PRO persona exists and has required fields."""
        assert "pro" in DEFAULT_PERSONAS
        pro = DEFAULT_PERSONAS["pro"]
        assert pro.name
        assert pro.description
        assert pro.background
        assert pro.argument_style

    def test_con_persona_exists(self):
        """Test that CON persona exists and has required fields."""
        assert "con" in DEFAULT_PERSONAS
        con = DEFAULT_PERSONAS["con"]
        assert con.name
        assert con.description
        assert con.background
        assert con.argument_style

    def test_neutral_persona_exists(self):
        """Test that NEUTRAL persona exists and has required fields."""
        assert "neutral" in DEFAULT_PERSONAS
        neutral = DEFAULT_PERSONAS["neutral"]
        assert neutral.name
        assert neutral.description
        assert neutral.background
        assert neutral.argument_style

    def test_default_personas_have_different_names(self):
        """Test that default personas have different names."""
        names = [
            DEFAULT_PERSONAS["pro"].name,
            DEFAULT_PERSONAS["con"].name,
            DEFAULT_PERSONAS["neutral"].name,
        ]
        assert len(names) == len(set(names))
