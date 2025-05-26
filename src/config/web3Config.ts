// Replace with process.env
const INFURA_API_KEY = process.env.VITE_INFURA_API_KEY;

// RPC URLs using the INFURA_API_KEY
const RPC_URLS = {
  ethereum: `https://mainnet.infura.io/v3/${INFURA_API_KEY}`,
  arbitrum: `https://arbitrum-mainnet.infura.io/v3/${INFURA_API_KEY}`,
  optimism: `https://optimism-mainnet.infura.io/v3/${INFURA_API_KEY}`,
  polygon: `https://polygon-mainnet.infura.io/v3/${INFURA_API_KEY}`
};

export { INFURA_API_KEY, RPC_URLS };