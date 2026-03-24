"""Arena module - coordinates the entire debate process."""

from typing import Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime

from debate_arena.core.debater import Debater, Stance, Argument, DEFAULT_PERSONAS
from debate_arena.core.moderator import Moderator
from debate_arena.core.judge import Judge, DebateVerdict


@dataclass
class DebateResult:
    """Result of a completed debate."""
    topic: str
    rounds: int
    transcript: list[str] = field(default_factory=list)
    verdict: Optional[DebateVerdict] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def report(self) -> str:
        """Generate a formatted report of the debate."""
        lines = [
            "=" * 80,
            f"DEBATE ARENA REPORT",
            "=" * 80,
            f"Topic: {self.topic}",
            f"Rounds: {self.rounds}",
            f"Date: {self.timestamp}",
            "=" * 80,
            "",
            "TRANSCRIPT",
            "-" * 80,
        ]

        for entry in self.transcript:
            lines.append(entry)
            lines.append("")

        if self.verdict:
            lines.extend([
                "",
                "=" * 80,
                "VERDICT",
                "=" * 80,
                self.verdict.summary,
            ])

            if self.verdict.best_argument:
                lines.extend([
                    "",
                    "BEST ARGUMENT:",
                    f"Score: {self.verdict.best_argument.total_score}/10",
                    f"{self.verdict.best_argument.content[:200]}...",
                ])

            lines.extend([
                "",
                "FINAL ANALYSIS:",
                self.verdict.final_analysis,
            ])

        lines.append("=" * 80)
        return "\n".join(lines)


class Arena:
    """Main arena that orchestrates the entire debate."""

    def __init__(
        self,
        topic: str,
        rounds: int = 3,
        api_key: Optional[str] = None,
        model: str = "claude-3-7-sonnet-20250219",
        on_progress: Optional[Callable[[str], None]] = None,
    ):
        """Initialize the arena.

        Args:
            topic: The debate topic/question
            rounds: Number of debate rounds
            api_key: Anthropic API key
            model: Claude model to use
            on_progress: Optional callback for progress updates
        """
        self.topic = topic
        self.rounds = rounds
        self.api_key = api_key
        self.model = model
        self.on_progress = on_progress

        # Initialize components
        self.moderator = Moderator(model=model, api_key=api_key)
        self.judge = Judge(model=model, api_key=api_key)

        # Create debaters
        self.debaters = [
            Debater(Stance.PRO, model=model, api_key=api_key),
            Debater(Stance.CON, model=model, api_key=api_key),
        ]

        # Track debate state
        self.transcript: list[str] = []
        self.arguments_by_stance: dict[Stance, list[Argument]] = {
            Stance.PRO: [],
            Stance.CON: []
        }

    def _log(self, message: str) -> None:
        """Add a message to the transcript and optionally call progress callback."""
        self.transcript.append(message)
        if self.on_progress:
            self.on_progress(message)

    def run(self) -> DebateResult:
        """Run the complete debate.

        Returns:
            DebateResult with transcript and verdict
        """
        # Phase 1: Opening
        self._log(f"\n{'='*60}\nDEBATE BEGINS\n{'='*60}\n")
        opening = self.moderator.open_debate(self.topic, self.debaters)
        self._log(f"[MODERATOR]:\n{opening}\n")

        # Phase 2: Opening statements
        for debater in self.debaters:
            statement = debater.generate_opening_statement(self.topic)
            self._log(f"[{debater.persona.name} ({debater.stance.value.upper()})]:\n{statement.content}\n")
            self.arguments_by_stance[debater.stance].append(statement)

        # Phase 3: Debate rounds
        for round_num in range(1, self.rounds + 1):
            self._log(f"\n{'-'*60}\nROUND {round_num}\n{'-'*60}\n")

            round_args = []

            # Each debater responds to the other's arguments
            for debater in self.debaters:
                opponent_stance = Stance.CON if debater.stance == Stance.PRO else Stance.PRO
                opponent_args = self.arguments_by_stance[opponent_stance]

                rebuttal = debater.generate_rebuttal(
                    self.topic,
                    opponent_args,
                    round_num,
                )
                self._log(f"[{debater.persona.name} ({debater.stance.value.upper()})]:\n{rebuttal.content}\n")
                self.arguments_by_stance[debater.stance].append(rebuttal)
                round_args.append(rebuttal)

            # Moderator summarizes the round
            summary = self.moderator.summarize_round(self.topic, round_num, round_args)
            self._log(f"\n[MODERATOR SUMMARY]:\n{summary}\n")

        # Phase 4: Closing statements
        self._log(f"\n{'-'*60}\nCLOSING STATEMENTS\n{'-'*60}\n")

        for debater in self.debaters:
            closing = debater.generate_closing_statement(
                self.topic,
                self.arguments_by_stance[debater.stance],
                self.arguments_by_stance[Stance.CON if debater.stance == Stance.PRO else Stance.PRO],
            )
            self._log(f"[{debater.persona.name} ({debater.stance.value.upper()})]:\n{closing.content}\n")

        # Phase 5: Moderator closes debate
        closing_remarks = self.moderator.close_debate(
            self.topic,
            self.arguments_by_stance[Stance.PRO] + self.arguments_by_stance[Stance.CON],
        )
        self._log(f"\n[MODERATOR]:\n{closing_remarks}\n")

        # Phase 6: Judge renders verdict
        self._log(f"\n{'='*60}\nJUDGE'S VERDICT\n{'='*60}\n")

        verdict = self.judge.render_verdict(
            self.topic,
            self.arguments_by_stance[Stance.PRO],
            self.arguments_by_stance[Stance.CON],
        )

        winner_text = {
            "pro": "PRO WINS",
            "con": "CON WINS",
            None: "TIE",
        }.get(verdict.winner, "INCONCLUSIVE")

        self._log(f"RESULT: {winner_text}\n")
        self._log(f"Score Summary: {verdict.summary}\n")
        self._log(f"\nFINAL ANALYSIS:\n{verdict.final_analysis}\n")

        return DebateResult(
            topic=self.topic,
            rounds=self.rounds,
            transcript=self.transcript,
            verdict=verdict,
        )
