"""Advanced Portfolio Optimizer with AI-driven risk management."""
import numpy as np
from typing import Dict, List, Optional, Tuple
import pandas as pd
from dataclasses import dataclass
from scipy.optimize import minimize
from datetime import datetime
import torch
from torch import nn

@dataclass
class OptimizationResult:
    total_value: float
    optimal_weights: Dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    suggested_trades: List[Dict]
    risk_metrics: Dict[str, float]
    confidence_score: float

class PortfolioOptimizer:
    def __init__(self, max_position_size: float = 0.2):
        self.max_position_size = max_position_size
        self.risk_free_rate = 0.02  # 2% risk-free rate
        self.min_acceptable_sharpe = 1.5
        self.volatility_penalty = 1.2
        self.correlation_threshold = 0.7
        
        # Initialize ML model for return predictions
        self.return_predictor = ReturnPredictor()
        
        # Risk management parameters
        self.max_drawdown_limit = 0.15  # 15% maximum drawdown
        self.var_confidence_level = 0.95  # 95% VaR
        self.position_limits = {
            'crypto': 0.4,  # 40% max in crypto
            'stables': 0.6,  # 60% max in stablecoins
            'volatile': 0.3  # 30% max in volatile assets
        }
        
    def optimize_portfolio(self, positions: Dict[str, float], 
                         prices: Dict[str, float],
                         volatilities: Dict[str, float],
                         capital: float,
                         market_data: Optional[Dict] = None) -> OptimizationResult:
        """Optimize portfolio with advanced risk management and AI predictions."""
        try:
            # Current portfolio state
            current_weights = self._calculate_current_weights(positions, prices, capital)
            
            # Get return predictions from ML model
            expected_returns = self.return_predictor.predict_returns(market_data or {})
            
            # Calculate correlation matrix
            correlation_matrix = self._calculate_correlation_matrix(list(positions.keys()))
            
            # Define optimization constraints
            constraints = self._generate_constraints(correlation_matrix)
            
            # Optimize with risk-adjusted objective
            result = minimize(
                self._objective_function,
                x0=list(current_weights.values()),
                args=(expected_returns, volatilities, correlation_matrix),
                method='SLSQP',
                constraints=constraints,
                bounds=[(0, self.max_position_size) for _ in current_weights]
            )
            
            if not result.success:
                raise ValueError("Portfolio optimization failed")
                
            # Calculate optimal portfolio metrics
            optimal_weights = dict(zip(positions.keys(), result.x))
            portfolio_metrics = self._calculate_portfolio_metrics(
                optimal_weights, expected_returns, volatilities, correlation_matrix
            )
            
            # Generate trade suggestions
            trades = self._generate_trade_suggestions(
                current_weights, optimal_weights, prices, capital
            )
            
            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(
                optimal_weights, volatilities, correlation_matrix, capital
            )
            
            # Calculate confidence score
            confidence = self._calculate_confidence_score(
                portfolio_metrics['sharpe_ratio'],
                risk_metrics,
                len(trades)
            )
            
            return OptimizationResult(
                total_value=capital,
                optimal_weights=optimal_weights,
                expected_return=portfolio_metrics['expected_return'],
                volatility=portfolio_metrics['volatility'],
                sharpe_ratio=portfolio_metrics['sharpe_ratio'],
                suggested_trades=trades,
                risk_metrics=risk_metrics,
                confidence_score=confidence
            )
            
        except Exception as e:
            logger.error(f"Portfolio optimization failed: {str(e)}")
            raise
            
    def _objective_function(self, weights: np.ndarray, 
                          expected_returns: np.ndarray,
                          volatilities: np.ndarray,
                          correlation_matrix: np.ndarray) -> float:
        """Risk-adjusted objective function for optimization."""
        # Calculate portfolio return and risk
        portfolio_return = np.sum(weights * expected_returns)
        portfolio_risk = np.sqrt(
            np.dot(weights.T, np.dot(correlation_matrix * np.outer(volatilities, volatilities), weights))
        )
        
        # Calculate Sharpe ratio
        sharpe = (portfolio_return - self.risk_free_rate) / (portfolio_risk + 1e-6)
        
        # Add penalties
        concentration_penalty = np.sum(weights ** 2)  # Penalize concentration
        volatility_penalty = portfolio_risk * self.volatility_penalty
        
        # Return negative Sharpe ratio (we minimize)
        return -sharpe + concentration_penalty + volatility_penalty
        
    def _calculate_correlation_matrix(self, assets: List[str]) -> np.ndarray:
        """Calculate correlation matrix with historical data."""
        # In real implementation, this would use historical price data
        n = len(assets)
        # For now, return identity matrix
        return np.eye(n)
        
    def _generate_constraints(self, correlation_matrix: np.ndarray) -> List[Dict]:
        """Generate optimization constraints."""
        n = correlation_matrix.shape[0]
        
        constraints = [
            # Sum of weights = 1
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            
            # Maximum allocation per asset
            *[{'type': 'ineq', 'fun': lambda x, i=i: self.max_position_size - x[i]}
              for i in range(n)],
              
            # Minimum allocation (0)
            *[{'type': 'ineq', 'fun': lambda x, i=i: x[i]}
              for i in range(n)]
        ]
        
        return constraints
        
    def _calculate_portfolio_metrics(self, weights: Dict[str, float],
                                   expected_returns: Dict[str, float],
                                   volatilities: Dict[str, float],
                                   correlation_matrix: np.ndarray) -> Dict[str, float]:
        """Calculate portfolio performance metrics."""
        w = np.array(list(weights.values()))
        r = np.array(list(expected_returns.values()))
        v = np.array(list(volatilities.values()))
        
        portfolio_return = np.sum(w * r)
        portfolio_vol = np.sqrt(np.dot(w.T, np.dot(correlation_matrix * np.outer(v, v), w)))
        sharpe = (portfolio_return - self.risk_free_rate) / (portfolio_vol + 1e-6)
        
        return {
            'expected_return': portfolio_return,
            'volatility': portfolio_vol,
            'sharpe_ratio': sharpe
        }
        
    def _generate_trade_suggestions(self, current_weights: Dict[str, float],
                                  target_weights: Dict[str, float],
                                  prices: Dict[str, float],
                                  capital: float) -> List[Dict]:
        """Generate trade suggestions to reach target allocation."""
        trades = []
        
        for asset in current_weights:
            current = current_weights[asset]
            target = target_weights[asset]
            
            if abs(target - current) > 0.01:  # 1% minimum trade size
                trade_value = (target - current) * capital
                trade_amount = trade_value / prices[asset]
                
                trades.append({
                    'asset': asset,
                    'action': 'buy' if target > current else 'sell',
                    'amount': abs(trade_amount),
                    'value': abs(trade_value),
                    'target_weight': target
                })
                
        return trades
        
    def _calculate_risk_metrics(self, weights: Dict[str, float],
                              volatilities: Dict[str, float],
                              correlation_matrix: np.ndarray,
                              capital: float) -> Dict[str, float]:
        """Calculate comprehensive risk metrics."""
        w = np.array(list(weights.values()))
        v = np.array(list(volatilities.values()))
        
        # Calculate Value at Risk (VaR)
        portfolio_vol = np.sqrt(np.dot(w.T, np.dot(correlation_matrix * np.outer(v, v), w)))
        var_95 = norm.ppf(0.95) * portfolio_vol * capital
        
        # Calculate Expected Shortfall (ES)
        es_95 = norm.pdf(norm.ppf(0.95)) / (1 - 0.95) * portfolio_vol * capital
        
        # Calculate maximum drawdown
        max_drawdown = portfolio_vol * np.sqrt(252) * 2.33  # 99% confidence
        
        return {
            'var_95': var_95,
            'es_95': es_95,
            'max_drawdown': max_drawdown,
            'portfolio_volatility': portfolio_vol,
            'diversification_score': 1 - np.sum(w ** 2)  # Herfindahl index
        }
        
    def _calculate_confidence_score(self, sharpe_ratio: float,
                                  risk_metrics: Dict[str, float],
                                  num_trades: int) -> float:
        """Calculate confidence score for the optimization result."""
        # Factors affecting confidence
        sharpe_factor = min(1.0, sharpe_ratio / self.min_acceptable_sharpe)
        risk_factor = 1 - (risk_metrics['portfolio_volatility'] / self.max_drawdown_limit)
        diversity_factor = risk_metrics['diversification_score']
        
        # Penalize too many trades
        trade_factor = 1 - (0.1 * (num_trades / 10))  # Penalize over 10 trades
        
        # Combine factors with weights
        confidence = (
            0.3 * sharpe_factor +
            0.3 * risk_factor +
            0.2 * diversity_factor +
            0.2 * trade_factor
        )
        
        return max(0.0, min(1.0, confidence))

class ReturnPredictor(nn.Module):
    """Neural network for predicting asset returns."""
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=10, hidden_size=64, num_layers=2, batch_first=True)
        self.fc1 = nn.Linear(64, 32)
        self.fc2 = nn.Linear(32, 1)
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        x, _ = self.lstm(x)
        x = torch.relu(self.fc1(x[:, -1, :]))
        x = self.dropout(x)
        return self.fc2(x)
        
    def predict_returns(self, market_data: Dict) -> Dict[str, float]:
        """Predict returns for each asset."""
        # Implementation would use actual market data
        # For now, return dummy predictions
        return {asset: 0.1 for asset in market_data.keys()}
