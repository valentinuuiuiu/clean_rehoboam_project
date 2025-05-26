import { PriceFeed } from './PriceFeed';
import { SinglePriceFeed } from './SinglePriceFeed';

export const Dashboard = () => {
  return (
    <div className="container mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Market Overview</h2>
      
      {/* Display specific assets */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <SinglePriceFeed pair="ETH_USD" />
        <SinglePriceFeed pair="BTC_USD" />
        <SinglePriceFeed pair="LINK_USD" />
      </div>

      {/* Display all price feeds */}
      <h2 className="text-2xl font-bold mb-4">All Markets</h2>
      <PriceFeed />
    </div>
  );
};