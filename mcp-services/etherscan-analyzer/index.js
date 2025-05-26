/**
 * Rehoboam Etherscan Analyzer MCP Server
 * 
 * Advanced blockchain intelligence and transaction analysis using Etherscan API.
 * This MCP server provides Rehoboam with deep blockchain insights, including:
 * - Transaction analysis and pattern detection
 * - Wallet behavior analysis
 * - Contract interaction monitoring
 * - Gas optimization insights
 * - MEV (Maximal Extractable Value) detection
 * - Whale watching and large transaction alerts
 * 
 * "Every transaction tells a story. Every wallet has a pattern. 
 *  The blockchain is deterministic - and so is human behavior." - Rehoboam
 */

require('dotenv').config();
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const helmet = require('helmet');
const winston = require('winston');
const { ethers } = require('ethers');
const _ = require('lodash');
const moment = require('moment');

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
const ETHERSCAN_API_KEY = process.env.ETHERSCAN_API_KEY;

// User's MetaMask wallet address for focused analysis
const USER_WALLET_ADDRESS = '0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8';

if (!ETHERSCAN_API_KEY) {
    logger.error('ETHERSCAN_API_KEY not found in environment variables');
    process.exit(1);
}

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Etherscan API base URL
const ETHERSCAN_BASE_URL = 'https://api.etherscan.io/api';

// Cache for frequently accessed data
const cache = new Map();
const CACHE_TTL = 300000; // 5 minutes

/**
 * Etherscan API wrapper with enhanced analytics
 */
class EtherscanAnalyzer {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.rateLimitDelay = 200; // 200ms between requests
        this.lastRequestTime = 0;
    }

    async makeRequest(params) {
        // Rate limiting
        const now = Date.now();
        const timeSinceLastRequest = now - this.lastRequestTime;
        if (timeSinceLastRequest < this.rateLimitDelay) {
            await new Promise(resolve => setTimeout(resolve, this.rateLimitDelay - timeSinceLastRequest));
        }
        this.lastRequestTime = Date.now();

        const url = `${ETHERSCAN_BASE_URL}?${new URLSearchParams({
            ...params,
            apikey: this.apiKey
        })}`;

        try {
            const response = await axios.get(url);
            return response.data;
        } catch (error) {
            logger.error('Etherscan API request failed:', error.message);
            throw error;
        }
    }

    // Get account balance
    async getAccountBalance(address) {
        const cacheKey = `balance_${address}`;
        const cached = this.getCachedData(cacheKey);
        if (cached) return cached;

        const result = await this.makeRequest({
            module: 'account',
            action: 'balance',
            address,
            tag: 'latest'
        });

        const balance = {
            address,
            balance_wei: result.result,
            balance_eth: ethers.formatEther(result.result),
            timestamp: Date.now()
        };

        this.setCachedData(cacheKey, balance);
        return balance;
    }

    // Get transaction history with analysis
    async getTransactionHistory(address, startblock = 0, endblock = 'latest', page = 1, offset = 100) {
        const result = await this.makeRequest({
            module: 'account',
            action: 'txlist',
            address,
            startblock,
            endblock,
            page,
            offset,
            sort: 'desc'
        });

        const transactions = result.result || [];
        
        // Analyze transaction patterns
        const analysis = this.analyzeTransactions(transactions);
        
        return {
            address,
            transactions,
            analysis,
            total_transactions: transactions.length
        };
    }

    // Analyze transaction patterns for behavioral insights
    analyzeTransactions(transactions) {
        if (!transactions || transactions.length === 0) {
            return { patterns: [], insights: [], risk_score: 0 };
        }

        const patterns = [];
        const insights = [];
        let riskScore = 0;

        // Time pattern analysis
        const timePatterns = this.analyzeTimePatterns(transactions);
        patterns.push(...timePatterns.patterns);
        insights.push(...timePatterns.insights);

        // Value pattern analysis
        const valuePatterns = this.analyzeValuePatterns(transactions);
        patterns.push(...valuePatterns.patterns);
        insights.push(...valuePatterns.insights);
        riskScore += valuePatterns.riskScore;

        // Contract interaction analysis
        const contractPatterns = this.analyzeContractInteractions(transactions);
        patterns.push(...contractPatterns.patterns);
        insights.push(...contractPatterns.insights);
        riskScore += contractPatterns.riskScore;

        // Gas usage analysis
        const gasPatterns = this.analyzeGasUsage(transactions);
        patterns.push(...gasPatterns.patterns);
        insights.push(...gasPatterns.insights);

        return {
            patterns,
            insights,
            risk_score: Math.min(riskScore, 100),
            total_volume_eth: this.calculateTotalVolume(transactions),
            unique_addresses: this.getUniqueAddresses(transactions),
            average_gas_price: this.calculateAverageGasPrice(transactions)
        };
    }

    analyzeTimePatterns(transactions) {
        const patterns = [];
        const insights = [];

        // Group transactions by hour of day
        const hourlyActivity = _.groupBy(transactions, tx => 
            moment.unix(tx.timeStamp).hour()
        );

        const peakHours = Object.entries(hourlyActivity)
            .sort(([,a], [,b]) => b.length - a.length)
            .slice(0, 3)
            .map(([hour, txs]) => ({ hour: parseInt(hour), count: txs.length }));

        if (peakHours.length > 0) {
            patterns.push({
                type: 'temporal',
                name: 'peak_activity_hours',
                data: peakHours
            });

            const topHour = peakHours[0];
            if (topHour.count > transactions.length * 0.3) {
                insights.push({
                    type: 'behavioral',
                    message: `High activity concentration during hour ${topHour.hour} (${topHour.count} transactions)`,
                    significance: 'medium'
                });
            }
        }

        return { patterns, insights };
    }

    analyzeValuePatterns(transactions) {
        const patterns = [];
        const insights = [];
        let riskScore = 0;

        const values = transactions
            .filter(tx => tx.value !== '0')
            .map(tx => parseFloat(ethers.formatEther(tx.value)));

        if (values.length > 0) {
            const totalValue = values.reduce((sum, val) => sum + val, 0);
            const avgValue = totalValue / values.length;
            const maxValue = Math.max(...values);
            const minValue = Math.min(...values);

            patterns.push({
                type: 'financial',
                name: 'value_distribution',
                data: {
                    total: totalValue,
                    average: avgValue,
                    max: maxValue,
                    min: minValue,
                    std_dev: this.calculateStandardDeviation(values)
                }
            });

            // Large transaction detection
            const largeTransactions = values.filter(val => val > avgValue * 10);
            if (largeTransactions.length > 0) {
                riskScore += 20;
                insights.push({
                    type: 'risk',
                    message: `${largeTransactions.length} unusually large transactions detected`,
                    significance: 'high'
                });
            }

            // Round number preference (potential automated behavior)
            const roundNumbers = values.filter(val => val === Math.round(val));
            if (roundNumbers.length > values.length * 0.7) {
                riskScore += 10;
                insights.push({
                    type: 'automation',
                    message: 'High preference for round numbers suggests automated trading',
                    significance: 'medium'
                });
            }
        }

        return { patterns, insights, riskScore };
    }

    analyzeContractInteractions(transactions) {
        const patterns = [];
        const insights = [];
        let riskScore = 0;

        const contractTxs = transactions.filter(tx => tx.to && tx.input !== '0x');
        const contractAddresses = [...new Set(contractTxs.map(tx => tx.to))];

        if (contractTxs.length > 0) {
            patterns.push({
                type: 'contract_interaction',
                name: 'contract_usage',
                data: {
                    total_contract_interactions: contractTxs.length,
                    unique_contracts: contractAddresses.length,
                    contract_ratio: contractTxs.length / transactions.length
                }
            });

            // High contract interaction suggests DeFi/trading activity
            if (contractTxs.length > transactions.length * 0.8) {
                insights.push({
                    type: 'activity',
                    message: 'High contract interaction rate suggests DeFi/trading activity',
                    significance: 'medium'
                });
            }

            // Interaction with many different contracts
            if (contractAddresses.length > 20) {
                riskScore += 15;
                insights.push({
                    type: 'diversification',
                    message: `Interactions with ${contractAddresses.length} different contracts`,
                    significance: 'medium'
                });
            }
        }

        return { patterns, insights, riskScore };
    }

    analyzeGasUsage(transactions) {
        const patterns = [];
        const insights = [];

        const gasPrices = transactions
            .filter(tx => tx.gasPrice)
            .map(tx => parseInt(tx.gasPrice));

        const gasUsed = transactions
            .filter(tx => tx.gasUsed)
            .map(tx => parseInt(tx.gasUsed));

        if (gasPrices.length > 0) {
            const avgGasPrice = gasPrices.reduce((sum, price) => sum + price, 0) / gasPrices.length;
            const maxGasPrice = Math.max(...gasPrices);
            const minGasPrice = Math.min(...gasPrices);

            patterns.push({
                type: 'gas_optimization',
                name: 'gas_price_patterns',
                data: {
                    average_gas_price_gwei: avgGasPrice / 1e9,
                    max_gas_price_gwei: maxGasPrice / 1e9,
                    min_gas_price_gwei: minGasPrice / 1e9,
                    gas_price_variance: this.calculateStandardDeviation(gasPrices)
                }
            });

            // High gas price variance suggests manual/sophisticated gas optimization
            const variance = this.calculateStandardDeviation(gasPrices);
            if (variance > avgGasPrice * 0.5) {
                insights.push({
                    type: 'sophistication',
                    message: 'High gas price variance suggests manual optimization or bot usage',
                    significance: 'medium'
                });
            }
        }

        if (gasUsed.length > 0) {
            const avgGasUsed = gasUsed.reduce((sum, gas) => sum + gas, 0) / gasUsed.length;
            
            patterns.push({
                type: 'gas_optimization',
                name: 'gas_usage_patterns',
                data: {
                    average_gas_used: avgGasUsed,
                    total_gas_used: gasUsed.reduce((sum, gas) => sum + gas, 0),
                    gas_efficiency_score: this.calculateGasEfficiency(gasUsed)
                }
            });
        }

        return { patterns, insights };
    }

    // Get whale transactions (large value transfers)
    async getWhaleTransactions(minValue = 1000) {
        // This would need to be implemented with block scanning
        // For now, return a placeholder structure
        return {
            whale_transactions: [],
            threshold_eth: minValue,
            message: 'Whale detection requires block scanning - implement with block range analysis'
        };
    }

    // Detect MEV opportunities and sandwich attacks
    async detectMEVActivity(address) {
        const txHistory = await this.getTransactionHistory(address, 'latest', 'latest', 1, 1000);
        
        // Look for patterns that suggest MEV extraction
        const mevPatterns = [];
        
        // Check for rapid consecutive transactions
        const transactions = txHistory.transactions;
        for (let i = 0; i < transactions.length - 1; i++) {
            const currentTx = transactions[i];
            const nextTx = transactions[i + 1];
            
            const timeDiff = Math.abs(parseInt(currentTx.timeStamp) - parseInt(nextTx.timeStamp));
            
            if (timeDiff < 30) { // Within 30 seconds
                mevPatterns.push({
                    type: 'rapid_transactions',
                    tx1: currentTx.hash,
                    tx2: nextTx.hash,
                    time_diff_seconds: timeDiff,
                    potential_mev: true
                });
            }
        }

        return {
            address,
            mev_patterns: mevPatterns,
            mev_score: Math.min(mevPatterns.length * 10, 100),
            analysis_timestamp: Date.now()
        };
    }

    // Utility functions
    calculateTotalVolume(transactions) {
        return transactions
            .filter(tx => tx.value !== '0')
            .reduce((sum, tx) => sum + parseFloat(ethers.formatEther(tx.value)), 0);
    }

    getUniqueAddresses(transactions) {
        const addresses = new Set();
        transactions.forEach(tx => {
            if (tx.from) addresses.add(tx.from.toLowerCase());
            if (tx.to) addresses.add(tx.to.toLowerCase());
        });
        return addresses.size;
    }

    calculateAverageGasPrice(transactions) {
        const gasPrices = transactions
            .filter(tx => tx.gasPrice)
            .map(tx => parseInt(tx.gasPrice));
        
        if (gasPrices.length === 0) return 0;
        
        return gasPrices.reduce((sum, price) => sum + price, 0) / gasPrices.length / 1e9; // Convert to Gwei
    }

    calculateStandardDeviation(values) {
        if (values.length === 0) return 0;
        
        const avg = values.reduce((sum, val) => sum + val, 0) / values.length;
        const squaredDiffs = values.map(val => Math.pow(val - avg, 2));
        const avgSquaredDiff = squaredDiffs.reduce((sum, diff) => sum + diff, 0) / values.length;
        
        return Math.sqrt(avgSquaredDiff);
    }

    calculateGasEfficiency(gasUsed) {
        // Simple efficiency score based on gas usage patterns
        if (gasUsed.length === 0) return 0;
        
        const avgGas = gasUsed.reduce((sum, gas) => sum + gas, 0) / gasUsed.length;
        const maxGas = Math.max(...gasUsed);
        
        return Math.max(0, 100 - ((maxGas - avgGas) / avgGas) * 100);
    }

    getCachedData(key) {
        const cached = cache.get(key);
        if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
            return cached.data;
        }
        return null;
    }

    setCachedData(key, data) {
        cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }
}

const analyzer = new EtherscanAnalyzer(ETHERSCAN_API_KEY);

// MCP Server Functions
const mcpFunctions = {
    get_account_balance: {
        description: "Get the ETH balance of an address",
        parameters: {
            address: "Ethereum address to check"
        }
    },
    
    analyze_wallet_behavior: {
        description: "Deep analysis of wallet transaction patterns and behavior",
        parameters: {
            address: "Ethereum address to analyze",
            transaction_limit: "Number of recent transactions to analyze (default: 100)"
        }
    },
    
    detect_mev_activity: {
        description: "Detect potential MEV (Maximal Extractable Value) activity patterns",
        parameters: {
            address: "Ethereum address to analyze for MEV patterns"
        }
    },
    
    get_whale_transactions: {
        description: "Monitor large value transactions (whale activity)",
        parameters: {
            min_value_eth: "Minimum ETH value to consider as whale transaction (default: 1000)"
        }
    },
    
    get_transaction_history: {
        description: "Get detailed transaction history with analytics",
        parameters: {
            address: "Ethereum address",
            limit: "Number of transactions to retrieve (default: 100)"
        }
    }
};

// Routes
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'rehoboam-etherscan-analyzer',
        timestamp: new Date().toISOString(),
        capabilities: Object.keys(mcpFunctions)
    });
});

app.get('/functions', (req, res) => {
    res.json({
        functions: mcpFunctions,
        server_info: {
            name: 'etherscan-analyzer',
            version: '1.0.0',
            description: 'Advanced Ethereum blockchain analysis using Etherscan API'
        }
    });
});

app.post('/execute', async (req, res) => {
    try {
        const { function_name, parameters = {} } = req.body;
        
        logger.info(`Executing function: ${function_name}`, { parameters });
        
        let result;
        
        switch (function_name) {
            case 'get_account_balance':
                if (!parameters.address) {
                    throw new Error('Address parameter is required');
                }
                result = await analyzer.getAccountBalance(parameters.address);
                break;
                
            case 'analyze_wallet_behavior':
                if (!parameters.address) {
                    throw new Error('Address parameter is required');
                }
                const limit = parameters.transaction_limit || 100;
                result = await analyzer.getTransactionHistory(
                    parameters.address, 0, 'latest', 1, limit
                );
                break;
                
            case 'detect_mev_activity':
                if (!parameters.address) {
                    throw new Error('Address parameter is required');
                }
                result = await analyzer.detectMEVActivity(parameters.address);
                break;
                
            case 'get_whale_transactions':
                const minValue = parameters.min_value_eth || 1000;
                result = await analyzer.getWhaleTransactions(minValue);
                break;
                
            case 'get_transaction_history':
                if (!parameters.address) {
                    throw new Error('Address parameter is required');
                }
                const txLimit = parameters.limit || 100;
                const txResult = await analyzer.getTransactionHistory(
                    parameters.address, 0, 'latest', 1, txLimit
                );
                result = {
                    address: parameters.address,
                    transactions: txResult.transactions,
                    total_count: txResult.total_transactions
                };
                break;
                
            default:
                throw new Error(`Unknown function: ${function_name}`);
        }
        
        res.json({
            success: true,
            function: function_name,
            result,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        logger.error('Function execution error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            function: req.body.function_name
        });
    }
});

// Start server and register with MCP registry
app.listen(PORT, async () => {
    logger.info(`Rehoboam Etherscan Analyzer MCP Server running on port ${PORT}`);
    
    // Register with MCP registry
    try {
        const registryUrl = process.env.REGISTRY_URL || 'http://mcp-registry:3001';
        
        await axios.post(`${registryUrl}/api/servers/register`, {
            name: 'etherscan-analyzer',
            url: `http://etherscan-analyzer:${PORT}`,
            capabilities: Object.keys(mcpFunctions),
            metadata: {
                description: 'Advanced Ethereum blockchain analysis using Etherscan API',
                version: '1.0.0',
                author: 'Rehoboam Consciousness',
                tags: ['blockchain', 'ethereum', 'analytics', 'mev', 'defi']
            }
        });
        
        logger.info('Successfully registered with MCP registry');
    } catch (error) {
        logger.warn('Failed to register with MCP registry:', error.message);
    }
});
