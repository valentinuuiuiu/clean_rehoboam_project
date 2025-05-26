# Usage Guide

## System Overview

This platform consists of several integrated components:
- Web3 Integration Layer (Frontend)
- Trading Engine (Backend)
- AI Market Analyzer
- Portfolio Optimizer
- Safety System

## Configuration

1. **Environment Setup**
   ```env
   VITE_ALCHEMY_API_KEY=your_key_here
   PYTHON_ENV=development
   ```

2. **Network Configuration**
   - Default supported networks: Ethereum, Arbitrum, Optimism, Polygon
   - Add custom networks in `src/contexts/Web3Context.tsx`

3. **Wallet Setup**
   - Install MetaMask or Talisman
   - Connect to the platform using the wallet button
   - Ensure sufficient funds for transactions

## Core Features

### 1. Wallet Integration
```typescript
// Using the Web3 Context
import { useWeb3 } from '../contexts/Web3Context';

// Connect wallet
const { connectWallet } = useWeb3();
await connectWallet('metamask'); // or 'talisman'

// Switch networks
const { switchNetwork } = useWeb3();
await switchNetwork(1); // Ethereum Mainnet
```

### 2. Trading Features

#### Price Monitoring
```python
# Using the price feed service
from utils.price_feed_service import PriceFeedService

price_feed = PriceFeedService()
price = await price_feed.get_price('ETH/USD')
```

#### Portfolio Management
```python
# Optimize portfolio
from utils.portfolio_optimizer import PortfolioOptimizer

optimizer = PortfolioOptimizer()
optimal_allocation = await optimizer.optimize(assets, constraints)
```

### 3. AI Market Analysis

The system includes:
- Sentiment Analysis
- Technical Analysis
- Market Trend Prediction
- Risk Assessment

Access through:
```python
from utils.ai_market_analyzer import AIMarketAnalyzer

analyzer = AIMarketAnalyzer()
analysis = await analyzer.analyze_market('ETH')
```

### 4. Safety Features

Built-in safety checks:
- Transaction validation
- Price impact analysis
- Slippage protection
- Gas optimization

## Best Practices

1. **Trading Safety**
   - Always set appropriate slippage tolerances
   - Use safety checks before trades
   - Monitor gas prices for optimal execution

2. **Portfolio Management**
   - Regularly rebalance portfolios
   - Set stop-loss limits
   - Diversify across chains and assets

3. **System Monitoring**
   - Check logs regularly
   - Monitor transaction status
   - Keep track of portfolio performance

## Troubleshooting

Common issues and solutions:

1. **Wallet Connection Issues**
   - Ensure wallet is installed and unlocked
   - Check network status
   - Verify RPC endpoints

2. **Transaction Failures**
   - Check gas prices
   - Verify sufficient balance
   - Confirm network congestion

3. **Price Feed Issues**
   - Verify Chainlink oracle status
   - Check network connectivity
   - Confirm feed addresses

## Advanced Usage

### Custom Trading Strategies
```python
from utils.trading_algorithms import TradingStrategy

class CustomStrategy(TradingStrategy):
    def analyze(self):
        # Implement custom logic
        pass
```

### Custom Safety Checks
```python
from utils.safety_checks import SafetyCheck

class CustomSafetyCheck(SafetyCheck):
    def validate(self):
        # Implement custom validation
        pass
```

## API Reference

See the following files for detailed API documentation:
- `trading_agent.py`
- `utils/trading_algorithms.py`
- `utils/portfolio_optimizer.py`
- `utils/ai_market_analyzer.py`