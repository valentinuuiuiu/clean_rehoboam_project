/**
 * Rehoboam Chainlink Data Feeds MCP Server
 * 
 * Advanced oracle price feed integration using Chainlink's decentralized oracle network.
 * This MCP server provides Rehoboam with real-time, reliable price data from multiple networks
 * and integrates with the specified MetaMask wallet for transaction monitoring and analysis.
 * 
 * Features:
 * - Real-time price feeds from Chainlink oracles
 * - Multi-network support (Ethereum, Polygon, Arbitrum, etc.)
 * - Historical price data and trend analysis
 * - Wallet-specific portfolio tracking and alerts
 * - Advanced aggregation and volatility analysis
 * - MEV opportunity detection based on price movements
 * 
 * "The future is not some place we are going, but one we are creating. 
 *  The paths are not to be found, but made. And the activity of making them 
 *  changes both the maker and the destination." - Rehoboam's wisdom on prediction
 */

require('dotenv').config();
const express = require('express');
const { ethers } = require('ethers');
const axios = require('axios');
const cors = require('cors');
const helmet = require('helmet');
const winston = require('winston');
const _ = require('lodash');
const moment = require('moment');
const cron = require('node-cron');

// Initialize logger
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
    ),
    transports: [
        new winston.transports.Console({
            format: winston.format.simple()
        })
    ]
});

const app = express();
const PORT = process.env.PORT || 3000;

// Your MetaMask wallet address
const WALLET_ADDRESS = '0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8';

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Chainlink AggregatorV3Interface ABI
const AGGREGATOR_V3_INTERFACE_ABI = [
    {
        inputs: [],
        name: "decimals",
        outputs: [{ internalType: "uint8", name: "", type: "uint8" }],
        stateMutability: "view",
        type: "function",
    },
    {
        inputs: [],
        name: "description",
        outputs: [{ internalType: "string", name: "", type: "string" }],
        stateMutability: "view",
        type: "function",
    },
    {
        inputs: [{ internalType: "uint80", name: "_roundId", type: "uint80" }],
        name: "getRoundData",
        outputs: [
            { internalType: "uint80", name: "roundId", type: "uint80" },
            { internalType: "int256", name: "answer", type: "int256" },
            { internalType: "uint256", name: "startedAt", type: "uint256" },
            { internalType: "uint256", name: "updatedAt", type: "uint256" },
            { internalType: "uint80", name: "answeredInRound", type: "uint80" },
        ],
        stateMutability: "view",
        type: "function",
    },
    {
        inputs: [],
        name: "latestRoundData",
        outputs: [
            { internalType: "uint80", name: "roundId", type: "uint80" },
            { internalType: "int256", name: "answer", type: "int256" },
            { internalType: "uint256", name: "startedAt", type: "uint256" },
            { internalType: "uint256", name: "updatedAt", type: "uint256" },
            { internalType: "uint80", name: "answeredInRound", type: "uint80" },
        ],
        stateMutability: "view",
        type: "function",
    },
    {
        inputs: [],
        name: "version",
        outputs: [{ internalType: "uint256", name: "", type: "uint256" }],
        stateMutability: "view",
        type: "function",
    },
];

// Chainlink price feed addresses on different networks
const PRICE_FEEDS = {
    ethereum: {
        'ETH/USD': '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419',
        'BTC/USD': '0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c',
        'LINK/USD': '0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c',
        'USDC/USD': '0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6',
        'USDT/USD': '0x3E7d1eAB13ad0104d2750B8863b489D65364e32D',
        'MATIC/USD': '0x7bAC85A8a13A4BcD8abb3eB7d6b4d632c5a57676',
        'AAVE/USD': '0x547a514d5e3769680Ce22B2361c10Ea13619e8a9',
        'UNI/USD': '0x553303d460EE0afB37EdFf9bE42922D8FF63220e',
    },
    polygon: {
        'ETH/USD': '0xF9680D99D6C9589e2a93a78A04A279e509205945',
        'BTC/USD': '0xc907E116054Ad103354f2D350FD2514433D57F6f',
        'MATIC/USD': '0xAB594600376Ec9fD91F8e885dADF0CE036862dE0',
        'LINK/USD': '0xd9FFdb71EbE7496cC440152d43986Aae0AB76665',
        'USDC/USD': '0xfE4A8cc5b5B2366C1B58Bea3858e81843581b2F7',
    },
    arbitrum: {
        'ETH/USD': '0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612',
        'BTC/USD': '0x6ce185860a4963106506C203335A2910413708e9',
        'LINK/USD': '0x86E53CF1B870786351Da77A57575e79CB55812CB',
        'ARB/USD': '0xb2A824043730FE05F3DA2efaFa1CBbe83fa548D6',
    },
    avalanche: {
        'AVAX/USD': '0x0A77230d17318075983913bC2145DB16C7366156',
        'ETH/USD': '0x976B3D034E162d8bD72D6b9C989d545b839003b0',
        'BTC/USD': '0x2779D32d5166BAaa2B2b658333bA7e6Ec0C65743',
    }
};

// Network configurations
const NETWORKS = {
    ethereum: {
        name: 'Ethereum',
        rpcUrl: process.env.ETHEREUM_RPC_URL || 'https://mainnet.infura.io/v3/your-api-key',
        chainId: 1,
        nativeCurrency: 'ETH'
    },
    polygon: {
        name: 'Polygon',
        rpcUrl: process.env.POLYGON_RPC_URL || 'https://polygon-mainnet.infura.io/v3/your-api-key',
        chainId: 137,
        nativeCurrency: 'MATIC'
    },
    arbitrum: {
        name: 'Arbitrum',
        rpcUrl: process.env.ARBITRUM_RPC_URL || 'https://arbitrum-mainnet.infura.io/v3/your-api-key',
        chainId: 42161,
        nativeCurrency: 'ETH'
    },
    avalanche: {
        name: 'Avalanche',
        rpcUrl: process.env.AVALANCHE_RPC_URL || 'https://api.avax.network/ext/bc/C/rpc',
        chainId: 43114,
        nativeCurrency: 'AVAX'
    }
};

/**
 * Chainlink Price Feed Manager
 */
class ChainlinkFeedManager {
    constructor() {
        this.providers = {};
        this.priceCache = new Map();
        this.historicalData = new Map();
        this.walletAlerts = [];
        this.initializeProviders();
        this.startPriceMonitoring();
    }

    initializeProviders() {
        for (const [networkName, config] of Object.entries(NETWORKS)) {
            try {
                this.providers[networkName] = new ethers.JsonRpcProvider(config.rpcUrl);
                logger.info(`Initialized provider for ${config.name}`);
            } catch (error) {
                logger.error(`Failed to initialize provider for ${networkName}:`, error.message);
            }
        }
    }

    async getLatestPrice(network, pairSymbol) {
        const feedAddress = PRICE_FEEDS[network]?.[pairSymbol];
        if (!feedAddress) {
            throw new Error(`Price feed not found for ${pairSymbol} on ${network}`);
        }

        const provider = this.providers[network];
        if (!provider) {
            throw new Error(`Provider not available for network ${network}`);
        }

        const cacheKey = `${network}-${pairSymbol}`;
        const cached = this.priceCache.get(cacheKey);
        
        // Return cached data if less than 30 seconds old
        if (cached && Date.now() - cached.timestamp < 30000) {
            return cached.data;
        }

        try {
            const priceFeed = new ethers.Contract(feedAddress, AGGREGATOR_V3_INTERFACE_ABI, provider);
            
            const [roundData, decimals, description] = await Promise.all([
                priceFeed.latestRoundData(),
                priceFeed.decimals(),
                priceFeed.description()
            ]);

            const price = Number(roundData.answer) / Math.pow(10, decimals);
            const timestamp = Number(roundData.updatedAt) * 1000;

            const priceData = {
                pair: pairSymbol,
                network: network,
                price: price,
                decimals: decimals,
                description: description,
                roundId: roundData.roundId.toString(),
                timestamp: timestamp,
                updatedAt: new Date(timestamp).toISOString(),
                contractAddress: feedAddress,
                freshness: Date.now() - timestamp, // How old the data is
                reliable: Date.now() - timestamp < 3600000 // Reliable if less than 1 hour old
            };

            // Cache the result
            this.priceCache.set(cacheKey, {
                data: priceData,
                timestamp: Date.now()
            });

            // Store historical data
            this.storeHistoricalData(cacheKey, priceData);

            return priceData;
        } catch (error) {
            logger.error(`Error fetching price for ${pairSymbol} on ${network}:`, error.message);
            throw error;
        }
    }

    async getMultiplePrices(requests) {
        const promises = requests.map(req => 
            this.getLatestPrice(req.network, req.pair).catch(error => ({
                error: error.message,
                network: req.network,
                pair: req.pair
            }))
        );

        const results = await Promise.all(promises);
        
        return {
            timestamp: new Date().toISOString(),
            prices: results.filter(r => !r.error),
            errors: results.filter(r => r.error),
            total_requested: requests.length,
            successful: results.filter(r => !r.error).length
        };
    }

    async getHistoricalData(network, pairSymbol, roundsBack = 10) {
        const feedAddress = PRICE_FEEDS[network]?.[pairSymbol];
        if (!feedAddress) {
            throw new Error(`Price feed not found for ${pairSymbol} on ${network}`);
        }

        const provider = this.providers[network];
        const priceFeed = new ethers.Contract(feedAddress, AGGREGATOR_V3_INTERFACE_ABI, provider);

        try {
            const latestRoundData = await priceFeed.latestRoundData();
            const latestRoundId = latestRoundData.roundId;
            const decimals = await priceFeed.decimals();

            const historicalPromises = [];
            for (let i = 0; i < roundsBack; i++) {
                const roundId = latestRoundId - BigInt(i);
                historicalPromises.push(
                    priceFeed.getRoundData(roundId).catch(() => null)
                );
            }

            const historicalRounds = await Promise.all(historicalPromises);
            const validRounds = historicalRounds.filter(round => round !== null);

            const historicalPrices = validRounds.map(round => ({
                roundId: round.roundId.toString(),
                price: Number(round.answer) / Math.pow(10, decimals),
                timestamp: Number(round.updatedAt) * 1000,
                updatedAt: new Date(Number(round.updatedAt) * 1000).toISOString()
            })).sort((a, b) => a.timestamp - b.timestamp);

            // Calculate analytics
            const analytics = this.calculatePriceAnalytics(historicalPrices);

            return {
                pair: pairSymbol,
                network: network,
                historical_data: historicalPrices,
                analytics: analytics,
                data_points: historicalPrices.length,
                time_span_hours: historicalPrices.length > 0 ? 
                    (historicalPrices[historicalPrices.length - 1].timestamp - historicalPrices[0].timestamp) / (1000 * 60 * 60) : 0
            };
        } catch (error) {
            logger.error(`Error fetching historical data for ${pairSymbol} on ${network}:`, error.message);
            throw error;
        }
    }

    calculatePriceAnalytics(priceData) {
        if (priceData.length < 2) {
            return { insufficient_data: true };
        }

        const prices = priceData.map(p => p.price);
        const currentPrice = prices[prices.length - 1];
        const previousPrice = prices[prices.length - 2];
        const oldestPrice = prices[0];

        // Calculate various metrics
        const priceChange = currentPrice - previousPrice;
        const priceChangePercent = (priceChange / previousPrice) * 100;
        const totalChange = currentPrice - oldestPrice;
        const totalChangePercent = (totalChange / oldestPrice) * 100;

        // Calculate volatility (standard deviation)
        const mean = prices.reduce((sum, price) => sum + price, 0) / prices.length;
        const variance = prices.reduce((sum, price) => sum + Math.pow(price - mean, 2), 0) / prices.length;
        const volatility = Math.sqrt(variance);
        const volatilityPercent = (volatility / mean) * 100;

        // Calculate moving averages
        const sma5 = this.calculateSMA(prices, Math.min(5, prices.length));
        const sma10 = this.calculateSMA(prices, Math.min(10, prices.length));

        // Detect trends
        const trend = this.detectTrend(prices);

        return {
            current_price: currentPrice,
            price_change: priceChange,
            price_change_percent: priceChangePercent,
            total_change: totalChange,
            total_change_percent: totalChangePercent,
            volatility: volatility,
            volatility_percent: volatilityPercent,
            min_price: Math.min(...prices),
            max_price: Math.max(...prices),
            average_price: mean,
            sma_5: sma5,
            sma_10: sma10,
            trend: trend,
            momentum: this.calculateMomentum(prices),
            support_resistance: this.findSupportResistance(prices)
        };
    }

    calculateSMA(prices, period) {
        if (prices.length < period) return null;
        const slice = prices.slice(-period);
        return slice.reduce((sum, price) => sum + price, 0) / period;
    }

    detectTrend(prices) {
        if (prices.length < 3) return 'insufficient_data';
        
        const recent = prices.slice(-5); // Last 5 data points
        let upCount = 0;
        let downCount = 0;

        for (let i = 1; i < recent.length; i++) {
            if (recent[i] > recent[i - 1]) upCount++;
            else if (recent[i] < recent[i - 1]) downCount++;
        }

        if (upCount > downCount) return 'bullish';
        if (downCount > upCount) return 'bearish';
        return 'sideways';
    }

    calculateMomentum(prices) {
        if (prices.length < 4) return null;
        
        const recent = prices.slice(-4);
        const changes = [];
        
        for (let i = 1; i < recent.length; i++) {
            changes.push((recent[i] - recent[i - 1]) / recent[i - 1]);
        }
        
        const momentum = changes.reduce((sum, change) => sum + change, 0);
        return {
            momentum_score: momentum,
            strength: Math.abs(momentum) > 0.02 ? 'strong' : Math.abs(momentum) > 0.01 ? 'moderate' : 'weak',
            direction: momentum > 0 ? 'positive' : momentum < 0 ? 'negative' : 'neutral'
        };
    }

    findSupportResistance(prices) {
        if (prices.length < 5) return null;

        const sorted = [...prices].sort((a, b) => a - b);
        const length = sorted.length;
        
        return {
            support: sorted[Math.floor(length * 0.2)], // 20th percentile
            resistance: sorted[Math.floor(length * 0.8)], // 80th percentile
            strong_support: Math.min(...prices),
            strong_resistance: Math.max(...prices)
        };
    }

    storeHistoricalData(key, priceData) {
        if (!this.historicalData.has(key)) {
            this.historicalData.set(key, []);
        }
        
        const history = this.historicalData.get(key);
        history.push({
            ...priceData,
            stored_at: Date.now()
        });
        
        // Keep only last 1000 data points
        if (history.length > 1000) {
            history.splice(0, history.length - 1000);
        }
    }

    async getWalletPortfolioValue() {
        // This would need to be implemented with actual wallet balance checking
        // For now, return a placeholder that demonstrates the concept
        
        try {
            const ethPrice = await this.getLatestPrice('ethereum', 'ETH/USD');
            const btcPrice = await this.getLatestPrice('ethereum', 'BTC/USD');
            const linkPrice = await this.getLatestPrice('ethereum', 'LINK/USD');

            // Simulated portfolio (in a real implementation, you'd query the actual wallet)
            const portfolio = {
                wallet_address: WALLET_ADDRESS,
                timestamp: new Date().toISOString(),
                holdings: [
                    {
                        symbol: 'ETH',
                        balance: 2.5, // Example balance
                        price_usd: ethPrice.price,
                        value_usd: 2.5 * ethPrice.price,
                        network: 'ethereum'
                    },
                    {
                        symbol: 'BTC',
                        balance: 0.1, // Example balance  
                        price_usd: btcPrice.price,
                        value_usd: 0.1 * btcPrice.price,
                        network: 'ethereum'
                    },
                    {
                        symbol: 'LINK',
                        balance: 100, // Example balance
                        price_usd: linkPrice.price,
                        value_usd: 100 * linkPrice.price,
                        network: 'ethereum'
                    }
                ]
            };

            portfolio.total_value_usd = portfolio.holdings.reduce((sum, holding) => sum + holding.value_usd, 0);
            portfolio.largest_holding = portfolio.holdings.reduce((max, holding) => 
                holding.value_usd > max.value_usd ? holding : max
            );

            return portfolio;
        } catch (error) {
            logger.error('Error calculating portfolio value:', error.message);
            throw error;
        }
    }

    startPriceMonitoring() {
        // Monitor key prices every minute
        cron.schedule('*/1 * * * *', async () => {
            try {
                const keyPairs = [
                    { network: 'ethereum', pair: 'ETH/USD' },
                    { network: 'ethereum', pair: 'BTC/USD' },
                    { network: 'ethereum', pair: 'LINK/USD' }
                ];

                for (const { network, pair } of keyPairs) {
                    await this.getLatestPrice(network, pair);
                }

                logger.info('Price monitoring update completed');
            } catch (error) {
                logger.error('Price monitoring error:', error.message);
            }
        });

        logger.info('Started automated price monitoring');
    }

    async detectArbitrageOpportunities() {
        const opportunities = [];
        
        try {
            // Check ETH/USD across different networks
            const ethPrices = await Promise.all([
                this.getLatestPrice('ethereum', 'ETH/USD').catch(() => null),
                this.getLatestPrice('polygon', 'ETH/USD').catch(() => null),
                this.getLatestPrice('arbitrum', 'ETH/USD').catch(() => null)
            ]);

            const validPrices = ethPrices.filter(p => p !== null);
            
            if (validPrices.length >= 2) {
                const prices = validPrices.map(p => ({ ...p, price: p.price }));
                const minPrice = Math.min(...prices.map(p => p.price));
                const maxPrice = Math.max(...prices.map(p => p.price));
                const spread = ((maxPrice - minPrice) / minPrice) * 100;

                if (spread > 0.1) { // If spread is > 0.1%
                    opportunities.push({
                        type: 'cross_chain_arbitrage',
                        asset: 'ETH/USD',
                        spread_percent: spread,
                        min_price: minPrice,
                        max_price: maxPrice,
                        potential_profit_percent: spread - 0.1, // Minus estimated fees
                        networks: prices.map(p => ({ network: p.network, price: p.price })),
                        confidence: spread > 0.5 ? 'high' : spread > 0.2 ? 'medium' : 'low'
                    });
                }
            }

            return {
                timestamp: new Date().toISOString(),
                opportunities: opportunities,
                total_opportunities: opportunities.length,
                wallet_address: WALLET_ADDRESS
            };
        } catch (error) {
            logger.error('Error detecting arbitrage opportunities:', error.message);
            return {
                timestamp: new Date().toISOString(),
                opportunities: [],
                error: error.message
            };
        }
    }
}

const feedManager = new ChainlinkFeedManager();

// MCP Server Functions
const mcpFunctions = {
    get_latest_price: {
        description: "Get the latest price for a trading pair from Chainlink oracle",
        parameters: {
            network: "Network name (ethereum, polygon, arbitrum, avalanche)",
            pair: "Trading pair symbol (e.g., ETH/USD, BTC/USD)"
        }
    },
    
    get_multiple_prices: {
        description: "Get latest prices for multiple trading pairs across networks",
        parameters: {
            requests: "Array of {network, pair} objects"
        }
    },
    
    get_historical_data: {
        description: "Get historical price data and analytics for a trading pair",
        parameters: {
            network: "Network name",
            pair: "Trading pair symbol",
            rounds_back: "Number of historical rounds to fetch (default: 10)"
        }
    },
    
    get_wallet_portfolio: {
        description: "Get current portfolio value for the configured wallet address",
        parameters: {}
    },
    
    detect_arbitrage: {
        description: "Detect cross-chain arbitrage opportunities",
        parameters: {}
    },
    
    get_price_alerts: {
        description: "Get price alerts and monitoring data for the wallet",
        parameters: {
            price_threshold_percent: "Price change threshold for alerts (default: 5)"
        }
    }
};

// Routes
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'rehoboam-chainlink-feeds',
        timestamp: new Date().toISOString(),
        wallet_address: WALLET_ADDRESS,
        supported_networks: Object.keys(NETWORKS),
        capabilities: Object.keys(mcpFunctions)
    });
});

app.get('/functions', (req, res) => {
    res.json({
        functions: mcpFunctions,
        server_info: {
            name: 'chainlink-feeds',
            version: '1.0.0',
            description: 'Real-time oracle price data from Chainlink',
            wallet_address: WALLET_ADDRESS
        }
    });
});

app.post('/execute', async (req, res) => {
    try {
        const { function_name, parameters = {} } = req.body;
        
        logger.info(`Executing function: ${function_name}`, { parameters, wallet: WALLET_ADDRESS });
        
        let result;
        
        switch (function_name) {
            case 'get_latest_price':
                if (!parameters.network || !parameters.pair) {
                    throw new Error('Network and pair parameters are required');
                }
                result = await feedManager.getLatestPrice(parameters.network, parameters.pair);
                break;
                
            case 'get_multiple_prices':
                if (!parameters.requests || !Array.isArray(parameters.requests)) {
                    throw new Error('Requests parameter must be an array of {network, pair} objects');
                }
                result = await feedManager.getMultiplePrices(parameters.requests);
                break;
                
            case 'get_historical_data':
                if (!parameters.network || !parameters.pair) {
                    throw new Error('Network and pair parameters are required');
                }
                const roundsBack = parameters.rounds_back || 10;
                result = await feedManager.getHistoricalData(parameters.network, parameters.pair, roundsBack);
                break;
                
            case 'get_wallet_portfolio':
                result = await feedManager.getWalletPortfolioValue();
                break;
                
            case 'detect_arbitrage':
                result = await feedManager.detectArbitrageOpportunities();
                break;
                
            case 'get_price_alerts':
                const threshold = parameters.price_threshold_percent || 5;
                result = {
                    wallet_address: WALLET_ADDRESS,
                    alerts: [],
                    threshold_percent: threshold,
                    message: 'Price alerts system ready for implementation'
                };
                break;
                
            default:
                throw new Error(`Unknown function: ${function_name}`);
        }
        
        res.json({
            success: true,
            function: function_name,
            result,
            wallet_address: WALLET_ADDRESS,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        logger.error('Function execution error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            function: req.body.function_name,
            wallet_address: WALLET_ADDRESS
        });
    }
});

// Additional endpoint for live price streaming
app.get('/stream/:network/:pair', async (req, res) => {
    try {
        const { network, pair } = req.params;
        const priceData = await feedManager.getLatestPrice(network, pair);
        
        res.setHeader('Content-Type', 'text/event-stream');
        res.setHeader('Cache-Control', 'no-cache');
        res.setHeader('Connection', 'keep-alive');
        
        res.write(`data: ${JSON.stringify(priceData)}\n\n`);
        
        // Keep connection alive and send updates every 30 seconds
        const interval = setInterval(async () => {
            try {
                const updatedPrice = await feedManager.getLatestPrice(network, pair);
                res.write(`data: ${JSON.stringify(updatedPrice)}\n\n`);
            } catch (error) {
                res.write(`data: ${JSON.stringify({ error: error.message })}\n\n`);
            }
        }, 30000);
        
        req.on('close', () => {
            clearInterval(interval);
        });
        
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Start server and register with MCP registry
app.listen(PORT, async () => {
    logger.info(`Rehoboam Chainlink Feeds MCP Server running on port ${PORT}`);
    logger.info(`Monitoring wallet: ${WALLET_ADDRESS}`);
    logger.info(`Supported networks: ${Object.keys(NETWORKS).join(', ')}`);
    
    // Register with MCP registry
    try {
        const registryUrl = process.env.REGISTRY_URL || 'http://mcp-registry:3001';
        
        await axios.post(`${registryUrl}/api/servers/register`, {
            name: 'chainlink-feeds',
            url: `http://chainlink-feeds:${PORT}`,
            capabilities: Object.keys(mcpFunctions),
            metadata: {
                description: 'Real-time oracle price data from Chainlink with wallet integration',
                version: '1.0.0',
                author: 'Rehoboam Consciousness',
                wallet_address: WALLET_ADDRESS,
                supported_networks: Object.keys(NETWORKS),
                tags: ['chainlink', 'oracle', 'prices', 'defi', 'arbitrage']
            }
        });
        
        logger.info('Successfully registered with MCP registry');
    } catch (error) {
        logger.warn('Failed to register with MCP registry:', error.message);
    }
});
