import { WebSocket, WebSocketServer } from 'ws';
import { createServer } from 'http';
import { Server } from 'http';

interface WebSocketMessage {
  type: string;
  data: any;
}

interface ClientSubscription {
  client: WebSocket;
  topics: Set<string>;
  networks: Set<string>;
}

class TradingWebSocketServer {
  private wss: WebSocketServer;
  private clients: Map<WebSocket, ClientSubscription> = new Map();
  private priceUpdateInterval: NodeJS.Timeout | null = null;
  private gasPriceUpdateInterval: NodeJS.Timeout | null = null;
  private arbitrageUpdateInterval: NodeJS.Timeout | null = null;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;

  constructor(server: Server) {
    this.wss = new WebSocketServer({ 
      server,
      path: '/ws/trading',
      clientTracking: true,
      // Remove complex compression settings that might cause issues
      perMessageDeflate: false
    });

    this.setupWebSocketServer();
    console.log('WebSocket server initialized with enhanced Layer 2 support');
  }

  private setupWebSocketServer() {
    this.wss.on('connection', (ws: WebSocket) => {
      console.log('New client attempting to connect...');

      // Add client with default subscriptions
      this.clients.set(ws, {
        client: ws,
        topics: new Set(['prices']), // Default subscription
        networks: new Set(['ethereum']) // Default network
      });
      
      console.log(`Client connected. Total clients: ${this.clients.size}`);

      ws.on('message', (message) => this.handleMessage(ws, message));

      ws.on('close', () => {
        this.clients.delete(ws);
        console.log(`Client disconnected. Remaining clients: ${this.clients.size}`);
      });

      ws.on('error', (error) => {
        console.error('WebSocket error:', error);
        this.clients.delete(ws);
      });

      // Send initial connection confirmation
      try {
        this.sendToClient(ws, {
          type: 'connection',
          data: { 
            status: 'connected',
            timestamp: new Date().toISOString(),
            supportedTopics: ['prices', 'gasPrices', 'arbitrage', 'networks'],
            supportedNetworks: ['ethereum', 'arbitrum', 'optimism', 'polygon', 'base', 'zksync']
          }
        });
      } catch (error) {
        console.error('Failed to send initial connection message:', error);
      }
    });

    this.wss.on('error', (error) => {
      console.error('WebSocket server error:', error);
    });
  }

  private handleMessage(client: WebSocket, message: string) {
    try {
      const parsedMessage: WebSocketMessage = JSON.parse(message.toString());
      console.log('Received message:', parsedMessage.type);
      
      const subscription = this.clients.get(client);
      if (!subscription) {
        console.warn('Message received from unregistered client');
        return;
      }

      switch (parsedMessage.type) {
        case 'subscribe':
          // Handle topic subscription
          if (parsedMessage.data.topics && Array.isArray(parsedMessage.data.topics)) {
            parsedMessage.data.topics.forEach((topic: string) => {
              subscription.topics.add(topic);
            });
          }
          
          // Handle network subscription
          if (parsedMessage.data.networks && Array.isArray(parsedMessage.data.networks)) {
            parsedMessage.data.networks.forEach((network: string) => {
              subscription.networks.add(network);
            });
          }
          
          console.log('Client subscribed to:', {
            topics: Array.from(subscription.topics),
            networks: Array.from(subscription.networks)
          });
          
          this.sendToClient(client, {
            type: 'subscribed',
            data: {
              topics: Array.from(subscription.topics),
              networks: Array.from(subscription.networks)
            }
          });
          break;

        case 'unsubscribe':
          // Handle topic unsubscription
          if (parsedMessage.data.topics && Array.isArray(parsedMessage.data.topics)) {
            parsedMessage.data.topics.forEach((topic: string) => {
              subscription.topics.delete(topic);
            });
          }
          
          // Handle network unsubscription
          if (parsedMessage.data.networks && Array.isArray(parsedMessage.data.networks)) {
            parsedMessage.data.networks.forEach((network: string) => {
              subscription.networks.delete(network);
            });
          }
          
          console.log('Client unsubscribed from:', parsedMessage.data);
          break;

        case 'ping':
          this.sendToClient(client, {
            type: 'pong',
            data: { timestamp: new Date().toISOString() }
          });
          break;
          
        case 'getNetworks':
          this.sendToClient(client, {
            type: 'networks',
            data: {
              networks: [
                { id: 'ethereum', name: 'Ethereum', layer: 1 },
                { id: 'arbitrum', name: 'Arbitrum', layer: 2, type: 'optimistic' },
                { id: 'optimism', name: 'Optimism', layer: 2, type: 'optimistic' },
                { id: 'polygon', name: 'Polygon', layer: 2, type: 'plasma' },
                { id: 'base', name: 'Base', layer: 2, type: 'optimistic' },
                { id: 'zksync', name: 'zkSync Era', layer: 2, type: 'zk' }
              ],
              timestamp: new Date().toISOString()
            }
          });
          break;
          
        case 'getGasPrices':
          // This would be replaced with actual API calls in production
          this.sendToClient(client, {
            type: 'gasPrices',
            data: {
              gasPrices: [
                { network: 'ethereum', maxFeeGwei: 20, usdCost: 2.5 },
                { network: 'arbitrum', maxFeeGwei: 0.25, usdCost: 0.1 },
                { network: 'optimism', maxFeeGwei: 0.1, usdCost: 0.05 },
                { network: 'polygon', maxFeeGwei: 100, usdCost: 0.2 },
                { network: 'base', maxFeeGwei: 0.1, usdCost: 0.03 },
                { network: 'zksync', maxFeeGwei: 0.3, usdCost: 0.15 }
              ],
              timestamp: new Date().toISOString()
            }
          });
          break;
          
        case 'getArbitrageOpportunities':
          // This would be replaced with actual API calls in production
          this.sendToClient(client, {
            type: 'arbitrageOpportunities',
            data: {
              opportunities: [
                { 
                  token: 'ETH',
                  buyNetwork: 'arbitrum',
                  sellNetwork: 'optimism',
                  profit: 0.2,
                  confidence: 0.8
                },
                { 
                  token: 'USDC',
                  buyNetwork: 'polygon',
                  sellNetwork: 'base',
                  profit: 0.1,
                  confidence: 0.9
                }
              ],
              timestamp: new Date().toISOString()
            }
          });
          break;

        default:
          console.warn('Unknown message type:', parsedMessage.type);
      }
    } catch (error) {
      console.error('Error handling websocket message:', error);
    }
  }

  private sendToClient(client: WebSocket, message: WebSocketMessage) {
    if (!client) {
      console.warn('Attempted to send message to null client');
      return;
    }

    try {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify(message));
      } else {
        console.warn('Client connection not ready:', client.readyState);
      }
    } catch (error) {
      console.error('Error sending message to client:', error);
      this.clients.delete(client);
    }
  }

  public broadcast(message: WebSocketMessage, topicFilter?: string, networkFilter?: string) {
    console.log(`Broadcasting message type: ${message.type} (topic=${topicFilter}, network=${networkFilter})`);
    
    this.clients.forEach((subscription, client) => {
      // Apply topic filter if specified
      if (topicFilter && !subscription.topics.has(topicFilter)) {
        return;
      }
      
      // Apply network filter if specified
      if (networkFilter && !subscription.networks.has(networkFilter)) {
        return;
      }
      
      this.sendToClient(client, message);
    });
  }
  
  public broadcastToNetwork(network: string, message: WebSocketMessage) {
    this.broadcast(message, undefined, network);
  }
  
  public broadcastToTopic(topic: string, message: WebSocketMessage) {
    this.broadcast(message, topic);
  }

  public startPriceUpdates(getLatestPrices: () => Promise<Record<string, number>>) {
    if (this.priceUpdateInterval) {
      clearInterval(this.priceUpdateInterval);
    }

    console.log('Starting price updates...');
    this.priceUpdateInterval = setInterval(async () => {
      try {
        if (this.clients.size === 0) {
          return; // Skip if no clients connected
        }

        const prices = await getLatestPrices();
        this.broadcastToTopic('prices', {
          type: 'prices',
          data: {
            prices,
            timestamp: new Date().toISOString()
          }
        });
      } catch (error) {
        console.error('Error broadcasting prices:', error);
      }
    }, 1000); // Update every second
  }
  
  public startGasPriceUpdates(getGasPrices: () => Promise<any[]>) {
    if (this.gasPriceUpdateInterval) {
      clearInterval(this.gasPriceUpdateInterval);
    }

    console.log('Starting gas price updates...');
    this.gasPriceUpdateInterval = setInterval(async () => {
      try {
        if (this.clients.size === 0) {
          return; // Skip if no clients connected
        }

        const gasPrices = await getGasPrices();
        this.broadcastToTopic('gasPrices', {
          type: 'gasPrices',
          data: {
            gasPrices,
            timestamp: new Date().toISOString()
          }
        });
      } catch (error) {
        console.error('Error broadcasting gas prices:', error);
      }
    }, 10000); // Update every 10 seconds
  }
  
  public startArbitrageUpdates(getArbitrageOpportunities: () => Promise<any[]>) {
    if (this.arbitrageUpdateInterval) {
      clearInterval(this.arbitrageUpdateInterval);
    }

    console.log('Starting arbitrage updates...');
    this.arbitrageUpdateInterval = setInterval(async () => {
      try {
        if (this.clients.size === 0) {
          return; // Skip if no clients connected
        }

        const opportunities = await getArbitrageOpportunities();
        this.broadcastToTopic('arbitrage', {
          type: 'arbitrageOpportunities',
          data: {
            opportunities,
            timestamp: new Date().toISOString()
          }
        });
      } catch (error) {
        console.error('Error broadcasting arbitrage opportunities:', error);
      }
    }, 30000); // Update every 30 seconds
  }

  public stopPriceUpdates() {
    if (this.priceUpdateInterval) {
      clearInterval(this.priceUpdateInterval);
      this.priceUpdateInterval = null;
      console.log('Price updates stopped');
    }
  }
  
  public stopGasPriceUpdates() {
    if (this.gasPriceUpdateInterval) {
      clearInterval(this.gasPriceUpdateInterval);
      this.gasPriceUpdateInterval = null;
      console.log('Gas price updates stopped');
    }
  }
  
  public stopArbitrageUpdates() {
    if (this.arbitrageUpdateInterval) {
      clearInterval(this.arbitrageUpdateInterval);
      this.arbitrageUpdateInterval = null;
      console.log('Arbitrage updates stopped');
    }
  }
  
  public stopAllUpdates() {
    this.stopPriceUpdates();
    this.stopGasPriceUpdates();
    this.stopArbitrageUpdates();
  }
}

export default TradingWebSocketServer;
