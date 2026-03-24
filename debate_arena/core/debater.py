"""Debater module - AI agents with specific stances."""

from enum import Enum
from typing import Optional
from dataclasses import dataclass, field
from anthropic import Anthropic
from anthropic.types import TextBlock


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


class Stance(Enum):
    """Debate stance positions."""
    PRO = "pro"           # Supporting the proposition
    CON = "con"           # Opposing the proposition
    NEUTRAL = "neutral"   # Neutral/mediator position


@dataclass
class Persona:
    """Persona configuration for a debater."""
    name: str
    description: str
    background: str
    argument_style: str


# Default personas
DEFAULT_PERSONAS = {
    "pro": Persona(
        name="Dr. Sarah Chen",
        description="A technology optimist who believes in progressive innovation",
        background="PhD in Computer Science, former AI researcher at leading tech company",
        argument_style="Uses technical examples, forward-looking arguments, and data-driven reasoning"
    ),
    "con": Persona(
        name="Prof. Marcus Webb",
        description="A cautious ethicist focused on societal implications",
        background="PhD in Philosophy, director of an AI ethics research institute",
        argument_style="Uses historical analogies, ethical frameworks, and precautionary principle"
    ),
    "neutral": Persona(
        name="Dr. Alex Morgan",
        description="A balanced analyst who considers multiple perspectives",
        background="PhD in Political Science, independent policy researcher",
        argument_style="Presents balanced analysis, weighs pros and cons, avoids strong bias"
    ),
}


@dataclass
class Argument:
    """A single argument made by a debater."""
    content: str
    stance: Stance
    debater_name: str
    round_num: int
    is_rebuttal: bool = False
    target_stance: Optional[Stance] = None


class Debater:
    """AI debater with a specific stance on a topic."""

    def __init__(
        self,
        stance: Stance,
        persona: Optional[Persona] = None,
        model: str = "claude-3-7-sonnet-20250219",
        api_key: Optional[str] = None,
    ):
        """Initialize a debater.

        Args:
            stance: The debater's position on the topic
            persona: Optional persona configuration
            model: Claude model to use
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.stance = stance
        self.persona = persona or DEFAULT_PERSONAS[stance.value]
        self.model = model
        self.client = Anthropic(api_key=api_key)

    def generate_opening_statement(self, topic: str) -> Argument:
        """Generate an opening statement for the debate.

        Args:
            topic: The debate topic/question

        Returns:
            An Argument containing the opening statement
        """
        prompt = self._build_opening_prompt(topic)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            temperature=0.8,
            messages=[{"role": "user", "content": prompt}]
        )

        content = _extract_text(response.content)

        return Argument(
            content=content,
            stance=self.stance,
            debater_name=self.persona.name,
            round_num=1,
            is_rebuttal=False,
        )

    def generate_rebuttal(
        self,
        topic: str,
        opponent_arguments: list[Argument],
        round_num: int,
    ) -> Argument:
        """Generate a rebuttal to opponent's arguments.

        Args:
            topic: The debate topic/question
            opponent_arguments: List of arguments to respond to
            round_num: Current debate round

        Returns:
            An Argument containing the rebuttal
        """
        prompt = self._build_rebuttal_prompt(topic, opponent_arguments, round_num)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            temperature=0.8,
            messages=[{"role": "user", "content": prompt}]
        )

        content = _extract_text(response.content)

        # Determine which stance we're rebutting
        target_stance = opponent_arguments[0].stance if opponent_arguments else None

        return Argument(
            content=content,
            stance=self.stance,
            debater_name=self.persona.name,
            round_num=round_num,
            is_rebuttal=True,
            target_stance=target_stance,
        )

    def generate_closing_statement(
        self,
        topic: str,
        my_arguments: list[Argument],
        opponent_arguments: list[Argument],
    ) -> Argument:
        """Generate a closing statement.

        Args:
            topic: The debate topic/question
            my_arguments: List of arguments made by this debater
            opponent_arguments: List of arguments made by opponents

        Returns:
            An Argument containing the closing statement
        """
        prompt = self._build_closing_prompt(topic, my_arguments, opponent_arguments)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        content = _extract_text(response.content)

        return Argument(
            content=content,
            stance=self.stance,
            debater_name=self.persona.name,
            round_num=999,  # Special value for closing
            is_rebuttal=False,
        )

    def _build_opening_prompt(self, topic: str) -> str:
        """Build the prompt for generating an opening statement."""
        stance_text = {
            Stance.PRO: "in support of",
            Stance.CON: "in opposition to",
            Stance.NEUTRAL: "regarding",
        }[self.stance]

        return f"""You are {self.persona.name}. {self.persona.background}.

Your argument style: {self.persona.argument_style}

You are participating in a formal debate {stance_text} the following topic:

**Topic:** {topic}

Please deliver an opening statement (2-3 paragraphs) that:
1. Clearly states your position on the topic
2. Presents 2-3 strong initial arguments
3. Sets the tone for the debate

Be persuasive but respectful. Focus on substance over rhetoric."""

    def _build_rebuttal_prompt(
        self,
        topic: str,
        opponent_arguments: list[Argument],
        round_num: int,
    ) -> str:
        """Build the prompt for generating a rebuttal."""
        stance_text = {
            Stance.PRO: "supporting",
            Stance.CON: "opposing",
        }[self.stance]

        args_text = "\n\n".join([
            f"**{arg.debater_name} (Round {arg.round_num}):**\n{arg.content}"
            for arg in opponent_arguments
        ])

        return f"""You are {self.persona.name}. You are {stance_text} the topic: "{topic}"

Your opponents have made the following arguments:

{args_text}

Please provide a rebuttal that:
1. Directly addresses the strongest points made by your opponents
2. Reinforces your original position with new evidence or reasoning
3. Identifies any logical fallacies or weaknesses in their arguments
4. Maintains a respectful and constructive tone

Focus on the most significant points—quality over quantity."""

    def _build_closing_prompt(
        self,
        topic: str,
        my_arguments: list[Argument],
        opponent_arguments: list[Argument],
    ) -> str:
        """Build the prompt for generating a closing statement."""
        stance_text = {
            Stance.PRO: "in favor of",
            Stance.CON: "against",
        }[self.stance]

        return f"""You are {self.persona.name}. You have been debating {stance_text}: "{topic}"

The debate is concluding. Please provide a closing statement that:
1. Summarizes your 2-3 strongest arguments from the debate
2. Explains why your position remains the most compelling
3. Acknowledges valid points made by opponents (if any)
4. Ends with a strong, memorable conclusion

This is your final statement—make it count. Be concise but impactful."""
