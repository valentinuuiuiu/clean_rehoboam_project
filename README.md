# Web3 Trading Agent Platform

A sophisticated trading platform that combines Web3 capabilities with AI-powered market analysis and automated trading strategies. The primary API is served by a FastAPI application ([`api_server.py`](api_server.py:1)).

## Features

- Multi-wallet support (MetaMask and Talisman)
- Multi-chain compatibility (Ethereum, Arbitrum, Optimism, Polygon, Base, and more)
- Real-time price feeds and market data
- AI-powered market analysis, sentiment detection, and strategy generation (integrating models like DeepSeek, Gemini, OpenAI)
- Automated trading strategies and execution
- Portfolio optimization and risk management
- Advanced safety checks
- Layer 2 network support with gas estimation and optimization
- Cross-chain arbitrage detection
- Blockchain analysis tools (wallet behavior, MEV detection, contract security)
- AI Companions for interactive experiences
- Model Context Protocol (MCP) integration for dynamic function execution
- Web interface with React and TypeScript

## Prerequisites

- Node.js v16+
- Python 3.11+ (as per [`Dockerfile.api`](Dockerfile.api:2))
- Web3 wallet (MetaMask or Talisman)
- API Keys (configure in `.env` file):
  - `ALCHEMY_API_KEY` (or `INFURA_PROJECT_ID`)
  - `OPENAI_API_KEY`
  - `DEEPSEEK_API_KEY`
  - `ETHERSCAN_API_KEY`
  - Optional: `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `CHAINLINK_API_KEY`, `COINGECKO_API_KEY`, etc.
- PostgreSQL database (optional, configured for Docker setup)
- Docker and Docker Compose (for full environment including MCP services)

## Web3 Configuration

The platform requires RPC endpoints for blockchain access. Configure these in your `.env` file:

### Required RPC Endpoints
- `ETHEREUM_RPC_URL`: Mainnet Ethereum RPC (e.g., Infura/Alchemy)
- `POLYGON_RPC_URL`: Polygon Mainnet RPC 
- `ARBITRUM_RPC_URL`: Arbitrum One RPC
- `OPTIMISM_RPC_URL`: Optimism Mainnet RPC
- `BSC_RPC_URL`: Binance Smart Chain RPC

### Wallet Security
- `WALLET_ENCRYPTION_KEY`: Encryption key for wallet security
- `HOT_WALLET_PRIVATE_KEY`: Private key for hot wallet (development only)
- `COLD_WALLET_ADDRESS`: Address for cold storage

### Security Notes
1. Never commit real private keys to source control
2. Use hardware wallets for production deployments
3. Configure proper gas limits (`MAX_GAS_PRICE_GWEI`)
4. Enable all security middleware in production

## Web3 API Endpoints

The following endpoints are available for direct Web3 interactions:

### Provider Management
- `POST /api/web3/providers`: Add a new Web3 provider
  - Parameters: `chain_id`, `rpc_url`
  
### Wallet Operations  
- `POST /api/web3/wallets`: Create a new wallet
  - Returns: `address`, `private_key`
  
- `GET /api/web3/balance`: Get wallet balance
  - Parameters: `address`, `chain_id`

### Transaction Handling
- `POST /api/web3/transactions`: Send a transaction
  - Parameters: `chain_id`, `from_address`, `to_address`, `value`, `private_key`, `gas_limit`, `max_priority_fee`, `max_fee`

## Environment Setup

1.  Clone the repository.
2.  Copy `.env.example` to `.env` and populate with your API keys and configurations:
    ```bash
    cp .env.example .env
    ```
3.  Key Environment Variables (see `.env.example` for a full list):
    -   `ALCHEMY_API_KEY` or `INFURA_PROJECT_ID`: For Web3 RPC connections.
    -   `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `GEMINI_API_KEY`: For AI features.
    -   `ETHERSCAN_API_KEY`: For blockchain analysis.
    -   `DATABASE_URL`: For PostgreSQL connection (used in Docker setup).
    -   `JWT_SECRET`: A secure secret key for JWT authentication.

## Quick Start (Local Development)

1.  Install dependencies:
    ```bash
    npm install
    pip install -r requirements.txt
    ```
2.  Ensure your `.env` file is configured with necessary API keys (e.g., `ALCHEMY_API_KEY`, `OPENAI_API_KEY`).
3.  Start the development servers (frontend and backend FastAPI API):
    ```bash
    npm run dev
    ```
    This will start:
    - Frontend (Vite): `http://localhost:5001` (or as configured by Vite)
    - Backend API (FastAPI): `http://localhost:5002`

For the full platform experience including MCP services, database, and monitoring, use Docker Compose:
```bash
docker-compose up -d
```

## API Endpoints

The main API is served by `api_server.py` and runs on port 5002.

### General

-   `GET /`: API information and root status.
-   `GET /health`: Health check for the API server and its core modules.

### Authentication (via FastAPI)

-   `POST /api/auth/login`: Authenticate user and return access token. (Placeholder implemented)
    -   Body: `username`, `password`
-   `POST /api/auth/register`: Register a new user. (Placeholder implemented)
    -   Body: `username`, `password`
-   `POST /api/auth/logout`: (To be implemented or verified)
-   `GET /api/auth/validate`: (To be implemented or verified)

### Market Data & Analysis

-   `GET /api/market/prices`: Get latest prices for a list of common cryptocurrencies.
-   `GET /api/market/analysis`: Get market analysis for a specific token and timeframe.
    -   Query params: `token`, `timeframe`
-   `GET /api/binance/ticker`: Proxy to fetch ticker price from Binance.
    -   Query params: `symbol`
-   `GET /api/market/price/{token}`: (Covered by `/api/market/prices`; client can filter)
-   `GET /api/market/chart/{token}`: (To be implemented or verified)
-   `GET /api/market/orderbook/{token}`: (To be implemented or verified)

### Trading

-   `POST /api/trading/execute`: Execute a trade.
    -   Body: `{action, token, network, amount, slippage, wallet}`
-   `GET /api/trading/strategies`: Get AI-generated trading strategies.
    -   Query params: `token`, `risk_profile`
-   `GET /api/trading/positions`: (To be implemented or verified)
-   `GET /api/trading/history`: (To be implemented or verified)

### Portfolio & Risk Management

-   `GET /api/portfolio/summary`: Get portfolio summary.
-   `POST /api/liquidation/price`: Calculate liquidation price for a position.
    -   Body: `{collateral_token, collateral_amount, debt_token, debt_amount}`
-   `POST /api/liquidation/borrowable`: Calculate maximum borrowable amount.
    -   Body: `{collateral_token, collateral_amount, borrow_token, buffer_percent}`
-   `GET /api/portfolio/performance`: (To be implemented or verified)
-   `GET /api/risk/metrics`: (To be implemented or verified)

### Layer 2 & Cross-Chain Operations

-   `GET /api/networks`: Get all supported networks with their details.
-   `GET /api/networks/compare`: Compare metrics across networks for a token.
    -   Query params: `token`
-   `GET /api/gas/prices`: Get gas prices across all networks.
-   `GET /api/gas/network/{network_id}`: Get gas price for a specific network.
-   `GET /api/bridging/estimate`: Estimate costs for bridging tokens between networks.
    -   Query params: `from_network`, `to_network`, `amount`
-   `GET /api/arbitrage/opportunities`: Get arbitrage opportunities for a specific token. (Formerly `/api/chains/opportunities`)
    -   Query params: `token`
-   `GET /api/arbitrage/strategies`: Get arbitrage strategies across multiple tokens.
-   `GET /api/optimizer/network`: Recommend the best network for a specific transaction.
    -   Query params: `token`, `transaction_type`, `amount`
-   `GET /api/optimizer/path`: Find best path for cross-network token exchange.
    -   Query params: `from_token`, `to_token`, `amount`
-   `GET /api/chains/liquidity/{token}`: (To be implemented or verified)
-   `POST /api/chains/bridge`: (To be implemented or verified)

### Rehoboam AI Analysis

-   `GET /api/ai/emotions`: Get market emotional state analysis from Rehoboam.
-   `GET /api/ai/consciousness-state`: Get the current state of Rehoboam's consciousness layers.
-   `POST /api/ai/reason`: Use Rehoboam's advanced multi-model reasoning capabilities.
    -   Query params: `prompt`, `task_type`, `complexity`
-   `GET /api/ai/market-intelligence/{token}`: Get comprehensive market intelligence for a token. (Covers old `/api/ai/sentiment`)
-   `POST /api/ai/mcp-function`: Execute a registered MCP function.
    -   Query params: `function_name`, `parameters` (body)
-   `GET /api/ai/prediction/{token}`: (To be implemented or verified)
-   `GET /api/ai/regime`: (To be implemented or verified)

### Blockchain Analysis (Etherscan-based)

-   `POST /api/blockchain/analyze-wallet`: Analyze wallet behavior.
    -   Query params: `address`, `transaction_limit`
-   `POST /api/blockchain/detect-mev`: Detect MEV opportunities and patterns for an address.
    -   Query params: `address`
-   `GET /api/blockchain/intelligence/{address}`: Get comprehensive blockchain intelligence for an address.
-   `GET /api/blockchain/whale-activity`: Monitor whale activity.
    -   Query params: `min_value_eth`
-   `POST /api/blockchain/analyze-contract`: Analyze smart contract security.
    -   Query params: `contract_address`

### User Preferences

-   `GET /api/preferences`: Get user preferences (requires auth).
-   `POST /api/preferences/update`: Update user preferences (requires auth).
    -   Body: `{ "category": { "key": "value" } }`
-   `POST /api/preferences/reset`: Reset user preferences (requires auth).
    -   Query params: `category` (optional)

### AI Companions API

-   Endpoints for creating and interacting with AI companions are available under the `/companions` prefix (e.g., `/companions/`, `/companions/{name}/interact`). These are defined in [`api_companions.py`](api_companions.py:1).

### Model Context Protocol (MCP) API

-   Endpoints for managing and visualizing MCP functions are available under the `/mcp` prefix (e.g., `/mcp/functions`, `/mcp/ws`). These are defined in [`api_mcp.py`](api_mcp.py:1).

### System Management (Legacy/Review Needed)

-   `GET /api/system/status`: (Functionality covered by `/health` on the FastAPI server)
-   `GET /api/system/logs`: (To be implemented or verified)
-   `POST /api/system/config`: (To be implemented or verified)

### Example Response Format
```json
{
    "success": true, // Typically true for 2xx, false otherwise
    "data": {
        // Endpoint specific data
    },
    "metadata": { // Optional metadata
        "timestamp": "2024-01-26T12:34:56Z",
        "version": "1.0.0" // API version
    },
    "error": null // Error object if success is false
}
```

### Error Response Format
```json
{
    "success": false,
    "data": null,
    "error": {
        "code": "ERROR_CODE_STRING", // e.g., "VALIDATION_ERROR", "NOT_FOUND"
        "message": "Human readable error message",
        "details": {} // Optional, more specific error details
    }
}
```
(Note: FastAPI uses a `detail` field for HTTPException by default, which might be a string or a more structured object. The above is a general guide.)

### Rate Limits
(These are indicative and may need to be configured/verified)
- Authentication endpoints: 5 requests per minute
- Market data endpoints: 60 requests per minute
- Trading endpoints: 30 requests per minute
- AI analysis endpoints: 20 requests per minute

### WebSocket Endpoints (FastAPI - `api_server.py`)

Base URL: `ws://localhost:5002` (or your API host)

-   `/ws/market`: Real-time market data updates.
-   `/ws/trades`: Real-time trade execution updates.
-   `/ws/portfolio`: Real-time portfolio updates.
-   `/ws/strategies`: Real-time trading strategy updates and interactions.
-   `/ws/preferences`: Real-time user preference synchronization.
-   `/ws/trading`: General trading activity channel.
-   `/ws/arbitrage`: Real-time arbitrage opportunity updates.

Additional WebSocket endpoints for AI Companions (`/companions/ws`) and MCP (`/mcp/ws`) are also available, managed by their respective routers.

## Frontend Integration Guide
(This section remains largely the same but should be tested against the FastAPI backend)

### API Client Setup
```typescript
// api/client.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.VITE_API_URL || 'http://localhost:5002', // Ensure this points to FastAPI
  timeout: Number(process.env.API_TIMEOUT) || 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### WebSocket Connection
(The `WebSocketManager` class can connect to the FastAPI WebSocket endpoints. The `process.env.WS_BASE_URL` should point to `ws://localhost:5002` or similar.)
```typescript
// utils/websocket.ts
export class WebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private url: string;

  constructor(endpoint: string) {
    // Example: endpoint could be '/ws/market', '/ws/trades'
    this.url = (process.env.VITE_WS_BASE_URL || 'ws://localhost:5002') + endpoint;
  }
  
  connect(onMessageCallback: (data: any) => void) {
    this.ws = new WebSocket(this.url);
    
    this.ws.onopen = () => {
      console.log(`WebSocket connected to ${this.url}`);
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data as string);
        onMessageCallback(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.ws.onclose = () => {
      console.log(`WebSocket disconnected from ${this.url}`);
      this.reconnect();
    };

    this.ws.onerror = (error) => {
      console.error(`WebSocket error on ${this.url}:`, error);
      // onclose will be called, triggering reconnect
    };
  }

  private reconnect() {
    if (this.reconnectAttempts < (Number(process.env.WS_MAX_RECONNECT_ATTEMPTS) || 5)) {
      const timeout = Math.pow(2, this.reconnectAttempts) * 1000; // Exponential backoff
      console.log(`Attempting to reconnect to ${this.url} in ${timeout / 1000}s...`);
      setTimeout(() => {
        // Ensure onMessageCallback is passed again if needed, or manage subscriptions
        // this.connect(onMessageCallback); // This needs careful handling of the callback
      }, timeout);
      this.reconnectAttempts++;
    } else {
      console.error(`Max reconnect attempts reached for ${this.url}`);
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.error('WebSocket not connected. Cannot send message.');
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}
```
(The example `WebSocketManager` has been slightly adjusted for clarity and to accept an endpoint path.)

### Example Usage in React Components
(These examples should now target the FastAPI endpoints)

#### Market Analysis Page
```typescript
// pages/MarketAnalysis.tsx
import { useState, useEffect } from 'react';
import api from '../api/client'; // Assuming api client is set up

export const MarketAnalysis = () => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchAnalysis = async (token: string, timeframe: string = "1h") => {
    try {
      setLoading(true);
      // Updated to match FastAPI endpoint
      const response = await api.get(`/api/market/analysis?token=${token}&timeframe=${timeframe}`);
      setAnalysis(response.data);
    } catch (error) {
      console.error('Error fetching analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    // ... your JSX
  );
};
```

#### Trading Execution
```typescript
// components/TradingForm.tsx
import { useState } from 'react';
import api from '../api/client'; // Assuming api client is set up

export const TradingForm = () => {
  const [order, setOrder] = useState({
    action: 'buy', // 'buy' or 'sell'
    token: 'ETH',
    network: 'arbitrum', // Example network
    amount: 0,
    slippage: 1, // Percentage
    // wallet: 'user_wallet_address_here' // This should come from Web3Context
  });

  const executeTrade = async () => {
    try {
      // Ensure wallet address is included from context
      // const tradeDataWithWallet = { ...order, wallet: accountFromWeb3Context };
      const response = await api.post('/api/trading/execute', order);
      // Handle successful trade
    } catch (error) {
      // Handle error
    }
  };

  return (
    // ... your JSX
  );
};
```

#### Portfolio Dashboard
```typescript
// pages/Portfolio.tsx
import { useState, useEffect } from 'react';
import api from '../api/client'; // Assuming api client is set up

export const Portfolio = () => {
  const [portfolio, setPortfolio] = useState(null);
  // const [performance, setPerformance] = useState(null); // Performance endpoint TBD

  const fetchPortfolioData = async () => {
    try {
      const portfolioRes = await api.get('/api/portfolio/summary');
      // const performanceRes = await api.get('/api/portfolio/performance?timeframe=1w'); // TBD
      
      setPortfolio(portfolioRes.data);
      // setPerformance(performanceRes.data);
    } catch (error) {
      console.error('Error fetching portfolio data:', error);
    }
  };

  useEffect(() => {
    fetchPortfolioData();
  }, []);

  return (
    // ... your JSX
  );
};
```

### Error Handling & Rate Limiting
(These utility examples remain conceptually valid but ensure environment variables for rate limits match backend configuration if implemented.)

## Known Issues

1.  **API Endpoint Coverage:** Some API endpoints listed in previous versions of this README (e.g., detailed trading history, specific chart data, logout) are not yet fully implemented or verified in the primary FastAPI server ([`api_server.py`](api_server.py:1)).
2.  **Authentication Implementation:** Authentication endpoints (`/api/auth/login`, `/api/auth/register`) are currently placeholders and require full implementation with secure credential handling and session management.
3.  **Environment Variables:** Ensure all required API keys and secrets (e.g., `JWT_SECRET`) are correctly configured in `.env`.
4.  **Wallet Integration:** Frontend error handling for wallet connection failures and chain switching needs to be robust.
5.  **Flask Application:** The role of the auxiliary Flask application ([`run.py`](run.py:1), `trading_platform/`) needs clarification, as local development now defaults to the FastAPI server. It might be deprecated or its unique functionalities migrated.

## To-Do

1.  **API Implementation & Refinement**:
    -   Fully implement authentication and authorization.
    -   Implement remaining critical API endpoints (trading history, positions, chart data, etc.).
    -   Review and refine existing API endpoint logic for robustness and security.
2.  **Backend Consolidation**:
    -   Migrate any necessary unique functionalities from the Flask app to the main FastAPI application.
    -   Remove Flask-related dependencies if fully consolidated.
3.  **Documentation**:
    -   Keep this API documentation (`README.md`) fully synchronized with `api_server.py`.
    -   Improve inline code documentation across frontend and backend.
    -   Add detailed architecture diagrams.
4.  **Frontend Enhancements**:
    -   Implement comprehensive error boundary handling.
    -   Ensure proper loading states for all network operations.
    -   Add support for more wallets (e.g., WalletConnect).
5.  **Testing**:
    -   Expand unit, integration, and end-to-end test coverage for both frontend and backend.

See [`USAGE.md`](USAGE.md:1) for detailed usage instructions.
