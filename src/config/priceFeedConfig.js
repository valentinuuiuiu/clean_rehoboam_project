export const CHAINLINK_FEEDS = {
  // Ethereum Mainnet Price Feeds
  ETH_USD: '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419',
  BTC_USD: '0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c',
  LINK_USD: '0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c',
  DAI_USD: '0xAed0c38402a5d19df6E4c03F4E2DceD6e29c1ee9',
  USDC_USD: '0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6',
  USDT_USD: '0x3E7d1eAB13ad0104d2750B8863b489D65364e32D',
  // DeFi Tokens
  AAVE_USD: '0x547a514d5e3769680Ce22B2361c10Ea13619e8a9',
  UNI_USD: '0x553303d460EE0afB37EdFf9bE42922D8FF63220e',
  SNX_USD: '0xDC3EA94CD0AC27d9A86C180091e7f78C683d3699',
  // Layer 2 and Sidechains
  MATIC_USD: '0x7bAC85A8a13A4BcD8abb3eB7d6b4d632c5a57676', // Polygon
  AVAX_USD: '0xFF3EEb22B5E3dE6e705b44749C2559d704923FD7', // Avalanche
  FTM_USD: '0x2DE7E4a9488488e0058B95854CC2f7955B35dC9b',  // Fantom
  // Commodities
  XAU_USD: '0x214eD9Da11D2fbe465a6fc601a91E62EbEc1a0D6', // Gold
  XAG_USD: '0x379589227b15F1a12195D3f2d90bBc9F31f95235', // Silver
};

// Feed decimals (most use 8 decimals but some differ)
export const FEED_DECIMALS = {
  ETH_USD: 8,
  BTC_USD: 8,
  LINK_USD: 8,
  DAI_USD: 8,
  USDC_USD: 8,
  USDT_USD: 8,
  AAVE_USD: 8,
  UNI_USD: 8,
  SNX_USD: 8,
  MATIC_USD: 8,
  AVAX_USD: 8,
  FTM_USD: 8,
  XAU_USD: 8,
  XAG_USD: 8,
};

// Update intervals in seconds
export const UPDATE_INTERVALS = {
  FAST: 10,    // Fast updating pairs like ETH, BTC
  MEDIUM: 30,  // Medium frequency updates
  SLOW: 60,    // Slower updating pairs
};

export const getChainlinkPrice = async (provider, feedAddress, decimals = 8) => {
  const aggregatorV3InterfaceABI = [
    {
      inputs: [],
      name: "latestRoundData",
      outputs: [
        { name: "roundId", type: "uint80" },
        { name: "answer", type: "int256" },
        { name: "startedAt", type: "uint256" },
        { name: "updatedAt", type: "uint256" },
        { name: "answeredInRound", type: "uint80" }
      ],
      stateMutability: "view",
      type: "function"
    }
  ];

  try {
    const priceFeed = new ethers.Contract(
      feedAddress,
      aggregatorV3InterfaceABI,
      provider
    );

    const [, answer, , updatedAt] = await priceFeed.latestRoundData();
    const timestamp = Number(updatedAt) * 1000; // Convert to milliseconds
    const price = Number(ethers.formatUnits(answer, decimals));

    return {
      price,
      timestamp,
      formatted: {
        price: price.toFixed(2),
        lastUpdate: new Date(timestamp).toLocaleString()
      }
    };
  } catch (error) {
    console.error(`Error fetching price for feed ${feedAddress}:`, error);
    throw error;
  }
};