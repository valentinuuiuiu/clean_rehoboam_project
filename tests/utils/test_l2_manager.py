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


# --- Tests for L2ArbitrageHelper ---
from utils.l2_manager import L2ArbitrageHelper # Ensure this is imported
from unittest.mock import AsyncMock

@pytest.fixture
def mock_l2_manager_for_helper():
    """Creates a comprehensive mock for L2Manager instance needed by L2ArbitrageHelper."""
    manager = MagicMock(spec=L2Manager)
    manager.network_config = MockNetworkConfig() # Use the existing mock
    manager.web3_service = MockWeb3Service()   # Use the existing mock
    manager.logger = MagicMock()
    manager.gas_estimator = MockLayer2GasEstimator(manager.network_config) # Helper uses manager's gas_estimator

    # _execute_arbitrage_trade calls l2_manager.execute_dex_swap
    manager.execute_dex_swap = AsyncMock(return_value="0xmock_buy_tx_hash") # Default success for buy leg
    return manager

@pytest.fixture
def l2_arbitrage_helper_fixture(mock_l2_manager_for_helper):
    """Provides an L2ArbitrageHelper instance with mocked L2Manager."""
    # We need a NetworkConfig instance for L2ArbitrageHelper's own initialization needs
    # if it directly uses it, apart from through L2Manager.
    # L2ArbitrageHelper.__init__ takes network_config_instance and l2_manager_instance

    helper = L2ArbitrageHelper(
        network_config_instance=mock_l2_manager_for_helper.network_config, # Can share the one from mocked L2Manager
        l2_manager_instance=mock_l2_manager_for_helper
    )

    # Set default values for testing calculations
    helper.default_slippage = Decimal("0.01")  # 1%
    helper.default_trade_amount_usd = Decimal("100.0")
    helper.wallet_address = "0xTestWalletAddress"
    helper.private_key = "0xTestPrivateKeyToPassInitCheck" # Ensure it passes the init check
    helper.enable_real_trading = True # To ensure _execute_arbitrage_trade runs
    helper.logger = MagicMock() # Mock logger for the helper itself

    # _load_dex_configurations is called in __init__.
    # We'll override common_tokens and dex_configs here for test predictability,
    # assuming _load_dex_configurations might not find a file or we want specific test data.
    helper.common_tokens = {
        "test_buy_net": {
            "USDC": {"address": "0xUSDCAddressBuy", "decimals": 6},
            "WETH": {"address": "0xWETHAddressBuy", "decimals": 18}
        },
        "test_sell_net": { # For completeness if sell leg was also deeply tested
            "USDC": {"address": "0xUSDCAddressSell", "decimals": 6},
            "WETH": {"address": "0xWETHAddressSell", "decimals": 18}
        }
    }
    helper.dex_configs = { # Minimal structure
        "test_buy_net": {"test_dex_buy": {"router_address": "0xRouterBuy"}},
        "test_sell_net": {"test_dex_sell": {"router_address": "0xRouterSell"}}
    }
    return helper


@pytest.mark.asyncio
async def test_execute_arbitrage_buy_leg_calculations(l2_arbitrage_helper_fixture):
    helper = l2_arbitrage_helper_fixture

    opportunity = {
        "buy_network": "test_buy_net",
        "sell_network": "test_sell_net",
        "token_to_trade_symbol": "WETH",
        "reference_token_symbol": "USDC",
        "buy_price_in_ref": Decimal("2000.0"),  # 1 WETH = 2000 USDC
        "sell_price_in_ref": Decimal("2020.0"), # Not used for buy leg calc but good for context
        "buy_dex_name": "test_dex_buy",
        "sell_dex_name": "test_dex_sell",
        "buy_dex_router_address": "0xRouterBuy",
        "sell_dex_router_address": "0xRouterSell",
        "reference_token_address_on_buy_network": "0xUSDCAddressBuy",
        "reference_token_decimals_on_buy_network": 6, # Overridden by helper.common_tokens
        "token_to_trade_address_on_buy_network": "0xWETHAddressBuy",
        "token_to_trade_decimals_on_buy_network": 18,   # Overridden by helper.common_tokens

        "reference_token_address_on_sell_network": "0xUSDCAddressSell",
        "reference_token_decimals_on_sell_network": 6,
        "token_to_trade_address_on_sell_network": "0xWETHAddressSell",
        "token_to_trade_decimals_on_sell_network": 18,
        "potential_net_profit_usd": Decimal("10.0"), # Example
        "description": "Test WETH/USDC Arbitrage Opportunity"
    }

    # Ensure the mock for execute_dex_swap is correctly associated with the helper's l2_manager instance
    # The fixture mock_l2_manager_for_helper already sets execute_dex_swap as an AsyncMock.

    # Call the method under test
    await helper._execute_arbitrage_trade(opportunity)

    # Assert that l2_manager.execute_dex_swap was called for the BUY leg
    helper.l2_manager.execute_dex_swap.assert_any_call(
        network_name="test_buy_net",
        dex_router_address="0xRouterBuy",
        from_token_address="0xUSDCAddressBuy",
        to_token_address="0xWETHAddressBuy",
        amount_in_wei=int(Decimal("100.0") * (10**6)),  # 100 USDC with 6 decimals
        min_amount_out_wei=int(Decimal("0.05") * (Decimal("1") - Decimal("0.01")) * (10**18)), # Expected: (100/2000) * 0.99 * 10^18
        wallet_address="0xTestWalletAddress",
        private_key="0xTestPrivateKeyToPassInitCheck"
    )

    # Check if it was called once for buy and once for sell (assuming buy was successful)
    # If execute_dex_swap is mocked to return a truthy value (like the default "0xmock_buy_tx_hash"),
    # it should proceed to the sell leg.
    assert helper.l2_manager.execute_dex_swap.call_count == 2 # Buy and Sell

    # Optionally, capture args for more detailed assertions if needed:
    buy_call_args = helper.l2_manager.execute_dex_swap.call_args_list[0]

    expected_amount_in_wei_buy = 100 * (10**6) # 100 USDC (6 decimals)

    expected_weth_out_decimal = Decimal("100.0") / Decimal("2000.0") # 0.05 WETH
    min_weth_out_decimal = expected_weth_out_decimal * (Decimal("1.0") - Decimal("0.01")) # 0.0495 WETH
    expected_min_amount_out_wei_buy = int(min_weth_out_decimal * (10**18)) # WETH (18 decimals)

    assert buy_call_args.kwargs['amount_in_wei'] == expected_amount_in_wei_buy
    assert buy_call_args.kwargs['min_amount_out_wei'] == expected_min_amount_out_wei_buy
    assert buy_call_args.kwargs['network_name'] == "test_buy_net"
    assert buy_call_args.kwargs['dex_router_address'] == "0xRouterBuy"
    assert buy_call_args.kwargs['from_token_address'] == "0xUSDCAddressBuy"
    assert buy_call_args.kwargs['to_token_address'] == "0xWETHAddressBuy"
    assert buy_call_args.kwargs['wallet_address'] == "0xTestWalletAddress"
