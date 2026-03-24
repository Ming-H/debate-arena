"""Moderator module - manages debate flow and decorum."""

from typing import Optional
from anthropic import Anthropic
from anthropic.types import TextBlock
from debate_arena.core.debater import Argument, Stance


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


class Moderator:
    """Moderator that controls the debate flow and maintains decorum."""

    def __init__(
        self,
        model: str = "claude-3-7-sonnet-20250219",
        api_key: Optional[str] = None,
    ):
        """Initialize the moderator.

        Args:
            model: Claude model to use
            api_key: Anthropic API key
        """
        self.model = model
        self.client = Anthropic(api_key=api_key)

    def open_debate(self, topic: str, debaters: list) -> str:
        """Generate an opening statement introducing the debate.

        Args:
            topic: The debate topic
            debaters: List of debaters participating

        Returns:
            Opening statement as a string
        """
        debater_descriptions = "\n".join([
            f"- {d.persona.name}: {d.persona.description} ({d.stance.value})"
            for d in debaters
        ])

        prompt = f"""You are the moderator of a formal debate. Please provide an opening statement that:

1. Introduces the debate topic clearly
2. Introduces the debaters and their positions
3. Sets expectations for respectful, substantive debate
4. Outlines the basic structure of the debate

Keep it concise but professional (2-3 paragraphs).

**Topic:** {topic}

**Debaters:**
{debater_descriptions}

Generate only the moderator's opening statement, with no additional commentary."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=800,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        return _extract_text(response.content)

    def summarize_round(
        self,
        topic: str,
        round_num: int,
        arguments: list[Argument],
    ) -> str:
        """Summarize the key points from a debate round.

        Args:
            topic: The debate topic
            round_num: Current round number
            arguments: Arguments made in this round

        Returns:
            Summary of the round
        """
        args_text = "\n\n".join([
            f"**{arg.debater_name}** ({arg.stance.value}):\n{arg.content}"
            for arg in arguments
        ])

        prompt = f"""You are the moderator of a debate on: "{topic}"

Round {round_num} has concluded with the following arguments:

{args_text}

Please provide:
1. A brief summary of the key points from each side
2. Any areas of agreement or disagreement that emerged
3. A transition to the next round (or to closing statements if debate is ending)

Keep it concise and balanced. Do not express your own opinion on the topic."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=800,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        return _extract_text(response.content)

    def close_debate(
        self,
        topic: str,
        all_arguments: list[Argument],
    ) -> str:
        """Provide closing remarks for the debate.

        Args:
            topic: The debate topic
            all_arguments: All arguments from the entire debate

        Returns:
            Closing remarks
        """
        # Count arguments by stance
        pro_count = sum(1 for a in all_arguments if a.stance == Stance.PRO)
        con_count = sum(1 for a in all_arguments if a.stance == Stance.CON)

        prompt = f"""You are the moderator of a debate on: "{topic}"

The debate has concluded with {pro_count} arguments from the pro side and {con_count} from the con side.

Please provide closing remarks that:
1. Thank the participants
2. Acknowledge the complexity of the topic
3. Note that both sides presented valid perspectives
4. Transition to the judge for final evaluation

Keep it brief and professional."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        return _extract_text(response.content)
