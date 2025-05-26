"""Analytics service for tracking user preferences and their impact on trading performance."""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import pandas as pd
import numpy as np
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class PreferenceMetric:
    """Metric for tracking preference performance."""
    timestamp: datetime
    user_id: str
    category: str
    key: str
    value: Any
    performance_impact: float
    confidence: float

class PreferenceAnalytics:
    """Track and analyze the impact of user preferences on trading performance."""
    
    def __init__(self):
        self.metrics: List[PreferenceMetric] = []
        self.performance_cache = defaultdict(list)
        self.correlation_cache = {}
        self.update_interval = 3600  # 1 hour

    async def track_preference_impact(
        self,
        user_id: str,
        preferences: Dict[str, Any],
        performance_data: Dict[str, Any]
    ):
        """Track the impact of preferences on trading performance."""
        try:
            timestamp = datetime.now()
            
            # Calculate baseline performance
            baseline = self._calculate_baseline_performance(performance_data)
            
            # Track impact of each preference
            for category, settings in preferences.items():
                for key, value in settings.items():
                    impact = self._calculate_performance_impact(
                        category,
                        key,
                        value,
                        performance_data,
                        baseline
                    )
                    
                    confidence = self._calculate_confidence(
                        category,
                        key,
                        value,
                        performance_data
                    )
                    
                    metric = PreferenceMetric(
                        timestamp=timestamp,
                        user_id=user_id,
                        category=category,
                        key=key,
                        value=value,
                        performance_impact=impact,
                        confidence=confidence
                    )
                    
                    self.metrics.append(metric)
                    
            # Update correlation analysis
            await self._update_correlations()
            
        except Exception as e:
            logger.error(f"Error tracking preference impact: {str(e)}")

    def get_preference_insights(
        self,
        user_id: str,
        timeframe: str = '7d'
    ) -> Dict[str, Any]:
        """Get insights about preference impact on performance."""
        try:
            # Filter metrics by timeframe
            start_time = self._parse_timeframe(timeframe)
            relevant_metrics = [
                m for m in self.metrics
                if m.timestamp >= start_time and m.user_id == user_id
            ]
            
            if not relevant_metrics:
                return {'error': 'No metrics available for analysis'}
            
            # Analyze impact by category
            category_impact = self._analyze_category_impact(relevant_metrics)
            
            # Get top performing settings
            top_settings = self._get_top_performing_settings(relevant_metrics)
            
            # Get improvement suggestions
            suggestions = self._generate_suggestions(
                user_id,
                relevant_metrics,
                category_impact
            )
            
            return {
                'category_impact': category_impact,
                'top_settings': top_settings,
                'suggestions': suggestions,
                'confidence': self._calculate_overall_confidence(relevant_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error getting preference insights: {str(e)}")
            return {'error': str(e)}

    def _calculate_baseline_performance(
        self,
        performance_data: Dict[str, Any]
    ) -> float:
        """Calculate baseline performance metrics."""
        try:
            # Extract relevant metrics
            roi = performance_data.get('roi', 0)
            sharpe = performance_data.get('sharpe_ratio', 0)
            win_rate = performance_data.get('win_rate', 0)
            
            # Weighted combination of metrics
            weights = {'roi': 0.4, 'sharpe': 0.3, 'win_rate': 0.3}
            
            # Normalize and combine
            normalized_roi = np.clip(roi / 0.1, -1, 1)  # Normalize to [-1, 1]
            normalized_sharpe = np.clip(sharpe / 2, -1, 1)
            normalized_win_rate = (win_rate - 0.5) * 2  # Convert to [-1, 1]
            
            return (
                weights['roi'] * normalized_roi +
                weights['sharpe'] * normalized_sharpe +
                weights['win_rate'] * normalized_win_rate
            )
            
        except Exception as e:
            logger.error(f"Error calculating baseline performance: {str(e)}")
            return 0.0

    def _calculate_performance_impact(
        self,
        category: str,
        key: str,
        value: Any,
        performance_data: Dict[str, Any],
        baseline: float
    ) -> float:
        """Calculate the performance impact of a specific preference."""
        try:
            # Get historical performance for this setting
            setting_key = f"{category}.{key}.{value}"
            historical = self.performance_cache[setting_key]
            
            if not historical:
                return 0.0
            
            # Calculate average performance difference
            avg_performance = np.mean([p['performance'] for p in historical])
            impact = avg_performance - baseline
            
            # Decay impact based on data age
            max_age = max(
                (datetime.now() - h['timestamp']).total_seconds()
                for h in historical
            )
            decay_factor = np.exp(-max_age / (7 * 24 * 3600))  # 7-day half-life
            
            return impact * decay_factor
            
        except Exception as e:
            logger.error(f"Error calculating performance impact: {str(e)}")
            return 0.0

    def _calculate_confidence(
        self,
        category: str,
        key: str,
        value: Any,
        performance_data: Dict[str, Any]
    ) -> float:
        """Calculate confidence in the performance impact calculation."""
        try:
            setting_key = f"{category}.{key}.{value}"
            historical = self.performance_cache[setting_key]
            
            if len(historical) < 5:
                return 0.3  # Low confidence with limited data
            
            # Calculate consistency of impact
            performances = [p['performance'] for p in historical]
            std_dev = np.std(performances)
            consistency = 1 / (1 + std_dev)  # Higher consistency = lower std dev
            
            # Consider data recency
            timestamps = [h['timestamp'] for h in historical]
            avg_age = (datetime.now() - np.mean(timestamps)).total_seconds()
            recency = np.exp(-avg_age / (30 * 24 * 3600))  # 30-day half-life
            
            # Combine factors
            return min(0.95, consistency * 0.7 + recency * 0.3)
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
            return 0.3

    async def _update_correlations(self):
        """Update correlation analysis between preferences and performance."""
        try:
            if not self.metrics:
                return
                
            # Convert metrics to DataFrame
            df = pd.DataFrame([
                {
                    'timestamp': m.timestamp,
                    'category': m.category,
                    'key': m.key,
                    'value': str(m.value),
                    'impact': m.performance_impact
                }
                for m in self.metrics
            ])
            
            # Calculate correlations
            pivot = df.pivot_table(
                index='timestamp',
                columns=['category', 'key', 'value'],
                values='impact',
                aggfunc='first'
            )
            
            self.correlation_cache = pivot.corr().to_dict()
            
        except Exception as e:
            logger.error(f"Error updating correlations: {str(e)}")

    def _analyze_category_impact(
        self,
        metrics: List[PreferenceMetric]
    ) -> Dict[str, Dict[str, float]]:
        """Analyze impact of each preference category."""
        impacts = defaultdict(list)
        
        for metric in metrics:
            impacts[metric.category].append({
                'impact': metric.performance_impact,
                'confidence': metric.confidence
            })
        
        return {
            category: {
                'impact': np.mean([m['impact'] for m in mlist]),
                'confidence': np.mean([m['confidence'] for m in mlist]),
                'sample_size': len(mlist)
            }
            for category, mlist in impacts.items()
        }

    def _get_top_performing_settings(
        self,
        metrics: List[PreferenceMetric]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get top performing settings for each category."""
        settings = defaultdict(list)
        
        for metric in metrics:
            settings[metric.category].append({
                'key': metric.key,
                'value': metric.value,
                'impact': metric.performance_impact,
                'confidence': metric.confidence
            })
        
        return {
            category: sorted(
                s,
                key=lambda x: x['impact'] * x['confidence'],
                reverse=True
            )[:3]
            for category, s in settings.items()
        }

    def _generate_suggestions(
        self,
        user_id: str,
        metrics: List[PreferenceMetric],
        category_impact: Dict[str, Dict[str, float]]
    ) -> List[Dict[str, Any]]:
        """Generate preference optimization suggestions."""
        suggestions = []
        
        # Find underperforming categories
        for category, stats in category_impact.items():
            if stats['impact'] < 0 and stats['confidence'] > 0.5:
                top_settings = self._get_top_performing_settings_for_category(
                    category,
                    metrics
                )
                
                if top_settings:
                    suggestions.append({
                        'category': category,
                        'current_impact': stats['impact'],
                        'suggested_settings': top_settings,
                        'confidence': stats['confidence'],
                        'priority': 'high' if stats['impact'] < -0.3 else 'medium'
                    })
        
        return suggestions

    def _get_top_performing_settings_for_category(
        self,
        category: str,
        metrics: List[PreferenceMetric]
    ) -> List[Dict[str, Any]]:
        """Get top performing settings for a specific category."""
        category_metrics = [m for m in metrics if m.category == category]
        
        if not category_metrics:
            return []
        
        settings = defaultdict(list)
        for metric in category_metrics:
            key = f"{metric.key}.{metric.value}"
            settings[key].append({
                'impact': metric.performance_impact,
                'confidence': metric.confidence
            })
        
        # Calculate average impact and confidence
        averaged = [
            {
                'key': key.split('.')[0],
                'value': key.split('.')[1],
                'impact': np.mean([m['impact'] for m in metrics]),
                'confidence': np.mean([m['confidence'] for m in metrics])
            }
            for key, metrics in settings.items()
        ]
        
        # Sort by impact * confidence
        return sorted(
            averaged,
            key=lambda x: x['impact'] * x['confidence'],
            reverse=True
        )[:3]

    def _calculate_overall_confidence(
        self,
        metrics: List[PreferenceMetric]
    ) -> float:
        """Calculate overall confidence in the analysis."""
        if not metrics:
            return 0.0
            
        # Weight confidence by recency
        now = datetime.now()
        weighted_conf = []
        
        for metric in metrics:
            age = (now - metric.timestamp).total_seconds()
            weight = np.exp(-age / (7 * 24 * 3600))  # 7-day half-life
            weighted_conf.append(metric.confidence * weight)
            
        return np.average(weighted_conf)

    def _parse_timeframe(self, timeframe: str) -> datetime:
        """Parse timeframe string into datetime."""
        now = datetime.now()
        
        units = {
            'd': 'days',
            'w': 'weeks',
            'm': 'months',
            'y': 'years'
        }
        
        amount = int(timeframe[:-1])
        unit = timeframe[-1]
        
        if unit not in units:
            raise ValueError(f"Invalid timeframe unit: {unit}")
            
        delta = {units[unit]: amount}
        return now - timedelta(**delta)