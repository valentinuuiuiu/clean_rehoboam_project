import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from decimal import Decimal

# Assuming L2Manager and its dependencies are structured in utils
from utils.l2_manager import L2Manager
# We need to mock NetworkConfig, Layer2GasEstimator, and web3_service
# if they are imported and used by L2Manager.

# Mock classes for dependencies that L2Manager might try to import or use
# These mocks will stand in for the actual classes if they are not available
# or if we want to control their behavior during tests.

class MockNetworkConfig:
    def __init__(self):
        self.logger = MagicMock()
    def get_network(self, network_name: str):
        if network_name == "test_l2_network":
            return {"name": "Test L2 Network", "chain_id": 12345, "rpc_url": "http://testrpc.com"}
        return None
    # Add other methods if L2Manager calls them, though not strictly needed for these tests

class MockLayer2GasEstimator:
    def __init__(self, network_config_instance=None):
        self.get_gas_price = MagicMock() # This will be the mock we configure per test
        self.logger = MagicMock()

class MockWeb3Service:
    def __init__(self):
        self.logger = MagicMock()
    # Add other methods if L2Manager calls them

@pytest.fixture
def l2_manager_fixture():
    """
    Provides an L2Manager instance with mocked dependencies for gas price tests.
    Patches Layer2GasEstimator at the point of its import by L2Manager.
    """
    # Mock NetworkConfig and web3_service to be passed to L2Manager constructor
    mock_nc_instance = MockNetworkConfig()
    mock_ws_instance = MockWeb3Service()

    # Layer2GasEstimator is instantiated inside L2Manager.
    # So we patch it where L2Manager looks for it.
    with patch('utils.l2_manager.Layer2GasEstimator', new_callable=lambda: MockLayer2GasEstimator(mock_nc_instance)) as mock_gas_estimator_constructor:
        # The L2Manager will be created, and its self.gas_estimator will be an instance of MockLayer2GasEstimator.
        # The mock_gas_estimator_constructor itself is a mock of the class constructor.
        # We often want to control the instance created by the constructor.
        # A simpler way if MockLayer2GasEstimator is already a sufficient mock:
        # just ensure it's used.

        # If Layer2GasEstimator is imported at module level of l2_manager.py:
        # with patch('utils.l2_manager.Layer2GasEstimator') as MockedGasEstimatorClass:
        #     mock_gas_estimator_instance = MockedGasEstimatorClass.return_value
        #     manager = L2Manager(network_config_instance=mock_nc_instance, web3_service_instance=mock_ws_instance)
        #     yield manager, mock_gas_estimator_instance.get_gas_price # Yield the specific method mock

        # Given L2Manager's current __init__ which creates its own gas_estimator:
        # self.gas_estimator = Layer2GasEstimator(network_config_instance=self.network_config)
        # We need to ensure that the instance created has a mockable get_gas_price method.
        # The MockLayer2GasEstimator already has self.get_gas_price = MagicMock()

        manager = L2Manager(network_config_instance=mock_nc_instance, web3_service_instance=mock_ws_instance)
        # The manager.gas_estimator is an instance of MockLayer2GasEstimator.
        # Its get_gas_price method is already a MagicMock.
        yield manager, manager.gas_estimator.get_gas_price


def test_get_l2_gas_price_success(l2_manager_fixture):
    """
    Tests successful retrieval of L2 gas price.
    """
    l2_manager, mock_get_gas_price_method = l2_manager_fixture
    network_name = "test_l2_network"
    expected_gas_info = {
        "standard": {"maxFeePerGas": Decimal("25"), "maxPriorityFeePerGas": Decimal("1.5")},
        "usd_price_eth": Decimal("2000.00")
    }
    mock_get_gas_price_method.return_value = expected_gas_info

    result = l2_manager.get_l2_gas_price(network_name)

    assert result == expected_gas_info
    mock_get_gas_price_method.assert_called_once_with(network_name)

def test_get_l2_gas_price_estimator_returns_none(l2_manager_fixture):
    """
    Tests behavior when the gas estimator returns None.
    """
    l2_manager, mock_get_gas_price_method = l2_manager_fixture
    network_name = "unknown_l2_network"
    mock_get_gas_price_method.return_value = None

    result = l2_manager.get_l2_gas_price(network_name)

    assert result is None
    mock_get_gas_price_method.assert_called_once_with(network_name)

def test_get_l2_gas_price_estimator_raises_exception(l2_manager_fixture, caplog):
    """
    Tests behavior when the gas estimator raises an exception.
    L2Manager should catch it, log, and return None.
    """
    import logging
    caplog.set_level(logging.ERROR)

    l2_manager, mock_get_gas_price_method = l2_manager_fixture
    network_name = "error_l2_network"
    error_message = "Estimator internal error"
    mock_get_gas_price_method.side_effect = Exception(error_message)

    result = l2_manager.get_l2_gas_price(network_name)

    assert result is None
    mock_get_gas_price_method.assert_called_once_with(network_name)
    assert f"Error getting gas price for {network_name}: {error_message}" in caplog.text

# Example of how to test the mocked Layer2GasEstimator itself (optional, for clarity)
def test_mock_gas_estimator_direct_call():
    mock_nc = MockNetworkConfig()
    estimator = MockLayer2GasEstimator(network_config_instance=mock_nc)
    network_name = "test_l2_network"
    expected_gas_info = {"fast": Decimal("10")}
    estimator.get_gas_price.return_value = expected_gas_info # Configure the MagicMock

    result = estimator.get_gas_price(network_name)
    assert result == expected_gas_info
    estimator.get_gas_price.assert_called_once_with(network_name)
