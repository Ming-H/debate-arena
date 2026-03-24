"""Debate history management module."""

import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from dataclasses import asdict

from debate_arena.core.arena import DebateResult
from debate_arena.core.judge import DebateVerdict, ArgumentScore


class DebateHistory:
    """Manages saving and loading debate history."""

    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize history manager.

        Args:
            storage_dir: Directory to store debate history files.
                        Defaults to 'debate_history' in current directory.
        """
        self.storage_dir = Path(storage_dir or "debate_history")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, result: DebateResult, filename: Optional[str] = None) -> str:
        """Save a debate result to file.

        Args:
            result: The DebateResult to save
            filename: Optional custom filename. If not provided, generates
                     one based on timestamp and topic.

        Returns:
            The path to the saved file
        """
        if filename is None:
            # Generate filename from timestamp and sanitized topic
            safe_topic = "".join(
                c if c.isalnum() or c in (' ', '-', '_') else '_'
                for c in result.topic
            )[:50]
            timestamp = result.timestamp.replace(':', '-').replace('.', '-')
            filename = f"debate_{timestamp}_{safe_topic}.json"

        filepath = self.storage_dir / filename

        # Convert to serializable format
        data = self._serialize_result(result)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def load(self, filename: str) -> DebateResult:
        """Load a debate result from file.

        Args:
            filename: The filename to load from

        Returns:
            The loaded DebateResult
        """
        filepath = self.storage_dir / filename

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return self._deserialize_result(data)

    def list_debates(self) -> List[dict]:
        """List all saved debates with metadata.

        Returns:
            List of dicts with 'filename', 'topic', 'timestamp', 'winner'
        """
        debates = []
        for filepath in sorted(self.storage_dir.glob("debate_*.json"), reverse=True):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                debates.append({
                    'filename': filepath.name,
                    'topic': data.get('topic', 'Unknown'),
                    'timestamp': data.get('timestamp', 'Unknown'),
                    'winner': data.get('verdict', {}).get('winner', 'N/A') if data.get('verdict') else 'N/A',
                })
            except (json.JSONDecodeError, KeyError):
                continue
        return debates

    def delete(self, filename: str) -> bool:
        """Delete a saved debate.

        Args:
            filename: The filename to delete

        Returns:
            True if deleted, False if file didn't exist
        """
        filepath = self.storage_dir / filename
        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def _serialize_result(self, result: DebateResult) -> dict:
        """Serialize DebateResult to dict."""
        data = {
            'topic': result.topic,
            'rounds': result.rounds,
            'transcript': result.transcript,
            'timestamp': result.timestamp,
            'verdict': None,
        }

        if result.verdict:
            data['verdict'] = self._serialize_verdict(result.verdict)

        return data

    def _serialize_verdict(self, verdict: DebateVerdict) -> dict:
        """Serialize DebateVerdict to dict."""
        return {
            'topic': verdict.topic,
            'winner': verdict.winner,
            'summary': verdict.summary,
            'pro_scores': [self._serialize_score(s) for s in verdict.pro_scores],
            'con_scores': [self._serialize_score(s) for s in verdict.con_scores],
            'neutral_scores': [self._serialize_score(s) for s in verdict.neutral_scores],
            'best_argument': self._serialize_score(verdict.best_argument) if verdict.best_argument else None,
            'final_analysis': verdict.final_analysis,
        }

    def _serialize_score(self, score: ArgumentScore) -> dict:
        """Serialize ArgumentScore to dict."""
        return {
            'content': score.content,
            'argument_strength': score.argument_strength,
            'evidence_quality': score.evidence_quality,
            'logical_consistency': score.logical_consistency,
            'clarity': score.clarity,
            'total_score': score.total_score,
            'reasoning': score.reasoning,
        }

    def _deserialize_result(self, data: dict) -> DebateResult:
        """Deserialize dict to DebateResult."""
        verdict = None
        if data.get('verdict'):
            verdict = self._deserialize_verdict(data['verdict'])

        return DebateResult(
            topic=data['topic'],
            rounds=data['rounds'],
            transcript=data['transcript'],
            timestamp=data['timestamp'],
            verdict=verdict,
        )

    def _deserialize_verdict(self, data: dict) -> DebateVerdict:
        """Deserialize dict to DebateVerdict."""
        return DebateVerdict(
            topic=data['topic'],
            winner=data['winner'],
            summary=data['summary'],
            pro_scores=[self._deserialize_score(s) for s in data.get('pro_scores', [])],
            con_scores=[self._deserialize_score(s) for s in data.get('con_scores', [])],
            neutral_scores=[self._deserialize_score(s) for s in data.get('neutral_scores', [])],
            best_argument=self._deserialize_score(data['best_argument']) if data.get('best_argument') else None,
            final_analysis=data.get('final_analysis', ''),
        )

    def _deserialize_score(self, data: dict) -> ArgumentScore:
        """Deserialize dict to ArgumentScore."""
        return ArgumentScore(
            content=data['content'],
            argument_strength=data['argument_strength'],
            evidence_quality=data['evidence_quality'],
            logical_consistency=data['logical_consistency'],
            clarity=data['clarity'],
            total_score=data['total_score'],
            reasoning=data['reasoning'],
        )

    def export_report(self, result: DebateResult, filename: Optional[str] = None) -> str:
        """Export debate result as a readable text report.

        Args:
            result: The DebateResult to export
            filename: Optional custom filename

        Returns:
            The path to the exported file
        """
        if filename is None:
            safe_topic = "".join(
                c if c.isalnum() or c in (' ', '-', '_') else '_'
                for c in result.topic
            )[:50]
            timestamp = result.timestamp.replace(':', '-').replace('.', '-')
            filename = f"report_{timestamp}_{safe_topic}.txt"

        filepath = self.storage_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(result.report)

        return str(filepath)
