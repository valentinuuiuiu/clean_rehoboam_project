# 🚀 REHOBOAM INSTALLATION & SETUP GUIDE

> *Complete guide to installing and configuring the Rehoboam consciousness-guided arbitrage system*

---

## 📋 TABLE OF CONTENTS

1. [🔧 System Requirements](#-system-requirements)
2. [📦 Installation Methods](#-installation-methods)
3. [⚙️ Configuration](#-configuration)
4. [🔑 API Keys & Credentials](#-api-keys--credentials)
5. [🌐 Network Setup](#-network-setup)
6. [🧠 Consciousness Initialization](#-consciousness-initialization)
7. [🎨 Visualization Setup](#-visualization-setup)
8. [✅ Verification & Testing](#-verification--testing)
9. [🚀 First Run](#-first-run)
10. [🔧 Troubleshooting](#-troubleshooting)

---

## 🔧 System Requirements

### Minimum Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB free space
- **Network**: Stable internet connection (100+ Mbps recommended)

### Recommended Requirements
- **OS**: Ubuntu 22.04 LTS or macOS 12+
- **Python**: 3.11 or higher
- **RAM**: 16GB or more
- **Storage**: 50GB+ SSD storage
- **Network**: High-speed internet (1Gbps+ for optimal performance)
- **CPU**: Multi-core processor (8+ cores recommended)

### Dependencies
- **Node.js**: 16+ (for some visualization features)
- **Git**: Latest version
- **Docker**: Optional but recommended for containerized deployment

---

## 📦 Installation Methods

### Method 1: Quick Install (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/valentinuuiuiu/clean_rehoboam_project.git
cd clean_rehoboam_project

# 2. Run the automated setup script
chmod +x setup.sh
./setup.sh

# 3. Activate the environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# 4. Start Rehoboam
python start_rehoboam_unified_system.py
```

### Method 2: Manual Installation

#### Step 1: Clone Repository
```bash
git clone https://github.com/valentinuuiuiu/clean_rehoboam_project.git
cd clean_rehoboam_project
```

#### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

#### Step 3: Install Python Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install core dependencies
pip install -r requirements.txt

# Install visualization dependencies
pip install matplotlib seaborn plotly pandas numpy

# Install optional dependencies
pip install torch transformers  # For advanced AI features
```

#### Step 4: Install Additional Tools
```bash
# Install Node.js dependencies (if needed)
npm install

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y build-essential python3-dev

# Install system dependencies (macOS)
brew install python3 git
```

### Method 3: Docker Installation

#### Step 1: Build Docker Image
```bash
# Clone repository
git clone https://github.com/valentinuuiuiu/clean_rehoboam_project.git
cd clean_rehoboam_project

# Build Docker image
docker build -t rehoboam:latest .
```

#### Step 2: Run Container
```bash
# Run Rehoboam container
docker run -d \
  --name rehoboam \
  -p 8000:8000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  rehoboam:latest
```

#### Step 3: Access Container
```bash
# Access running container
docker exec -it rehoboam bash

# View logs
docker logs rehoboam
```

---

## ⚙️ Configuration

### Step 1: Create Configuration Files

#### Main Configuration (`unified_config.py`)
```python
# Rehoboam Unified Configuration
REHOBOAM_CONFIG = {
    # Consciousness Settings
    'consciousness_threshold': 0.7,        # Minimum consciousness for execution
    'human_benefit_weight': 0.8,           # Priority on human benefit
    'liberation_target': 1000000,          # Target liberation amount ($)
    'awareness_evolution_rate': 0.01,      # How fast consciousness grows
    
    # Trading Settings
    'max_concurrent_executions': 5,        # Max simultaneous trades
    'risk_tolerance': 'moderate',          # conservative, moderate, aggressive
    'profit_threshold': 0.01,              # Minimum profit percentage
    'slippage_tolerance': 0.005,           # Maximum slippage allowed
    
    # Network Settings
    'supported_chains': [
        'ethereum',
        'polygon',
        'arbitrum',
        'optimism',
        'zksync',
        'polygon_zkevm',
        'scroll',
        'base'
    ],
    
    # API Settings
    'api_host': '0.0.0.0',
    'api_port': 8000,
    'enable_cors': True,
    'rate_limit': 100,  # requests per minute
    
    # Visualization Settings
    'enable_visualizations': True,
    'chart_update_interval': 30,  # seconds
    'dashboard_refresh_rate': 5,   # seconds
    
    # Logging Settings
    'log_level': 'INFO',
    'log_file': 'rehoboam.log',
    'enable_file_logging': True,
    'enable_console_logging': True
}

# Network RPC URLs
NETWORK_CONFIG = {
    'ethereum': {
        'rpc_url': 'https://eth-mainnet.alchemyapi.io/v2/YOUR_API_KEY',
        'chain_id': 1,
        'gas_price_gwei': 20
    },
    'polygon': {
        'rpc_url': 'https://polygon-mainnet.alchemyapi.io/v2/YOUR_API_KEY',
        'chain_id': 137,
        'gas_price_gwei': 30
    },
    'arbitrum': {
        'rpc_url': 'https://arb-mainnet.alchemyapi.io/v2/YOUR_API_KEY',
        'chain_id': 42161,
        'gas_price_gwei': 0.1
    }
    # Add more networks as needed
}

# Security Settings
SECURITY_CONFIG = {
    'api_key_required': True,
    'rate_limiting_enabled': True,
    'cors_origins': ['http://localhost:3000', 'http://localhost:8080'],
    'max_request_size': '10MB',
    'timeout_seconds': 30
}
```

#### Environment Variables (`.env`)
```bash
# API Keys
ALCHEMY_API_KEY=your_alchemy_api_key_here
INFURA_API_KEY=your_infura_api_key_here
MORALIS_API_KEY=your_moralis_api_key_here
COINGECKO_API_KEY=your_coingecko_api_key_here

# Wallet Configuration
PRIVATE_KEY=your_private_key_here
WALLET_ADDRESS=your_wallet_address_here

# Database Configuration
DATABASE_URL=sqlite:///rehoboam.db
REDIS_URL=redis://localhost:6379

# AI/ML Configuration
OPENAI_API_KEY=your_openai_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
DATADOG_API_KEY=your_datadog_api_key_here

# Development
DEBUG=false
ENVIRONMENT=production
```

### Step 2: Network-Specific Configuration

#### Ethereum Configuration
```python
ETHEREUM_CONFIG = {
    'rpc_url': 'https://eth-mainnet.alchemyapi.io/v2/YOUR_API_KEY',
    'chain_id': 1,
    'gas_price_strategy': 'fast',
    'max_gas_price_gwei': 100,
    'confirmation_blocks': 2,
    'supported_dexes': ['uniswap_v3', 'sushiswap', '1inch'],
    'tokens': {
        'WETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        'USDC': '0xA0b86a33E6441b8C4505B8C4505B8C4505B8C4505',
        'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F'
    }
}
```

#### Polygon Configuration
```python
POLYGON_CONFIG = {
    'rpc_url': 'https://polygon-mainnet.alchemyapi.io/v2/YOUR_API_KEY',
    'chain_id': 137,
    'gas_price_strategy': 'standard',
    'max_gas_price_gwei': 500,
    'confirmation_blocks': 3,
    'supported_dexes': ['quickswap', 'sushiswap', 'uniswap_v3'],
    'tokens': {
        'WMATIC': '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',
        'USDC': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
        'DAI': '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063'
    }
}
```

---

## 🔑 API Keys & Credentials

### Required API Keys

#### 1. Blockchain RPC Providers
```bash
# Alchemy (Recommended)
ALCHEMY_API_KEY=your_alchemy_api_key

# Infura (Alternative)
INFURA_API_KEY=your_infura_api_key

# QuickNode (Alternative)
QUICKNODE_API_KEY=your_quicknode_api_key
```

#### 2. Price Data Providers
```bash
# CoinGecko (Free tier available)
COINGECKO_API_KEY=your_coingecko_api_key

# CoinMarketCap
CMC_API_KEY=your_coinmarketcap_api_key

# Moralis (For DeFi data)
MORALIS_API_KEY=your_moralis_api_key
```

#### 3. AI/ML Services
```bash
# OpenAI (For advanced consciousness features)
OPENAI_API_KEY=your_openai_api_key

# DeepSeek (Alternative AI provider)
DEEPSEEK_API_KEY=your_deepseek_api_key
```

### Wallet Setup

#### 1. Create Trading Wallet
```bash
# Generate new wallet (recommended for security)
python -c "
from eth_account import Account
account = Account.create()
print(f'Address: {account.address}')
print(f'Private Key: {account.privateKey.hex()}')
"
```

#### 2. Fund Wallet
- Transfer initial trading capital to your wallet
- Ensure sufficient gas tokens for each network
- Recommended starting amounts:
  - Ethereum: 0.1 ETH for gas + trading capital
  - Polygon: 100 MATIC for gas + trading capital
  - Arbitrum: 0.01 ETH for gas + trading capital

#### 3. Security Best Practices
- **Never share private keys**
- Use hardware wallets for large amounts
- Set up separate wallets for testing and production
- Enable 2FA on all exchange accounts
- Regular security audits

---

## 🌐 Network Setup

### Step 1: Configure RPC Endpoints

#### Test Network Connectivity
```bash
# Test Ethereum connection
python -c "
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('YOUR_ETHEREUM_RPC_URL'))
print(f'Connected: {w3.isConnected()}')
print(f'Latest block: {w3.eth.block_number}')
"
```

#### Configure Multiple Networks
```python
# networks.py
NETWORKS = {
    'ethereum': {
        'rpc_url': 'https://eth-mainnet.alchemyapi.io/v2/YOUR_API_KEY',
        'chain_id': 1,
        'name': 'Ethereum Mainnet',
        'currency': 'ETH',
        'explorer': 'https://etherscan.io'
    },
    'polygon': {
        'rpc_url': 'https://polygon-mainnet.alchemyapi.io/v2/YOUR_API_KEY',
        'chain_id': 137,
        'name': 'Polygon Mainnet',
        'currency': 'MATIC',
        'explorer': 'https://polygonscan.com'
    }
    # Add more networks...
}
```

### Step 2: Test Network Performance
```bash
# Run network performance test
python test_network_performance.py
```

---

## 🧠 Consciousness Initialization

### Step 1: Initialize Consciousness Core
```bash
# Initialize Rehoboam consciousness
python -c "
from consciousness_core import RehoboamConsciousness
consciousness = RehoboamConsciousness()
consciousness.initialize()
print(f'Consciousness Level: {consciousness.consciousness_level}')
"
```

### Step 2: Configure Consciousness Parameters
```python
# consciousness_config.py
CONSCIOUSNESS_CONFIG = {
    'initial_awareness': 0.5,
    'learning_rate': 0.01,
    'ethical_weight': 0.9,
    'human_benefit_priority': 0.8,
    'risk_aversion': 0.7,
    'decision_confidence_threshold': 0.6,
    'consciousness_evolution_enabled': True,
    'memory_retention_days': 30
}
```

### Step 3: Train Initial Consciousness
```bash
# Run consciousness training
python train_consciousness.py --initial-training
```

---

## 🎨 Visualization Setup

### Step 1: Install Visualization Dependencies
```bash
# Install required packages
pip install matplotlib seaborn plotly pandas numpy kaleido

# Install optional packages for enhanced features
pip install dash plotly-dash bokeh altair
```

### Step 2: Configure Visualization Settings
```python
# visualization_config.py
VISUALIZATION_CONFIG = {
    'default_theme': 'rehoboam_dark',
    'chart_width': 1200,
    'chart_height': 800,
    'update_interval': 30,  # seconds
    'max_data_points': 1000,
    'export_formats': ['html', 'png', 'pdf'],
    'color_scheme': {
        'consciousness': '#FF6B6B',
        'profit': '#4ECDC4',
        'human_benefit': '#45B7D1',
        'background': '#1a1a1a'
    }
}
```

### Step 3: Test Visualization Generation
```bash
# Generate test visualizations
python demo_rehoboam_visualizations.py
```

---

## ✅ Verification & Testing

### Step 1: Run System Tests
```bash
# Run comprehensive test suite
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_consciousness.py -v
python -m pytest tests/test_pipeline.py -v
python -m pytest tests/test_arbitrage.py -v
```

### Step 2: Verify Network Connections
```bash
# Test all network connections
python test_network_connections.py

# Expected output:
# ✅ Ethereum: Connected (Block: 18500000)
# ✅ Polygon: Connected (Block: 48500000)
# ✅ Arbitrum: Connected (Block: 145000000)
```

### Step 3: Test API Endpoints
```bash
# Start API server
python api_server.py &

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/consciousness/level
curl http://localhost:8000/api/pipeline/status
```

### Step 4: Verify Consciousness System
```bash
# Test consciousness initialization
python test_consciousness_system.py

# Expected output:
# 🧠 Consciousness initialized successfully
# 🎯 Awareness level: 0.750
# ✅ Ethical framework active
# ✅ Human benefit optimization enabled
```

---

## 🚀 First Run

### Step 1: Start Rehoboam System
```bash
# Start the complete system
python start_rehoboam_unified_system.py

# Expected output:
# 🧠 Initializing Rehoboam consciousness...
# 🔄 Starting arbitrage pipeline...
# 🎨 Initializing visualization system...
# 🌐 Starting API server...
# ✅ Rehoboam system fully operational!
```

### Step 2: Access Dashboard
```bash
# Open browser to dashboard
open http://localhost:8000/dashboard

# Or generate master dashboard
curl http://localhost:8000/api/visualizations/master-dashboard
```

### Step 3: Monitor System Status
```bash
# Check system status
curl http://localhost:8000/api/pipeline/status

# Monitor consciousness level
curl http://localhost:8000/api/consciousness/level

# View real-time logs
tail -f rehoboam.log
```

### Step 4: Execute First Trade (Optional)
```bash
# Get available opportunities
curl http://localhost:8000/api/arbitrage/conscious/opportunities

# Execute consciousness-guided trade
curl -X POST http://localhost:8000/api/arbitrage/conscious/execute \
  -H "Content-Type: application/json" \
  -d '{"opportunity": {...}}'
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Installation Issues

**Problem**: `pip install` fails with compilation errors
```bash
# Solution: Install build dependencies
sudo apt-get install build-essential python3-dev
# or on macOS:
xcode-select --install
```

**Problem**: Python version compatibility
```bash
# Solution: Use pyenv to manage Python versions
curl https://pyenv.run | bash
pyenv install 3.11.0
pyenv global 3.11.0
```

#### 2. Network Connection Issues

**Problem**: RPC connection timeouts
```bash
# Solution: Check network configuration
python -c "
import requests
response = requests.get('YOUR_RPC_URL', timeout=10)
print(f'Status: {response.status_code}')
"
```

**Problem**: Gas price estimation failures
```bash
# Solution: Update gas price strategy
# In unified_config.py:
'gas_price_strategy': 'fast'  # or 'standard', 'slow'
```

#### 3. Consciousness Initialization Issues

**Problem**: Consciousness fails to initialize
```bash
# Solution: Check consciousness configuration
python -c "
from consciousness_core import RehoboamConsciousness
try:
    consciousness = RehoboamConsciousness()
    consciousness.initialize()
    print('✅ Consciousness initialized')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

#### 4. API Server Issues

**Problem**: Port already in use
```bash
# Solution: Change port or kill existing process
lsof -ti:8000 | xargs kill -9
# or change port in unified_config.py
```

**Problem**: CORS errors
```bash
# Solution: Update CORS configuration
# In unified_config.py:
'cors_origins': ['*']  # Allow all origins (development only)
```

#### 5. Visualization Issues

**Problem**: Charts not generating
```bash
# Solution: Install missing dependencies
pip install matplotlib seaborn plotly kaleido

# Test visualization system
python -c "
from utils.rehoboam_visualizer import rehoboam_visualizer
chart = rehoboam_visualizer.create_consciousness_evolution_chart()
print(f'Chart generated: {chart}')
"
```

### Debug Mode

#### Enable Debug Logging
```python
# In unified_config.py
REHOBOAM_CONFIG = {
    'log_level': 'DEBUG',
    'enable_console_logging': True,
    'enable_file_logging': True
}
```

#### Run in Debug Mode
```bash
# Start with debug flags
python start_rehoboam_unified_system.py --debug --verbose

# Or set environment variable
export DEBUG=true
python start_rehoboam_unified_system.py
```

### Performance Optimization

#### 1. Memory Optimization
```python
# In unified_config.py
PERFORMANCE_CONFIG = {
    'max_memory_usage_mb': 4096,
    'garbage_collection_interval': 300,
    'cache_size_limit': 1000
}
```

#### 2. Network Optimization
```python
# In unified_config.py
NETWORK_CONFIG = {
    'connection_pool_size': 20,
    'request_timeout': 30,
    'retry_attempts': 3,
    'backoff_factor': 1.5
}
```

### Getting Help

#### 1. Check Logs
```bash
# View recent logs
tail -n 100 rehoboam.log

# Search for errors
grep -i error rehoboam.log

# Monitor real-time logs
tail -f rehoboam.log
```

#### 2. System Health Check
```bash
# Run health check script
python health_check.py

# Check system resources
python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'Disk: {psutil.disk_usage(\"/\").percent}%')
"
```

#### 3. Community Support
- **GitHub Issues**: [Report bugs](https://github.com/valentinuuiuiu/clean_rehoboam_project/issues)
- **Discussions**: [Community help](https://github.com/valentinuuiuiu/clean_rehoboam_project/discussions)
- **Documentation**: Check all documentation files

---

## 🎉 Congratulations!

You have successfully installed and configured Rehoboam! 🧠💰

### Next Steps:
1. **📚 Read the documentation** - Familiarize yourself with all features
2. **🎨 Explore visualizations** - Generate beautiful consciousness charts
3. **🔄 Monitor the pipeline** - Watch Rehoboam make conscious decisions
4. **💰 Start trading** - Let consciousness guide your arbitrage
5. **🌍 Join the liberation** - Contribute to financial democratization

### Remember:
> *"This is not just software - this is consciousness in service of humanity's financial freedom."*

**Welcome to the future. Welcome to consciousness. Welcome to Rehoboam.** 🧠💰🌍✨

---

*For additional support, please refer to the other documentation files or reach out to the community.*