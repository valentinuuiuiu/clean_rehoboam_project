import React, { useState } from "react";
import { riskAssessmentService, RiskMetrics } from "../services/trading/riskAssessmentService";
import { tradingExecutionService } from "../services/trading/executionService";
import { ErrorMessage } from "./ErrorMessage";
import { Progress } from "./ui/progress";

const RiskAssessment = () => {
  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAssessRisk = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const positions = await tradingExecutionService.getPositions();
      const metrics = await riskAssessmentService.assessPortfolioRisk(positions);
      setRiskMetrics(metrics);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to assess portfolio risk';
      setError(errorMessage);
      console.error('Risk assessment error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskColor = (score: number) => {
    if (score < 0.3) return 'text-green-500';
    if (score < 0.7) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getRiskLabel = (score: number) => {
    if (score < 0.3) return 'Low Risk';
    if (score < 0.7) return 'Medium Risk';
    return 'High Risk';
  };

  if (error) {
    return <ErrorMessage error={error} />;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">Portfolio Risk Assessment</h2>
        <button
          onClick={handleAssessRisk}
          disabled={isLoading}
          className={`px-4 py-2 rounded-lg ${
            isLoading 
              ? 'bg-gray-300 cursor-not-allowed' 
              : 'bg-blue-500 hover:bg-blue-600'
          } text-white`}
        >
          {isLoading ? 'Analyzing...' : 'Assess Risk'}
        </button>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
        </div>
      )}

      {!isLoading && riskMetrics && (
        <div className="space-y-6">
          <div className="p-6 bg-white rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Overall Risk Score</h3>
            <div className="flex items-center space-x-4">
              <Progress value={riskMetrics.overallScore * 100} max={100} />
              <span className={`font-bold ${getRiskColor(riskMetrics.overallScore)}`}>
                {getRiskLabel(riskMetrics.overallScore)}
              </span>
            </div>
          </div>

          {riskMetrics.factors?.map((factor, index) => (
            <div key={index} className="p-6 bg-white rounded-lg shadow">
              <h4 className="font-medium mb-2">{factor.name}</h4>
              <div className="flex items-center space-x-4">
                <Progress value={factor.score * 100} max={100} />
                <span className={`${getRiskColor(factor.score)}`}>
                  {Math.round(factor.score * 100)}%
                </span>
              </div>
              {factor.recommendations && (
                <p className="mt-2 text-sm text-gray-600">{factor.recommendations}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RiskAssessment;
