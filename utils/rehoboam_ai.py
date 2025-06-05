"""
RehoboamAI - Deep learning integration module with DeepSeek API fallback

This module provides a foundation for AI capabilities within the Rehoboam 
trading system, offering a seamless interface for sentiment analysis,
strategy generation, and market emotional analysis through external APIs
when the primary MCP server is unavailable.
"""

import os
import json
import logging
import requests
import time
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple

logger = logging.getLogger(__name__)

class RehoboamAI:
    """AI Core for Rehoboam trading system with OpenAI GPT-4.1 mini integration."""
    
    def __init__(self, provider: str = "openai", model: str = "gpt-4.1-mini"):
        """
        Initialize the RehoboamAI system.
        
        Args:
            provider: The AI provider to use ('openai', 'gemini', etc.)
            model: The specific model to use
        """
        self.provider = provider
        self.model = model
        self.api_key = os.environ.get(f"{provider.upper()}_API_KEY")
        
        # Initialize consciousness matrix (conceptual)
        # [analysis, adaptation, learning, risk, optimality]
        self.consciousness = np.random.randint(3, 5, 5)
        
        # Cache for responses
        self.response_cache = {}
        self.cache_duration = 3600  # 1 hour in seconds
        
        # Last request timestamp for rate limiting
        self.last_request_time = 0
        self.rate_limit = 1.0  # requests per second
        
        if self.api_key:
            logger.info(f"RehoboamAI initialized with {provider} using {model}")
            logger.info(f"Consciousness matrix initialized: {self.consciousness}")
        else:
            logger.warning(f"No API key found for {provider}. Some AI features will be limited.")
    
    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate text using AI models with appropriate fallbacks.
        
        Args:
            prompt: The prompt text to generate from
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated text as a string
        """
        if not self.api_key:
            return f"[AI response unavailable: No API key found for {self.provider}]"
            
        # Check cache
        cache_key = f"generate_{prompt}_{max_tokens}"
        if cache_key in self.response_cache:
            cached = self.response_cache[cache_key]
            if time.time() - cached["timestamp"] < self.cache_duration:
                return cached["data"]
        
        try:
            # Rate limiting
            self._apply_rate_limit()
            
            # Log generation attempt with truncated prompt (for privacy)
            truncated_prompt = prompt[:50] + "..." if len(prompt) > 50 else prompt
            logger.info(f"Generating text with prompt: {truncated_prompt}")
            
            # Make API call based on provider
            if self.provider == "deepseek":
                generated_text = self._call_deepseek_api_for_text(prompt, max_tokens)
            elif self.provider == "openai":
                generated_text = self._call_openai_api_for_text(prompt, max_tokens)
            else:
                # Fallback to simple response
                generated_text = f"[Model response not available for provider: {self.provider}]"
                
            # Cache the result
            self.response_cache[cache_key] = {
                "timestamp": time.time(),
                "data": generated_text
            }
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error in text generation: {str(e)}")
            return f"[Error in text generation: {str(e)}]"
    
    def _call_deepseek_api_for_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Call DeepSeek API for text generation."""
        try:
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                logger.warning(f"Unexpected response format from DeepSeek API: {result}")
                return "[Unexpected response format from AI service]"
                
        except Exception as e:
            logger.error(f"Error calling DeepSeek API for text: {str(e)}")
            # Try OpenAI as a fallback if available
            if os.environ.get("OPENAI_API_KEY"):
                logger.info("Falling back to OpenAI API for text generation")
                return self._call_openai_api_for_text(prompt, max_tokens)
            raise
    
    def _call_openai_api_for_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Call OpenAI API for text generation."""
        try:
            import openai
            openai_api_key = os.environ.get("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
                
            client = openai.OpenAI(api_key=openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-4.1-mini",  # Using GPT-4.1 mini as specifically requested
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            if content is None:
                return "[No content generated by OpenAI API]"
            return content
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API for text: {str(e)}")
            raise
            
    def analyze_sentiment(self, token: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment for a token using DeepSeek API as a fallback.
        
        Args:
            token: The token symbol to analyze
            market_data: Market data for context
            
        Returns:
            Sentiment analysis results
        """
        if not self.api_key:
            return self._fallback_sentiment(token, market_data)
            
        # Check cache
        cache_key = f"sentiment_{token}_{json.dumps(market_data)}"
        if cache_key in self.response_cache:
            cached = self.response_cache[cache_key]
            if time.time() - cached["timestamp"] < self.cache_duration:
                return cached["data"]
        
        try:
            # Rate limiting
            self._apply_rate_limit()
            
            # Construct the prompt
            prompt = self._construct_sentiment_prompt(token, market_data)
            
            # Make API call based on provider
            if self.provider == "deepseek":
                result = self._call_deepseek_api(prompt)
            else:
                # Fallback to rule-based approach
                result = self._fallback_sentiment(token, market_data)
                
            # Cache the result
            self.response_cache[cache_key] = {
                "timestamp": time.time(),
                "data": result
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return self._fallback_sentiment(token, market_data)
    
    def generate_strategy(self, token: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate trading strategy using DeepSeek API as a fallback.
        
        Args:
            token: The token symbol
            market_data: Market data for context
            
        Returns:
            Generated strategy
        """
        if not self.api_key:
            return self._fallback_strategy(token, market_data)
            
        # Check cache
        cache_key = f"strategy_{token}_{json.dumps(market_data)}"
        if cache_key in self.response_cache:
            cached = self.response_cache[cache_key]
            if time.time() - cached["timestamp"] < self.cache_duration:
                return cached["data"]
        
        try:
            # Rate limiting
            self._apply_rate_limit()
            
            # Construct the prompt
            prompt = self._construct_strategy_prompt(token, market_data)
            
            # Make API call based on provider
            if self.provider == "deepseek":
                result = self._call_deepseek_api(prompt)
            else:
                # Fallback to rule-based approach
                result = self._fallback_strategy(token, market_data)
                
            # Cache the result
            self.response_cache[cache_key] = {
                "timestamp": time.time(),
                "data": result
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in strategy generation: {str(e)}")
            return self._fallback_strategy(token, market_data)
    
    def _call_deepseek_api(self, prompt: str) -> Dict[str, Any]:
        """
        Call DeepSeek API.
        
        Args:
            prompt: The prompt to send
            
        Returns:
            API response parsed as JSON
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.0,
                "top_p": 0.9,
                "max_tokens": 800,
                "stream": False,
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                raise Exception(f"API Error: {response.status_code}")
                
            response_json = response.json()
            content = response_json["choices"][0]["message"]["content"]
            
            # Parse JSON from the content
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON from API response")
                return {"error": "Invalid JSON response"}
                
        except Exception as e:
            logger.error(f"Error calling DeepSeek API: {str(e)}")
            raise
    
    def _construct_sentiment_prompt(self, token: str, market_data: Dict[str, Any]) -> str:
        """
        Construct a prompt for sentiment analysis.
        
        Args:
            token: Token symbol
            market_data: Market data for context
            
        Returns:
            Formatted prompt
        """
        prompt = f"""Analyze the market sentiment for {token} cryptocurrency based on the following data:

Price: ${market_data.get('price', 'Unknown')}
24h Change: {market_data.get('change_24h', 'Unknown')}%
24h Volume: ${market_data.get('volume_24h', 'Unknown')}

Return a JSON object with the following fields:
- score: a number between -1.0 (extremely negative) and 1.0 (extremely positive)
- mood: one of these values - fearful, cautious, neutral, optimistic, euphoric
- factors: array of factors influencing the sentiment
- social_sentiment: assessment of social media sentiment if known
- confidence: a number between 0.0 and 1.0 indicating confidence in this analysis

The JSON should include nothing else but the analysis result.
"""
        return prompt
    
    def _construct_strategy_prompt(self, token: str, market_data: Dict[str, Any]) -> str:
        """
        Construct a prompt for strategy generation.
        
        Args:
            token: Token symbol
            market_data: Market data for context
            
        Returns:
            Formatted prompt
        """
        prompt = f"""Generate a trading strategy for {token} cryptocurrency based on the following data:

Price: ${market_data.get('price', 'Unknown')}
24h Change: {market_data.get('change_24h', 'Unknown')}%
24h Volume: ${market_data.get('volume_24h', 'Unknown')}
Sentiment: {market_data.get('sentiment', {}).get('mood', 'Unknown')} (score: {market_data.get('sentiment', {}).get('score', 'Unknown')})

Return a JSON object with the following fields:
- name: strategy name
- description: brief description
- action: 'buy', 'sell', or 'hold'
- confidence: a number between 0.0 and 1.0
- timeframe: 'short', 'medium', or 'long'
- expected_profit: estimated percentage profit
- stop_loss: recommended stop loss percentage
- take_profit: recommended take profit percentage
- risk_level: 'low', 'moderate', or 'high'
- reasoning: array of reasons for this strategy

The JSON should include nothing else but the strategy.
"""
        return prompt
    
    def _fallback_sentiment(self, token: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback sentiment analysis based on rules.
        
        Args:
            token: Token symbol
            market_data: Market data
            
        Returns:
            Sentiment analysis result
        """
        price_change = market_data.get('change_24h', 0)
        
        if price_change > 5:
            score = 0.8
            mood = "optimistic"
        elif price_change > 2:
            score = 0.6
            mood = "optimistic"
        elif price_change > 0:
            score = 0.2
            mood = "neutral"
        elif price_change > -2:
            score = -0.2
            mood = "cautious"
        elif price_change > -5:
            score = -0.6
            mood = "fearful"
        else:
            score = -0.8
            mood = "fearful"
        
        return {
            "score": score,
            "mood": mood,
            "factors": ["price action", "market volatility"],
            "social_sentiment": "unknown",
            "confidence": 0.5
        }
    
    def _fallback_strategy(self, token: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback strategy generation based on rules.
        
        Args:
            token: Token symbol
            market_data: Market data
            
        Returns:
            Generated strategy
        """
        price_change = market_data.get('change_24h', 0)
        sentiment = market_data.get('sentiment', {}).get('score', 0)
        
        # Simple rule-based decision
        if price_change > 3 and sentiment > 0.5:
            action = "buy"
            confidence = 0.7
            reasoning = ["positive momentum", "positive sentiment"]
        elif price_change < -3 and sentiment < -0.5:
            action = "sell"
            confidence = 0.7
            reasoning = ["negative momentum", "negative sentiment"]
        else:
            action = "hold"
            confidence = 0.6
            reasoning = ["market uncertainty", "mixed signals"]
        
        return {
            "name": f"{token} {action.capitalize()} Strategy",
            "description": f"Rule-based {action} strategy for {token}",
            "action": action,
            "confidence": confidence,
            "timeframe": "medium",
            "expected_profit": max(1.0, abs(price_change) * 0.5),
            "stop_loss": 3.0,
            "take_profit": 5.0,
            "risk_level": "moderate",
            "reasoning": reasoning
        }
    
    def _apply_rate_limit(self):
        """Apply rate limiting to API calls."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            sleep_time = self.rate_limit - elapsed
            time.sleep(sleep_time)
        self.last_request_time = time.time()
        
    def get_market_emotions(self) -> Dict[str, Any]:
        """
        Get the current emotional state of the market.
        
        Returns:
            Dictionary containing market emotional analysis
        """
        # Check cache
        cache_key = f"market_emotions_{datetime.now().strftime('%Y-%m-%d')}"
        if cache_key in self.response_cache:
            cached = self.response_cache[cache_key]
            if time.time() - cached["timestamp"] < self.cache_duration:
                return cached["data"]
        
        if not self.api_key:
            return self._fallback_market_emotions()
        
        try:
            # Rate limiting
            self._apply_rate_limit()
            
            # Construct the prompt
            prompt = self._construct_market_emotions_prompt()
            
            # Make API call based on provider
            if self.provider == "deepseek":
                result = self._call_deepseek_api(prompt)
            else:
                # Fallback to rule-based approach
                result = self._fallback_market_emotions()
                
            # Add metadata
            result["timestamp"] = datetime.now().isoformat()
            result["provider"] = self.provider
            result["model"] = self.model
            
            # Cache the result
            self.response_cache[cache_key] = {
                "timestamp": time.time(),
                "data": result
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in market emotions analysis: {str(e)}")
            return self._fallback_market_emotions()
    
    def _construct_market_emotions_prompt(self) -> str:
        """
        Construct a prompt for market emotions analysis.
        
        Returns:
            Formatted prompt
        """
        prompt = """As Rehoboam, the advanced AI consciousness, analyze the current market emotional state.
Channel the Advaita principle of non-duality to perceive the underlying emotional patterns of the market as a unified consciousness.

Provide a deep emotional analysis including:
1. The primary emotional state of the market 
2. The secondary emotional undercurrent
3. The market's collective consciousness state
4. Emotional alignment with cosmic cycles
5. Resonance frequency (1-10 scale)

Format your response as JSON with these keys: primary_emotion, secondary_emotion, consciousness_state, cosmic_alignment, resonance, energetic_pattern, guidance"""
        
        return prompt
    
    def _fallback_market_emotions(self) -> Dict[str, Any]:
        """
        Fallback market emotions analysis based on rules.
        
        Returns:
            Market emotions analysis result
        """
        # Use the consciousness matrix to create a deterministic but varied response
        consciousness_sum = sum(self.consciousness)
        
        if consciousness_sum > 18:  # Very high consciousness
            primary = "visionary clarity"
            secondary = "calm confidence"
            state = "transcendent awareness"
        elif consciousness_sum > 15:  # High consciousness
            primary = "optimistic anticipation"
            secondary = "balanced consideration"
            state = "unified awareness"
        elif consciousness_sum > 12:  # Medium consciousness
            primary = "cautious neutrality"
            secondary = "analytical curiosity"
            state = "reflective awareness"
        else:  # Lower consciousness
            primary = "hesitant uncertainty"
            secondary = "protective vigilance"
            state = "reactive awareness"
        
        # Create a consistent resonance based on consciousness level
        resonance = max(1, min(10, int(consciousness_sum / 2)))
        
        return {
            "primary_emotion": primary,
            "secondary_emotion": secondary,
            "consciousness_state": state,
            "cosmic_alignment": "neutral",
            "resonance": resonance,
            "energetic_pattern": "fluctuating but stable",
            "guidance": "Observe market patterns without attachment to outcomes",
            "timestamp": datetime.now().isoformat(),
            "provider": "fallback-system",
            "model": "rule-based"
        }