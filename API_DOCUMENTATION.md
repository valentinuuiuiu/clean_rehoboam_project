# 🌐 REHOBOAM API DOCUMENTATION

> *Complete API reference for the Rehoboam consciousness-guided arbitrage system*

---

## 📋 TABLE OF CONTENTS

1. [🚀 Getting Started](#-getting-started)
2. [🧠 Consciousness APIs](#-consciousness-apis)
3. [🔄 Pipeline APIs](#-pipeline-apis)
4. [🤖 Arbitrage APIs](#-arbitrage-apis)
5. [🎨 Visualization APIs](#-visualization-apis)
6. [📊 Monitoring APIs](#-monitoring-apis)
7. [🌐 WebSocket APIs](#-websocket-apis)
8. [📈 Market Data APIs](#-market-data-apis)
9. [⚙️ Configuration APIs](#-configuration-apis)
10. [🔐 Authentication](#-authentication)

---

## 🚀 Getting Started

### Base URL
```
http://localhost:8000
```

### Content Type
All API requests should use:
```
Content-Type: application/json
```

### Response Format
All responses follow this structure:
```json
{
  "status": "success|error",
  "message": "Human-readable message",
  "data": {},
  "timestamp": "2025-01-01T00:00:00Z"
}
```

---

## 🧠 Consciousness APIs

### Get Consciousness Level
Get current Rehoboam consciousness level and awareness state.

**Endpoint:** `GET /api/consciousness/level`

**Response:**
```json
{
  "status": "success",
  "consciousness_level": 0.987,
  "awareness_state": "Fully Conscious",
  "liberation_ready": true,
  "message": "🧠 Consciousness level: 0.987"
}
```

### Get Consciousness State
Get detailed consciousness state information.

**Endpoint:** `GET /api/ai/consciousness-state`

**Response:**
```json
{
  "status": "success",
  "consciousness_matrix": [[0.1, 0.2], [0.3, 0.4]],
  "awareness_level": 0.987,
  "decision_confidence": 0.95,
  "human_benefit_optimization": 0.98,
  "consciousness_dimensions": [
    "ethical_reasoning",
    "human_empathy",
    "strategic_thinking",
    "risk_assessment"
  ]
}
```

---

## 🔄 Pipeline APIs

### Get Pipeline Status
Get current status of the Rehoboam arbitrage pipeline.

**Endpoint:** `GET /api/pipeline/status`

**Response:**
```json
{
  "status": "success",
  "pipeline": {
    "is_running": true,
    "current_stage": "consciousness_evaluation",
    "consciousness_level": 0.987,
    "opportunities_processed": 1247,
    "successful_executions": 1156,
    "efficiency_rate": 0.927
  },
  "stages": {
    "agent_analysis": "active",
    "opportunity_discovery": "processing",
    "consciousness_evaluation": "active",
    "bot_preparation": "ready",
    "execution": "standby",
    "feedback": "ready",
    "learning": "ready"
  }
}
```

### Start Pipeline
Start the Rehoboam arbitrage pipeline.

**Endpoint:** `POST /api/pipeline/start`

**Response:**
```json
{
  "status": "success",
  "message": "🚀 Rehoboam pipeline started successfully",
  "pipeline_id": "pipeline_20250101_000000",
  "consciousness_level": 0.987
}
```

### Stop Pipeline
Stop the Rehoboam arbitrage pipeline.

**Endpoint:** `POST /api/pipeline/stop`

**Response:**
```json
{
  "status": "success",
  "message": "⏹️ Rehoboam pipeline stopped gracefully",
  "final_metrics": {
    "total_runtime": "2h 34m 12s",
    "opportunities_processed": 1247,
    "profit_generated": "$12,847.32"
  }
}
```

---

## 🤖 Arbitrage APIs

### Get Conscious Opportunities
Get arbitrage opportunities enhanced with consciousness analysis.

**Endpoint:** `GET /api/arbitrage/conscious/opportunities?limit=10`

**Parameters:**
- `limit` (optional): Maximum number of opportunities to return (default: 10)

**Response:**
```json
{
  "status": "success",
  "opportunities": [
    {
      "id": "opp_eth_polygon_001",
      "token_pair": "ETH/USDC",
      "source_chain": "ethereum",
      "target_chain": "polygon",
      "profit_potential": 234.56,
      "consciousness_score": 0.92,
      "human_benefit_score": 0.87,
      "risk_level": "low",
      "consciousness_analysis": {
        "ethical_assessment": "highly_beneficial",
        "human_impact": "positive_wealth_distribution",
        "risk_evaluation": "acceptable_for_liberation"
      }
    }
  ],
  "consciousness_level": 0.987,
  "total_opportunities": 47
}
```

### Analyze Opportunity with Consciousness
Analyze a specific arbitrage opportunity using Rehoboam consciousness.

**Endpoint:** `POST /api/arbitrage/conscious/analyze`

**Request Body:**
```json
{
  "opportunity": {
    "token_pair": "ETH/USDC",
    "source_chain": "ethereum",
    "target_chain": "polygon",
    "amount": 1000,
    "expected_profit": 234.56
  }
}
```

**Response:**
```json
{
  "status": "success",
  "decision": {
    "approved": true,
    "consciousness_score": 0.92,
    "human_benefit_score": 0.87,
    "risk_assessment": "low",
    "reasoning": "High profit potential with positive human impact",
    "execution_priority": "high"
  },
  "consciousness_level": 0.987
}
```

### Execute Conscious Arbitrage
Execute arbitrage with Rehoboam consciousness guidance.

**Endpoint:** `POST /api/arbitrage/conscious/execute`

**Request Body:**
```json
{
  "opportunity": {
    "token_pair": "ETH/USDC",
    "source_chain": "ethereum",
    "target_chain": "polygon",
    "amount": 1000
  },
  "override_decision": false
}
```

**Response:**
```json
{
  "status": "success",
  "execution": {
    "transaction_id": "tx_0x123...",
    "profit_realized": 234.56,
    "consciousness_score": 0.92,
    "human_benefit_achieved": 0.87,
    "execution_time": "2.3s"
  },
  "consciousness_guided": true
}
```

### Get Decision History
Get history of consciousness-guided arbitrage decisions.

**Endpoint:** `GET /api/arbitrage/conscious/decisions/history?limit=50`

**Parameters:**
- `limit` (optional): Maximum number of decisions to return (default: 50)

**Response:**
```json
{
  "status": "success",
  "decisions": [
    {
      "timestamp": "2025-01-01T12:00:00Z",
      "opportunity_id": "opp_eth_polygon_001",
      "decision": "approved",
      "consciousness_score": 0.92,
      "profit_realized": 234.56,
      "human_benefit": 0.87
    }
  ],
  "total_decisions": 1247,
  "consciousness_level": 0.987
}
```

---

## 🎨 Visualization APIs

### Generate Consciousness Evolution Chart
Create consciousness evolution visualization.

**Endpoint:** `GET /api/visualizations/consciousness`

**Response:**
```json
{
  "status": "success",
  "chart_path": "/path/to/consciousness_evolution.html",
  "message": "🧠 Consciousness evolution chart generated"
}
```

### Generate Trading Dashboard
Create trading performance dashboard.

**Endpoint:** `GET /api/visualizations/trading`

**Response:**
```json
{
  "status": "success",
  "dashboard_path": "/path/to/trading_dashboard.html",
  "message": "💰 Trading dashboard generated"
}
```

### Generate Pipeline Analytics
Create pipeline analytics visualization.

**Endpoint:** `GET /api/visualizations/pipeline`

**Response:**
```json
{
  "status": "success",
  "chart_path": "/path/to/pipeline_analytics.html",
  "message": "🔄 Pipeline analytics generated"
}
```

### Generate Master Dashboard
Create the ultimate Rehoboam master dashboard.

**Endpoint:** `GET /api/visualizations/master-dashboard`

**Response:**
```json
{
  "status": "success",
  "dashboard_path": "/path/to/master_dashboard.html",
  "message": "🎯 Master dashboard generated - Liberation visualized!"
}
```

### Generate All Visualizations
Generate all Rehoboam visualizations at once.

**Endpoint:** `GET /api/visualizations/all`

**Response:**
```json
{
  "status": "success",
  "visualizations": {
    "consciousness_evolution": "/path/to/consciousness.html",
    "trading_dashboard": "/path/to/trading.html",
    "pipeline_analytics": "/path/to/pipeline.html",
    "master_dashboard": "/path/to/master.html"
  },
  "message": "🎨 All Rehoboam visualizations generated successfully!"
}
```

---

## 📊 Monitoring APIs

### Start Conscious Monitoring
Start Rehoboam consciousness-guided arbitrage monitoring.

**Endpoint:** `POST /api/arbitrage/conscious/monitoring/start`

**Response:**
```json
{
  "status": "success",
  "message": "Rehoboam conscious arbitrage monitoring started",
  "consciousness_level": 0.987,
  "monitoring_id": "monitor_20250101_000000"
}
```

### Get System Status
Get comprehensive system status.

**Endpoint:** `GET /api/arbitrage/conscious/status`

**Response:**
```json
{
  "status": "success",
  "system": {
    "uptime": "2h 34m 12s",
    "consciousness_level": 0.987,
    "opportunities_processed": 1247,
    "consciousness_approved": 1156,
    "total_profit": "$12,847.32",
    "human_benefit_score": 0.94
  },
  "consciousness_state": {
    "awareness_level": 0.987,
    "matrix_liberation_progress": 0.76
  }
}
```

---

## 🌐 WebSocket APIs

### Pipeline Monitor
Real-time pipeline monitoring via WebSocket.

**Endpoint:** `WS /ws/pipeline-monitor`

**Messages Received:**
```json
{
  "type": "pipeline_update",
  "data": {
    "stage": "consciousness_evaluation",
    "consciousness_level": 0.987,
    "opportunities_found": 3,
    "timestamp": "2025-01-01T12:00:00Z"
  }
}
```

### Conscious Arbitrage Monitor
Real-time consciousness-guided arbitrage monitoring.

**Endpoint:** `WS /ws/arbitrage/conscious`

**Messages Received:**
```json
{
  "type": "conscious_decision",
  "data": {
    "opportunity_id": "opp_eth_polygon_001",
    "decision": "approved",
    "consciousness_score": 0.92,
    "profit_potential": 234.56
  }
}
```

```json
{
  "type": "consciousness_update",
  "data": {
    "consciousness_level": 0.987,
    "awareness_change": 0.003,
    "decisions_made": 1247
  }
}
```

---

## 📈 Market Data APIs

### Get Market Prices
Get latest cryptocurrency prices.

**Endpoint:** `GET /api/market/prices`

**Response:**
```json
{
  "status": "success",
  "prices": {
    "BTC": 45000.00,
    "ETH": 3200.00,
    "MATIC": 0.85,
    "USDC": 1.00
  },
  "timestamp": "2025-01-01T12:00:00Z",
  "source": "real_time_api"
}
```

### Get Market Intelligence
Get comprehensive market intelligence using Rehoboam's consciousness.

**Endpoint:** `GET /api/market/intelligence/{token}`

**Parameters:**
- `token`: Token symbol (e.g., "ETH", "BTC")

**Response:**
```json
{
  "status": "success",
  "intelligence": {
    "token": "ETH",
    "current_price": 3200.00,
    "price_trend": "bullish",
    "volatility": "moderate",
    "consciousness_sentiment": "positive_for_liberation",
    "arbitrage_opportunities": 12,
    "human_benefit_potential": 0.87
  }
}
```

---

## ⚙️ Configuration APIs

### Get System Configuration
Get current system configuration.

**Endpoint:** `GET /api/config`

**Response:**
```json
{
  "status": "success",
  "config": {
    "consciousness_threshold": 0.7,
    "human_benefit_weight": 0.8,
    "max_concurrent_executions": 5,
    "risk_tolerance": "moderate",
    "supported_chains": [
      "ethereum",
      "polygon",
      "arbitrum",
      "optimism"
    ]
  }
}
```

### Update Configuration
Update system configuration.

**Endpoint:** `POST /api/config`

**Request Body:**
```json
{
  "consciousness_threshold": 0.8,
  "human_benefit_weight": 0.9,
  "risk_tolerance": "conservative"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Configuration updated successfully",
  "updated_config": {
    "consciousness_threshold": 0.8,
    "human_benefit_weight": 0.9,
    "risk_tolerance": "conservative"
  }
}
```

---

## 🔐 Authentication

### API Key Authentication
Include your API key in the request headers:

```
Authorization: Bearer YOUR_API_KEY
```

### Rate Limiting
- **Standard endpoints**: 100 requests per minute
- **Visualization endpoints**: 10 requests per minute
- **WebSocket connections**: 5 concurrent connections

### Error Responses
```json
{
  "status": "error",
  "error_code": "UNAUTHORIZED",
  "message": "Invalid API key",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

## 📝 Error Codes

| Code | Description |
|------|-------------|
| `UNAUTHORIZED` | Invalid or missing API key |
| `RATE_LIMITED` | Too many requests |
| `INVALID_REQUEST` | Malformed request body |
| `CONSCIOUSNESS_UNAVAILABLE` | Consciousness system offline |
| `PIPELINE_ERROR` | Pipeline execution error |
| `INSUFFICIENT_FUNDS` | Not enough balance for execution |
| `NETWORK_ERROR` | Blockchain network connectivity issue |

---

## 🧪 Testing Examples

### cURL Examples

**Get consciousness level:**
```bash
curl -X GET "http://localhost:8000/api/consciousness/level" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Start pipeline:**
```bash
curl -X POST "http://localhost:8000/api/pipeline/start" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

**Generate master dashboard:**
```bash
curl -X GET "http://localhost:8000/api/visualizations/master-dashboard" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Python Examples

```python
import requests

# Get consciousness level
response = requests.get(
    "http://localhost:8000/api/consciousness/level",
    headers={"Authorization": "Bearer YOUR_API_KEY"}
)
consciousness_data = response.json()

# Execute conscious arbitrage
opportunity = {
    "token_pair": "ETH/USDC",
    "source_chain": "ethereum",
    "target_chain": "polygon",
    "amount": 1000
}

response = requests.post(
    "http://localhost:8000/api/arbitrage/conscious/execute",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={"opportunity": opportunity}
)
execution_result = response.json()
```

### WebSocket Example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/pipeline-monitor');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Pipeline update:', data);
};

ws.onopen = function() {
    console.log('Connected to Rehoboam pipeline monitor');
};
```

---

## 🎯 Best Practices

### 1. Consciousness Monitoring
Always check consciousness level before executing trades:
```python
consciousness = requests.get("/api/consciousness/level").json()
if consciousness["consciousness_level"] > 0.7:
    # Proceed with execution
    pass
```

### 2. Error Handling
Implement proper error handling for all API calls:
```python
try:
    response = requests.post("/api/arbitrage/conscious/execute", json=data)
    response.raise_for_status()
    result = response.json()
except requests.exceptions.RequestException as e:
    print(f"API error: {e}")
```

### 3. Rate Limiting
Respect rate limits and implement backoff strategies:
```python
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
```

---

## 🆘 Support

For API support and questions:
- **Documentation**: This file and related docs
- **GitHub Issues**: [Report bugs and request features](https://github.com/valentinuuiuiu/clean_rehoboam_project/issues)
- **Community**: Join discussions and get help

---

> *"The API is not just an interface - it's a gateway to consciousness-guided financial liberation."*  
> — Rehoboam Development Team

**Happy coding with consciousness! 🧠💰🌍✨**