import { useState, useEffect } from 'react';
import { ethers } from 'ethers';
import { CHAINLINK_FEEDS, FEED_DECIMALS, getChainlinkPrice } from '../config/priceFeedConfig';
import { ErrorMessage } from './ErrorMessage';

export const PriceFeed = () => {
  const [prices, setPrices] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchPrices = async () => {
      try {
        const provider = new ethers.providers.JsonRpcProvider(
          import.meta.env.VITE_ETHEREUM_RPC_URL
        );

        const priceEntries = await Promise.all(
          Object.entries(CHAINLINK_FEEDS).map(async ([pair, address]) => {
            try {
              const data = await getChainlinkPrice(provider, address, FEED_DECIMALS[pair]);
              return [pair, data];
            } catch (err) {
              console.error(`Error fetching ${pair}:`, err);
              return [pair, null]; // Return null for failed fetches
            }
          })
        );

        // Filter out failed fetches
        const validPrices = priceEntries.filter(([, data]) => data !== null);
        setPrices(Object.fromEntries(validPrices));
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch prices'));
        setLoading(false);
      }
    };

    fetchPrices();
    const interval = setInterval(fetchPrices, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
      </div>
    );
  }

  if (error) {
    return <ErrorMessage error={error} />;
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 p-4">
      {Object.entries(prices).map(([pair, data]) => (
        <div key={pair} className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow">
          <h3 className="text-lg font-bold">{pair.replace('_', '/')}</h3>
          <p className="text-2xl font-semibold">${data.formatted.price}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Updated: {new Date(data.timestamp).toLocaleTimeString()}
          </p>
        </div>
      ))}
    </div>
  );
};