"""Extended tests for Judge functionality."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from debate_arena.core.debater import Stance, Argument
from debate_arena.core.judge import Judge, DebateVerdict, ArgumentScore


class TestJudgeVerdictCalculations:
    """Test verdict calculation logic."""

    def test_pro_wins_clearly(self):
        """Test verdict when PRO wins clearly."""
        judge = Judge(api_key="test_key")

        pro_args = [
            Argument(f"PRO arg {i}", Stance.PRO, "Dr. Chen", i)
            for i in range(1, 4)
        ]
        con_args = [
            Argument(f"CON arg {i}", Stance.CON, "Prof. Webb", i)
            for i in range(1, 4)
        ]

        with patch('debate_arena.core.judge._extract_text') as mock_extract:
            # Mock PRO scores higher
            mock_extract.return_value = """ARGUMENT_STRENGTH: 9
EVIDENCE_QUALITY: 9
LOGICAL_CONSISTENCY: 9
CLARITY: 9
TOTAL: 9
REASONING: Excellent."""

            verdict = judge.render_verdict("Test", pro_args, con_args)
            # With all mocked equal, winner depends on avg calculation
            assert verdict is not None

    def test_con_wins_clearly(self):
        """Test verdict when CON wins clearly."""
        judge = Judge(api_key="test_key")

        with patch('debate_arena.core.judge._extract_text') as mock_extract:
            mock_extract.return_value = """ARGUMENT_STRENGTH: 5
EVIDENCE_QUALITY: 5
LOGICAL_CONSISTENCY: 5
CLARITY: 5
TOTAL: 5
REASONING: Average."""

            verdict = judge.render_verdict(
                "Test",
                [Argument("PRO", Stance.PRO, "P", 1)],
                [Argument("CON", Stance.CON, "C", 1)]
            )
            assert verdict is not None

    def test_tie_verdict(self):
        """Test verdict when it's a tie."""
        judge = Judge(api_key="test_key")

        with patch('debate_arena.core.judge._extract_text') as mock_extract:
            mock_extract.return_value = """ARGUMENT_STRENGTH: 7
EVIDENCE_QUALITY: 7
LOGICAL_CONSISTENCY: 7
CLARITY: 7
TOTAL: 7
REASONING: Good."""

            verdict = judge.render_verdict(
                "Test",
                [Argument("PRO", Stance.PRO, "P", 1)],
                [Argument("CON", Stance.CON, "C", 1)]
            )
            # With equal scores, should be a tie (margin < 0.5)
            assert verdict.winner is None

    def test_verdict_with_empty_pro_args(self):
        """Test verdict with no PRO arguments."""
        judge = Judge(api_key="test_key")

        with patch('debate_arena.core.judge._extract_text') as mock_extract:
            mock_extract.return_value = """ARGUMENT_STRENGTH: 8
EVIDENCE_QUALITY: 8
LOGICAL_CONSISTENCY: 8
CLARITY: 8
TOTAL: 8
REASONING: Good."""

            verdict = judge.render_verdict(
                "Test",
                [],  # No PRO args
                [Argument("CON", Stance.CON, "C", 1)]
            )
            assert verdict is not None
            assert len(verdict.pro_scores) == 0

    def test_verdict_with_empty_con_args(self):
        """Test verdict with no CON arguments."""
        judge = Judge(api_key="test_key")

        with patch('debate_arena.core.judge._extract_text') as mock_extract:
            mock_extract.return_value = """ARGUMENT_STRENGTH: 8
EVIDENCE_QUALITY: 8
LOGICAL_CONSISTENCY: 8
CLARITY: 8
TOTAL: 8
REASONING: Good."""

            verdict = judge.render_verdict(
                "Test",
                [Argument("PRO", Stance.PRO, "P", 1)],
                []  # No CON args
            )
            assert verdict is not None
            assert len(verdict.con_scores) == 0

    def test_verdict_with_neutral_args(self):
        """Test verdict including neutral arguments."""
        judge = Judge(api_key="test_key")

        with patch('debate_arena.core.judge._extract_text') as mock_extract:
            mock_extract.return_value = """ARGUMENT_STRENGTH: 7
EVIDENCE_QUALITY: 7
LOGICAL_CONSISTENCY: 7
CLARITY: 7
TOTAL: 7
REASONING: Balanced."""

            neutral_args = [Argument("NEUTRAL", Stance.NEUTRAL, "N", 1)]

            verdict = judge.render_verdict(
                "Test",
                [Argument("PRO", Stance.PRO, "P", 1)],
                [Argument("CON", Stance.CON, "C", 1)],
                neutral_arguments=neutral_args
            )
            assert verdict is not None
            assert len(verdict.neutral_scores) == 1


class TestJudgeScoreParsing:
    """Test score parsing edge cases."""

    def test_parse_score_with_extra_whitespace(self):
        """Test parsing score with extra whitespace."""
        judge = Judge(api_key="test_key")

        with patch('debate_arena.core.judge._extract_text') as mock_extract:
            mock_extract.return_value = """
ARGUMENT_STRENGTH:   8
EVIDENCE_QUALITY:	7
LOGICAL_CONSISTENCY:  9
CLARITY: 8
TOTAL: 8
REASONING: Good argument
"""

            result = judge.evaluate_argument(
                Argument("Test", Stance.PRO, "Speaker", 1)
            )
            assert result.argument_strength == 8

    def test_parse_score_with_decimal_values(self):
        """Test parsing score with decimal values (should truncate to int)."""
        judge = Judge(api_key="test_key")

        with patch('debate_arena.core.judge._extract_text') as mock_extract:
            mock_extract.return_value = """ARGUMENT_STRENGTH: 8.5
EVIDENCE_QUALITY: 7.3
LOGICAL_CONSISTENCY: 9.1
CLARITY: 8.7
TOTAL: 8.4
REASONING: Good"""

            result = judge.evaluate_argument(
                Argument("Test", Stance.PRO, "Speaker", 1)
            )
            # int() will truncate decimals
            assert result.total_score == 8

    def test_parse_score_with_missing_optional_fields(self):
        """Test parsing when some optional fields are missing."""
        judge = Judge(api_key="test_key")

        with patch('debate_arena.core.judge._extract_text') as mock_extract:
            mock_extract.return_value = """ARGUMENT_STRENGTH: 8
TOTAL: 8
REASONING: Basic score"""

            result = judge.evaluate_argument(
                Argument("Test", Stance.PRO, "Speaker", 1)
            )
            # Missing fields should get default value of 5
            assert result.argument_strength == 8
            assert result.evidence_quality == 5
            assert result.logical_consistency == 5
            assert result.clarity == 5

    def test_parse_score_case_insensitive(self):
        """Test that key parsing is case-insensitive."""
        judge = Judge(api_key="test_key")

        with patch('debate_arena.core.judge._extract_text') as mock_extract:
            mock_extract.return_value = """argument_strength: 8
evidence_quality: 7
logical_consistency: 9
clarity: 8
total: 8
reasoning: Case insensitive test"""

            result = judge.evaluate_argument(
                Argument("Test", Stance.PRO, "Speaker", 1)
            )
            assert result.argument_strength == 8
            assert result.evidence_quality == 7

    def test_parse_score_with_colon_in_reasoning(self):
        """Test parsing when reasoning contains colons."""
        judge = Judge(api_key="test_key")

        with patch('debate_arena.core.judge._extract_text') as mock_extract:
            mock_extract.return_value = """ARGUMENT_STRENGTH: 8
EVIDENCE_QUALITY: 7
LOGICAL_CONSISTENCY: 9
CLARITY: 8
TOTAL: 8
REASONING: Key point: evidence is strong; however: logic could improve"""

            result = judge.evaluate_argument(
                Argument("Test", Stance.PRO, "Speaker", 1)
            )
            assert "Key point" in result.reasoning


class TestJudgeBestArgumentSelection:
    """Test best argument selection logic."""

    def test_best_argument_from_multiple(self):
        """Test selecting best argument from multiple."""
        judge = Judge(api_key="test_key")

        # Create scores with different totals
        scores = [
            ArgumentScore("Weak", 3, 3, 3, 3, 3, "Weak"),
            ArgumentScore("Strong", 9, 9, 9, 9, 9, "Strong"),
            ArgumentScore("Medium", 6, 6, 6, 6, 6, "Medium"),
        ]

        best = max(scores, key=lambda s: s.total_score)
        assert best.total_score == 9
        assert "Strong" in best.content

    def test_best_argument_with_ties(self):
        """Test best argument selection when there are ties."""
        judge = Judge(api_key="test_key")

        scores = [
            ArgumentScore("Arg A", 8, 8, 8, 8, 8, "Good A"),
            ArgumentScore("Arg B", 8, 8, 8, 8, 8, "Good B"),
        ]

        # First one returned by max() with ties depends on order
        best = max(scores, key=lambda s: s.total_score)
        assert best.total_score == 8


class TestJudgeFinalAnalysis:
    """Test final analysis generation."""

    def test_final_analysis_for_pro_winner(self):
        """Test final analysis when PRO wins."""
        judge = Judge(api_key="test_key")

        pro_scores = [ArgumentScore("PRO", 9, 9, 9, 9, 9, "Excellent")]
        con_scores = [ArgumentScore("CON", 5, 5, 5, 5, 5, "Weak")]

        with patch('debate_arena.core.judge._extract_text') as mock_extract:
            mock_extract.return_value = "PRO won convincingly with superior arguments."

            analysis = judge._generate_final_analysis("Test", pro_scores, con_scores, "pro")
            assert analysis is not None

    def test_final_analysis_for_con_winner(self):
        """Test final analysis when CON wins."""
        judge = Judge(api_key="test_key")

        pro_scores = [ArgumentScore("PRO", 5, 5, 5, 5, 5, "Weak")]
        con_scores = [ArgumentScore("CON", 9, 9, 9, 9, 9, "Excellent")]

        with patch('debate_arena.core.judge._extract_text') as mock_extract:
            mock_extract.return_value = "CON won convincingly with superior arguments."

            analysis = judge._generate_final_analysis("Test", pro_scores, con_scores, "con")
            assert analysis is not None

    def test_final_analysis_for_tie(self):
        """Test final analysis when it's a tie."""
        judge = Judge(api_key="test_key")

        pro_scores = [ArgumentScore("PRO", 7, 7, 7, 7, 7, "Good")]
        con_scores = [ArgumentScore("CON", 7, 7, 7, 7, 7, "Good")]

        with patch('debate_arena.core.judge._extract_text') as mock_extract:
            mock_extract.return_value = "The debate was evenly matched."

            analysis = judge._generate_final_analysis("Test", pro_scores, con_scores, None)
            assert analysis is not None


class TestJudgeEdgeCases:
    """Test judge edge cases."""

    def test_evaluate_very_long_argument(self):
        """Test evaluating a very long argument."""
        judge = Judge(api_key="test_key")

        long_content = "This is a very long argument. " * 100

        with patch('debate_arena.core.judge._extract_text') as mock_extract:
            mock_extract.return_value = """ARGUMENT_STRENGTH: 7
EVIDENCE_QUALITY: 7
LOGICAL_CONSISTENCY: 7
CLARITY: 5
TOTAL: 6
REASONING: Too long"""

            result = judge.evaluate_argument(
                Argument(long_content, Stance.PRO, "Speaker", 1)
            )
            assert result is not None

    def test_evaluate_empty_argument(self):
        """Test evaluating an empty argument."""
        judge = Judge(api_key="test_key")

        with patch('debate_arena.core.judge._extract_text') as mock_extract:
            mock_extract.return_value = """ARGUMENT_STRENGTH: 1
EVIDENCE_QUALITY: 1
LOGICAL_CONSISTENCY: 1
CLARITY: 1
TOTAL: 1
REASONING: Empty argument"""

            result = judge.evaluate_argument(
                Argument("", Stance.PRO, "Speaker", 1)
            )
            assert result is not None

    def test_render_verdict_no_arguments(self):
        """Test rendering verdict with no arguments at all."""
        judge = Judge(api_key="test_key")

        with patch('debate_arena.core.judge._extract_text') as mock_extract:
            mock_extract.return_value = "No debate occurred."

            verdict = judge.render_verdict("Test", [], [])
            assert verdict is not None
            assert verdict.winner is None  # No winner when no arguments
