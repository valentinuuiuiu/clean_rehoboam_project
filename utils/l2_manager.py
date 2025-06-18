"""
Consolidated Layer 2 Management Utilities.

This module provides classes and functions to assist with managing
Layer 2 smart contract deployments, interactions, and other related tasks,
primarily leveraging tools like Foundry's forge and web3.py.
"""
import subprocess
import os
import logging
import re
import time # For price cache
from typing import Optional, Dict, List, Tuple, Any
from decimal import Decimal, ROUND_DOWN

# Assuming network_config.py is in the same directory or accessible in PYTHONPATH
try:
    from .network_config import NetworkConfig # Relative import if in the same package
    from .layer2_trading import Layer2GasEstimator
    from .web3_service import web3_service
    from .web_data import WebDataFetcher # For price oracle in arbitrage helper
except ImportError:
    import network_config # type: ignore
    network_config.NetworkConfig

    class MockLayer2GasEstimator:
        def __init__(self, network_config_instance=None):
            self.logger = logging.getLogger(__name__ + ".MockLayer2GasEstimator")
            self.logger.info("Using MockLayer2GasEstimator.")
        def get_gas_price(self, network_name: str) -> Optional[Dict[str, Any]]:
            self.logger.info(f"Mock: get_gas_price for {network_name}")
            if "sepolia" in network_name.lower() or "arbitrum" in network_name.lower() or "polygon" in network_name.lower():
                return {
                    "standard": {"maxFeePerGas": Decimal("20"), "maxPriorityFeePerGas": Decimal("1")},
                    "fast": {"maxFeePerGas": Decimal("30"), "maxPriorityFeePerGas": Decimal("2")},
                    "usd_price_eth": Decimal("2000.00") # Updated example ETH price
                }
            return None
        def estimate_transaction_cost(self, network_name: str, gas_units: int = 21000, gas_price_gwei: Optional[Decimal] = None) -> Optional[Dict[str, Any]]:
            gas_price_info = self.get_gas_price(network_name)
            if gas_price_info and gas_price_info.get('standard'):
                price_gwei = gas_price_gwei if gas_price_gwei else gas_price_info['standard']['maxFeePerGas']
                cost_native = (price_gwei * Decimal(gas_units)) / Decimal("1e9")
                cost_usd = cost_native * gas_price_info['usd_price_eth']
                return {"cost_native": cost_native, "cost_usd": cost_usd, "gas_price_gwei": price_gwei, "native_currency_usd_price": gas_price_info['usd_price_eth']}
            return None

    class MockWeb3Service:
        def __init__(self):
            self.logger = logging.getLogger(__name__ + ".MockWeb3Service")
            self.logger.info("Using MockWeb3Service.")
        def get_balance(self, address: str, chain_id: int) -> Optional[Decimal]: return Decimal("1.23")
        def read_contract(self, chain_id: int, contract_address: str, abi: List[Dict], function_name: str, *args) -> Optional[Any]: return "MockReadResult"
        def send_transaction(self, chain_id: int, from_address: str, to_address: str, private_key: str, value: Decimal = Decimal(0), data: Optional[str] = None, gas_limit: Optional[int] = None, max_fee_per_gas: Optional[Decimal] = None, max_priority_fee_per_gas: Optional[Decimal] = None) -> Optional[str]: return f"0xmocktxhash{time.time_ns()}"

    class MockWebDataFetcher:
        def __init__(self):
            self.logger = logging.getLogger(__name__ + ".MockWebDataFetcher")
            self.logger.info("Using MockWebDataFetcher.")
        async def get_crypto_prices(self, symbols: List[str], vs_currency: str = 'usd') -> Dict[str, Optional[float]]:
            prices = {}
            base_prices = {"WETH": 2000.0, "USDC": 1.0, "WBTC": 30000.0, "MATIC": 0.7}
            for symbol_key in symbols: # Changed variable name to avoid conflict
                prices[symbol_key.upper()] = base_prices.get(symbol_key.upper(), None)
            return prices

    Layer2GasEstimator = MockLayer2GasEstimator # type: ignore
    web3_service = MockWeb3Service() # type: ignore
    WebDataFetcher = MockWebDataFetcher # type: ignore
    # --- End Mock implementations ---

class L2ArbitrageHelper: # Forward declaration was here, actual class below
    pass

class L2Manager:
    def __init__(self, network_config_instance: NetworkConfig, web3_service_instance: Any = web3_service):
        self.network_config = network_config_instance
        self.logger = logging.getLogger(__name__ + ".L2Manager")
        if not self.logger.handlers:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.gas_estimator = Layer2GasEstimator(network_config_instance=self.network_config)
        self.web3_service = web3_service_instance
        self.arbitrage_helper = L2ArbitrageHelper(self.network_config, self)

    def _execute_command(self, command: List[str], cwd: Optional[str] = None) -> Tuple[bool, str, str]:
        self.logger.info(f"Executing command: {' '.join(command)}{f' in {cwd}' if cwd else ''}")
        try:
            process = subprocess.run(command, capture_output=True, text=True, check=False, cwd=cwd)
            if process.stdout: self.logger.debug(f"Stdout:\n{process.stdout}")
            if process.stderr: self.logger.debug(f"Stderr:\n{process.stderr}")
            if process.returncode == 0:
                self.logger.info("Command executed successfully.")
                return True, process.stdout, process.stderr
            else:
                self.logger.error(f"Command failed with return code {process.returncode}.\nStderr:\n{process.stderr}")
                return False, process.stdout, process.stderr
        except FileNotFoundError:
            self.logger.error(f"Command not found: {command[0]}. Ensure it's in PATH.")
            return False, "", f"Command not found: {command[0]}"
        except Exception as e:
            self.logger.error(f"Exception executing command: {' '.join(command)}. Error: {e}")
            return False, "", str(e)

    def build_contracts(self, contracts_dir: str = "contracts") -> bool:
        self.logger.info(f"Attempting to build contracts in directory: {contracts_dir}")
        command = ["forge", "build"]
        success, _, _ = self._execute_command(command, cwd=contracts_dir)
        if success: self.logger.info("Contracts built successfully.")
        else: self.logger.error("Contract build failed.")
        return success

    def deploy_contract(
        self, contract_script_path: str, network_name: str, deployer_private_key: str,
        etherscan_api_key: Optional[str] = None, broadcast: bool = True, verify: bool = False,
        constructor_args_str: Optional[str] = None
    ) -> Optional[str]:
        self.logger.info(f"Attempting to deploy contract from script '{contract_script_path}' to network '{network_name}'.")
        network_details = self.network_config.get_network(network_name)
        if not network_details:
            self.logger.error(f"Network '{network_name}' not found in configuration.")
            return None
        rpc_url, chain_id = network_details.get("rpc_url"), network_details.get("chain_id")
        if not rpc_url:
            self.logger.error(f"RPC URL for network '{network_name}' not found.")
            return None

        command = ["forge", "script", contract_script_path, "--rpc-url", rpc_url, "--private-key", deployer_private_key]
        if constructor_args_str: command.extend(constructor_args_str.split(' '))
        if broadcast: command.append("--broadcast")
        if verify:
            if etherscan_api_key and chain_id:
                command.extend(["--verify", "--etherscan-api-key", etherscan_api_key, "--chain-id", str(chain_id)])
            else:
                self.logger.warning("Verification requested but Etherscan API key or Chain ID missing. Skipping.")

        success, stdout, _ = self._execute_command(command, cwd=None)
        if not success:
            self.logger.error("Contract deployment script execution failed.")
            return None

        match = re.search(r"(?:Contract deployed at:|Deployed to:)\s*(0x[a-fA-F0-9]{40})", stdout)
        if match:
            contract_address = match.group(1)
            self.logger.info(f"Successfully deployed contract. Address: {contract_address}")
            return contract_address
        else:
            self.logger.warning("Could not find specific deployment message. Searching for any 0x address.")
            fallback_match = re.search(r"(0x[a-fA-F0-9]{40})", stdout)
            if fallback_match:
                contract_address = fallback_match.group(1)
                self.logger.info(f"Found potential contract address (fallback): {contract_address}")
                return contract_address
        self.logger.error("Could not parse deployed contract address from script output.")
        self.logger.debug(f"Full stdout for parsing attempt:\n{stdout}")
        return None

    def get_l2_gas_price(self, network_name: str) -> Optional[Dict[str, Any]]:
        self.logger.info(f"Fetching gas price for L2 network: {network_name}")
        try:
            gas_price_info = self.gas_estimator.get_gas_price(network_name)
            if gas_price_info:
                self.logger.info(f"Gas price for {network_name}: {gas_price_info}")
                return gas_price_info
            else:
                self.logger.warning(f"Could not retrieve gas price for {network_name}.")
                return None
        except Exception as e:
            self.logger.error(f"Error getting gas price for {network_name}: {e}")
            return None

    def get_l2_balance(self, network_name: str, address: str) -> Optional[Decimal]:
        self.logger.info(f"Fetching balance for address {address} on L2 network {network_name}.")
        network_details = self.network_config.get_network(network_name)
        if not network_details or "chain_id" not in network_details:
            self.logger.error(f"Chain ID for network '{network_name}' not found in configuration.")
            return None
        chain_id = network_details["chain_id"]
        try:
            balance = self.web3_service.get_balance(address, chain_id)
            if balance is not None: self.logger.info(f"Balance for {address} on {network_name}: {balance}")
            return balance
        except Exception as e:
            self.logger.error(f"Error getting balance for {address} on {network_name}: {e}")
            return None

    def estimate_l2_transaction_cost(self, network_name: str, gas_units: int = 21000) -> Optional[Dict[str, Any]]:
        self.logger.info(f"Estimating transaction cost for {gas_units} gas units on {network_name}.")
        gas_price_info = self.get_l2_gas_price(network_name)
        if not gas_price_info or 'standard' not in gas_price_info or 'usd_price_eth' not in gas_price_info:
            self.logger.error(f"Could not get sufficient gas price information for {network_name} to estimate cost.")
            return None
        try:
            gas_price_gwei = gas_price_info['standard']['maxFeePerGas']
            cost_native = (Decimal(str(gas_price_gwei)) * Decimal(str(gas_units))) / Decimal("1e9")
            usd_price_native = gas_price_info['usd_price_eth']
            cost_usd = cost_native * Decimal(str(usd_price_native))
            estimation = {"cost_native": cost_native, "cost_usd": cost_usd, "gas_price_gwei_used": gas_price_gwei, "native_currency_usd_price": usd_price_native}
            self.logger.info(f"Estimated cost on {network_name}: {estimation}")
            return estimation
        except Exception as e:
            self.logger.error(f"Error estimating transaction cost for {network_name}: {e}")
            return None

    def read_l2_contract(self, network_name: str, contract_address: str, contract_abi: List[Dict], function_name: str, *args) -> Optional[Any]:
        self.logger.info(f"Reading contract {contract_address} function {function_name} on {network_name} with args {args}.")
        network_details = self.network_config.get_network(network_name)
        if not network_details or "chain_id" not in network_details:
            self.logger.error(f"Chain ID for network '{network_name}' not found.")
            return None
        chain_id = network_details["chain_id"]
        try:
            result = self.web3_service.read_contract(chain_id, contract_address, contract_abi, function_name, *args)
            self.logger.info(f"Result from {function_name}: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Error reading contract {contract_address} on {network_name}: {e}")
            return None

    def send_l2_transaction(self, network_name: str, from_address: str, to_address: str, private_key: str, value: Decimal = Decimal("0"), data: Optional[str] = None, gas_limit: Optional[int] = None) -> Optional[str]:
        self.logger.info(f"Preparing to send transaction on {network_name} from {from_address} to {to_address}.")
        network_details = self.network_config.get_network(network_name)
        if not network_details or "chain_id" not in network_details:
            self.logger.error(f"Chain ID for network '{network_name}' not found.")
            return None
        chain_id = network_details["chain_id"]
        max_fee_per_gas, max_priority_fee_per_gas = None, None
        gas_price_info = self.get_l2_gas_price(network_name)
        if gas_price_info and 'standard' in gas_price_info:
            max_fee_per_gas = gas_price_info['standard'].get('maxFeePerGas')
            max_priority_fee_per_gas = gas_price_info['standard'].get('maxPriorityFeePerGas')
            self.logger.info(f"Using EIP-1559 gas prices for {network_name}: maxFee={max_fee_per_gas}, priorityFee={max_priority_fee_per_gas}")
        else:
            self.logger.warning(f"Could not fetch EIP-1559 gas prices for {network_name}. Tx might use provider defaults or fail.")
        try:
            tx_hash = self.web3_service.send_transaction(chain_id=chain_id, from_address=from_address, to_address=to_address, private_key=private_key, value=value, data=data, gas_limit=gas_limit, max_fee_per_gas=max_fee_per_gas, max_priority_fee_per_gas=max_priority_fee_per_gas)
            if tx_hash: self.logger.info(f"Transaction sent on {network_name}. Hash: {tx_hash}")
            return tx_hash
        except Exception as e:
            self.logger.error(f"Error sending transaction on {network_name}: {e}")
            return None

class L2ArbitrageHelper:
    def __init__(self, network_config_instance: NetworkConfig, l2_manager_instance: L2Manager):
        self.network_config = network_config_instance
        self.l2_manager = l2_manager_instance
        self.gas_estimator = l2_manager_instance.gas_estimator
        self.logger = logging.getLogger(__name__ + ".L2ArbitrageHelper")
        self.price_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_duration_seconds: int = 60
        self.min_profit_usd_threshold: Decimal = Decimal("1.0")
        self.dex_configs: Dict[str, List[Dict[str, str]]] = {
            "arbitrum_sepolia": [{"name": "ArbiSwap", "router_address": "0xArbiSwapRouter"}, {"name": "SushiSwapArb", "router_address": "0xSushiRouterArb"}],
            "optimism_kovan": [{"name": "OptiSwap", "router_address": "0xOptiSwapRouter"}, {"name": "UniV3Opti", "router_address": "0xUniV3RouterOpti"}],
            "polygon_mumbai": [{"name": "QuickSwapPoly", "router_address": "0xQuickSwapRouterPoly"}]
        }
        self.common_tokens: Dict[str, Dict[str, str]] = {
            "arbitrum_sepolia": {"WETH": "0xArbitrumWETHAddress", "USDC": "0xArbitrumUSDCAddress", "WBTC": "0xArbitrumWBTCAddress", "MATIC": "0xArbitrumMATICAddress"},
            "optimism_kovan": {"WETH": "0xOptimismWETHAddress", "USDC": "0xOptimismUSDCAddress"},
            "polygon_mumbai": {"WMATIC": "0xPolygonWMATICAddress", "USDC": "0xPolygonUSDCAddress", "WETH": "0xPolygonWETHAddress"}
        }
        self.price_fetcher = WebDataFetcher()

    async def get_real_dex_price(self, network_name: str, dex_name: str, token_in_symbol: str, token_out_symbol: str, amount_in: Decimal) -> Optional[Decimal]:
        self.logger.warning(f"SIMULATED PRICE: get_real_dex_price for {dex_name} on {network_name} ({amount_in} {token_in_symbol} -> {token_out_symbol}). This is NOT a real on-chain price. TODO: Implement actual DEX interaction.")
        base_prices = await self.price_fetcher.get_crypto_prices([token_in_symbol, token_out_symbol])
        price_in_usd = base_prices.get(token_in_symbol.upper())
        price_out_usd = base_prices.get(token_out_symbol.upper())
        if price_in_usd is None or price_out_usd is None:
            self.logger.error(f"Could not get base price for {token_in_symbol} or {token_out_symbol} for simulation.")
            return None
        simulated_rate = (Decimal(str(price_in_usd)) / Decimal(str(price_out_usd)))
        variation_factor = Decimal(str(1.0 - (abs(hash(dex_name + token_in_symbol + token_out_symbol)) % 100) / 5000.0))
        simulated_rate *= variation_factor
        if amount_in > Decimal("10"): simulated_rate *= Decimal("0.99")
        self.logger.debug(f"Simulated rate for {amount_in} {token_in_symbol} to {token_out_symbol} on {dex_name}: {simulated_rate}")
        return simulated_rate

    async def scan_opportunities_on_network(self, network_name: str, token_pairs: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        self.logger.info(f"Scanning for arbitrage opportunities on network: {network_name}")
        opportunities = []
        dexes_on_network = self.dex_configs.get(network_name, [])
        if len(dexes_on_network) < 2:
            self.logger.info(f"Not enough DEXes configured on {network_name} for intra-network arbitrage.")
            return opportunities
        probe_amount = Decimal("1.0")
        for token_a_symbol, token_b_symbol in token_pairs:
            for i in range(len(dexes_on_network)):
                for j in range(len(dexes_on_network)):
                    if i == j: continue
                    dex1, dex2 = dexes_on_network[i], dexes_on_network[j]
                    amount_a_from_dex1 = await self.get_real_dex_price(network_name, dex1['name'], token_b_symbol, token_a_symbol, probe_amount)
                    if not amount_a_from_dex1 or amount_a_from_dex1 <= 0: continue
                    rate_b_per_a_dex2 = await self.get_real_dex_price(network_name, dex2['name'], token_a_symbol, token_b_symbol, amount_a_from_dex1)
                    if not rate_b_per_a_dex2: continue
                    amount_b_final = amount_a_from_dex1 * rate_b_per_a_dex2
                    profit_b = amount_b_final - probe_amount
                    if profit_b > 0:
                        opportunity = {"type": "intra_network_arbitrage", "network": network_name, "buy_token": token_a_symbol, "sell_token": token_b_symbol, "dex_buy": dex1['name'], "dex_sell": dex2['name'], "amount_in_b": probe_amount, "amount_out_a_dex1": amount_a_from_dex1, "amount_out_b_dex2": amount_b_final, "potential_profit_b": profit_b, "description": f"Buy {token_a_symbol} with {token_b_symbol} on {dex1['name']}, sell {token_a_symbol} for {token_b_symbol} on {dex2['name']}"}
                        self.logger.info(f"Found potential opportunity: {opportunity['description']}, Profit: {profit_b} {token_b_symbol}")
                        opportunities.append(opportunity)
        return opportunities

    async def scan_multichain_opportunities(self, reference_token_symbol: str = 'USDC') -> List[Dict[str, Any]]:
        self.logger.info(f"Scanning for multichain L2 arbitrage opportunities against {reference_token_symbol}.")
        opportunities = []
        network_token_prices: Dict[str, Dict[str, Decimal]] = {}
        tokens_to_scan = set()
        for _network, token_map in self.common_tokens.items():
            for symbol_key in token_map.keys(): # Changed variable name
                if symbol_key.upper() != reference_token_symbol.upper(): tokens_to_scan.add(symbol_key)
        self.logger.debug(f"Tokens to scan across chains: {list(tokens_to_scan)}")

        for network_name, dex_list in self.dex_configs.items():
            if not dex_list: continue
            primary_dex = dex_list[0]
            network_token_prices[network_name] = {}
            for token_symbol in tokens_to_scan:
                if not self.common_tokens.get(network_name, {}).get(token_symbol) or not self.common_tokens.get(network_name, {}).get(reference_token_symbol):
                    self.logger.debug(f"Skipping {token_symbol}/{reference_token_symbol} on {network_name}: missing address.")
                    continue
                price = await self.get_real_dex_price(network_name, primary_dex['name'], token_symbol, reference_token_symbol, Decimal("1.0"))
                if price:
                    network_token_prices[network_name][token_symbol] = price
                    self.logger.info(f"Price on {network_name} ({primary_dex['name']}): 1 {token_symbol} = {price:.4f} {reference_token_symbol}")

        for token_symbol in tokens_to_scan:
            prices_for_token: List[Tuple[str, Decimal, str]] = []
            for network_name, token_price_map in network_token_prices.items():
                if token_symbol in token_price_map:
                    primary_dex_name = self.dex_configs.get(network_name, [{}])[0].get('name', 'UnknownDEX')
                    prices_for_token.append((network_name, token_price_map[token_symbol], primary_dex_name))
            if len(prices_for_token) < 2: continue
            prices_for_token.sort(key=lambda x: x[1])
            buy_network, buy_price, buy_dex = prices_for_token[0]
            sell_network, sell_price, sell_dex = prices_for_token[-1]
            if buy_network == sell_network or sell_price <= buy_price: continue
            gross_profit_ref = sell_price - buy_price
            gas_cost_buy_tx_usd, gas_cost_sell_tx_usd = Decimal("0.50"), Decimal("0.50")
            cost_estimation_buy = self.l2_manager.estimate_l2_transaction_cost(buy_network, gas_units=150000)
            if cost_estimation_buy: gas_cost_buy_tx_usd = cost_estimation_buy['cost_usd']
            cost_estimation_sell = self.l2_manager.estimate_l2_transaction_cost(sell_network, gas_units=150000)
            if cost_estimation_sell: gas_cost_sell_tx_usd = cost_estimation_sell['cost_usd']

            # Mock bridge cost estimation
            bridge_cost_details = self.network_config.estimate_bridging_costs(buy_network, sell_network, 1.0, token_symbol)
            bridge_cost_usd = bridge_cost_details.get("cost_usd", Decimal("1.00")) # Default if mock fails

            total_costs_usd = gas_cost_buy_tx_usd + gas_cost_sell_tx_usd + bridge_cost_usd
            net_profit_usd = gross_profit_ref - total_costs_usd
            if net_profit_usd > self.min_profit_usd_threshold:
                opportunity = {"type": "cross_l2_arbitrage", "token_to_trade": token_symbol, "reference_token": reference_token_symbol, "buy_network": buy_network, "buy_dex": buy_dex, "buy_price_in_ref": buy_price, "sell_network": sell_network, "sell_dex": sell_dex, "sell_price_in_ref": sell_price, "estimated_gas_cost_buy_usd": gas_cost_buy_tx_usd, "estimated_gas_cost_sell_usd": gas_cost_sell_tx_usd, "estimated_bridge_cost_usd": bridge_cost_usd, "potential_net_profit_usd": net_profit_usd, "description": f"Buy {token_symbol} on {buy_network} ({buy_dex}) at ~{buy_price:.4f} {reference_token_symbol}, bridge, sell on {sell_network} ({sell_dex}) at ~{sell_price:.4f} {reference_token_symbol}. Est. Net Profit: ${net_profit_usd:.2f}"}
                self.logger.info(f"Found cross-L2 opportunity: {opportunity['description']}")
                opportunities.append(opportunity)
        return opportunities

if __name__ == '__main__':
    import asyncio # Ensure asyncio is imported for the example run
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    class ExampleNetworkConfig:
        def get_network(self, network_name_query: str) -> Optional[Dict[str, Any]]:
            networks = {
                "arbitrum_sepolia": {"name": "Arbitrum Sepolia", "chain_id": 421614, "rpc_url": os.getenv("ARBITRUM_SEPOLIA_RPC_URL", "https://sepolia-rollup.arbitrum.io/rpc"), "currency": "ETH", "type": "L2_Testnet"},
                "optimism_kovan": {"name": "Optimism Kovan", "chain_id": 69, "rpc_url": "https://kovan.optimism.io", "currency": "ETH", "type": "L2_Testnet"},
                "polygon_mumbai": {"name": "Polygon Mumbai", "chain_id": 80001, "rpc_url": "https://rpc-mumbai.maticvigil.com", "currency": "MATIC", "type": "L2_Testnet"},
                "sepolia_test": {"name": "Sepolia Testnet", "chain_id": 11155111, "rpc_url": os.getenv("RPC_URL_SEPOLIA"), "currency": "ETH", "type": "L1_Testnet"}
            }
            return networks.get(network_name_query)
        def get_all_networks(self) -> List[Dict[str, Any]]: return []
        def compare_networks(self, token: str) -> List[Dict[str, Any]]: return []
        def estimate_bridging_costs(self, from_network: str, to_network: str, amount: float, token_symbol: str = "ETH") -> Dict[str, Any]:
            self.logger = logging.getLogger(__name__ + ".ExampleNetworkConfig") # Ensure logger is available if used
            self.logger.info(f"Mock: estimate_bridging_costs from {from_network} to {to_network} for {amount} {token_symbol}")
            return {"cost_usd": Decimal("1.50"), "duration_seconds": 600}

    nc_instance = ExampleNetworkConfig()
    l2_manager = L2Manager(network_config_instance=nc_instance, web3_service_instance=web3_service)

    logger.info("--- L2Manager & L2ArbitrageHelper Examples ---")
    arbitrage_helper = l2_manager.arbitrage_helper

    async def run_arbitrage_scans():
        logger.info("\n--- Example: Scan Intra-Network Arbitrage (Arbitrum Sepolia) ---")
        arb_pairs = [("WETH", "USDC"), ("WBTC", "WETH")]
        arb_ops = await arbitrage_helper.scan_opportunities_on_network("arbitrum_sepolia", arb_pairs)
        if arb_ops:
            for op in arb_ops: logger.info(f"Arbitrum Opp: {op['description']}")
        else:
            logger.info("No intra-Arbitrum arbitrage opportunities found in this scan.")

        logger.info("\n--- Example: Scan Multi-Chain L2 Arbitrage (vs USDC) ---")
        multichain_ops = await arbitrage_helper.scan_multichain_opportunities(reference_token_symbol="USDC")
        if multichain_ops:
            for op in multichain_ops: logger.info(f"Multichain Opp: {op['description']}")
        else:
            logger.info("No multi-chain L2 arbitrage opportunities found in this scan.")

    asyncio.run(run_arbitrage_scans())

    logger.info("\nL2Manager & L2ArbitrageHelper examples complete.")
    pass
# Removed duplicate [end of utils/l2_manager.py]
