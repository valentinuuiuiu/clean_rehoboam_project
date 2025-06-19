import pytest
import json
from unittest.mock import patch, MagicMock

from utils.t2l_auditor_engine import T2LAuditorEngine

# Default mock config values for the engine's __init__
MOCK_API_KEY = "test_openrouter_api_key"
MOCK_MODEL_NAME = "test/model"
MOCK_BASE_URL = "https://testurl.com/api/v1"
MOCK_CHAT_ENDPOINT = "/test_chat"

@pytest.fixture
def auditor_engine():
    """
    Provides an instance of T2LAuditorEngine with mocked config values
    for testing synchronous methods like construct_audit_prompt.
    """
    # Patch the configuration constants at the module level where T2LAuditorEngine reads them.
    # This assumes the fallback mechanism in T2LAuditorEngine's import block is triggered
    # if `from config import Config` fails, or if these are directly imported.
    with patch('utils.t2l_auditor_engine.OPENROUTER_API_KEY', MOCK_API_KEY), \
         patch('utils.t2l_auditor_engine.OPENROUTER_DEFAULT_MODEL', MOCK_MODEL_NAME), \
         patch('utils.t2l_auditor_engine.OPENROUTER_API_BASE_URL', MOCK_BASE_URL), \
         patch('utils.t2l_auditor_engine.OPENROUTER_CHAT_ENDPOINT', MOCK_CHAT_ENDPOINT):
        engine = T2LAuditorEngine()
    return engine

def test_auditor_engine_initialization(auditor_engine: T2LAuditorEngine):
    """Test that the engine initializes correctly with patched config."""
    assert auditor_engine.api_key == MOCK_API_KEY
    assert auditor_engine.model_name == MOCK_MODEL_NAME
    assert auditor_engine.base_url == MOCK_BASE_URL
    assert auditor_engine.chat_endpoint == MOCK_CHAT_ENDPOINT
    assert auditor_engine.logger is not None
    assert auditor_engine.client is not None

# --- Test Cases for construct_audit_prompt ---

SAMPLE_CONTRACT_CODE = """
pragma solidity ^0.8.0;
contract Sample {
    uint public value;
    function setValue(uint _value) public {
        value = _value;
    }
}
"""

def test_construct_audit_prompt_basic(auditor_engine: T2LAuditorEngine):
    """Test basic prompt construction with all parts present."""
    contract_code = SAMPLE_CONTRACT_CODE
    audit_task_description = "Check for basic overflow/underflow issues."
    simulated_lora_config = {
        "adapter_type": "overflow_checker",
        "specialization_level": 0.9,
        "description": "Focuses on integer arithmetic."
    }

    prompt = auditor_engine.construct_audit_prompt(contract_code, audit_task_description, simulated_lora_config)

    assert isinstance(prompt, str)
    assert contract_code in prompt
    assert audit_task_description in prompt
    assert simulated_lora_config["adapter_type"] in prompt
    assert simulated_lora_config["description"] in prompt
    assert "audit_summary" in prompt
    assert "vulnerability_findings" in prompt # Updated key from prompt
    assert "severity" in prompt
    assert "recommendation" in prompt
    assert "gas_optimization_notes" in prompt
    assert "code_quality_observations" in prompt # Updated key from prompt
    assert "overall_security_rating" in prompt # Updated key from prompt
    assert "audit_confidence_score" in prompt
    assert "```solidity" in prompt # Ensure code block formatting
    assert "You are an expert AI smart contract auditing assistant" in prompt
    assert "Ensure your output is ONLY the single, valid JSON object requested" in prompt

def test_construct_audit_prompt_no_lora_config(auditor_engine: T2LAuditorEngine):
    """Test prompt construction when simulated_lora_config is None."""
    contract_code = SAMPLE_CONTRACT_CODE
    audit_task_description = "General security review."

    prompt = auditor_engine.construct_audit_prompt(contract_code, audit_task_description, None)

    assert isinstance(prompt, str)
    assert contract_code in prompt
    assert audit_task_description in prompt
    assert "No specific LoRA adapter configuration applied" in prompt
    assert "(using default model capabilities)" in prompt # More specific part
    assert "audit_summary" in prompt # Check for JSON schema presence

def test_construct_audit_prompt_empty_lora_config(auditor_engine: T2LAuditorEngine):
    """Test prompt construction when simulated_lora_config is an empty dict."""
    contract_code = SAMPLE_CONTRACT_CODE
    audit_task_description = "Review for best practices."
    simulated_lora_config = {} # Empty dict

    prompt = auditor_engine.construct_audit_prompt(contract_code, audit_task_description, simulated_lora_config)

    assert isinstance(prompt, str)
    assert contract_code in prompt
    assert audit_task_description in prompt
    # json.dumps({}, indent=2) produces "{}" for an empty dict
    assert "{}" in prompt
    assert simulated_lora_config.get('adapter_type', 'general audit') in prompt # Should be 'general audit'
    assert "audit_summary" in prompt

@pytest.mark.parametrize("task_desc, lora_adapter_type_keyword, lora_desc_keyword", [
    ("Focus on reentrancy vulnerabilities.", "reentrancy_detector", "reentrancy"),
    ("Optimize gas usage for all public functions.", "gas_optimizer_analyzer", "gas usage"),
    ("Verify ERC20 compliance thoroughly.", "token_standard_compliance", "token standards"),
    ("Check access control for owner-only functions.", "access_control_auditor", "ownership")
])
def test_construct_audit_prompt_different_tasks(auditor_engine: T2LAuditorEngine, task_desc, lora_adapter_type_keyword, lora_desc_keyword):
    """Test prompt customization for different tasks and (simulated) LoRA configs."""
    contract_code = SAMPLE_CONTRACT_CODE
    # Simulate a LoRA config that would be generated for this task
    simulated_lora_config = {
        "adapter_type": lora_adapter_type_keyword, # This should match the expected specialization
        "description": f"Simulated LoRA focusing on {lora_desc_keyword}",
        "specialization_level": 0.88,
        "based_on_task_description": task_desc
    }

    prompt = auditor_engine.construct_audit_prompt(contract_code, task_desc, simulated_lora_config)

    assert isinstance(prompt, str)
    assert contract_code in prompt
    assert task_desc in prompt # The original task description
    assert lora_adapter_type_keyword in prompt # Check if the adapter type from LoRA config is in prompt
    assert lora_desc_keyword in prompt # Check if part of LoRA description is in prompt
    assert "audit_summary" in prompt
    assert "vulnerability_findings" in prompt

def test_prompt_contains_json_schema_keywords(auditor_engine: T2LAuditorEngine):
    """Explicitly test for all main keys of the requested JSON schema."""
    prompt = auditor_engine.construct_audit_prompt("test code", "test task", None)

    expected_keys = [
        "audit_summary", "vulnerability_findings", "id", "title", "description",
        "severity", "recommendation", "code_references", "lines", "function_context",
        "gas_optimization_notes", "suggestion", "potential_saving",
        "code_quality_observations", "observation",
        "overall_security_rating", "audit_confidence_score"
    ]
    for key in expected_keys:
        assert f'"{key}"' in prompt # Check for keys as they'd appear in JSON schema example
    assert "```solidity" in prompt
    assert "Please provide your audit findings. Structure your response as a single, valid JSON object" in prompt
    assert "Ensure your output is ONLY the single, valid JSON object requested" in prompt
