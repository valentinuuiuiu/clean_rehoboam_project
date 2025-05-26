import React, { useState, useEffect } from 'react';
import { useWeb3 } from './contexts/Web3Context';
import { useNotification } from './contexts/NotificationContext';
import { useAsyncHandler } from './hooks/useAsyncHandler';
import { Card } from './components/ui/card';
import { Progress } from './components/ui/progress';
import { ErrorMessage } from './components/ErrorMessage';

const AutomatedTrading: React.FC = () => {
  const { account, connectWallet } = useWeb3();
  const { addNotification } = useNotification();
  const { handleAsync, error } = useAsyncHandler({
    loadingKey: 'automated-trading',
    successMessage: 'Trading executed successfully',
    errorMessage: 'Failed to execute trading'
  });

  const [tradingData, setTradingData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!account) return;
    setIsLoading(true);
    handleAsync(async () => {
      // Fetch trading data
      const response = await fetch('/api/trading-data');
      const data = await response.json();
      setTradingData(data);
    }).finally(() => setIsLoading(false));
  }, [account, handleAsync]);

  const executeTrade = async () => {
    if (!account) {
      addNotification('error', 'Please connect your wallet to execute trades');
      return;
    }

    handleAsync(async () => {
      // Execute trade
      const response = await fetch('/api/execute-trade', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ account })
      });
      const result = await response.json();
      addNotification('success', `Trade executed: ${result.message}`);
    });
  };

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center space-x-2">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500" />
          <span>Loading trading data...</span>
        </div>
      </Card>
    );
  }

  if (error) {
    return <ErrorMessage error={error} />;
  }

  return (
    <Card className="p-6">
      <h2 className="text-xl font-bold mb-4">Automated Trading</h2>
      {tradingData ? (
        <div>
          <p className="mb-4">Trading data loaded successfully.</p>
          <button
            onClick={executeTrade}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Execute Trade
          </button>
        </div>
      ) : (
        <p className="text-gray-500">No trading data available.</p>
      )}
    </Card>
  );
};

export default AutomatedTrading;