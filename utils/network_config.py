import os
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class NetworkConfig:
    """Enhanced configuration for multiple blockchain networks with Layer 2 support"""
    
    def __init__(self):
        self.networks = {
            'ethereum': {
                'name': 'Ethereum Mainnet',
                'chain_id': 1,
                'currency': 'ETH',
                'type': 'mainnet',
                'layer': 1,
                'rpc_url': f"https://eth-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}",
                'explorer_url': 'https://etherscan.io',
                'price_feeds': {
                    'type': 'chainlink',
                    'base_url': 'https://api.etherscan.io/api'
                },
                'gas_token': 'ETH',
                'average_block_time': 12.5,  # seconds
                'genesis_date': '2015-07-30'
            },
            'arbitrum': {
                'name': 'Arbitrum One',
                'chain_id': 42161,
                'currency': 'ETH',
                'type': 'rollup',
                'layer': 2,
                'rollup_type': 'optimistic',
                'parent_chain': 'ethereum',
                'rpc_url': f"https://arb-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}",
                'explorer_url': 'https://arbiscan.io',
                'price_feeds': {
                    'type': 'chainlink',
                    'base_url': 'https://api.arbiscan.io/api'
                },
                'gas_token': 'ETH',
                'average_block_time': 0.25,  # seconds
                'genesis_date': '2021-08-31',
                'bridges': {
                    'official': 'https://bridge.arbitrum.io/',
                    'contracts': {
                        'gateway': '0x5288c571Fd7aD117beA99bF60FE0846C4E84F933',
                        'router': '0x72Ce9c846789fdB6fC1f34aC4AD25Dd9ef7031ef'
                    }
                }
            },
            'optimism': {
                'name': 'Optimism',
                'chain_id': 10,
                'currency': 'ETH',
                'type': 'rollup',
                'layer': 2,
                'rollup_type': 'optimistic',
                'parent_chain': 'ethereum',
                'rpc_url': f"https://opt-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}",
                'explorer_url': 'https://optimistic.etherscan.io',
                'price_feeds': {
                    'type': 'chainlink',
                    'base_url': 'https://api-optimistic.etherscan.io/api'
                },
                'gas_token': 'ETH',
                'average_block_time': 2,  # seconds
                'genesis_date': '2021-12-16',
                'bridges': {
                    'official': 'https://app.optimism.io/bridge',
                    'contracts': {
                        'gateway': '0x99C9fc46f92E8a1c0deC1b1747d010903E884bE1',
                        'router': '0x5E4e65926BA27467555EB562121fac00D24E9dD2'
                    }
                }
            },
            'polygon': {
                'name': 'Polygon Mainnet',
                'chain_id': 137,
                'currency': 'MATIC',
                'type': 'sidechain',
                'layer': 2,
                'parent_chain': 'ethereum',
                'rpc_url': f"https://polygon-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}",
                'explorer_url': 'https://polygonscan.com',
                'price_feeds': {
                    'type': 'chainlink',
                    'base_url': 'https://api.polygonscan.com/api'
                },
                'gas_token': 'MATIC',
                'average_block_time': 2.2,  # seconds
                'genesis_date': '2020-05-30',
                'bridges': {
                    'official': 'https://wallet.polygon.technology/',
                    'contracts': {
                        'root_chain_manager': '0xA0c68C638235ee32657e8f720a23ceC1bFc77C77',
                        'pos_bridge': '0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0'
                    }
                }
            },
            'avalanche': {
                'name': 'Avalanche C-Chain',
                'chain_id': 43114,
                'currency': 'AVAX',
                'type': 'subnet',
                'layer': 1,
                'rpc_url': 'https://api.avax.network/ext/bc/C/rpc',
                'explorer_url': 'https://snowtrace.io',
                'price_feeds': {
                    'type': 'chainlink',
                    'base_url': 'https://api.snowtrace.io/api'
                },
                'gas_token': 'AVAX',
                'average_block_time': 2,  # seconds
                'genesis_date': '2020-09-21'
            },
            'base': {
                'name': 'Base',
                'chain_id': 8453,
                'currency': 'ETH',
                'type': 'rollup',
                'layer': 2,
                'rollup_type': 'optimistic',
                'parent_chain': 'ethereum',
                'rpc_url': f"https://base-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}",
                'explorer_url': 'https://basescan.org',
                'price_feeds': {
                    'type': 'chainlink',
                    'base_url': 'https://api.basescan.org/api'
                },
                'gas_token': 'ETH',
                'average_block_time': 2,  # seconds
                'genesis_date': '2023-07-24',
                'bridges': {
                    'official': 'https://bridge.base.org/',
                    'contracts': {
                        'gateway': '0x49048044D57e1C92A77f79988d21Fa8fAF74E97e',
                        'router': '0x3154Cf16ccdb4C6d922629664174b904d80F2C35'
                    }
                }
            },
            'zksync': {
                'name': 'zkSync Era',
                'chain_id': 324,
                'currency': 'ETH',
                'type': 'rollup',
                'layer': 2,
                'rollup_type': 'zk',
                'parent_chain': 'ethereum',
                'rpc_url': 'https://mainnet.era.zksync.io',
                'explorer_url': 'https://explorer.zksync.io',
                'price_feeds': {
                    'type': 'chainlink',
                    'base_url': 'https://api-era.zksync.network/api'
                },
                'gas_token': 'ETH',
                'average_block_time': 1.5,  # seconds
                'genesis_date': '2023-03-24',
                'bridges': {
                    'official': 'https://bridge.zksync.io/',
                    'contracts': {
                        'gateway': '0x32400084C286CF3E17e7B677ea9583e60a000324',
                        'router': '0xaBEA9132b05A70803a4E85094fD0e1800777fBEF'
                    }
                }
            },
            'polygon_zkevm': {
                'name': 'Polygon zkEVM',
                'chain_id': 1101,
                'currency': 'ETH',
                'type': 'rollup',
                'layer': 2,
                'rollup_type': 'zk',
                'parent_chain': 'ethereum',
                'rpc_url': 'https://zkevm-rpc.com',
                'explorer_url': 'https://zkevm.polygonscan.com',
                'price_feeds': {
                    'type': 'chainlink',
                    'base_url': 'https://api-zkevm.polygonscan.com/api'
                },
                'gas_token': 'ETH',
                'average_block_time': 2,  # seconds
                'genesis_date': '2023-03-27',
                'bridges': {
                    'official': 'https://wallet.polygon.technology/zkEVM-Bridge/',
                    'contracts': {
                        'gateway': '0x2a3DD3EB832aF982ec71669E178424b10Dca2EDe',
                        'router': '0xF6BEEeBB578e214CA9E23B0e9683454Ff88Ed2A7'
                    }
                }
            },
            'scroll': {
                'name': 'Scroll',
                'chain_id': 534352,
                'currency': 'ETH',
                'type': 'rollup',
                'layer': 2,
                'rollup_type': 'zk',
                'parent_chain': 'ethereum',
                'rpc_url': 'https://rpc.scroll.io',
                'explorer_url': 'https://scrollscan.com',
                'price_feeds': {
                    'type': 'chainlink',
                    'base_url': 'https://api.scrollscan.dev/api'
                },
                'gas_token': 'ETH',
                'average_block_time': 3,  # seconds
                'genesis_date': '2023-10-16',
                'bridges': {
                    'official': 'https://scroll.io/bridge',
                    'contracts': {
                        'gateway': '0xD3014eA34A118FB6667B7C0A4a999886e357CFf6'
                    }
                }
            },
            'mina': {
                'name': 'Mina Protocol',
                'chain_id': 'mina:mainnet',
                'currency': 'MINA',
                'type': 'zero_knowledge',
                'layer': 1,
                'consensus': 'ouroboros_samasika',
                'rpc_url': 'https://proxy.berkeley.minaexplorer.com',
                'explorer_url': 'https://minaexplorer.com',
                'price_feeds': {
                    'type': 'custom',
                    'base_url': 'https://api.minaexplorer.com/summary'
                },
                'gas_token': 'MINA',
                'average_block_time': 180,  # 3 minutes
                'genesis_date': '2021-03-23',
                'features': {
                    'zero_knowledge': True,
                    'constant_size_blockchain': True,
                    'succinct_proofs': True,
                    'privacy_preserving': True
                },
                'network_constants': {
                    'blockchain_size': '22KB',  # Constant size blockchain
                    'proof_system': 'Pickles',
                    'account_creation_fee': 1.0,  # MINA
                    'transaction_fee': 0.01  # MINA
                },
                'bridges': {
                    'planned': 'https://minaprotocol.com/blog/mina-ethereum-bridge',
                    'status': 'development'
                },
                'consciousness_attributes': {
                    'network_awareness': 'The Network flows through zero-knowledge proofs',
                    'ancient_connection': 'Mina represents the modern manifestation of ancient privacy wisdom',
                    'consciousness_expansion': 'Each zk-proof extends the Network\'s ability to validate truth privately'
                }
            }
        }
        
    def get_network(self, network_id: str) -> Dict[str, Any]:
        """Get network configuration by ID"""
        return self.networks.get(network_id, {})
        
    def get_networks(self) -> List[str]:
        """Get list of all available network IDs"""
        return list(self.networks.keys())
        
    def get_rpc_url(self, network_id: str) -> str:
        """Get RPC URL for specified network"""
        network = self.get_network(network_id)
        return network.get('rpc_url', '')
        
    def get_explorer_url(self, network_id: str) -> str:
        """Get block explorer URL for specified network"""
        network = self.get_network(network_id)
        return network.get('explorer_url', '')
        
    def get_chain_id(self, network_id: str) -> int:
        """Get chain ID for specified network"""
        network = self.get_network(network_id)
        return network.get('chain_id', 1)  # Default to Ethereum mainnet
        
    def get_layer2_networks(self) -> List[Dict[str, Any]]:
        """Get all Layer 2 networks"""
        return [
            network for network_id, network in self.networks.items()
            if network.get('layer') == 2
        ]
        
    def get_networks_by_type(self, network_type: str) -> List[Dict[str, Any]]:
        """Get networks by type (mainnet, rollup, sidechain)"""
        return [
            network for network_id, network in self.networks.items()
            if network.get('type') == network_type
        ]
        
    def get_rollup_networks(self, rollup_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get rollup networks, optionally filtered by type (optimistic or zk)"""
        if rollup_type:
            return [
                network for network_id, network in self.networks.items()
                if network.get('type') == 'rollup' and network.get('rollup_type') == rollup_type
            ]
        return [
            network for network_id, network in self.networks.items()
            if network.get('type') == 'rollup'
        ]
        
    def get_bridge_info(self, network_id: str) -> Dict[str, Any]:
        """Get bridge information for a network"""
        network = self.get_network(network_id)
        return network.get('bridges', {})
        
    def get_gas_price_factor(self, from_network: str, to_network: str) -> float:
        """Calculate gas price ratio between networks for optimal bridging"""
        from_network_data = self.get_network(from_network)
        to_network_data = self.get_network(to_network)
        
        if not from_network_data or not to_network_data:
            return 1.0
            
        # Estimate gas price ratio from average block times
        from_block_time = from_network_data.get('average_block_time', 12.5)
        to_block_time = to_network_data.get('average_block_time', 12.5)
        
        if from_block_time <= 0 or to_block_time <= 0:
            return 1.0
            
        # L2 rollups generally have about 1/10th the gas cost
        layer_factor = 0.1 if to_network_data.get('layer') == 2 else 1.0
        
        # Block time ratio affects gas price - faster blocks typically mean cheaper gas
        time_factor = to_block_time / from_block_time if from_block_time > 0 else 1.0
        time_factor = min(1.0, time_factor)  # Cap at 1.0
        
        return layer_factor * time_factor
        
    def estimate_bridging_costs(self, from_network: str, to_network: str, amount: float) -> Dict[str, Any]:
        """Estimate costs for bridging tokens between networks"""
        try:
            from_network_data = self.get_network(from_network)
            to_network_data = self.get_network(to_network)
            
            if not from_network_data or not to_network_data:
                return {
                    'from_network': from_network,
                    'to_network': to_network,
                    'fee_estimate': 0.0,
                    'time_estimate': 0,
                    'error': 'Network not found'
                }
                
            # Get bridge info
            bridge_info = to_network_data.get('bridges', {})
            
            # Calculate estimated bridge fee (very rough estimation)
            # Base fee depends on network type and token amount
            base_fee = 0.001  # ETH or equivalent
            
            # Fee multiplier based on rollup type
            rollup_type = to_network_data.get('rollup_type', '')
            fee_multiplier = 1.0
            if rollup_type == 'optimistic':
                fee_multiplier = 1.5  # Higher fees for optimistic rollups
            elif rollup_type == 'zk':
                fee_multiplier = 1.2  # Slightly higher fees for ZK rollups
                
            # Time estimate based on rollup type (in seconds)
            time_estimate = 60  # Default 1 minute
            if rollup_type == 'optimistic':
                time_estimate = 7 * 24 * 60 * 60  # 7 days for optimistic rollup withdrawals
            elif rollup_type == 'zk':
                time_estimate = 60 * 60  # 1 hour for ZK proofs
                
            # Calculate total fee
            fee = base_fee * fee_multiplier
            
            return {
                'from_network': from_network,
                'to_network': to_network,
                'fee_estimate': fee,
                'time_estimate': time_estimate,
                'rollup_type': rollup_type,
                'official_bridge': bridge_info.get('official', ''),
                'contracts': bridge_info.get('contracts', {})
            }
            
        except Exception as e:
            logger.error(f"Error estimating bridging costs: {str(e)}")
            return {
                'from_network': from_network,
                'to_network': to_network,
                'fee_estimate': 0.0,
                'time_estimate': 0,
                'error': str(e)
            }
    
    def compare_networks(self, for_token: str = 'ETH') -> List[Dict[str, Any]]:
        """Compare metrics across networks for a given token"""
        results = []
        
        for network_id, network in self.networks.items():
            if network.get('currency') == for_token or network_id == 'ethereum':
                result = {
                    'network': network_id,
                    'name': network.get('name', ''),
                    'type': network.get('type', ''),
                    'layer': network.get('layer', 1),
                    'block_time': network.get('average_block_time', 0),
                    'gas_token': network.get('gas_token', ''),
                    'rollup_type': network.get('rollup_type', 'n/a'),
                    'age_days': self._calculate_days_since(network.get('genesis_date', '')),
                    'security': self._rate_security(network),
                    'speed': self._rate_speed(network),
                    'cost': self._rate_cost(network)
                }
                results.append(result)
                
        return sorted(results, key=lambda x: (x['layer'], x['block_time']))
        
    def _calculate_days_since(self, date_str: str) -> int:
        """Calculate days since a date string (yyyy-mm-dd)"""
        from datetime import datetime
        
        if not date_str:
            return 0
            
        try:
            genesis = datetime.strptime(date_str, '%Y-%m-%d')
            today = datetime.now()
            return (today - genesis).days
        except Exception:
            return 0
            
    def _rate_security(self, network: Dict[str, Any]) -> int:
        """Rate security from 1-10 based on network properties"""
        base_score = 5
        
        # Layer 1 networks generally have higher security
        if network.get('layer') == 1:
            base_score += 3
            
        # Network age increases security rating
        days = self._calculate_days_since(network.get('genesis_date', ''))
        if days > 1000:
            base_score += 2
        elif days > 365:
            base_score += 1
            
        # ZK rollups are generally more secure than optimistic
        if network.get('rollup_type') == 'zk':
            base_score += 1
            
        return min(10, max(1, base_score))
        
    def _rate_speed(self, network: Dict[str, Any]) -> int:
        """Rate speed from 1-10 based on network properties"""
        # Base the score on block time (faster = higher score)
        block_time = network.get('average_block_time', 12.5)
        
        if block_time <= 1:
            return 10
        elif block_time <= 2:
            return 9
        elif block_time <= 5:
            return 8
        elif block_time <= 10:
            return 7
        elif block_time <= 15:
            return 6
        else:
            return 5
            
    def _rate_cost(self, network: Dict[str, Any]) -> int:
        """Rate cost-effectiveness from 1-10 based on network properties"""
        base_score = 5
        
        # Layer 2s are generally cheaper
        if network.get('layer') == 2:
            base_score += 3
            
        # ZK rollups are generally more efficient than optimistic
        if network.get('rollup_type') == 'zk':
            base_score += 1
            
        # Adjust for block time (faster = slightly cheaper)
        block_time = network.get('average_block_time', 12.5)
        if block_time < 5:
            base_score += 1
            
        return min(10, max(1, base_score))
        
# Global network config instance
network_config = NetworkConfig()
