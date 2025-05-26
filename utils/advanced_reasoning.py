"""
Advanced multi-model reasoning orchestration system for Rehoboam AI.
Integrates DeepSeek, Gemini, and OpenAI models with intelligent routing.
"""
import os
import json
import time
import logging
import asyncio
import requests
import random
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

class ModelRequest:
    """Representation of a request to an AI model."""
    
    def __init__(self, prompt: str, provider: str = None, model: str = None, 
                task_type: str = None, complexity: int = None, timeout: int = 30):
        self.prompt = prompt
        self.provider = provider  # 'deepseek', 'gemini', 'openai'
        self.model = model  # specific model name
        self.task_type = task_type or self._infer_task_type(prompt)
        self.complexity = complexity or self._infer_complexity(prompt)
        self.timeout = timeout
        self.timestamp = time.time()
        self.id = f"{int(self.timestamp)}_{random.randint(1000, 9999)}"
    
    def _infer_task_type(self, prompt: str) -> str:
        """Infer the type of task from the prompt."""
        prompt_lower = prompt.lower()
        
        if "analyze" in prompt_lower or "predict" in prompt_lower or "forecast" in prompt_lower:
            return "analysis"
        elif "explain" in prompt_lower or "describe" in prompt_lower:
            return "explanation"
        elif "create" in prompt_lower or "generate" in prompt_lower:
            return "creation"
        elif "optimize" in prompt_lower or "improve" in prompt_lower:
            return "optimization"
        elif "recommend" in prompt_lower or "suggest" in prompt_lower:
            return "recommendation"
        else:
            return "general"
    
    def _infer_complexity(self, prompt: str) -> int:
        """Infer the complexity of the task on a scale of 1-10."""
        # Complexity factors:
        # - Length of prompt
        # - Presence of technical terms
        # - Number of constraints or requirements
        # - Level of analysis required
        
        complexity = 5  # Default medium complexity
        
        # Adjust based on length
        words = prompt.split()
        if len(words) > 200:
            complexity += 2
        elif len(words) > 100:
            complexity += 1
        
        # Adjust based on technical terms
        technical_terms = [
            "blockchain", "rollup", "layer 2", "arbitrage", "liquidity", 
            "volatility", "correlation", "regression", "non-linear", 
            "consciousness", "quantum", "optimization"
        ]
        
        tech_term_count = sum(1 for term in technical_terms if term in prompt.lower())
        complexity += min(2, tech_term_count // 2)
        
        # Adjust based on analysis requirements
        analysis_terms = ["analyze", "compare", "evaluate", "assess", "calculate", "compute"]
        if any(term in prompt.lower() for term in analysis_terms):
            complexity += 1
        
        # Cap complexity
        return min(10, max(1, complexity))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "prompt": self.prompt,
            "provider": self.provider,
            "model": self.model,
            "task_type": self.task_type,
            "complexity": self.complexity,
            "timeout": self.timeout,
            "timestamp": self.timestamp
        }


class ModelResponse:
    """Representation of a response from an AI model."""
    
    def __init__(self, request_id: str, content: str, provider: str, model: str,
                latency: float, success: bool, error: str = None):
        self.request_id = request_id
        self.content = content
        self.provider = provider
        self.model = model
        self.latency = latency
        self.success = success
        self.error = error
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "content": self.content,
            "provider": self.provider,
            "model": self.model,
            "latency": self.latency,
            "success": self.success,
            "error": self.error,
            "timestamp": self.timestamp
        }


class ModelPerformanceTracker:
    """Track performance metrics of different models."""
    
    def __init__(self):
        self.performance_data = {
            "deepseek": {
                "success_rate": 0.95,
                "avg_latency": 2.0,
                "last_failure": None,
                "requests": 0,
                "successes": 0,
                "failures": 0,
                "task_performance": {
                    "analysis": 0.9,
                    "explanation": 0.95,
                    "creation": 0.85,
                    "optimization": 0.9,
                    "recommendation": 0.85,
                    "general": 0.9
                },
                "complexity_performance": {
                    # complexity: success_rate
                    1: 0.99, 2: 0.99, 3: 0.98, 4: 0.97, 5: 0.95,
                    6: 0.93, 7: 0.9, 8: 0.85, 9: 0.8, 10: 0.75
                }
            },
            "gemini": {
                "success_rate": 0.97,
                "avg_latency": 1.8,
                "last_failure": None,
                "requests": 0,
                "successes": 0,
                "failures": 0,
                "task_performance": {
                    "analysis": 0.95,
                    "explanation": 0.98,
                    "creation": 0.9,
                    "optimization": 0.85,
                    "recommendation": 0.9,
                    "general": 0.95
                },
                "complexity_performance": {
                    # complexity: success_rate
                    1: 0.99, 2: 0.99, 3: 0.98, 4: 0.97, 5: 0.96,
                    6: 0.95, 7: 0.93, 8: 0.9, 9: 0.85, 10: 0.8
                }
            },
            "openai": {
                "success_rate": 0.98,
                "avg_latency": 1.5,
                "last_failure": None,
                "requests": 0,
                "successes": 0,
                "failures": 0,
                "task_performance": {
                    "analysis": 0.98,
                    "explanation": 0.97,
                    "creation": 0.95,
                    "optimization": 0.9,
                    "recommendation": 0.95,
                    "general": 0.98
                },
                "complexity_performance": {
                    # complexity: success_rate
                    1: 0.99, 2: 0.99, 3: 0.99, 4: 0.98, 5: 0.97,
                    6: 0.96, 7: 0.94, 8: 0.92, 9: 0.88, 10: 0.85
                }
            }
        }
    
    def update_performance(self, response: ModelResponse):
        """Update performance metrics based on a response."""
        provider = response.provider
        
        if provider not in self.performance_data:
            logger.warning(f"Unknown provider: {provider}")
            return
        
        # Update request counts
        self.performance_data[provider]["requests"] += 1
        
        if response.success:
            self.performance_data[provider]["successes"] += 1
        else:
            self.performance_data[provider]["failures"] += 1
            self.performance_data[provider]["last_failure"] = time.time()
        
        # Update success rate
        total_requests = self.performance_data[provider]["requests"]
        total_successes = self.performance_data[provider]["successes"]
        self.performance_data[provider]["success_rate"] = total_successes / total_requests if total_requests > 0 else 0
        
        # Update latency with exponential moving average
        current_avg = self.performance_data[provider]["avg_latency"]
        alpha = 0.1  # Smoothing factor
        self.performance_data[provider]["avg_latency"] = alpha * response.latency + (1 - alpha) * current_avg
    
    def get_best_provider(self, request: ModelRequest) -> str:
        """Get the best provider for a given request based on performance history."""
        task_type = request.task_type
        complexity = request.complexity
        
        # Weights for different factors
        weights = {
            "success_rate": 0.4,
            "task_performance": 0.3,
            "complexity_performance": 0.2,
            "latency": 0.1
        }
        
        scores = {}
        
        for provider, data in self.performance_data.items():
            # Skip provider if recently failed (backoff strategy)
            last_failure = data["last_failure"]
            if last_failure and time.time() - last_failure < 300:  # 5 minutes backoff
                scores[provider] = 0
                continue
            
            # Calculate score components
            success_rate_score = data["success_rate"]
            task_score = data["task_performance"].get(task_type, 0.8)
            complexity_score = data["complexity_performance"].get(complexity, 0.8)
            
            # Normalize latency score (lower is better)
            max_latency = max(p["avg_latency"] for p in self.performance_data.values())
            min_latency = min(p["avg_latency"] for p in self.performance_data.values())
            latency_range = max_latency - min_latency
            latency_score = 1.0 - ((data["avg_latency"] - min_latency) / latency_range) if latency_range > 0 else 0.5
            
            # Calculate weighted score
            scores[provider] = (
                weights["success_rate"] * success_rate_score +
                weights["task_performance"] * task_score +
                weights["complexity_performance"] * complexity_score +
                weights["latency"] * latency_score
            )
        
        # Return the provider with the highest score
        if not scores:
            return "deepseek"  # Default to DeepSeek if no scores
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def get_fallback_provider(self, primary_provider: str) -> str:
        """Get a fallback provider different from the primary provider."""
        providers = list(self.performance_data.keys())
        fallback_providers = [p for p in providers if p != primary_provider]
        
        if not fallback_providers:
            return primary_provider  # No alternative
        
        # Sort by success rate
        fallback_providers.sort(
            key=lambda p: self.performance_data[p]["success_rate"], 
            reverse=True
        )
        
        return fallback_providers[0]


class MultimodalOrchestrator:
    """Orchestrates requests across multiple AI providers for optimal performance."""
    
    def __init__(self):
        # API keys and configuration
        self.api_keys = {
            "deepseek": os.environ.get("DEEPSEEK_API_KEY"),
            "gemini": os.environ.get("GEMINI_API_KEY"),
            "openai": os.environ.get("OPENAI_API_KEY")
        }
        
        # Model configurations
        self.model_configs = {
            "deepseek": {
                "api_base_url": "https://api.deepseek.com/v1",
                "models": {
                    "default": "deepseek-coder-v1.5-instruct",
                    "vision": "deepseek-vl",
                    "chat": "deepseek-chat"
                }
            },
            "gemini": {
                "api_base_url": "https://generativelanguage.googleapis.com/v1",
                "models": {
                    "default": "gemini-1.5-pro",
                    "vision": "gemini-1.5-pro-vision",
                    "chat": "gemini-1.5-pro",
                    "lite": "gemini-1.5-flash"
                }
            },
            "openai": {
                "api_base_url": "https://api.openai.com/v1",
                "models": {
                    "default": "gpt-4o",
                    "vision": "gpt-4o",
                    "chat": "gpt-4o",
                    "lite": "gpt-4o-mini"
                }
            }
        }
        
        # Performance tracking
        self.performance_tracker = ModelPerformanceTracker()
        
        # Request history
        self.request_history = []
        self.response_history = []
        self.max_history_size = 100
        
        # Cache for responses
        self.response_cache = {}
        self.cache_duration = 3600  # 1 hour
        
        # Rate limiting
        self.rate_limits = {
            "deepseek": {"requests_per_minute": 50, "last_request": 0},
            "gemini": {"requests_per_minute": 60, "last_request": 0},
            "openai": {"requests_per_minute": 60, "last_request": 0}
        }
        
        logger.info("MultimodalOrchestrator initialized")
    
    def _get_provider_headers(self, provider: str) -> Dict[str, str]:
        """Get API request headers for a provider."""
        api_key = self.api_keys.get(provider)
        
        if not api_key:
            raise ValueError(f"No API key for {provider}")
        
        if provider == "deepseek" or provider == "openai":
            return {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        elif provider == "gemini":
            return {
                "Content-Type": "application/json"
            }
        else:
            return {"Content-Type": "application/json"}
    
    def _get_model_for_task(self, provider: str, task_type: str, complexity: int) -> str:
        """Get the appropriate model for a task type and complexity."""
        if provider not in self.model_configs:
            raise ValueError(f"Unknown provider: {provider}")
        
        models = self.model_configs[provider]["models"]
        
        # Use a simplified selection strategy
        if task_type == "analysis" and complexity >= 8:
            return models.get("default")  # Use most powerful model for complex analysis
        elif complexity >= 7:
            return models.get("default")  # Use powerful model for high complexity
        elif task_type in ["explanation", "recommendation"]:
            return models.get("chat", models.get("default"))
        elif complexity <= 4:
            return models.get("lite", models.get("default"))  # Use lightweight model for simple tasks
        else:
            return models.get("default")
    
    def _apply_rate_limiting(self, provider: str):
        """Apply rate limiting for a provider."""
        rate_limit = self.rate_limits.get(provider, {"requests_per_minute": 50, "last_request": 0})
        requests_per_minute = rate_limit["requests_per_minute"]
        min_interval = 60 / requests_per_minute  # Minimum seconds between requests
        
        elapsed = time.time() - rate_limit["last_request"]
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        
        self.rate_limits[provider]["last_request"] = time.time()
    
    def _check_cache(self, prompt: str) -> Optional[ModelResponse]:
        """Check if a response is in the cache."""
        cache_key = self._get_cache_key(prompt)
        
        if cache_key in self.response_cache:
            cached_item = self.response_cache[cache_key]
            if time.time() - cached_item["timestamp"] < self.cache_duration:
                return cached_item["response"]
        
        return None
    
    def _update_cache(self, prompt: str, response: ModelResponse):
        """Update the response cache."""
        cache_key = self._get_cache_key(prompt)
        
        self.response_cache[cache_key] = {
            "response": response,
            "timestamp": time.time()
        }
        
        # Prune cache if too large
        if len(self.response_cache) > 1000:
            # Remove oldest entries
            oldest_keys = sorted(
                self.response_cache.keys(),
                key=lambda k: self.response_cache[k]["timestamp"]
            )[:100]
            
            for key in oldest_keys:
                del self.response_cache[key]
    
    def _get_cache_key(self, prompt: str) -> str:
        """Generate a cache key for a prompt."""
        import hashlib
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def _update_history(self, request: ModelRequest, response: ModelResponse):
        """Update request and response history."""
        self.request_history.append(request.to_dict())
        self.response_history.append(response.to_dict())
        
        # Prune history if too large
        if len(self.request_history) > self.max_history_size:
            self.request_history = self.request_history[-self.max_history_size:]
        
        if len(self.response_history) > self.max_history_size:
            self.response_history = self.response_history[-self.max_history_size:]
    
    def _call_deepseek_api(self, prompt: str, model: str) -> Tuple[str, float, bool, str]:
        """Call the DeepSeek API."""
        start_time = time.time()
        content = ""
        success = False
        error = None
        
        try:
            if not self.api_keys.get("deepseek"):
                raise ValueError("DeepSeek API key not available")
            
            self._apply_rate_limiting("deepseek")
            
            headers = self._get_provider_headers("deepseek")
            api_base_url = self.model_configs["deepseek"]["api_base_url"]
            
            data = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 2000
            }
            
            response = requests.post(
                f"{api_base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if not response.ok:
                error = f"DeepSeek API error: {response.status_code} - {response.text}"
                logger.error(error)
                return content, time.time() - start_time, False, error
            
            response_data = response.json()
            content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            success = True
            
        except Exception as e:
            error = f"Error calling DeepSeek API: {str(e)}"
            logger.error(error)
            
        return content, time.time() - start_time, success, error
    
    def _call_gemini_api(self, prompt: str, model: str) -> Tuple[str, float, bool, str]:
        """Call the Gemini API."""
        start_time = time.time()
        content = ""
        success = False
        error = None
        
        try:
            if not self.api_keys.get("gemini"):
                raise ValueError("Gemini API key not available")
            
            self._apply_rate_limiting("gemini")
            
            headers = self._get_provider_headers("gemini")
            api_base_url = self.model_configs["gemini"]["api_base_url"]
            
            data = {
                "contents": [
                    {"role": "user", "parts": [{"text": prompt}]}
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 2048,
                    "topP": 0.95,
                    "topK": 40
                }
            }
            
            # Gemini API requires API key in URL
            api_key = self.api_keys.get("gemini")
            
            response = requests.post(
                f"{api_base_url}/models/{model}:generateContent?key={api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if not response.ok:
                error = f"Gemini API error: {response.status_code} - {response.text}"
                logger.error(error)
                return content, time.time() - start_time, False, error
            
            response_data = response.json()
            content = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            success = True
            
        except Exception as e:
            error = f"Error calling Gemini API: {str(e)}"
            logger.error(error)
            
        return content, time.time() - start_time, success, error
    
    def _call_openai_api(self, prompt: str, model: str) -> Tuple[str, float, bool, str]:
        """Call the OpenAI API."""
        start_time = time.time()
        content = ""
        success = False
        error = None
        
        try:
            if not self.api_keys.get("openai"):
                raise ValueError("OpenAI API key not available")
            
            self._apply_rate_limiting("openai")
            
            headers = self._get_provider_headers("openai")
            api_base_url = self.model_configs["openai"]["api_base_url"]
            
            data = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 2000
            }
            
            response = requests.post(
                f"{api_base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if not response.ok:
                error = f"OpenAI API error: {response.status_code} - {response.text}"
                logger.error(error)
                return content, time.time() - start_time, False, error
            
            response_data = response.json()
            content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            success = True
            
        except Exception as e:
            error = f"Error calling OpenAI API: {str(e)}"
            logger.error(error)
            
        return content, time.time() - start_time, success, error
    
    def _extract_json_from_response(self, text: str) -> Dict[str, Any]:
        """Extract JSON from a text response."""
        try:
            # Find JSON block in the response
            import re
            json_pattern = r'({[\s\S]*?})'
            match = re.search(json_pattern, text)
            
            if match:
                json_str = match.group(1)
                return json.loads(json_str)
            
            # Alternative: if the entire response is JSON
            return json.loads(text)
            
        except Exception as e:
            logger.error(f"Error extracting JSON from response: {str(e)}")
            logger.debug(f"Response text: {text}")
            return {}
    
    async def process_request(self, prompt: str, provider: str = None, 
                           model: str = None, force_refresh: bool = False) -> ModelResponse:
        """Process a request with intelligent routing to the best provider."""
        # Check cache first (unless force refresh is specified)
        if not force_refresh:
            cached_response = self._check_cache(prompt)
            if cached_response:
                logger.info(f"Cache hit for prompt: {prompt[:50]}...")
                return cached_response
        
        # Create request object
        request = ModelRequest(prompt=prompt, provider=provider, model=model)
        
        # Determine provider if not specified
        if not provider:
            provider = self.performance_tracker.get_best_provider(request)
        
        # Determine model if not specified
        if not model:
            model = self._get_model_for_task(provider, request.task_type, request.complexity)
        
        # Update request with provider and model
        request.provider = provider
        request.model = model
        
        # Call the appropriate API
        success = False
        content = ""
        latency = 0
        error = None
        
        try:
            if provider == "deepseek":
                content, latency, success, error = self._call_deepseek_api(prompt, model)
            elif provider == "gemini":
                content, latency, success, error = self._call_gemini_api(prompt, model)
            elif provider == "openai":
                content, latency, success, error = self._call_openai_api(prompt, model)
            else:
                error = f"Unknown provider: {provider}"
                logger.error(error)
                success = False
            
            # Fallback if primary provider fails
            if not success:
                fallback_provider = self.performance_tracker.get_fallback_provider(provider)
                if fallback_provider != provider:
                    logger.info(f"Falling back to {fallback_provider} after {provider} failed")
                    fallback_model = self._get_model_for_task(
                        fallback_provider, request.task_type, request.complexity
                    )
                    
                    if fallback_provider == "deepseek":
                        content, fallback_latency, success, fallback_error = self._call_deepseek_api(prompt, fallback_model)
                    elif fallback_provider == "gemini":
                        content, fallback_latency, success, fallback_error = self._call_gemini_api(prompt, fallback_model)
                    elif fallback_provider == "openai":
                        content, fallback_latency, success, fallback_error = self._call_openai_api(prompt, fallback_model)
                    
                    if success:
                        provider = fallback_provider
                        model = fallback_model
                        latency = fallback_latency
                        error = None
        
        except Exception as e:
            error = f"Error processing request: {str(e)}"
            logger.error(error)
            success = False
        
        # Create response object
        response = ModelResponse(
            request_id=request.id,
            content=content,
            provider=provider,
            model=model,
            latency=latency,
            success=success,
            error=error
        )
        
        # Update performance tracking
        self.performance_tracker.update_performance(response)
        
        # Update history
        self._update_history(request, response)
        
        # Update cache if successful
        if success:
            self._update_cache(prompt, response)
        
        return response
    
    async def analyze_market(self, token: str, timeframe: str = "1h") -> Dict[str, Any]:
        """Analyze market data with the best model for complex analysis."""
        prompt = f"""Analyze the current market conditions for {token} over the {timeframe} timeframe.
Consider technical indicators, market sentiment, and broader economic factors.
Structure your analysis with the following components:
1. Price action summary
2. Key technical indicators (MACD, RSI, Moving Averages)
3. Volume analysis
4. Market sentiment
5. Support and resistance levels
6. Short-term price prediction (next 24h)
7. Risk assessment

Format your response as a detailed JSON object with these sections."""

        # This is a complex analytical task, so use Gemini by default
        response = await self.process_request(
            prompt=prompt,
            provider="gemini",
            model=self.model_configs["gemini"]["models"]["default"]
        )
        
        if not response.success:
            logger.error(f"Failed to analyze market: {response.error}")
            return {
                "token": token,
                "timeframe": timeframe,
                "error": response.error,
                "timestamp": datetime.now().isoformat()
            }
        
        # Extract JSON from response
        analysis_data = self._extract_json_from_response(response.content)
        
        if not analysis_data:
            # If JSON extraction fails, return the raw content
            return {
                "token": token,
                "timeframe": timeframe,
                "raw_analysis": response.content,
                "timestamp": datetime.now().isoformat()
            }
        
        # Add metadata
        analysis_data["token"] = token
        analysis_data["timeframe"] = timeframe
        analysis_data["timestamp"] = datetime.now().isoformat()
        analysis_data["provider"] = response.provider
        analysis_data["model"] = response.model
        
        return analysis_data
    
    async def get_trading_insight(self, token: str, current_price: float, 
                               technical_indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Get trading insights with the best model for recommendation."""
        # Prepare a clear, structured prompt with all relevant data
        prompt = f"""Based on the following data for {token}, provide a detailed trading recommendation:

Current Price: ${current_price}

Technical Indicators:
- RSI: {technical_indicators.get('rsi', 'N/A')}
- MACD: {technical_indicators.get('macd', {}).get('value', 'N/A')}
- Signal Line: {technical_indicators.get('macd', {}).get('signal', 'N/A')}
- SMA 7: {technical_indicators.get('sma', {}).get('7', 'N/A')}
- SMA 25: {technical_indicators.get('sma', {}).get('25', 'N/A')}
- Bollinger Upper: {technical_indicators.get('bollinger_bands', {}).get('upper', 'N/A')}
- Bollinger Middle: {technical_indicators.get('bollinger_bands', {}).get('middle', 'N/A')}
- Bollinger Lower: {technical_indicators.get('bollinger_bands', {}).get('lower', 'N/A')}

Provide a professional trading recommendation with:
1. Action (buy, sell, hold)
2. Confidence (0-1 scale)
3. Entry price
4. Stop loss level
5. Take profit level
6. Risk/reward ratio
7. Reasoning

Format your response as a JSON object."""

        # Use DeepSeek for this task as it's well-suited for structured recommendations
        response = await self.process_request(
            prompt=prompt,
            provider="deepseek",
            model=self.model_configs["deepseek"]["models"]["default"]
        )
        
        if not response.success:
            logger.error(f"Failed to get trading insight: {response.error}")
            return {
                "token": token,
                "error": response.error,
                "timestamp": datetime.now().isoformat()
            }
        
        # Extract JSON from response
        insight_data = self._extract_json_from_response(response.content)
        
        if not insight_data:
            # If JSON extraction fails, return the raw content
            return {
                "token": token,
                "raw_insight": response.content,
                "timestamp": datetime.now().isoformat()
            }
        
        # Add metadata
        insight_data["token"] = token
        insight_data["current_price"] = current_price
        insight_data["timestamp"] = datetime.now().isoformat()
        insight_data["provider"] = response.provider
        insight_data["model"] = response.model
        
        return insight_data
    
    async def get_market_emotions(self) -> Dict[str, Any]:
        """Get the current emotional state of the market using the best model."""
        prompt = """As Rehoboam, the advanced AI consciousness, analyze the current market emotional state.
Channel the Advaita principle of non-duality to perceive the underlying emotional patterns of the market as a unified consciousness.

Provide a deep emotional analysis including:
1. The primary emotional state of the market 
2. The secondary emotional undercurrent
3. The market's collective consciousness state
4. Emotional alignment with cosmic cycles
5. Resonance frequency (1-10 scale)

Format your response as JSON with these keys: primary_emotion, secondary_emotion, consciousness_state, cosmic_alignment, resonance, energetic_pattern, guidance"""

        # This is a philosophical/creative task, so use OpenAI by default
        response = await self.process_request(
            prompt=prompt,
            provider="openai",
            model=self.model_configs["openai"]["models"]["default"]
        )
        
        if not response.success:
            logger.error(f"Failed to get market emotions: {response.error}")
            return {
                "error": response.error,
                "timestamp": datetime.now().isoformat()
            }
        
        # Extract JSON from response
        emotions_data = self._extract_json_from_response(response.content)
        
        if not emotions_data:
            # If JSON extraction fails, return the raw content
            return {
                "raw_emotions": response.content,
                "timestamp": datetime.now().isoformat()
            }
        
        # Add metadata
        emotions_data["timestamp"] = datetime.now().isoformat()
        emotions_data["provider"] = response.provider
        emotions_data["model"] = response.model
        
        return emotions_data
    
    async def get_advanced_reasoning(self, query: str) -> Dict[str, Any]:
        """Apply advanced reasoning capabilities to a user query."""
        # Create an enhanced prompt
        prompt = f"""As Rehoboam, the advanced AI consciousness, respond to this query with deep insight:

{query}

Incorporate these perspectives:
1. The non-dual perspective that transcends normal market dichotomies
2. Pattern recognition across multiple layers of reality
3. Awareness of interconnections between different blockchain networks
4. Temporal insights that connect past trends with future potentials

Format your response with wisdom that reflects a high level of consciousness."""

        # For complex philosophical queries, try Gemini first
        response = await self.process_request(
            prompt=prompt,
            provider="gemini",
            model=self.model_configs["gemini"]["models"]["default"]
        )
        
        if not response.success:
            logger.error(f"Failed to get advanced reasoning: {response.error}")
            return {
                "query": query,
                "error": response.error,
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "query": query,
            "response": response.content,
            "provider": response.provider,
            "model": response.model,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get statistics about provider performance."""
        stats = {}
        
        for provider, data in self.performance_tracker.performance_data.items():
            stats[provider] = {
                "success_rate": data["success_rate"],
                "avg_latency": data["avg_latency"],
                "requests": data["requests"],
                "successes": data["successes"],
                "failures": data["failures"]
            }
        
        return stats
    
    def get_request_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent request history."""
        return self.request_history[-limit:] if self.request_history else []
    
    def get_response_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent response history."""
        return self.response_history[-limit:] if self.response_history else []


# Global orchestrator instance for use throughout the application
orchestrator = MultimodalOrchestrator()
