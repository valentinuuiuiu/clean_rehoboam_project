"""System monitoring and alerting configuration."""
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging

@dataclass
class AlertThreshold:
    warning_level: float
    critical_level: float
    cooldown_period: int  # seconds

@dataclass
class MonitoringConfig:
    # Price movement thresholds
    price_change_thresholds: Dict[str, AlertThreshold] = None
    
    # Trading thresholds
    max_daily_trades: int = 50
    max_position_size_usd: float = 10000
    max_total_exposure_usd: float = 50000
    
    # Circuit breaker conditions
    circuit_breaker_conditions: Dict[str, AlertThreshold] = None
    
    def __post_init__(self):
        if self.price_change_thresholds is None:
            self.price_change_thresholds = {
                'default': AlertThreshold(0.05, 0.10, 300),  # 5% warning, 10% critical
                'volatile_assets': AlertThreshold(0.10, 0.20, 300),  # More lenient for volatile assets
                'stablecoins': AlertThreshold(0.01, 0.02, 300),  # Stricter for stablecoins
            }
            
        if self.circuit_breaker_conditions is None:
            self.circuit_breaker_conditions = {
                'price_impact': AlertThreshold(0.03, 0.05, 600),  # Price impact thresholds
                'slippage': AlertThreshold(0.02, 0.04, 600),      # Slippage thresholds
                'volatility': AlertThreshold(0.5, 0.8, 900),      # Volatility index thresholds
            }

    # Performance monitoring
    min_profit_threshold: float = -0.02  # -2% threshold for individual trades
    max_drawdown_threshold: float = -0.10  # -10% max drawdown
    
    # System health
    max_api_error_rate: float = 0.10  # 10% error rate threshold
    max_response_time_ms: int = 5000  # 5 second response time threshold

    def get_price_threshold(self, asset: str) -> AlertThreshold:
        """Get price threshold for specific asset."""
        if asset.endswith('USD'):
            return self.price_change_thresholds['stablecoins']
        elif asset in ['BTC', 'ETH', 'SOL']:
            return self.price_change_thresholds['volatile_assets']
        return self.price_change_thresholds['default']

logging.getLogger(__name__).info("Monitoring configuration loaded")