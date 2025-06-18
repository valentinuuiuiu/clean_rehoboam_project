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

  // State for selected companion's detailed data
  const [selectedCompanionDetails, setSelectedCompanionDetails] = useState(null);
  const [companionBackstory, setCompanionBackstory] = useState(null);
  const [isFetchingDetails, setIsFetchingDetails] = useState(false);
  const [detailsError, setDetailsError] = useState(null);
  
  // UI state
  const [activeTab, setActiveTab] = useState('interact');
  const [isLoading, setIsLoading] = useState(false); // This is for the main companion list
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
      const response = await fetch('/api/companions', {
        method: 'GET',
        headers: { 'Accept': 'application/json', }
      });
      if (!response.ok) throw new Error(`Error fetching companions: ${response.statusText}`);
      const data = await response.json();
      setCompanions(data);
      if (data.length > 0 && !selectedCompanion) {
         // Auto-select first companion and fetch its details if none is selected yet
        handleSelectCompanion(data[0]);
      }
    } catch (error) {
      console.error("Error fetching companions:", error);
      const errorMessage = error.message.includes('fetch') 
        ? 'Unable to connect to AI companion service' 
        : error.message;
      toast({ title: "Could not load companions", description: errorMessage, variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  }, [toast]); // Removed selectedCompanion, handleSelectCompanion to break potential loops. handleSelectCompanion will be called once if needed.
  
  // Handle form input change
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setCompanionForm(prev => ({ ...prev, [name]: value }));
  };
  
  // Create a new companion
  const createCompanion = async (e) => {
    e.preventDefault();
    setIsCreating(true);
    try {
      const payload = {
        ...companionForm,
        themes: companionForm.themes.split(',').map(theme => theme.trim()),
        archetypes: companionForm.archetypes.split(',').map(archetype => archetype.trim()),
      };
      const response = await fetch('/api/companions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error(`Error creating companion: ${response.statusText}`);
      const data = await response.json();
      setCompanionForm({ name: '', themes: '', archetypes: '', complexity: 0.7 });
      await fetchCompanions(); // Refetch to include the new one
      // Try to select the newly created companion
      const newCompanion = data; // Assuming API returns the created companion
      if (newCompanion) {
        handleSelectCompanion(newCompanion); // This will set it and fetch its details/history
      }
      setActiveTab('interact');
      toast({ title: "Companion created", description: `${data.name} is ready for interaction!` });
    } catch (error) {
      console.error("Error creating companion:", error);
      toast({ title: "Could not create companion", description: error.message, variant: "destructive" });
    } finally {
      setIsCreating(false);
    }
  };
  
  // Send message to the companion
  const sendUserMessage = async () => {
    if (!userInput.trim() || !selectedCompanion) return;
    const originalInput = userInput;
    const newMessage = { role: 'user', content: userInput, timestamp: new Date().toISOString() };
    setConversationHistory(prev => [...prev, newMessage]);
    setUserInput('');
    try {
      const response = await fetch(`/api/companions/${selectedCompanion.name}/interact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: originalInput }),
      });
      if (!response.ok) {
        if (response.status === 404) throw new Error('AI companion service not available');
        else throw new Error(`Error sending message: ${response.statusText}`);
      }
      const data = await response.json();
      const companionMessage = { 
        role: 'companion', 
        content: data.response || data.message || 'I received your message but had trouble responding.', 
        timestamp: new Date().toISOString()
      };
      setConversationHistory(prev => [...prev, companionMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      const fallbackResponse = {
        role: 'companion',
        content: `I appreciate your message: "${originalInput}". However, I'm experiencing some technical difficulties. Please try again later.`,
        timestamp: new Date().toISOString(),
        isError: true
      };
      setConversationHistory(prev => [...prev, fallbackResponse]);
      toast({ title: "Connection issue", description: "Chat temporarily unavailable.", variant: "destructive" });
    }
  };
  
  // Handle companion selection
  const handleSelectCompanion = async (companion) => {
    console.log('Selecting companion:', companion);
    if (selectedCompanion?.name === companion.name && selectedCompanionDetails) {
        // If same companion is clicked and details are already loaded, do nothing or minimal refresh
        fetchConversationHistory(companion.name); // Still refresh conversation
        return;
    }
    setSelectedCompanion(companion);
    setConversationHistory([]);
    setSelectedCompanionDetails(null);
    setCompanionBackstory(null);
    setDetailsError(null);
    fetchConversationHistory(companion.name);
    fetchCompanionDetails(companion.name);
    fetchCompanionBackstory(companion.name);
  };

  // Fetch full details for a selected companion
  const fetchCompanionDetails = useCallback(async (companionName) => {
    if (!companionName) return;
    setIsFetchingDetails(true);
    setDetailsError(null);
    try {
      const response = await fetch(`/api/companions/${companionName}`);
      if (!response.ok) throw new Error(`Error fetching companion details: ${response.statusText}`);
      const data = await response.json();
      setSelectedCompanionDetails(data);
    } catch (error) {
      console.error("Error fetching companion details:", error);
      setDetailsError(error.message);
      // toast({ title: "Could not load companion details", description: error.message, variant: "destructive" });
    } finally {
      // Combined loading state management in fetchCompanionBackstory
    }
  }, []);

  // Fetch structured backstory for a selected companion
  const fetchCompanionBackstory = useCallback(async (companionName) => {
    if (!companionName) return;
    // setIsFetchingDetails(true); // Handled by fetchCompanionDetails if called sequentially
    try {
      const response = await fetch(`/api/companions/${companionName}/backstory`);
      if (!response.ok) throw new Error(`Error fetching companion backstory: ${response.statusText}`);
      const data = await response.json();
      setCompanionBackstory(data);
    } catch (error) {
      console.error("Error fetching companion backstory:", error);
      setDetailsError(prevError => prevError ? `${prevError}; ${error.message}` : error.message); // Append errors
      // toast({ title: "Could not load companion backstory", description: error.message, variant: "destructive" });
    } finally {
      setIsFetchingDetails(false);
    }
  }, []);
  
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [conversationHistory]);
  useEffect(() => { fetchCompanions(); const intervalId = setInterval(fetchCompanions, 300000); return () => clearInterval(intervalId); }, []);
  
  useEffect(() => {
    if (lastMessage) {
      if (lastMessage.type === 'companion_update') {
        fetchCompanions();
        toast({ title: "Companion updated", description: lastMessage.message });
      }
      if (lastMessage.type === 'conversation_update' && selectedCompanion && lastMessage.companionName === selectedCompanion.name) {
        fetchConversationHistory(selectedCompanion.name);
      }
    }
  }, [lastMessage, selectedCompanion, fetchCompanions, fetchConversationHistory, toast]);

  const placeholderText = (text) => <p className="text-sm text-gray-500 italic">{text}</p>;
  
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
              <CardDescription>Design an AI character with unique personality traits, knowledge domains, and interaction patterns.</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={createCompanion} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input id="name" name="name" value={companionForm.name} onChange={handleFormChange} placeholder="Companion's Name" required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="themes">Knowledge Domains</Label>
                  <Input id="themes" name="themes" value={companionForm.themes} onChange={handleFormChange} placeholder="e.g., finance, history, art" required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="archetypes">Personality Archetypes</Label>
                  <Input id="archetypes" name="archetypes" value={companionForm.archetypes} onChange={handleFormChange} placeholder="e.g., mentor, explorer, sage" required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="complexity">Personality Complexity: {companionForm.complexity}</Label>
                  <input id="complexity" name="complexity" type="range" min="0.1" max="1.0" step="0.1" value={companionForm.complexity} onChange={handleFormChange} className="w-full" />
                  <div className="flex justify-between text-xs text-gray-500"><span>Simple</span><span>Complex</span></div>
                </div>
                <Button type="submit" disabled={isCreating} className="w-full">{isCreating ? 'Creating...' : 'Create Companion'}</Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="interact" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="md:col-span-1">
              <CardHeader><CardTitle>Your Companions</CardTitle></CardHeader>
              <CardContent>
                {isLoading ? <Progress value={80} className="w-full" /> :
                 companions.length > 0 ? (
                  <ul className="space-y-2">
                    {companions.map(companion => (
                      <li key={companion.name}
                          className={`p-2 rounded cursor-pointer hover:bg-gray-700 ${selectedCompanion?.name === companion.name ? 'bg-gray-700 border border-blue-500' : 'border border-transparent'}`}
                          onClick={() => handleSelectCompanion(companion)}>
                        <h3 className="font-medium text-blue-400">{companion.name}</h3>
                        {companion.traits && companion.traits.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-1">
                            {companion.traits.slice(0, 3).map(trait => (
                              <Badge key={trait.name || trait} variant="outline" className="text-xs">{trait.name || trait}</Badge>
                            ))}
                          </div>
                        )}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="text-center p-4">
                    {placeholderText("No companions yet.")}
                    <Button variant="link" onClick={() => setActiveTab('create')} className="mt-2">Create your first companion</Button>
                  </div>
                )}
              </CardContent>
            </Card>
            
            <div className="md:col-span-3 space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>{selectedCompanion ? `Conversation with ${selectedCompanion.name}` : 'Select a companion'}</CardTitle>
                  {selectedCompanion && (
                    <CardDescription>{selectedCompanionDetails?.persona?.description || selectedCompanion.description || placeholderText("No description available.")}</CardDescription>
                  )}
                </CardHeader>
                <CardContent>
                  {selectedCompanion ? (
                    <>
                      <div className="bg-gray-800/50 rounded p-4 h-96 overflow-y-auto mb-4 border border-gray-700">
                        {conversationHistory.length > 0 ? (
                          <div className="space-y-4">
                            {conversationHistory.map((message, index) => (
                              <div key={index} className={`flex flex-col max-w-[80%] ${message.role === 'user' ? 'ml-auto items-end' : 'mr-auto items-start'}`}>
                                <div className={`p-3 rounded-lg ${message.role === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-gray-600 text-gray-100 rounded-bl-none'} ${message.isError ? 'bg-red-600 text-white' : ''}`}>
                                  <p className="text-sm">{message.content}</p>
                                </div>
                                {message.timestamp && (<p className={`text-xs mt-1 ${message.role === 'user' ? 'text-blue-400' : 'text-gray-400'}`}>{new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>)}
                              </div>
                            ))}
                            <div ref={messagesEndRef} />
                          </div>
                        ) : placeholderText(`Start a conversation with ${selectedCompanion.name}.`)}
                      </div>
                      <div className="mt-4 flex items-center space-x-2 p-2 bg-gray-700/50 rounded-lg border border-gray-600">
                        <Input value={userInput} onChange={(e) => setUserInput(e.target.value)} placeholder="Type your message..."
                               onKeyPress={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendUserMessage(); }}}
                               className="flex-grow bg-gray-800 border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 text-gray-100" />
                        <Button onClick={sendUserMessage} disabled={!userInput.trim()} className="bg-blue-600 hover:bg-blue-700 text-white rounded-md px-4 py-2">Send</Button>
                      </div>
                    </>
                  ) : placeholderText("Select a companion from the list to start chatting.")}
                </CardContent>
                {selectedCompanion && (
                  <CardFooter className="flex justify-between">
                    <div className="text-sm text-gray-500">Connection status: <span className={isConnected ? 'text-green-500' : 'text-red-500'}>{isConnected ? 'Connected' : 'Disconnected'}</span></div>
                    <Button variant="outline" size="sm" onClick={() => fetchConversationHistory(selectedCompanion.name)}>Refresh Chat</Button>
                  </CardFooter>
                )}
              </Card>

              {selectedCompanion && (
                <Card className="bg-gray-800/50 border-gray-700">
                  <CardHeader><CardTitle className="text-blue-400">{selectedCompanion.name}'s Profile & Backstory</CardTitle></CardHeader>
                  <CardContent>
                    {isFetchingDetails && placeholderText("Loading details...")}
                    {detailsError && <p className="text-red-400 italic">Error loading details: {detailsError}</p>}

                    {selectedCompanionDetails && !isFetchingDetails && (
                      <div className="space-y-3 mb-4 text-sm">
                        <h3 className="text-lg font-semibold text-purple-400 mb-2">Personality & Traits</h3>
                        {(selectedCompanionDetails.persona?.archetypes && selectedCompanionDetails.persona.archetypes.length > 0) ? (
                          <div><h4 className="font-medium text-gray-300">Archetypes:</h4><div className="flex flex-wrap gap-1 mt-1">{selectedCompanionDetails.persona.archetypes.map(arch => <Badge key={arch} variant="secondary" className="bg-purple-600 text-purple-100">{arch}</Badge>)}</div></div>
                        ) : placeholderText("No archetypes listed.")}

                        {(selectedCompanionDetails.persona?.personality_traits && selectedCompanionDetails.persona.personality_traits.length > 0) ? (
                           <div><h4 className="font-medium text-gray-300 mt-2">Traits:</h4><ul className="list-disc list-inside text-gray-400">{selectedCompanionDetails.persona.personality_traits.map((trait, i) => <li key={i}>{trait}</li>)}</ul></div>
                        ) : placeholderText("No traits listed.")}

                        {(selectedCompanionDetails.persona?.core_motivations && selectedCompanionDetails.persona.core_motivations.length > 0) ? (
                          <div><h4 className="font-medium text-gray-300 mt-2">Core Motivations:</h4><ul className="list-disc list-inside text-gray-400">{selectedCompanionDetails.persona.core_motivations.map((motive, i) => <li key={i}>{motive}</li>)}</ul></div>
                        ) : placeholderText("No core motivations listed.")}

                        {selectedCompanionDetails.meta_information?.custom_fields && Object.keys(selectedCompanionDetails.meta_information.custom_fields).length > 0 && (
                          <div><h4 className="font-medium text-gray-300 mt-2">Other Details:</h4>{Object.entries(selectedCompanionDetails.meta_information.custom_fields).map(([key, value]) => (<p key={key} className="text-gray-400"><strong>{key.replace(/_/g, ' ')}:</strong> {String(value)}</p>))}</div>
                        )}
                      </div>
                    )}

                    {companionBackstory && !isFetchingDetails && (
                       <div className="space-y-3 text-sm">
                        <Separator className="my-3 bg-gray-600"/>
                        <h3 className="text-lg font-semibold text-purple-400 mb-2">Backstory</h3>
                        <p className="text-gray-400 whitespace-pre-wrap">{companionBackstory.backstory || placeholderText("No backstory available.")}</p>

                        {(companionBackstory.key_moments && companionBackstory.key_moments.length > 0) ? (
                          <div><h4 className="font-medium text-gray-300 mt-2">Key Moments:</h4><ul className="list-disc list-inside text-gray-400">{companionBackstory.key_moments.map((moment, i) => <li key={i}>{moment.description} (Impact: {moment.impact})</li>)}</ul></div>
                        ) : placeholderText("No key moments recorded.")}

                        {(companionBackstory.relationships && companionBackstory.relationships.length > 0) ? (
                          <div><h4 className="font-medium text-gray-300 mt-2">Relationships:</h4><ul className="list-disc list-inside text-gray-400">{companionBackstory.relationships.map((rel, i) => <li key={i}>{rel.name}: {rel.relationship_type} ({rel.attitude})</li>)}</ul></div>
                        ) : placeholderText("No relationships listed.")}

                         {(companionBackstory.secrets && companionBackstory.secrets.length > 0) ? (
                          <div><h4 className="font-medium text-gray-300 mt-2">Secrets:</h4><ul className="list-disc list-inside text-gray-400">{companionBackstory.secrets.map((secret, i) => <li key={i}>{secret}</li>)}</ul></div>
                        ) : placeholderText("No secrets listed.")}

                        {(companionBackstory.future_goals && companionBackstory.future_goals.length > 0) ? (
                          <div><h4 className="font-medium text-gray-300 mt-2">Future Goals:</h4><ul className="list-disc list-inside text-gray-400">{companionBackstory.future_goals.map((goal, i) => <li key={i}>{goal}</li>)}</ul></div>
                        ) : placeholderText("No future goals listed.")}
                      </div>
                    )}
                    {(!selectedCompanionDetails && !companionBackstory && !isFetchingDetails && !detailsError) && placeholderText("Select a companion to see their full profile and backstory.")}
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AICompanionCreator;