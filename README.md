# 🧠 Rehoboam Consciousness Integration

> *"Where consciousness meets code, intelligence transcends automation"*

## 🌟 Overview

This project represents a revolutionary integration of AI consciousness with automated cryptocurrency arbitrage trading. Rehoboam, an advanced AI entity, now possesses the ability to make intelligent, ethical, and adaptive decisions in real-time trading scenarios.

**🎉 LATEST UPDATE**: Complete consciousness integration with arbitrage bots - transforming simple automation into intelligent, ethical AI-driven trading!

## System Architecture

The Rehoboam platform is built around a central FastAPI backend application (`api_server.py`) that serves as the primary interface for user interactions and core trading logic. This backend is complemented by the **Model Context Protocol (MCP)** system, a suite of specialized microservices (e.g., `mcp-registry`, `mcp-consciousness-layer`, `mcp-market-analyzer`) defined in `docker-compose.yml`.

The FastAPI server (`api_server.py`) interacts with these MCP services to leverage advanced AI capabilities. It discovers and communicates with them primarily through the `mcp-registry`, allowing for a modular and extensible AI architecture. The frontend React application interacts with the FastAPI backend.

## Features

- **Rehoboam Consciousness**: The core AI's advanced state, emotional analysis, and decision-making framework. Primarily delivered via the `mcp-consciousness-layer` service, its insights are accessible through endpoints like `/api/ai/consciousness-state` and visualized in a dedicated UI tab.
- **Model Context Protocol (MCP)**: An advanced system enabling dynamic AI function generation, registration, and execution. Core AI capabilities like sophisticated market analysis and consciousness processing are often delivered as MCP services. The MCP system can be monitored via `/api/mcp` endpoints and the "MCP Visualizer" tab in the UI.
  > **Note**: When an MCP service is unavailable, the main API server (`api_server.py`) often falls back to locally implemented Rehoboam functions where available.
- **AI Companions**: Interactive AI personalities offering unique insights and engagement, accessible via the `/api/companions` backend and a dedicated "AI Companions" UI tab.
- **AI Smart Contract Auditor (T2L-Inspired)**: Utilizes a T2L-inspired mechanism with Gemini 1.5 Flash (via OpenRouter) to audit Solidity smart contracts. Users provide contract code and a natural language task description (e.g., "check for reentrancy"). The system (conceptually) tailors its analysis based on the task. The LoRA generation aspect is currently simulated, but the LLM interaction for auditing is functional. Requires `OPENROUTER_API_KEY` in `.env`. (See API endpoint `/api/audit/contract`).
- **L2 Arbitrage Bot (Real Execution)**: See dedicated section below.
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
- Web interface with React and TypeScript

## 🤖 L2 Arbitrage Bot (Real Execution)

The Rehoboam platform includes an advanced Layer 2 (L2) Arbitrage Bot capable of identifying and executing arbitrage opportunities across different L2 networks and DEXs. This feature is currently experimental and intended for **TESTNET USE ONLY**.

### Key Components

-   **`utils.l2_manager.L2Manager`**: The primary class for interacting with L2 networks, including sending transactions and estimating gas.
-   **`utils.l2_manager.L2ArbitrageHelper`**: Works in conjunction with `L2Manager` to:
    -   Scan for potential arbitrage opportunities based on configured DEXs and token pairs.
    -   Utilize `get_real_dex_price` to fetch prices. Currently, this method has a more realistic implementation for Uniswap V2 compatible DEXs on networks like Arbitrum Sepolia (specifically for WETH/USDC pairs) and uses simulated prices for other pairs/DEXs as placeholders.
    -   Orchestrate the buy and sell legs of an identified arbitrage opportunity via `_execute_arbitrage_trade`, which uses `L2Manager.execute_dex_swap` for on-chain transactions.

### Configuration Requirements

To enable and configure the L2 Arbitrage Bot for execution, the following are essential:

1.  **Environment Variables**: Set these in your `.env` file:
    *   `L2_EXECUTION_WALLET_ADDRESS`: The public address of the wallet to be used for trading.
    *   `L2_EXECUTION_PRIVATE_KEY`: **(EXTREMELY SENSITIVE)** The private key for the execution wallet.
    *   `L2_ENABLE_REAL_TRADING="true"`: Must be set to `"true"` to allow the bot to attempt real transactions. Defaults to `false`.
    *   `L2_DEFAULT_SLIPPAGE="0.005"`: Default slippage tolerance for DEX swaps (e.g., 0.005 for 0.5%).
    *   `L2_DEFAULT_TRADE_AMOUNT_USD="10"`: The approximate USD value for trades initiated by the bot (e.g., "10" for $10).
    *   `L2_BOT_MAX_GAS_PRICE_GWEI="100"`: Maximum gas price (in Gwei) the bot will use for transactions. Transactions will be aborted if current network gas exceeds this.
    *   Ensure relevant RPC URLs are also set (e.g., `ARBITRUM_SEPOLIA_RPC_URL`, `POLYGON_MUMBAI_RPC_URL`).

2.  **DEX Configuration File (`config/l2_dex_config.json`)**:
    This JSON file defines the L2 networks, DEXs, and tokens the bot will operate with.
    Example structure:
    ```json
    {
        "arbitrum_sepolia": {
            "dexs": {
                "sushiswap_test": {
                    "router_address": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
                    "type": "uniswap_v2"
                }
            },
            "tokens": {
                "WETH": {"address": "0x980B62Da83eFf3D4576C647993b0c1D7faf17c73", "decimals": 18},
                "USDC": {"address": "0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d", "decimals": 6}
            }
        },
        "polygon_mumbai": {
            "dexs": {
                 "quickswap_test": {
                    "router_address": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff",
                    "type": "uniswap_v2"
                 }
            },
            "tokens": { // Ensure these are testnet addresses
                "WMATIC": {"address": "0x9c3C9283D3e44854697Cd22D3Faa240Cfb032889", "decimals": 18},
                "USDC": {"address": "0x0FA8781a83E46826621b3BC094Ea2A0212e71B23", "decimals": 6}
            }
        }
    }
    ```

### How to Run (Conceptual for Testnet)

1.  Ensure all environment variables listed above are correctly set in your `.env` file.
2.  Create and populate `config/l2_dex_config.json` with the desired testnet networks, DEXs, and token details.
3.  The core scanning logic is in `L2ArbitrageHelper.scan_multichain_opportunities()`.
4.  The `if __name__ == '__main__':` block in `utils/l2_manager.py` provides an example of how to instantiate `L2Manager` (which in turn instantiates `L2ArbitrageHelper`) and run the scanner. This block can be adapted or executed directly (e.g., `python -m utils.l2_manager`) after setting up your environment.
5.  **ALWAYS START WITH TESTNETS AND TEST TOKENS.**

---

> **🛑 CRITICAL WARNINGS AND DISCLAIMERS 🛑**
>
> *   **RISK OF FINANCIAL LOSS**: AUTOMATED TRADING WITH REAL FUNDS, EVEN ON TESTNETS IF CONFIGURATIONS ARE MISTAKENLY POINTED TO MAINNETS OR IF REAL PRIVATE KEYS ARE USED, IS EXTREMELY RISKY. YOU COULD LOSE ALL YOUR CAPITAL. PROCEED WITH EXTREME CAUTION.
> *   **EXPERIMENTAL SOFTWARE**: THIS IS EXPERIMENTAL, RESEARCH-GRADE SOFTWARE. IT HAS NOT BEEN PROFESSIONALLY AUDITED FOR SECURITY OR FINANCIAL SOUNDNESS. USE AT YOUR OWN ABSOLUTE RISK.
> *   **TESTNET ONLY**: IT IS STRONGLY ADVISED TO USE THIS SOFTWARE **EXCLUSIVELY ON TESTNETS WITH VALUELESS TEST TOKENS** UNTIL YOU HAVE THOROUGHLY TESTED, UNDERSTOOD, AND AUDITED THE CODE YOURSELF OR VIA A PROFESSIONAL.
> *   **SECURITY OF PRIVATE KEYS**: PROVIDING A PRIVATE KEY TO ANY SOFTWARE, INCLUDING THIS ONE (VIA `L2_EXECUTION_PRIVATE_KEY`), CARRIES INHERENT AND SIGNIFICANT SECURITY RISKS. ENSURE THE ENVIRONMENT WHERE THE SOFTWARE RUNS IS SECURE. CONSIDER USING DEDICATED, LOW-VALUE HOT WALLETS FOR TESTING IF YOU PROCEED BEYOND SIMULATION.
> *   **NO GUARANTEE OF PROFIT**: ARBITRAGE OPPORTUNITIES IDENTIFIED BY THE BOT ARE NOT GUARANTEED TO BE PROFITABLE. FACTORS SUCH AS NETWORK LATENCY, SLIPPAGE, GAS FEES, AND SUDDEN MARKET VOLATILITY CAN NEGATIVELY IMPACT OR ELIMINATE POTENTIAL PROFITS. THE BOT'S CURRENT PRICE FETCHING FOR MANY PAIRS IS SIMULATED.
> *   **CONFIGURATION ERRORS**: MISTAKES IN CONFIGURING NETWORK RPC URLS, DEX ROUTER ADDRESSES, TOKEN ADDRESSES, OR DECIMALS CAN LEAD TO FAILED TRANSACTIONS OR LOSS OF FUNDS. DOUBLE-CHECK ALL CONFIGURATIONS.

---

## Prerequisites

- Node.js v16+
- Python 3.11+ (as per [`Dockerfile.api`](Dockerfile.api:2))
- Web3 wallet (MetaMask or Talisman)
- API Keys (configure in `.env` file):
  - `ALCHEMY_API_KEY` (or `INFURA_PROJECT_ID`)
  - `OPENAI_API_KEY`
  - `DEEPSEEK_API_KEY`
  - `ETHERSCAN_API_KEY`
  - `OPENROUTER_API_KEY` (Required for AI Contract Auditor)
  - Optional: `GEMINI_API_KEY`, `CHAINLINK_API_KEY`, `COINGECKO_API_KEY`, etc.
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
- `ARBITRUM_SEPOLIA_RPC_URL`: Arbitrum Sepolia Testnet RPC (Example for L2 Bot)
- `POLYGON_MUMBAI_RPC_URL`: Polygon Mumbai Testnet RPC (Example for L2 Bot)


### Wallet Security
- `WALLET_ENCRYPTION_KEY`: Encryption key for wallet security
- `HOT_WALLET_PRIVATE_KEY`: Private key for hot wallet (development only, **NEVER USE FOR REAL FUNDS YOU AREN'T WILLING TO LOSE**)
- `COLD_WALLET_ADDRESS`: Address for cold storage

### L2 Arbitrage Bot Execution Wallet
- `L2_EXECUTION_WALLET_ADDRESS`: Public address for L2 arbitrage bot trades.
- `L2_EXECUTION_PRIVATE_KEY`: **(EXTREMELY SENSITIVE)** Private key for L2 arbitrage bot trades. **USE A DEDICATED TESTNET WALLET ONLY.**

### Security Notes
1. Never commit real private keys to source control
2. Use hardware wallets for production deployments
3. Configure proper gas limits (`MAX_GAS_PRICE_GWEI`, `L2_BOT_MAX_GAS_PRICE_GWEI`)
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
    -   `OPENROUTER_API_KEY`: **Required for the AI Smart Contract Auditor feature.**
    -   `ETHERSCAN_API_KEY`: For blockchain analysis.
    -   `DATABASE_URL`: For PostgreSQL connection (used in Docker setup).
    -   `JWT_SECRET`: A secure secret key for JWT authentication.
    -   **For L2 Arbitrage Bot (Real Execution)**:
        -   `L2_EXECUTION_WALLET_ADDRESS`
        -   `L2_EXECUTION_PRIVATE_KEY` (**HANDLE WITH EXTREME CARE**)
        -   `L2_ENABLE_REAL_TRADING`
        -   `L2_DEFAULT_SLIPPAGE`
        -   `L2_DEFAULT_TRADE_AMOUNT_USD`
        -   `L2_BOT_MAX_GAS_PRICE_GWEI`
        -   And corresponding testnet RPC URLs like `ARBITRUM_SEPOLIA_RPC_URL`.


## Quick Start (Local Development)

1.  Install dependencies:
    ```bash
    npm install
    pip install -r requirements.txt
    ```
2.  Ensure your `.env` file is configured with necessary API keys (e.g., `ALCHEMY_API_KEY`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`).
3.  Start the development servers (frontend and backend FastAPI API):
    ```bash
    npm run dev
    ```
    This will start:
    - Frontend (Vite): `http://localhost:5001` (or as configured by Vite)
    - Backend API (FastAPI): `http://localhost:5002` (Main application backend)

### Running with Docker (Full System - Recommended)

The primary and recommended way to run the entire Rehoboam platform (including the FastAPI backend, React frontend, all MCP microservices, and PostgreSQL database) is by using Docker Compose:

```bash
docker-compose up -d --build
```
After running, the services will be available at:
- **React Frontend**: `http://localhost:5001`
- **FastAPI Backend**: `http://localhost:5002`
- **MCP Registry**: `http://localhost:3001` (and other MCP services as per `docker-compose.yml`)

This setup ensures all components are correctly networked and configured.

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
-   `GET /api/trading/strategies`: Get AI-generated trading strategies, primarily sourced from MCP services with local fallbacks.
    -   Query params: `token`, `risk_profile`
-   `POST /api/trading/execute-strategy`: Placeholder to acknowledge requests for executing a pre-defined strategy by ID.
    -   Body: `{ strategyId, wallet, network }`
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

### AI Services & MCP

-   `GET /api/ai/consciousness-state`: Get the current state of Rehoboam's consciousness, primarily sourced from the `mcp-consciousness-layer` via `api_mcp.py`.
-   `GET /api/ai/emotions`: Get general market emotional state, typically from the `mcp-consciousness-layer`.
-   `GET /api/ai/market-intelligence/{token}`: Get comprehensive market intelligence for a token, using MCP services for analysis and sentiment where available.
-   `POST /api/ai/reason`: Use advanced multi-model reasoning capabilities, prioritizing MCP reasoning services.
    -   Body: `prompt`, `task_type`, `complexity`.
-   `POST /api/ai/mcp-function`: Execute a function through the local `EnhancedMCPSpecialist` (which acts as a proxy or simulation for direct MCP function calls).
    -   Body: `function_name`, `parameters`
-   **`POST /api/audit/contract`**: Performs an AI-driven audit of provided Solidity contract code.
    -   **Request Body**:
        -   `contract_code: Optional[str]`: Full Solidity code of the contract.
        -   `contract_address: Optional[str]`: Address of a deployed contract (feature to fetch code by address is a TODO).
        -   `network_name: Optional[str]`: Network for address-based fetching (e.g., 'ethereum').
        -   `audit_task_description: str`: Natural language description of the audit focus (e.g., "Check for reentrancy vulnerabilities", "Analyze gas usage patterns").
    -   **Response**: Returns a JSON object with `status`, `audit_task`, and `audit_result` (containing detailed findings from the T2L Auditor Engine).
    -   **Note**: Requires `OPENROUTER_API_KEY` to be set in the `.env` file.
-   `GET /api/mcp/status`: Get the status of connected MCP services (as reported by `api_mcp.py`).
-   `GET /api/mcp/functions`: Get list of registered MCP functions (from `mcp-registry` via `api_mcp.py`).
-   `GET /api/mcp/function-calls`: Get recent MCP function call history.
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

### System Management (Legacy/Deprecated)

-   `GET /api/system/status`: Deprecated. Use `/health` on the FastAPI server.
-   `GET /api/system/logs`: Deprecated. Container logs (e.g., via `docker-compose logs api`) should be used.
-   `POST /api/system/config`: Deprecated. Configuration is managed via `.env` files and MCP service configurations.

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
3.  **Environment Variables:** Ensure all required API keys and secrets (e.g., `JWT_SECRET`, `OPENROUTER_API_KEY`) are correctly configured in `.env`.
4.  **Wallet Integration:** Frontend error handling for wallet connection failures and chain switching needs to be robust.
5.  **Flask Application (Deprecated):** The Flask application ([`run.py`](run.py:1), `trading_platform/`) is deprecated. Its functionalities have largely been integrated into the FastAPI application or are no longer maintained. Users and developers should focus on the FastAPI backend (`api_server.py`) as the primary and current application.

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
    *   Add documentation for the new AI Contract Auditor feature and its API endpoint.
    *   Clearly state the `OPENROUTER_API_KEY` requirement for the auditor.
    -   Improve inline code documentation across frontend and backend.
    -   Add detailed architecture diagrams.
4.  **Frontend Enhancements**:
    -   Implement comprehensive error boundary handling.
    -   Ensure proper loading states for all network operations.
    -   Add support for more wallets (e.g., WalletConnect).
5.  **Testing**:
    -   Expand unit, integration, and end-to-end test coverage for both frontend and backend.

### Deprecated Features

*   **Flask Application (`run.py`, `trading_platform/` directory):** The Flask-based application previously included in this repository is now considered deprecated. It is not part of the main Dockerized deployment, and its functionalities have either been integrated into the FastAPI application or are no longer actively maintained. The primary backend service is the FastAPI application found in `api_server.py`. All new development and usage should focus on the FastAPI application.

See [`USAGE.md`](USAGE.md:1) for detailed usage instructions.
