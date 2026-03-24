"""Tests for Personas functionality."""

import pytest
from debate_arena.personas import PERSONAS, get_persona, register_persona
from debate_arena.core.debater import Persona


def test_personas_dict_exists():
    """Test that PERSONAS dictionary exists and is populated."""
    assert isinstance(PERSONAS, dict)
    assert len(PERSONAS) > 0


def test_default_personas_available():
    """Test that all default personas are available."""
    expected_personas = [
        "pro_default",
        "con_default",
        "economist_pro",
        "economist_con",
        "scientist_pro",
        "scientist_con",
    ]

    for name in expected_personas:
        assert name in PERSONAS, f"Persona '{name}' not found in PERSONAS"


def test_persona_structure():
    """Test that each persona has the required structure."""
    for name, persona in PERSONAS.items():
        assert isinstance(persona, Persona)
        assert hasattr(persona, "name")
        assert hasattr(persona, "description")
        assert hasattr(persona, "background")
        assert hasattr(persona, "argument_style")

        assert isinstance(persona.name, str)
        assert isinstance(persona.description, str)
        assert isinstance(persona.background, str)
        assert isinstance(persona.argument_style, str)

        assert len(persona.name) > 0
        assert len(persona.description) > 0
        assert len(persona.background) > 0
        assert len(persona.argument_style) > 0


def test_pro_default_persona():
    """Test pro_default persona attributes."""
    persona = PERSONAS["pro_default"]
    assert persona.name == "Dr. Sarah Chen"
    assert "optimist" in persona.description.lower()
    assert "computer science" in persona.background.lower()


def test_con_default_persona():
    """Test con_default persona attributes."""
    persona = PERSONAS["con_default"]
    assert persona.name == "Prof. Marcus Webb"
    assert "ethicist" in persona.description.lower()
    assert "philosophy" in persona.background.lower()


def test_economist_personas():
    """Test economist personas have relevant backgrounds."""
    pro = PERSONAS["economist_pro"]
    con = PERSONAS["economist_con"]

    assert "economist" in pro.name.lower() or "rivera" in pro.name.lower()
    assert "economist" in con.name.lower() or "patel" in con.name.lower()


def test_scientist_personas():
    """Test scientist personas have relevant backgrounds."""
    pro = PERSONAS["scientist_pro"]
    con = PERSONAS["scientist_con"]

    assert "scientist" in pro.name.lower() or "foster" in pro.name.lower()
    assert "scientist" in con.name.lower() or "zhang" in con.name.lower()


def test_get_persona_existing():
    """Test get_persona with existing persona."""
    persona = get_persona("pro_default")
    assert persona is not None
    assert persona.name == "Dr. Sarah Chen"


def test_get_persona_nonexistent():
    """Test get_persona with non-existent persona."""
    persona = get_persona("nonexistent_persona")
    assert persona is None


def test_register_new_persona():
    """Test registering a new persona."""
    new_persona = Persona(
        name="Test Persona",
        description="Test description",
        background="Test background",
        argument_style="Test style"
    )

    register_persona("test_persona", new_persona)

    assert "test_persona" in PERSONAS
    assert PERSONAS["test_persona"].name == "Test Persona"

    # Clean up
    del PERSONAS["test_persona"]
    assert "test_persona" not in PERSONAS


def test_register_persona_overwrite():
    """Test that register_persona can overwrite existing personas."""
    original = PERSONAS.get("pro_default")

    new_persona = Persona(
        name="New Name",
        description="New description",
        background="New background",
        argument_style="New style"
    )

    register_persona("pro_default", new_persona)

    assert PERSONAS["pro_default"].name == "New Name"

    # Restore original
    PERSONAS["pro_default"] = original
    assert PERSONAS["pro_default"].name == "Dr. Sarah Chen"


def test_persona_names_are_unique():
    """Test that all persona display names are unique."""
    names = [persona.name for persona in PERSONAS.values()]
    assert len(names) == len(set(names)), "Persona names should be unique"


def test_all_pro_con_pairs_exist():
    """Test that pro/con pairs exist for each type."""
    pairs = [
        ("pro_default", "con_default"),
        ("economist_pro", "economist_con"),
        ("scientist_pro", "scientist_con"),
        ("lawyer_pro", "lawyer_con"),
        ("philosopher_pro", "philosopher_con"),
        ("technologist_pro", "technologist_con"),
        ("journalist_pro", "journalist_con"),
        ("educator_pro", "educator_con"),
        ("doctor_pro", "doctor_con"),
    ]

    for pro, con in pairs:
        assert pro in PERSONAS, f"Missing pro persona: {pro}"
        assert con in PERSONAS, f"Missing con persona: {con}"


def test_lawyer_personas():
    """Test lawyer personas have relevant backgrounds."""
    pro = PERSONAS["lawyer_pro"]
    con = PERSONAS["lawyer_con"]

    assert "Esq" in pro.name or "attorney" in pro.description.lower()
    assert "Esq" in con.name or "attorney" in con.description.lower()


def test_philosopher_personas():
    """Test philosopher personas have relevant backgrounds."""
    pro = PERSONAS["philosopher_pro"]
    con = PERSONAS["philosopher_con"]

    assert "philosopher" in pro.description.lower() or "ethics" in pro.background.lower()
    assert "philosopher" in con.description.lower() or "ethics" in con.background.lower()


def test_technologist_personas():
    """Test technologist personas have relevant backgrounds."""
    pro = PERSONAS["technologist_pro"]
    con = PERSONAS["technologist_con"]

    # Check for technology-related terms
    pro_terms = ["tech", "software", "computer", "engineering", "cto", "architect"]
    con_terms = ["security", "cyber", "nsa", "vulnerab", "risk"]

    assert any(term in pro.background.lower() for term in pro_terms)
    assert any(term in con.background.lower() for term in con_terms)


def test_journalist_personas():
    """Test journalist personas have relevant backgrounds."""
    pro = PERSONAS["journalist_pro"]
    con = PERSONAS["journalist_con"]

    assert "journalist" in pro.description.lower() or "reporter" in pro.background.lower()
    assert "journalist" in con.description.lower() or "editor" in con.background.lower()


def test_educator_personas():
    """Test educator personas have relevant backgrounds."""
    pro = PERSONAS["educator_pro"]
    con = PERSONAS["educator_con"]

    assert "education" in pro.background.lower() or "learning" in pro.argument_style.lower()
    assert "education" in con.background.lower() or "classroom" in con.background.lower()


def test_doctor_personas():
    """Test doctor personas have relevant backgrounds."""
    pro = PERSONAS["doctor_pro"]
    con = PERSONAS["doctor_con"]

    assert "MD" in pro.background or "physician" in pro.description.lower()
    assert "MD" in con.background or "physician" in con.description.lower()


def test_get_personas_by_category():
    """Test getting personas by category prefix."""
    from debate_arena.personas import get_personas_by_category

    economists = get_personas_by_category("economist")
    assert len(economists) >= 2

    scientists = get_personas_by_category("scientist")
    assert len(scientists) >= 2


def test_list_all_personas():
    """Test listing all persona names."""
    from debate_arena.personas import list_all_personas

    all_names = list_all_personas()
    assert len(all_names) >= 15  # We should have at least 15 personas now
    assert "pro_default" in all_names
    assert "con_default" in all_names


def test_neutral_persona_exists():
    """Test that neutral persona exists."""
    assert "neutral_default" in PERSONAS
    neutral = PERSONAS["neutral_default"]
    assert "balanced" in neutral.description.lower()
