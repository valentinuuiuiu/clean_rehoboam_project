
import unittest
from utils.portfolio_optimizer import PortfolioOptimizer

class TestPortfolioOptimizer(unittest.TestCase):
    def setUp(self):
        self.optimizer = PortfolioOptimizer(max_position_size=0.2)
        
    def test_basic_position_sizing(self):
        position_size, metrics = self.optimizer.calculate_optimal_position(
            current_price=1000.0,
            volatility=0.1,
            available_capital=10000.0
        )
        
        self.assertGreater(position_size, 0)
        self.assertLess(position_size * 1000.0, 10000.0)  # Position value less than capital
        
    def test_max_position_constraint(self):
        position_size, metrics = self.optimizer.calculate_optimal_position(
            current_price=100.0,
            volatility=0.01,  # Very low volatility to force max position
            available_capital=10000.0
        )
        
        # Max position should be 20% of capital
        self.assertAlmostEqual(
            position_size * 100.0 / 10000.0,  # Position value / capital
            0.2,  # Max position size
            places=2
        )
        
    def test_high_volatility_reduces_position(self):
        low_vol_size, _ = self.optimizer.calculate_optimal_position(
            current_price=100.0,
            volatility=0.1,
            available_capital=10000.0
        )
        
        high_vol_size, _ = self.optimizer.calculate_optimal_position(
            current_price=100.0,
            volatility=0.2,
            available_capital=10000.0
        )
        
        self.assertGreater(low_vol_size, high_vol_size)

    def test_metrics_output(self):
        _, metrics = self.optimizer.calculate_optimal_position(
            current_price=1000.0,
            volatility=0.1,
            available_capital=10000.0
        )
        
        required_metrics = [
            "risk_amount",
            "volatility_adjusted_size",
            "max_position_size",
            "final_position_size",
            "capital_utilization"
        ]
        
        for metric in required_metrics:
            self.assertIn(metric, metrics)
            self.assertIsInstance(metrics[metric], float)

if __name__ == '__main__':
    unittest.main()
