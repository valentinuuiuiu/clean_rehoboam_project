import { ethers } from 'ethers';

// Flash Arbitrage Bot Contract ABI (simplified for the essential functions)
const FLASH_ARBITRAGE_ABI = [
  "function executeFlashArbitrage(address flashLender, address token, uint256 amount, address buyDEX, address sellDEX, bytes calldata buyCalldata, bytes calldata sellCalldata, uint256 minProfit) external",
  "function quickArbitrage(address token, address buyDEX, address sellDEX, uint256 amount) external",
  "function trustedLenders(address) external view returns (bool)",
  "function trustedDEXs(address) external view returns (bool)",
  "function addTrustedLender(address) external",
  "function addTrustedDEX(address) external",
  "event FlashArbitrageExecuted(uint256 indexed opportunityId, address token, uint256 amount, uint256 profit, string wisdom)"
];

export interface FlashArbitrageOpportunity {
  token: string;
  buyDEX: string;
  sellDEX: string;
  buyPrice: number;
  sellPrice: number;
  amount: string; // Amount in wei
  expectedProfit: number;
  confidence: number;
  gasEstimate: string;
  flashLoanFee: number;
  netProfit: number;
  profitPercentage: number;
}

export interface NetworkConfig {
  chainId: number;
  name: string;
  rpcUrl: string;
  aavePool: string;
  dexes: {
    uniswapV3: string;
    sushiswap: string;
    balancer: string;
    curve: string;
  };
  tokens: {
    [symbol: string]: string;
  };
}

export class FlashArbitrageService {
  private provider: ethers.Provider;
  private signer?: ethers.Signer;
  private arbitrageBotAddress: string = '0x0000000000000000000000000000000000000000';
  private networks: Map<number, NetworkConfig>;

  constructor(provider: ethers.Provider, arbitrageBotAddress?: string) {
    this.provider = provider;
    
    // Use provided address or try to get from environment
    if (arbitrageBotAddress) {
      this.arbitrageBotAddress = arbitrageBotAddress;
    } else {
      // Try to detect network and use appropriate contract address
      this.detectContractAddress();
    }
    
    this.networks = new Map();
    this.initializeNetworks();
  }

  private async detectContractAddress() {
    try {
      const network = await this.provider.getNetwork();
      const chainId = Number(network.chainId);
      
      // Get contract address from environment based on chain
      switch (chainId) {
        case 1:
          this.arbitrageBotAddress = process.env.VITE_FLASH_ARBITRAGE_ETHEREUM || '0x0000000000000000000000000000000000000000';
          break;
        case 42161:
          this.arbitrageBotAddress = process.env.VITE_FLASH_ARBITRAGE_ARBITRUM || '0x0000000000000000000000000000000000000000';
          break;
        case 10:
          this.arbitrageBotAddress = process.env.VITE_FLASH_ARBITRAGE_OPTIMISM || '0x0000000000000000000000000000000000000000';
          break;
        case 8453:
          this.arbitrageBotAddress = process.env.VITE_FLASH_ARBITRAGE_BASE || '0x0000000000000000000000000000000000000000';
          break;
        case 137:
          this.arbitrageBotAddress = process.env.VITE_FLASH_ARBITRAGE_POLYGON || '0x0000000000000000000000000000000000000000';
          break;
        default:
          this.arbitrageBotAddress = '0x0000000000000000000000000000000000000000';
      }
    } catch (error) {
      console.warn('Could not detect network, using placeholder contract address');
      this.arbitrageBotAddress = '0x0000000000000000000000000000000000000000';
    }
  }

  private initializeNetworks() {
    // Ethereum Mainnet
    this.networks.set(1, {
      chainId: 1,
      name: 'Ethereum',
      rpcUrl: process.env.VITE_ETHEREUM_RPC_URL || 'https://eth-mainnet.g.alchemy.com/v2/demo',
      aavePool: '0x87870Bace7f90197cdc9628ed13C8E6e96cB4E56',
      dexes: {
        uniswapV3: '0xE592427A0AEce92De3Edee1F18E0157C05861564',
        sushiswap: '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F',
        balancer: '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
        curve: '0x8301AE4fc9c624d1D396cbDAa1ed877821D7C511'
      },
      tokens: {
        ETH: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        USDC: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        USDT: '0xdAC17F958D2ee523a2206206994597C13D831ec7',
        LINK: '0x514910771AF9Ca656af840dff83E8264EcF986CA',
        UMA: '0x04Fa0d235C4abf4BcF4787aF4CF447DE572eF828'
      }
    });

    // Arbitrum
    this.networks.set(42161, {
      chainId: 42161,
      name: 'Arbitrum',
      rpcUrl: process.env.VITE_ARBITRUM_RPC_URL || 'https://arb-mainnet.g.alchemy.com/v2/demo',
      aavePool: '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
      dexes: {
        uniswapV3: '0xE592427A0AEce92De3Edee1F18E0157C05861564',
        sushiswap: '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506',
        balancer: '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
        curve: '0x7544Fe3d184b6B55D6B36c3FCA1157eE0Ba30287'
      },
      tokens: {
        ETH: '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
        USDC: '0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
        USDT: '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
        LINK: '0xf97f4df75117a78c1A5a0DBb814Af92458539FB4',
        UMA: '0xd693Ec944A85eeca4247eC1c3b130DCa9B0C3b22'
      }
    });

    // Optimism
    this.networks.set(10, {
      chainId: 10,
      name: 'Optimism',
      rpcUrl: process.env.VITE_OPTIMISM_RPC_URL || 'https://opt-mainnet.g.alchemy.com/v2/demo',
      aavePool: '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
      dexes: {
        uniswapV3: '0xE592427A0AEce92De3Edee1F18E0157C05861564',
        sushiswap: '0xFBc12984689e5f15626Bad03Ad60160Fe98B303C',
        balancer: '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
        curve: '0x2db0E83599a91b508Ac268a6197b8B14F5e72840'
      },
      tokens: {
        ETH: '0x4200000000000000000000000000000000000006',
        USDC: '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85',
        USDT: '0x94b008aA00579c1307B0EF2c499aD98a8ce58e58',
        LINK: '0x350a791Bfc2C21F9Ed5d10980Dad2e2638ffa7f6',
        UMA: '0xE7798f023fC62146e8Aa1b36Da45fb70855a77Ea'
      }
    });

    // Base
    this.networks.set(8453, {
      chainId: 8453,
      name: 'Base',
      rpcUrl: process.env.VITE_BASE_RPC_URL || 'https://base-mainnet.g.alchemy.com/v2/demo',
      aavePool: '0xA238Dd80C259a72e81d7e4664a9801593F98d1c5',
      dexes: {
        uniswapV3: '0x2626664c2603336E57B271c5C0b26F421741e481',
        sushiswap: '0x6BDED42c6DA8FBf0d2bA55B2fa120C5e0c8D7891',
        balancer: '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
        curve: '0x8C3cEeA57F8Ed1461dB47689dF44d2624E2ad9eF'
      },
      tokens: {
        ETH: '0x4200000000000000000000000000000000000006',
        USDC: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
        LINK: '0x88Fb150BDc53A65fe94Dea0c9BA0a6dAf8C6e196',
        UMA: '0x3950BF4a93b4E28a3EE4D6a6e8e2B6E8a3969a83'
      }
    });

    // Polygon
    this.networks.set(137, {
      chainId: 137,
      name: 'Polygon',
      rpcUrl: process.env.VITE_POLYGON_RPC_URL || 'https://polygon-mainnet.g.alchemy.com/v2/demo',
      aavePool: '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
      dexes: {
        uniswapV3: '0xE592427A0AEce92De3Edee1F18E0157C05861564',
        sushiswap: '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506',
        balancer: '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
        curve: '0x445FE580eF8d70FF569aB36e80c647af338db351'
      },
      tokens: {
        ETH: '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619', // WETH on Polygon
        USDC: '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
        USDT: '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
        LINK: '0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39',
        UMA: '0x3066818837c5e6eD6601bd5a91B0762877A6B731'
      }
    });
  }

  /**
   * Find arbitrage opportunities across multiple DEXs
   */
  async findArbitrageOpportunities(
    tokenSymbol: string,
    maxAmount: string = ethers.parseEther("10").toString(),
    minProfitPercentage: number = 0.5
  ): Promise<FlashArbitrageOpportunity[]> {
    const network = await this.provider.getNetwork();
    const config = this.networks.get(Number(network.chainId));
    
    if (!config) {
      throw new Error(`Unsupported network: ${network.chainId}`);
    }

    const tokenAddress = config.tokens[tokenSymbol];
    if (!tokenAddress) {
      throw new Error(`Token ${tokenSymbol} not supported on ${config.name}`);
    }

    const opportunities: FlashArbitrageOpportunity[] = [];

    // Check all DEX pairs for arbitrage opportunities
    const dexNames = Object.keys(config.dexes);
    
    for (let i = 0; i < dexNames.length; i++) {
      for (let j = i + 1; j < dexNames.length; j++) {
        const buyDEX = dexNames[i];
        const sellDEX = dexNames[j];
        
        try {
          const opportunity = await this.checkDEXPair(
            config,
            tokenAddress,
            tokenSymbol,
            buyDEX,
            sellDEX,
            maxAmount,
            minProfitPercentage
          );
          
          if (opportunity) {
            opportunities.push(opportunity);
          }
        } catch (error) {
          console.error(`Error checking ${buyDEX} -> ${sellDEX}:`, error);
        }
      }
    }

    // Sort by profit percentage (highest first)
    return opportunities.sort((a, b) => b.profitPercentage - a.profitPercentage);
  }

  private async checkDEXPair(
    config: NetworkConfig,
    tokenAddress: string,
    tokenSymbol: string,
    buyDEX: string,
    sellDEX: string,
    maxAmount: string,
    minProfitPercentage: number
  ): Promise<FlashArbitrageOpportunity | null> {
    // In a real implementation, you would:
    // 1. Query actual DEX prices using their respective APIs/contracts
    // 2. Calculate slippage for the given amount
    // 3. Estimate gas costs accurately
    // 4. Factor in flash loan fees
    
    // For now, let's simulate realistic price differences
    const basePriceUSD = this.getTokenBasePrice(tokenSymbol);
    const buyPriceVariance = (Math.random() - 0.5) * 0.02; // ±1% variance
    const sellPriceVariance = (Math.random() - 0.5) * 0.02;
    
    const buyPrice = basePriceUSD * (1 + buyPriceVariance);
    const sellPrice = basePriceUSD * (1 + sellPriceVariance);
    
    const priceDifference = sellPrice - buyPrice;
    const profitPercentage = (priceDifference / buyPrice) * 100;
    
    // Only return if profitable above threshold
    if (profitPercentage < minProfitPercentage) {
      return null;
    }

    const amountEther = ethers.formatEther(maxAmount);
    const expectedProfitUSD = priceDifference * parseFloat(amountEther);
    
    // Estimate flash loan fee (typically 0.05% for Aave)
    const flashLoanFeePercentage = 0.05;
    const flashLoanFeeUSD = basePriceUSD * parseFloat(amountEther) * (flashLoanFeePercentage / 100);
    
    // Estimate gas costs (varies by network)
    const gasEstimateUSD = this.estimateGasCost(config.chainId);
    
    const netProfitUSD = expectedProfitUSD - flashLoanFeeUSD - gasEstimateUSD;
    const netProfitPercentage = (netProfitUSD / (basePriceUSD * parseFloat(amountEther))) * 100;
    
    // Only return if still profitable after fees
    if (netProfitUSD <= 0) {
      return null;
    }

    return {
      token: tokenAddress,
      buyDEX: config.dexes[buyDEX as keyof typeof config.dexes],
      sellDEX: config.dexes[sellDEX as keyof typeof config.dexes],
      buyPrice,
      sellPrice,
      amount: maxAmount,
      expectedProfit: expectedProfitUSD,
      confidence: this.calculateConfidence(profitPercentage, netProfitUSD),
      gasEstimate: gasEstimateUSD.toFixed(4),
      flashLoanFee: flashLoanFeeUSD,
      netProfit: netProfitUSD,
      profitPercentage: netProfitPercentage
    };
  }

  /**
   * Execute flash arbitrage opportunity
   */
  async executeArbitrage(
    opportunity: FlashArbitrageOpportunity,
    signer: ethers.Signer
  ): Promise<ethers.ContractTransactionResponse> {
    if (!signer) {
      throw new Error('Signer required to execute arbitrage');
    }

    const contract = new ethers.Contract(this.arbitrageBotAddress, FLASH_ARBITRAGE_ABI, signer);
    const network = await this.provider.getNetwork();
    const config = this.networks.get(Number(network.chainId));
    
    if (!config) {
      throw new Error(`Unsupported network: ${network.chainId}`);
    }

    // Prepare transaction data for DEX interactions
    const buyCalldata = this.prepareDEXCalldata(opportunity.buyDEX, opportunity.token, opportunity.amount, 'buy');
    const sellCalldata = this.prepareDEXCalldata(opportunity.sellDEX, opportunity.token, opportunity.amount, 'sell');

    // Calculate minimum profit in wei
    const minProfitWei = ethers.parseEther((opportunity.netProfit / opportunity.buyPrice).toString());

    return await contract.executeFlashArbitrage(
      config.aavePool,
      opportunity.token,
      opportunity.amount,
      opportunity.buyDEX,
      opportunity.sellDEX,
      buyCalldata,
      sellCalldata,
      minProfitWei
    );
  }

  /**
   * Quick arbitrage for small amounts (perfect for testing)
   */
  async quickArbitrage(
    tokenSymbol: string,
    buyDEX: string,
    sellDEX: string,
    amountEther: string,
    signer: ethers.Signer
  ): Promise<ethers.ContractTransactionResponse> {
    const contract = new ethers.Contract(this.arbitrageBotAddress, FLASH_ARBITRAGE_ABI, signer);
    const network = await this.provider.getNetwork();
    const config = this.networks.get(Number(network.chainId));
    
    if (!config) {
      throw new Error(`Unsupported network: ${network.chainId}`);
    }

    const tokenAddress = config.tokens[tokenSymbol];
    const amount = ethers.parseEther(amountEther);

    return await contract.quickArbitrage(
      tokenAddress,
      buyDEX,
      sellDEX,
      amount
    );
  }

  /**
   * Get current gas price and estimate costs
   */
  private estimateGasCost(chainId: number): number {
    // Estimated gas costs in USD for flash arbitrage transaction
    const gasCosts: Record<number, number> = {
      1: 15.0,     // Ethereum - higher gas
      42161: 0.5,  // Arbitrum - very low gas
      10: 0.3,     // Optimism - very low gas
      8453: 0.2,   // Base - very low gas
      137: 0.1     // Polygon - very low gas
    };

    return gasCosts[chainId] || 5.0; // Default
  }

  /**
   * Calculate confidence score based on profit and market conditions
   */
  private calculateConfidence(profitPercentage: number, netProfitUSD: number): number {
    let confidence = 0.5; // Base confidence

    // Higher profit percentage = higher confidence
    if (profitPercentage > 2.0) confidence += 0.3;
    else if (profitPercentage > 1.0) confidence += 0.2;
    else if (profitPercentage > 0.5) confidence += 0.1;

    // Higher absolute profit = higher confidence
    if (netProfitUSD > 100) confidence += 0.2;
    else if (netProfitUSD > 50) confidence += 0.1;

    return Math.min(confidence, 0.95); // Cap at 95%
  }

  /**
   * Get base price for token (simplified - in production use real price feeds)
   */
  private getTokenBasePrice(symbol: string): number {
    const prices: Record<string, number> = {
      ETH: 3000,
      USDC: 1.0,
      USDT: 1.0,
      LINK: 15.0,
      UMA: 3.5,
      AAVE: 90.0
    };

    return prices[symbol] || 100;
  }

  /**
   * Prepare calldata for DEX interactions (simplified)
   */
  private prepareDEXCalldata(dexAddress: string, token: string, amount: string, action: 'buy' | 'sell'): string {
    // In a real implementation, this would prepare actual calldata for:
    // - Uniswap V3 exactInputSingle or exactOutputSingle
    // - Sushiswap swapExactTokensForTokens
    // - Balancer batchSwap
    // - Curve exchange
    
    // For now, return empty calldata
    return '0x';
  }

  /**
   * Monitor for new arbitrage opportunities
   */
  startMonitoring(
    tokenSymbols: string[],
    callback: (opportunities: FlashArbitrageOpportunity[]) => void,
    intervalMs: number = 10000
  ): NodeJS.Timeout {
    const checkOpportunities = async () => {
      for (const symbol of tokenSymbols) {
        try {
          const opportunities = await this.findArbitrageOpportunities(symbol);
          if (opportunities.length > 0) {
            callback(opportunities);
          }
        } catch (error) {
          console.error(`Error monitoring ${symbol}:`, error);
        }
      }
    };

    // Initial check
    checkOpportunities();

    // Set up interval
    return setInterval(checkOpportunities, intervalMs);
  }

  /**
   * Get network configuration
   */
  getNetworkConfig(chainId: number): NetworkConfig | undefined {
    return this.networks.get(chainId);
  }

  /**
   * Check if arbitrage bot is properly configured
   */
  async isConfigured(chainId: number): Promise<boolean> {
    const config = this.networks.get(chainId);
    if (!config) return false;

    try {
      const contract = FlashArbitrageBot__factory.connect(this.arbitrageBotAddress, this.provider);
      
      // Check if Aave pool is trusted
      const aavePoolTrusted = await contract.trustedLenders(config.aavePool);
      
      // Check if at least one DEX is trusted
      const dexAddresses = Object.values(config.dexes);
      const dexChecks = await Promise.all(
        dexAddresses.map(dex => contract.trustedDEXs(dex))
      );
      const hasTrustedDEX = dexChecks.some(trusted => trusted);

      return aavePoolTrusted && hasTrustedDEX;
    } catch (error) {
      console.error('Error checking configuration:', error);
      return false;
    }
  }
}

export default FlashArbitrageService;
