import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { useWebSocket } from '../hooks/useWebSocket';

/**
 * MCPFunctionVisualizer Component
 * 
 * This component provides a real-time visualization of the MCP function generation
 * and execution process, showing how functions are dynamically created and used
 * by the AI companions.
 */
const MCPFunctionVisualizer = () => {
  // State to store MCP function data
  const [mcpFunctions, setMcpFunctions] = useState([]);
  const [functionCalls, setFunctionCalls] = useState([]);
  const [selectedFunction, setSelectedFunction] = useState(null);
  const [activeTab, setActiveTab] = useState('functions');
  const [isLoading, setIsLoading] = useState(true);

  // State for the test API call
  const [isExecutingTestCall, setIsExecutingTestCall] = useState(false);
  const [testCallError, setTestCallError] = useState(null);
  const [testCallResponse, setTestCallResponse] = useState(null);
  
  // WebSocket for real-time updates
  const wsApiPath = '/api/mcp/ws';
  const wsOptions = {
    reconnectInterval: 3000,
    maxReconnectAttempts: 10,
    onOpen: () => console.log('MCP WebSocket connected successfully'),
    onClose: () => console.log('MCP WebSocket connection closed'),
    onError: (error) => console.error('MCP WebSocket error:', error),
    onMessage: handleWebSocketMessage
  };
  
  const { isConnected, lastMessage, send } = useWebSocket(wsApiPath, wsOptions);
  const messagesEndRef = useRef(null);
  
  // Handle incoming WebSocket messages
  function handleWebSocketMessage(data) {
    console.log('MCP WebSocket message received:', data);
    
    if (data.type === 'mcp_function_registered') {
      // Add or update function in the list
      setMcpFunctions(prevFuncs => {
        const existingIndex = prevFuncs.findIndex(f => f.name === data.function.name);
        if (existingIndex !== -1) {
          const updatedFuncs = [...prevFuncs];
          updatedFuncs[existingIndex] = { ...updatedFuncs[existingIndex], ...data.function };
          return updatedFuncs;
        }
        return [...prevFuncs, data.function];
      });
    } 
    else if (data.type === 'mcp_function_executed') {
      const execution = data.execution;
      // Add new function call to the list
      setFunctionCalls(prev => [execution, ...prev].slice(0, 100)); // Keep last 100 calls
      // Update the last_execution for the specific function in the mcpFunctions list
      setMcpFunctions(prevFuncs =>
        prevFuncs.map(f =>
          f.name === execution.function_name
            ? { ...f, last_execution: execution }
            : f
        )
      );
      // If this executed function is currently selected, update its details too
      if (selectedFunction && selectedFunction.name === execution.function_name) {
        setSelectedFunction(prevSelected => ({ ...prevSelected, last_execution: execution }));
      }
    }
    else if (data.type === 'mcp_functions_list') {
      // Set the full list of functions
      setMcpFunctions(data.functions || []); // Ensure it's an array
      setIsLoading(false);
    }
    else if (data.type === 'mcp_function_calls_list') {
      // Set the list of recent function calls
      setFunctionCalls(data.calls || []); // Ensure it's an array
      setIsLoading(false);
    }
    else if (data.type === 'mcp_function_details') {
      const detailedFunc = data.function;
      if (detailedFunc) {
        // Update the function in the main list
        setMcpFunctions(prevFuncs =>
          prevFuncs.map(f => f.name === detailedFunc.name ? { ...f, ...detailedFunc } : f)
        );
        // If this function is currently selected, update the selectedFunction state
        if (selectedFunction && selectedFunction.name === detailedFunc.name) {
          setSelectedFunction(prevSelected => ({...prevSelected, ...detailedFunc}));
        }
      }
    }
  }
  
  // Fetch initial data
  useEffect(() => {
    const fetchMCPFunctions = async () => {
      try {
        const response = await fetch('/api/mcp/functions');
        if (response.ok) {
          const data = await response.json();
          setMcpFunctions(data);
        }
      } catch (error) {
        console.error('Error fetching MCP functions:', error);
      }
    };
    
    const fetchMCPFunctionCalls = async () => {
      try {
        const response = await fetch('/api/mcp/function-calls');
        if (response.ok) {
          const data = await response.json();
          setFunctionCalls(data);
        }
      } catch (error) {
        console.error('Error fetching MCP function calls:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchMCPFunctions();
    fetchMCPFunctionCalls();
  }, []);
  
  // Auto-scroll to bottom of execution logs
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [functionCalls]);
  
  // Request function details
  const handleFunctionSelect = (func) => {
    // If the same function is clicked, and we already have details, maybe toggle or do nothing?
    // For now, always re-select and re-fetch, ensuring UI updates if details change.
    setSelectedFunction(func);
    
    // Request more details via WebSocket if connected
    if (isConnected) {
      send({
        type: 'get_function_details',
        function_name: func.name
      });
    }
  };
  
  // Format parameter display
  const formatParameters = (parameters) => {
    if (!parameters || Object.keys(parameters).length === 0) {
      return <p className="text-sm text-gray-400">This function takes no parameters.</p>;
    }
    
    return (
      <div className="space-y-2 bg-gray-700 p-3 rounded-md">
        {Object.entries(parameters).map(([name, type]) => (
          <div key={name} className="flex justify-between items-center text-sm">
            <span className="font-mono text-purple-300 bg-gray-800 px-2 py-1 rounded">{name}</span>
            <span className="text-gray-300">{String(type) || 'any'}</span>
          </div>
        ))}
      </div>
    );
  };
  
  // Format timestamp
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };
  
  // Format execution status badge
  const getStatusBadge = (status) => {
    switch(status) {
      case 'success':
        return <Badge className="bg-green-100 text-green-800">Success</Badge>;
      case 'error':
        return <Badge className="bg-red-100 text-red-800">Error</Badge>;
      case 'in_progress':
        return <Badge className="bg-blue-100 text-blue-800">In Progress</Badge>;
      default:
        return <Badge className="bg-gray-100 text-gray-800">{status}</Badge>;
    }
  };

  const handleExecuteTestCall = async () => {
    setIsExecutingTestCall(true);
    setTestCallError(null);
    setTestCallResponse(null);

    const payload = {
      function_name: "mcp-consciousness-layer", // Target service
      parameters: {
        mcp_action: "emotions" // Action to perform on the target service
      }
    };

    try {
      const response = await fetch('/api/ai/mcp-function', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`HTTP error ${response.status}: ${errorData || response.statusText}`);
      }
      const data = await response.json();
      setTestCallResponse(data);
      console.log("Test call response:", data);
    } catch (error) {
      console.error("Test call failed:", error);
      setTestCallError(error.message);
    } finally {
      setIsExecutingTestCall(false);
    }
  };
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">MCP Function Visualizer</h1>
      
      <div className="flex items-center justify-between mb-4">
        <div>
          <Badge className={isConnected ? "bg-green-500 text-white" : "bg-red-500 text-white"}>
            {isConnected ? "Connected" : "Disconnected"}
          </Badge>
          <span className="ml-2 text-sm text-gray-400">
            {isConnected ? "Receiving real-time updates" : "Attempting to reconnect..."}
          </span>
        </div>
      </div>

      {/* Test Call Section */}
      <Card className="mb-6 bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-lg text-amber-400">Test Enhanced MCP Specialist Call</CardTitle>
          <CardDescription className="text-gray-400">
            Invoke a predefined function on an MCP service via the `/api/ai/mcp-function` endpoint,
            which uses the `EnhancedMCPSpecialist`.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            onClick={handleExecuteTestCall}
            disabled={isExecutingTestCall}
            className="bg-amber-500 hover:bg-amber-600 text-black"
          >
            {isExecutingTestCall ? 'Executing...' : 'Call: Get Consciousness Emotions'}
          </Button>
          {isExecutingTestCall && <p className="text-amber-300 mt-2">Loading response...</p>}
          {testCallError && (
            <div className="mt-4 p-3 bg-red-900/50 border border-red-700 rounded-md">
              <h4 className="font-semibold text-red-400">Error:</h4>
              <pre className="text-xs text-red-300 whitespace-pre-wrap">{testCallError}</pre>
            </div>
          )}
          {testCallResponse && (
            <div className="mt-4 p-3 bg-gray-700 rounded-md">
              <h4 className="font-semibold text-gray-200">Response:</h4>
              <pre className="text-xs text-gray-300 whitespace-pre-wrap max-h-60 overflow-y-auto">
                {JSON.stringify(testCallResponse, null, 2)}
              </pre>
            </div>
          )}
        </CardContent>
      </Card>
      
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2 bg-gray-700 text-gray-300">
          <TabsTrigger value="functions" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white">Registered Functions</TabsTrigger>
          <TabsTrigger value="executions" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white">Function Executions</TabsTrigger>
        </TabsList>
        
        <TabsContent value="functions" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="md:col-span-1 bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-xl text-blue-300">MCP Functions</CardTitle>
                <CardDescription className="text-gray-400">
                  Dynamic functions registered in the MCP ecosystem. Click to see details.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="p-4 text-center text-gray-400">Loading functions...</div>
                ) : mcpFunctions.length > 0 ? (
                  <ul className="max-h-[calc(100vh-300px)] overflow-y-auto space-y-2 pr-2"> {/* Adjusted height */}
                    {mcpFunctions.map(func => (
                      <li 
                        key={func.name} 
                        className={`p-3 border border-gray-600 rounded cursor-pointer hover:bg-gray-700 transition-colors ${
                          selectedFunction?.name === func.name ? 'bg-gray-700 border-blue-500 shadow-md' : 'bg-gray-800/50'
                        }`}
                        onClick={() => handleFunctionSelect(func)}
                      >
                        <h3 className="font-medium text-blue-400">{func.name}</h3>
                        <div className="mt-1 text-sm text-gray-400 truncate">
                          {func.description || "No description"}
                        </div>
                        <div className="mt-2">
                          <Badge variant="outline" className="border-purple-600 text-purple-400 text-xs">
                            {func.mcp_type || "processor"}
                          </Badge>
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="p-4 text-center text-gray-500">
                    No MCP functions registered yet. Waiting for WebSocket updates...
                  </div>
                )}
              </CardContent>
            </Card>
            
            <Card className="md:col-span-2 bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-xl text-blue-300">
                  {selectedFunction ? selectedFunction.name : 'Function Details'}
                </CardTitle>
                {selectedFunction && (
                  <CardDescription className="text-gray-400 mt-1">
                    {selectedFunction.description || "No detailed description available."}
                  </CardDescription>
                )}
              </CardHeader>
              <CardContent className="text-gray-200">
                {selectedFunction ? (
                  <div className="space-y-6">
                    <div>
                        <h4 className="text-md font-semibold text-purple-400 mb-1">Type</h4>
                      <Badge variant="outline" className="border-purple-600 text-purple-400">
                        {selectedFunction.mcp_type || "processor"}
                      </Badge>
                    </div>
                    
                    <div>
                      <h4 className="text-md font-semibold text-purple-400 mb-1">Parameters</h4>
                      {formatParameters(selectedFunction.parameters)}
                    </div>
                    
                    {selectedFunction.source_code && (
                      <div className="mt-3">
                        <h4 className="text-md font-semibold text-purple-400 mb-1">Source Code Snippet (Illustrative)</h4>
                        <pre className="bg-gray-900 p-3 rounded-md overflow-x-auto text-sm text-green-400 max-h-48">
                          <code>{selectedFunction.source_code}</code>
                        </pre>
                      </div>
                    )}
                    
                    {selectedFunction.last_execution && (
                      <div className="mt-3">
                        <h4 className="text-md font-semibold text-purple-400 mb-1">Last Execution Details</h4>
                        <div className="bg-gray-700/50 p-3 rounded-md space-y-2">
                          <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-400">
                              Time: {formatTime(selectedFunction.last_execution.timestamp)}
                            </span>
                            {getStatusBadge(selectedFunction.last_execution.status)}
                          </div>
                          
                          <div>
                            <h5 className="font-medium text-xs text-gray-400 mb-1">Inputs:</h5>
                            <pre className="bg-gray-900 p-2 rounded-md text-xs text-gray-300 max-h-32 overflow-y-auto">
                              {JSON.stringify(selectedFunction.last_execution.inputs, null, 2)}
                            </pre>
                          </div>
                          
                          <div>
                            <h5 className="font-medium text-xs text-gray-400 mb-1">Result:</h5>
                            <pre className="bg-gray-900 p-2 rounded-md text-xs text-gray-300 max-h-32 overflow-y-auto">
                              {JSON.stringify(selectedFunction.last_execution.result, null, 2)}
                            </pre>
                          </div>
                        </div>
                      </div>
                    )}
                    {!selectedFunction.last_execution && (
                        <p className="text-sm text-gray-400">No execution recorded for this function yet.</p>
                    )}
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-64 text-gray-500">
                    Select a function from the list to view its detailed information.
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        
        <TabsContent value="executions" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Function Execution Log</CardTitle>
              <CardDescription>
                Real-time visualization of MCP function executions
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="p-4 text-center">Loading execution history...</div>
              ) : functionCalls.length > 0 ? (
                <div className="h-[600px] overflow-y-auto">
                  <div className="space-y-3">
                    {functionCalls.map((execution, index) => (
                      <div key={index} className="border rounded-md p-3">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className="font-medium">{execution.function_name}</h3>
                            <p className="text-sm text-gray-600">
                              {formatTime(execution.timestamp)}
                            </p>
                          </div>
                          {getStatusBadge(execution.status)}
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
                          <div>
                            <h4 className="text-sm font-medium mb-1">Inputs:</h4>
                            <pre className="bg-gray-50 p-2 rounded-md text-xs overflow-x-auto">
                              {JSON.stringify(execution.inputs, null, 2)}
                            </pre>
                          </div>
                          
                          <div>
                            <h4 className="text-sm font-medium mb-1">Result:</h4>
                            <pre className="bg-gray-50 p-2 rounded-md text-xs overflow-x-auto">
                              {JSON.stringify(execution.result, null, 2)}
                            </pre>
                          </div>
                        </div>
                        
                        {execution.execution_time && (
                          <div className="mt-2 text-xs text-right text-gray-500">
                            Execution time: {execution.execution_time}ms
                          </div>
                        )}
                      </div>
                    ))}
                    <div ref={messagesEndRef} />
                  </div>
                </div>
              ) : (
                <div className="p-4 text-center text-gray-500">
                  No function executions yet
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MCPFunctionVisualizer;