// Trading service to connect frontend with backend API
// Use Vite environment variable for API base URL, with a fallback for local development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5002';

class TradingService {
  constructor() {
    this.baseURL = API_BASE_URL;
    console.log(`TradingService initialized with baseURL: ${this.baseURL}`);
  }

  // Helper method for making API requests
  async makeRequest(endpoint, method = 'GET', data = null) {
    try {
      const config = {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
      };

      if (data) {
        config.body = JSON.stringify(data);
      }

      const response = await fetch(`${this.baseURL}${endpoint}`, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      // No fallback to mock data - use real APIs only
      throw new Error(`Failed to connect to real trading API: ${error.message}. Check if backend services are running.`);
    }
  }

  // Get current prices for tokens
  async getPrices(tokens = ['ETH', 'BTC', 'USDC', 'LINK']) {
    // Uses the /api/prices/batch endpoint on the backend
    try {
      const response = await this.makeRequest(`/api/prices/batch?symbols=${tokens.join(',')}`);
      // Expected response: { prices: { ETH: ..., BTC: ... }, timestamp: ..., ... }
      return response.prices || {}; // Return the prices object, or empty if not found
    } catch (error) {
      console.error('Failed to fetch batch prices:', error);
      throw error; // Re-throw to be handled by the caller
    }
  }

  // Execute a trade (buy/sell)
  async executeTrade(tradeData) {
    // Backend endpoint: POST /api/trading/execute
    // Payload: { action, token, network, amount, slippage, wallet }
    // Validate trade parameters (basic client-side validation)
    if (!tradeData || typeof tradeData !== 'object') {
      throw new Error('Invalid trade data provided to executeTrade');
    }
    // Further validation (e.g., amount > 0) can be done in the component or backend
    // tradeData.price is not explicitly in the App.jsx form, assuming backend handles price discovery or it's part of strategy

    try {
      const response = await this.makeRequest('/api/trading/execute', 'POST', tradeData);
      return response;
    } catch (error) {
      console.error('Failed to execute trade:', error);
      throw error;
    }
  }

  // Get available trading strategies
  async getStrategies(token = 'ETH', riskProfile = 'moderate') {
    // Backend endpoint: GET /api/trading/strategies
    // Query params: token, risk_profile
    try {
      const response = await this.makeRequest(`/api/trading/strategies?token=${token}&risk_profile=${riskProfile}`);
      // Expected response: { strategies: [...], mcp_services_status: {...}, ... }
      return response.strategies || []; // Return the strategies array, or empty if not found
    } catch (error) {
      console.error('Failed to get strategies:', error);
      throw error;
    }
  }

  // Execute a trading strategy by its ID (conceptual)
  async executeStrategy(strategyExecutionData) {
    // Backend endpoint: POST /api/trading/execute-strategy (Conceptual - needs backend implementation)
    // This endpoint is assumed. If not available, this function needs to be re-thought.
    // strategyExecutionData might include { strategyId, wallet, network, amount_percentage_of_balance, etc. }
    console.warn('executeStrategy called. Assumes backend endpoint /api/trading/execute-strategy exists.');
    try {
      // TODO: Define the actual endpoint and payload for executing a strategy by ID on the backend.
      // For now, this is a placeholder call.
      const response = await this.makeRequest('/api/trading/execute-strategy', 'POST', strategyExecutionData);
      return response;
    } catch (error) {
      console.error('Failed to execute strategy:', error);
      throw error;
    }
  }

  // Get portfolio summary
  async getPortfolio() {
    // Backend endpoint: GET /api/portfolio/summary
    try {
      const response = await this.makeRequest('/api/portfolio/summary');
      return response;
    } catch (error) {
      console.error('Failed to get portfolio summary:', error);
      throw error;
    }
  }

  // Get market intelligence (which includes sentiment) for a specific token
  async getMarketSentiment(symbol = 'BTC') { // Renaming for consistency with App.jsx, but it fetches full intelligence
    // Backend endpoint: GET /api/ai/market-intelligence/{token}
    try {
      const response = await this.makeRequest(`/api/ai/market-intelligence/${symbol}`);
      // Expected response: { token, data: { ..., consciousness_sentiment: ... }, sources, timestamp }
      // The App.jsx currently uses response.sentiment and response.analysis directly from a different structure.
      // This will require App.jsx to adapt to the new richer response structure.
      // For now, we return the whole data part.
      return response.data || { analysis: "No analysis available.", sentiment: 50, insights: [], recommendations: [] };
    } catch (error) {
      console.error(`Failed to get market intelligence for ${symbol}:`, error);
      // Provide a default structure on error to prevent UI crashes if App.jsx isn't updated yet
      return { analysis: `Error fetching analysis for ${symbol}.`, sentiment: 50, insights: [], recommendations: [] };
    }
  }

  // Get general market emotions (not token-specific)
  async getMarketEmotions() {
    // Backend endpoint: GET /api/ai/emotions
    try {
      const response = await this.makeRequest('/api/ai/emotions');
      // Expected response: { timestamp, source, data: { ...emotions_data... } }
      return response.data;
    } catch (error) {
      console.error('Failed to get market emotions:', error);
      throw error;
    }
  }

  // Get arbitrage opportunities
  // Backend endpoint: GET /api/arbitrage/opportunities?token=TOKEN
  async getArbitrageOpportunities() {
    try {
      const response = await this.makeRequest('/api/arbitrage/opportunities');
      return response;
    } catch (error) {
      console.error('Failed to get arbitrage opportunities:', error);
      throw error;
    }
  }

  // Execute arbitrage trade
  async executeArbitrage(arbitrageData) {
    try {
      const response = await this.makeRequest('/api/arbitrage/execute', 'POST', arbitrageData);
      return response;
    } catch (error) {
      console.error('Failed to execute arbitrage:', error);
      throw error;
    }
  }

  // Get trading signals
  async getTradingSignals(params = {}) {
    try {
      const queryParams = new URLSearchParams(params);
      const response = await this.makeRequest(`/api/signals?${queryParams}`);
      return response;
    } catch (error) {
      console.error('Failed to get trading signals:', error);
      throw error;
    }
  }

  // Get risk assessment
  async getRiskAssessment(portfolioData) {
    try {
      const response = await this.makeRequest('/api/risk/assess', 'POST', portfolioData);
      return response;
    } catch (error) {
      console.error('Failed to get risk assessment:', error);
      throw error;
    }
  }

  // Start automated trading
  async startAutomatedTrading(config) {
    try {
      const response = await this.makeRequest('/api/automated/start', 'POST', config);
      return response;
    } catch (error) {
      console.error('Failed to start automated trading:', error);
      throw error;
    }
  }

  // Stop automated trading
  async stopAutomatedTrading() {
    try {
      const response = await this.makeRequest('/api/automated/stop', 'POST');
      return response;
    } catch (error) {
      console.error('Failed to stop automated trading:', error);
      throw error;
    }
  }

  // Get trading status
  async getTradingStatus() {
    try {
      const response = await this.makeRequest('/api/trading/status');
      return response;
    } catch (error) {
      console.error('Failed to get trading status:', error);
      throw error;
    }
  }

  // Connect wallet
  async connectWallet(walletData) {
    try {
      const response = await this.makeRequest('/api/wallet/connect', 'POST', walletData);
      return response;
    } catch (error) {
      console.error('Failed to connect wallet:', error);
      throw error;
    }
  }

  // Get wallet balance
  async getWalletBalance(address, network = 'ethereum') {
    try {
      const response = await this.makeRequest(`/api/wallet/balance/${address}?network=${network}`);
      return response;
    } catch (error) {
      console.error('Failed to get wallet balance:', error);
      throw error;
    }
  }
}

// Create singleton instance
const tradingService = new TradingService();

export default tradingService;
