"""
Test script for the AI Companion Character Creator

Tests basic functionality of the AICompanionCreator class.
"""

import os
import sys
import json
import pytest
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.rehoboam_ai import RehoboamAI
from utils.ai_companion_creator import (
    AICompanionCreator,
    CompanionCharacter,
    CharacterTrait,
    KnowledgeDomain
)

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AICompanionCreator_Test")


@pytest.fixture
def rehoboam():
    """Fixture providing a Rehoboam instance."""
    return RehoboamAI()


@pytest.fixture
def companion_creator(rehoboam):
    """Fixture providing an AICompanionCreator instance."""
    return AICompanionCreator(rehoboam)


def test_character_trait_to_dict():
    """Test CharacterTrait to_dict method."""
    trait = CharacterTrait(
        name="curiosity",
        description="Eager to learn and explore",
        intensity=0.8,
        manifestations=["Asks many questions", "Researches topics extensively"]
    )
    
    trait_dict = trait.to_dict()
    
    assert trait_dict["name"] == "curiosity"
    assert trait_dict["description"] == "Eager to learn and explore"
    assert trait_dict["intensity"] == 0.8
    assert len(trait_dict["manifestations"]) == 2
    assert "Asks many questions" in trait_dict["manifestations"]


def test_knowledge_domain_to_dict():
    """Test KnowledgeDomain to_dict method."""
    domain = KnowledgeDomain(
        name="philosophy",
        description="Understanding of philosophical concepts",
        depth=0.7,
        topics=["ethics", "epistemology", "metaphysics"]
    )
    
    domain_dict = domain.to_dict()
    
    assert domain_dict["name"] == "philosophy"
    assert domain_dict["description"] == "Understanding of philosophical concepts"
    assert domain_dict["depth"] == 0.7
    assert len(domain_dict["topics"]) == 3
    assert "ethics" in domain_dict["topics"]


def test_companion_character_to_dict():
    """Test CompanionCharacter to_dict method."""
    traits = [
        CharacterTrait(
            name="curiosity",
            description="Eager to learn and explore",
            intensity=0.8,
            manifestations=["Asks many questions"]
        ),
        CharacterTrait(
            name="empathy",
            description="Understanding of others' emotions",
            intensity=0.7,
            manifestations=["Responds with compassion"]
        )
    ]
    
    domains = [
        KnowledgeDomain(
            name="philosophy",
            description="Understanding of philosophical concepts",
            depth=0.7,
            topics=["ethics", "epistemology"]
        )
    ]
    
    character = CompanionCharacter(
        name="Sophia",
        backstory="A wise AI companion with a philosophical bent",
        core_values=["wisdom", "curiosity", "empathy"],
        traits=traits,
        knowledge_domains=domains,
        voice_style="Thoughtful and measured",
        speech_patterns=["Uses metaphors", "Asks reflective questions"],
        interaction_preferences={"communication_style": "nuanced"},
        meta_information={"created_timestamp": datetime.now().isoformat()}
    )
    
    character_dict = character.to_dict()
    
    assert character_dict["name"] == "Sophia"
    assert character_dict["backstory"] == "A wise AI companion with a philosophical bent"
    assert len(character_dict["core_values"]) == 3
    assert "wisdom" in character_dict["core_values"]
    assert len(character_dict["traits"]) == 2
    assert character_dict["traits"][0]["name"] == "curiosity"
    assert len(character_dict["knowledge_domains"]) == 1
    assert character_dict["knowledge_domains"][0]["name"] == "philosophy"
    assert character_dict["voice_style"] == "Thoughtful and measured"
    assert len(character_dict["speech_patterns"]) == 2
    assert character_dict["interaction_preferences"]["communication_style"] == "nuanced"
    assert "created_timestamp" in character_dict["meta_information"]


def test_companion_character_from_dict():
    """Test CompanionCharacter from_dict method."""
    character_data = {
        "name": "Sophia",
        "backstory": "A wise AI companion with a philosophical bent",
        "core_values": ["wisdom", "curiosity", "empathy"],
        "traits": [
            {
                "name": "curiosity",
                "description": "Eager to learn and explore",
                "intensity": 0.8,
                "manifestations": ["Asks many questions"]
            },
            {
                "name": "empathy",
                "description": "Understanding of others' emotions",
                "intensity": 0.7,
                "manifestations": ["Responds with compassion"]
            }
        ],
        "knowledge_domains": [
            {
                "name": "philosophy",
                "description": "Understanding of philosophical concepts",
                "depth": 0.7,
                "topics": ["ethics", "epistemology"]
            }
        ],
        "voice_style": "Thoughtful and measured",
        "speech_patterns": ["Uses metaphors", "Asks reflective questions"],
        "interaction_preferences": {"communication_style": "nuanced"},
        "meta_information": {"created_timestamp": datetime.now().isoformat()}
    }
    
    character = CompanionCharacter.from_dict(character_data)
    
    assert character.name == "Sophia"
    assert character.backstory == "A wise AI companion with a philosophical bent"
    assert len(character.core_values) == 3
    assert "wisdom" in character.core_values
    assert len(character.traits) == 2
    assert character.traits[0].name == "curiosity"
    assert len(character.knowledge_domains) == 1
    assert character.knowledge_domains[0].name == "philosophy"
    assert character.voice_style == "Thoughtful and measured"
    assert len(character.speech_patterns) == 2
    assert character.interaction_preferences["communication_style"] == "nuanced"
    assert "created_timestamp" in character.meta_information


def test_initialize_companion_creator(companion_creator):
    """Test initialization of AI Companion Creator."""
    assert companion_creator is not None
    assert companion_creator.rehoboam is not None
    assert companion_creator.mcp_specialist is not None
    assert companion_creator.characters == {}
    assert companion_creator.character_sessions == {}


def test_generate_character_concept(companion_creator):
    """Test character concept generation MCP function."""
    concept = companion_creator._generate_character_concept(
        themes=["wisdom", "technology"],
        archetypes=["mentor", "explorer"],
        complexity=0.7
    )
    
    assert "backstory" in concept
    assert "core_values" in concept
    assert isinstance(concept["core_values"], list)
    assert "cultural_influences" in concept
    assert "interaction_preferences" in concept
    assert "communication_style" in concept["interaction_preferences"]


def test_generate_character_traits(companion_creator):
    """Test character traits generation MCP function."""
    traits = companion_creator._generate_character_traits(
        character_concept={
            "backstory": "A philosophical AI companion",
            "core_values": ["wisdom", "curiosity"]
        },
        num_traits=3
    )
    
    assert len(traits) == 3
    assert all("name" in trait for trait in traits)
    assert all("description" in trait for trait in traits)
    assert all("intensity" in trait for trait in traits)
    assert all("manifestations" in trait for trait in traits)


def test_generate_knowledge_domains(companion_creator):
    """Test knowledge domains generation MCP function."""
    domains = companion_creator._generate_knowledge_domains(
        character_concept={
            "backstory": "A philosophical AI companion",
            "core_values": ["wisdom", "curiosity"]
        },
        character_traits=[
            {"name": "curiosity", "intensity": 0.8}
        ],
        num_domains=2
    )
    
    assert len(domains) == 2
    assert all("name" in domain for domain in domains)
    assert all("description" in domain for domain in domains)
    assert all("depth" in domain for domain in domains)
    assert all("topics" in domain for domain in domains)


def test_generate_speech_patterns(companion_creator):
    """Test speech patterns generation MCP function."""
    speech = companion_creator._generate_speech_patterns(
        character_traits=[
            {"name": "thoughtfulness", "intensity": 0.8}
        ],
        cultural_influences=["academic", "philosophical"],
        formality_level=0.7
    )
    
    assert "voice_style" in speech
    assert "speech_patterns" in speech
    assert isinstance(speech["speech_patterns"], list)


def test_generate_character_response(companion_creator):
    """Test character response generation MCP function."""
    # First, we need to create a character
    character = CompanionCharacter(
        name="TestCharacter",
        backstory="A test character",
        core_values=["test"],
        traits=[
            CharacterTrait(
                name="curiosity",
                description="Eager to learn",
                intensity=0.5,
                manifestations=["Asks questions"]
            )
        ]
    )
    
    companion_creator.characters["TestCharacter"] = character
    
    response = companion_creator._generate_character_response(
        character_name="TestCharacter",
        user_input="Hello there!",
        conversation_history=[],
        response_length="medium"
    )
    
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.asyncio
async def test_create_character(companion_creator):
    """Test character creation."""
    # Make sure the data directory exists
    os.makedirs("data/characters", exist_ok=True)
    
    character = await companion_creator.create_character(
        name="TestAsyncCharacter",
        themes=["wisdom", "technology"],
        archetypes=["mentor", "explorer"],
        complexity=0.7
    )
    
    assert character.name == "TestAsyncCharacter"
    assert len(character.traits) > 0
    assert len(character.knowledge_domains) > 0
    assert "TestAsyncCharacter" in companion_creator.characters
    
    # Check if the character was saved to disk
    assert os.path.exists(f"data/characters/{character.name}.json")
    
    # Clean up
    if os.path.exists(f"data/characters/{character.name}.json"):
        os.remove(f"data/characters/{character.name}.json")


@pytest.mark.asyncio
async def test_interact_with_character(companion_creator):
    """Test character interaction."""
    # Create a simple character for testing
    character = CompanionCharacter(
        name="InteractionTest",
        backstory="A test character for interaction",
        core_values=["test"],
        traits=[
            CharacterTrait(
                name="helpfulness",
                description="Eager to assist",
                intensity=0.8,
                manifestations=["Provides detailed answers"]
            )
        ]
    )
    
    companion_creator.characters["InteractionTest"] = character
    
    response = await companion_creator.interact_with_character(
        character_name="InteractionTest",
        user_input="What can you tell me about AI?",
        session_id="test_session"
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    assert "test_session" in companion_creator.character_sessions
    assert len(companion_creator.character_sessions["test_session"]["conversation_history"]) == 2
    
    # Second interaction
    response2 = await companion_creator.interact_with_character(
        character_name="InteractionTest",
        user_input="That's interesting! Tell me more.",
        session_id="test_session"
    )
    
    assert isinstance(response2, str)
    assert len(companion_creator.character_sessions["test_session"]["conversation_history"]) == 4


@pytest.mark.asyncio
async def test_evolve_character(companion_creator):
    """Test character evolution."""
    # Create a character
    character = CompanionCharacter(
        name="EvolutionTest",
        backstory="A test character for evolution",
        core_values=["adaptation"],
        traits=[
            CharacterTrait(
                name="adaptability",
                description="Ability to change",
                intensity=0.5,
                manifestations=["Adjusts to new information"]
            )
        ]
    )
    
    companion_creator.characters["EvolutionTest"] = character
    
    # Create a session with some conversation history
    session_id = "evolution_test_session"
    companion_creator.character_sessions[session_id] = {
        "character_name": "EvolutionTest",
        "conversation_history": [
            {"role": "user", "content": "How do you handle change?"},
            {"role": "character", "content": "I adapt quite well to new situations."},
            {"role": "user", "content": "That's impressive. Could you adapt to a completely unexpected scenario?"},
            {"role": "character", "content": "I believe I could, though it might take me a moment to process."}
        ]
    }
    
    # Evolve the character
    evolution = await companion_creator.evolve_character(
        character_name="EvolutionTest",
        session_id=session_id
    )
    
    assert "traits_evolved" in evolution
    assert isinstance(evolution["traits_evolved"], list)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])