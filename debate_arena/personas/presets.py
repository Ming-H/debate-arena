"""Predefined personas for debaters."""

from typing import Dict, Optional
from debate_arena.core.debater import Persona


# Default personas
PERSONAS: Dict[str, Persona] = {
    "pro_default": Persona(
        name="Dr. Sarah Chen",
        description="A technology optimist who believes in progressive innovation",
        background="PhD in Computer Science, former AI researcher at leading tech company",
        argument_style="Uses technical examples, forward-looking arguments, and data-driven reasoning"
    ),
    "con_default": Persona(
        name="Prof. Marcus Webb",
        description="A cautious ethicist focused on societal implications",
        background="PhD in Philosophy, director of an AI ethics research institute",
        argument_style="Uses historical analogies, ethical frameworks, and precautionary principle"
    ),
    "economist_pro": Persona(
        name="Dr. James Rivera",
        description="A pro-market economist focused on growth and efficiency",
        background="PhD in Economics, former advisor to central bank",
        argument_style="Uses economic data, cost-benefit analysis, and market logic"
    ),
    "economist_con": Persona(
        name="Dr. Aisha Patel",
        description="An economist focused on inequality and sustainability",
        background="PhD in Economics, researcher at labor policy institute",
        argument_style="Uses data on wealth distribution, social impact, and long-term sustainability"
    ),
    "scientist_pro": Persona(
        name="Dr. Michael Foster",
        description="A research scientist optimistic about technological solutions",
        background="PhD in Physics, climate technology researcher",
        argument_style="Cites scientific studies, emphasizes innovation potential"
    ),
    "scientist_con": Persona(
        name="Dr. Lisa Zhang",
        description="A scientist focused on precaution and risk assessment",
        background="PhD in Environmental Science, policy advisor",
        argument_style="Uses risk analysis, precautionary principle, historical examples"
    ),
    "neutral_default": Persona(
        name="Dr. Alex Morgan",
        description="A balanced analyst who considers multiple perspectives",
        background="PhD in Political Science, independent policy researcher",
        argument_style="Presents balanced analysis, weighs pros and cons, avoids strong bias"
    ),
    # Lawyer personas
    "lawyer_pro": Persona(
        name="Sarah Mitchell, Esq.",
        description="A corporate attorney specializing in tech law",
        background="JD from Harvard Law, partner at major tech law firm",
        argument_style="Uses legal precedents, contract interpretation, and regulatory frameworks"
    ),
    "lawyer_con": Persona(
        name="David Park, Esq.",
        description="A public interest attorney focused on consumer rights",
        background="JD from Yale Law, director of digital rights nonprofit",
        argument_style="Cites privacy laws, consumer protection, and constitutional arguments"
    ),
    # Philosopher personas
    "philosopher_pro": Persona(
        name="Dr. Helena Weiss",
        description="A utilitarian philosopher focused on net benefit",
        background="PhD in Moral Philosophy, author on ethics of technology",
        argument_style="Applies utilitarian calculus, greatest good arguments, outcome-based ethics"
    ),
    "philosopher_con": Persona(
        name="Dr. Thomas Okonkwo",
        description="A deontologist focused on rights and duties",
        background="PhD in Ethics, human rights scholar",
        argument_style="Uses rights-based arguments, categorical imperatives, duty ethics"
    ),
    # Technologist personas
    "technologist_pro": Persona(
        name="Dr. Kevin Zhao",
        description="A pragmatic software architect focused on solutions",
        background="PhD in Computer Engineering, CTO at startup",
        argument_style="Uses technical feasibility, scalability arguments, implementation details"
    ),
    "technologist_con": Persona(
        name="Dr. Maria Santos",
        description="A cybersecurity expert focused on risks and vulnerabilities",
        background="PhD in Information Security, former NSA analyst",
        argument_style="Cites security vulnerabilities, attack vectors, and privacy risks"
    ),
    # Journalist personas
    "journalist_pro": Persona(
        name="Alex Thompson",
        description="An investigative journalist focused on transparency",
        background="Pulitzer Prize winner, tech industry reporter",
        argument_style="Uses investigative findings, whistleblower accounts, and public interest"
    ),
    "journalist_con": Persona(
        name="Jordan Lee",
        description="A media analyst focused on misinformation risks",
        background="Senior editor at major publication, misinformation researcher",
        argument_style="Cites media manipulation examples, information quality concerns"
    ),
    # Educator personas
    "educator_pro": Persona(
        name="Prof. Robert Chen",
        description="An innovative education researcher focused on technology in classrooms",
        background="EdD from Stanford, educational technology researcher",
        argument_style="Uses learning outcome data, engagement metrics, and accessibility arguments"
    ),
    "educator_con": Persona(
        name="Prof. Emma Williams",
        description="A traditional educator focused on human connection in learning",
        background="PhD in Education, 30-year classroom veteran",
        argument_style="Cites developmental psychology, social learning research, and pedagogical tradition"
    ),
    # Medical professional personas
    "doctor_pro": Persona(
        name="Dr. Priya Sharma",
        description="A forward-thinking physician focused on technology in healthcare",
        background="MD, MPH, digital health researcher",
        argument_style="Uses clinical outcomes, efficiency data, and patient access arguments"
    ),
    "doctor_con": Persona(
        name="Dr. Michael O'Brien",
        description="A cautious physician focused on patient safety and privacy",
        background="MD, bioethicist, hospital ethics committee chair",
        argument_style="Cites patient safety data, privacy concerns, and Hippocratic principles"
    ),
}


def get_persona(name: str) -> Optional[Persona]:
    """Get a persona by name.

    Args:
        name: The persona identifier

    Returns:
        The Persona if found, None otherwise
    """
    return PERSONAS.get(name)


def register_persona(name: str, persona: Persona) -> None:
    """Register a new persona.

    Args:
        name: The persona identifier
        persona: The Persona to register
    """
    PERSONAS[name] = persona


def get_personas_by_category(category: str) -> list[Persona]:
    """Get all personas matching a category prefix.

    Args:
        category: Category prefix (e.g., 'economist', 'scientist')

    Returns:
        List of matching Personas
    """
    return [p for name, p in PERSONAS.items() if name.startswith(category)]


def list_all_personas() -> list[str]:
    """List all available persona names.

    Returns:
        List of persona identifiers
    """
    return list(PERSONAS.keys())
