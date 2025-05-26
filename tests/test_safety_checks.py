import unittest
from unittest.mock import Mock, patch
from web3 import Web3
from utils.safety_checks import SafetyChecks
from config import Config
import time

class TestSafetyChecks(unittest.TestCase):
    def setUp(self):
        self.mock_web3 = Mock()
        self.safety_checks = SafetyChecks(self.mock_web3)

    def test_check_gas_price_success(self):
        """Test successful gas price check"""
        self.mock_web3.eth.gas_price = Web3.to_wei(50, 'gwei')
        self.assertTrue(self.safety_checks.check_gas_price())

    def test_check_gas_price_failure(self):
        """Test gas price too high"""
        self.mock_web3.eth.gas_price = Web3.to_wei(150, 'gwei')
        self.assertFalse(self.safety_checks.check_gas_price())

    def test_check_slippage_success(self):
        """Test acceptable slippage"""
        self.assertTrue(self.safety_checks.check_slippage(100, 100.4))  # 0.4% slippage

    def test_check_slippage_failure(self):
        """Test excessive slippage"""
        self.assertFalse(self.safety_checks.check_slippage(100, 101))  # 1% slippage

    def test_check_trade_size_success(self):
        """Test acceptable trade size"""
        self.assertTrue(self.safety_checks.check_trade_size(5))

    def test_check_trade_size_failure(self):
        """Test excessive trade size"""
        self.assertFalse(self.safety_checks.check_trade_size(15))

    def test_circuit_breaker_lifecycle(self):
        """Test complete circuit breaker lifecycle"""
        # Initial state - should allow trading
        self.assertTrue(self.safety_checks.check_circuit_breaker())
        
        # After trade - should block
        self.safety_checks.update_last_trade_timestamp()
        self.assertFalse(self.safety_checks.check_circuit_breaker())
        
        # After cooldown - should allow trading again
        time.sleep(0.1)  # Small delay for testing
        self.safety_checks.last_trade_timestamp -= Config.CIRCUIT_BREAKER_COOLDOWN + 1
        self.assertTrue(self.safety_checks.check_circuit_breaker())

    def test_retry_mechanism_sequence(self):
        """Test retry mechanism with sequence of attempts"""
        for i in range(Config.MAX_RETRY_ATTEMPTS):
            self.assertTrue(
                self.safety_checks.record_failed_attempt(),
                f"Attempt {i+1} should be allowed"
            )
        
        # One more attempt after max should fail
        self.assertFalse(
            self.safety_checks.record_failed_attempt(),
            "Should not allow attempts beyond max retry limit"
        )
        
        # Reset and verify we can try again
        self.safety_checks.reset_failed_attempts()
        self.assertTrue(
            self.safety_checks.record_failed_attempt(),
            "Should allow new attempts after reset"
        )

if __name__ == '__main__':
    unittest.main()
