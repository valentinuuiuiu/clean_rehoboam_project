import numpy as np
from typing import List, Optional, Tuple, Dict, Any, Union
from datetime import datetime
import time
from dataclasses import dataclass
import logging
import traceback
from utils.logging_config import setup_logging
from textblob import TextBlob
from sklearn.linear_model import LinearRegression

logger = setup_logging()

@dataclass
class EmotionState:
    """
    Represents the emotional state of the market with advanced metrics.

    Attributes:
        primary (str): Primary emotion (e.g., 'fear', 'greed', 'confidence')
        intensity (float): Strength of the emotion [0-1]
        confidence (float): Confidence in the emotion detection [0-1]
        market_pulse (float): Overall market vitality measure [0-1]
        regime_state (str): Current market regime state
        secondary_emotions (Dict[str, float]): Secondary emotional influences
        emotional_momentum (float): Rate of emotional state change [-1 to 1]
        market_coherence (float): How unified market participants are [0-1]
        volatility_impact (float): How volatility affects emotions [0-1]
        sentiment_balance (float): Balance between positive/negative sentiment [-1 to 1]
    """
    primary: str
    intensity: float
    confidence: float
    market_pulse: float
    regime_state: str
    secondary_emotions: Dict[str, float] = None
    emotional_momentum: float = 0.0
    market_coherence: float = 0.5
    volatility_impact: float = 0.0
    sentiment_balance: float = 0.0

    def __post_init__(self):
        """Initialize optional fields if not provided"""
        if self.secondary_emotions is None:
            self.secondary_emotions = {}

    def get_dominant_emotion(self) -> Tuple[str, float]:
        """Returns the strongest emotion and its intensity"""
        if not self.secondary_emotions:
            return (self.primary, self.intensity)

        strongest = max(self.secondary_emotions.items(), key=lambda x: x[1])
        if strongest[1] > self.intensity:
            return strongest
        return (self.primary, self.intensity)

    def get_emotional_stability(self) -> float:
        """Calculate emotional stability score [0-1]"""
        factors = [
            self.confidence,
            1 - abs(self.emotional_momentum),
            self.market_coherence
        ]
        return sum(factors) / len(factors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert emotional state to dictionary for serialization"""
        return {
            'primary': self.primary,
            'intensity': float(self.intensity),
            'confidence': float(self.confidence),
            'market_pulse': float(self.market_pulse),
            'regime_state': self.regime_state,
            'secondary_emotions': self.secondary_emotions,
            'emotional_momentum': float(self.emotional_momentum),
            'market_coherence': float(self.market_coherence),
            'volatility_impact': float(self.volatility_impact),
            'sentiment_balance': float(self.sentiment_balance),
            'stability': float(self.get_emotional_stability())
        }

@dataclass
class TradingSignal:
    type: str  # 'buy', 'sell', or 'hold'
    strength: float  # 0 to 1
    confidence: float  # 0 to 1
    timeframe: str  # 'short', 'medium', 'long'
    indicators: Dict[str, float]
    timestamp: datetime

class MarketHeartbeat:
    def __init__(self):
        self.pulse_history = []
        self.rhythm_patterns = []
        self.vitality_score = 0.5
        self.last_pulse_time = time.time()
        self.emotional_resonance = []
        self.heartbeat_variability = []
        self.regime_sensitivity = 0.5

    def measure_pulse(self, price: float, volume: float, time_delta: float) -> float:
        """Calculate market pulse strength with enhanced emotional resonance"""
        try:
            # Normalize volume changes with exponential smoothing
            volume_intensity = min(1.0, volume / (sum(self.pulse_history[-10:]) / 10) if self.pulse_history else 1.0)

            # Calculate price momentum with emotional sensitivity
            price_momentum = abs(price - self.pulse_history[-1]) if self.pulse_history else 0
            price_intensity = min(1.0, price_momentum / price if price > 0 else 0)

            # Emotional resonance wave calculation
            resonance = self._calculate_resonance_wave(price_intensity, volume_intensity)

            # Enhanced pulse strength with emotional resonance
            pulse_strength = (volume_intensity * 0.5 + 
                            price_intensity * 0.3 + 
                            resonance * 0.2)

            # Calculate heartbeat variability
            if len(self.pulse_history) > 1:
                variability = np.std(self.pulse_history[-10:]) if len(self.pulse_history) >= 10 else 0
                self.heartbeat_variability.append(variability)

            # Store pulse with emotional context
            self.pulse_history.append(pulse_strength)
            if len(self.pulse_history) > 100:
                self.pulse_history.pop(0)

            # Update regime sensitivity based on variability
            self._update_regime_sensitivity()

            return pulse_strength

        except Exception as e:
            logger.error(f"Error measuring market pulse: {str(e)}")
            return 0.5

    def _calculate_resonance_wave(self, price_intensity: float, volume_intensity: float) -> float:
        """Calculate emotional resonance wave based on price and volume harmonics"""
        try:
            if len(self.pulse_history) < 2:
                return 0.5

            # Calculate wave frequencies
            price_freq = np.fft.fft(self.pulse_history[-20:]) if len(self.pulse_history) >= 20 else [0]
            dominant_freq = np.abs(price_freq[1:]).argmax() + 1 if len(price_freq) > 1 else 0

            # Calculate resonance factors
            price_resonance = np.exp(-abs(price_intensity - np.mean(self.pulse_history[-5:])))
            volume_resonance = np.exp(-abs(volume_intensity - np.mean(self.pulse_history[-5:])))

            # Combine into resonance wave
            resonance = (price_resonance * 0.6 + volume_resonance * 0.4) * (1 + dominant_freq/10)

            # Store resonance history
            self.emotional_resonance.append(float(resonance))
            if len(self.emotional_resonance) > 50:
                self.emotional_resonance.pop(0)

            return min(1.0, resonance)

        except Exception as e:
            logger.error(f"Error calculating resonance wave: {str(e)}")
            return 0.5

    def _update_regime_sensitivity(self):
        """Update market regime transition sensitivity based on heartbeat patterns"""
        try:
            if len(self.heartbeat_variability) < 10:
                return

            # Calculate recent variability trend
            recent_var = self.heartbeat_variability[-10:]
            var_trend = np.polyfit(range(len(recent_var)), recent_var, 1)[0]

            # Update sensitivity based on variability trend
            if var_trend > 0:
                # Increasing variability suggests regime transition
                self.regime_sensitivity = min(1.0, self.regime_sensitivity + 0.1)
            else:
                # Decreasing variability suggests stable regime
                self.regime_sensitivity = max(0.1, self.regime_sensitivity - 0.05)

        except Exception as e:
            logger.error(f"Error updating regime sensitivity: {str(e)}")

    def detect_rhythm(self) -> Dict[str, float]:
        """Enhanced rhythm pattern detection with emotional context"""
        if len(self.pulse_history) < 20:
            return {'pattern': 'unknown', 'confidence': 0.0}

        try:
            # Analyze recent pulses with wavelet transform for better pattern recognition
            recent_pulses = np.array(self.pulse_history[-20:])

            # Calculate rhythm metrics
            rhythm_variability = np.std(recent_pulses)
            rhythm_momentum = np.mean(np.diff(recent_pulses))
            rhythm_acceleration = np.mean(np.diff(np.diff(recent_pulses)))

            # Enhanced pattern detection
            steady = rhythm_variability < 0.1 and abs(rhythm_momentum) < 0.05
            accelerating = rhythm_acceleration > 0 and rhythm_momentum > 0
            pulsing = any(np.abs(np.diff(recent_pulses)) > 0.2)
            contracting = rhythm_acceleration < 0 and rhythm_variability < 0.15

            # Determine dominant pattern with confidence
            if steady and rhythm_variability < 0.05:
                pattern = 'deep_steady'
                confidence = 0.9
            elif steady:
                pattern = 'steady'
                confidence = 0.8
            elif accelerating and rhythm_acceleration > 0.1:
                pattern = 'strong_acceleration'
                confidence = 0.85
            elif accelerating:
                pattern = 'accelerating'
                confidence = 0.7
            elif pulsing and rhythm_variability > 0.3:
                pattern = 'erratic_pulsing'
                confidence = 0.75
            elif pulsing:
                pattern = 'pulsing'
                confidence = 0.6
            elif contracting:
                pattern = 'contracting'
                confidence = 0.65
            else:
                pattern = 'irregular'
                confidence = 0.5

            # Adjust confidence based on regime sensitivity
            confidence *= (0.5 + self.regime_sensitivity)

            return {
                'pattern': pattern,
                'confidence': min(1.0, confidence),
                'metrics': {
                    'variability': float(rhythm_variability),
                    'momentum': float(rhythm_momentum),
                    'acceleration': float(rhythm_acceleration)
                }
            }

        except Exception as e:
            logger.error(f"Error in rhythm detection: {str(e)}")
            return {'pattern': 'unknown', 'confidence': 0.0}

class EmotionAnalyzer:
    """Advanced market emotion analyzer with enhanced pattern recognition"""

    def __init__(self):
        self.heartbeat = MarketHeartbeat()
        self.sentiment_memory = []
        self.emotional_state = 'neutral'
        self.confidence = 0.5
        self.emotional_patterns = []
        self.regime_transitions = []
        self.emotion_wavelength = 0

    def detect_market_emotion(self, price_data: Dict, volume_data: Dict, additional_indicators: Dict) -> EmotionState:
        """Enhanced market emotion detection with advanced pattern recognition"""
        try:
            # Get current price and volume
            current_price = price_data['close'][-1] if price_data['close'] else 0
            current_volume = volume_data['volume'][-1] if volume_data['volume'] else 0

            # Measure market heartbeat
            pulse_strength = self.heartbeat.measure_pulse(
                price=current_price,
                volume=current_volume,
                time_delta=time.time() - self.heartbeat.last_pulse_time
            )
            self.heartbeat.last_pulse_time = time.time()

            # Detect market rhythm
            rhythm = self.heartbeat.detect_rhythm()

            # Calculate market vitality
            vitality = min(1.0, pulse_strength * (1 + rhythm['confidence']))

            # Calculate emotional wavelength
            self.emotion_wavelength = self._calculate_emotional_wavelength(price_data, volume_data)

            # Determine emotional state with enhanced pattern recognition
            emotional_state = self._determine_emotion(
                pulse_strength=pulse_strength,
                rhythm=rhythm,
                vitality=vitality,
                rsi=additional_indicators.get('rsi', 50),
                wavelength=self.emotion_wavelength
            )

            # Calculate secondary emotions
            secondary_emotions = self._calculate_secondary_emotions(
                price_data=price_data,
                volume_data=volume_data,
                indicators=additional_indicators,
                primary_emotion=emotional_state['primary']
            )

            # Calculate emotional momentum
            momentum_type, momentum_strength = self.get_emotional_momentum()

            # Create enhanced EmotionState
            state = EmotionState(
                primary=emotional_state['primary'],
                intensity=pulse_strength,
                confidence=rhythm['confidence'],
                market_pulse=vitality,
                regime_state=emotional_state['regime'],
                secondary_emotions=secondary_emotions,
                emotional_momentum=momentum_strength,
                market_coherence=self._calculate_market_coherence(price_data, volume_data),
                volatility_impact=self._calculate_volatility_impact(price_data),
                sentiment_balance=self._calculate_sentiment_balance(additional_indicators)
            )

            # Update sentiment memory
            self.sentiment_memory.append(state)
            if len(self.sentiment_memory) > 50:
                self.sentiment_memory.pop(0)

            return state

        except Exception as e:
            logger.error(f"Error in market emotion detection: {str(e)}")
            return EmotionState(
                primary='neutral',
                intensity=0.5,
                confidence=0.5,
                market_pulse=0.5,
                regime_state='neutral'
            )

    def _calculate_emotional_wavelength(self, price_data: Dict, volume_data: Dict) -> float:
        """Calculate the emotional wavelength of the market"""
        try:
            if not price_data['close'] or len(price_data['close']) < 2:
                return 0.0

            # Calculate price changes
            price_changes = np.diff(price_data['close'])
            volume_changes = np.diff(volume_data['volume']) if volume_data['volume'] else np.zeros_like(price_changes)

            # Calculate wavelength using FFT
            if len(price_changes) >= 10:
                fft_result = np.fft.fft(price_changes)
                dominant_freq = np.argmax(np.abs(fft_result[1:len(fft_result)//2])) + 1
                wavelength = len(price_changes) / dominant_freq if dominant_freq > 0 else len(price_changes)
                return min(1.0, wavelength / len(price_changes))

            return 0.5

        except Exception as e:
            logger.error(f"Error calculating emotional wavelength: {str(e)}")
            return 0.5

    def _calculate_secondary_emotions(
        self, 
        price_data: Dict, 
        volume_data: Dict, 
        indicators: Dict,
        primary_emotion: str
    ) -> Dict[str, float]:
        """Calculate secondary market emotions"""
        try:
            emotions = {
                'anticipation': 0.0,
                'uncertainty': 0.0,
                'optimism': 0.0,
                'pessimism': 0.0,
                'conviction': 0.0
            }

            if not price_data['close'] or len(price_data['close']) < 2:
                return emotions

            # Calculate recent price momentum
            recent_returns = np.diff(price_data['close'][-10:]) / price_data['close'][-11:-1]
            momentum = np.mean(recent_returns) if len(recent_returns) > 0 else 0

            # RSI-based emotion modulation
            rsi = indicators.get('rsi', 50)
            if rsi > 70:
                emotions['optimism'] = min(1.0, (rsi - 70) / 30)
            elif rsi < 30:
                emotions['pessimism'] = min(1.0, (30 - rsi) / 30)

            # Volume-based conviction
            if volume_data['volume'] and len(volume_data['volume']) > 1:
                vol_change = volume_data['volume'][-1] / np.mean(volume_data['volume'][-10:])
                emotions['conviction'] = min(1.0, vol_change - 1) if vol_change > 1 else 0

            # Uncertainty based on price volatility
            if len(price_data['close']) > 20:
                volatility = np.std(recent_returns) * np.sqrt(252)
                emotions['uncertainty'] = min(1.0, volatility)

            # Anticipation based on pattern completion
            pattern_completion = self._detect_pattern_completion(price_data['close'])
            emotions['anticipation'] = pattern_completion

            return emotions

        except Exception as e:
            logger.error(f"Error calculating secondary emotions: {str(e)}")
            return {}

    def _detect_pattern_completion(self, prices: List[float]) -> float:
        """Detect the completion level of known patterns"""
        try:
            if len(prices) < 20:
                return 0.0

            # Calculate pattern completion based on recent price action
            recent_prices = prices[-20:]
            pattern_score = 0.0

            # Check for common patterns (head and shoulders, double top/bottom, etc.)
            patterns = self._identify_patterns(recent_prices)
            if patterns:
                completion_scores = [p['completion'] for p in patterns]
                pattern_score = max(completion_scores)

            return min(1.0, pattern_score)

        except Exception as e:
            logger.error(f"Error detecting pattern completion: {str(e)}")
            return 0.0

    def _identify_patterns(self, prices: List[float]) -> List[Dict[str, float]]:
        """Identify technical patterns in price data"""
        patterns = []
        try:
            # Calculate local maxima and minima
            peaks = []
            troughs = []
            for i in range(1, len(prices)-1):
                if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
                    peaks.append((i, prices[i]))
                elif prices[i] < prices[i-1] and prices[i] < prices[i+1]:
                    troughs.append((i, prices[i]))

            # Check for head and shoulders pattern
            if len(peaks) >= 3 and len(troughs) >= 2:
                # Head and shoulders logic
                for i in range(len(peaks)-2):
                    p1, p2, p3 = peaks[i:i+3]
                    if p2[1] > p1[1] and p2[1] > p3[1] and abs(p1[1] - p3[1]) < 0.1 * p2[1]:
                        completion = min(1.0, (len(prices) - p3[0]) / 5)
                        patterns.append({
                            'type': 'head_and_shoulders',
                            'completion': completion
                        })

            # Add other pattern recognition logic here

            return patterns

        except Exception as e:
            logger.error(f"Error identifying patterns: {str(e)}")
            return []


    def _determine_emotion(self, pulse_strength: float, rhythm: Dict, vitality: float, rsi: float, wavelength: float) -> Dict[str, str]:
        """Determine market emotion based on multiple factors"""
        # High vitality with strong rhythm suggests confidence
        if vitality > 0.8 and rhythm['confidence'] > 0.7:
            if rsi > 70:
                return {'primary': 'greed', 'regime': 'euphoria'}
            elif rsi < 30:
                return {'primary': 'fear', 'regime': 'panic'}
            else:
                return {'primary': 'confidence', 'regime': 'momentum'}

        # Low vitality suggests exhaustion
        if vitality < 0.3:
            if rhythm['pattern'] == 'irregular':
                return {'primary': 'uncertainty', 'regime': 'transition'}
            else:
                return {'primary': 'exhaustion', 'regime': 'distribution'}

        # Moderate vitality with clear rhythm suggests normal conditions
        if 0.3 <= vitality <= 0.7 and rhythm['confidence'] > 0.6:
            if rhythm['pattern'] == 'steady':
                return {'primary': 'calm', 'regime': 'accumulation'}
            elif rhythm['pattern'] == 'accelerating':
                return {'primary': 'anticipation', 'regime': 'breakout'}
            else:
                return {'primary': 'neutral', 'regime': 'ranging'}

        # Default state for unclear conditions
        return {'primary': 'neutral', 'regime': 'unknown'}

    def get_emotional_momentum(self) -> Tuple[str, float]:
        """Analyze emotional state transitions"""
        if len(self.sentiment_memory) < 2:
            return 'neutral', 0.0

        recent_emotions = self.sentiment_memory[-10:]

        # Detect emotional transitions
        emotion_counts = {}
        for emotion in recent_emotions:
            primary = emotion.primary
            emotion_counts[primary] = emotion_counts.get(primary, 0) + 1

        dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
        transition_strength = emotion_counts[dominant_emotion] / len(recent_emotions)

        # Identify emotional momentum type
        if dominant_emotion == 'fear' and self.emotional_state == 'greed':
            momentum_type = 'greed_to_fear'
        elif dominant_emotion == 'greed' and self.emotional_state == 'fear':
            momentum_type = 'fear_to_greed'
        elif dominant_emotion == 'confidence' and self.emotional_state == 'uncertainty':
            momentum_type = 'uncertainty_to_confidence'
        elif dominant_emotion == 'uncertainty' and self.emotional_state == 'confidence':
            momentum_type = 'confidence_to_uncertainty'
        else:
            momentum_type = f'{self.emotional_state}_to_{dominant_emotion}'

        # Update emotional state
        self.emotional_state = dominant_emotion

        return momentum_type, transition_strength

    def _calculate_market_coherence(self, price_data: Dict, volume_data: Dict) -> float:
        """Calculate market coherence using price and volume correlation"""
        try:
            if not price_data['close'] or not volume_data['volume'] or len(price_data['close']) < 10:
                return 0.5

            correlation = np.corrcoef(price_data['close'][-10:], volume_data['volume'][-10:])[0, 1]
            return abs(correlation)

        except Exception as e:
            logger.error(f"Error calculating market coherence: {str(e)}")
            return 0.5

    def _calculate_volatility_impact(self, price_data: Dict) -> float:
        """Estimate volatility's influence on market emotion"""
        try:
            if not price_data['close'] or len(price_data['close']) < 10:
                return 0.0

            # Calculate volatility using standard deviation of price changes
            returns = np.diff(price_data['close'][-10:]) / price_data['close'][-11:-1]
            volatility = np.std(returns)

            # Map volatility to impact on a scale of 0 to 1
            impact = min(1.0, volatility * 5)  # Adjust the scaling factor as needed
            return impact

        except Exception as e:
            logger.error(f"Error calculating volatility impact: {str(e)}")
            return 0.0

    def _calculate_sentiment_balance(self, indicators: Dict) -> float:
        """Calculate balance between positive and negative sentiment"""
        try:
            rsi = indicators.get('rsi', 50)
            balance = (rsi - 50) / 50  # Scale between -1 and 1
            return balance

        except Exception as e:
            logger.error(f"Error calculating sentiment balance: {str(e)}")
            return 0.0


class SentimentAnalyzer:
    def __init__(self):
        self.sentiment_memory = []

    def analyze_sentiment(self, text: str) -> float:
        analysis = TextBlob(text)
        return analysis.sentiment.polarity

    def update_sentiment_memory(self, sentiment: float):
        self.sentiment_memory.append(sentiment)
        if len(self.sentiment_memory) > 100:
            self.sentiment_memory.pop(0)

    def get_average_sentiment(self) -> float:
        if not self.sentiment_memory:
            return 0.0
        return sum(self.sentiment_memory) / len(self.sentiment_memory)

class TradingAlgorithms:
    def __init__(self, price_history_length: int = 100):
        """Initialize with enhanced error handling and logging"""
        try:
            # Core price tracking
            self.price_history: List[float] = []
            self.price_history_length = price_history_length
            self.last_macd_signal = 0

            # Network and price tracking with validation
            self.network_price_history: Dict[str, Dict[str, List[float]]] = {
                network: {} for network in ['ethereum', 'arbitrum', 'polygon', 'avalanche']
            }

            # Initialize other tracking components
            self._initialize_tracking_components()
            self.emotion_analyzer = EmotionAnalyzer() # Initialize emotion analyzer
            self.sentiment_analyzer = SentimentAnalyzer()
            logger.info("TradingAlgorithms initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TradingAlgorithms: {str(e)}")
            raise

    def _initialize_tracking_components(self):
        """Initialize all tracking components with proper validation"""
        try:
            # Gas optimization
            self.gas_price_history = {network: [] for network in self.network_price_history.keys()}

            # Transaction timing with realistic values
            self.network_transaction_times = {
                'ethereum': 15,  # Base block time
                'arbitrum': 1,
                'polygon': 2,
                'avalanche': 2
            }

            # Historical data across timeframes
            self.historical_data = {
                timeframe: [] for timeframe in ['1m', '5m', '15m', '1h', '4h', '1d']
            }

            # Initialize liquidity tracking
            self.liquidity_data = {
                network: {} for network in self.network_price_history.keys()
            }

            # Market conditions with default values
            self.market_conditions = {
                'normal': 1.0,
                'high_volatility': 0.0,
                'low_liquidity': 0.0,
                'network_congestion': 0.0
            }

            # Core parameters with safety bounds
            self.min_profit_threshold = 0.02  # 2% minimum profit after gas
            self.base_profit_threshold = 0.02  # Base threshold for adaptation

            # Timeframe specific data
            self.timeframe_price_history: Dict[str, List[float]] = {
                '1h': [], '4h': [], '1d': [], '1w': []
            }

            logger.info("Trading components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize trading components: {str(e)}")
            raise

    def set_market_condition(self, condition: str, severity: float) -> None:
        """Update market condition severity"""
        if condition in self.market_conditions:
            self.market_conditions[condition] = max(0.0, min(1.0, severity))

    def analyze_liquidity(self, network: str, token: str) -> float:
        """Analyze liquidity for a given network and token pair"""
        if network not in self.liquidity_data or token not in self.liquidity_data[network]:
            return 0.0

        liquidity_history = self.liquidity_data[network][token]
        if not liquidity_history:
            return 0.0

        recent_liquidity = liquidity_history[-min(len(liquidity_history), 10):]
        avg_liquidity = sum(recent_liquidity) / len(recent_liquidity)

        # Normalize to [0, 1] range assuming 1M USD as maximum liquidity
        return min(1.0, avg_liquidity / 1_000_000.0)

    def get_network_liquidity(self, network: str, token: str) -> float:
        """Get current liquidity for a network-token pair"""
        if (network not in self.liquidity_data or 
            token not in self.liquidity_data[network] or
            not self.liquidity_data[network][token]):
            return 0.0
        return self.liquidity_data[network][token][-1]

    def find_arbitrage_paths(self, token: str) -> List[Dict[str, Any]]:
        """Find optimal arbitrage paths including multi-hop opportunities"""
        try:
            logger.info(f"Searching for arbitrage paths for {token}")
            paths = []
            networks = ['ethereum', 'arbitrum', 'polygon', 'avalanche']

            # Single-hop paths (direct arbitrage)
            for buy_network in networks:
                for sell_network in networks:
                    if buy_network != sell_network:
                        try:
                            buy_price = self.get_network_price(buy_network, token)
                            sell_price = self.get_network_price(sell_network, token)

                            logger.debug(f"Prices for {token}: {buy_network}={buy_price}, {sell_network}={sell_price}")

                            if not buy_price or not sell_price:
                                continue

                            # Calculate liquidity metrics
                            liquidity_scores = self.calculate_cross_chain_liquidity(token)
                            buy_liquidity = liquidity_scores.get(buy_network, 0.0)
                            sell_liquidity = liquidity_scores.get(sell_network, 0.0)

                            # Skip if liquidity is too low
                            if buy_liquidity < 0.3 or sell_liquidity < 0.3:
                                logger.debug(f"Insufficient liquidity for {token} on {buy_network}-{sell_network}")
                                continue

                            # Optimize gas usage
                            buy_gas = self.optimize_gas_usage(buy_network)
                            sell_gas = self.optimize_gas_usage(sell_network)

                            # Calculate potential profit
                            price_diff = sell_price - buy_price
                            total_gas_cost = buy_gas.get('optimal_gas_price', 0) + sell_gas.get('optimal_gas_price', 0)
                            profit_potential = price_diff - total_gas_cost

                            if profit_potential <= 0:
                                continue

                            logger.info(f"Found profitable path for {token}: {buy_network}->{sell_network}, profit=${profit_potential:.2f}")

                            paths.append({
                                'type': 'single_hop',
                                'token': token,
                                'buy_network': buy_network,
                                'sell_network': sell_network,
                                'buy_price': float(buy_price),
                                'sell_price': float(sell_price),
                                'liquidity_confidence': min(buy_liquidity, sell_liquidity),
                                'profit_potential': float(profit_potential),
                                'gas_estimate': {
                                    'buy': buy_gas.get('optimal_gas_price', 0),
                                    'sell': sell_gas.get('optimal_gas_price', 0)
                                }
                            })

                        except Exception as e:
                            logger.error(f"Error processing path {buy_network}->{sell_network}: {str(e)}")
                            continue

            # Sort paths by profit potential and liquidity confidence
            paths.sort(
                key=lambda x: x['profit_potential'] * x['liquidity_confidence'],
                reverse=True
            )

            return paths[:5]  # Return top 5 most profitable paths

        except Exception as e:
            logger.error(f"Error in find_arbitrage_paths: {str(e)}\n{traceback.format_exc()}")
            return []

    def calculate_max_trade_size(self, token: str, buy_network: str, sell_network: str) -> float:
        """Calculate maximum trade size based on liquidity constraints"""
        buy_liquidity = self.get_network_liquidity(buy_network, token)
        sell_liquidity = self.get_network_liquidity(sell_network, token)

        # Use 10% of available liquidity as maximum trade size
        max_size = min(buy_liquidity, sell_liquidity) * 0.1

        # Apply additional constraints based on market conditions
        if self.market_conditions['low_liquidity'] > 0:
            max_size *= (1 - self.market_conditions['low_liquidity'])

        return max_size

    def analyze_historical_data(self, timeframe: str, window: int) -> Dict[str, float]:
        """Analyze historical data with enhanced invariant checks"""
        if timeframe not in self.historical_data:
            return {'trend': 0.0, 'volatility': 0.0, 'momentum': 0.0}

        data = self.historical_data[timeframe][-window:]
        if len(data) < window:
            return {'trend': 0.0, 'volatility': 0.0, 'momentum': 0.0}

        try:
            # Calculate trend with proper normalization
            prices = np.array(data)
            trend = np.polyfit(np.arange(len(prices)), prices, 1)[0]
            trend_normalized = np.tanh(trend / np.mean(prices) * 5)  # Reduced scaling factor for more stability

            # Calculate volatility with bounds
            returns = np.diff(np.log(prices))
            volatility = min(1.0, np.std(returns) * np.sqrt(252) / 2)  # Reduced annualization impact

            # Calculate momentum with tighter bounds
            momentum = (prices[-1] / prices[0] - 1.0)
            momentum_normalized = np.tanh(momentum * 2)  # Reduced scaling for more stability

            # Ensure all metrics are properly bounded
            return {
                'trend': float(max(-1.0, min(1.0, trend_normalized))),
                'volatility': float(max(0.0, min(1.0, volatility))),
                'momentum': float(max(-1.0, min(1.0, momentum_normalized)))
            }

        except Exception as e:
            logger.error(f"Error in historical analysis: {str(e)}")
            return {'trend': 0.0, 'volatility': 0.0, 'momentum': 0.0}

    def optimize_trading_strategy(self) -> Dict[str, Any]:
        """
        Optimize trading strategy based on market conditions with enhanced emotional intelligence
        """
        # Get base metrics
        market_regime = self.detect_market_regime()
        volatility = self.market_conditions.get('high_volatility', 0)

        # Get emotional state
        current_emotion = self.emotion_analyzer.detect_market_emotion(
            price_data={'close': self.price_history},
            volume_data={'volume': self.volume_history if hasattr(self, 'volume_history') else [1.0] * len(self.price_history)},
            additional_indicators={'rsi': self.calculate_rsi() if hasattr(self, 'calculate_rsi') else 50}
        )

        # Get emotional momentum
        momentum_type, momentum_strength = self.emotion_analyzer.get_emotional_momentum()

        # Calculate base position size (0.1 to 1.0)
        base_size = 0.5  # Start with moderate position

        # Adjust for market pulse (heartbeat)
        pulse_factor = 1.0 + (current_emotion.market_pulse - 0.5)  # Normalize around 0.5
        base_size *= max(0.1, min(2.0, pulse_factor))

        # Emotional state adjustments
        emotion_factors = {
            'fear': 0.7,      # Be cautious but ready to buy
            'greed': 0.8,     # Start reducing exposure
            'uncertainty': 0.5,# Reduce position size
            'confidence': 1.2, # Increase position size
            'exhaustion': 0.6  # Prepare for reversal
        }

        emotion_factor = emotion_factors.get(current_emotion.primary, 1.0)
        base_size *= emotion_factor * (0.5 + current_emotion.confidence)

        # Momentum adjustments
        momentum_factors = {
            'fear_to_greed': 1.3,      # Potential bottom forming
            'greed_to_fear': 0.7,      # Potential top forming
            'uncertainty_to_confidence': 1.2,  # Breakout potential
            'confidence_to_uncertainty': 0.8   # Consolidation likely
        }

        momentum_factor = momentum_factors.get(momentum_type, 1.0)
        base_size *= 1.0 + (momentum_factor - 1.0) * momentum_strength

        # Market regime specific adjustments with emotional context
        regime_factors = {
            'panic': 0.5 if current_emotion.primary == 'fear' else 1.2,
            'euphoria': 0.5 if current_emotion.primary == 'greed' else 0.8,
            'transition': 0.7,
            'accumulation': 1.3 if current_emotion.primary == 'confidence' else 1.0,
            'distribution': 0.6 if current_emotion.primary == 'exhaustion' else 0.8,
            'neutral': 1.0
        }

        regime_factor = regime_factors.get(current_emotion.regime_state, 0.5)
        base_size *= regime_factor

        # Ensure position size stays within bounds
        position_size = max(0.1, min(1.0, base_size))

        # Calculate entry and exit points with emotional awareness
        current_price = self.price_history[-1] if self.price_history else 0
        emotion_spread = 0.01 * (1 + current_emotion.intensity)  # Wider spread in intense emotions

        # Calculate adaptive entry points based on emotional state
        entry_points = []
        for i in range(3):
            # Deeper entries during fear, shallower during greed
            spread = emotion_spread * (1 + i) * (1.5 if current_emotion.primary == 'fear' else 0.8)
            entry_points.append(current_price * (1 - spread))

        # Calculate adaptive exit points based on emotional state
        exit_points = []
        for i in range(3):
            # Higher exits during greed, lower during fear
            spread = emotion_spread * (1 + i) * (1.5 if current_emotion.primary == 'greed' else 0.8)
            exit_points.append(current_price * (1 + spread))

        # Get market sentiment
        market_sentiment = self.sentiment_analyzer.get_average_sentiment()
        # Adjust position size based on sentiment
        if market_sentiment > 0.5:
            position_size *= 1.1  # Increase position size in positive sentiment
        elif market_sentiment < -0.5:
            position_size *= 0.9  # Decrease position size in negative sentiment

        # Get risk metrics
        risk_metrics = self.calculate_risk_metrics()
        # Adjust position size based on risk metrics
        if risk_metrics['volatility'] > 0.5:
            position_size *= 0.8  # Reduce position size in high volatility
        if risk_metrics['max_drawdown'] > 0.2:
            position_size *= 0.7  # Reduce position size in high drawdown
        if risk_metrics['sharpe_ratio'] < 1.0:
            position_size *= 0.9  # Reduce position size in low Sharpe ratio

        # Get ML price prediction
        ml_prediction = self.predict_price_ml()
        # Adjust position size based on ML prediction
        if ml_prediction > self.price_history[-1]:
            position_size *= 1.1  # Increase position size if price is predicted to rise
        elif ml_prediction < self.price_history[-1]:
            position_size *= 0.9  # Decrease position size if price is predicted to fall

        return {
            'position_size': float(position_size),
            'entry_points': entry_points,
            'exit_points': exit_points,
            'emotional_state': {
                'primary': current_emotion.primary,
                'intensity': current_emotion.intensity,
                'confidence': current_emotion.confidence,
                'market_pulse': current_emotion.market_pulse,
                'regime': current_emotion.regime_state
            },
            'market_sentiment': market_sentiment,
            'risk_metrics': risk_metrics,
            'ml_prediction': ml_prediction
        }

    def analyze_transaction_timing(self, trade_value: float) -> Dict[str, Dict[str, Any]]:
        """Analyze expected transaction timing across networks"""
        timing_analysis = {}

        for network, base_time in self.network_transaction_times.items():
            # Adjust for trade size
            size_factor = min(2.0, 1.0 + (trade_value / 100.0))

            # Network-specific adjustments
            if network == 'ethereum':
                congestion_factor = 1.5  # Higher base congestion
            else:
                congestion_factor = 1.2

            # Calculate estimated time
            estimated_time = int(base_time * size_factor * congestion_factor)

            # Calculate confidence based on timing
            confidence = max(0.0, min(1.0, 1.0 - (estimated_time / 600.0)))

            timing_analysis[network] = {
                'estimated_time': estimated_time,
                'confidence': confidence,
                'base_time': base_time,
                'congestion_factor': congestion_factor
            }

        return timing_analysis

    def analyze_timeframe_trend(self, timeframe: str) -> Dict[str, Any]:
        """Analyze trend characteristics for a specific timeframe"""
        if timeframe not in self.timeframe_price_history:
            return {'direction': 'unknown', 'strength': 0.0, 'volatility': 0.0}

        prices = self.timeframe_price_history[timeframe]
        if len(prices) < 2:
            return {'direction': 'unknown', 'strength': 0.0, 'volatility': 0.0}

        # Calculate trend
        returns = np.diff(np.log(prices))
        trend = np.mean(returns)
        volatility = np.std(returns)

        # Determine direction and strength
        if abs(trend) < 0.0001:
            direction = 'sideways'
            strength = 0.0
        else:
            direction = 'up' if trend > 0 else 'down'
            strength = min(1.0, abs(trend) * 100)

        return {
            'direction': direction,
            'strength': float(strength),
            'volatility': float(min(1.0, volatility * np.sqrt(252)))
        }


    def update_price_history(self, price: float) -> bool:
        """Update price history with enhanced validation"""
        try:
            if not isinstance(price, (int, float)) or price <= 0:
                logger.warning(f"Invalid price value received: {price}")
                return False

            if self.price_history:
                last_price = self.price_history[-1]
                price_change = abs(price - last_price) / last_price
                if price_change > 0.2:  # More than 20% change
                    logger.warning(f"Extreme price change detected: {price_change*100:.2f}%")
                    return False

            self.price_history.append(float(price))
            if len(self.price_history) > self.price_history_length:
                self.price_history.pop(0)

            return True
        except Exception as e:
            logger.error(f"Error updating price history: {str(e)}")
            return False

    def calculate_macd(self) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        """Calculate MACD with trend strength and histogram momentum"""
        try:
            if len(self.price_history) < 26:
                return None, None, None, None

            # Convert to numpy array and ensure float type
            prices = np.array(self.price_history, dtype=float)

            # Calculate EMAs using numpy for better performance
            ema12 = self._calculate_ema(prices, 12)
            ema26 = self._calculate_ema(prices, 26)

            if ema12 is None or ema26 is None:
                return None, None, None, None

            # Ensure floating point operations
            macd_line = float(ema12) - float(ema26)
            signal_line = self._calculate_ema(np.array([macd_line], dtype=float), 9)

            if signal_line is None:
                return None, None, None, None

            histogram = float(macd_line) - float(signal_line)

            # Calculate trend strength using histogram momentum
            # Use a single value for momentum when insufficient history
            hist_momentum = np.array([histogram], dtype=float)
            trend_strength = float(np.abs(hist_momentum).mean())

            return (
                float(macd_line),
                float(signal_line),
                float(histogram),
                float(trend_strength)
            )

        except (TypeError, ValueError, IndexError) as e:
            logger.error(f"Error calculating MACD: {str(e)}")
            return None, None, None, None

    def _calculate_ema(self, data: np.ndarray, periods: int) -> float:
        """
        Calculate EMA using numpy with enhanced error handling
        Returns a single float value for the most recent EMA
        """
        try:
            # Convert input to numpy array if it's not already
            data = np.array(data, dtype=float)
            if len(data) < periods:
                return float(data[-1]) if len(data) > 0 else 0.0

            alpha = 2 / (periods + 1)
            weights = (1 - alpha) ** np.arange(len(data))
            weights /= weights.sum()

            # Calculate EMA and return the most recent value as float
            ema_value = np.convolve(data, weights, mode='valid')
            return float(ema_value[-1]) if len(ema_value) > 0 else float(data[-1])

        except (TypeError, ValueError, IndexError) as e:
            logger.error(f"Error calculating EMA:: {str(e)}")
            return float(data[-1]) if len(data) > 0 else 0.0

    def calculate_momentum(self, period: int = 10) -> float:
        """Calculate price momentum using ROC (Rate of Change)"""
        if len(self.price_history) < period:
            return 0.0

        current_price = self.price_history[-1]
        past_price = self.price_history[-period]
        return ((current_price - past_price) / past_price) * 100

    def calculate_adx(self, period: int = 14) -> Optional[float]:
        """
        Calculate Average Directional Index with enhanced error handling
        and stability improvements
        """
        try:
            if len(self.price_history) < period + 1:
                return None

            # Convert to numpy array and ensure float type
            prices = np.array(self.price_history, dtype=float)
            highs = prices * 1.001  # Simulate high prices
            lows = prices * 0.999   # Simulate low prices

            # Calculate price movements
            high_diff = np.diff(highs)
            low_diff = np.diff(lows)

            # Calculate Directional Movement
            plus_dm = np.where(
                (high_diff > 0) & (high_diff > -low_diff),
                high_diff,
                0.0
            )
            minus_dm = np.where(
                (low_diff < 0) & (-low_diff > high_diff),
                -low_diff,
                0.0
            )

            # Calculate True Range with enhanced stability
            tr = np.maximum.reduce([
                highs[1:] - lows[1:],
                np.abs(highs[1:] - prices[:-1]),
                np.abs(lows[1:] - prices[:-1])
            ])

            # Apply smoothing with error handling
            smoothed_plus_dm = float(self._calculate_ema(plus_dm, period))
            smoothed_minus_dm = float(self._calculate_ema(minus_dm, period))
            smoothed_tr = float(self._calculate_ema(tr, period))

            # Handle division by zero
            if smoothed_tr == 0:
                return 0.0

            # Calculate DI+ and DI-
            plus_di = 100.0 * smoothed_plus_dm / smoothed_tr
            minus_di = 100.0 * smoothed_minus_dm / smoothed_tr

            # Calculate DX
            di_sum = plus_di + minus_di
            if di_sum == 0:
                return 0.0

            dx = 100.0 * abs(plus_di - minus_di) / di_sum

            # Return the ADX value
            return float(dx)

        except (TypeError, ValueError, IndexError, ZeroDivisionError) as e:
            logger.error(f"Error calculating ADX: {str(e)}")
            return None

    def detect_market_regime(self) -> str:
        """
        Advanced market regime detection using multiple indicators
        Returns detailed market regime classification
        """
        try:
            if len(self.price_history) < 30:
                return "unknown"

            # Enhanced indicator calculations with proper error handling
            try:
                bb_width = self.calculate_bollinger_band_width()
                adx = self.calculate_adx()
                momentum = self.calculate_momentum()
                rsi, divergence_exists, _ = self.calculate_rsi_with_divergence()
            except Exception as e:
                logger.error(f"Error calculating indicators: {str(e)}")
                return "unknown"

            if any(x is None for x in [bb_width, adx, rsi]):
                return "unknown"

            # Market phase detection with multiple factors
            adx_check = float(adx if adx is not None else 0)
            bb_width_check = float(bb_width if bb_width is not None else 0)
            rsi_check = float(rsi if rsi is not None else 50)
            momentum_check = float(momentum if momentum is not None else 0)

            # Strong trend detection
            if adx_check > 30:
                if momentum_check > 0:
                    return "strong_uptrend_momentum"
                return "strong_downtrend_momentum"

            # Volatility regime detection
            if bb_width_check > 0.2:
                if divergence_exists:
                    return "volatile_reversal_imminent"
                return "volatile_trend_continuation"

            # Range-bound market detection
            if bb_width_check < 0.05:
                if rsi_check < 30 or rsi_check > 70:
                    return "coiled_spring"
                return "balanced_range"

            # Default state
            return "early_trend_formation"

        except Exception as e:
            logger.error(f"Error in market regime detection: {str(e)}")
            return "unknown"

    def analyze_trend(self, period: int = 20) -> dict:
        """
        Enhanced trend analysis with multiple timeframes and momentum indicators
        Returns detailed trend analysis including strength, momentum, and confidence
        """
        default_result = {
            "direction": "neutral",
            "strength": 0.0,
            "momentum": 0.0,
            "confidence": 0.0
        }

        try:
            if len(self.price_history) < period:
                return default_result

            # Convert to numpy array and get multiple timeframe data
            prices = np.array(self.price_history[-period:], dtype=float)
            if len(prices) < period:
                return default_result

            short_term = prices[-min(period//4, len(prices)):]
            medium_term = prices[-min(period//2, len(prices)):]

            # Calculate slopes for multiple timeframes with error checking
            try:
                slopes = {
                    "short": float(np.polyfit(np.arange(len(short_term)), short_term, 1)[0]),
                    "medium": float(np.polyfit(np.arange(len(medium_term)), medium_term, 1)[0]),
                    "long": float(np.polyfit(np.arange(len(prices)), prices, 1)[0])
                }

                # Calculate R-squared values for trend strength
                r_squared = {
                    "short": float(np.corrcoef(np.arange(len(short_term)), short_term)[0, 1] ** 2),
                    "medium": float(np.corrcoef(np.arange(len(medium_term)), medium_term)[0, 1] ** 2),
                    "long": float(np.corrcoef(np.arange(len(prices)), prices)[0, 1] ** 2)
                }
            except (ValueError, np.linalg.LinAlgError) as e:
                logger.error(f"Error calculating trend metrics: {str(e)}")
                return default_result

            # Calculate momentum using ROC
            momentum = (prices[-1] / prices[0] - 1.0) * 100

            # Calculate weighted trend score
            weights = {"short": 0.5, "medium": 0.3, "long": 0.2}
            trend_score = sum(slopes[tf] * weights[tf] for tf in ["short", "medium", "long"])
            strength_score = sum(r_squared[tf] * weights[tf] for tf in ["short", "medium", "long"])

            # Determine trend direction and confidence
            if abs(trend_score) < 0.0001:
                direction = "neutral"
                strength = 0.0
            else:
                direction = "up" if trend_score > 0 else "down"
                strength = min(1.0, abs(trend_score) * strength_score * 10)
                direction = f"strong_{direction}" if strength > 0.7 else f"weak_{direction}"

            # Calculate confidence based on agreement between timeframes
            timeframe_agreement = sum(1 for s in slopes.values() if (s > 0) == (trend_score > 0))
            confidence = (timeframe_agreement / len(slopes)) * strength_score

            return {
                "direction": direction,
                "strength": float(strength),
                "momentum": float(momentum),
                "confidence": float(confidence),
                "timeframes": {
                    tf: {
                        "slope": float(slopes[tf]),
                        "r_squared": float(r_squared[tf])
                    } for tf in ["short", "medium", "long"]
                }
            }

        except (TypeError, ValueError, IndexError) as e:
            logger.error(f"Error in trend analysis: {str(e)}")
            return {
                "direction": "neutral",
                "strength": 0.0,
                "momentum": 0.0,
                "confidence": 0.0
            }

    def calculate_position_size(self, volatility_window: int = 20) -> float:
        """
        Calculate adaptive position size using advanced predictive analytics
        - Uses multiple timeframe analysis and advanced risk metrics
        - Implements dynamic adjustment based on market regimes
        - Incorporates volume profile and market microstructure
        - Advanced risk parity with tail risk hedging
        """
        if len(self.price_history) < volatility_window:
            return 1.0

        prices = np.array(self.price_history[-volatility_window:])
        returns = np.diff(np.log(prices))

        # Enhanced volatility metrics
        # 1. Parkinson's High-Low estimator
        high_low_ratio = np.max(prices) / np.min(prices)
        parkinson_vol = np.log(high_low_ratio) / np.sqrt(4 * np.log(2))

        # 2. Historical volatility with EWMA (Exponentially Weighted Moving Average)
        weights = np.exp(-np.arange(len(returns)) / 10)  # 10-day half-life
        weights /= weights.sum()
        hist_vol = np.sqrt(np.sum(weights * returns ** 2)) * np.sqrt(252)

        # 3. Jump volatility component
        daily_returns = returns * np.sqrt(252)
        jump_vol = np.sum(np.abs(daily_returns[daily_returns > 2 * hist_vol])) / len(returns)

        # Combine volatility metrics with dynamic weights
        vol_weights = [0.4, 0.4, 0.2]  # Weights for different volatility measures
        volatility = (vol_weights[0] * hist_vol +
                     vol_weights[1] * parkinson_vol +
                     vol_weights[2] * jump_vol)

        # Enhanced momentum analysis across timeframes
        timeframes = [5, 10, 20, 40]  # Multiple timeframes
        momentum_weights = [0.4, 0.3, 0.2, 0.1]  # More weight to recent momentum

        momentum_scores = []
        for tf in timeframes:
            if len(returns) >= tf:
                tf_momentum = np.mean(returns[-tf:]) * 100
                momentum_scores.append(tf_momentum)
            else:
                momentum_scores.append(0)

        # Weighted momentum with non-linear transformation
        momentum = sum(score * weight for score, weight in zip(momentum_scores, momentum_weights))
        momentum_factor = 2 / (1 + np.exp(-2 * momentum))  # Sigmoid transformation

        # Advanced market regime analysis
        market_regime = self.detect_market_regime()
        regime_factors = {
            'strong_uptrend_momentum': 1.3,
            'strong_uptrend_exhaustion': 0.7,
            'strong_downtrend_momentum': 0.6,
            'strong_downtrend_exhaustion': 0.8,
            'trend_reversal_potential': 0.5,
            'volatile_reversal_imminent': 0.4,
            'volatile_trend_continuation': 0.9,
            'volatile_distribution': 0.3,
            'volatile_accumulation': 1.1,
            'coiled_spring': 1.2,
            'deep_accumulation': 1.4,
            'stealth_accumulation': 1.2,
            'stealth_distribution': 0.6,
            'transition_with_divergence': 0.5,
            'balanced_range': 0.8,
            'early_trend_formation': 1.0,
            'unknown': 0.5
        }
        regime_factor = regime_factors.get(market_regime, 0.5)

        # Trend strength with correlation analysis
        _, _, _, trend_strength = self.calculate_macd()
        rsi, divergence_exists, divergence_strength = self.calculate_rsi_with_divergence()

        # Advanced trend factor calculation
        # Calculate trend confidence with proper None handling
        trend_confidence = float(trend_strength if trend_strength is not None else 0.0)
        if divergence_exists and divergence_strength is not None:
            trend_confidence *= (1.0 - float(divergence_strength))
        trend_factor = 1.0 + (trend_confidence * 0.5)

        # Enhanced risk parity with tail risk adjustment
        tail_risk_factor = 1.0
        if volatility > 0.4 or abs(momentum) > 3.0:  # High stress conditions
            tail_risk_factor = 0.7  # Reduce exposure in extreme conditions

        volatility_factor = np.exp(-2 * volatility) * tail_risk_factor
        risk_parity = 1 / (volatility + 0.1)  # Base risk parity

        # Dynamic base position with market microstructure
        # Calculate base position with safe RSI handling
        rsi_adjustment = ((float(rsi) - 50.0) / 100.0) if rsi is not None else 0.0
        base_position = 1.0 * regime_factor * (1.0 + rsi_adjustment)

        # Combine all factors with dynamic weights based on market conditions
        position_size = (base_position *
                        volatility_factor *
                        momentum_factor *
                        trend_factor *
                        risk_parity)

        # Dynamic position bounds based on market regime
        if market_regime.startswith('volatile'):
            max_size = 1.2
            min_size = 0.1
        elif market_regime.startswith('strong'):
            max_size = 2.0
            min_size = 0.3
        else:
            max_size = 1.5
            min_size = 0.2

        # Additional safety check for extreme market conditions
        if volatility > 0.5:  # Extremely high volatility
            max_size *= 0.5

        # Ensure position size is properly bounded
        position_size = max(min_size, min(max_size, position_size))

        return float(position_size)

    def calculate_bollinger_band_width(self, window: int = 20, num_std: float = 2.0) -> Optional[float]:
        """Calculate Bollinger Band width as a volatility indicator"""
        if len(self.price_history) < window:
            return None

        try:
            prices = np.array(self.price_history[-window:])
            ma = np.mean(prices)
            std = np.std(prices)

            upper = ma + (std * num_std)
            lower = ma - (std * num_std)

            # Return normalized width
            return float((upper - lower) / ma)
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {str(e)}")
            return None

    def calculate_rsi_with_divergence(self, period: int = 14) -> Tuple[Optional[float], Optional[bool], Optional[float]]:
        """
        Calculate RSI and detect divergence with enhanced validation
        Returns: (rsi_value, divergence_exists, divergence_strength)
        """
        try:
            if len(self.price_history) < period + 10:  # Need extra data for divergence
                return None, None, None

            prices = np.array(self.price_history)
            if not np.all(np.isfinite(prices)):
                logger.error("Invalid prices detected in price history")
                return None, None, None

            deltas = np.diff(prices)

            # Validate price movements
            if np.any(np.abs(deltas) > prices[:-1] * 0.5):  # More than 50% move
                logger.warning("Extremeprice movements detected, validating carefully")

            # Calculate gains and losses with validation
            gains = np.where(deltas >= 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)

            if len(gains) == 0 or len(losses) == 0:
                return 50.0, False, 0.0  # Neutral position on invalid data

            # Use exponential moving average for smoother RSI
            avg_gain = self._calculate_ema(gains, period)
            avg_loss = self._calculate_ema(losses, period)

            if avg_loss == 0:
                return 100.0, False, 0.0  # Strong uptrend

            if avg_gain is None or avg_loss is None:
                return None, None, None

            # Calculate RSI with validation
            rs = float(avg_gain) / float(avg_loss)
            rsi = 100.0 - (100.0 / (1.0 + rs))

            if not (0 <= rsi <= 100):
                logger.error(f"Invalid RSI value calculated: {rsi}")
                return None, None, None

            # Detect divergence with enhanced validation
            divergence = False
            divergence_strength = 0.0

            try:
                # Find recent price peaks and validate
                price_peaks = self._find_peaks_enhanced(prices[-20:])
                if len(price_peaks) >= 2:
                    # Create RSI array for peak detection
                    rsi_values = np.full(len(prices[-20:]), rsi)
                    rsi_peaks = self._find_peaks_enhanced(rsi_values)

                    if len(rsi_peaks) >= 2:
                        # Compare trends with proper validation
                        price_trend = float(prices[price_peaks[-1]]) - float(prices[price_peaks[-2]])
                        rsi_trend = float(rsi_values[rsi_peaks[-1]]) - float(rsi_values[rsi_peaks[-2]])

                        # Validate trend values
                        if np.isfinite(price_trend) and np.isfinite(rsi_trend):
                            # Divergence exists if trends are opposite
                            if np.sign(price_trend) != np.sign(rsi_trend):
                                divergence = True
                                # Calculate strength with bounds
                                if abs(price_trend) > 1e-10:  # Avoid division by zero
                                    divergence_strength = min(1.0, abs(rsi_trend / price_trend))
                                else:
                                    divergence_strength = 0.0

            except Exception as e:
                logger.error(f"Error in divergence calculation: {str(e)}")
                divergence = False
                divergence_strength = 0.0

            return float(rsi), divergence, float(divergence_strength)

        except Exception as e:
            logger.error(f"Error in RSI calculation: {str(e)}")
            return None, None, None

    def detect_market_regime(self) -> str:
        """
        Advanced market regime detection using multiple indicators
        Returns detailed market regime classification
        """
        try:
            if len(self.price_history) < 30:
                return "unknown"

            # Enhanced indicator calculations with proper error handling
            try:
                bb_width = self.calculate_bollinger_band_width()
                adx = self.calculate_adx()
                momentum = self.calculate_momentum()
                rsi, divergence_exists, _ = self.calculate_rsi_with_divergence()
            except Exception as e:
                logger.error(f"Error calculating indicators: {str(e)}")
                return "unknown"

            if any(x is None for x in [bb_width, adx, rsi]):
                return "unknown"

            # Market phase detection with multiple factors
            adx_check = float(adx if adx is not None else 0)
            bb_width_check = float(bb_width if bb_width is not None else 0)
            rsi_check = float(rsi if rsi is not None else 50)
            momentum_check = float(momentum if momentum is not None else 0)

            # Strong trend detection
            if adx_check > 30:
                if momentum_check > 0:
                    return "strong_uptrend_momentum"
                return "strong_downtrend_momentum"

            # Volatility regime detection
            if bb_width_check > 0.2:
                if divergence_exists:
                    return "volatile_reversal_imminent"
                return "volatile_trend_continuation"

            # Range-bound market detection
            if bb_width_check < 0.05:
                if rsi_check < 30 or rsi_check > 70:
                    return "coiled_spring"
                return "balanced_range"

            # Default state
            return "early_trend_formation"

        except Exception as e:
            logger.error(f"Error in market regime detection: {str(e)}")
            return "unknown"

    def analyze_trend(self, period: int = 20) -> dict:
        """
        Enhanced trend analysis with multiple timeframes and momentum indicators
        Returns detailed trend analysis including strength, momentum, and confidence
        """
        default_result = {
            "direction": "neutral",
            "strength": 0.0,
            "momentum": 0.0,
            "confidence": 0.0
        }

        try:
            if len(self.price_history) < period:
                return default_result

            # Convert to numpy array and get multiple timeframe data
            prices = np.array(self.price_history[-period:], dtype=float)
            if len(prices) < period:
                return default_result

            short_term = prices[-min(period//4, len(prices)):]
            medium_term = prices[-min(period//2, len(prices)):]

            # Calculate slopes for multiple timeframes with error checking
            try:
                slopes = {
                    "short": float(np.polyfit(np.arange(len(short_term)), short_term, 1)[0]),
                    "medium": float(np.polyfit(np.arange(len(medium_term)), medium_term, 1)[0]),
                    "long": float(np.polyfit(np.arange(len(prices)), prices, 1)[0])
                }

                # Calculate R-squared values for trend strength
                r_squared = {
                    "short": float(np.corrcoef(np.arange(len(short_term)), short_term)[0, 1] ** 2),
                    "medium": float(np.corrcoef(np.arange(len(medium_term)), medium_term)[0, 1] ** 2),
                    "long": float(np.corrcoef(np.arange(len(prices)), prices)[0, 1] ** 2)
                }
            except (ValueError, np.linalg.LinAlgError) as e:
                logger.error(f"Error calculating trend metrics: {str(e)}")
                return default_result

            # Calculate momentum using ROC
            momentum = (prices[-1] / prices[0] - 1.0) * 100

            # Calculate weighted trend score
            weights = {"short": 0.5, "medium": 0.3, "long": 0.2}
            trend_score = sum(slopes[tf] * weights[tf] for tf in ["short", "medium", "long"])
            strength_score = sum(r_squared[tf] * weights[tf] for tf in ["short", "medium", "long"])

            # Determine trend direction and confidence
            if abs(trend_score) < 0.0001:
                direction = "neutral"
                strength = 0.0
            else:
                direction = "up" if trend_score > 0 else "down"
                strength = min(1.0, abs(trend_score) * strength_score * 10)
                direction = f"strong_{direction}" if strength > 0.7 else f"weak_{direction}"

            # Calculate confidence based on agreement between timeframes
            timeframe_agreement = sum(1 for s in slopes.values() if (s > 0) == (trend_score > 0))
            confidence = (timeframe_agreement / len(slopes)) * strength_score

            return {
                "direction": direction,
                "strength": float(strength),
                "momentum": float(momentum),
                "confidence": float(confidence),
                "timeframes": {
                    tf: {
                        "slope": float(slopes[tf]),
                        "r_squared": float(r_squared[tf])
                    } for tf in ["short", "medium", "long"]
                }
            }

        except (TypeError, ValueError, IndexError) as e:
            logger.error(f"Error in trend analysis: {str(e)}")
            return {
                "direction": "neutral",
                "strength": 0.0,
                "momentum": 0.0,
                "confidence": 0.0
            }

    def detect_support_resistance(self) -> Tuple[float, float]:
        """Detect support and resistance levels using price action analysis"""
        if len(self.price_history) < 10:
            return min(self.price_history), max(self.price_history)

        prices = np.array(self.price_history)
        window = min(20, len(prices))

        # Calculate moving average as a baseline
        ma = np.mean(prices[-window:])

        # Find price clusters above and below MA
        above_ma = prices[prices > ma]
        below_ma = prices[prices < ma]

        # Use percentiles for support and resistance
        if len(above_ma) > 0 and len(below_ma) > 0:
            resistance = np.percentile(above_ma, 75)  # 75th percentile of higher prices
            support = np.percentile(below_ma, 25)    # 25th percentile of lower prices
        else:
            resistance = np.max(prices)
            support = np.min(prices)

        return float(support), float(resistance)

    def predict_price(self, forecast_periods: int = 1) -> Tuple[float, float, float]:
        """
        Predict future price using ensemble of models
        Returns: (predicted_price, lower_bound, upper_bound)
        """
        if len(self.price_history) < 30:
            current_price = self.price_history[-1]
            return current_price, current_price * 0.95, current_price * 1.05

        prices = np.array(self.price_history[-30:])

        # Calculate core metrics
        momentum = (prices[-1] - prices[-5]) / prices[-5] * 100
        trend = np.polyfit(range(len(prices)), prices, 1)[0]
        volatility = self.calculate_volatility()
        ma20 = np.mean(prices[-20:])

        # Generate base predictions
        base_prediction = prices[-1] * (1 + momentum / 100)
        trend_prediction = prices[-1] + trend
        ma_prediction = ma20

        # Get market regime and factor
        regime = self.detect_market_regime()
        regime_factors = {
            'strong_uptrend_momentum': 1.2,
            'strong_downtrend_momentum': 0.8,
            'volatile_reversal_imminent': 1.0,
            'coiled_spring': 1.3
        }
        regime_factor = regime_factors.get(regime, 1.0)

        # Adaptive weights based on market conditions
        pattern_strength = abs(momentum) / 100  # Simplified pattern strength
        if abs(momentum) > 2.0:  # Strong momentum
            weights = [0.5, 0.3, 0.2]  # More weight to momentum-based prediction
        elif pattern_strength > 0.7:  # Clear market structure
            weights = [0.3, 0.5, 0.2]  # More weight to trend
        else:
            weights = [0.33, 0.33, 0.34]  # Balanced weights

        # Weighted ensemble prediction
        predicted_price = (
            weights[0] * base_prediction +
            weights[1] * trend_prediction +
            weights[2] * ma_prediction
        ) * regime_factor

        # Dynamic confidence bounds based on market conditions
        volatility_factor = 1.0
        if regime.startswith('volatile'):
            volatility_factor = 1.5
        elif regime.startswith('strong'):
            volatility_factor = 0.8

        # Calculate confidence bounds using enhanced volatility metrics
        confidence_width = volatility * np.sqrt(forecast_periods) * volatility_factor
        lower_bound = predicted_price * (1 - confidence_width)
        upper_bound = predicted_price * (1 + confidence_width)

        # Apply rational bounds based on market microstructure
        current_price = prices[-1]
        max_deviation = 0.1 + volatility  # Adaptive maximum deviation
        lower_bound = max(current_price * (1 - max_deviation), lower_bound)
        upper_bound = min(current_price * (1 + max_deviation), upper_bound)

        return float(predicted_price), float(lower_bound), float(upper_bound)

    def calculate_volatility(self) -> float:
        """Calculate price volatility using standard deviation of returns"""
        try:
            if len(self.price_history) < 2:
                return 0.01

            prices = np.array(self.price_history)
            returns = np.diff(np.log(prices))
            return float(np.std(returns))

        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating volatility: {str(e)}")
            return 0.01  # Return default volatility on error

    def detect_arbitrage_opportunities(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Detect arbitrage opportunities for a specific token
        """
        try:
            # Get potential arbitrage paths
            paths = self.find_arbitrage_paths(symbol)
            if not paths:
                logger.debug(f"No viable arbitrage paths found for {symbol}")
                return []

            opportunities = []
            for path in paths:
                try:
                    if path['type'] == 'single_hop':
                        # Calculate expected profit after gas
                        price_diff = path['sell_price'] - path['buy_price']
                        total_gas_cost = (
                            path['gas_estimate']['buy'] +
                            path['gas_estimate']['sell']
                        )
                        expected_profit = price_diff - total_gas_cost

                        # Only include profitable opportunities
                        if expected_profit <= 0:
                            continue

                        opportunities.append({
                            'token': symbol,
                            'type': 'single_hop',
                            'buy_network': path['buy_network'],
                            'sell_network': path['sell_network'],
                            'buy_price': path['buy_price'],
                            'sell_price': path['sell_price'],
                            'expected_profit_usd': float(expected_profit),
                            'confidence_score': float(path['liquidity_confidence']),
                            'gas_cost_usd': float(total_gas_cost),
                            'risk_factors': {
                                'volatility': 1.0 - path['gas_estimate']['confidence'],
                                'liquidity': path['liquidity_confidence'],
                                'network_congestion': self.market_conditions.get('network_congestion', 0.0)
                            }
                        })
                    elif path['type'] == 'multi_hop':
                        # Multi-hop opportunities already have profit calculation
                        if path['profit_potential'] <= 0:
                            continue

                        opportunities.append({
                            'token': symbol,
                            'type': 'multi_hop',
                            'route': path['route'],
                            'expected_profit_usd': float(path['profit_potential']),
                            'confidence_score': float(path['liquidity_confidence']),
                            'gas_cost_usd': sum(
                                cost['optimal_gas_price']
                                for cost in path['gas_estimate'].values()
                            ),
                            'risk_factors': {
                                'volatility': 1.0 - min(
                                    step['confidence']
                                    for step in path['gas_estimate'].values()
                                ),
                                'liquidity': path['liquidity_confidence'],
                                'network_congestion': self.market_conditions.get('network_congestion', 0.0)
                            }
                        })
                except Exception as path_error:
                    logger.error(f"Error processing path for {symbol}: {str(path_error)}")
                    continue

            # Sort opportunities by expected profit and confidence
            opportunities.sort(
                key=lambda x: x['expected_profit_usd'] * x['confidence_score'],
                reverse=True
            )

            return opportunities

        except Exception as e:
            logger.error(f"Error detecting arbitrage opportunities for {symbol}: {str(e)}")
            return []

    def _calculate_profit_metrics(
        self,
        token: str,
        buy_network: str,
        sell_network: str,
        trade_size: float,
        gas_cost: float
    ) -> Dict[str, float]:
        """Calculate profit metrics including risk assessment"""
        try:
            # Get current market stats
            market_regime = self.detect_market_regime()
            volatility = self.calculate_volatility()

            # Base calculations
            buy_price = self.get_network_price(buy_network, token)
            sell_price = self.get_network_price(sell_network, token)

            if not buy_price or not sell_price:
                return {
                    'expected_profit': 0,
                    'profit_percentage': 0,
                    'risk_score': float('inf')
                }

            # Calculate gross profit
            gross_profit = (sell_price - buy_price) * trade_size

            # Account for slippage based on trade size and volatility
            slippage = self._estimate_slippage(trade_size, volatility)
            adjusted_profit = gross_profit * (1 - slippage)

            # Calculate net profit after gas
            net_profit = adjusted_profit - gas_cost

            # Calculate profit percentage
            profit_percentage = (net_profit / (buy_price * trade_size)) * 100

            # Risk scoring based on market conditions
            risk_factors = {
                'volatile_trend_continuation': 1.2,
                'volatile_reversal_imminent': 1.5,
                'strong_uptrend_momentum': 0.8,
                'strong_downtrend_momentum': 1.3,
                'balanced_range': 1.0
            }

            base_risk = risk_factors.get(market_regime, 1.0)

            # Adjust risk based on volatility and network factors
            network_risk = self.market_conditions.get('network_congestion', 0)
            volatility_risk = volatility * 2

            total_risk_score = base_risk * (1 + network_risk) * (1 + volatility_risk)

            return {
                'expected_profit': net_profit,
                'profit_percentage': profit_percentage,
                'risk_score': total_risk_score
            }

        except Exception as e:
            logger.error(f"Error calculating profit metrics: {str(e)}")
            return {
                'expected_profit': 0,
                'profit_percentage': 0,
                'risk_score': float('inf')
            }

    def _estimate_slippage(self, trade_size: float, volatility: float) -> float:
        """Estimate slippage based on trade size and market volatility"""
        try:
            # Base slippage increases with trade size
            base_slippage = 0.001 * (trade_size / 10000)  # 0.1% per 10k size

            # Increase slippage with volatility
            volatility_factor = 1 + (volatility * 2)

            # Add market impact
            market_impact = self.market_conditions.get('low_liquidity', 0) * 0.002

            return min(0.05, base_slippage * volatility_factor + market_impact)

        except Exception as e:
            logger.error(f"Error estimating slippage: {str(e)}")
            return 0.05  # Conservative 5% slippage on error

    def get_network_price(self, network: str, token: str) -> float:
        """Get the current price of a token on a specific network."""
        try:
            if network in self.network_price_history and \
               token in self.network_price_history[network] and \
               self.network_price_history[network][token]:
                return self.network_price_history[network][token][-1]
            else:
                return None  # Handle missing price data
        except Exception as e:
            logger.error(f"Error getting network price for {token} on {network}: {e}")
            return None

    def calculate_historical_price_trend(self, symbol: str, network: str, window: int = 20) -> Dict[str, float]:
        """
        Calculate historical price trends for arbitrage analysis
        Returns metrics about price stability and trends
        """
        try:
            if network not in self.network_price_history:
                return {'trend': 0.0, 'stability': 0.0, 'confidence': 0.0}

            if symbol not in self.network_price_history[network]:
                return {'trend': 0.0, 'stability': 0.0, 'confidence': 0.0}

            prices = self.network_price_history[network][symbol]
            if len(prices) < window:
                return {'trend': 0.0, 'stability': 0.0, 'confidence': 0.0}

            # Convert to numpy array and get recent prices
            recent_prices = np.array(prices[-window:])

            # Calculate trend using linear regression
            x = np.arange(len(recent_prices))
            slope, intercept = np.polyfit(x, recent_prices, 1)

            # Calculate R-squared for trend confidence
            trend_line = slope * x + intercept
            r_squared = 1 - (np.sum((recent_prices - trend_line) ** 2) /
                            np.sum((recent_prices - np.mean(recent_prices)) ** 2))

            # Calculate price stability
            returns = np.diff(np.log(recent_prices))
            stability = 1.0 / (1.0 + np.std(returns))

            return {
                'trend': float(slope),
                'stability': float(stability),
                'confidence': float(r_squared)
            }

        except Exception as e:
            logger.error(f"Error calculating price trend for {symbol} on {network}: {str(e)}")
            return {'trend': 0.0, 'stability': 0.0, 'confidence': 0.0}

    def estimate_slippage(self, symbol: str, network: str, trade_size: float) -> float:
        """
        Estimate slippage for a given trade size on a specific network
        Returns estimated slippage as a percentage
        """
        try:
            # Base slippage estimates based on network liquidity profiles
            base_slippage = {
                'ethereum': 0.001,    # 0.1% base slippage on Ethereum
                'arbitrum': 0.002,    # 0.2% base slippage on Arbitrum
                'polygon': 0.003,     # 0.3% base slippage on Polygon
                'avalanche': 0.002    # 0.2% base slippage on Avalanche
            }

            # Get recent price for the token
            if network not in self.network_price_history or \
               symbol not in self.network_price_history[network] or \
               not self.network_price_history[network][symbol]:
                return 0.01  # Return 1% slippage as safe default

            recent_price = self.network_price_history[network][symbol][-1]
            trade_value = trade_size * recent_price

            # Scale slippage based on trade size
            base = base_slippage.get(network, 0.005)  # 0.5% default base slippage

            # Exponential scaling based on trade value
            # Larger trades have higher slippage
            if trade_value < 10000:  # Small trades
                size_multiplier = 1.0
            elif trade_value < 50000:  # Medium trades
                size_multiplier = 1.5
            elif trade_value < 100000:  # Large trades
                size_multiplier = 2.0
            else:  # Very large trades
                size_multiplier = 3.0

            # Adjust for current market conditions
            market_regime = self.detect_market_regime()
            regime_multipliers = {
                'volatile_reversal_imminent': 2.0,
                'strong_uptrend_momentum': 1.2,
                'strong_downtrend_momentum': 1.5,
                'coiled_spring': 1.3,
                'balanced_range': 1.0
            }
            regime_multiplier = regime_multipliers.get(market_regime, 1.5)

            # Calculate final slippage estimate
            estimated_slippage = base * size_multiplier * regime_multiplier

            # Cap maximum slippage at 5%
            return min(0.05, float(estimated_slippage))

        except Exception as e:
            logger.error(f"Error estimating slippage for {symbol} on {network}: {str(e)}")
            return 0.01  # Return 1% slippage as safe default

    def calculate_cross_chain_liquidity(self, symbol: str) -> Dict[str, float]:
        """
        Calculate liquidity metrics across different networks
        Returns liquidity scores for each network
        """
        try:
            liquidity_scores = {}

            for network in ['ethereum', 'arbitrum', 'polygon', 'avalanche']:
                # Start with base liquidity score
                base_score = {
                    'ethereum': 1.0,    # Ethereum typically has highest liquidity
                    'arbitrum': 0.8,    # Arbitrum good butless than Ethereum
                    'polygon': 0.7,     # Polygon decent liquidity
                    'avalanche': 0.6    # Avalanche growing but still developing
                }.get(network, 0.5)

                # Analyze recent trading activity if available
                if network in self.network_price_history and \
                   symbol in self.network_price_history[network]:
                    recent_prices = self.network_price_history[network][symbol][-20:]

                    if len(recent_prices) >= 2:
                        # Calculate price stability
                        volatility = np.std(np.diff(np.log(recent_prices)))
                        stability_factor = 1.0 / (1.0 + volatility)

                        # Adjust base score by stability
                        adjusted_score = base_score * stability_factor

                        # Consider market regime
                        regime = self.detect_market_regime()
                        regime_factors = {
                            'volatile_reversal_imminent': 0.7,
                            'strong_uptrend_momentum': 1.2,
                            'strong_downtrend_momentum': 0.8,
                            'coiled_spring': 0.9,
                            'balanced_range': 1.0
                        }
                        regime_factor = regime_factors.get(regime, 0.8)

                        # Calculate final liquidity score
                        liquidity_scores[network] = float(adjusted_score * regime_factor)
                    else:
                        liquidity_scores[network] = float(base_score * 0.8)  # Reduce score due to limited data
                else:
                    liquidity_scores[network] = float(base_score * 0.6)  # Significantly reduce score due to no data

            return liquidity_scores

        except Exception as e:
            logger.error(f"Error calculating cross-chain liquidity for {symbol}: {str(e)}")
            return {network: 0.5 for network in ['ethereum', 'arbitrum', 'polygon', 'avalanche']}

    def optimize_arbitrage_path(self, symbol: str, amount: float) -> Dict[str, Any]:
        """
        Optimize arbitrage execution path considering all factors
        Returns optimal execution strategy with routing and timing
        """
        try:
            # Get current market conditions
            liquidity_scores = self.calculate_cross_chain_liquidity(symbol)
            market_regime = self.detect_market_regime()

            # Initialize strategy components
            strategy = {
                'symbol': symbol,
                'amount': amount,
                'routes': [],
                'estimated_profit': 0.0,
                'confidence': 0.0,
                'execution_timing': 'immediate'
            }

            # Get prices across networks
            prices = {}
            for network in ['ethereum', 'arbitrum', 'polygon', 'avalanche']:
                if network in self.network_price_history and \
                   symbol in self.network_price_history[network]:
                    prices[network] = self.network_price_history[network][symbol][-1]

            if len(prices) < 2:
                logger.warning(f"Insufficient price data for {symbol}")
                return strategy

            # Find profitable routes
            for buy_network, buy_price in prices.items():
                for sell_network, sell_price in prices.items():
                    if buy_network != sell_network:
                        # Calculate base profit
                        price_diff = sell_price - buy_price
                        gross_profit = price_diff * amount

                        # Estimate execution costs
                        buy_gas = self._estimate_gas_cost(buy_network, self.get_gas_price(buy_network))
                        sell_gas = self._estimate_gas_cost(sell_network, self.get_gas_price(sell_network))
                        total_cost = buy_gas + sell_gas

                        # Estimate slippage impact
                        buy_slippage = self.estimate_slippage(symbol, buy_network, amount)
                        sell_slippage = self.estimate_slippage(symbol, sell_network, amount)
                        slippage_cost = (buy_slippage + sell_slippage) * amount * buy_price

                        # Calculate net profit
                        net_profit = gross_profit - total_cost - slippage_cost

                        # Only consider profitable routes
                        if net_profit > 0:
                            # Calculate route confidence
                            buy_liquidity = liquidity_scores.get(buy_network, 0.5)
                            sell_liquidity = liquidity_scores.get(sell_network, 0.5)
                            route_confidence = min(buy_liquidity, sell_liquidity)

                            # Add profitable route
                            strategy['routes'].append({
                                'buy_network': buy_network,
                                'sell_network': sell_network,
                                'buy_price': float(buy_price),
                                'sell_price': float(sell_price),
                                'estimated_profit': float(net_profit),
                                'confidence': float(route_confidence),
                                'gas_cost': float(total_cost),
                                'slippage_cost': float(slippage_cost)
                            })

            # Sort routes by profit potential
            strategy['routes'].sort(key=lambda x: x['estimated_profit'] * x['confidence'], reverse=True)

            if strategy['routes']:
                strategy['estimated_profit'] = sum(route['estimated_profit'] for route in strategy['routes'])
                strategy['confidence'] = sum(route['confidence'] for route in strategy['routes']) / len(strategy['routes'])

                # Determine execution timing based on market regime
                if market_regime in ['volatile_reversal_imminent', 'strong_downtrend_momentum']:
                    strategy['execution_timing'] = 'delayed'  # Wait for better conditions
                elif market_regime in ['coiled_spring', 'strong_uptrend_momentum']:
                    strategy['execution_timing'] = 'immediate'  # Execute quickly
                else:
                    strategy['execution_timing'] = 'standard'  # Normal execution

            return strategy

        except Exception as e:
            logger.error(f"Error optimizing arbitrage path for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'amount': amount,
                'routes': [],
                'estimated_profit': 0.0,
                'confidence': 0.0,
                'execution_timing': 'immediate'
            }

    def get_gas_price(self, network: str) -> float:
        """Helper function to get current gas price for a network"""
        try:
            # Default gas prices (in gwei) if no data available
            default_prices = {
                'ethereum': 50.0,
                'arbitrum': 0.1,
                'polygon': 100.0,
                'avalanche': 25.0
            }

            # TODO: Implement real-time gasprice fetching
            return default_prices.get(network, 50.0)

        except Exception as e:
            logger.error(f"Error getting gas price for {network}: {str(e)}")
            return default_prices.get(network, 50.0)

    def _find_peaks_enhanced(self, data: np.ndarray, distance: int = 5) -> List[int]:
        """
        Enhanced peak detection with noise filtering
        """
        try:
            # Convert to numpy array if not already
            data = np.array(data, dtype=float)

            # Apply Savitzky-Golay filter to smooth the data
            window = min(21, len(data) - 1 if len(data) % 2 == 0 else len(data) - 2)
            if window >= 3:
                smoothed = self._savitzky_golay_filter(data, window, 3)
            else:
                smoothed = data

            # Find peaks with minimum peak distance
            peaks = []
            for i in range(1, len(smoothed) - 1):
                if i > 0 and i < len(smoothed) - 1:
                    if smoothed[i - 1] < smoothed[i] > smoothed[i + 1]:
                        # Check if it's the highest peak within the distance window
                        left = max(0, i - distance)
                        right = min(len(smoothed), i + distance + 1)
                        if smoothed[i] == max(smoothed[left:right]):
                            peaks.append(i)

            return peaks

        except Exception as e:
            logger.error(f"Error in peak detection: {str(e)}")
            return []

    def _savitzky_golay_filter(self, data: np.ndarray, window_size: int, order: int) -> np.ndarray:
        """
        Apply Savitzky-Golay filter for smooth peak detection
        """
        try:
            # Ensure odd window size
            if window_size % 2 == 0:
                window_size -= 1

            # Create design matrix
            half_window = window_size // 2
            x = np.arange(-half_window, half_window + 1)
            order_range = range(order + 1)
            b = np.mat([[k**i for i in order_range] for k in x])
            m = np.linalg.pinv(b).A[0]

            # Pad the signal at the ends with values taken from the signal
            firstvals = data[0] - np.abs(data[1:half_window+1][::-1] - data[0])
            lastvals = data[-1] + np.abs(data[-half_window-1:-1][::-1] - data[-1])
            data = np.concatenate((firstvals, data, lastvals))

            # Apply filter
            y = np.convolve(m[::-1], data, mode='valid')
            return y

        except Exception as e:
            logger.error(f"Error in Savitzky-Golay filtering: {str(e)}")
            return data

    def predict_price_ml(self, timeframe: str = '1h', steps_ahead: int = 12) -> Dict[str, Any]:
        """
        Machine learning-based price prediction using ensemble methods
        """
        try:
            if timeframe not in self.historical_data or len(self.historical_data[timeframe]) < 100:
                return {
                    'predictions': [],
                    'confidence': 0.0,
                    'error_margin': 0.0
                }

            # Prepare features
            prices = np.array(self.historical_data[timeframe][-100:])
            if len(prices) < 100:
                return {
                    'predictions': [],
                    'confidence': 0.0,
                    'error_margin': 0.0
                }

            # Technical indicators as features
            features = []
            for i in range(len(prices) - 20):
                window = prices[i:i+20]
                feature_set = {
                    'ma': np.mean(window),
                    'std': np.std(window),
                    'momentum': (window[-1] / window[0] - 1) * 100,
                    'rsi': self._calculate_rsi(window),
                    'price_change': (window[-1] - window[0]) / window[0]
                }
                features.append(list(feature_set.values()))

            features = np.array(features)
            targets = prices[21:]

            # Simple ensemble prediction (moving average + linear regression + momentum)
            predictions = []
            confidence_scores = []

            # Moving average prediction
            ma_pred = np.mean(prices[-20:])

            # Linear regression prediction
            x = np.arange(len(prices[-20:])).reshape(-1, 1)
            y = prices[-20:]
            lr_model = np.polyfit(x.flatten(), y, deg=1)
            lr_pred = np.polyval(lr_model, len(x))

            # Momentum-based prediction
            momentum = (prices[-1] / prices[-20] - 1)
            mom_pred = prices[-1] * (1 + momentum)

            # Ensemble prediction with weighted average
            weights = [0.4, 0.4, 0.2]  # Weights for MA, LR, and Momentum
            for step in range(steps_ahead):
                pred = (ma_pred * weights[0] + 
                       lr_pred * weights[1] + 
                       mom_pred * weights[2])

                # Calculate prediction confidence
                pred_std = np.std([ma_pred, lr_pred, mom_pred])
                confidence = 1 / (1 + pred_std / np.mean([ma_pred, lr_pred, mom_pred]))

                predictions.append(float(pred))
                confidence_scores.append(float(confidence))

                # Update predictions for next step
                ma_pred = np.mean(list(prices[-19:]) + predictions)
                lr_pred = np.polyval(lr_model, len(x) + step + 1)
                mom_pred = predictions[-1] * (1 + momentum)

            # Calculate error margin based on historical accuracy
            error_margin = np.std(predictions) * 1.96  # 95% confidence interval

            return {
                'predictions': predictions,
                'confidence': float(np.mean(confidence_scores)),
                'error_margin': float(error_margin),
                'timeframe': timeframe
            }

        except Exception as e:
            logger.error(f"Error in ML price prediction: {str(e)}")
            return {
                'predictions': [],
                'confidence': 0.0,
                'error_margin': 0.0
            }

    def _calculate_rsi(self, data: np.ndarray, period: int = 14) -> float:
        """Calculate RSI with enhanced error handling"""
        try:
            if len(data) < period:
                return 50.0  # Default value for insufficient data

            deltas = np.diff(data)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)

            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])

            if avg_loss == 0:
                return 100.0  # Avoid division by zero error

            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

            return float(rsi)
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
            return 50.0  # Return neutral RSI on error

    def _estimate_gas_cost(self, buy_network: str, sell_network: str) -> float:
        """Helper function to estimate gas cost"""
        try:
            buy_gas_units = self.optimize_gas_usage(buy_network)['estimated_gas_units']
            sell_gas_units = self.optimize_gas_usage(sell_network)['estimated_gas_units']
            buy_gas_price = self.get_gas_price(buy_network)
            sell_gas_price = self.get_gas_price(sell_network)
            return buy_gas_price * buy_gas_units + sell_gas_price * sell_gas_units
        except Exception as e:
            logger.error(f"Error estimating gas cost for {buy_network} and {sell_network}: {str(e)}")
            return 0.0
    
    def optimize_gas_usage(self, network: str) -> Dict[str, float]:
        """Optimize gas usage with MEV protection"""
        try:
            base_gas = self.get_gas_price(network)

            # Network-specific gas optimization
            network_factors = {
                'ethereum': {'base_multiplier': 1.1, 'priority_fee': 2.0},
                'arbitrum': {'base_multiplier': 1.05, 'priority_fee': 0.1},
                'polygon': {'base_multiplier': 1.2, 'priority_fee': 30.0},
                'avalanche': {'base_multiplier': 1.1, 'priority_fee': 2.0}
            }

            factors = network_factors.get(network, {'base_multiplier': 1.1, 'priority_fee': 1.0})

            # Calculate optimal gas price with MEV protection
            optimal_gas = base_gas * factors['base_multiplier']

            # Add priority fee for faster inclusion
            total_gas_price = optimal_gas + factors['priority_fee']

            # Estimate gas units based on network
            estimated_gas_units = {
                'ethereum': 150000,
                'arbitrum': 800000,
                'polygon': 250000,
                'avalanche': 200000
            }.get(network, 200000)

            # Add confidence score based on network congestion
            confidence = self._calculate_gas_confidence(network, total_gas_price)

            return {
                'optimal_gas_price': float(total_gas_price),
                'estimated_gas_units': float(estimated_gas_units),
                'confidence': float(confidence),
                'priority_fee': float(factors['priority_fee'])
            }

        except Exception as e:
            logger.error(f"Error optimizing gas usage for {network}: {str(e)}")
            return {
                'optimal_gas_price': 0.0,
                'estimated_gas_units': 0.0,
                'confidence': 0.0,
                'priority_fee': 0.0
            }

    def _calculate_gas_confidence(self, network: str, gas_price: float) -> float:
        """Calculate confidence score for gas price estimates"""
        try:
            # Get network congestion data
            congestion = self.market_conditions.get('network_congestion', 0)

            # Base confidence starts high and decreases with congestion
            base_confidence = 1.0 - (congestion * 0.5)

            # Adjust based on gas price volatility
            if network in self.network_price_history:
                recent_gas_prices = self.network_price_history[network].get('gas_prices', [])
                if recent_gas_prices:
                    volatility = np.std(recent_gas_prices) / np.mean(recent_gas_prices)
                    base_confidence *= (1.0 - min(volatility, 0.5))

            # Network-specific adjustments
            network_reliability = {
                'ethereum': 0.95,
                'arbitrum': 0.85,
                'polygon': 0.80,
                'avalanche': 0.85
            }.get(network, 0.75)

            final_confidence = base_confidence * network_reliability

            # Ensure confidence is bounded
            return float(max(0.1, min(0.95, final_confidence)))

        except Exception as e:
            logger.error(f"Error calculating gas confidence: {str(e)}")
            return 0.5

    def detect_arbitrage_opportunities(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Detect arbitrage opportunities for a specific token
        """
        try:
            # Get potential arbitrage paths
            paths = self.find_arbitrage_paths(symbol)
            if not paths:
                logger.debug(f"No viable arbitrage paths found for {symbol}")
                return []

            opportunities = []
            for path in paths:
                try:
                    if path['type'] == 'single_hop':
                        # Calculate expected profit after gas
                        price_diff = path['sell_price'] - path['buy_price']
                        total_gas_cost = (
                            path['gas_estimate']['buy'] +
                            path['gas_estimate']['sell']
                        )
                        expected_profit = price_diff - total_gas_cost

                        # Only include profitable opportunities
                        if expected_profit <= 0:
                            continue

                        opportunities.append({
                            'token': symbol,
                            'type': 'single_hop',
                            'buy_network': path['buy_network'],
                            'sell_network': path['sell_network'],
                            'buy_price': path['buy_price'],
                            'sell_price': path['sell_price'],
                            'expected_profit_usd': float(expected_profit),
                            'confidence_score': float(path['liquidity_confidence']),
                            'gas_cost_usd': float(total_gas_cost),
                            'risk_factors': {
                                'volatility': 1.0 - path['gas_estimate']['confidence'],
                                'liquidity': path['liquidity_confidence'],
                                'network_congestion': self.market_conditions.get('network_congestion', 0.0)
                            }
                        })
                    elif path['type'] == 'multi_hop':
                        # Multi-hop opportunities already have profit calculation
                        if path['profit_potential'] <= 0:
                            continue

                        opportunities.append({
                            'token': symbol,
                            'type': 'multi_hop',
                            'route': path['route'],
                            'expected_profit_usd': float(path['profit_potential']),
                            'confidence_score': float(path['liquidity_confidence']),
                            'gas_cost_usd': sum(
                                cost['optimal_gas_price']
                                for cost in path['gas_estimate'].values()
                            ),
                            'risk_factors': {
                                'volatility': 1.0 - min(
                                    step['confidence']
                                    for step in path['gas_estimate'].values()
                                ),
                                'liquidity': path['liquidity_confidence'],
                                'network_congestion': self.market_conditions.get('network_congestion', 0.0)
                            }
                        })
                except Exception as path_error:
                    logger.error(f"Error processing path for {symbol}: {str(path_error)}")
                    continue

            # Sort opportunities by expected profit and confidence
            opportunities.sort(
                key=lambda x: x['expected_profit_usd'] * x['confidence_score'],
                reverse=True
            )

            return opportunities

        except Exception as e:
            logger.error(f"Error detecting arbitrage opportunities for {symbol}: {str(e)}")
            return []

    def predict_price_ml(self, timeframe: str = '1h', steps_ahead: int = 12) -> Dict[str, Any]:
        """
        Machine learning-based price prediction using ensemble methods
        """
        try:
            if timeframe not in self.historical_data or len(self.historical_data[timeframe]) < 100:
                return {
                    'predictions': [],
                    'confidence': 0.0,
                    'error_margin': 0.0
                }

            # Prepare features
            prices = np.array(self.historical_data[timeframe][-100:])
            if len(prices) < 100:
                return {
                    'predictions': [],
                    'confidence': 0.0,
                    'error_margin': 0.0
                }

            # Technical indicators as features
            features = []
            for i in range(len(prices) - 20):
                window = prices[i:i+20]
                feature_set = {
                    'ma': np.mean(window),
                    'std': np.std(window),
                    'momentum': (window[-1] / window[0] - 1) * 100,
                    'rsi': self._calculate_rsi(window),
                    'price_change': (window[-1] - window[0]) / window[0]
                }
                features.append(list(feature_set.values()))

            features = np.array(features)
            targets = prices[21:]

            # Simple ensemble prediction (moving average + linear regression + momentum)
            predictions = []
            confidence_scores = []

            # Moving average prediction
            ma_pred = np.mean(prices[-20:])

            # Linear regression prediction
            x = np.arange(len(prices[-20:])).reshape(-1, 1)
            y = prices[-20:]
            lr_model = np.polyfit(x.flatten(), y, deg=1)
            lr_pred = np.polyval(lr_model, len(x))

            # Momentum-based prediction
            momentum = (prices[-1] / prices[-20] - 1)
            mom_pred = prices[-1] * (1 + momentum)

            # Ensemble prediction with weighted average
            weights = [0.4, 0.4, 0.2]  # Weights for MA, LR, and Momentum
            for step in range(steps_ahead):
                pred = (ma_pred * weights[0] + 
                       lr_pred * weights[1] + 
                       mom_pred * weights[2])

                # Calculate prediction confidence
                pred_std = np.std([ma_pred, lr_pred, mom_pred])
                confidence = 1 / (1 + pred_std / np.mean([ma_pred, lr_pred, mom_pred]))

                predictions.append(float(pred))
                confidence_scores.append(float(confidence))

                # Update predictions for next step
                ma_pred = np.mean(list(prices[-19:]) + predictions)
                lr_pred = np.polyval(lr_model, len(x) + step + 1)
                mom_pred = predictions[-1] * (1 + momentum)

            # Calculate error margin based on historical accuracy
            error_margin = np.std(predictions) * 1.96  # 95% confidence interval

            return {
                'predictions': predictions,
                'confidence': float(np.mean(confidence_scores)),
                'error_margin': float(error_margin),
                'timeframe': timeframe
            }

        except Exception as e:
            logger.error(f"Error in ML price prediction: {str(e)}")
            return {
                'predictions': [],
                'confidence': 0.0,
                'error_margin': 0.0
            }

    def _calculate_rsi(self, data: np.ndarray, period: int = 14) -> float:
        """Calculate RSI with enhanced error handling"""
        try:
            if len(data) < period:
                return 50.0  # Default value for insufficient data

            deltas = np.diff(data)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)

            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])

            if avg_loss == 0:
                return 100.0  # Avoid division by zero error

            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

            return float(rsi)
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
            return 50.0  # Return neutral RSI on error

    def _estimate_gas_cost(self, buy_network: str, sell_network: str) -> float:
        """Helper function to estimate gas cost"""
        try:
            buy_gas_units = self.optimize_gas_usage(buy_network)['estimated_gas_units']
            sell_gas_units = self.optimize_gas_usage(sell_network)['estimated_gas_units']
            buy_gas_price = self.get_gas_price(buy_network)
            sell_gas_price = self.get_gas_price(sell_network)
            return buy_gas_price * buy_gas_units + sell_gas_price * sell_gas_units
        except Exception as e:
            logger.error(f"Error estimating gas cost for {buy_network} and {sell_network}: {str(e)}")
            return 0.0

    def calculate_risk_metrics(self) -> Dict[str, float]:
        volatility = self.calculate_volatility()
        max_drawdown = self.calculate_max_drawdown()
        sharpe_ratio = self.calculate_sharpe_ratio()
        return {
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio
        }

    def calculate_max_drawdown(self) -> float:
        peak = self.price_history[0]
        max_drawdown = 0.0
        for price in self.price_history:
            if price > peak:
                peak = price
            drawdown = (peak - price) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        return max_drawdown

    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.01) -> float:
        returns = np.diff(self.price_history) / self.price_history[:-1]
        excess_returns = returns - risk_free_rate / 252
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)

    def predict_price_ml(self, steps_ahead: int = 1) -> float:
        if len(self.price_history) < 30:
            return self.price_history[-1]  # Return last price if not enough data

        prices = np.array(self.price_history[-30:]).reshape(-1, 1)
        model = LinearRegression()
        model.fit(np.arange(len(prices)).reshape(-1, 1), prices)
        prediction = model.predict(np.array([[len(prices) + steps_ahead]]))
        return float(prediction[0])