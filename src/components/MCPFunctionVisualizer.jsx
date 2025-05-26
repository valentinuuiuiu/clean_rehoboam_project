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
      // Add new function to the list
      setMcpFunctions(prev => [...prev, data.function]);
    } 
    else if (data.type === 'mcp_function_executed') {
      // Add new function call to the list
      setFunctionCalls(prev => [data.execution, ...prev].slice(0, 100)); // Keep last 100 calls
    }
    else if (data.type === 'mcp_functions_list') {
      // Set the full list of functions
      setMcpFunctions(data.functions);
      setIsLoading(false);
    }
    else if (data.type === 'mcp_function_calls_list') {
      // Set the list of recent function calls
      setFunctionCalls(data.calls);
      setIsLoading(false);
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
      return <em className="text-gray-500">No parameters</em>;
    }
    
    return (
      <ul className="space-y-1">
        {Object.entries(parameters).map(([name, desc]) => (
          <li key={name} className="text-sm">
            <span className="font-mono bg-gray-100 p-1 rounded">{name}</span>
            {' - '}
            <span className="text-gray-700">{desc}</span>
          </li>
        ))}
      </ul>
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
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">MCP Function Visualizer</h1>
      
      <div className="flex items-center justify-between mb-4">
        <div>
          <Badge className={isConnected ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
            {isConnected ? "Connected" : "Disconnected"}
          </Badge>
          <span className="ml-2 text-sm text-gray-500">
            {isConnected ? "Receiving real-time updates" : "Reconnecting..."}
          </span>
        </div>
      </div>
      
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="functions">Registered Functions</TabsTrigger>
          <TabsTrigger value="executions">Function Executions</TabsTrigger>
        </TabsList>
        
        <TabsContent value="functions" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="md:col-span-1">
              <CardHeader>
                <CardTitle>MCP Functions</CardTitle>
                <CardDescription>
                  Dynamic functions created by the system
                </CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="p-4 text-center">Loading functions...</div>
                ) : mcpFunctions.length > 0 ? (
                  <ul className="max-h-[600px] overflow-y-auto space-y-2">
                    {mcpFunctions.map(func => (
                      <li 
                        key={func.name} 
                        className={`p-3 border rounded cursor-pointer hover:bg-gray-50 ${
                          selectedFunction?.name === func.name ? 'bg-gray-100 border-blue-300' : ''
                        }`}
                        onClick={() => handleFunctionSelect(func)}
                      >
                        <h3 className="font-medium">{func.name}</h3>
                        <div className="mt-1 text-sm text-gray-600 truncate">
                          {func.description || "No description"}
                        </div>
                        <div className="mt-2">
                          <Badge className="bg-purple-100 text-purple-800">
                            {func.mcp_type || "processor"}
                          </Badge>
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="p-4 text-center text-gray-500">
                    No MCP functions registered yet
                  </div>
                )}
              </CardContent>
            </Card>
            
            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>
                  {selectedFunction ? selectedFunction.name : 'Function Details'}
                </CardTitle>
                {selectedFunction && (
                  <CardDescription>
                    {selectedFunction.description}
                  </CardDescription>
                )}
              </CardHeader>
              <CardContent>
                {selectedFunction ? (
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-lg font-medium mb-2">Type</h3>
                      <Badge className="bg-purple-100 text-purple-800">
                        {selectedFunction.mcp_type || "processor"}
                      </Badge>
                    </div>
                    
                    <div>
                      <h3 className="text-lg font-medium mb-2">Parameters</h3>
                      {formatParameters(selectedFunction.parameters)}
                    </div>
                    
                    {selectedFunction.source_code && (
                      <div>
                        <h3 className="text-lg font-medium mb-2">Source Code</h3>
                        <pre className="bg-gray-50 p-3 rounded-md overflow-x-auto text-sm">
                          <code>{selectedFunction.source_code}</code>
                        </pre>
                      </div>
                    )}
                    
                    {selectedFunction.last_execution && (
                      <div>
                        <h3 className="text-lg font-medium mb-2">Last Execution</h3>
                        <div className="bg-gray-50 p-3 rounded-md">
                          <div className="flex justify-between mb-2">
                            <span className="text-sm text-gray-600">
                              {formatTime(selectedFunction.last_execution.timestamp)}
                            </span>
                            {getStatusBadge(selectedFunction.last_execution.status)}
                          </div>
                          
                          <h4 className="font-medium text-sm mb-1">Inputs:</h4>
                          <pre className="bg-gray-100 p-2 rounded-md text-xs mb-2">
                            {JSON.stringify(selectedFunction.last_execution.inputs, null, 2)}
                          </pre>
                          
                          <h4 className="font-medium text-sm mb-1">Result:</h4>
                          <pre className="bg-gray-100 p-2 rounded-md text-xs">
                            {JSON.stringify(selectedFunction.last_execution.result, null, 2)}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-64 text-gray-500">
                    Select a function to see its details
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