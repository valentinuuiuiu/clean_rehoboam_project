"""
Enhanced safety checks for trading operations with advanced risk management.
"""
import time
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SafetyChecks:
    """Advanced safety checks for trading operations with quantum-inspired risk management."""
    
    def __init__(self):
        # Circuit breaker state
        self.last_trade_timestamp = 0
        self.trade_attempt_count = 0
        self.failed_attempts = 0
        self.max_consecutive_failures = 3
        self.last_error = None
        
        # State flags
        self.high_volatility_flag = False
        self.circuit_breaker_active = False
        self.market_paused = False
        
        # Risk thresholds
        self.max_slippage = 0.02  # 2% maximum slippage
        self.max_position_size = 0.10  # 10% of portfolio
        self.min_liquidity_ratio = 5.0  # Trade size should be at most 1/5 of available liquidity
        
        # Market state tracking
        self.historical_prices = []
        self.historical_volumes = []
        self.price_moving_average = None
        self.volume_moving_average = None
        self.last_volatility = None
        
        logger.info("Safety checks initialized with enhanced risk management")
    
    def check_circuit_breaker(self, current_price: float = None, last_price: float = None,
                             current_volume: float = None, avg_volume: float = None,
                             volatility: float = None) -> bool:
        """
        Check if the circuit breaker should prevent a trade.
        
        Args:
            current_price: Current asset price
            last_price: Previous asset price (used for volatility check)
            current_volume: Current trading volume
            avg_volume: Average trading volume (for liquidity check)
            volatility: Current market volatility measure
        
        Returns:
            bool: True if trading is allowed, False if circuit breaker is active
        """
        now = time.time()
        cooldown_period = 300  # 5 minutes between trades
        
        # Check if enough time has passed since last trade
        if now - self.last_trade_timestamp < cooldown_period:
            remaining = cooldown_period - (now - self.last_trade_timestamp)
            logger.warning(f"Circuit breaker active: {remaining:.1f} seconds remaining")
            self.circuit_breaker_active = True
            self.last_error = f"Circuit breaker active: {remaining:.1f} seconds remaining"
            return False
        
        # Check for too many consecutive failures
        if self.failed_attempts >= self.max_consecutive_failures:
            logger.warning(f"Circuit breaker active: Too many failed attempts ({self.failed_attempts})")
            self.circuit_breaker_active = True
            self.last_error = f"Circuit breaker active: Too many failed attempts ({self.failed_attempts})"
            return False
        
        # Check for high volatility if data provided
        if (current_price is not None and last_price is not None and 
            abs(current_price - last_price) / last_price > 0.05):  # 5% price movement
            logger.warning("Circuit breaker active: High volatility detected")
            self.high_volatility_flag = True
            self.circuit_breaker_active = True
            self.last_error = "Circuit breaker active: High volatility detected"
            return False
        
        # Check for abnormal volume if data provided
        if (current_volume is not None and avg_volume is not None and 
            current_volume > avg_volume * 3):  # 3x normal volume
            logger.warning("Circuit breaker active: Abnormal volume detected")
            self.circuit_breaker_active = True
            self.last_error = "Circuit breaker active: Abnormal volume detected"
            return False
        
        # All checks passed
        self.circuit_breaker_active = False
        return True
    
    def check_slippage(self, expected_price: float, execution_price: float) -> bool:
        """
        Check if slippage is within acceptable limits.
        
        Args:
            expected_price: Expected execution price
            execution_price: Actual execution price
            
        Returns:
            bool: True if slippage is acceptable, False otherwise
        """
        if expected_price <= 0 or execution_price <= 0:
            self.last_error = "Invalid price values for slippage check"
            return False
        
        slippage = abs(execution_price - expected_price) / expected_price
        
        if slippage > self.max_slippage:
            logger.warning(f"Slippage check failed: {slippage:.2%} exceeds maximum allowed {self.max_slippage:.2%}")
            self.last_error = f"Slippage {slippage:.2%} exceeds maximum allowed {self.max_slippage:.2%}"
            return False
        
        return True
    
    def check_position_size(self, position_size: float, portfolio_value: float) -> bool:
        """
        Check if position size is within acceptable limits.
        
        Args:
            position_size: Size of the position in value terms
            portfolio_value: Total portfolio value
            
        Returns:
            bool: True if position size is acceptable, False otherwise
        """
        if portfolio_value <= 0:
            self.last_error = "Invalid portfolio value"
            return False
        
        position_ratio = position_size / portfolio_value
        
        if position_ratio > self.max_position_size:
            logger.warning(f"Position size check failed: {position_ratio:.2%} of portfolio exceeds maximum allowed {self.max_position_size:.2%}")
            self.last_error = f"Position size {position_ratio:.2%} exceeds maximum allowed {self.max_position_size:.2%}"
            return False
        
        return True
    
    def check_gas_price(self, current_gas_price: int, max_gas_price: int) -> bool:
        """
        Check if gas price is within acceptable limits.
        
        Args:
            current_gas_price: Current gas price in wei
            max_gas_price: Maximum acceptable gas price in wei
            
        Returns:
            bool: True if gas price is acceptable, False otherwise
        """
        if current_gas_price > max_gas_price:
            logger.warning(f"Gas price check failed: {current_gas_price} wei exceeds maximum {max_gas_price} wei")
            self.last_error = f"Gas price too high: {current_gas_price / 1e9:.1f} gwei > {max_gas_price / 1e9:.1f} gwei"
            return False
        
        return True
    
    def check_liquidity(self, trade_size: float, market_volume: float) -> bool:
        """
        Check if there is sufficient liquidity for the trade.
        
        Args:
            trade_size: Size of the trade in tokens
            market_volume: Current market volume in tokens
            
        Returns:
            bool: True if liquidity is sufficient, False otherwise
        """
        if market_volume <= 0:
            self.last_error = "Invalid market volume"
            return False
        
        liquidity_ratio = market_volume / trade_size
        
        if liquidity_ratio < self.min_liquidity_ratio:
            logger.warning(f"Liquidity check failed: ratio {liquidity_ratio:.2f} below minimum {self.min_liquidity_ratio:.2f}")
            self.last_error = f"Insufficient liquidity: trade size is too large relative to market volume"
            return False
        
        return True
    
    def record_market_data(self, price: float, volume: float, window_size: int = 20):
        """
        Record market data for historical analysis.
        
        Args:
            price: Current price
            volume: Current volume
            window_size: Number of historical data points to keep
        """
        # Add new data
        self.historical_prices.append(price)
        self.historical_volumes.append(volume)
        
        # Trim data to window size
        if len(self.historical_prices) > window_size:
            self.historical_prices = self.historical_prices[-window_size:]
            self.historical_volumes = self.historical_volumes[-window_size:]
        
        # Update moving averages
        if len(self.historical_prices) > 0:
            self.price_moving_average = sum(self.historical_prices) / len(self.historical_prices)
            self.volume_moving_average = sum(self.historical_volumes) / len(self.historical_volumes)
        
        # Calculate volatility if enough data
        if len(self.historical_prices) > 1:
            price_changes = [abs(self.historical_prices[i] - self.historical_prices[i-1]) / self.historical_prices[i-1]
                          for i in range(1, len(self.historical_prices))]
            self.last_volatility = sum(price_changes) / len(price_changes)
    
    def increment_failed_attempts(self):
        """Increment the count of consecutive failed attempts."""
        self.failed_attempts += 1
        logger.info(f"Incremented failed attempts to {self.failed_attempts}")
    
    def record_successful_trade(self):
        """Record that a trade was successful and reset failure counters."""
        self.last_trade_timestamp = time.time()
        self.trade_attempt_count += 1
        self.failed_attempts = 0
        logger.info(f"Recorded successful trade #{self.trade_attempt_count}")
    
    def is_high_volatility(self) -> bool:
        """Check if market is currently in a high volatility state."""
        return self.high_volatility_flag
    
    def set_high_volatility(self, state: bool):
        """Set the high volatility flag."""
        self.high_volatility_flag = state
        logger.info(f"High volatility flag set to {state}")
    
    def is_circuit_breaker_active(self) -> bool:
        """Check if circuit breaker is currently active."""
        return self.circuit_breaker_active
    
    def reset_circuit_breaker(self):
        """Reset the circuit breaker state."""
        self.circuit_breaker_active = False
        self.failed_attempts = 0
        self.last_error = None
        logger.info("Circuit breaker reset")
    
    def get_volatility(self) -> Optional[float]:
        """Get the last calculated volatility."""
        return self.last_volatility
    
    def get_price_deviation(self) -> Optional[float]:
        """Get the deviation of current price from moving average."""
        if not self.historical_prices or not self.price_moving_average:
            return None
        
        current_price = self.historical_prices[-1]
        return (current_price - self.price_moving_average) / self.price_moving_average
    
    def get_volume_deviation(self) -> Optional[float]:
        """Get the deviation of current volume from moving average."""
        if not self.historical_volumes or not self.volume_moving_average:
            return None
        
        current_volume = self.historical_volumes[-1]
        return (current_volume - self.volume_moving_average) / self.volume_moving_average
    
    def summarize_state(self) -> Dict[str, Any]:
        """Get a summary of the current safety state."""
        return {
            "circuit_breaker_active": self.circuit_breaker_active,
            "high_volatility": self.high_volatility_flag,
            "failed_attempts": self.failed_attempts,
            "successful_trades": self.trade_attempt_count,
            "last_trade_timestamp": self.last_trade_timestamp,
            "last_error": self.last_error,
            "price_moving_average": self.price_moving_average,
            "volume_moving_average": self.volume_moving_average,
            "last_volatility": self.last_volatility
        }
