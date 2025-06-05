// Trading service to connect frontend with backend API
const API_BASE_URL = 'http://localhost:5002';

class TradingService {
  constructor() {
    this.baseURL = API_BASE_URL;
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

  // Get current prices for tokens using real Chainlink and API data
  async getPrices(tokens = ['ETH', 'BTC', 'USDC']) {
    try {
      const prices = {};
      for (const token of tokens) {
        const response = await this.makeRequest(`/api/price/${token}`);
        prices[token] = response.price;
      }
      return prices;
    } catch (error) {
      console.error('Failed to fetch prices:', error);
      throw error;
    }
  }

  // Execute a trade (buy/sell)
  async executeTrade(tradeData) {
    // Validate trade parameters
    if (!tradeData || typeof tradeData !== 'object') {
      throw new Error('Invalid trade data');
    }
    if (tradeData.price <= 0) {
      throw new Error('Trade price must be greater than zero');
    }
    if (tradeData.amount <= 0) {
      throw new Error('Trade amount must be greater than zero');
    }
    try {
      const response = await this.makeRequest('/api/trading/execute', 'POST', tradeData);
      return response;
    } catch (error) {
      console.error('Failed to execute trade:', error);
      throw error;
    }
  }

  // Get available trading strategies
  async getStrategies() {
    try {
      const response = await this.makeRequest('/api/strategies');
      return response;
    } catch (error) {
      console.error('Failed to get strategies:', error);
      throw error;
    }
  }

  // Execute a trading strategy
  async executeStrategy(strategyData) {
    try {
      const response = await this.makeRequest('/api/strategies/execute', 'POST', strategyData);
      return response;
    } catch (error) {
      console.error('Failed to execute strategy:', error);
      throw error;
    }
  }

  // Get portfolio data
  async getPortfolio() {
    try {
      const response = await this.makeRequest('/api/portfolio');
      return response;
    } catch (error) {
      console.error('Failed to get portfolio:', error);
      throw error;
    }
  }

  // Get market sentiment analysis
  async getMarketSentiment(symbol = 'BTC') {
    try {
      const response = await this.makeRequest(`/api/sentiment/${symbol}`);
      return response;
    } catch (error) {
      console.error('Failed to get market sentiment:', error);
      throw error;
    }
  }

  // Get arbitrage opportunities
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
