import React, { useState, useEffect } from 'react';
import { Card } from './components/ui/card';
import { Progress } from './components/ui/progress';
import { ErrorMessage } from './components/ErrorMessage';
import { useFetchWithPerformance } from './hooks/useFetchWithPerformance';

const MarketSentiment: React.FC = () => {
  const { data: sentimentData, error, isLoading } = useFetchWithPerformance<any>({
    queryKey: ['market-sentiment'],
    fetchFn: async () => {
      const response = await fetch('/api/market-sentiment');
      return response.json();
    },
    componentName: 'MarketSentiment',
    successMessage: 'Market sentiment data loaded successfully',
    errorMessage: 'Failed to load market sentiment data'
  });

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center space-x-2">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500" />
          <span>Loading market sentiment...</span>
        </div>
      </Card>
    );
  }

  if (error) {
    return <ErrorMessage error={error} />;
  }

  return (
    <Card className="p-6">
      <h2 className="text-xl font-bold mb-4">Market Sentiment</h2>
      {sentimentData ? (
        <div>
          <p className="mb-4">Market sentiment data loaded successfully.</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {sentimentData.map((sentiment: any, index: number) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg">
                <h3 className="text-lg font-semibold mb-2">{sentiment.name}</h3>
                <Progress value={sentiment.score * 100} className="mb-2" />
                <p className="text-sm text-gray-500">{sentiment.description}</p>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <p className="text-gray-500">No market sentiment data available.</p>
      )}
    </Card>
  );
};

export default MarketSentiment;
