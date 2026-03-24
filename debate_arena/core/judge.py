"""Judge module - evaluates argument quality and debate outcomes."""

from typing import Optional, Dict
from dataclasses import dataclass, field
from anthropic import Anthropic
from anthropic.types import TextBlock
from debate_arena.core.debater import Argument, Stance


import math


def _extract_text(content_blocks: list) -> str:
    """Extract text from API response content blocks.

    Args:
        content_blocks: List of content blocks from API response

    Returns:
        The text content from the first TextBlock, or empty string
    """
    for block in content_blocks:
        if isinstance(block, TextBlock):
            return block.text
    return ""


# Default scoring weights (must sum to 1.0)
DEFAULT_WEIGHTS = {
    'argument_strength': 0.30,
    'evidence_quality': 0.25,
    'logical_consistency': 0.25,
    'clarity': 0.20,
}


@dataclass
class ScoringWeights:
    """Weights for scoring criteria."""
    argument_strength: float = 0.30
    evidence_quality: float = 0.25
    logical_consistency: float = 0.25
    clarity: float = 0.20

    def __post_init__(self):
        """Validate weights sum to approximately 1.0."""
        total = self.argument_strength + self.evidence_quality + self.logical_consistency + self.clarity
        if not math.isclose(total, 1.0, rel_tol=0.01):
            raise ValueError(f"Weights must sum to 1.0, got {total}")

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'argument_strength': self.argument_strength,
            'evidence_quality': self.evidence_quality,
            'logical_consistency': self.logical_consistency,
            'clarity': self.clarity,
        }

    @classmethod
    def default(cls) -> 'ScoringWeights':
        """Create default weights."""
        return cls()

    @classmethod
    def evidence_focused(cls) -> 'ScoringWeights':
        """Weights emphasizing evidence quality."""
        return cls(
            argument_strength=0.20,
            evidence_quality=0.40,
            logical_consistency=0.25,
            clarity=0.15,
        )

    @classmethod
    def logic_focused(cls) -> 'ScoringWeights':
        """Weights emphasizing logical consistency."""
        return cls(
            argument_strength=0.25,
            evidence_quality=0.20,
            logical_consistency=0.40,
            clarity=0.15,
        )

    @classmethod
    def balanced(cls) -> 'ScoringWeights':
        """Equal weights for all criteria."""
        return cls(
            argument_strength=0.25,
            evidence_quality=0.25,
            logical_consistency=0.25,
            clarity=0.25,
        )


@dataclass
class ArgumentScore:
    """Score for a single argument."""
    content: str
    argument_strength: int  # 1-10
    evidence_quality: int   # 1-10
    logical_consistency: int # 1-10
    clarity: int            # 1-10
    total_score: int        # 1-10 average
    reasoning: str
    weighted_score: Optional[float] = None  # Score using custom weights


@dataclass
class DebateVerdict:
    """Final verdict on the debate."""
    topic: str
    winner: Optional[str]  # "pro", "con", "neutral", or None for tie
    summary: str
    pro_scores: list[ArgumentScore] = field(default_factory=list)
    con_scores: list[ArgumentScore] = field(default_factory=list)
    neutral_scores: list[ArgumentScore] = field(default_factory=list)
    best_argument: Optional[ArgumentScore] = None
    final_analysis: str = ""


class Judge:
    """Judge that evaluates debate arguments and provides verdict."""

    def __init__(
        self,
        model: str = "claude-3-7-sonnet-20250219",
        api_key: Optional[str] = None,
        scoring_weights: Optional[ScoringWeights] = None,
    ):
        """Initialize the judge.

        Args:
            model: Claude model to use
            api_key: Anthropic API key
            scoring_weights: Custom weights for scoring criteria
        """
        self.model = model
        self.client = Anthropic(api_key=api_key)
        self.scoring_weights = scoring_weights or ScoringWeights.balanced()

    def set_scoring_weights(self, weights: ScoringWeights) -> None:
        """Set custom scoring weights.

        Args:
            weights: The new scoring weights to use
        """
        self.scoring_weights = weights

    def get_scoring_weights(self) -> ScoringWeights:
        """Get current scoring weights.

        Returns:
            Current scoring weights
        """
        return self.scoring_weights

    def evaluate_argument(self, argument: Argument) -> ArgumentScore:
        """Evaluate a single argument.

        Args:
            argument: The argument to evaluate

        Returns:
            An ArgumentScore with detailed ratings
        """
        prompt = f"""You are an impartial debate judge. Evaluate the following argument on the criteria below.

**Topic context:** This is a debate where the speaker is {argument.stance.value} the topic.

**Argument by {argument.debater_name}:**
{argument.content}

Please rate this argument on the following scales (1-10):

1. **Argument Strength:** How persuasive and well-reasoned is the core claim?
2. **Evidence Quality:** Does the argument support claims with facts, data, or logical reasoning?
3. **Logical Consistency:** Is the reasoning sound and free of fallacies?
4. **Clarity:** Is the argument clearly articulated and easy to follow?

Provide your response in this exact format:

ARGUMENT_STRENGTH: [1-10]
EVIDENCE_QUALITY: [1-10]
LOGICAL_CONSISTENCY: [1-10]
CLARITY: [1-10]
TOTAL: [average of above]
REASONING: [2-3 sentences explaining your rating]"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        result = _extract_text(response.content)
        return self._parse_score(argument.content, result)

    def render_verdict(
        self,
        topic: str,
        pro_arguments: list[Argument],
        con_arguments: list[Argument],
        neutral_arguments: Optional[list[Argument]] = None,
    ) -> DebateVerdict:
        """Render a final verdict on the debate.

        Args:
            topic: The debate topic
            pro_arguments: All arguments from pro side
            con_arguments: All arguments from con side

        Returns:
            A DebateVerdict with comprehensive analysis
        """
        # Score all arguments
        pro_scores = [self.evaluate_argument(arg) for arg in pro_arguments]
        con_scores = [self.evaluate_argument(arg) for arg in con_arguments]
        neutral_scores = [self.evaluate_argument(arg) for arg in (neutral_arguments or [])]

        # Find best argument
        all_scores = pro_scores + con_scores + neutral_scores
        best_argument = max(all_scores, key=lambda s: s.total_score) if all_scores else None

        # Determine winner
        pro_avg = sum(s.total_score for s in pro_scores) / len(pro_scores) if pro_scores else 0
        con_avg = sum(s.total_score for s in con_scores) / len(con_scores) if con_scores else 0

        if pro_avg > con_avg + 0.5:
            winner = "pro"
        elif con_avg > pro_avg + 0.5:
            winner = "con"
        else:
            winner = None  # Tie

        # Generate final analysis
        analysis = self._generate_final_analysis(
            topic, pro_scores, con_scores, winner
        )

        return DebateVerdict(
            topic=topic,
            winner=winner,
            summary=f"Pro average: {pro_avg:.1f}/10, Con average: {con_avg:.1f}/10",
            pro_scores=pro_scores,
            con_scores=con_scores,
            neutral_scores=neutral_scores,
            best_argument=best_argument,
            final_analysis=analysis,
        )

    def _parse_score(self, content: str, response: str) -> ArgumentScore:
        """Parse the scoring response into an ArgumentScore."""
        # Extract values from structured response
        values = {}
        for line in response.split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                values[key.strip().lower()] = val.strip()

        def get_val(key: str, default: int = 5) -> int:
            for k in [key, key.replace('_', ' ')]:
                if k.lower() in values:
                    try:
                        return int(values[k.lower()])
                    except (ValueError, IndexError):
                        pass
            return default

        argument_strength = get_val('argument_strength', 5)
        evidence_quality = get_val('evidence_quality', 5)
        logical_consistency = get_val('logical_consistency', 5)
        clarity = get_val('clarity', 5)
        total = get_val('total', (argument_strength + evidence_quality + logical_consistency + clarity) // 4)
        reasoning = values.get('reasoning', 'No reasoning provided.')

        return ArgumentScore(
            content=content,
            argument_strength=argument_strength,
            evidence_quality=evidence_quality,
            logical_consistency=logical_consistency,
            clarity=clarity,
            total_score=total,
            reasoning=reasoning,
        )

    def _generate_final_analysis(
        self,
        topic: str,
        pro_scores: list[ArgumentScore],
        con_scores: list[ArgumentScore],
        winner: Optional[str],
    ) -> str:
        """Generate the final analysis text."""
        pro_avg = sum(s.total_score for s in pro_scores) / len(pro_scores) if pro_scores else 0
        con_avg = sum(s.total_score for s in con_scores) / len(con_scores) if con_scores else 0

        winner_text = {
            "pro": "The PRO side has presented a more compelling case.",
            "con": "The CON side has presented a more compelling case.",
            None: "The debate is effectively tied—both sides presented equally strong arguments.",
        }.get(winner, "The debate is closely contested.")

        prompt = f"""You are the final judge for a debate on: "{topic}"

**Score Summary:**
- PRO side average: {pro_avg:.1f}/10
- CON side average: {con_avg:.1f}/10

**Assessment:** {winner_text}

Please provide a concise final analysis (3-4 paragraphs) that:
1. Identifies the strongest arguments from each side
2. Explains why the winning side prevailed (or why it was tied)
3. Acknowledges any areas where the losing side performed well
4. Concludes with key takeaways from this debate

Be balanced and objective in your assessment."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.5,
            messages=[{"role": "user", "content": prompt}]
        )

        return _extract_text(response.content)
