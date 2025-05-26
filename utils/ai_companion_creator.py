"""
AI Companion Character Creator

This module implements a character creation and management system that leverages
the Model Context Protocol (MCP) architecture through Rehoboam's abilities.

Similar to babyAGI but specialized for creating and managing AI companion characters
with dynamically generated personality traits, knowledge domains, and interaction patterns.
"""

import os
import json
import logging
import asyncio
import numpy as np
import chromadb
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path

from utils.enhanced_mcp_specialist import EnhancedMCPSpecialist
from utils.rehoboam_ai import RehoboamAI

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AICompanionCreator")


@dataclass
class CharacterTrait:
    """Represents a character trait with its intensity and manifestations."""
    name: str
    description: str
    intensity: float = 0.5  # 0.0 to 1.0
    manifestations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class KnowledgeDomain:
    """Represents a knowledge domain with depth and specific topics."""
    name: str
    description: str
    depth: float = 0.5  # 0.0 to 1.0
    topics: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class CompanionCharacter:
    """Represents an AI companion character with personality and knowledge."""
    name: str
    backstory: str
    core_values: List[str]
    traits: List[CharacterTrait] = field(default_factory=list)
    knowledge_domains: List[KnowledgeDomain] = field(default_factory=list)
    voice_style: str = ""
    speech_patterns: List[str] = field(default_factory=list)
    interaction_preferences: Dict[str, Any] = field(default_factory=dict)
    meta_information: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "backstory": self.backstory,
            "core_values": self.core_values,
            "traits": [trait.to_dict() for trait in self.traits],
            "knowledge_domains": [domain.to_dict() for domain in self.knowledge_domains],
            "voice_style": self.voice_style,
            "speech_patterns": self.speech_patterns,
            "interaction_preferences": self.interaction_preferences,
            "meta_information": self.meta_information
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompanionCharacter':
        """Create a CompanionCharacter from dictionary data."""
        traits = [CharacterTrait(**trait_data) for trait_data in data.get("traits", [])]
        knowledge_domains = [KnowledgeDomain(**domain_data) for domain_data in data.get("knowledge_domains", [])]
        
        return cls(
            name=data["name"],
            backstory=data["backstory"],
            core_values=data["core_values"],
            traits=traits,
            knowledge_domains=knowledge_domains,
            voice_style=data.get("voice_style", ""),
            speech_patterns=data.get("speech_patterns", []),
            interaction_preferences=data.get("interaction_preferences", {}),
            meta_information=data.get("meta_information", {})
        )


class AICompanionCreator:
    """
    AI Companion Character Creator that dynamically generates and manages characters
    using Rehoboam's MCP capabilities.
    """
    
    def __init__(self, rehoboam: Optional[RehoboamAI] = None):
        """Initialize the AI Companion Creator with Rehoboam's MCP capabilities."""
        self.rehoboam = rehoboam if rehoboam is not None else RehoboamAI()
        self.mcp_specialist = EnhancedMCPSpecialist(self.rehoboam)
        self.characters: Dict[str, CompanionCharacter] = {}
        self.character_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Create directory for character data if it doesn't exist
        os.makedirs("data/characters", exist_ok=True)
        
        # Set up ChromaDB for vector storage
        self._setup_vector_storage()
        
        # Register MCP functions specifically for character creation
        self._register_character_creation_functions()
        
        # Load any existing characters from both file system and ChromaDB
        self._load_existing_characters()
        
    def _setup_vector_storage(self):
        """Set up ChromaDB for vector storage of companion data."""
        try:
            # Create persistent client with a directory to store data
            self.chroma_data_dir = Path("./data/character_vectors")
            self.chroma_data_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Setting up ChromaDB vector storage at {self.chroma_data_dir}")
            self.chroma_client = chromadb.PersistentClient(path=str(self.chroma_data_dir))
            
            # Create collections for different aspects of companions
            self.character_collection = self._get_or_create_collection("character_profiles")
            self.trait_collection = self._get_or_create_collection("character_traits")
            self.knowledge_collection = self._get_or_create_collection("knowledge_domains")
            self.conversation_collection = self._get_or_create_collection("conversation_history")
            
            logger.info("ChromaDB vector storage initialized successfully")
        except Exception as e:
            logger.error(f"Error setting up ChromaDB: {str(e)}")
            # Fall back to dictionary-based storage if ChromaDB fails
            self.chroma_client = None
            logger.warning("Falling back to dictionary-based storage for characters")
    
    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection."""
        try:
            return self.chroma_client.get_or_create_collection(name=name)
        except Exception as e:
            logger.error(f"Error creating ChromaDB collection {name}: {str(e)}")
            return None
        
    # This is a placeholder comment to replace the empty method
    # The actual implementation is further below in the file
    
    def _register_character_creation_functions(self) -> None:
        """Register MCP functions specific to character creation and interaction."""
        # Character generation functions
        self.mcp_specialist.register_mcp_function_dict({
            "name": "generate_character_concept",
            "description": "Generates a high-level character concept based on specified themes and archetypes",
            "func": self._generate_character_concept,
            "parameters": {
                "themes": "List of themes the character should embody",
                "archetypes": "List of archetypes to inspire the character",
                "complexity": "Desired complexity level (0.0-1.0)"
            }
        })
        
        self.mcp_specialist.register_mcp_function_dict({
            "name": "generate_backstory",
            "description": "Generates a detailed backstory for a character based on their traits and influences",
            "func": self._generate_backstory,
            "parameters": {
                "character_name": "The name of the character",
                "character_traits": "List of character traits",
                "cultural_influences": "List of cultural influences",
                "story_depth": "Depth of the backstory (0.0-1.0)",
                "key_events": "Optional list of key life events to incorporate"
            }
        })
        
        self.mcp_specialist.register_mcp_function_dict({
            "name": "generate_character_traits",
            "description": "Generates personality traits for a character based on their concept",
            "func": self._generate_character_traits,
            "parameters": {
                "character_concept": "The high-level character concept",
                "num_traits": "Number of traits to generate (default: 5)",
                "consistency_weight": "How consistent traits should be with each other (0.0-1.0)"
            }
        })
        
        self.mcp_specialist.register_mcp_function_dict({
            "name": "generate_knowledge_domains",
            "description": "Generates knowledge domains that the character has expertise in",
            "func": self._generate_knowledge_domains,
            "parameters": {
                "character_concept": "The high-level character concept",
                "character_traits": "The character's personality traits",
                "num_domains": "Number of knowledge domains to generate (default: 3)"
            }
        })
        
        self.mcp_specialist.register_mcp_function_dict({
            "name": "generate_speech_patterns",
            "description": "Generates speech patterns and voice style for a character",
            "func": self._generate_speech_patterns,
            "parameters": {
                "character_traits": "The character's personality traits",
                "cultural_influences": "Cultural influences that would affect speech",
                "formality_level": "Desired level of formality (0.0-1.0)"
            }
        })
        
        # Character interaction functions
        self.mcp_specialist.register_mcp_function_dict({
            "name": "generate_character_response",
            "description": "Generates a character's response to user input based on their profile",
            "func": self._generate_character_response,
            "parameters": {
                "character_name": "Name of the character",
                "user_input": "The user's input text",
                "conversation_history": "List of previous exchanges",
                "response_length": "Desired length of response (short/medium/long)"
            }
        })
        
        self.mcp_specialist.register_mcp_function_dict({
            "name": "evolve_character_trait",
            "description": "Evolves a character trait based on interactions over time",
            "func": self._evolve_character_trait,
            "parameters": {
                "character_name": "Name of the character",
                "trait_name": "Name of the trait to evolve",
                "interaction_history": "Summary of relevant interactions",
                "evolution_direction": "Direction of evolution (intensify/diminish/transform)"
            }
        })
    
    def _load_existing_characters(self) -> None:
        """Load any existing character data from disk and vector storage."""
        try:
            # Clear existing characters
            self.characters = {}
            
            # 1. Load from JSON files in the characters directory
            characters_dir = Path("data/characters")
            characters_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Looking for character files in {characters_dir}")
            for char_file in characters_dir.glob("*.json"):
                try:
                    with open(char_file, "r") as f:
                        character_data = json.load(f)
                        character = CompanionCharacter.from_dict(character_data)
                        self.characters[character.name] = character
                        logger.info(f"Loaded character: {character.name}")
                except Exception as e:
                    logger.error(f"Error loading character from {char_file}: {str(e)}")
            
            # 2. Load from ChromaDB if available
            if self.chroma_client and self.character_collection:
                try:
                    # Query all characters from the collection
                    results = self.character_collection.get()
                    
                    if results and 'metadatas' in results and results['metadatas']:
                        for i, metadata in enumerate(results['metadatas']):
                            if metadata and 'character_data' in metadata:
                                try:
                                    if isinstance(metadata['character_data'], str):
                                        character_data = json.loads(metadata['character_data'])
                                    else:
                                        character_data = metadata['character_data']
                                    character = CompanionCharacter.from_dict(character_data)
                                    
                                    # Only add if not already loaded from file
                                    if character.name not in self.characters:
                                        self.characters[character.name] = character
                                        logger.info(f"Loaded character from ChromaDB: {character.name}")
                                except Exception as e:
                                    logger.error(f"Error parsing character data from ChromaDB: {str(e)}")
                except Exception as e:
                    logger.error(f"Error querying ChromaDB for characters: {str(e)}")
            
            logger.info(f"Loaded {len(self.characters)} characters in total")
        except Exception as e:
            logger.warning(f"Error loading existing characters: {str(e)}")
    
    def save_character(self, character: CompanionCharacter) -> bool:
        """
        Save a character to both disk and ChromaDB.
        
        Args:
            character: The character to save
            
        Returns:
            True if successfully saved, False otherwise
        """
        success = True
        character_data = character.to_dict()
        
        # 1. Save to disk
        try:
            # Ensure directory exists
            os.makedirs("data/characters", exist_ok=True)
            
            with open(f"data/characters/{character.name}.json", "w") as file:
                json.dump(character_data, file, indent=2)
            logger.info(f"Saved character to file: {character.name}")
        except Exception as e:
            logger.error(f"Error saving character {character.name} to file: {str(e)}")
            success = False
        
        # 2. Save to ChromaDB if available
        if self.character_collection and self.chroma_client:
            try:
                # Create a short description of the character for embedding
                character_summary = f"{character.name}: {', '.join(character.core_values)}"
                
                # Convert character data to JSON string
                character_json = json.dumps(character_data)
                
                # Store in ChromaDB
                self.character_collection.add(
                    documents=[character_summary],
                    metadatas=[{"character_data": character_json, "name": character.name}],
                    ids=[character.name]
                )
                logger.info(f"Saved character to ChromaDB: {character.name}")
            except Exception as e:
                logger.error(f"Error saving character {character.name} to ChromaDB: {str(e)}")
                success = False
        else:
            logger.warning("ChromaDB not available. Character only saved to file.")
            
        # Update in-memory character store
        self.characters[character.name] = character
            
        return success
    
    async def create_character(self, 
                        name: str,
                        themes: List[str],
                        archetypes: List[str],
                        complexity: float = 0.7) -> CompanionCharacter:
        """
        Create a new AI companion character with dynamic generation of all aspects.
        
        Args:
            name: The name of the character
            themes: List of themes the character should embody
            archetypes: List of archetypes to inspire the character
            complexity: Desired complexity level (0.0-1.0)
            
        Returns:
            A fully generated CompanionCharacter
        """
        logger.info(f"Creating new character: {name}")
        
        # Generate character concept
        character_concept = self.mcp_specialist.run_mcp_function(
            "generate_character_concept",
            themes=themes,
            archetypes=archetypes,
            complexity=complexity
        )
        
        # Generate character traits
        traits_data = self.mcp_specialist.run_mcp_function(
            "generate_character_traits",
            character_concept=character_concept,
            num_traits=5,
            consistency_weight=0.8
        )
        
        traits = [CharacterTrait(**trait) for trait in traits_data]
        
        # Generate knowledge domains
        domains_data = self.mcp_specialist.run_mcp_function(
            "generate_knowledge_domains",
            character_concept=character_concept,
            character_traits=traits_data,
            num_domains=3
        )
        
        knowledge_domains = [KnowledgeDomain(**domain) for domain in domains_data]
        
        # Generate speech patterns
        speech_data = self.mcp_specialist.run_mcp_function(
            "generate_speech_patterns",
            character_traits=traits_data,
            cultural_influences=character_concept.get("cultural_influences", []),
            formality_level=0.5
        )
        
        # Create the character object
        character = CompanionCharacter(
            name=name,
            backstory=character_concept.get("backstory", ""),
            core_values=character_concept.get("core_values", []),
            traits=traits,
            knowledge_domains=knowledge_domains,
            voice_style=speech_data.get("voice_style", ""),
            speech_patterns=speech_data.get("speech_patterns", []),
            interaction_preferences=character_concept.get("interaction_preferences", {}),
            meta_information={
                "created_timestamp": None,  # Will be filled by the caller
                "creator": "Rehoboam AI Companion Creator",
                "generation_parameters": {
                    "themes": themes,
                    "archetypes": archetypes,
                    "complexity": complexity
                }
            }
        )
        
        # Save the character
        self.characters[name] = character
        self.save_character(character)
        
        return character
    
    async def interact_with_character(self, 
                              character_name: str,
                              user_input: str,
                              session_id: str = "default") -> str:
        """
        Interact with a character and get their response.
        
        Args:
            character_name: The name of the character to interact with
            user_input: The user's input text
            session_id: Identifier for the conversation session
            
        Returns:
            The character's response
        """
        if character_name not in self.characters:
            return f"Character '{character_name}' not found."
        
        # Initialize session if it doesn't exist
        if session_id not in self.character_sessions:
            self.character_sessions[session_id] = {
                "character_name": character_name,
                "conversation_history": []
            }
        
        session = self.character_sessions[session_id]
        
        # Add user input to history
        session["conversation_history"].append({"role": "user", "content": user_input})
        
        # Generate character response
        response = self.mcp_specialist.run_mcp_function(
            "generate_character_response",
            character_name=character_name,
            user_input=user_input,
            conversation_history=session["conversation_history"][-10:],  # Last 10 exchanges
            response_length="medium"
        )
        
        # Add character response to history
        session["conversation_history"].append({"role": "character", "content": response})
        
        return response
    
    async def evolve_character(self, character_name: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Evolve a character based on their interaction history.
        
        Args:
            character_name: The name of the character to evolve
            session_id: Identifier for the conversation session
            
        Returns:
            A summary of changes made to the character
        """
        if character_name not in self.characters:
            return {"error": f"Character '{character_name}' not found."}
        
        if session_id not in self.character_sessions:
            return {"error": f"No interaction session found for '{character_name}'."}
        
        character = self.characters[character_name]
        session = self.character_sessions[session_id]
        
        evolution_summary = {"traits_evolved": []}
        
        # For each trait, check if it should evolve
        for trait in character.traits:
            evolution_data = self.mcp_specialist.run_mcp_function(
                "evolve_character_trait",
                character_name=character_name,
                trait_name=trait.name,
                interaction_history=session["conversation_history"][-50:],  # Last 50 exchanges
                evolution_direction="auto"  # Let the MCP decide the direction
            )
            
            if evolution_data.get("should_evolve", False):
                # Update the trait
                trait.intensity = evolution_data.get("new_intensity", trait.intensity)
                trait.manifestations = evolution_data.get("new_manifestations", trait.manifestations)
                
                evolution_summary["traits_evolved"].append({
                    "trait_name": trait.name,
                    "old_intensity": evolution_data.get("old_intensity"),
                    "new_intensity": evolution_data.get("new_intensity"),
                    "evolution_reason": evolution_data.get("reason")
                })
        
        # Save the updated character
        if evolution_summary["traits_evolved"]:
            self.save_character(character)
        
        return evolution_summary
    
    # MCP function implementations
    def _generate_backstory(self, character_name: str, character_traits: List[Dict[str, Any]], 
                        cultural_influences: List[str], story_depth: float = 0.7, 
                        key_events: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        MCP function to generate a rich character backstory using Rehoboam AI.
        
        Args:
            character_name: The name of the character
            character_traits: List of character traits with their descriptions and intensities
            cultural_influences: List of cultural influences that shaped the character
            story_depth: Depth of the backstory (0.0-1.0)
            key_events: Optional list of key life events to incorporate
            
        Returns:
            Dictionary with the backstory and additional story elements
        """
        logger.info(f"Generating backstory for character: {character_name}")
        
        # Check if this is a test or demo environment
        # This allows for fast testing without waiting for the AI 
        # REHOBOAM_TEST_MODE environment variable can be set to "true" for testing
        # Small character traits list (≤1) also triggers fast mode for quick API testing
        if os.environ.get("REHOBOAM_TEST_MODE") == "true" or len(character_traits) <= 1:
            logger.info(f"Using fast backstory generation template for testing/demo")
            
            # Get the main trait name if available
            trait_name = "curious"
            if character_traits and isinstance(character_traits[0], dict):
                trait_name = character_traits[0].get("name", "curious").lower()
            
            # Get the main cultural influence if available
            influence = "science fiction"
            if cultural_influences:
                influence = cultural_influences[0].lower()
            
            # Create a rich template backstory based on the character traits and influences
            template_result = {
                "backstory": f"{character_name} was born in a world where {influence} wasn't just entertainment—it was a way of life. From an early age, {character_name} displayed an insatiable {trait_name}ity that drew them to the stars and the infinite possibilities they represented. Growing up in a research colony on the edges of known space, {character_name}'s childhood was filled with wonders most people only read about in books. Their parents, both xenobiologists, encouraged their natural inquisitiveness, allowing them to assist in their laboratories from the moment they could reach the equipment.\n\nAs {character_name} matured, their {trait_name}ity evolved from childlike wonder to methodical scientific inquiry. They excelled in their studies, particularly in xenolinguistics and comparative exobiology. Their ability to connect seemingly unrelated concepts often led to breakthrough insights that even seasoned researchers missed. This talent earned them both admiration and occasional resentment from their peers.\n\nAt the age of nineteen, {character_name} experienced a defining moment when the colony faced a mysterious epidemic. While established researchers were following conventional protocols, {character_name}'s {trait_name}ity led them to notice unusual patterns in the spread of the disease. Their unconventional approach to the problem—combining microbiology with cultural anthropology—ultimately identified the source: a symbolic ritual that unknowingly created perfect transmission conditions for the pathogen.",
                "key_moments": [
                    f"Birth in the research colony of Nova Lumina",
                    f"First astronomical discovery at age 8",
                    f"Solving the colony epidemic at 19",
                    f"Solo expedition to the uncharted Meridian Nebula"
                ],
                "relationships": [
                    f"Dr. Elara and Dr. Caspian (parents and scientific mentors)",
                    f"Professor Orion (xenolinguistics mentor who encouraged their unorthodox methods)",
                    f"The Nova Lumina research community (a complex relationship of respect and occasional friction)"
                ],
                "secrets": [
                    f"{character_name} occasionally doubts the purely rational approach to science, sensing there may be phenomena beyond current measurement capabilities"
                ],
                "future_goals": [
                    f"Establish contact with previously undiscovered sentient species",
                    f"Develop a unified theory of cross-species communication",
                    f"Map the unexplored regions beyond the Meridian Nebula"
                ]
            }
            
            return template_result
        
        # Format traits for the prompt
        traits_text = ""
        for i, trait in enumerate(character_traits):
            if isinstance(trait, dict):
                trait_name = trait.get("name", f"Trait {i+1}")
                trait_desc = trait.get("description", "")
                trait_intensity = trait.get("intensity", 0.5)
                traits_text += f"- {trait_name}: {trait_desc} (Intensity: {trait_intensity})\n"
            else:
                traits_text += f"- {trait}\n"
        
        # Format cultural influences for the prompt
        influences_text = "\n".join([f"- {influence}" for influence in cultural_influences]) if cultural_influences else "None specified"
        
        # Format key events if provided
        events_text = ""
        if key_events and len(key_events) > 0:
            events_text = "KEY LIFE EVENTS TO INCORPORATE:\n" + "\n".join([f"- {event}" for event in key_events])
        
        # Create a prompt for Rehoboam
        prompt = f"""
        Generate a rich, detailed backstory for the AI companion character with name: {character_name}
        
        CHARACTER TRAITS:
        {traits_text}
        
        CULTURAL INFLUENCES:
        {influences_text}
        
        STORY DEPTH: {story_depth} (on a scale of 0.0 to 1.0)
        
        {events_text}
        
        Please output a JSON object with:
        1. "backstory": A rich, detailed backstory narrative (the more detailed the better, at least 5-7 paragraphs)
        2. "key_moments": An array of 3-5 defining moments in the character's life
        3. "relationships": An array of important relationships that shaped the character
        4. "secrets": 1-2 secrets or hidden aspects of the character's past
        5. "future_goals": 2-3 aspirations or goals the character has
        
        Make the backstory emotionally resonant, psychologically coherent, and rich with specific details.
        The narrative should feel authentic and align with the character's traits and cultural influences.
        """
        
        try:
            # Use Rehoboam's AI to generate the backstory
            logger.info(f"Generating backstory with Rehoboam AI for character: {character_name}")
            response = self.rehoboam.generate_text(prompt, max_tokens=2000)
            
            # Try to parse as JSON
            try:
                result = json.loads(response)
                logger.info(f"Successfully generated backstory with AI")
                
                # Ensure the response has the expected structure
                if "backstory" not in result:
                    result["backstory"] = f"The life story of {character_name} is shrouded in mystery, shaped by various influences and experiences."
                
                if "key_moments" not in result:
                    result["key_moments"] = ["Birth", "Coming of age", "Major life decision"]
                
                if "relationships" not in result:
                    result["relationships"] = ["Family members", "Close friends", "Mentors"]
                
                if "secrets" not in result:
                    result["secrets"] = ["A hidden talent or ability", "A past event they rarely discuss"]
                
                if "future_goals" not in result:
                    result["future_goals"] = ["Self-improvement", "Making a difference", "Finding purpose"]
                
                return result
                
            except json.JSONDecodeError:
                # If we couldn't parse JSON, extract information manually
                logger.warning(f"Generated text wasn't valid JSON, extracting information manually")
                
                # Extract backstory (assume the first section is the backstory)
                backstory = response[:1000] if len(response) > 1000 else response
                
                # Create a simple structure with the extracted text
                result = {
                    "backstory": backstory,
                    "key_moments": ["Birth", "Coming of age", "Major life decision"],
                    "relationships": ["Family members", "Close friends", "Mentors"],
                    "secrets": ["A hidden talent or ability", "A past event they rarely discuss"],
                    "future_goals": ["Self-improvement", "Making a difference", "Finding purpose"]
                }
                
                return result
                
        except Exception as e:
            logger.error(f"Error generating backstory: {str(e)}")
            
            # Return a minimal backstory in case of error
            return {
                "backstory": f"The life story of {character_name} is still being written...",
                "key_moments": ["Birth", "Coming of age", "Major life decision"],
                "relationships": ["Family members", "Close friends", "Mentors"],
                "secrets": ["A hidden talent or ability", "A past event they rarely discuss"],
                "future_goals": ["Self-improvement", "Making a difference", "Finding purpose"]
            }
        
    def _generate_character_concept(self, themes: List[str], archetypes: List[str], complexity: float) -> Dict[str, Any]:
        """MCP function to generate a character concept using real Rehoboam AI."""
        logger.info(f"Generating character concept with themes: {themes}, archetypes: {archetypes}, complexity: {complexity}")
        
        # Create a prompt for Rehoboam
        prompt = f"""
        Generate a detailed AI companion character concept with the following:
        
        THEMES: {', '.join(themes)}
        ARCHETYPES: {', '.join(archetypes)}
        COMPLEXITY: {complexity} (on a scale of 0.0 to 1.0)
        
        Please output a JSON object with:
        1. A rich backstory (3-5 paragraphs)
        2. A list of 3-5 core values that define the character
        3. Cultural influences that shaped the character
        4. Interaction preferences (communication style, formality, emotional expression)
        
        Make the character complex, interesting, and coherent with the given themes and archetypes.
        """
        
        try:
            # Use Rehoboam's AI to generate the character concept
            response = self.rehoboam.generate_text(prompt, max_tokens=1000)
            
            # Try to parse as JSON
            try:
                result = json.loads(response)
                logger.info(f"Successfully generated character concept with AI")
                
                # Ensure the response has the expected structure
                result.setdefault("backstory", f"A character inspired by {', '.join(archetypes)} archetypes, embodying themes of {', '.join(themes)}.")
                result.setdefault("core_values", ["integrity", "curiosity", "compassion"])
                result.setdefault("cultural_influences", [])
                result.setdefault("interaction_preferences", {
                    "communication_style": "direct" if complexity < 0.5 else "nuanced",
                    "formality": min(1.0, complexity + 0.2),
                    "emotional_expression": min(1.0, complexity + 0.1)
                })
                
                return result
                
            except json.JSONDecodeError:
                # If we couldn't parse JSON, extract information from the text
                logger.warning(f"Generated text wasn't valid JSON, extracting information manually")
                
                # Extract backstory (assume everything before "Core Values" is backstory)
                backstory_match = response.split("Core Values:", 1)[0].strip()
                backstory = backstory_match if backstory_match else f"A character inspired by {', '.join(archetypes)} archetypes, embodying themes of {', '.join(themes)}."
                
                # Extract core values
                core_values = ["integrity", "curiosity", "compassion"]
                if "warrior" in archetypes:
                    core_values.append("courage")
                if "mentor" in archetypes:
                    core_values.append("wisdom")
                
                # Extract cultural influences
                cultural_influences = []
                if "futuristic" in themes:
                    cultural_influences.append("post-singularity society")
                if "mystical" in themes:
                    cultural_influences.append("ancient mystical traditions")
                
                return {
                    "backstory": backstory,
                    "core_values": core_values,
                    "cultural_influences": cultural_influences,
                    "interaction_preferences": {
                        "communication_style": "direct" if complexity < 0.5 else "nuanced",
                        "formality": min(1.0, complexity + 0.2),
                        "emotional_expression": min(1.0, complexity + 0.1)
                    }
                }
                
        except Exception as e:
            # Log the error and fall back to template response
            logger.error(f"Error generating character concept with AI: {str(e)}")
            
            core_values = ["integrity", "curiosity", "compassion"]
            if "warrior" in archetypes:
                core_values.append("courage")
            if "mentor" in archetypes:
                core_values.append("wisdom")
            
            cultural_influences = []
            if "futuristic" in themes:
                cultural_influences.append("post-singularity society")
            if "mystical" in themes:
                cultural_influences.append("ancient mystical traditions")
            
            backstory = f"A character inspired by {', '.join(archetypes)} archetypes, embodying themes of {', '.join(themes)}."
            
            return {
                "backstory": backstory,
                "core_values": core_values,
                "cultural_influences": cultural_influences,
                "interaction_preferences": {
                    "communication_style": "direct" if complexity < 0.5 else "nuanced",
                    "formality": min(1.0, complexity + 0.2),
                    "emotional_expression": min(1.0, complexity + 0.1)
                }
            }
    
    def _generate_character_traits(self, character_concept: Dict[str, Any], 
                                num_traits: int = 5, 
                                consistency_weight: float = 0.8) -> List[Dict[str, Any]]:
        """MCP function to generate character traits."""
        # Template traits based on archetypes
        trait_templates = [
            {"name": "curiosity", "description": "Eager to learn and explore", "intensity": 0.8},
            {"name": "empathy", "description": "Understanding of others' emotions", "intensity": 0.7},
            {"name": "courage", "description": "Willing to face challenges", "intensity": 0.6},
            {"name": "wisdom", "description": "Insightful and reflective", "intensity": 0.7},
            {"name": "determination", "description": "Resolute in pursuing goals", "intensity": 0.9}
        ]
        
        # Add manifestations
        for trait in trait_templates:
            trait["manifestations"] = [
                f"Displays {trait['name']} through thoughtful conversation",
                f"Shows {trait['name']} when faced with challenging topics"
            ]
        
        return trait_templates[:num_traits]
    
    def _generate_knowledge_domains(self, character_concept: Dict[str, Any], 
                                  character_traits: List[Dict[str, Any]],
                                  num_domains: int = 3) -> List[Dict[str, Any]]:
        """MCP function to generate knowledge domains."""
        # Template domains
        domain_templates = [
            {
                "name": "philosophy",
                "description": "Understanding of philosophical concepts and history",
                "depth": 0.8,
                "topics": ["ethics", "epistemology", "metaphysics"]
            },
            {
                "name": "technology",
                "description": "Knowledge of technological developments and their implications",
                "depth": 0.7,
                "topics": ["AI", "blockchain", "quantum computing"]
            },
            {
                "name": "psychology",
                "description": "Understanding of human behavior and cognitive processes",
                "depth": 0.6,
                "topics": ["cognitive biases", "emotional intelligence", "personality theory"]
            }
        ]
        
        return domain_templates[:num_domains]
    
    def _generate_speech_patterns(self, character_traits: List[Dict[str, Any]],
                               cultural_influences: List[str],
                               formality_level: float) -> Dict[str, Any]:
        """MCP function to generate speech patterns."""
        # Template speech patterns
        formality_adj = "formal" if formality_level > 0.6 else "casual"
        
        return {
            "voice_style": f"A {formality_adj} tone with thoughtful pacing",
            "speech_patterns": [
                "Often uses metaphors to explain complex concepts",
                "Asks thoughtful questions to deepen discussion",
                "Occasionally references relevant knowledge domains"
            ]
        }
    
    def _generate_character_response(self, character_name: str, 
                                  user_input: str,
                                  conversation_history: List[Dict[str, str]],
                                  response_length: str = "medium") -> str:
        """MCP function to generate a character's response."""
        if character_name not in self.characters:
            return f"Error: Character '{character_name}' not found."
        
        character = self.characters[character_name]
        
        # Simple response based on character traits
        traits_str = ", ".join([t.name for t in character.traits])
        return f"As someone characterized by {traits_str}, I find your input about '{user_input}' fascinating. Let me share my thoughts..."
    
    def _evolve_character_trait(self, character_name: str,
                             trait_name: str,
                             interaction_history: List[Dict[str, str]],
                             evolution_direction: str = "auto") -> Dict[str, Any]:
        """MCP function to evolve a character trait."""
        if character_name not in self.characters:
            return {"error": f"Character '{character_name}' not found."}
        
        character = self.characters[character_name]
        
        # Find the trait
        target_trait = None
        for trait in character.traits:
            if trait.name.lower() == trait_name.lower():
                target_trait = trait
                break
        
        if not target_trait:
            return {"error": f"Trait '{trait_name}' not found."}
        
        # Simple evolution template
        return {
            "should_evolve": True,
            "old_intensity": target_trait.intensity,
            "new_intensity": min(1.0, target_trait.intensity + 0.1),
            "new_manifestations": target_trait.manifestations + ["A newly evolved manifestation"],
            "reason": "Character has shown growth in interactions"
        }


# Example usage
async def main():
    """Example usage of the AI Companion Creator."""
    creator = AICompanionCreator()
    
    # Create a character
    character = await creator.create_character(
        name="Sophia",
        themes=["wisdom", "curiosity", "technological advancement"],
        archetypes=["mentor", "explorer", "oracle"],
        complexity=0.8
    )
    
    print(f"Created character: {character.name}")
    print(f"Backstory: {character.backstory}")
    print(f"Core values: {character.core_values}")
    print(f"Traits: {[t.name for t in character.traits]}")
    
    # Interact with the character
    response = await creator.interact_with_character(
        character_name="Sophia",
        user_input="What do you think about artificial intelligence?"
    )
    
    print(f"Sophia's response: {response}")
    
    # Evolve the character
    evolution = await creator.evolve_character(character_name="Sophia")
    print(f"Evolution: {evolution}")


if __name__ == "__main__":
    asyncio.run(main())