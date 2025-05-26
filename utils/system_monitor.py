"""System monitoring and alerting service."""
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
from .monitoring_config import MonitoringConfig, AlertThreshold

logger = logging.getLogger(__name__)

@dataclass
class Alert:
    timestamp: datetime
    level: str  # 'warning' or 'critical'
    category: str
    message: str
    asset: Optional[str] = None
    value: Optional[float] = None

class SystemMonitor:
    def __init__(self):
        self.config = MonitoringConfig()
        self.alerts: List[Alert] = []
        self.price_history: Dict[str, List[Tuple[datetime, float]]] = {}
        self.trade_history: List[Dict] = []
        self.api_response_times: List[Tuple[datetime, float]] = []
        self.api_errors: List[Tuple[datetime, str]] = []
        self.last_alert_time: Dict[str, datetime] = {}

    def monitor_price_change(self, asset: str, current_price: float) -> Optional[Alert]:
        """Monitor price changes and generate alerts if thresholds are exceeded."""
        if asset not in self.price_history:
            self.price_history[asset] = []
        
        now = datetime.now()
        self.price_history[asset].append((now, current_price))
        
        # Keep only last 24 hours of data
        cutoff = now - timedelta(hours=24)
        self.price_history[asset] = [x for x in self.price_history[asset] if x[0] > cutoff]
        
        if len(self.price_history[asset]) < 2:
            return None
            
        # Calculate price change
        previous_price = self.price_history[asset][-2][1]
        price_change = abs(current_price - previous_price) / previous_price
        
        threshold = self.config.get_price_threshold(asset)
        alert_key = f"price_change_{asset}"
        
        if self._can_alert(alert_key, threshold.cooldown_period):
            if price_change >= threshold.critical_level:
                alert = Alert(
                    timestamp=now,
                    level='critical',
                    category='price_change',
                    message=f"Critical price change detected for {asset}: {price_change:.2%}",
                    asset=asset,
                    value=price_change
                )
                self._record_alert(alert_key, alert)
                return alert
            elif price_change >= threshold.warning_level:
                alert = Alert(
                    timestamp=now,
                    level='warning',
                    category='price_change',
                    message=f"Significant price change detected for {asset}: {price_change:.2%}",
                    asset=asset,
                    value=price_change
                )
                self._record_alert(alert_key, alert)
                return alert
        
        return None

    def monitor_trading_activity(self, trade: Dict) -> Optional[Alert]:
        """Monitor trading activity for suspicious patterns."""
        now = datetime.now()
        self.trade_history.append({**trade, 'timestamp': now})
        
        # Keep only last 24 hours of trades
        cutoff = now - timedelta(hours=24)
        self.trade_history = [t for t in self.trade_history if t['timestamp'] > cutoff]
        
        # Check daily trade count
        if len(self.trade_history) > self.config.max_daily_trades:
            return Alert(
                timestamp=now,
                level='critical',
                category='trading_activity',
                message=f"Daily trade limit exceeded: {len(self.trade_history)} trades",
                value=len(self.trade_history)
            )
        
        # Check position size
        if trade.get('value_usd', 0) > self.config.max_position_size_usd:
            return Alert(
                timestamp=now,
                level='critical',
                category='position_size',
                message=f"Position size exceeds limit: ${trade['value_usd']:,.2f}",
                asset=trade.get('asset'),
                value=trade['value_usd']
            )
            
        return None

    def monitor_system_health(self, api_response_time_ms: float, error: Optional[str] = None) -> Optional[Alert]:
        """Monitor system health metrics."""
        now = datetime.now()
        self.api_response_times.append((now, api_response_time_ms))
        if error:
            self.api_errors.append((now, error))
            
        # Keep only last hour of data
        cutoff = now - timedelta(hours=1)
        self.api_response_times = [x for x in self.api_response_times if x[0] > cutoff]
        self.api_errors = [x for x in self.api_errors if x[0] > cutoff]
        
        alerts = []
        
        # Check API response times
        if api_response_time_ms > self.config.max_response_time_ms:
            alerts.append(Alert(
                timestamp=now,
                level='warning',
                category='system_health',
                message=f"High API response time: {api_response_time_ms}ms",
                value=api_response_time_ms
            ))
            
        # Check error rate
        total_requests = len(self.api_response_times)
        if total_requests > 0:
            error_rate = len(self.api_errors) / total_requests
            if error_rate > self.config.max_api_error_rate:
                alerts.append(Alert(
                    timestamp=now,
                    level='critical',
                    category='system_health',
                    message=f"High API error rate: {error_rate:.1%}",
                    value=error_rate
                ))
                
        return alerts[0] if alerts else None

    def _can_alert(self, key: str, cooldown_period: int) -> bool:
        """Check if enough time has passed since last alert."""
        now = datetime.now()
        if key not in self.last_alert_time:
            return True
        
        time_since_last = (now - self.last_alert_time[key]).total_seconds()
        return time_since_last >= cooldown_period

    def _record_alert(self, key: str, alert: Alert):
        """Record an alert and update last alert time."""
        self.alerts.append(alert)
        self.last_alert_time[key] = alert.timestamp
        logger.warning(f"Alert generated: {alert.message}")

    def get_system_status(self) -> Dict:
        """Get overall system status summary."""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)
        
        return {
            'alerts': {
                'last_hour': len([a for a in self.alerts if a.timestamp > hour_ago]),
                'last_day': len([a for a in self.alerts if a.timestamp > day_ago])
            },
            'trades': {
                'count_24h': len(self.trade_history),
                'volume_24h': sum(t.get('value_usd', 0) for t in self.trade_history)
            },
            'system_health': {
                'avg_response_time': np.mean([t[1] for t in self.api_response_times]) if self.api_response_times else 0,
                'error_rate': len(self.api_errors) / len(self.api_response_times) if self.api_response_times else 0
            }
        }