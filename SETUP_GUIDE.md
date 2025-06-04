# Rehoboam Trading Platform - Setup Guide

This guide will help you set up the Rehoboam Trading Platform for development and production use.

## Prerequisites

- Node.js v16+ 
- Python 3.11+
- Git
- Web3 wallet (MetaMask or Talisman)
- PostgreSQL (for production)

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/valentinuuiuiu/clean_rehoboam_project.git
cd clean_rehoboam_project
```

### 2. Environment Configuration

```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your API keys and configuration
nano .env
```

**Required API Keys:**
- `ALCHEMY_API_KEY` - Get from [Alchemy](https://www.alchemy.com/)
- `OPENAI_API_KEY` - Get from [OpenAI](https://platform.openai.com/)
- `ETHERSCAN_API_KEY` - Get from [Etherscan](https://etherscan.io/apis)

**Optional but Recommended:**
- `DEEPSEEK_API_KEY` - For enhanced AI capabilities
- `GEMINI_API_KEY` - For additional AI model support

### 3. Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt
```

### 4. Start Development Servers

```bash
# Start both frontend and backend
npm run dev
```

This will start:
- Frontend (React/Vite): http://localhost:5001
- Backend (FastAPI): http://localhost:5002

## Production Deployment

### Using Docker Compose

```bash
# Build and start all services
docker-compose up -d
```

This includes:
- Frontend and Backend services
- PostgreSQL database
- MCP services
- Monitoring stack

### Manual Deployment

1. **Build Frontend:**
```bash
npm run build
```

2. **Start Backend:**
```bash
uvicorn api_server:app --host 0.0.0.0 --port 5002
```

3. **Serve Frontend:**
```bash
npm run preview
```

## Configuration

### Wallet Setup

1. Install MetaMask or Talisman browser extension
2. Create or import your wallet
3. Add supported networks (Arbitrum, Optimism, Polygon, etc.)
4. Fund your wallet with test tokens for development

### Network Configuration

The platform supports multiple networks:
- Ethereum Mainnet
- Arbitrum
- Optimism  
- Polygon
- Base
- And more...

### Security Notes

⚠️ **Important Security Guidelines:**

- Never commit real private keys to version control
- Use environment variables for all sensitive data
- Enable 2FA on all API key accounts
- Use testnet for development and testing
- Regularly rotate API keys

## Features Overview

### Core Features
- Multi-wallet support (MetaMask, Talisman)
- Multi-chain trading and arbitrage
- Real-time market data and analysis
- AI-powered trading strategies
- Portfolio optimization
- Risk management tools

### AI Capabilities
- Market sentiment analysis
- Automated strategy generation
- Cross-chain arbitrage detection
- Whale activity monitoring
- Smart contract security analysis

### Advanced Features
- Model Context Protocol (MCP) integration
- Layer 2 optimization
- Gas fee estimation
- MEV detection and protection
- Real-time WebSocket updates

## API Documentation

The API documentation is available at:
- Development: http://localhost:5002/docs
- Production: https://your-domain.com/docs

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   - Change ports in `.env` file
   - Kill existing processes: `lsof -ti:5002 | xargs kill -9`

2. **API key errors:**
   - Verify keys are correctly set in `.env`
   - Check API key permissions and quotas

3. **Web3 connection issues:**
   - Ensure wallet is connected
   - Check network configuration
   - Verify RPC endpoints

4. **Database connection:**
   - Ensure PostgreSQL is running
   - Check DATABASE_URL format
   - Verify credentials

### Getting Help

- Check the [Issues](https://github.com/valentinuuiuiu/clean_rehoboam_project/issues) page
- Review the [Documentation](README.md)
- Join our community discussions

## Development

### Project Structure

```
├── src/                 # Frontend React application
├── api_server.py       # Main FastAPI backend
├── utils/              # Utility modules
├── contracts/          # Smart contracts
├── mcp-services/       # MCP service implementations
├── tests/              # Test suites
└── docs/               # Documentation
```

### Running Tests

```bash
# Python tests
pytest

# Frontend tests  
npm test
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the ISC License - see the LICENSE file for details.