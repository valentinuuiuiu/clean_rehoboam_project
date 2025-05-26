import React from "react";
import { useQuery } from '@tanstack/react-query';
import { Card } from "./ui/card";
import { Progress } from "./ui/progress";
import { ErrorMessage } from "./ErrorMessage";
import { useLoading } from "../contexts/LoadingContext";
import { useNotification } from "../contexts/NotificationContext";
import { useTradingWorker } from "../hooks/useTradingWorker";
import { useWeb3 } from "../contexts/Web3Context";

export const RiskAssessment: React.FC = () => {
  const { isLoading, startLoading, stopLoading } = useLoading();
  const { addNotification } = useNotification();
  const { assessRisk } = useTradingWorker();
  const { account } = useWeb3();

  const { data: riskMetrics, error, isError } = useQuery({
    queryKey: ['risk-assessment', account],
    queryFn: async () => {
      if (!account) throw new Error('Wallet not connected');
      
      startLoading('risk-assessment');
      try {
        const result = await assessRisk({
          account,
          timestamp: Date.now()
        });
        addNotification('success', 'Risk assessment completed');
        return result;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to assess risk';
        addNotification('error', message);
        throw err;
      } finally {
        stopLoading('risk-assessment');
      }
    },
    enabled: !!account,
    staleTime: 60000, // Consider data stale after 1 minute
    cacheTime: 5 * 60000 // Cache for 5 minutes
  });

  if (!account) {
    return (
      <Card className="p-6">
        <p className="text-center text-gray-500">Please connect your wallet to view risk assessment</p>
      </Card>
    );
  }

  if (isError) {
    return <ErrorMessage error={error} />;
  }

  if (isLoading('risk-assessment')) {
    return (
      <Card className="p-6">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
          <p className="text-gray-500">Analyzing portfolio risks...</p>
        </div>
      </Card>
    );
  }

  if (!riskMetrics) {
    return (
      <Card className="p-6">
        <p className="text-center text-gray-500">No risk data available</p>
      </Card>
    );
  }

  const { overallRisk, metrics } = riskMetrics;

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Overall Risk Score</h3>
        <div className="flex items-center space-x-4">
          <Progress 
            value={overallRisk * 100} 
            className={`
              ${overallRisk < 0.3 ? 'bg-green-200' : ''}
              ${overallRisk >= 0.3 && overallRisk < 0.7 ? 'bg-yellow-200' : ''}
              ${overallRisk >= 0.7 ? 'bg-red-200' : ''}
            `}
          />
          <span className={`font-bold ${
            overallRisk < 0.3 ? 'text-green-500' :
            overallRisk < 0.7 ? 'text-yellow-500' :
            'text-red-500'
          }`}>
            {Math.round(overallRisk * 100)}%
          </span>
        </div>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6">
          <h4 className="font-medium mb-2">Volatility Risk</h4>
          <Progress value={metrics.volatility * 100} className="mb-2" />
          <p className="text-sm text-gray-500">
            Market volatility impact on your portfolio
          </p>
        </Card>

        <Card className="p-6">
          <h4 className="font-medium mb-2">Exposure Risk</h4>
          <Progress value={metrics.exposure * 100} className="mb-2" />
          <p className="text-sm text-gray-500">
            Total exposure across different assets
          </p>
        </Card>

        <Card className="p-6">
          <h4 className="font-medium mb-2">Concentration Risk</h4>
          <Progress value={metrics.concentration * 100} className="mb-2" />
          <p className="text-sm text-gray-500">
            Portfolio concentration in single assets
          </p>
        </Card>
      </div>
    </div>
  );
};

export default RiskAssessment;
