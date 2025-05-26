import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Progress } from "../ui/progress";
import { Button } from "../ui/button";
import { Alert, AlertDescription } from "../ui/alert";
import { Badge } from "../ui/badge";

interface RiskMetrics {
  overall_risk_score: number;
  portfolio_volatility: number;
  max_drawdown: number;
  var_95: number;
  position_concentration: number;
  leverage_ratio: number;
  liquidity_risk: number;
  correlation_risk: number;
  recommendations: string[];
  risk_breakdown: {
    crypto: number;
    stables: number;
    volatile: number;
  };
}

export const RiskAssessment: React.FC = () => {
  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const assessRisk = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Get portfolio data
      const portfolioResponse = await fetch('/api/portfolio');
      const portfolioData = await portfolioResponse.json();
      
      // Get current market data for risk calculation
      const marketResponse = await fetch('/api/market/prices');
      const marketData = await marketResponse.json();
      
      // Calculate risk metrics using your sophisticated backend
      const riskResponse = await fetch('/api/trading/risk-assessment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          portfolio: portfolioData,
          market_data: marketData
        })
      });
      
      if (!riskResponse.ok) {
        throw new Error('Failed to assess portfolio risk');
      }
      
      const metrics = await riskResponse.json();
      setRiskMetrics(metrics);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to assess portfolio risk';
      setError(errorMessage);
      console.error('Risk assessment error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    assessRisk();
  }, []);

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

  const getRiskBadgeVariant = (score: number): "default" | "secondary" | "destructive" => {
    if (score < 0.3) return 'default';
    if (score < 0.7) return 'secondary';
    return 'destructive';
  };

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-xl font-bold">🛡️ Portfolio Risk Assessment</CardTitle>
          <Button 
            onClick={assessRisk} 
            disabled={isLoading}
            className="bg-gradient-to-r from-blue-500 to-purple-600"
          >
            {isLoading ? '🔄 Analyzing...' : '📊 Refresh Analysis'}
          </Button>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {riskMetrics && (
            <>
              {/* Overall Risk Score */}
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-4 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-lg font-semibold">Overall Risk Score</span>
                  <Badge variant={getRiskBadgeVariant(riskMetrics.overall_risk_score)}>
                    {getRiskLabel(riskMetrics.overall_risk_score)}
                  </Badge>
                </div>
                <Progress 
                  value={riskMetrics.overall_risk_score * 100} 
                  className="h-3"
                />
                <span className={`text-sm font-bold ${getRiskColor(riskMetrics.overall_risk_score)}`}>
                  {(riskMetrics.overall_risk_score * 100).toFixed(1)}%
                </span>
              </div>

              {/* Risk Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 p-3 rounded-lg">
                  <h4 className="font-semibold text-blue-800">Portfolio Volatility</h4>
                  <p className="text-lg font-bold text-blue-600">
                    {(riskMetrics.portfolio_volatility * 100).toFixed(1)}%
                  </p>
                </div>
                
                <div className="bg-red-50 p-3 rounded-lg">
                  <h4 className="font-semibold text-red-800">Max Drawdown</h4>
                  <p className="text-lg font-bold text-red-600">
                    {(riskMetrics.max_drawdown * 100).toFixed(1)}%
                  </p>
                </div>
                
                <div className="bg-orange-50 p-3 rounded-lg">
                  <h4 className="font-semibold text-orange-800">VaR (95%)</h4>
                  <p className="text-lg font-bold text-orange-600">
                    {(riskMetrics.var_95 * 100).toFixed(1)}%
                  </p>
                </div>
                
                <div className="bg-purple-50 p-3 rounded-lg">
                  <h4 className="font-semibold text-purple-800">Concentration</h4>
                  <p className="text-lg font-bold text-purple-600">
                    {(riskMetrics.position_concentration * 100).toFixed(1)}%
                  </p>
                </div>
              </div>

              {/* Risk Breakdown */}
              <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3 text-indigo-800">Risk Distribution</h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span>Crypto Assets</span>
                    <div className="flex items-center space-x-2">
                      <Progress value={riskMetrics.risk_breakdown.crypto * 100} className="w-20 h-2" />
                      <span className="text-sm font-bold">
                        {(riskMetrics.risk_breakdown.crypto * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Stablecoins</span>
                    <div className="flex items-center space-x-2">
                      <Progress value={riskMetrics.risk_breakdown.stables * 100} className="w-20 h-2" />
                      <span className="text-sm font-bold">
                        {(riskMetrics.risk_breakdown.stables * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Volatile Assets</span>
                    <div className="flex items-center space-x-2">
                      <Progress value={riskMetrics.risk_breakdown.volatile * 100} className="w-20 h-2" />
                      <span className="text-sm font-bold">
                        {(riskMetrics.risk_breakdown.volatile * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* AI Recommendations */}
              {riskMetrics.recommendations.length > 0 && (
                <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded-lg">
                  <h4 className="font-semibold mb-3 text-green-800">🤖 AI Risk Recommendations</h4>
                  <ul className="space-y-2">
                    {riskMetrics.recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <span className="text-green-600 font-bold">•</span>
                        <span className="text-green-700">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
