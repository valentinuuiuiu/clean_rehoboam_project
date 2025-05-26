/**
 * Rehoboam MCP Registry Service
 * 
 * Central orchestration hub for all MCP servers in the Rehoboam ecosystem.
 * This service manages server discovery, health monitoring, load balancing,
 * and provides a unified API for accessing all MCP capabilities.
 * 
 * Inspired by Westworld's Rehoboam - an advanced AI system capable of
 * predicting and orchestrating complex interactions across multiple domains.
 */

require('dotenv').config();
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const { Pool } = require('pg');
const Redis = require('redis');
const winston = require('winston');
const Docker = require('dockerode');
const { v4: uuidv4 } = require('uuid');
const cron = require('cron');

// Initialize logger
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
    ),
    transports: [
        new winston.transports.File({ filename: '/app/logs/error.log', level: 'error' }),
        new winston.transports.File({ filename: '/app/logs/combined.log' }),
        new winston.transports.Console({
            format: winston.format.simple()
        })
    ]
});

// Initialize Express app
const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

// Initialize Docker client
const docker = new Docker();

// Initialize database connection
const db = new Pool({
    connectionString: process.env.POSTGRES_URL || 'postgresql://rehoboam:rehoboam123@postgres:5432/rehoboam'
});

// Initialize Redis client
const redis = Redis.createClient({
    url: process.env.REDIS_URL || 'redis://redis:6379'
});

// Connect to Redis
redis.connect().catch(err => {
    logger.error('Redis connection failed:', err);
});

// Middleware
app.use(helmet());
app.use(compression());
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Registry state
const mcpServers = new Map();
const activeSessions = new Map();
const systemMetrics = {
    totalServers: 0,
    activeServers: 0,
    totalRequests: 0,
    totalErrors: 0,
    uptime: Date.now()
};

/**
 * MCP Server Registration and Discovery
 */
class MCPServerManager {
    constructor() {
        this.servers = new Map();
        this.healthCheckInterval = 30000; // 30 seconds
        this.startHealthMonitoring();
    }

    async registerServer(serverInfo) {
        const serverId = serverInfo.name || uuidv4();
        const server = {
            id: serverId,
            name: serverInfo.name,
            url: serverInfo.url,
            capabilities: serverInfo.capabilities || [],
            status: 'active',
            lastHeartbeat: Date.now(),
            registeredAt: Date.now(),
            metadata: serverInfo.metadata || {}
        };

        this.servers.set(serverId, server);
        mcpServers.set(serverId, server);
        
        // Store in database
        try {
            await db.query(
                'INSERT INTO mcp_servers (id, name, url, capabilities, metadata, registered_at) VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT (id) DO UPDATE SET url = $3, capabilities = $4, metadata = $5, last_updated = NOW()',
                [serverId, server.name, server.url, JSON.stringify(server.capabilities), JSON.stringify(server.metadata), new Date()]
            );
        } catch (error) {
            logger.error('Database error during server registration:', error);
        }

        // Cache in Redis
        await redis.setex(`mcp_server:${serverId}`, 3600, JSON.stringify(server));

        logger.info(`MCP Server registered: ${server.name} (${serverId})`);
        
        // Broadcast to connected clients
        io.emit('server_registered', server);
        
        return serverId;
    }

    async unregisterServer(serverId) {
        const server = this.servers.get(serverId);
        if (server) {
            this.servers.delete(serverId);
            mcpServers.delete(serverId);
            
            // Remove from database
            try {
                await db.query('DELETE FROM mcp_servers WHERE id = $1', [serverId]);
            } catch (error) {
                logger.error('Database error during server unregistration:', error);
            }
            
            // Remove from Redis
            await redis.del(`mcp_server:${serverId}`);
            
            logger.info(`MCP Server unregistered: ${server.name} (${serverId})`);
            
            // Broadcast to connected clients
            io.emit('server_unregistered', { id: serverId, name: server.name });
        }
    }

    async getServer(serverId) {
        // Try memory first
        let server = this.servers.get(serverId);
        if (server) return server;
        
        // Try Redis cache
        const cached = await redis.get(`mcp_server:${serverId}`);
        if (cached) {
            server = JSON.parse(cached);
            this.servers.set(serverId, server);
            return server;
        }
        
        // Try database
        try {
            const result = await db.query('SELECT * FROM mcp_servers WHERE id = $1', [serverId]);
            if (result.rows.length > 0) {
                const row = result.rows[0];
                server = {
                    id: row.id,
                    name: row.name,
                    url: row.url,
                    capabilities: row.capabilities,
                    status: 'unknown',
                    lastHeartbeat: 0,
                    registeredAt: row.registered_at.getTime(),
                    metadata: row.metadata
                };
                this.servers.set(serverId, server);
                return server;
            }
        } catch (error) {
            logger.error('Database error during server lookup:', error);
        }
        
        return null;
    }

    getAllServers() {
        return Array.from(this.servers.values());
    }

    async healthCheck(serverId) {
        const server = this.servers.get(serverId);
        if (!server) return false;

        try {
            const response = await fetch(`${server.url}/health`, {
                method: 'GET',
                timeout: 5000
            });
            
            if (response.ok) {
                server.status = 'active';
                server.lastHeartbeat = Date.now();
                
                // Update Redis cache
                await redis.setex(`mcp_server:${serverId}`, 3600, JSON.stringify(server));
                
                return true;
            } else {
                server.status = 'unhealthy';
                return false;
            }
        } catch (error) {
            server.status = 'offline';
            logger.warn(`Health check failed for ${server.name}: ${error.message}`);
            return false;
        }
    }

    startHealthMonitoring() {
        // Health check every 30 seconds
        setInterval(async () => {
            const servers = this.getAllServers();
            for (const server of servers) {
                await this.healthCheck(server.id);
            }
            
            // Update system metrics
            systemMetrics.totalServers = servers.length;
            systemMetrics.activeServers = servers.filter(s => s.status === 'active').length;
            
            // Broadcast metrics
            io.emit('system_metrics', systemMetrics);
        }, this.healthCheckInterval);
    }
}

const serverManager = new MCPServerManager();

/**
 * API Routes
 */

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: Date.now() - systemMetrics.uptime,
        version: '1.0.0'
    });
});

// Get system information
app.get('/api/system', (req, res) => {
    res.json({
        ...systemMetrics,
        uptime: Date.now() - systemMetrics.uptime
    });
});

// Register a new MCP server
app.post('/api/servers/register', async (req, res) => {
    try {
        const serverInfo = req.body;
        const serverId = await serverManager.registerServer(serverInfo);
        systemMetrics.totalRequests++;
        
        res.json({
            success: true,
            serverId,
            message: 'Server registered successfully'
        });
    } catch (error) {
        systemMetrics.totalErrors++;
        logger.error('Server registration error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Unregister an MCP server
app.delete('/api/servers/:serverId', async (req, res) => {
    try {
        const { serverId } = req.params;
        await serverManager.unregisterServer(serverId);
        systemMetrics.totalRequests++;
        
        res.json({
            success: true,
            message: 'Server unregistered successfully'
        });
    } catch (error) {
        systemMetrics.totalErrors++;
        logger.error('Server unregistration error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Get all registered servers
app.get('/api/servers', (req, res) => {
    const servers = serverManager.getAllServers();
    systemMetrics.totalRequests++;
    
    res.json({
        success: true,
        servers,
        count: servers.length
    });
});

// Get specific server details
app.get('/api/servers/:serverId', async (req, res) => {
    try {
        const { serverId } = req.params;
        const server = await serverManager.getServer(serverId);
        systemMetrics.totalRequests++;
        
        if (server) {
            res.json({
                success: true,
                server
            });
        } else {
            res.status(404).json({
                success: false,
                error: 'Server not found'
            });
        }
    } catch (error) {
        systemMetrics.totalErrors++;
        logger.error('Server lookup error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Proxy MCP function calls
app.post('/api/servers/:serverId/execute', async (req, res) => {
    try {
        const { serverId } = req.params;
        const { function_name, parameters } = req.body;
        
        const server = await serverManager.getServer(serverId);
        if (!server) {
            return res.status(404).json({
                success: false,
                error: 'Server not found'
            });
        }
        
        if (server.status !== 'active') {
            return res.status(503).json({
                success: false,
                error: 'Server is not active'
            });
        }
        
        // Forward the request to the MCP server
        const response = await fetch(`${server.url}/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ function_name, parameters })
        });
        
        const result = await response.json();
        systemMetrics.totalRequests++;
        
        // Broadcast execution to connected clients
        io.emit('function_executed', {
            serverId,
            serverName: server.name,
            functionName: function_name,
            parameters,
            result,
            timestamp: Date.now()
        });
        
        res.json({
            success: true,
            result
        });
    } catch (error) {
        systemMetrics.totalErrors++;
        logger.error('Function execution error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * WebSocket handlers
 */
io.on('connection', (socket) => {
    logger.info(`Client connected: ${socket.id}`);
    
    // Send current system state
    socket.emit('system_metrics', systemMetrics);
    socket.emit('servers_list', serverManager.getAllServers());
    
    socket.on('get_servers', () => {
        socket.emit('servers_list', serverManager.getAllServers());
    });
    
    socket.on('get_metrics', () => {
        socket.emit('system_metrics', systemMetrics);
    });
    
    socket.on('disconnect', () => {
        logger.info(`Client disconnected: ${socket.id}`);
    });
});

/**
 * Database initialization
 */
async function initializeDatabase() {
    try {
        // Create tables if they don't exist
        await db.query(`
            CREATE TABLE IF NOT EXISTS mcp_servers (
                id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                url VARCHAR(255) NOT NULL,
                capabilities JSONB DEFAULT '[]',
                metadata JSONB DEFAULT '{}',
                registered_at TIMESTAMP DEFAULT NOW(),
                last_updated TIMESTAMP DEFAULT NOW()
            )
        `);
        
        await db.query(`
            CREATE TABLE IF NOT EXISTS mcp_function_calls (
                id SERIAL PRIMARY KEY,
                server_id VARCHAR(255) REFERENCES mcp_servers(id),
                function_name VARCHAR(255) NOT NULL,
                parameters JSONB DEFAULT '{}',
                result JSONB,
                status VARCHAR(50) DEFAULT 'success',
                execution_time FLOAT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        `);
        
        logger.info('Database initialized successfully');
    } catch (error) {
        logger.error('Database initialization error:', error);
    }
}

/**
 * Cleanup and graceful shutdown
 */
process.on('SIGTERM', async () => {
    logger.info('Received SIGTERM, shutting down gracefully');
    
    // Close database connections
    await db.end();
    
    // Close Redis connection
    await redis.quit();
    
    // Close server
    server.close(() => {
        logger.info('Server closed');
        process.exit(0);
    });
});

/**
 * Start the server
 */
const PORT = process.env.REGISTRY_PORT || 3001;

async function startServer() {
    try {
        await initializeDatabase();
        
        server.listen(PORT, () => {
            logger.info(`Rehoboam MCP Registry running on port ${PORT}`);
            logger.info('Rehoboam awakening... All systems online. The future is predictable.');
        });
    } catch (error) {
        logger.error('Failed to start server:', error);
        process.exit(1);
    }
}

startServer();
