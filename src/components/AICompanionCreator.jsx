import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { Progress } from './ui/progress';
import { useToast } from '../hooks/useToast';
import { useWebSocket } from '../hooks/useWebSocket';

/**
 * AI Companion Creator Component
 * 
 * This component provides functionality to:
 * 1. Create new AI companions with customized traits
 * 2. Interact with companions through natural conversation
 * 3. View and manage companion evolution over time
 * 
 * The component uses WebSockets for real-time updates and
 * MCP integration for intelligent character generation.
 */
const AICompanionCreator = () => {
  // State for companion list and selection
  const [companions, setCompanions] = useState([]);
  const [selectedCompanion, setSelectedCompanion] = useState(null);
  
  // State for companion creation form
  const [companionForm, setCompanionForm] = useState({
    name: '',
    themes: '',
    archetypes: '',
    complexity: 0.7,
  });
  
  // State for conversation
  const [conversationHistory, setConversationHistory] = useState([]);
  const [userInput, setUserInput] = useState('');
  
  // UI state
  const [activeTab, setActiveTab] = useState('interact');
  const [isLoading, setIsLoading] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  
  // Refs
  const messagesEndRef = useRef(null);
  
  // Toast for notifications
  const { toast } = useToast();
  
  // WebSocket connection configuration
  const wsApiPath = '/api/companions/ws';
  const wsOptions = {
    reconnectInterval: 3000,           // 3 seconds between reconnect attempts
    maxReconnectAttempts: 10,          // Try more times before giving up
    onOpen: () => console.log('WebSocket connected successfully'),
    onClose: () => console.log('WebSocket connection closed'),
    onError: (error) => console.error('WebSocket error:', error),
    onMessage: (data) => console.log('WebSocket message received:', data)
  };
  
  // Use websocket hook with improved options
  console.log('Using WebSocket path with enhanced options:', wsApiPath);
  const { isConnected, lastMessage, send, reconnect } = useWebSocket(wsApiPath, wsOptions);
  
  // Fetch conversation history for a companion
  const fetchConversationHistory = useCallback(async (companionName) => {
    try {
      const response = await fetch(`/api/companions/${companionName}/conversation`);
      if (!response.ok) {
        throw new Error(`Error fetching conversation: ${response.statusText}`);
      }
      
      const data = await response.json();
      setConversationHistory(data);
      
    } catch (error) {
      console.error("Error fetching conversation:", error);
      toast({
        title: "Could not load conversation",
        description: error.message,
        variant: "destructive",
      });
    }
  }, [toast]);
  
  // Fetch the list of available companions
  const fetchCompanions = useCallback(async () => {
    setIsLoading(true);
    
    try {
      // Make sure to use the exact endpoint path with no trailing slash
      const response = await fetch('/api/companions', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        }
      });
      
      console.log("Fetching companions response:", response.status, response.statusText);
      
      if (!response.ok) {
        throw new Error(`Error fetching companions: ${response.statusText}`);
      }
      
      const data = await response.json();
      setCompanions(data);
      
      // If we have companions but none selected, select the first one
      if (data.length > 0 && !selectedCompanion) {
        setSelectedCompanion(data[0]);
        fetchConversationHistory(data[0].name);
      }
      
    } catch (error) {
      console.error("Error fetching companions:", error);
      toast({
        title: "Could not load companions",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }, [selectedCompanion, toast, fetchConversationHistory]);
  
  // Handle form input change
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setCompanionForm(prev => ({
      ...prev,
      [name]: value,
    }));
  };
  
  // Create a new companion
  const createCompanion = async (e) => {
    e.preventDefault();
    setIsCreating(true);
    
    try {
      // Format themes and archetypes as arrays
      const payload = {
        ...companionForm,
        themes: companionForm.themes.split(',').map(theme => theme.trim()),
        archetypes: companionForm.archetypes.split(',').map(archetype => archetype.trim()),
      };
      
      const response = await fetch('/api/companions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
      
      if (!response.ok) {
        throw new Error(`Error creating companion: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Reset form
      setCompanionForm({
        name: '',
        themes: '',
        archetypes: '',
        complexity: 0.7,
      });
      
      // Switch to interact tab and select the new companion
      setActiveTab('interact');
      await fetchCompanions();
      
      // Find the newly created companion in the updated list
      const newCompanion = companions.find(c => c.name === data.name);
      if (newCompanion) {
        setSelectedCompanion(newCompanion);
        fetchConversationHistory(newCompanion.name);
      }
      
      toast({
        title: "Companion created",
        description: `${data.name} is ready for interaction!`,
      });
      
    } catch (error) {
      console.error("Error creating companion:", error);
      toast({
        title: "Could not create companion",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setIsCreating(false);
    }
  };
  
  // Send message to the companion
  const sendUserMessage = async () => {
    if (!userInput.trim() || !selectedCompanion) return;
    
    // Add user message to conversation immediately for UI responsiveness
    const newMessage = { role: 'user', content: userInput };
    setConversationHistory(prev => [...prev, newMessage]);
    
    // Clear input field
    setUserInput('');
    
    try {
      const response = await fetch(`/api/companions/${selectedCompanion.name}/interact`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userInput }),
      });
      
      if (!response.ok) {
        throw new Error(`Error sending message: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Add companion's response to conversation
      setConversationHistory(prev => [...prev, { role: 'companion', content: data.response }]);
      
    } catch (error) {
      console.error("Error sending message:", error);
      toast({
        title: "Message failed",
        description: error.message,
        variant: "destructive",
      });
    }
  };
  
  // Handle companion selection
  const handleSelectCompanion = (companion) => {
    setSelectedCompanion(companion);
    fetchConversationHistory(companion.name);
  };
  
  // Scroll to bottom of conversation when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversationHistory]);
  
  // Fetch companions on component mount
  useEffect(() => {
    fetchCompanions();
    
    // Set up interval to periodically fetch companions (every 30 seconds)
    const intervalId = setInterval(fetchCompanions, 30000);
    
    // Clean up on unmount
    return () => clearInterval(intervalId);
  }, [fetchCompanions]);
  
  // Process websocket messages
  useEffect(() => {
    if (lastMessage) {
      // Check for companion update messages
      if (lastMessage.type === 'companion_update') {
        fetchCompanions();
        toast({
          title: "Companion updated",
          description: lastMessage.message,
        });
      }
      
      // Check for conversation update messages
      if (lastMessage.type === 'conversation_update' && 
          selectedCompanion && 
          lastMessage.companionName === selectedCompanion.name) {
        fetchConversationHistory(selectedCompanion.name);
      }
    }
  }, [lastMessage, selectedCompanion, fetchCompanions, fetchConversationHistory, toast]);
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">AI Companion Creator</h1>
      
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="create">Create</TabsTrigger>
          <TabsTrigger value="interact">Interact</TabsTrigger>
        </TabsList>
        
        <TabsContent value="create" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Create a New AI Companion</CardTitle>
              <CardDescription>
                Design an AI character with unique personality traits, knowledge domains, and interaction patterns.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={createCompanion} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input 
                    id="name" 
                    name="name" 
                    value={companionForm.name} 
                    onChange={handleFormChange} 
                    placeholder="Enter a name for your companion"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="themes">Knowledge Domains</Label>
                  <Input 
                    id="themes" 
                    name="themes" 
                    value={companionForm.themes} 
                    onChange={handleFormChange} 
                    placeholder="Enter comma-separated knowledge domains (e.g., finance, history, art)"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="archetypes">Personality Archetypes</Label>
                  <Input 
                    id="archetypes" 
                    name="archetypes" 
                    value={companionForm.archetypes} 
                    onChange={handleFormChange} 
                    placeholder="Enter comma-separated archetypes (e.g., mentor, explorer, sage)"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="complexity">Personality Complexity: {companionForm.complexity.toFixed(1)}</Label>
                  <input 
                    id="complexity" 
                    name="complexity" 
                    type="range" 
                    min="0.1" 
                    max="1.0" 
                    step="0.1" 
                    value={companionForm.complexity} 
                    onChange={handleFormChange} 
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>Simple</span>
                    <span>Complex</span>
                  </div>
                </div>
                
                <Button type="submit" disabled={isCreating} className="w-full">
                  {isCreating ? 'Creating...' : 'Create Companion'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="interact" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="md:col-span-1">
              <CardHeader>
                <CardTitle>Your Companions</CardTitle>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="flex justify-center p-4">
                    <Progress value={80} className="w-full" />
                  </div>
                ) : companions.length > 0 ? (
                  <ul className="space-y-2">
                    {companions.map(companion => (
                      <li 
                        key={companion.name} 
                        className={`p-2 rounded cursor-pointer hover:bg-gray-100 ${selectedCompanion?.name === companion.name ? 'bg-gray-100' : ''}`}
                        onClick={() => handleSelectCompanion(companion)}
                      >
                        <h3 className="font-medium">{companion.name}</h3>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {companion.traits.slice(0, 3).map(trait => (
                            <Badge key={trait} variant="outline" className="text-xs">
                              {trait}
                            </Badge>
                          ))}
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="text-center p-4">
                    <p className="text-gray-500">No companions yet</p>
                    <Button 
                      variant="link" 
                      onClick={() => setActiveTab('create')}
                      className="mt-2"
                    >
                      Create your first companion
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
            
            <Card className="md:col-span-3">
              <CardHeader>
                <CardTitle>
                  {selectedCompanion ? `Conversation with ${selectedCompanion.name}` : 'Select a companion'}
                </CardTitle>
                {selectedCompanion && (
                  <CardDescription>
                    {selectedCompanion.description}
                  </CardDescription>
                )}
              </CardHeader>
              <CardContent>
                {selectedCompanion ? (
                  <>
                    <div className="bg-gray-50 rounded p-4 h-96 overflow-y-auto mb-4">
                      {conversationHistory.length > 0 ? (
                        <div className="space-y-4">
                          {conversationHistory.map((message, index) => (
                            <div 
                              key={index} 
                              className={`p-3 rounded-lg max-w-[80%] ${
                                message.role === 'user' 
                                  ? 'bg-blue-100 ml-auto' 
                                  : 'bg-gray-200'
                              }`}
                            >
                              <p>{message.content}</p>
                            </div>
                          ))}
                          <div ref={messagesEndRef} />
                        </div>
                      ) : (
                        <div className="h-full flex items-center justify-center">
                          <p className="text-gray-500">Start a conversation with {selectedCompanion.name}</p>
                        </div>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <Input 
                        value={userInput} 
                        onChange={(e) => setUserInput(e.target.value)}
                        placeholder="Type your message..."
                        onKeyPress={(e) => e.key === 'Enter' && sendUserMessage()}
                      />
                      <Button onClick={sendUserMessage}>Send</Button>
                    </div>
                  </>
                ) : (
                  <div className="h-80 flex items-center justify-center">
                    <p className="text-gray-500">Select a companion from the list to start chatting</p>
                  </div>
                )}
              </CardContent>
              {selectedCompanion && (
                <CardFooter className="flex justify-between">
                  <div className="text-sm text-gray-500">
                    <span>Connection status: </span>
                    <span className={isConnected ? 'text-green-500' : 'text-red-500'}>
                      {isConnected ? 'Connected' : 'Disconnected'}
                    </span>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => fetchConversationHistory(selectedCompanion.name)}
                  >
                    Refresh
                  </Button>
                </CardFooter>
              )}
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AICompanionCreator;