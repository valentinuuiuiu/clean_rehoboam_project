"""WebSocket server with enhanced connection management and monitoring."""
import asyncio
from datetime import datetime
from fastapi import WebSocket
from utils.connection_manager import ConnectionManager
from prometheus_client import Counter, Gauge, Histogram
from typing import Dict, Callable, Awaitable, Set, Optional, Any
import logging
import json

logger = logging.getLogger(__name__)

# Prometheus metrics
ws_connections = Gauge('ws_connections_total', 'Number of active WebSocket connections')
ws_messages = Counter('ws_messages_total', 'Number of WebSocket messages', ['channel'])
ws_errors = Counter('ws_errors_total', 'Number of WebSocket errors', ['type'])
ws_latency = Histogram('ws_message_latency_seconds', 'WebSocket message latency')

class EnhancedWebSocketServer:
    """Enhanced WebSocket server with connection management and monitoring."""
    def __init__(self):
        self._running = False
        # Use an instance of ConnectionManager to handle WebSocket connections
        self.connection_manager = ConnectionManager()
        self.metrics = {
            'connections': 0,
            'messages_processed': 0,
            'errors': 0
        }

    async def initialize(self):
        """Initialize the websocket server and register handlers"""
        await self.connection_manager.register_handler('market', self._handle_market_data)
        await self.connection_manager.register_handler('trades', self._handle_trade_updates)
        await self.connection_manager.register_handler('portfolio', self._handle_portfolio_updates)
        await self.connection_manager.register_handler('emotions', self._handle_emotion_updates)
        await self.connection_manager.register_handler('strategies', self._handle_strategies_updates)
        await self._setup_monitoring()

    async def start(self):
        """Start the WebSocket server and connection manager."""
        await self.connection_manager.start()
        
    async def stop(self):
        """Stop the server and cleanup connections."""
        await self.connection_manager.stop()

    async def _setup_monitoring(self):
        """Set up monitoring and metrics collection"""
        self._running = True
        self.metrics = {
            'connections': 0,
            'messages_processed': 0,
            'errors': 0
        }
        
        # Start the price update task
        asyncio.create_task(self._price_update_task())
        
    async def _price_update_task(self):
        """Background task to send real-time price updates with AI trading insights."""
        import random
        from utils.web_data import WebDataFetcher
        from trading_agent import TradingAgent
        
        # Initialize web data fetcher and AI trading agent
        web_data = WebDataFetcher()
        
        # Create a trading agent with AI capabilities
        logger.info("Initializing AI Trading Agent for WebSocket server")
        try:
            ai_agent = TradingAgent()
            use_ai = True
            logger.info("AI Trading Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI Trading Agent: {str(e)}")
            use_ai = False
        
        # Trading pairs we want to broadcast
        trading_pairs = ['BTC', 'ETH', 'LINK', 'UMA', 'AAVE', 'XMR', 'SHIB']
        
        logger.info("Starting price update task with AI insights")
        
        while self._running:
            try:
                # Get real prices for all trading pairs
                price_data = {}
                
                for symbol in trading_pairs:
                    try:
                        # Get current price
                        price = web_data.get_crypto_price(symbol)
                        
                        # Get 24h change or simulate
                        try:
                            change_24h = web_data.get_24h_change(symbol)
                        except:
                            change_24h = random.uniform(-5.0, 8.0)
                        
                        # Generate some realistic data for high/low
                        variance = price * 0.02  # 2% variance
                        high_24h = price + (variance * 0.7)
                        low_24h = price - (variance * 0.5)
                        
                        # Get volume if available, otherwise simulate
                        try:
                            volume = web_data.get_24h_volume(symbol)
                        except:
                            # Simulate volume based on price
                            volume = price * 1000 * (0.8 + 0.4 * random.random())
                        
                        # Get AI insights if agent is available
                        ai_insights = None
                        if use_ai:
                            try:
                                # Get market analysis from AI
                                ai_analysis = ai_agent.analyze_market_with_rehoboam(symbol)
                                
                                # Create AI insights object
                                ai_insights = {
                                    'recommendation': ai_analysis.get('recommendation', 'hold'),
                                    'confidence': ai_analysis.get('confidence', 0.5),
                                    'sentiment': ai_analysis.get('metrics', {}).get('market_sentiment', 0),
                                    'volatility': ai_analysis.get('metrics', {}).get('volatility', 0.02),
                                    'trend_strength': ai_analysis.get('metrics', {}).get('trend_strength', 0.5),
                                    'prediction': ai_analysis.get('prediction', {})
                                }
                                
                                # If we have arbitrage data, include it
                                if symbol in ['ETH', 'LINK', 'USDC']:
                                    arbitrage_data = ai_agent.find_arbitrage_opportunities()
                                    token_arbitrage = [
                                        opp for opp in arbitrage_data 
                                        if opp.get('token') == symbol
                                    ]
                                    if token_arbitrage:
                                        ai_insights['arbitrage'] = token_arbitrage[0]
                            except Exception as e:
                                logger.error(f"Error getting AI insights for {symbol}: {str(e)}")
                        
                        # Get real Layer 2 network prices through our AI agent if available
                        networks = {}
                        if use_ai:
                            try:
                                # For real Layer 2 network data, we'd query each network
                                # For now, we'll use price variations for demonstration
                                layer2_optimizer = ai_agent.l2_optimizer
                                for network in ['ethereum', 'arbitrum', 'optimism', 'polygon', 'base', 'zksync']:
                                    network_price = price
                                    # Apply realistic price differences based on network
                                    if network != 'ethereum':
                                        network_price *= (0.993 + 0.014 * random.random())
                                    
                                    # Get gas prices for the network
                                    gas_price = ai_agent.get_gas_price(network)
                                    
                                    networks[network] = {
                                        'price': network_price,
                                        'gasPrice': gas_price,
                                        'liquidity': 'high' if network in ['ethereum', 'arbitrum', 'polygon'] else 'medium'
                                    }
                            except Exception as e:
                                logger.error(f"Error getting network data: {str(e)}")
                                # Fallback to simple calculation
                                networks = {
                                    'ethereum': {'price': price * (0.998 + 0.004 * random.random())},
                                    'arbitrum': {'price': price * (0.997 + 0.006 * random.random())},
                                    'optimism': {'price': price * (0.996 + 0.008 * random.random())},
                                    'polygon': {'price': price * (0.995 + 0.010 * random.random())},
                                    'base': {'price': price * (0.994 + 0.012 * random.random())},
                                    'zksync': {'price': price * (0.993 + 0.014 * random.random())}
                                }
                        else:
                            # Fallback to simple network simulation
                            networks = {
                                'ethereum': {'price': price * (0.998 + 0.004 * random.random())},
                                'arbitrum': {'price': price * (0.997 + 0.006 * random.random())},
                                'optimism': {'price': price * (0.996 + 0.008 * random.random())},
                                'polygon': {'price': price * (0.995 + 0.010 * random.random())},
                                'base': {'price': price * (0.994 + 0.012 * random.random())},
                                'zksync': {'price': price * (0.993 + 0.014 * random.random())}
                            }
                        
                        # Create price data entry with AI insights
                        price_data_entry = {
                            'price': price,
                            'change24h': change_24h,
                            'high24h': high_24h,
                            'low24h': low_24h,
                            'volume': volume,
                            'lastUpdate': datetime.now().isoformat(),
                            'networks': networks
                        }
                        
                        # Add AI insights if available
                        if ai_insights:
                            price_data_entry['ai'] = ai_insights
                        
                        # Add to price data
                        price_data[f"{symbol}USDT"] = price_data_entry
                        
                    except Exception as e:
                        logger.error(f"Error fetching price for {symbol}: {str(e)}")
                
                # Broadcast price data to all clients subscribed to market channel
                if price_data:
                    # Create market data message
                    market_message = {
                        'prices': price_data,
                        'timestamp': datetime.now().isoformat(),
                        'ai_enabled': use_ai
                    }
                    
                    # Broadcast to all clients subscribed to market channel
                    await self.broadcast_market_update(market_message)
                    logger.debug(f"Broadcasted price updates with AI insights for {len(price_data)} trading pairs")
                
            except Exception as e:
                logger.error(f"Error in price update task: {str(e)}")
            
            # Wait before sending next update
            await asyncio.sleep(2)  # 2-second update interval

    async def handle_client(self, websocket: WebSocket):
        """Handle new client connection."""
        client_id = str(id(websocket))
        
        if await self.connect(websocket, client_id):
            ws_connections.inc()
            try:
                await self._handle_client_messages(client_id, websocket)
            finally:
                await self.disconnect(client_id)
                ws_connections.dec()

    async def _handle_client_messages(self, client_id: str, websocket: WebSocket):
        """Handle messages from a client."""
        try:
            while True:
                message = await websocket.receive_json()
                with ws_latency.time():
                    await self.handle_message(client_id, message)
                    ws_messages.labels(channel=message.get('channel', 'unknown')).inc()
        except Exception as e:
            ws_errors.labels(type='message_handling').inc()
            raise

    async def broadcast_market_update(self, data: dict):
        """Broadcast market update to subscribed clients."""
        await self.broadcast(
            {
                'type': 'market_update',
                'data': data,
                'timestamp': datetime.now().isoformat()
            },
            channel='market'
        )

    async def broadcast_trade_update(self, data: dict):
        """Broadcast trade update to subscribed clients."""
        await self.broadcast(
            {
                'type': 'trade_update',
                'data': data,
                'timestamp': datetime.now().isoformat()
            },
            channel='trades'
        )

    async def broadcast_portfolio_update(self, data: dict):
        """Broadcast portfolio update to subscribed clients."""
        await self.broadcast(
            {
                'type': 'portfolio_update',
                'data': data,
                'timestamp': datetime.now().isoformat()
            },
            channel='portfolio'
        )

    async def broadcast_emotion_update(self, data: dict):
        """Broadcast emotion update to subscribed clients."""
        await self.broadcast(
            {
                'type': 'emotion_update',
                'data': data,
                'timestamp': datetime.now().isoformat()
            },
            channel='emotions'
        )
        
    async def broadcast_strategies_update(self, data: dict):
        """Broadcast trading strategies update to subscribed clients."""
        await self.broadcast(
            {
                'type': 'strategies_update',
                'data': data,
                'timestamp': datetime.now().isoformat()
            },
            channel='strategies'
        )

    async def _collect_metrics(self):
        """Collect metrics periodically using ConnectionManager stats"""
        while self._running:
            try:
                # Get stats from connection manager
                stats = self.connection_manager.get_connection_stats()
                # Update metrics
                self.metrics['connections'] = stats['total_connections']
                # Log metrics every 60 seconds
                logging.info(f"Current metrics: {self.metrics}")
                await asyncio.sleep(60)
            except Exception as e:
                logging.error(f"Error collecting metrics: {e}")
                self.metrics['errors'] += 1
                await asyncio.sleep(5)

    async def _handle_market_data(self, client_id: str, message: dict):
        """Handle market data channel messages."""
        from trading_agent import TradingAgent
        
        action = message.get('action')
        logger.info(f"Handling market data action: {action}")
        
        try:
            # Initialize AI trading agent for this request
            ai_agent = TradingAgent()
            
            if action == 'subscribe':
                # Subscribe client to market data updates
                symbols = message.get('symbols', ['BTC', 'ETH'])
                await self.connection_manager.subscribe(client_id, 'market')
                
                # Send confirmation
                await self.connection_manager.send_to_client(
                    client_id,
                    {
                        'type': 'market_subscription',
                        'status': 'success',
                        'symbols': symbols,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
            elif action == 'analyze':
                # Get token from request
                token = message.get('token', 'ETH')
                
                # Get analysis from AI trading agent
                analysis = ai_agent.analyze_market_with_rehoboam(token)
                
                # Send analysis to client
                await self.connection_manager.send_to_client(
                    client_id,
                    {
                        'type': 'market_analysis',
                        'token': token,
                        'analysis': analysis,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
            elif action == 'arbitrage':
                # Get arbitrage opportunities from the AI agent
                opportunities = ai_agent.find_arbitrage_opportunities()
                
                # Send opportunities to client
                await self.connection_manager.send_to_client(
                    client_id,
                    {
                        'type': 'arbitrage_opportunities',
                        'opportunities': opportunities,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
            elif action == 'network_recommendation':
                # Get token and transaction type from request
                token = message.get('token', 'ETH')
                transaction_type = message.get('transaction_type', 'swap')
                amount = message.get('amount', 1.0)
                
                # Get network recommendation from AI agent
                recommendation = ai_agent.recommend_network(token, transaction_type, amount)
                
                # Send recommendation to client
                await self.connection_manager.send_to_client(
                    client_id,
                    {
                        'type': 'network_recommendation',
                        'token': token,
                        'transaction_type': transaction_type,
                        'recommendation': recommendation,
                        'timestamp': datetime.now().isoformat()
                    }
                )
            
            else:
                # Unknown action
                await self.connection_manager.send_to_client(
                    client_id,
                    {
                        'type': 'error',
                        'message': f'Unknown market data action: {action}',
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
        except Exception as e:
            logger.error(f"Error handling market data message: {str(e)}")
            await self.connection_manager.send_to_client(
                client_id,
                {
                    'type': 'error',
                    'message': f'Error processing market data request: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }
            )

    async def _handle_trade_updates(self, client_id: str, message: dict):
        """Handle trade updates channel messages."""
        from trading_agent import TradingAgent
        
        action = message.get('action')
        logger.info(f"Handling trade update action: {action}")
        
        try:
            # Initialize AI trading agent for this request
            ai_agent = TradingAgent()
            
            if action == 'subscribe':
                # Subscribe client to trade updates
                await self.connection_manager.subscribe(client_id, 'trades')
                
                # Send confirmation
                await self.connection_manager.send_to_client(
                    client_id,
                    {
                        'type': 'trade_subscription',
                        'status': 'success',
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
            elif action == 'execute_trade':
                # Get trade details
                token = message.get('token', 'ETH')
                amount = message.get('amount', 0.1)
                side = message.get('side', 'buy')
                network = message.get('network', 'ethereum')
                
                # Validate input
                if amount <= 0:
                    raise ValueError("Trade amount must be greater than 0")
                
                # Convert to contract units (wei, satoshi, etc.)
                amount_in_units = int(amount * 10**18)  # Assumes 18 decimal places like ETH
                
                # Execute trade with AI trading agent
                result = ai_agent.trade_tokens(amount_in_units, side, network)
                
                # Send trade result to client
                await self.connection_manager.send_to_client(
                    client_id,
                    {
                        'type': 'trade_result',
                        'token': token,
                        'amount': amount,
                        'side': side,
                        'network': network,
                        'success': result,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
                # Broadcast trade update to all clients subscribed to trades channel
                await self.broadcast_trade_update({
                    'token': token,
                    'amount': amount,
                    'side': side,
                    'network': network,
                    'success': result,
                    'timestamp': datetime.now().isoformat()
                })
                
            elif action == 'execute_arbitrage':
                # Get opportunity details
                opportunity_id = message.get('opportunity_id')
                token = message.get('token', 'ETH')
                
                # Find relevant arbitrage opportunity
                opportunities = ai_agent.find_arbitrage_opportunities()
                selected_opportunity = None
                
                for opp in opportunities:
                    if opp.get('id') == opportunity_id or (opportunity_id is None and opp.get('token') == token):
                        selected_opportunity = opp
                        break
                
                if not selected_opportunity:
                    raise ValueError(f"Arbitrage opportunity not found for ID: {opportunity_id} or token: {token}")
                
                # Execute arbitrage with AI trading agent
                result = ai_agent.execute_arbitrage(selected_opportunity)
                
                # Send arbitrage result to client
                await self.connection_manager.send_to_client(
                    client_id,
                    {
                        'type': 'arbitrage_result',
                        'opportunity': selected_opportunity,
                        'result': result,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
                # Broadcast arbitrage execution to all clients subscribed to trades channel
                await self.broadcast_trade_update({
                    'type': 'arbitrage_execution',
                    'opportunity': selected_opportunity,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                })
                
            else:
                # Unknown action
                await self.connection_manager.send_to_client(
                    client_id,
                    {
                        'type': 'error',
                        'message': f'Unknown trade action: {action}',
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
        except Exception as e:
            logger.error(f"Error handling trade update message: {str(e)}")
            await self.connection_manager.send_to_client(
                client_id,
                {
                    'type': 'error',
                    'message': f'Error processing trade request: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }
            )

    async def _handle_portfolio_updates(self, client_id: str, message: dict):
        """Handle portfolio updates channel messages."""
        # Implementation in portfolio service
        pass

    async def _handle_emotion_updates(self, client_id: str, message: dict):
        """Handle emotion updates channel messages."""
        # Implementation in Rehoboam AI service
        pass
        
    async def _handle_strategies_updates(self, client_id: str, message: dict):
        """Handle trading strategies channel messages."""
        from trading_agent import TradingAgent
        
        action = message.get('action')
        logger.info(f"Handling strategies action: {action}")
        
        try:
            # Initialize AI trading agent for this request
            ai_agent = TradingAgent()
            
            if action == 'subscribe':
                # Subscribe client to strategies updates
                await self.connection_manager.subscribe(client_id, 'strategies')
                
                # Send confirmation
                await self.connection_manager.send_to_client(
                    client_id,
                    {
                        'type': 'strategies_subscription',
                        'status': 'success',
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
            elif action == 'get_strategies':
                # Get token and risk profile from request
                token = message.get('token', 'ETH')
                risk_profile = message.get('risk_profile', 'moderate')
                
                # Get market analysis
                analysis = ai_agent.analyze_market_with_rehoboam(token)
                
                # Create strategies based on analysis
                strategy = {
                    'id': f"{token.lower()}-strategy-1",
                    'name': f"{token} Trading Strategy",
                    'description': f"AI-generated strategy for {token} based on current market conditions",
                    'token': token,
                    'recommendation': analysis.get('recommendation', 'hold'),
                    'confidence': analysis.get('confidence', 0.5),
                    'risk_level': risk_profile,
                    'expected_return': 0.05 if analysis.get('recommendation') == 'buy' else 0.02,
                    'timeframe': analysis.get('prediction', {}).get('time_horizon', '24h'),
                    'reasoning': analysis.get('reasoning', 'Based on current market analysis'),
                    'networks': ['ethereum', 'arbitrum', 'optimism'],
                    'timestamp': datetime.now().isoformat()
                }
                
                strategies = [strategy]
                
                # Add Layer 2 specific strategy if we have a positive recommendation
                if analysis.get('recommendation') == 'buy':
                    l2_strategy = {
                        'id': f"{token.lower()}-l2-strategy-1",
                        'name': f"{token} Layer 2 Opportunity",
                        'description': f"Layer 2 focused strategy for {token} with lower gas fees",
                        'token': token,
                        'recommendation': 'buy',
                        'confidence': min(analysis.get('confidence', 0.5) + 0.1, 0.95),
                        'risk_level': risk_profile,
                        'expected_return': 0.07,
                        'timeframe': '12h',
                        'reasoning': 'Lower fees and faster execution on Layer 2 networks',
                        'networks': ['arbitrum', 'optimism', 'base'],
                        'timestamp': datetime.now().isoformat()
                    }
                    strategies.append(l2_strategy)
                    
                # Send strategies to client
                await self.connection_manager.send_to_client(
                    client_id,
                    {
                        'type': 'strategies',
                        'token': token,
                        'strategies': strategies,
                        'count': len(strategies),
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
            else:
                # Unknown action
                await self.connection_manager.send_to_client(
                    client_id,
                    {
                        'type': 'error',
                        'message': f'Unknown strategies action: {action}',
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
        except Exception as e:
            logger.error(f"Error handling strategies message: {str(e)}")
            await self.connection_manager.send_to_client(
                client_id,
                {
                    'type': 'error',
                    'message': f'Error processing strategies request: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }
            )

    def get_health_metrics(self) -> dict:
        """Get server health metrics."""
        stats = self.connection_manager.get_connection_stats()
        return {
            'connections': {
                'current': stats['total_connections'],
                'by_channel': stats['channels']
            },
            'metrics': {
                'messages': ws_messages._value.sum(),
                'errors': ws_errors._value.sum(),
                'average_latency': ws_latency.observe(),
            },
            'status': 'healthy' if ws_errors._value.sum() < 100 else 'degraded'
        }

    async def connect(self, websocket: WebSocket, client_id: str) -> bool:
        """Accept connection and add to active connections using ConnectionManager."""
        result = await self.connection_manager.connect(client_id, websocket)
        if result:
            self.metrics['connections'] += 1
            logger.info(f"Client {client_id} connected. Total connections: {self.metrics['connections']}")
        return result

    async def disconnect(self, client_id: str):
        """Handle client disconnection using ConnectionManager."""
        await self.connection_manager.disconnect(client_id)
        stats = self.connection_manager.get_connection_stats()
        self.metrics['connections'] = stats['total_connections']
        
    def _cleanup_client(self, client_id: str):
        """Clean up client data on disconnect - now handled by ConnectionManager."""
        # This is now handled by the ConnectionManager
        stats = self.connection_manager.get_connection_stats()
        self.metrics['connections'] = stats['total_connections']

    async def broadcast(self, message: Any, channel: Optional[str] = None):
        """Broadcast message to all clients or specific channel using ConnectionManager."""
        try:
            # Format the message for broadcasting
            formatted_message = {
                "data": message,
                "timestamp": datetime.now().isoformat(),
                "channel": channel or "all"
            }
            
            # Use connection manager to broadcast
            if channel:
                await self.connection_manager.broadcast(formatted_message, channel)
            else:
                await self.connection_manager.broadcast(formatted_message)
                
            self.metrics['messages_processed'] += 1
        except Exception as e:
            logger.error(f"Error broadcasting to channel {channel}: {str(e)}")
            self.metrics['errors'] += 1

    async def subscribe(self, client_id: str, channel: str) -> bool:
        """Subscribe client to a channel using ConnectionManager."""
        result = await self.connection_manager.subscribe(client_id, channel)
        if result:
            logger.info(f"Client {client_id} subscribed to {channel}")
        return result

    async def unsubscribe(self, client_id: str, channel: str) -> bool:
        """Unsubscribe client from a channel using ConnectionManager."""
        if client_id and channel:
            await self.connection_manager.unsubscribe(client_id, channel)
            logger.info(f"Client {client_id} unsubscribed from {channel}")
            return True
        else:
            logger.warning(f"Invalid unsubscribe request: client_id={client_id}, channel={channel}")
            return False

    async def handle_message(self, client_id: str, message: Dict):
        """Handle incoming messages from clients using ConnectionManager."""
        try:
            # Pass message to connection manager for handling
            await self.connection_manager.handle_message(client_id, message)
            self.metrics['messages_processed'] += 1
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {str(e)}")
            self.metrics['errors'] += 1

    def get_metrics(self) -> Dict[str, int]:
        """Get current server metrics."""
        return dict(self.metrics)