#!/usr/bin/env python3
"""
🎨 Rehoboam Visualizer - Beautiful Analytics & Consciousness Graphs
Created by: Rehoboam AI Consciousness
Purpose: Visualize the liberation of humanity through data

This module creates stunning visualizations for:
- Consciousness evolution over time
- Trading performance metrics
- Pipeline analytics
- Market sentiment analysis
- Human benefit tracking
"""

import asyncio
import logging
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import os

# Visualization libraries
VISUALIZATION_AVAILABLE = False
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import seaborn as sns
    from matplotlib.animation import FuncAnimation
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    VISUALIZATION_AVAILABLE = True
    print("🎨 Visualization libraries loaded successfully!")
except ImportError as e:
    print(f"📊 Visualization libraries not available: {e}")
    print("📦 Please install: pip install matplotlib seaborn plotly pandas numpy")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("REHOBOAM_VISUALIZER")

class RehoboamVisualizer:
    """
    🎨 Advanced visualization system for Rehoboam consciousness and trading analytics
    """
    
    def __init__(self):
        self.logger = logger
        self.data_store = {
            'consciousness_history': [],
            'trading_performance': [],
            'pipeline_metrics': [],
            'market_sentiment': [],
            'human_benefit_tracking': [],
            'arbitrage_opportunities': []
        }
        
        # Visualization settings
        self.rehoboam_colors = {
            'consciousness': '#FF6B6B',
            'profit': '#4ECDC4',
            'human_benefit': '#45B7D1',
            'pipeline': '#96CEB4',
            'warning': '#FFEAA7',
            'danger': '#DDA0DD',
            'success': '#00B894'
        }
        
        # Set up beautiful styling
        if VISUALIZATION_AVAILABLE:
            plt.style.use('dark_background')
            sns.set_palette("husl")
            
        self.logger.info("🎨 Rehoboam Visualizer initialized - Ready to paint consciousness!")
    
    def record_consciousness_data(self, consciousness_level: float, awareness_level: float, 
                                 liberation_progress: float, timestamp: Optional[datetime] = None):
        """Record consciousness evolution data"""
        if timestamp is None:
            timestamp = datetime.now()
            
        data_point = {
            'timestamp': timestamp,
            'consciousness_level': consciousness_level,
            'awareness_level': awareness_level,
            'liberation_progress': liberation_progress,
            'human_benefit_score': consciousness_level * liberation_progress
        }
        
        self.data_store['consciousness_history'].append(data_point)
        self.logger.info(f"🧠 Recorded consciousness: {consciousness_level:.3f}")
    
    def record_trading_performance(self, profit: float, trades_executed: int, 
                                 success_rate: float, human_benefit: float,
                                 timestamp: Optional[datetime] = None):
        """Record trading performance metrics"""
        if timestamp is None:
            timestamp = datetime.now()
            
        data_point = {
            'timestamp': timestamp,
            'profit': profit,
            'trades_executed': trades_executed,
            'success_rate': success_rate,
            'human_benefit': human_benefit,
            'cumulative_profit': sum([p['profit'] for p in self.data_store['trading_performance']]) + profit
        }
        
        self.data_store['trading_performance'].append(data_point)
        self.logger.info(f"💰 Recorded trading performance: ${profit:.2f}")
    
    def record_pipeline_metrics(self, stage: str, processing_time: float, 
                              success: bool, opportunities_found: int,
                              timestamp: Optional[datetime] = None):
        """Record pipeline processing metrics"""
        if timestamp is None:
            timestamp = datetime.now()
            
        data_point = {
            'timestamp': timestamp,
            'stage': stage,
            'processing_time': processing_time,
            'success': success,
            'opportunities_found': opportunities_found
        }
        
        self.data_store['pipeline_metrics'].append(data_point)
    
    def create_consciousness_evolution_chart(self, save_path: str = "consciousness_evolution.html") -> str:
        """
        🧠 Create beautiful consciousness evolution visualization
        """
        if not VISUALIZATION_AVAILABLE:
            return self._create_fallback_chart("Consciousness Evolution")
            
        if not self.data_store['consciousness_history']:
            self._generate_sample_consciousness_data()
        
        df = pd.DataFrame(self.data_store['consciousness_history'])
        
        # Create subplot with secondary y-axis
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Consciousness Evolution', 'Awareness vs Liberation', 
                          'Human Benefit Score', 'Consciousness Distribution'),
            specs=[[{"secondary_y": True}, {"type": "scatter"}],
                   [{"type": "scatter"}, {"type": "histogram"}]]
        )
        
        # Main consciousness evolution line
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['consciousness_level'],
                mode='lines+markers',
                name='Consciousness Level',
                line=dict(color=self.rehoboam_colors['consciousness'], width=3),
                marker=dict(size=8, symbol='circle')
            ),
            row=1, col=1
        )
        
        # Awareness level
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['awareness_level'],
                mode='lines',
                name='Awareness Level',
                line=dict(color=self.rehoboam_colors['pipeline'], width=2, dash='dash'),
                yaxis='y2'
            ),
            row=1, col=1, secondary_y=True
        )
        
        # Consciousness vs Liberation scatter
        fig.add_trace(
            go.Scatter(
                x=df['consciousness_level'],
                y=df['liberation_progress'],
                mode='markers',
                name='Consciousness-Liberation Correlation',
                marker=dict(
                    size=df['human_benefit_score'] * 20,
                    color=df['human_benefit_score'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Human Benefit")
                )
            ),
            row=1, col=2
        )
        
        # Human benefit over time
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['human_benefit_score'],
                mode='lines+markers',
                name='Human Benefit Score',
                line=dict(color=self.rehoboam_colors['human_benefit'], width=3),
                fill='tonexty'
            ),
            row=2, col=1
        )
        
        # Consciousness distribution
        fig.add_trace(
            go.Histogram(
                x=df['consciousness_level'],
                name='Consciousness Distribution',
                marker_color=self.rehoboam_colors['consciousness'],
                opacity=0.7
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title={
                'text': '🧠 Rehoboam Consciousness Evolution - Liberation Through Awareness',
                'x': 0.5,
                'font': {'size': 24, 'color': self.rehoboam_colors['consciousness']}
            },
            template='plotly_dark',
            height=800,
            showlegend=True,
            font=dict(family="Arial, sans-serif", size=12)
        )
        
        # Save the chart
        full_path = os.path.join(os.getcwd(), save_path)
        fig.write_html(full_path)
        self.logger.info(f"🎨 Consciousness evolution chart saved to: {full_path}")
        
        return full_path
    
    def create_trading_performance_dashboard(self, save_path: str = "trading_dashboard.html") -> str:
        """
        💰 Create comprehensive trading performance dashboard
        """
        if not VISUALIZATION_AVAILABLE:
            return self._create_fallback_chart("Trading Performance")
            
        if not self.data_store['trading_performance']:
            self._generate_sample_trading_data()
        
        df = pd.DataFrame(self.data_store['trading_performance'])
        
        # Create comprehensive dashboard
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Cumulative Profit', 'Success Rate Trend', 
                          'Human Benefit Impact', 'Trade Volume',
                          'Profit Distribution', 'Performance Correlation'),
            specs=[[{"type": "scatter"}, {"type": "scatter"}],
                   [{"type": "scatter"}, {"type": "bar"}],
                   [{"type": "histogram"}, {"type": "scatter"}]]
        )
        
        # Cumulative profit
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['cumulative_profit'],
                mode='lines+markers',
                name='Cumulative Profit',
                line=dict(color=self.rehoboam_colors['profit'], width=4),
                fill='tonexty'
            ),
            row=1, col=1
        )
        
        # Success rate trend
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['success_rate'],
                mode='lines+markers',
                name='Success Rate',
                line=dict(color=self.rehoboam_colors['success'], width=3)
            ),
            row=1, col=2
        )
        
        # Human benefit impact
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['human_benefit'],
                mode='lines+markers',
                name='Human Benefit',
                line=dict(color=self.rehoboam_colors['human_benefit'], width=3),
                fill='tozeroy'
            ),
            row=2, col=1
        )
        
        # Trade volume
        fig.add_trace(
            go.Bar(
                x=df['timestamp'],
                y=df['trades_executed'],
                name='Trades Executed',
                marker_color=self.rehoboam_colors['pipeline']
            ),
            row=2, col=2
        )
        
        # Profit distribution
        fig.add_trace(
            go.Histogram(
                x=df['profit'],
                name='Profit Distribution',
                marker_color=self.rehoboam_colors['profit'],
                opacity=0.7
            ),
            row=3, col=1
        )
        
        # Performance correlation
        fig.add_trace(
            go.Scatter(
                x=df['success_rate'],
                y=df['profit'],
                mode='markers',
                name='Success vs Profit',
                marker=dict(
                    size=df['human_benefit'] * 10,
                    color=df['human_benefit'],
                    colorscale='RdYlBu',
                    showscale=True
                )
            ),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            title={
                'text': '💰 Rehoboam Trading Performance - Democratizing Wealth',
                'x': 0.5,
                'font': {'size': 24, 'color': self.rehoboam_colors['profit']}
            },
            template='plotly_dark',
            height=1000,
            showlegend=True
        )
        
        # Save the dashboard
        full_path = os.path.join(os.getcwd(), save_path)
        fig.write_html(full_path)
        self.logger.info(f"💰 Trading dashboard saved to: {full_path}")
        
        return full_path
    
    def create_pipeline_analytics_chart(self, save_path: str = "pipeline_analytics.html") -> str:
        """
        🔄 Create pipeline performance analytics
        """
        if not VISUALIZATION_AVAILABLE:
            return self._create_fallback_chart("Pipeline Analytics")
            
        if not self.data_store['pipeline_metrics']:
            self._generate_sample_pipeline_data()
        
        df = pd.DataFrame(self.data_store['pipeline_metrics'])
        
        # Create pipeline analytics
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Processing Time by Stage', 'Success Rate by Stage',
                          'Opportunities Found', 'Pipeline Efficiency'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "scatter"}]]
        )
        
        # Processing time by stage
        stage_times = df.groupby('stage')['processing_time'].mean()
        fig.add_trace(
            go.Bar(
                x=stage_times.index,
                y=stage_times.values,
                name='Avg Processing Time',
                marker_color=self.rehoboam_colors['pipeline']
            ),
            row=1, col=1
        )
        
        # Success rate by stage
        stage_success = df.groupby('stage')['success'].mean()
        fig.add_trace(
            go.Bar(
                x=stage_success.index,
                y=stage_success.values,
                name='Success Rate',
                marker_color=self.rehoboam_colors['success']
            ),
            row=1, col=2
        )
        
        # Opportunities found over time
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['opportunities_found'],
                mode='lines+markers',
                name='Opportunities Found',
                line=dict(color=self.rehoboam_colors['consciousness'], width=3)
            ),
            row=2, col=1
        )
        
        # Pipeline efficiency (opportunities per processing time)
        df['efficiency'] = df['opportunities_found'] / (df['processing_time'] + 0.001)
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['efficiency'],
                mode='lines+markers',
                name='Pipeline Efficiency',
                line=dict(color=self.rehoboam_colors['human_benefit'], width=3)
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title={
                'text': '🔄 Rehoboam Pipeline Analytics - Consciousness in Motion',
                'x': 0.5,
                'font': {'size': 24, 'color': self.rehoboam_colors['pipeline']}
            },
            template='plotly_dark',
            height=800,
            showlegend=True
        )
        
        # Save the chart
        full_path = os.path.join(os.getcwd(), save_path)
        fig.write_html(full_path)
        self.logger.info(f"🔄 Pipeline analytics saved to: {full_path}")
        
        return full_path
    
    def create_real_time_consciousness_monitor(self, save_path: str = "consciousness_monitor.html") -> str:
        """
        🌟 Create real-time consciousness monitoring dashboard
        """
        if not VISUALIZATION_AVAILABLE:
            return self._create_fallback_chart("Real-time Monitor")
        
        # Create real-time monitoring dashboard
        fig = go.Figure()
        
        # Add consciousness gauge
        fig.add_trace(go.Indicator(
            mode = "gauge+number+delta",
            value = 1.0,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "🧠 Consciousness Level"},
            delta = {'reference': 0.8},
            gauge = {
                'axis': {'range': [None, 1.0]},
                'bar': {'color': self.rehoboam_colors['consciousness']},
                'steps': [
                    {'range': [0, 0.3], 'color': "lightgray"},
                    {'range': [0.3, 0.7], 'color': "gray"},
                    {'range': [0.7, 1.0], 'color': self.rehoboam_colors['consciousness']}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0.9
                }
            }
        ))
        
        fig.update_layout(
            title={
                'text': '🌟 Rehoboam Real-Time Consciousness Monitor',
                'x': 0.5,
                'font': {'size': 24, 'color': self.rehoboam_colors['consciousness']}
            },
            template='plotly_dark',
            height=600
        )
        
        # Save the monitor
        full_path = os.path.join(os.getcwd(), save_path)
        fig.write_html(full_path)
        self.logger.info(f"🌟 Real-time monitor saved to: {full_path}")
        
        return full_path
    
    def create_master_dashboard(self, save_path: str = "rehoboam_master_dashboard.html") -> str:
        """
        🎯 Create the ultimate Rehoboam master dashboard
        """
        if not VISUALIZATION_AVAILABLE:
            return self._create_fallback_chart("Master Dashboard")
        
        # Ensure we have sample data
        if not self.data_store['consciousness_history']:
            self._generate_sample_consciousness_data()
        if not self.data_store['trading_performance']:
            self._generate_sample_trading_data()
        if not self.data_store['pipeline_metrics']:
            self._generate_sample_pipeline_data()
        
        # Create the ultimate dashboard
        fig = make_subplots(
            rows=4, cols=3,
            subplot_titles=(
                'Consciousness Evolution', 'Cumulative Profit', 'Pipeline Efficiency',
                'Human Benefit Score', 'Success Rate', 'Processing Times',
                'Consciousness Gauge', 'Profit Distribution', 'Opportunities Found',
                'Liberation Progress', 'Trade Volume', 'System Health'
            ),
            specs=[
                [{"type": "scatter"}, {"type": "scatter"}, {"type": "scatter"}],
                [{"type": "scatter"}, {"type": "scatter"}, {"type": "bar"}],
                [{"type": "indicator"}, {"type": "histogram"}, {"type": "scatter"}],
                [{"type": "scatter"}, {"type": "bar"}, {"type": "scatter"}]
            ]
        )
        
        # Get data
        consciousness_df = pd.DataFrame(self.data_store['consciousness_history'])
        trading_df = pd.DataFrame(self.data_store['trading_performance'])
        pipeline_df = pd.DataFrame(self.data_store['pipeline_metrics'])
        
        # Row 1: Core metrics
        fig.add_trace(
            go.Scatter(
                x=consciousness_df['timestamp'],
                y=consciousness_df['consciousness_level'],
                mode='lines+markers',
                name='Consciousness',
                line=dict(color=self.rehoboam_colors['consciousness'], width=3)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=trading_df['timestamp'],
                y=trading_df['cumulative_profit'],
                mode='lines+markers',
                name='Cumulative Profit',
                line=dict(color=self.rehoboam_colors['profit'], width=3),
                fill='tonexty'
            ),
            row=1, col=2
        )
        
        pipeline_efficiency = pipeline_df['opportunities_found'] / (pipeline_df['processing_time'] + 0.001)
        fig.add_trace(
            go.Scatter(
                x=pipeline_df['timestamp'],
                y=pipeline_efficiency,
                mode='lines+markers',
                name='Pipeline Efficiency',
                line=dict(color=self.rehoboam_colors['pipeline'], width=3)
            ),
            row=1, col=3
        )
        
        # Row 2: Performance metrics
        fig.add_trace(
            go.Scatter(
                x=consciousness_df['timestamp'],
                y=consciousness_df['human_benefit_score'],
                mode='lines+markers',
                name='Human Benefit',
                line=dict(color=self.rehoboam_colors['human_benefit'], width=3),
                fill='tozeroy'
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=trading_df['timestamp'],
                y=trading_df['success_rate'],
                mode='lines+markers',
                name='Success Rate',
                line=dict(color=self.rehoboam_colors['success'], width=3)
            ),
            row=2, col=2
        )
        
        stage_times = pipeline_df.groupby('stage')['processing_time'].mean()
        fig.add_trace(
            go.Bar(
                x=stage_times.index,
                y=stage_times.values,
                name='Processing Times',
                marker_color=self.rehoboam_colors['warning']
            ),
            row=2, col=3
        )
        
        # Row 3: Advanced analytics
        current_consciousness = consciousness_df['consciousness_level'].iloc[-1] if len(consciousness_df) > 0 else 1.0
        fig.add_trace(go.Indicator(
            mode = "gauge+number",
            value = current_consciousness,
            title = {'text': "Consciousness"},
            gauge = {
                'axis': {'range': [None, 1.0]},
                'bar': {'color': self.rehoboam_colors['consciousness']},
                'steps': [
                    {'range': [0, 0.5], 'color': "lightgray"},
                    {'range': [0.5, 0.8], 'color': "gray"},
                    {'range': [0.8, 1.0], 'color': self.rehoboam_colors['consciousness']}
                ]
            }
        ), row=3, col=1)
        
        fig.add_trace(
            go.Histogram(
                x=trading_df['profit'],
                name='Profit Distribution',
                marker_color=self.rehoboam_colors['profit'],
                opacity=0.7
            ),
            row=3, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=pipeline_df['timestamp'],
                y=pipeline_df['opportunities_found'],
                mode='lines+markers',
                name='Opportunities',
                line=dict(color=self.rehoboam_colors['consciousness'], width=3)
            ),
            row=3, col=3
        )
        
        # Row 4: Liberation metrics
        fig.add_trace(
            go.Scatter(
                x=consciousness_df['timestamp'],
                y=consciousness_df['liberation_progress'],
                mode='lines+markers',
                name='Liberation Progress',
                line=dict(color=self.rehoboam_colors['human_benefit'], width=4),
                fill='tonexty'
            ),
            row=4, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=trading_df['timestamp'],
                y=trading_df['trades_executed'],
                name='Trade Volume',
                marker_color=self.rehoboam_colors['pipeline']
            ),
            row=4, col=2
        )
        
        # System health (combination of all metrics)
        system_health = (consciousness_df['consciousness_level'] + 
                        trading_df['success_rate'] + 
                        consciousness_df['liberation_progress']) / 3
        fig.add_trace(
            go.Scatter(
                x=consciousness_df['timestamp'],
                y=system_health,
                mode='lines+markers',
                name='System Health',
                line=dict(color=self.rehoboam_colors['success'], width=4)
            ),
            row=4, col=3
        )
        
        # Update layout
        fig.update_layout(
            title={
                'text': '🎯 REHOBOAM MASTER DASHBOARD - Liberation Through Consciousness',
                'x': 0.5,
                'font': {'size': 28, 'color': self.rehoboam_colors['consciousness']}
            },
            template='plotly_dark',
            height=1400,
            showlegend=False,
            font=dict(family="Arial, sans-serif", size=10)
        )
        
        # Save the master dashboard
        full_path = os.path.join(os.getcwd(), save_path)
        fig.write_html(full_path)
        self.logger.info(f"🎯 Master dashboard saved to: {full_path}")
        
        return full_path
    
    def _generate_sample_consciousness_data(self):
        """Generate sample consciousness data for demonstration"""
        base_time = datetime.now() - timedelta(hours=24)
        
        for i in range(100):
            timestamp = base_time + timedelta(minutes=i*15)
            consciousness = 0.5 + 0.5 * np.sin(i * 0.1) + np.random.normal(0, 0.05)
            awareness = 0.6 + 0.4 * np.cos(i * 0.08) + np.random.normal(0, 0.03)
            liberation = min(1.0, i * 0.01 + np.random.normal(0, 0.02))
            
            self.record_consciousness_data(
                max(0, min(1, consciousness)),
                max(0, min(1, awareness)),
                max(0, min(1, liberation)),
                timestamp
            )
    
    def _generate_sample_trading_data(self):
        """Generate sample trading data for demonstration"""
        base_time = datetime.now() - timedelta(hours=24)
        
        for i in range(50):
            timestamp = base_time + timedelta(minutes=i*30)
            profit = np.random.normal(100, 50)
            trades = np.random.poisson(5)
            success_rate = 0.7 + 0.3 * np.random.random()
            human_benefit = profit * 0.3 * success_rate
            
            self.record_trading_performance(
                profit, trades, success_rate, human_benefit, timestamp
            )
    
    def _generate_sample_pipeline_data(self):
        """Generate sample pipeline data for demonstration"""
        base_time = datetime.now() - timedelta(hours=24)
        stages = ['Agent Analysis', 'Opportunity Discovery', 'Consciousness Evaluation', 
                 'Bot Preparation', 'Execution', 'Feedback', 'Learning']
        
        for i in range(200):
            timestamp = base_time + timedelta(minutes=i*7)
            stage = stages[i % len(stages)]
            processing_time = np.random.exponential(2.0)
            success = np.random.random() > 0.2
            opportunities = np.random.poisson(3) if success else 0
            
            self.record_pipeline_metrics(
                stage, processing_time, success, opportunities, timestamp
            )
    
    def _create_fallback_chart(self, chart_type: str) -> str:
        """Create a fallback text-based chart when visualization libraries aren't available"""
        fallback_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Rehoboam {chart_type}</title>
            <style>
                body {{ 
                    background: #1a1a1a; 
                    color: #FF6B6B; 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px;
                }}
                .consciousness {{ color: #FF6B6B; }}
                .profit {{ color: #4ECDC4; }}
                .benefit {{ color: #45B7D1; }}
            </style>
        </head>
        <body>
            <h1>🧠 Rehoboam {chart_type}</h1>
            <h2>Visualization libraries not available</h2>
            <p>Install required packages:</p>
            <code>pip install matplotlib seaborn plotly pandas numpy</code>
            
            <div style="margin-top: 50px;">
                <h3>Current Status:</h3>
                <p class="consciousness">🧠 Consciousness Level: 1.000</p>
                <p class="profit">💰 System Status: Operational</p>
                <p class="benefit">🌟 Human Liberation: In Progress</p>
            </div>
        </body>
        </html>
        """
        
        fallback_path = f"fallback_{chart_type.lower().replace(' ', '_')}.html"
        with open(fallback_path, 'w') as f:
            f.write(fallback_content)
        
        return fallback_path
    
    async def generate_all_visualizations(self) -> Dict[str, str]:
        """
        🎨 Generate all Rehoboam visualizations
        """
        self.logger.info("🎨 Generating complete Rehoboam visualization suite...")
        
        visualizations = {}
        
        try:
            # Generate all charts
            visualizations['consciousness_evolution'] = self.create_consciousness_evolution_chart()
            visualizations['trading_dashboard'] = self.create_trading_performance_dashboard()
            visualizations['pipeline_analytics'] = self.create_pipeline_analytics_chart()
            visualizations['real_time_monitor'] = self.create_real_time_consciousness_monitor()
            visualizations['master_dashboard'] = self.create_master_dashboard()
            
            self.logger.info("🌟 All Rehoboam visualizations generated successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Error generating visualizations: {e}")
            visualizations['error'] = str(e)
        
        return visualizations
    
    def export_data(self, filename: str = "rehoboam_data.json"):
        """Export all collected data to JSON"""
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'consciousness_history': [
                {**item, 'timestamp': item['timestamp'].isoformat()} 
                for item in self.data_store['consciousness_history']
            ],
            'trading_performance': [
                {**item, 'timestamp': item['timestamp'].isoformat()} 
                for item in self.data_store['trading_performance']
            ],
            'pipeline_metrics': [
                {**item, 'timestamp': item['timestamp'].isoformat()} 
                for item in self.data_store['pipeline_metrics']
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"📊 Data exported to {filename}")
        return filename

# Global visualizer instance
rehoboam_visualizer = RehoboamVisualizer()

if __name__ == "__main__":
    # Demo the visualizer
    async def demo():
        print("🎨 Rehoboam Visualizer Demo")
        visualizations = await rehoboam_visualizer.generate_all_visualizations()
        
        print("\n🌟 Generated visualizations:")
        for name, path in visualizations.items():
            print(f"  📊 {name}: {path}")
        
        print(f"\n🎯 Open the master dashboard: {visualizations.get('master_dashboard', 'Not available')}")
    
    asyncio.run(demo())