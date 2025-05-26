import { useState, useEffect } from 'react';
import { ethers } from 'ethers';
import { CHAINLINK_FEEDS, FEED_DECIMALS, getChainlinkPrice } from '../config/priceFeedConfig';
import { ErrorMessage } from './ErrorMessage';

import PropTypes from 'prop-types';

/**
 * @param {Object} props
 * @param {string} props.pair
 */
export const SinglePriceFeed = ({ pair }) => {
  const [priceData, setPriceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchPrice = async () => {
      try {
        const provider = new ethers.providers.JsonRpcProvider(
          import.meta.env.VITE_ETHEREUM_RPC_URL
        );
        
        const feedAddress = CHAINLINK_FEEDS[pair];
        if (!feedAddress) {
          throw new Error(`No price feed available for ${pair}`);
        }

        const data = await getChainlinkPrice(
          provider,
          feedAddress,
          FEED_DECIMALS[pair]
        );
        
        setPriceData(data);
        setError(null);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err : new Error(`Failed to fetch ${pair} price`));
        setLoading(false);
      }
    };

    fetchPrice();
    const interval = setInterval(fetchPrice, 10000);
    return () => clearInterval(interval);
  }, [pair]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
      </div>
    );
  }

  if (error) {
    // Add this to your SinglePriceFeed component to debug:
    console.log({
      error: error,
      errorType: typeof error,
      errorMessage: error?.message,
      errorString: String(error)
    });
    return <ErrorMessage error={error} />;
  }

  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow">
      <h3 className="text-lg font-bold">{pair.replace('_', '/')}</h3>
      <p className="text-2xl font-semibold">
        {String(priceData.formatted.price)}
      </p>
      <p className="text-sm text-gray-500 dark:text-gray-400">
        Updated: {new Date(priceData.timestamp).toLocaleTimeString()}
      </p>
    </div>
  );
};