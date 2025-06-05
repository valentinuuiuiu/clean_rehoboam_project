import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';

/**
 * Simple test component to verify interaction functionality
 */
const TestInteract = () => {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const testInteract = async () => {
    console.log('Test interact button clicked with message:', message);
    
    if (!message.trim()) {
      alert('Please enter a message');
      return;
    }

    setLoading(true);
    
    try {
      console.log('Making test API call...');
      const response = await fetch('/api/companions/Akenaton/interact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      console.log('Test API response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Test API response data:', data);
        setResponse(data.response || 'No response received');
      } else {
        setResponse(`Error: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Test API error:', error);
      setResponse(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 bg-gray-800 rounded-lg max-w-md">
      <h3 className="text-white mb-4">Test Interaction</h3>
      <div className="space-y-4">
        <Input
          value={message}
          onChange={(e) => {
            console.log('Test input changed:', e.target.value);
            setMessage(e.target.value);
          }}
          placeholder="Enter test message..."
          className="w-full"
        />
        <Button 
          onClick={testInteract}
          disabled={loading}
          className="w-full"
        >
          {loading ? 'Testing...' : 'Test Interact'}
        </Button>
        {response && (
          <div className="mt-4 p-3 bg-gray-700 rounded text-white text-sm">
            <strong>Response:</strong> {response}
          </div>
        )}
      </div>
    </div>
  );
};

export default TestInteract;
