import React, { useState } from 'react';
import { useWeb3 } from './contexts/Web3Context';
import { useNotification } from './contexts/NotificationContext';
import { useAsyncHandler } from './hooks/useAsyncHandler';
import { Card } from './components/ui/card';
import { Progress } from './components/ui/progress';
import { ErrorMessage } from './components/ErrorMessage';

const TradingDeposit: React.FC = () => {
  const { account, connectWallet } = useWeb3();
  const { addNotification } = useNotification();
  const { handleAsync, error } = useAsyncHandler({
    loadingKey: 'trading-deposit',
    successMessage: 'Deposit successful',
    errorMessage: 'Failed to deposit'
  });

  const [amount, setAmount] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(false);

  const handleDeposit = async () => {
    if (!account) {
      addNotification('error', 'Please connect your wallet to deposit');
      return;
    }

    handleAsync(async () => {
      // Execute deposit
      const response = await fetch('/api/deposit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ account, amount })
      });
      const result = await response.json();
      addNotification('success', `Deposit successful: ${result.message}`);
    });
  };

  return (
    <Card className="p-6">
      <h2 className="text-xl font-bold mb-4">Trading Deposit</h2>
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700">Amount</label>
        <input
          type="number"
          value={amount}
          onChange={(e) => setAmount(Number(e.target.value))}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
        />
      </div>
      <button
        onClick={handleDeposit}
        className={`px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
        disabled={isLoading}
      >
        {isLoading ? 'Processing...' : 'Deposit'}
      </button>
      {error && <ErrorMessage error={error} />}
    </Card>
  );
};

export default TradingDeposit;