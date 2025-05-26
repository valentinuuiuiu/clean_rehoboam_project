import React, { useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

/**
 * Component for testing and debugging WebSocket connections
 */
const WebSocketTest = () => {
  const [messages, setMessages] = useState([]);
  const [manualMessage, setManualMessage] = useState('');
  const [selectedEndpoint, setSelectedEndpoint] = useState('/ws/trading');

  // Available WebSocket endpoints
  const endpoints = [
    { path: '/ws/trading', name: 'Trading Data' },
    { path: '/ws/emotions', name: 'Market Emotions' },
    { path: '/ws/networks', name: 'Network Stats' },
    { path: '/ws/preferences', name: 'User Preferences' }
  ];

  // Connect to the selected WebSocket endpoint
  const { 
    isConnected, 
    error, 
    send, 
    subscribe, 
    reconnect 
  } = useWebSocket(selectedEndpoint, {
    onMessage: (message) => {
      setMessages(prev => [...prev, { 
        type: 'received', 
        content: message, 
        time: new Date().toISOString() 
      }].slice(-10)); // Keep only last 10 messages
    },
    onConnected: () => {
      console.log('Connected to', selectedEndpoint);
      // Add connection message
      setMessages(prev => [...prev, { 
        type: 'system', 
        content: `Connected to ${selectedEndpoint}`, 
        time: new Date().toISOString() 
      }].slice(-10));
    },
    onDisconnected: () => {
      console.log('Disconnected from', selectedEndpoint);
      // Add disconnection message
      setMessages(prev => [...prev, { 
        type: 'system', 
        content: `Disconnected from ${selectedEndpoint}`, 
        time: new Date().toISOString() 
      }].slice(-10));
    }
  });

  // Change WebSocket endpoint
  const changeEndpoint = (endpoint) => {
    setSelectedEndpoint(endpoint);
    setMessages([]);
  };

  // Send a manual message
  const sendManualMessage = () => {
    if (!manualMessage) return;
    
    try {
      const parsed = JSON.parse(manualMessage);
      send(parsed);
      
      // Add sent message to the log
      setMessages(prev => [...prev, { 
        type: 'sent', 
        content: parsed, 
        time: new Date().toISOString() 
      }].slice(-10));
      
      setManualMessage('');
    } catch (e) {
      alert('Invalid JSON: ' + e.message);
    }
  };

  // Send predefined test messages
  const sendTestMessage = (type) => {
    let message;
    
    switch (type) {
      case 'ping':
        message = { type: 'ping', data: { timestamp: new Date().toISOString() } };
        break;
      case 'getPrices':
        message = { type: 'getPrices', data: { pairs: ['BTCUSDT', 'ETHUSDT', 'SHIBUSDT', 'AAVEUSDT'] } };
        break;
      case 'getNetworks':
        message = { type: 'getNetworks', data: {} };
        break;
      case 'getGasPrices':
        message = { type: 'getGasPrices', data: {} };
        break;
      case 'getArbitrageOpportunities':
        message = { type: 'getArbitrageOpportunities', data: {} };
        break;
      default:
        return;
    }
    
    send(message);
    
    // Add sent message to the log
    setMessages(prev => [...prev, { 
      type: 'sent', 
      content: message, 
      time: new Date().toISOString() 
    }].slice(-10));
  };

  // Subscribe to topics
  const handleSubscribe = () => {
    subscribe({
      topics: ['prices', 'gasPrices', 'arbitrage'],
      networks: ['ethereum', 'arbitrum', 'optimism']
    });
    
    // Add subscription message to the log
    setMessages(prev => [...prev, { 
      type: 'system', 
      content: 'Subscribed to topics: prices, gasPrices, arbitrage', 
      time: new Date().toISOString() 
    }].slice(-10));
  };

  return (
    <div className="bg-gray-900 p-6 rounded-xl shadow-xl border border-gray-700">
      <h2 className="text-2xl font-bold text-white mb-4">WebSocket Debugger</h2>
      
      {/* Connection status */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-4">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className={`font-medium ${isConnected ? 'text-green-500' : 'text-red-500'}`}>
            {isConnected ? 'Connected' : 'Disconnected'} 
          </span>
          <span className="text-gray-400">to {selectedEndpoint}</span>
        </div>
        
        {error && (
          <div className="bg-red-900/30 border border-red-600 p-3 rounded-lg text-red-400 mb-4">
            {error.toString()}
          </div>
        )}
        
        <div className="flex flex-wrap gap-2 mb-4">
          {endpoints.map(endpoint => (
            <button
              key={endpoint.path}
              onClick={() => changeEndpoint(endpoint.path)}
              className={`px-3 py-1 rounded-md text-sm ${
                selectedEndpoint === endpoint.path
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {endpoint.name}
            </button>
          ))}
          
          <button
            onClick={reconnect}
            className="px-3 py-1 rounded-md text-sm bg-yellow-600 text-white hover:bg-yellow-500 ml-auto"
          >
            Reconnect
          </button>
        </div>
      </div>
      
      {/* Quick actions */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-white mb-2">Quick Actions</h3>
        <div className="flex flex-wrap gap-2 mb-4">
          <button
            onClick={() => sendTestMessage('ping')}
            className="px-3 py-1 rounded-md text-sm bg-indigo-600 text-white hover:bg-indigo-500"
          >
            Send Ping
          </button>
          <button
            onClick={() => sendTestMessage('getPrices')}
            className="px-3 py-1 rounded-md text-sm bg-indigo-600 text-white hover:bg-indigo-500"
          >
            Get Prices
          </button>
          <button
            onClick={() => sendTestMessage('getNetworks')}
            className="px-3 py-1 rounded-md text-sm bg-indigo-600 text-white hover:bg-indigo-500"
          >
            Get Networks
          </button>
          <button
            onClick={() => sendTestMessage('getGasPrices')}
            className="px-3 py-1 rounded-md text-sm bg-indigo-600 text-white hover:bg-indigo-500"
          >
            Get Gas Prices
          </button>
          <button
            onClick={() => sendTestMessage('getArbitrageOpportunities')}
            className="px-3 py-1 rounded-md text-sm bg-indigo-600 text-white hover:bg-indigo-500"
          >
            Get Arbitrage
          </button>
          <button
            onClick={handleSubscribe}
            className="px-3 py-1 rounded-md text-sm bg-green-600 text-white hover:bg-green-500"
          >
            Subscribe
          </button>
        </div>
      </div>
      
      {/* Custom message */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-white mb-2">Send Custom Message</h3>
        <div className="flex gap-2">
          <textarea
            value={manualMessage}
            onChange={(e) => setManualMessage(e.target.value)}
            placeholder='{"type": "ping", "data": {}}'
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg p-2 text-white resize-none"
            rows={3}
          />
          <button
            onClick={sendManualMessage}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg h-fit self-end"
          >
            Send
          </button>
        </div>
      </div>
      
      {/* Message log */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-2">Message Log</h3>
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 h-80 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="text-gray-500 text-center py-4">No messages yet</div>
          ) : (
            <div className="flex flex-col gap-3">
              {messages.map((msg, index) => (
                <div key={index} className="border-b border-gray-700 pb-2 last:border-none">
                  <div className="flex justify-between items-center mb-1">
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                      msg.type === 'received' ? 'bg-green-900/50 text-green-400' :
                      msg.type === 'sent' ? 'bg-blue-900/50 text-blue-400' :
                      'bg-gray-700 text-gray-300'
                    }`}>
                      {msg.type.toUpperCase()}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(msg.time).toLocaleTimeString()}
                    </span>
                  </div>
                  <pre className="bg-gray-900 p-2 rounded text-xs text-gray-300 overflow-x-auto">
                    {JSON.stringify(msg.content, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default WebSocketTest;