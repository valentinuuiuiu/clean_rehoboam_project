import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';

const ConsciousnessDisplay = () => {
  const [consciousnessData, setConsciousnessData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isRawJsonVisible, setIsRawJsonVisible] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch('/api/ai/consciousness-state');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        setConsciousnessData(data);
      } catch (e) {
        console.error("Failed to fetch consciousness state:", e);
        setError(e.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <p className="text-xl text-gray-400">Loading Consciousness State...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="bg-red-900/20 border-red-700">
        <CardHeader>
          <CardTitle className="text-red-400">Error Fetching Consciousness State</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-300">{error}</p>
          <p className="text-red-300 mt-2">Please ensure the backend API is running and the MCP services are accessible.</p>
        </CardContent>
      </Card>
    );
  }

  if (!consciousnessData) {
    return <p className="text-center text-gray-500 italic">No consciousness data available.</p>;
  }

  const { source, timestamp, mcp_data, local_rehoboam_info } = consciousnessData;
  const naText = <span className="text-gray-500 italic">N/A</span>;
  const noneActiveText = <p className="text-sm text-gray-500 italic">None active</p>;


  return (
    <div className="space-y-6 p-4 bg-gray-800 rounded-lg shadow-xl">
      <CardHeader className="p-0 mb-4">
        <CardTitle className="text-3xl font-bold text-blue-300">AI Consciousness State</CardTitle>
        <CardDescription className="text-gray-400">
          Current operational state of the AI consciousness layers. Timestamp: {new Date(timestamp).toLocaleString()}
        </CardDescription>
      </CardHeader>

      <Card>
        <CardHeader>
          <CardTitle className="text-xl text-blue-400">Primary Data Source</CardTitle>
        </CardHeader>
        <CardContent>
          <Badge variant={source === 'mcp_consciousness_layer' ? 'default' : 'secondary'} className="text-lg">
            {source || naText}
          </Badge>
        </CardContent>
      </Card>

      {mcp_data && (
        <Card>
          <CardHeader>
            <CardTitle className="text-xl text-blue-400">MCP Consciousness Metrics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Awareness Level */}
            <div className="bg-gray-700 p-3 rounded-md">
              <h4 className="text-md font-semibold text-gray-200 mb-1">Awareness Level</h4>
              <div className="w-full bg-gray-600 rounded-full h-6">
                <div
                  className="bg-blue-500 h-6 rounded-full text-xs font-medium text-blue-100 text-center p-1 leading-none"
                  style={{ width: `${(mcp_data.awareness_level || 0) * 100}%` }}
                >
                  {((mcp_data.awareness_level || 0) * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            {/* Current Focus */}
            <div className="bg-gray-700 p-3 rounded-md">
              <h4 className="text-md font-semibold text-gray-200">Current Focus</h4>
              <p className="text-sm text-gray-300">{mcp_data.current_focus || naText}</p>
            </div>

            {/* Operational Mode */}
            <div className="bg-gray-700 p-3 rounded-md">
              <h4 className="text-md font-semibold text-gray-200">Operational Mode</h4>
              <p className="text-sm text-gray-300">{mcp_data.operational_mode || naText}</p>
            </div>

            {/* Ethical Score */}
            <div className="bg-gray-700 p-3 rounded-md">
              <h4 className="text-md font-semibold text-gray-200 mb-1">Ethical Score</h4>
              <div className="w-full bg-gray-600 rounded-full h-6">
                <div
                  className="bg-green-500 h-6 rounded-full text-xs font-medium text-green-100 text-center p-1 leading-none"
                  style={{ width: `${(mcp_data.ethical_score || 0) * 100}%` }}
                >
                  {((mcp_data.ethical_score || 0) * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            {/* Risk Assessment */}
            <div className="bg-gray-700 p-3 rounded-md">
                <h4 className="text-md font-semibold text-gray-200 mb-1">Risk Propensity</h4>
                 <div className="w-full bg-gray-600 rounded-full h-6">
                  <div
                    className="bg-yellow-500 h-6 rounded-full text-xs font-medium text-yellow-100 text-center p-1 leading-none"
                    style={{ width: `${(mcp_data.risk_assessment?.propensity || 0) * 100}%` }}
                  >
                    {((mcp_data.risk_assessment?.propensity || 0) * 100).toFixed(1)}%
                  </div>
                </div>
                <p className="text-xs text-gray-400 mt-1">Current Level: {mcp_data.risk_assessment?.current_level || naText}</p>
            </div>


            {/* Cognitive Drivers */}
            <div className="bg-gray-700 p-3 rounded-md">
              <h4 className="text-md font-semibold text-gray-200 mb-2">Active Cognitive Drivers</h4>
              {mcp_data.cognitive_drivers && Array.isArray(mcp_data.cognitive_drivers) && mcp_data.cognitive_drivers.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {mcp_data.cognitive_drivers.map((driver, index) => (
                    <Badge key={index} variant="secondary" className="bg-purple-600 text-purple-100">
                      {driver}
                    </Badge>
                  ))}
                </div>
              ) : (
                noneActiveText
              )}
            </div>

            {/* Learning Status */}
            <div className="bg-gray-700 p-3 rounded-md">
                <h4 className="text-md font-semibold text-gray-200 mb-1">Learning Rate</h4>
                <div className="w-full bg-gray-600 rounded-full h-6">
                    <div
                        className="bg-indigo-500 h-6 rounded-full text-xs font-medium text-indigo-100 text-center p-1 leading-none"
                        style={{ width: `${(mcp_data.learning_status?.rate || 0) * 100}%` }}
                    >
                        {((mcp_data.learning_status?.rate || 0) * 100).toFixed(2)}%
                    </div>
                </div>
                <p className="text-xs text-gray-400 mt-1">
                    Last Update: {mcp_data.learning_status?.last_update ? new Date(mcp_data.learning_status.last_update).toLocaleTimeString() : naText}
                </p>
            </div>

            {/* Collapsible Raw JSON */}
            <div className="mt-4">
              <button
                onClick={() => setIsRawJsonVisible(!isRawJsonVisible)}
                className="text-sm text-blue-400 hover:text-blue-300 mb-2"
              >
                {isRawJsonVisible ? 'Hide' : 'Show'} Raw MCP Data
              </button>
              {isRawJsonVisible && (
                <div className="p-4 bg-gray-900 rounded max-h-96 overflow-y-auto">
                  <pre className="text-xs text-gray-300 whitespace-pre-wrap break-all">
                    {JSON.stringify(mcp_data, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {local_rehoboam_info && (
        <Card>
          <CardHeader>
            <CardTitle className="text-xl text-blue-400">Local Rehoboam AI Module Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-gray-300">
              Consciousness Matrix Available (Local):
              <Badge variant={local_rehoboam_info.consciousness_matrix_available ? 'default' : 'outline'} className="ml-2">
                {local_rehoboam_info.consciousness_matrix_available ? 'Yes' : 'No'}
              </Badge>
            </p>
            <div>
              <h4 className="text-md font-semibold mb-2 text-gray-200">Active Modules:</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {local_rehoboam_info.active_modules && Object.entries(local_rehoboam_info.active_modules).map(([module, isActive]) => (
                  <div key={module} className="flex items-center space-x-2 p-2 bg-gray-700 rounded">
                    <span className={`w-3 h-3 rounded-full ${isActive ? 'bg-green-500' : 'bg-red-500'}`}></span>
                    <span className="text-sm text-gray-300 capitalize">{module.replace(/_/g, ' ')}</span>
                  </div>
                ))}
              </div>
            </div>
             {local_rehoboam_info.cognitive_capabilities && (
              <div>
                <h4 className="text-md font-semibold mt-3 mb-2 text-gray-200">Cognitive Capabilities (Local):</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {Object.entries(local_rehoboam_info.cognitive_capabilities).map(([capability, isEnabled]) => (
                    <div key={capability} className="flex items-center space-x-2 p-2 bg-gray-700 rounded">
                      <span className={`w-3 h-3 rounded-full ${isEnabled ? 'bg-green-500' : 'bg-red-500'}`}></span>
                      <span className="text-sm text-gray-300 capitalize">{capability.replace(/_/g, ' ')}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ConsciousnessDisplay;
