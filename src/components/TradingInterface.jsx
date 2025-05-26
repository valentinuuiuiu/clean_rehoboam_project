import React, { useState } from 'react';
import { tradingService } from '../services/tradingService';
import { useBinancePrices } from '../services/binanceService';
import { formatPrice, formatChange } from '../config/trading';

const TradingInterface = () => {
  const [depositAmount, setDepositAmount] = useState('');
  const [tradeAmount, setTradeAmount] = useState('');
  const [selectedPair, setSelectedPair] = useState('ETHUSDT');
  const [tradeSide, setTradeSide] = useState('buy');
  const { prices, error, isLoading } = useBinancePrices();

  const handleDeposit = async () => {
    const amount = parseFloat(depositAmount);
    if (isNaN(amount) || amount <= 0) {
      alert('Please enter a valid deposit amount');
      return;
    }

    const success = await tradingService.deposit('ETH', amount);
    if (success) {
      alert(`Successfully deposited ${amount} ETH`);
      setDepositAmount('');
      // Enable trading after deposit
      tradingService.enableTrading();
    } else {
      alert('Deposit failed. Please try again.');
    }
  };

  const handleTrade = async () => {
    const amount = parseFloat(tradeAmount);
    if (isNaN(amount) || amount <= 0) {
      alert('Please enter a valid trade amount');
      return;
    }

    const success = await tradingService.executeTrade(selectedPair, tradeSide, amount);
    if (success) {
      alert(`Successfully executed ${tradeSide} trade for ${amount} ${selectedPair}`);
      setTradeAmount('');
    } else {
      alert('Trade execution failed. Please check console for details.');
    }
  };

  const ethBalance = tradingService.getBalance('ETH');
  const positions = tradingService.getAllPositions();

  return (
    <div className="bg-gray-800 p-6 rounded-lg">
      <h2 className="text-2xl font-bold mb-6">Trading Interface</h2>
      
      {/* Deposit Section */}
      <div className="mb-8">
        <h3 className="text-xl mb-4">Deposit ETH</h3>
        <div className="flex gap-4">
          <input
            type="number"
            value={depositAmount}
            onChange={(e) => setDepositAmount(e.target.value)}
            placeholder="Amount of ETH"
            className="flex-1 bg-gray-700 p-2 rounded"
          />
          <button
            onClick={handleDeposit}
            className="bg-green-600 px-4 py-2 rounded hover:bg-green-700"
          >
            Deposit
          </button>
        </div>
      </div>

      {/* Balance Display */}
      <div className="mb-8">
        <h3 className="text-xl mb-4">Your Balance</h3>
        <div className="bg-gray-700 p-4 rounded">
          <p>ETH Available: {ethBalance?.free.toFixed(8) || '0.00000000'}</p>
          <p>ETH Locked: {ethBalance?.locked.toFixed(8) || '0.00000000'}</p>
        </div>
      </div>

      {/* Trading Section */}
      <div className="mb-8">
        <h3 className="text-xl mb-4">Execute Trade</h3>
        <div className="space-y-4">
          <div>
            <label className="block mb-2">Trading Pair</label>
            <select
              value={selectedPair}
              onChange={(e) => setSelectedPair(e.target.value)}
              className="w-full bg-gray-700 p-2 rounded"
            >
              <option value="ETHUSDT">ETH/USDT</option>
              <option value="BTCUSDT">BTC/USDT</option>
            </select>
          </div>

          <div>
            <label className="block mb-2">Trade Side</label>
            <div className="flex gap-4">
              <button
                onClick={() => setTradeSide('buy')}
                className={`flex-1 p-2 rounded ${
                  tradeSide === 'buy' ? 'bg-green-600' : 'bg-gray-700'
                }`}
              >
                Buy
              </button>
              <button
                onClick={() => setTradeSide('sell')}
                className={`flex-1 p-2 rounded ${
                  tradeSide === 'sell' ? 'bg-red-600' : 'bg-gray-700'
                }`}
              >
                Sell
              </button>
            </div>
          </div>

          <div>
            <label className="block mb-2">Amount</label>
            <input
              type="number"
              value={tradeAmount}
              onChange={(e) => setTradeAmount(e.target.value)}
              placeholder="Trade amount"
              className="w-full bg-gray-700 p-2 rounded"
            />
          </div>

          <button
            onClick={handleTrade}
            className="w-full bg-blue-600 p-2 rounded hover:bg-blue-700"
          >
            Execute Trade
          </button>
        </div>
      </div>

      {/* Positions Display */}
      <div>
        <h3 className="text-xl mb-4">Current Positions</h3>
        <div className="space-y-4">
          {positions.map((position, index) => (
            <div key={index} className="bg-gray-700 p-4 rounded">
              <p>Pair: {position.pair}</p>
              <p>Side: {position.side}</p>
              <p>Amount: {position.amount}</p>
              <p>Entry Price: {formatPrice(position.entryPrice)}</p>
              <p>Timestamp: {new Date(position.timestamp).toLocaleString()}</p>
            </div>
          ))}
          {positions.length === 0 && (
            <p className="text-gray-400">No active positions</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default TradingInterface;
