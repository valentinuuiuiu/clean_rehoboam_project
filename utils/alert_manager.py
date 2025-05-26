"""Alert manager for WebSocket system monitoring."""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import smtplib
import json
from email.mime.text import MIMEText
from prometheus_client import Counter, Gauge

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class AlertThreshold:
    warning: float
    error: float
    critical: float
    duration: int  # seconds the condition must persist
    cooldown: int  # seconds before re-alerting

@dataclass
class Alert:
    id: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    metric: str
    value: float
    threshold: float
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class AlertManager:
    """Manage system alerts and notifications."""
    
    def __init__(self):
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.thresholds = {
            'connection_count': AlertThreshold(
                warning=100,
                error=200,
                critical=300,
                duration=60,
                cooldown=300
            ),
            'error_rate': AlertThreshold(
                warning=5,
                error=10,
                critical=20,
                duration=300,
                cooldown=900
            ),
            'latency': AlertThreshold(
                warning=200,  # ms
                error=500,
                critical=1000,
                duration=120,
                cooldown=600
            ),
            'message_rate': AlertThreshold(
                warning=1000,
                error=2000,
                critical=3000,
                duration=60,
                cooldown=300
            )
        }
        
        # Prometheus metrics
        self.alert_counter = Counter('ws_alerts_total', 'Number of alerts generated', ['severity'])
        self.active_alerts_gauge = Gauge('ws_active_alerts', 'Number of active alerts', ['severity'])
        
        # Alert channels
        self.notification_channels = {
            AlertSeverity.INFO: self._notify_slack,
            AlertSeverity.WARNING: self._notify_slack,
            AlertSeverity.ERROR: self._notify_all,
            AlertSeverity.CRITICAL: self._notify_all
        }

    async def start_monitoring(self, metrics_callback):
        """Start continuous system monitoring."""
        while True:
            try:
                metrics = await metrics_callback()
                await self._check_thresholds(metrics)
                await asyncio.sleep(15)  # Check every 15 seconds
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(5)

    async def _check_thresholds(self, metrics: Dict[str, Any]):
        """Check metrics against thresholds."""
        for metric, value in metrics.items():
            if metric in self.thresholds:
                threshold = self.thresholds[metric]
                
                # Check each severity level
                if value >= threshold.critical:
                    await self._create_alert(metric, value, AlertSeverity.CRITICAL, threshold.critical)
                elif value >= threshold.error:
                    await self._create_alert(metric, value, AlertSeverity.ERROR, threshold.error)
                elif value >= threshold.warning:
                    await self._create_alert(metric, value, AlertSeverity.WARNING, threshold.warning)
                else:
                    await self._resolve_alert(metric)

    async def _create_alert(self, metric: str, value: float, severity: AlertSeverity, threshold: float):
        """Create new alert if conditions are met."""
        alert_id = f"{metric}_{severity.value}"
        
        # Check if alert already exists
        if alert_id in self.active_alerts:
            return
            
        # Check cooldown period
        recent_alert = next(
            (alert for alert in reversed(self.alert_history)
             if alert.id == alert_id and 
             datetime.now() - alert.timestamp < timedelta(seconds=self.thresholds[metric].cooldown)),
            None
        )
        if recent_alert:
            return

        # Create new alert
        alert = Alert(
            id=alert_id,
            severity=severity,
            message=f"{metric} exceeded {severity.value} threshold: {value} >= {threshold}",
            timestamp=datetime.now(),
            metric=metric,
            value=value,
            threshold=threshold
        )
        
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Update metrics
        self.alert_counter.labels(severity=severity.value).inc()
        self.active_alerts_gauge.labels(severity=severity.value).inc()
        
        # Send notifications
        await self._send_notifications(alert)

    async def _resolve_alert(self, metric: str):
        """Resolve active alert for metric."""
        for severity in AlertSeverity:
            alert_id = f"{metric}_{severity.value}"
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                alert.resolved_at = datetime.now()
                
                # Update metrics
                self.active_alerts_gauge.labels(severity=severity.value).dec()
                
                # Remove from active alerts
                del self.active_alerts[alert_id]
                
                # Send resolution notification
                await self._send_resolution_notification(alert)

    async def _send_notifications(self, alert: Alert):
        """Send notifications through configured channels."""
        notification_func = self.notification_channels.get(alert.severity)
        if notification_func:
            await notification_func(alert)

    async def _send_resolution_notification(self, alert: Alert):
        """Send alert resolution notification."""
        resolution_message = (
            f"RESOLVED: {alert.message}\n"
            f"Duration: {alert.resolved_at - alert.timestamp}"
        )
        await self._notify_slack({
            'text': resolution_message,
            'color': 'good'
        })

    async def _notify_slack(self, alert: Alert):
        """Send notification to Slack."""
        try:
            webhook_url = os.getenv('SLACK_WEBHOOK_URL')
            if not webhook_url:
                return
                
            color_map = {
                AlertSeverity.INFO: '#2196f3',
                AlertSeverity.WARNING: '#ffc107',
                AlertSeverity.ERROR: '#f44336',
                AlertSeverity.CRITICAL: '#d32f2f'
            }
            
            payload = {
                'attachments': [{
                    'color': color_map[alert.severity],
                    'title': f'{alert.severity.value.upper()}: {alert.metric}',
                    'text': alert.message,
                    'fields': [
                        {
                            'title': 'Value',
                            'value': str(alert.value),
                            'short': True
                        },
                        {
                            'title': 'Threshold',
                            'value': str(alert.threshold),
                            'short': True
                        }
                    ],
                    'ts': int(alert.timestamp.timestamp())
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status != 200:
                        logger.error(f"Error sending Slack notification: {await response.text()}")
                        
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {str(e)}")

    async def _notify_email(self, alert: Alert):
        """Send notification via email."""
        try:
            smtp_host = os.getenv('SMTP_HOST')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER')
            smtp_pass = os.getenv('SMTP_PASS')
            recipient = os.getenv('ALERT_EMAIL')
            
            if not all([smtp_host, smtp_user, smtp_pass, recipient]):
                return
                
            subject = f"{alert.severity.value.upper()} Alert: {alert.metric}"
            body = (
                f"Alert Details:\n"
                f"Metric: {alert.metric}\n"
                f"Value: {alert.value}\n"
                f"Threshold: {alert.threshold}\n"
                f"Timestamp: {alert.timestamp.isoformat()}\n\n"
                f"Message: {alert.message}"
            )
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = smtp_user
            msg['To'] = recipient
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
                
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")

    async def _notify_all(self, alert: Alert):
        """Send notification through all available channels."""
        await asyncio.gather(
            self._notify_slack(alert),
            self._notify_email(alert)
        )

    def get_active_alerts(self) -> List[Alert]:
        """Get list of active alerts."""
        return list(self.active_alerts.values())

    def get_alert_history(self, 
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None,
                         severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get filtered alert history."""
        alerts = self.alert_history
        
        if start_time:
            alerts = [a for a in alerts if a.timestamp >= start_time]
        if end_time:
            alerts = [a for a in alerts if a.timestamp <= end_time]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
            
        return alerts

    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics."""
        return {
            'total_alerts': len(self.alert_history),
            'active_alerts': len(self.active_alerts),
            'by_severity': {
                severity.value: len([a for a in self.alert_history if a.severity == severity])
                for severity in AlertSeverity
            },
            'resolution_time_avg': self._calculate_avg_resolution_time()
        }

    def _calculate_avg_resolution_time(self) -> float:
        """Calculate average alert resolution time in seconds."""
        resolved_alerts = [a for a in self.alert_history if a.resolved and a.resolved_at]
        if not resolved_alerts:
            return 0.0
            
        total_time = sum(
            (a.resolved_at - a.timestamp).total_seconds()
            for a in resolved_alerts
        )
        return total_time / len(resolved_alerts)