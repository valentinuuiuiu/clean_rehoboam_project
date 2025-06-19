"""
T2L-Inspired Smart Contract Auditor Engine for Rehoboam.

This module defines the T2LAuditorEngine class, which is envisioned to use
Task-To-LoRA (T2L) inspired mechanisms for dynamically generating or selecting
specialized LoRA adapters for auditing smart contracts based on specific tasks.
The initial implementation will use simulated embeddings and LoRA configurations.
"""

import os
import logging
import json
import httpx
from typing import Optional, Dict, Any, List

# Attempt to import from a central Config class first
try:
    from config import Config
    OPENROUTER_API_KEY = Config.OPENROUTER_API_KEY
    OPENROUTER_API_BASE_URL = Config.OPENROUTER_API_BASE_URL
    OPENROUTER_DEFAULT_MODEL = Config.OPENROUTER_DEFAULT_MODEL
    OPENROUTER_CHAT_ENDPOINT = Config.OPENROUTER_CHAT_ENDPOINT
except (ImportError, AttributeError):
    # Fallback to direct import from config module if Config class is not used or constants are module-level
    try:
        from config import OPENROUTER_API_KEY, OPENROUTER_API_BASE_URL, OPENROUTER_DEFAULT_MODEL, OPENROUTER_CHAT_ENDPOINT
    except ImportError:
        # Last resort: Use environment variables directly or define defaults if config.py is missing
        logging.warning("Could not import OpenRouter config from 'config.py'. Using environment variables or defaults.")
        OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
        OPENROUTER_API_BASE_URL = os.getenv("OPENROUTER_API_BASE_URL", "https://openrouter.ai/api/v1")
        OPENROUTER_DEFAULT_MODEL = os.getenv("OPENROUTER_DEFAULT_MODEL", "google/gemini-flash-1.5")
        OPENROUTER_CHAT_ENDPOINT = os.getenv("OPENROUTER_CHAT_ENDPOINT", "/chat/completions")


class T2LAuditorEngine:
    """
    A T2L-inspired engine to generate specialized auditing configurations and perform audits.
    Current version uses simulated embeddings and LoRA adapter configurations for internal decision-making,
    and then calls an LLM (via OpenRouter) for the actual audit.
    """

    def __init__(self):
        """
        Initializes the T2LAuditorEngine.
        """
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers: # Avoid duplicate handlers
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.api_key = OPENROUTER_API_KEY
        self.model_name = OPENROUTER_DEFAULT_MODEL
        self.base_url = OPENROUTER_API_BASE_URL
        self.chat_endpoint = OPENROUTER_CHAT_ENDPOINT

        self.client = httpx.AsyncClient(timeout=120.0) # Increased timeout for LLM responses

        if self.api_key:
            self.logger.info("T2L Auditor Engine initialized. OpenRouter API Key is configured.")
        else:
            self.logger.warning("T2L Auditor Engine initialized, but OpenRouter API Key is MISSING. Audit calls will fail.")
        self.logger.info(f"Default Model: {self.model_name}")
        self.logger.info(f"Base URL: {self.base_url}")

    async def _get_task_embedding(self, task_description: str, contract_snippet: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        (Simulated) Generates a task embedding based on the description and contract snippet.
        """
        if not task_description:
            self.logger.warning("Task description is empty, cannot generate embedding.")
            return None
        self.logger.info(f"Simulating task embedding generation for: {task_description[:100]}...")
        if contract_snippet:
            self.logger.info("Contract snippet provided and would be part of real embedding generation.")
        # TODO: Implement real embedding generation (e.g., via OpenRouter or local model)
        vector_length = 10
        simulated_vector = [(abs(hash(task_description + str(i))) % 1000) / 1000.0 for i in range(vector_length)]
        return {
            "task_description": task_description,
            "contract_snippet_present": bool(contract_snippet),
            "simulated_embedding_vector": simulated_vector,
            "embedding_model_simulated": "text-embedding-mock-v1",
            "engine_version": "sim_v1.0"
        }

    async def _generate_lora_adapter_config(self, task_embedding: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        (Simulated) Generates a conceptual LoRA adapter configuration based on a task embedding.
        """
        if not task_embedding or not task_embedding.get("task_description"):
            self.logger.warning("Cannot generate LoRA adapter config: Invalid or missing task embedding/description.")
            return None
        task_desc_lower = task_embedding.get("task_description", "").lower()
        self.logger.info(f"Simulating LoRA adapter configuration for task: {task_desc_lower[:100]}...")
        # TODO: Implement real T2L hypernetwork logic or interface to select/generate LoRA adapters.
        adapter_type = "general_solidity_auditor"
        specialization = "Provides a general audit for common Solidity issues."
        if "reentrancy" in task_desc_lower:
            adapter_type = "reentrancy_detector"
            specialization = "Detects reentrancy vulnerabilities using control flow analysis patterns."
        elif "gas" in task_desc_lower or "optimization" in task_desc_lower:
            adapter_type = "gas_optimizer_analyzer"
            specialization = "Analyzes gas usage patterns and suggests optimizations."
        elif "access control" in task_desc_lower or "auth" in task_desc_lower:
            adapter_type = "access_control_auditor"
            specialization = "Focuses on ownership, roles, and modifier correctness."
        elif "erc20" in task_desc_lower or "token standard" in task_desc_lower:
            adapter_type = "token_standard_compliance"
            specialization = "Checks for compliance with token standards like ERC20, ERC721."
        embedding_sum = sum(task_embedding.get("simulated_embedding_vector", [0.1]))
        specialization_level = 0.75 + (embedding_sum % 0.25)
        return {
            "adapter_name": f"sim_lora_{adapter_type}_{os.urandom(2).hex()}",
            "adapter_type": adapter_type,
            "description": specialization,
            "specialization_level": round(specialization_level, 2),
            "target_llm_layers_conceptual": ["attention_qkv", "feed_forward"],
            "based_on_task_description": task_embedding.get("task_description"),
            "simulated_source_embedding_hash": hex(abs(hash(json.dumps(task_embedding.get("simulated_embedding_vector")))))
        }

    def construct_audit_prompt(self, contract_code: str, audit_task_description: str, simulated_lora_config: Optional[Dict[str, Any]]) -> str:
        """
        Constructs a detailed audit prompt for the LLM.

        Args:
            contract_code: The smart contract code to be audited.
            audit_task_description: The specific task or focus for the audit.
            simulated_lora_config: The (simulated) LoRA adapter configuration.

        Returns:
            A string representing the fully constructed prompt.
        """
        lora_config_str = "No specific LoRA adapter configuration applied (using default model capabilities)."
        if simulated_lora_config is not None: # Condition already corrected, ensuring it stays this way
            try:
                lora_config_str = json.dumps(simulated_lora_config, indent=2)
            except TypeError:
                lora_config_str = str(simulated_lora_config) # Fallback if not JSON serializable

        prompt = f"""
You are an expert AI smart contract auditing assistant, specialized by a dynamic conceptual LoRA configuration.
        Your current specialization profile: {simulated_lora_config.get('adapter_type', 'general audit') if simulated_lora_config is not None else 'general audit'}
Focused on: {audit_task_description}
Conceptual LoRA details:
{lora_config_str}

Audit Task: {audit_task_description}
Contract Code to Audit:
```solidity
{contract_code}
```

Please provide your audit findings. Structure your response as a single, valid JSON object with the following schema:
{{
    "audit_summary": "A brief summary of your overall findings.",
    "vulnerability_findings": [
        {{
            "id": "finding_001",
            "title": "Descriptive title of the finding (e.g., Potential Reentrancy Vulnerability)",
            "description": "Detailed explanation of the issue, including where it occurs in the code and potential impact.",
            "severity": "Critical / High / Medium / Low / Informational",
            "recommendation": "Specific, actionable steps to mitigate or fix the issue.",
            "code_references": [ {{ "lines": "L10-L15", "function_context": "withdraw()" }} ]
        }}
    ],
    "gas_optimization_notes": [
        {{
            "id": "gas_opt_001",
            "suggestion": "Specific gas optimization suggestion.",
            "potential_saving": "Small / Medium / Large / Specific gas units if calculable",
            "code_references": [ {{ "lines": "L20", "variable_or_function": "myVar" }} ]
        }}
    ],
    "code_quality_observations": [
         {{
            "id": "quality_001",
            "observation": "Observation about code style, best practices, or readability.",
            "recommendation": "Suggestion for improvement.",
            "code_references": [ {{ "lines": "L50-L55" }} ]
         }}
    ],
    "overall_security_rating": "Excellent / Good / Fair / Poor / Critical",
    "audit_confidence_score": 0.0
}}
Ensure your output is ONLY the single, valid JSON object requested, without any surrounding text or explanations.
The JSON should be complete and parseable.
"""
        self.logger.info(f"Constructed audit prompt for task '{audit_task_description[:50]}...'. Prompt length: {len(prompt)}")
        self.logger.debug(f"Prompt snippet: {prompt[:500]}...")
        return prompt

    async def perform_audit(self, contract_code: str, audit_task_description: str) -> Optional[Dict[str, Any]]:
        """
        Performs a smart contract audit using the T2L-inspired approach.

        Args:
            contract_code: The smart contract code as a string.
            audit_task_description: A description of the specific audit task.

        Returns:
            A dictionary containing the structured audit results, or None if an error occurs.
        """
        self.logger.info(f"Starting audit for task: {audit_task_description}")

        if not self.api_key:
            self.logger.error("OpenRouter API Key is not configured. Cannot perform audit.")
            return None

        task_embedding = await self._get_task_embedding(audit_task_description, contract_code[:500])
        if not task_embedding:
            self.logger.error("Failed to generate task embedding. Aborting audit.")
            return None

        lora_config = await self._generate_lora_adapter_config(task_embedding)
        if not lora_config:
            self.logger.warning("Failed to generate LoRA adapter configuration. Proceeding with default model capabilities for prompt.")
            # Proceed without specific LoRA details in prompt, or use a default placeholder
            lora_config = {"adapter_type": "general_fallback", "description": "Using general model capabilities due to LoRA config failure."}


        prompt = self.construct_audit_prompt(contract_code, audit_task_description, lora_config)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            # "response_format": {"type": "json_object"} # Included in prompt, some models might not support this field
        }
        # Some models like Gemini might prefer system prompts or specific user/assistant turn structures.
        # For OpenRouter, the simple user message with detailed instructions is usually a good start.

        self.logger.info(f"Sending audit request to OpenRouter for model {self.model_name}...")

        raw_llm_response_content = None
        try:
            response = await self.client.post(
                f"{self.base_url.rstrip('/')}{self.chat_endpoint.lstrip('/')}",
                headers=headers,
                json=payload
            )
            response.raise_for_status()  # Raise an exception for HTTP errors

            response_json = response.json()
            self.logger.debug(f"Full API response: {response_json}")

            if not response_json.get("choices") or not response_json["choices"][0].get("message") or \
               not response_json["choices"][0]["message"].get("content"):
                self.logger.error("Invalid response structure from OpenRouter.")
                self.logger.debug(f"Problematic response: {response_json}")
                return None

            raw_llm_response_content = response_json["choices"][0]["message"]["content"]
            self.logger.info("Successfully received response from LLM.")
            self.logger.debug(f"Raw LLM content snippet: {raw_llm_response_content[:500]}...")

            # Attempt to parse the LLM's string content as JSON
            # The prompt asks for JSON, but LLMs can make mistakes.
            # Strip potential markdown ```json ... ``` fences
            if raw_llm_response_content.startswith("```json"):
                raw_llm_response_content = raw_llm_response_content[7:]
                if raw_llm_response_content.endswith("```"):
                    raw_llm_response_content = raw_llm_response_content[:-3]

            audit_result = json.loads(raw_llm_response_content.strip())
            self.logger.info("Successfully parsed LLM response content as JSON.")
            return audit_result

        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error during OpenRouter API call: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            self.logger.error(f"Network error during OpenRouter API call: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON from LLM response string: {e}")
            self.logger.error(f"LLM Raw Content that failed parsing: {raw_llm_response_content}") # Log the problematic string
            return None
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during audit: {e}")
            return None


if __name__ == '__main__':
    import asyncio

    async def main_test():
        engine = T2LAuditorEngine()

        if not engine.api_key:
            print("\nWARNING: OpenRouter API Key is not set. LLM audit calls will fail.")
            # You might want to skip the perform_audit part if no key is set
            # return

        print("\n--- Testing Task Embedding Generation (Simulated) ---")
        test_task_1 = "Audit for reentrancy vulnerabilities in a DeFi lending pool."
        embedding1 = await engine._get_task_embedding(test_task_1, "contract snippet here...")
        if embedding1: print(json.dumps(embedding1, indent=2, ensure_ascii=False))

        print("\n--- Testing LoRA Adapter Configuration (Simulated) ---")
        lora_config1 = await engine._generate_lora_adapter_config(embedding1)
        if lora_config1: print(json.dumps(lora_config1, indent=2, ensure_ascii=False))

        print("\n--- Testing Audit Prompt Construction ---")
        sample_contract_code = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleBank {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        // Potential reentrancy vulnerability if not using Checks-Effects-Interactions
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed.");
        balances[msg.sender] -= amount;
    }
}
"""
        prompt = engine.construct_audit_prompt(sample_contract_code, test_task_1, lora_config1)
        print(f"Generated prompt (first 500 chars):\n{prompt[:500]}...")

        print("\n--- Testing perform_audit ---")
        if engine.api_key: # Only run if API key is present
            audit_result = await engine.perform_audit(sample_contract_code, test_task_1)
            if audit_result:
                print("Audit Result:")
                print(json.dumps(audit_result, indent=2, ensure_ascii=False))
            else:
                print("Audit failed or returned no result.")
        else:
            print("Skipping perform_audit test as API key is not set.")

    asyncio.run(main_test())
