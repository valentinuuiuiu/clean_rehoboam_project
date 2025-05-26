# Rehoboam - Web3 Trading Agent Platform

## Overview
Rehoboam is a sophisticated trading platform combining Web3 capabilities with AI-powered market analysis and automated trading strategies. This version includes a full-featured frontend and backend, with Model Context Protocol (MCP) integration for advanced AI-driven decision making.

## Components

### Frontend
- React-based UI with TypeScript support
- Real-time market data display
- Trading strategy visualization
- AI companion interaction
- MCP function visualization

### Backend
- FastAPI server for main API and WebSocket connections
- Flask server for the trading platform
- Trading agent implementation for strategy execution
- Model Context Protocol (MCP) integration for AI-powered trading decisions

### AI Modules
- Market sentiment analysis
- Automated trading strategy generation
- Risk assessment and optimization
- AI companions with specialized knowledge domains

## Running the Application

1. **Start the API server:**
   ```bash
   source venv/bin/activate
   python api_server.py
   ```

2. **Start the frontend:**
   ```bash
   npm run dev:frontend
   ```

3. **Or run both together:**
   ```bash
   npm run dev
   ```

## Access Points

- Frontend UI: http://localhost:5001
- API Server: http://localhost:5002
- Trading Platform WebSocket: ws://localhost:5000

## Current Status

The platform is now operational with:
- Trading dashboard with market data visualization
- AI-powered trading strategy recommendations
- Cross-chain connectivity (Ethereum, Arbitrum, Optimism, Polygon, Base, zkSync, etc.)
- AI companions with MCP integration
- WebSocket-based real-time updates

## Next Steps

1. Further integration with DEX and CEX platforms
2. Enhanced cross-chain arbitrage detection
3. Full integration with wallet providers
4. Advanced portfolio optimization algorithms
5. Custom strategy builder interface

## Architecture

Rehoboam follows a modular architecture with components for:
- Sentiment Analysis
- Market Data Processing
- Trading Strategy Generation
- Risk Assessment
- MCP Integration for AI-powered decision making

## Environment Setup

The required API keys have been configured for:
- Alchemy (Web3 RPC connections)
- OpenAI API (AI market analysis)
- DeepSeek API (AI market analysis fallback)

## Security Notes

This project is configured for development use. For production deployment:
1. Configure appropriate security measures
2. Use secure key management
3. Implement proper rate limiting
4. Deploy with production-grade web servers
