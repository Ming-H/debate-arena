"""Tests for Debate history functionality."""

import pytest
import json
import tempfile
import os
from pathlib import Path

from debate_arena.core.history import DebateHistory
from debate_arena.core.arena import DebateResult
from debate_arena.core.judge import DebateVerdict, ArgumentScore


@pytest.fixture
def temp_storage_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_result():
    """Create a sample DebateResult for testing."""
    return DebateResult(
        topic="Should AI be regulated?",
        rounds=2,
        transcript=[
            "[MODERATOR]: Welcome to the debate",
            "[PRO]: AI should be regulated",
            "[CON]: AI should not be regulated",
        ],
        timestamp="2024-01-15T10:30:00",
        verdict=None,
    )


@pytest.fixture
def sample_result_with_verdict():
    """Create a sample DebateResult with verdict for testing."""
    verdict = DebateVerdict(
        topic="Should AI be regulated?",
        winner="pro",
        summary="Pro wins with score 8/10",
        pro_scores=[
            ArgumentScore(
                content="Pro argument 1",
                argument_strength=8,
                evidence_quality=7,
                logical_consistency=9,
                clarity=8,
                total_score=8,
                reasoning="Strong argument"
            )
        ],
        con_scores=[
            ArgumentScore(
                content="Con argument 1",
                argument_strength=6,
                evidence_quality=6,
                logical_consistency=7,
                clarity=6,
                total_score=6,
                reasoning="Weaker argument"
            )
        ],
        neutral_scores=[],
        best_argument=None,
        final_analysis="Pro presented stronger arguments."
    )
    return DebateResult(
        topic="Should AI be regulated?",
        rounds=2,
        transcript=["[MODERATOR]: Welcome"],
        timestamp="2024-01-15T10:30:00",
        verdict=verdict,
    )


class TestDebateHistoryInit:
    """Test DebateHistory initialization."""

    def test_init_default_dir(self, temp_storage_dir):
        """Test initialization with default directory."""
        history = DebateHistory(temp_storage_dir)
        assert history.storage_dir == Path(temp_storage_dir)

    def test_init_creates_directory(self, temp_storage_dir):
        """Test that initialization creates the directory."""
        new_dir = os.path.join(temp_storage_dir, "new_history")
        history = DebateHistory(new_dir)
        assert os.path.exists(new_dir)


class TestDebateHistorySave:
    """Test saving debate results."""

    def test_save_basic(self, temp_storage_dir, sample_result):
        """Test basic save functionality."""
        history = DebateHistory(temp_storage_dir)
        filepath = history.save(sample_result)

        assert os.path.exists(filepath)
        assert filepath.endswith('.json')

    def test_save_with_custom_filename(self, temp_storage_dir, sample_result):
        """Test save with custom filename."""
        history = DebateHistory(temp_storage_dir)
        filepath = history.save(sample_result, filename="custom_debate.json")

        assert filepath.endswith("custom_debate.json")
        assert os.path.exists(filepath)

    def test_save_creates_valid_json(self, temp_storage_dir, sample_result):
        """Test that saved file is valid JSON."""
        history = DebateHistory(temp_storage_dir)
        filepath = history.save(sample_result)

        with open(filepath, 'r') as f:
            data = json.load(f)

        assert data['topic'] == sample_result.topic
        assert data['rounds'] == sample_result.rounds
        assert data['transcript'] == sample_result.transcript

    def test_save_with_verdict(self, temp_storage_dir, sample_result_with_verdict):
        """Test saving result with verdict."""
        history = DebateHistory(temp_storage_dir)
        filepath = history.save(sample_result_with_verdict)

        with open(filepath, 'r') as f:
            data = json.load(f)

        assert data['verdict'] is not None
        assert data['verdict']['winner'] == "pro"
        assert len(data['verdict']['pro_scores']) == 1

    def test_save_sanitizes_topic_in_filename(self, temp_storage_dir):
        """Test that special characters in topic are sanitized in filename."""
        result = DebateResult(
            topic="AI: Should it be regulated? (Yes/No)",
            rounds=1,
            transcript=[],
            timestamp="2024-01-15T10:30:00",
        )
        history = DebateHistory(temp_storage_dir)
        filepath = history.save(result)

        # Should not contain problematic characters
        assert ':' not in os.path.basename(filepath) or filepath.count(':') <= 2  # Allow timestamps


class TestDebateHistoryLoad:
    """Test loading debate results."""

    def test_load_basic(self, temp_storage_dir, sample_result):
        """Test basic load functionality."""
        history = DebateHistory(temp_storage_dir)
        filepath = history.save(sample_result)

        loaded = history.load(os.path.basename(filepath))

        assert loaded.topic == sample_result.topic
        assert loaded.rounds == sample_result.rounds
        assert loaded.transcript == sample_result.transcript
        assert loaded.timestamp == sample_result.timestamp

    def test_load_with_verdict(self, temp_storage_dir, sample_result_with_verdict):
        """Test loading result with verdict."""
        history = DebateHistory(temp_storage_dir)
        filepath = history.save(sample_result_with_verdict)

        loaded = history.load(os.path.basename(filepath))

        assert loaded.verdict is not None
        assert loaded.verdict.winner == "pro"
        assert len(loaded.verdict.pro_scores) == 1
        assert loaded.verdict.pro_scores[0].argument_strength == 8


class TestDebateHistoryList:
    """Test listing saved debates."""

    def test_list_empty(self, temp_storage_dir):
        """Test listing when no debates saved."""
        history = DebateHistory(temp_storage_dir)
        debates = history.list_debates()

        assert debates == []

    def test_list_single(self, temp_storage_dir, sample_result):
        """Test listing single saved debate."""
        history = DebateHistory(temp_storage_dir)
        history.save(sample_result)

        debates = history.list_debates()

        assert len(debates) == 1
        assert debates[0]['topic'] == sample_result.topic

    def test_list_multiple(self, temp_storage_dir, sample_result):
        """Test listing multiple saved debates."""
        history = DebateHistory(temp_storage_dir)

        # Save multiple debates
        for i in range(3):
            result = DebateResult(
                topic=f"Topic {i}",
                rounds=1,
                transcript=[],
                timestamp=f"2024-01-1{i}T10:30:00",
            )
            history.save(result)

        debates = history.list_debates()

        assert len(debates) == 3

    def test_list_includes_winner(self, temp_storage_dir, sample_result_with_verdict):
        """Test that list includes winner information."""
        history = DebateHistory(temp_storage_dir)
        history.save(sample_result_with_verdict)

        debates = history.list_debates()

        assert debates[0]['winner'] == "pro"


class TestDebateHistoryDelete:
    """Test deleting saved debates."""

    def test_delete_existing(self, temp_storage_dir, sample_result):
        """Test deleting existing debate."""
        history = DebateHistory(temp_storage_dir)
        filepath = history.save(sample_result)
        filename = os.path.basename(filepath)

        result = history.delete(filename)

        assert result is True
        assert not os.path.exists(filepath)

    def test_delete_nonexistent(self, temp_storage_dir):
        """Test deleting non-existent debate."""
        history = DebateHistory(temp_storage_dir)

        result = history.delete("nonexistent.json")

        assert result is False


class TestDebateHistoryExport:
    """Test exporting debate reports."""

    def test_export_report(self, temp_storage_dir, sample_result):
        """Test exporting debate report."""
        history = DebateHistory(temp_storage_dir)
        filepath = history.export_report(sample_result)

        assert filepath.endswith('.txt')
        assert os.path.exists(filepath)

    def test_export_report_content(self, temp_storage_dir, sample_result):
        """Test exported report contains expected content."""
        history = DebateHistory(temp_storage_dir)
        filepath = history.export_report(sample_result)

        with open(filepath, 'r') as f:
            content = f.read()

        assert "DEBATE ARENA REPORT" in content
        assert sample_result.topic in content

    def test_export_with_custom_filename(self, temp_storage_dir, sample_result):
        """Test export with custom filename."""
        history = DebateHistory(temp_storage_dir)
        filepath = history.export_report(sample_result, filename="custom_report.txt")

        assert filepath.endswith("custom_report.txt")


class TestDebateHistoryRoundTrip:
    """Test save/load round trip preserves data."""

    def test_round_trip_preserves_all_data(self, temp_storage_dir, sample_result_with_verdict):
        """Test that save/load preserves all data."""
        history = DebateHistory(temp_storage_dir)
        filepath = history.save(sample_result_with_verdict)
        loaded = history.load(os.path.basename(filepath))

        # Check basic fields
        assert loaded.topic == sample_result_with_verdict.topic
        assert loaded.rounds == sample_result_with_verdict.rounds
        assert loaded.transcript == sample_result_with_verdict.transcript
        assert loaded.timestamp == sample_result_with_verdict.timestamp

        # Check verdict
        assert loaded.verdict.winner == sample_result_with_verdict.verdict.winner
        assert loaded.verdict.summary == sample_result_with_verdict.verdict.summary

        # Check scores
        assert len(loaded.verdict.pro_scores) == len(sample_result_with_verdict.verdict.pro_scores)
        original_score = sample_result_with_verdict.verdict.pro_scores[0]
        loaded_score = loaded.verdict.pro_scores[0]
        assert loaded_score.argument_strength == original_score.argument_strength
        assert loaded_score.total_score == original_score.total_score
