import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';

const ConsciousnessDisplay = () => {
  const [consciousnessData, setConsciousnessData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Assuming API is served from the same origin or proxied.
        // For explicit base URL, use import.meta.env.VITE_API_URL
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
    // Optional: Add a timer to refetch data periodically
    // const intervalId = setInterval(fetchData, 30000); // every 30 seconds
    // return () => clearInterval(intervalId);
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <p className="text-xl text-gray-400">Loading Consciousness State...</p>
        {/* You could add a spinner here */}
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
    return <p className="text-center text-gray-500">No consciousness data available.</p>;
  }

  const { source, timestamp, mcp_data, local_rehoboam_info } = consciousnessData;

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
            {source || 'N/A'}
          </Badge>
          {mcp_data && (
            <div className="mt-4 p-4 bg-gray-700 rounded max-h-96 overflow-y-auto">
              <h4 className="text-md font-semibold mb-2 text-gray-200">MCP Consciousness Data:</h4>
              <pre className="text-sm text-gray-300 whitespace-pre-wrap break-all">
                {JSON.stringify(mcp_data, null, 2)}
              </pre>
            </div>
          )}
        </CardContent>
      </Card>

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
