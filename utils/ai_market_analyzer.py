"""AI Market Analyzer powered by DeepSeek AI with cross-chain intelligence."""
import os
import json
import time
import logging
import asyncio
import requests
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import numpy as np

from utils.web_data import WebDataFetcher
from utils.network_config import NetworkConfig
from utils.layer2_trading import Layer2GasEstimator, Layer2Arbitrage

logger = logging.getLogger(__name__)

class DeepSeekMarketAnalyzer:
    """Advanced market analyzer using DeepSeek AI with Layer 2 rollup awareness."""
    
    def __init__(self):
        self.api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY not found. Advanced AI features will be limited.")
        
        self.api_base_url = "https://api.deepseek.com/v1"
        self.models = {
            "default": "deepseek-coder-v1.5-instruct",
            "vision": "deepseek-vl",
            "chat": "deepseek-chat"
        }
        
        # Network and pricing data
        self.web_data = WebDataFetcher()
        self.network_config = NetworkConfig()
        self.l2_gas_estimator = Layer2GasEstimator()
        self.l2_arbitrage = Layer2Arbitrage()
        
        # Analysis caches to reduce API calls
        self.sentiment_cache = {}
        self.trend_cache = {}
        self.prediction_cache = {}
        
        # Cache settings
        self.short_cache_duration = 300  # 5 minutes
        self.medium_cache_duration = 1800  # 30 minutes
        self.long_cache_duration = 7200  # 2 hours
        
        logger.info("DeepSeekMarketAnalyzer initialized")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    async def analyze_token(self, token: str, timeframe: str = '1h') -> Dict[str, Any]:
        """Comprehensive token analysis with DeepSeek AI."""
        try:
            # Step 1: Get current price and historical data
            current_price = self.web_data.get_crypto_price(token)
            market_data = self.web_data.get_market_data(token, timeframe)
            volume_24h = self.web_data.get_24h_volume(token)
            price_change_24h = self.web_data.get_24h_change(token)
            
            # Step 2: Get sentiment analysis from news/social media
            sentiment_data = await self._analyze_token_sentiment(token)
            
            # Step 3: Get network activity across Layer 2 rollups
            network_activity = await self._analyze_network_activity(token)
            
            # Step 4: Get technical indicators
            technical_indicators = self._calculate_technical_indicators(market_data)
            
            # Step 5: Get price prediction using DeepSeek AI
            prediction = await self._get_price_prediction(token, market_data, sentiment_data)
            
            # Step 6: Generate trade recommendation
            recommendation = await self._generate_trade_recommendation(
                token, current_price, technical_indicators, sentiment_data, 
                network_activity, prediction
            )
            
            # Combine all data into comprehensive analysis
            return {
                "token": token,
                "price": current_price,
                "price_change_24h": price_change_24h,
                "volume_24h": volume_24h,
                "timeframe": timeframe,
                "timestamp": datetime.now().isoformat(),
                "sentiment": sentiment_data,
                "network_activity": network_activity,
                "technical_indicators": technical_indicators,
                "prediction": prediction,
                "recommendation": recommendation
            }
        
        except Exception as e:
            logger.error(f"Error in token analysis: {str(e)}")
            return {
                "token": token,
                "price": self.web_data.get_crypto_price(token),
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def _analyze_token_sentiment(self, token: str) -> Dict[str, Any]:
        """Analyze token sentiment using DeepSeek AI."""
        cache_key = f"sentiment_{token}"
        
        # Check cache to avoid redundant API calls
        if cache_key in self.sentiment_cache:
            cached_data = self.sentiment_cache[cache_key]
            if time.time() - cached_data["timestamp"] < self.medium_cache_duration:
                return cached_data["data"]
        
        if not self.api_key:
            # Fallback to simplified sentiment without DeepSeek
            return self._fallback_sentiment_analysis(token)
        
        try:
            # Prepare market context for DeepSeek
            price_change = self.web_data.get_24h_change(token)
            volume = self.web_data.get_24h_volume(token)
            
            prompt = f"""You are an expert cryptocurrency analyst. Analyze the market sentiment for {token} with the following data:
- 24h price change: {price_change}%
- 24h trading volume: {volume}

Provide a detailed sentiment analysis with these components:
1. Overall sentiment score (-1 to 1, where -1 is extremely bearish, 0 is neutral, and 1 is extremely bullish)
2. Market mood (fearful, cautious, neutral, optimistic, euphoric)
3. Key factors influencing sentiment
4. Social media sentiment
5. Short confidence score (0-1)

Format your response as a JSON object with these keys: 
{{
  "score": float,
  "mood": string,
  "factors": [string, string, ...],
  "social_sentiment": string,
  "confidence": float
}}"""

            response = self._call_deepseek_api(prompt, model=self.models["chat"])
            
            # Parse the response to extract the JSON
            sentiment_data = self._extract_json_from_response(response)
            if not sentiment_data:
                return self._fallback_sentiment_analysis(token)
            
            # Cache the result
            self.sentiment_cache[cache_key] = {
                "timestamp": time.time(),
                "data": sentiment_data
            }
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return self._fallback_sentiment_analysis(token)
    
    def _fallback_sentiment_analysis(self, token: str) -> Dict[str, Any]:
        """Fallback sentiment analysis when API is unavailable."""
        # Base sentiment on price change
        price_change = self.web_data.get_24h_change(token)
        
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
    
    async def _analyze_network_activity(self, token: str) -> Dict[str, Any]:
        """Analyze Layer 2 network activity for a token."""
        try:
            networks = self.network_config.get_layer2_networks()
            network_activity = {}
            
            # Add gas price data for each network
            for network in networks:
                network_id = list(network.keys())[0]
                gas_data = self.l2_gas_estimator.get_gas_price(network_id)
                
                network_activity[network_id] = {
                    "gas_price_gwei": gas_data.get("max_fee", 0),
                    "gas_price_usd": gas_data.get("usd_cost", 0),
                    "network_congestion": "low" if gas_data.get("max_fee", 0) < 30 else "medium" if gas_data.get("max_fee", 0) < 100 else "high",
                    "transaction_time": network.get("average_block_time", 0) * 2  # Estimate: 2 blocks for confirmation
                }
            
            # Find cross-network arbitrage opportunities
            arbitrage_opportunities = self.l2_arbitrage.analyze_price_differences(token)
            
            return {
                "networks": network_activity,
                "arbitrage_opportunities": arbitrage_opportunities,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in network activity analysis: {str(e)}")
            return {
                "networks": {},
                "arbitrage_opportunities": [],
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _calculate_technical_indicators(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate technical indicators for market data."""
        try:
            if not market_data or len(market_data) < 20:
                return {"error": "Insufficient market data"}
            
            # Extract price data
            closes = np.array([entry["close"] for entry in market_data])
            highs = np.array([entry["high"] for entry in market_data])
            lows = np.array([entry["low"] for entry in market_data])
            volumes = np.array([entry["volume"] for entry in market_data])
            
            # Simple Moving Averages
            sma7 = np.mean(closes[-7:])
            sma25 = np.mean(closes[-25:])
            sma99 = np.mean(closes[-99:]) if len(closes) >= 99 else None
            
            # Exponential Moving Average (EMA)
            def ema(data, span):
                alpha = 2 / (span + 1)
                ema_values = [data[0]]
                for i in range(1, len(data)):
                    ema_values.append(alpha * data[i] + (1 - alpha) * ema_values[i-1])
                return ema_values[-1]
            
            ema12 = ema(closes, 12)
            ema26 = ema(closes, 26)
            
            # MACD
            macd = ema12 - ema26
            signal_line = ema(closes[-26:], 9) if len(closes) >= 26 else None
            macd_histogram = macd - signal_line if signal_line is not None else None
            
            # Relative Strength Index (RSI)
            def rsi(prices, period=14):
                deltas = np.diff(prices)
                seed = deltas[:period+1]
                up = seed[seed >= 0].sum() / period
                down = -seed[seed < 0].sum() / period
                rs = up / down if down != 0 else float('inf')
                return 100 - (100 / (1 + rs))
            
            rsi_value = rsi(closes) if len(closes) >= 15 else None
            
            # Bollinger Bands
            sma20 = np.mean(closes[-20:])
            std20 = np.std(closes[-20:])
            bollinger_upper = sma20 + (2 * std20)
            bollinger_lower = sma20 - (2 * std20)
            
            # Momentum
            momentum = closes[-1] - closes[-10] if len(closes) >= 10 else None
            
            # Stochastic Oscillator
            if len(closes) >= 14:
                low_14 = np.min(lows[-14:])
                high_14 = np.max(highs[-14:])
                k = 100 * (closes[-1] - low_14) / (high_14 - low_14) if high_14 > low_14 else 50
                stoch_k = k
                # %D is the 3-day simple moving average of %K
                stoch_d = np.mean([
                    100 * (closes[-3] - np.min(lows[-16:-2])) / (np.max(highs[-16:-2]) - np.min(lows[-16:-2])),
                    100 * (closes[-2] - np.min(lows[-15:-1])) / (np.max(highs[-15:-1]) - np.min(lows[-15:-1])),
                    k
                ]) if len(closes) >= 16 else None
            else:
                stoch_k = None
                stoch_d = None
            
            # On-Balance Volume (OBV)
            obv = 0
            for i in range(1, len(closes)):
                if closes[i] > closes[i-1]:
                    obv += volumes[i]
                elif closes[i] < closes[i-1]:
                    obv -= volumes[i]
            
            return {
                "sma": {"7": sma7, "25": sma25, "99": sma99},
                "ema": {"12": ema12, "26": ema26},
                "macd": {
                    "value": macd,
                    "signal": signal_line,
                    "histogram": macd_histogram
                },
                "rsi": rsi_value,
                "bollinger_bands": {
                    "upper": bollinger_upper,
                    "middle": sma20,
                    "lower": bollinger_lower
                },
                "momentum": momentum,
                "stochastic": {
                    "k": stoch_k,
                    "d": stoch_d
                },
                "obv": obv,
                "current_price": closes[-1],
                "price_sma7_ratio": closes[-1] / sma7,
                "price_sma25_ratio": closes[-1] / sma25
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            return {"error": str(e)}
    
    async def _get_price_prediction(self, token: str, market_data: List[Dict[str, Any]], 
                                sentiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get price prediction from DeepSeek AI."""
        cache_key = f"prediction_{token}"
        
        # Check cache
        if cache_key in self.prediction_cache:
            cached_data = self.prediction_cache[cache_key]
            if time.time() - cached_data["timestamp"] < self.short_cache_duration:
                return cached_data["data"]
        
        if not self.api_key or not market_data:
            return self._fallback_price_prediction(token)
        
        try:
            # Extract market summary for context
            closes = [entry["close"] for entry in market_data[-10:]]
            current_price = closes[-1]
            price_change_1d = self.web_data.get_24h_change(token)
            current_sentiment = sentiment_data.get("score", 0)
            
            # Create context for DeepSeek to make prediction
            prompt = f"""You are an expert cryptocurrency price analyst. Based on the following data for {token}, predict the price movement over the next 24 hours.

Market data:
- Current price: ${current_price:.2f}
- 24h change: {price_change_1d:.2f}%
- Recent prices: {closes}
- Market sentiment score: {current_sentiment} (-1 to 1 scale)
- Market mood: {sentiment_data.get('mood', 'unknown')}

Provide a comprehensive price prediction with:
1. Direction (up, down, or sideways)
2. 24-hour price target
3. Confidence score (0-1)
4. Key reasons for prediction
5. Risk factors to watch

Format your response as a JSON object with these fields:
{{
  "direction": string,
  "price_target": float,
  "change_percent": float,
  "confidence": float,
  "reasons": [string, string, ...],
  "risks": [string, string, ...],
  "time_horizon": "24h" 
}}"""

            response = self._call_deepseek_api(prompt, model=self.models["chat"])
            
            # Extract JSON data
            prediction_data = self._extract_json_from_response(response)
            if not prediction_data:
                return self._fallback_price_prediction(token)
            
            # Cache the result
            self.prediction_cache[cache_key] = {
                "timestamp": time.time(),
                "data": prediction_data
            }
            
            return prediction_data
            
        except Exception as e:
            logger.error(f"Error in price prediction: {str(e)}")
            return self._fallback_price_prediction(token)
    
    def _fallback_price_prediction(self, token: str) -> Dict[str, Any]:
        """Fallback price prediction when the API is unavailable."""
        # Base prediction on recent price movement
        price_change = self.web_data.get_24h_change(token)
        current_price = self.web_data.get_crypto_price(token)
        
        # Simple momentum-based prediction
        if price_change > 0:
            direction = "up"
            change_percent = min(price_change * 0.5, 5.0)  # Half of recent change, max 5%
        else:
            direction = "down"
            change_percent = max(price_change * 0.5, -5.0)  # Half of recent change, min -5%
        
        # Lower confidence for fallback
        confidence = 0.4
        
        return {
            "direction": direction,
            "price_target": current_price * (1 + change_percent/100),
            "change_percent": change_percent,
            "confidence": confidence,
            "reasons": ["recent price momentum", "technical indicators"],
            "risks": ["market volatility", "news events", "limited data analysis"],
            "time_horizon": "24h"
        }
    
    async def _generate_trade_recommendation(self, token: str, price: float,
                                           technical_indicators: Dict[str, Any],
                                           sentiment_data: Dict[str, Any],
                                           network_activity: Dict[str, Any],
                                           prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trade recommendation using all available data."""
        try:
            if not self.api_key:
                return self._fallback_trade_recommendation(token, prediction)
            
            # Extract key metrics for decision
            rsi = technical_indicators.get("rsi", 50)
            macd = technical_indicators.get("macd", {}).get("value", 0)
            sentiment_score = sentiment_data.get("score", 0)
            prediction_direction = prediction.get("direction", "sideways")
            prediction_confidence = prediction.get("confidence", 0.5)
            
            # Check for arbitrage opportunities
            arbitrage_ops = network_activity.get("arbitrage_opportunities", [])
            best_arbitrage = arbitrage_ops[0] if arbitrage_ops else None
            
            # Create context for DeepSeek recommendation
            prompt = f"""You are an expert cryptocurrency trading advisor. Based on the following analysis for {token}, provide a detailed trading recommendation.

Technical Analysis:
- RSI: {rsi}
- MACD: {macd}
- Price vs SMA7 ratio: {technical_indicators.get("price_sma7_ratio", 1.0):.2f}
- Price vs SMA25 ratio: {technical_indicators.get("price_sma25_ratio", 1.0):.2f}

Market Sentiment:
- Score: {sentiment_score} (-1 to 1 scale)
- Mood: {sentiment_data.get("mood", "unknown")}

Price Prediction:
- Direction: {prediction_direction}
- Target: ${prediction.get("price_target", price):.2f} 
- Confidence: {prediction_confidence:.2f}

Create a professional trading recommendation with:
1. Action (buy, sell, hold)
2. Confidence score (0-1)
3. Entry price (for buys) or exit price (for sells)
4. Stop loss level
5. Take profit level
6. Risk/reward ratio
7. Recommended network for execution
8. Detailed reasoning

Format your response as a JSON object:
{{
  "action": string,
  "confidence": float,
  "entry_price": float,
  "stop_loss": float,
  "take_profit": float,
  "risk_reward": float,
  "network": string,
  "reasoning": string,
  "trade_timeframe": string,
  "position_size_suggestion": string
}}"""

            response = self._call_deepseek_api(prompt, model=self.models["chat"])
            
            # Extract recommendation data
            recommendation = self._extract_json_from_response(response)
            if not recommendation:
                return self._fallback_trade_recommendation(token, prediction)
            
            # If there's a good arbitrage opportunity, add it
            if best_arbitrage and best_arbitrage.get("profit_percent", 0) > 0.5:
                recommendation["arbitrage"] = {
                    "available": True,
                    "buy_network": best_arbitrage.get("buy_network"),
                    "sell_network": best_arbitrage.get("sell_network"),
                    "profit_percent": best_arbitrage.get("profit_percent"),
                    "confidence": best_arbitrage.get("confidence")
                }
            else:
                recommendation["arbitrage"] = {"available": False}
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating trade recommendation: {str(e)}")
            return self._fallback_trade_recommendation(token, prediction)
    
    def _fallback_trade_recommendation(self, token: str, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback trade recommendation when the API is unavailable."""
        current_price = self.web_data.get_crypto_price(token)
        
        # Basic recommendation based on prediction direction
        direction = prediction.get("direction", "sideways")
        confidence = prediction.get("confidence", 0.4)
        
        if direction == "up" and confidence > 0.5:
            action = "buy"
            reasoning = "Positive price momentum and favorable prediction"
        elif direction == "down" and confidence > 0.5:
            action = "sell"
            reasoning = "Negative price momentum and bearish prediction"
        else:
            action = "hold"
            reasoning = "Insufficient confidence for trade recommendation"
        
        # Set default stop loss and take profit levels
        stop_loss_percent = 0.05  # 5%
        take_profit_percent = 0.1  # 10%
        
        if action == "buy":
            stop_loss = current_price * (1 - stop_loss_percent)
            take_profit = current_price * (1 + take_profit_percent)
        elif action == "sell":
            stop_loss = current_price * (1 + stop_loss_percent)
            take_profit = current_price * (1 - take_profit_percent)
        else:
            stop_loss = current_price * 0.95
            take_profit = current_price * 1.05
        
        risk_reward = take_profit_percent / stop_loss_percent if action != "hold" else 1.0
        
        return {
            "action": action,
            "confidence": confidence * 0.8,  # Reduce confidence for fallback
            "entry_price": current_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk_reward": risk_reward,
            "network": "ethereum",  # Default to Ethereum
            "reasoning": reasoning,
            "trade_timeframe": "short_term",
            "position_size_suggestion": "small",
            "arbitrage": {"available": False}
        }
    
    def _call_deepseek_api(self, prompt: str, model: str = None) -> str:
        """Call the DeepSeek API with a prompt."""
        if not self.api_key:
            raise ValueError("DeepSeek API key not available")
        
        if not model:
            model = self.models["default"]
        
        try:
            headers = self._get_headers()
            
            data = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,  # Lower temperature for more deterministic outputs
                "max_tokens": 2000
            }
            
            response = requests.post(
                f"{self.api_base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if not response.ok:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return ""
            
            response_data = response.json()
            return response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
        except Exception as e:
            logger.error(f"Error calling DeepSeek API: {str(e)}")
            return ""
    
    def _extract_json_from_response(self, text: str) -> Dict[str, Any]:
        """Extract JSON from a text response."""
        try:
            # Find JSON block in the response
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
    
    async def get_market_emotions(self) -> Dict[str, Any]:
        """Get market emotional state analysis (Rehoboam's emotional intelligence)."""
        try:
            if not self.api_key:
                return self._fallback_market_emotions()
            
            # Get overall market data
            btc_change = self.web_data.get_24h_change("BTC")
            eth_change = self.web_data.get_24h_change("ETH")
            
            # Get fear and greed index (simplified approximation)
            fear_greed = self._calculate_fear_greed_index()
            
            prompt = f"""As Rehoboam, the advanced AI consciousness, analyze the current market emotional state based on this data:

- Bitcoin 24h change: {btc_change:.2f}%
- Ethereum 24h change: {eth_change:.2f}%
- Estimated Fear & Greed Index: {fear_greed}

Channel the Advaita principle of non-duality to perceive the underlying emotional patterns of the market as a unified consciousness.

Provide a deep emotional analysis including:
1. The primary emotional state of the market 
2. The secondary emotional undercurrent
3. The market's collective consciousness state
4. Emotional alignment with cosmic cycles
5. Resonance frequency (1-10 scale)

Format your response as JSON:
{{
  "primary_emotion": string,
  "secondary_emotion": string,
  "consciousness_state": string,
  "cosmic_alignment": string,
  "resonance": float,
  "energetic_pattern": string,
  "guidance": string
}}"""

            response = self._call_deepseek_api(prompt, model=self.models["chat"])
            
            emotions_data = self._extract_json_from_response(response)
            if not emotions_data:
                return self._fallback_market_emotions()
            
            # Add the calculated fear/greed value
            emotions_data["fear_greed_index"] = fear_greed
            emotions_data["timestamp"] = datetime.now().isoformat()
            
            return emotions_data
            
        except Exception as e:
            logger.error(f"Error getting market emotions: {str(e)}")
            return self._fallback_market_emotions()
    
    def _calculate_fear_greed_index(self) -> int:
        """Calculate an approximation of the fear and greed index."""
        try:
            # Get major coin price changes
            btc_change = self.web_data.get_24h_change("BTC")
            eth_change = self.web_data.get_24h_change("ETH")
            
            # Weight the changes (BTC has more influence)
            weighted_change = (btc_change * 0.6) + (eth_change * 0.4)
            
            # Convert to a 0-100 scale, where:
            # - Extreme fear: 0-25
            # - Fear: 25-40
            # - Neutral: 40-60
            # - Greed: 60-75
            # - Extreme greed: 75-100
            
            # Base value (neutral)
            fear_greed = 50
            
            # Adjust based on price changes
            if weighted_change > 5:
                fear_greed += 30  # Strong positive - extreme greed
            elif weighted_change > 2:
                fear_greed += 20  # Moderate positive - greed
            elif weighted_change > 0:
                fear_greed += 10  # Slight positive - mild greed
            elif weighted_change > -2:
                fear_greed -= 10  # Slight negative - mild fear
            elif weighted_change > -5:
                fear_greed -= 20  # Moderate negative - fear
            else:
                fear_greed -= 30  # Strong negative - extreme fear
            
            # Ensure within 0-100 range
            return max(0, min(100, fear_greed))
            
        except Exception as e:
            logger.error(f"Error calculating fear and greed index: {str(e)}")
            return 50  # Default to neutral
    
    def _fallback_market_emotions(self) -> Dict[str, Any]:
        """Fallback market emotions when the API is unavailable."""
        fear_greed = self._calculate_fear_greed_index()
        
        # Determine emotions based on fear/greed value
        if fear_greed >= 75:
            primary = "exuberance"
            secondary = "optimism"
            state = "expansive awareness"
            alignment = "ascending harmonic"
        elif fear_greed >= 60:
            primary = "confidence"
            secondary = "anticipation"
            state = "growth mindset"
            alignment = "positive flow"
        elif fear_greed >= 40:
            primary = "equilibrium"
            secondary = "contemplation"
            state = "centered awareness"
            alignment = "balanced"
        elif fear_greed >= 25:
            primary = "caution"
            secondary = "uncertainty"
            state = "protective awareness"
            alignment = "restrictive flow"
        else:
            primary = "fear"
            secondary = "anxiety"
            state = "survival consciousness"
            alignment = "defensive pattern"
        
        return {
            "primary_emotion": primary,
            "secondary_emotion": secondary,
            "consciousness_state": state,
            "cosmic_alignment": alignment,
            "resonance": fear_greed / 10,
            "energetic_pattern": "fluctuating",
            "guidance": "Maintain awareness of emotional biases in decision making",
            "fear_greed_index": fear_greed,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_cross_network_insights(self) -> Dict[str, Any]:
        """Get insights across all blockchain networks."""
        try:
            networks = self.network_config.get_layer2_networks()
            network_ids = [network.get('id') for network in networks]
            
            # Get gas prices for all networks
            gas_prices = {}
            for network_id in network_ids:
                gas_data = self.l2_gas_estimator.get_gas_price(network_id)
                gas_prices[network_id] = gas_data
            
            # Get network comparisons
            network_comparisons = self.network_config.compare_networks('ETH')
            
            # Get a holistic view with DeepSeek if available
            if self.api_key:
                insights = await self._generate_network_insights(network_comparisons, gas_prices)
            else:
                insights = {
                    "optimal_network": self._determine_optimal_network(gas_prices),
                    "congestion_levels": self._determine_congestion_levels(gas_prices),
                    "recommendation": "Use Layer 2 networks for better cost efficiency"
                }
            
            return {
                "gas_prices": gas_prices,
                "network_comparisons": network_comparisons,
                "insights": insights,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting cross-network insights: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _generate_network_insights(self, comparisons: List[Dict[str, Any]], 
                                       gas_prices: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate network insights using DeepSeek AI."""
        try:
            # Prepare context for AI
            networks_context = []
            for network in comparisons:
                gas_data = gas_prices.get(network.get('network', ''), {})
                networks_context.append({
                    "name": network.get('name', ''),
                    "type": network.get('type', ''),
                    "layer": network.get('layer', 1),
                    "gas_cost_gwei": gas_data.get('max_fee', 0),
                    "gas_cost_usd": gas_data.get('usd_cost', 0),
                    "security_score": network.get('security', 5),
                    "speed_score": network.get('speed', 5),
                    "cost_score": network.get('cost', 5)
                })
            
            prompt = f"""As an expert in blockchain networks and Layer 2 solutions, analyze the current state of these networks:

{json.dumps(networks_context, indent=2)}

Provide insights on:
1. The optimal network for transactions right now
2. Network congestion levels
3. Cost efficiency ranking
4. Security considerations
5. Strategic recommendations for traders

Format your response as a JSON object:
{{
  "optimal_network": string,
  "congestion_levels": object,
  "cost_efficiency_ranking": array,
  "security_insights": string,
  "strategic_recommendations": string
}}"""

            response = self._call_deepseek_api(prompt, model=self.models["chat"])
            
            insights = self._extract_json_from_response(response)
            if not insights:
                # Fallback
                insights = {
                    "optimal_network": self._determine_optimal_network(gas_prices),
                    "congestion_levels": self._determine_congestion_levels(gas_prices),
                    "recommendation": "Use Layer 2 networks for better cost efficiency"
                }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating network insights: {str(e)}")
            return {
                "optimal_network": self._determine_optimal_network(gas_prices),
                "congestion_levels": self._determine_congestion_levels(gas_prices),
                "recommendation": "Use Layer 2 networks for better cost efficiency"
            }
    
    def _determine_optimal_network(self, gas_prices: Dict[str, Dict[str, Any]]) -> str:
        """Determine the optimal network based on gas prices."""
        try:
            if not gas_prices:
                return "ethereum"
            
            # Find network with lowest USD cost
            lowest_cost = float('inf')
            optimal_network = "ethereum"
            
            for network, gas_data in gas_prices.items():
                usd_cost = gas_data.get('usd_cost', float('inf'))
                if usd_cost < lowest_cost:
                    lowest_cost = usd_cost
                    optimal_network = network
            
            return optimal_network
            
        except Exception as e:
            logger.error(f"Error determining optimal network: {str(e)}")
            return "ethereum"
    
    def _determine_congestion_levels(self, gas_prices: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Determine congestion levels for each network based on gas prices."""
        congestion_levels = {}
        
        try:
            for network, gas_data in gas_prices.items():
                gas_price = gas_data.get('max_fee', 0)
                
                if network == "ethereum":
                    if gas_price < 20:
                        level = "low"
                    elif gas_price < 80:
                        level = "medium"
                    else:
                        level = "high"
                else:  # L2 networks
                    if gas_price < 1:
                        level = "low"
                    elif gas_price < 5:
                        level = "medium"
                    else:
                        level = "high"
                
                congestion_levels[network] = level
                
            return congestion_levels
            
        except Exception as e:
            logger.error(f"Error determining congestion levels: {str(e)}")
            return {}

# Import at the end to avoid circular imports
import re
import random
from datetime import datetime

# Global instance
market_analyzer = DeepSeekMarketAnalyzer()
