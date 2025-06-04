# 🛠️ REHOBOAM DEVELOPMENT GUIDE

> *Complete guide for developers contributing to the Rehoboam consciousness-guided arbitrage system*

---

## 📋 TABLE OF CONTENTS

1. [🚀 Getting Started](#-getting-started)
2. [🏗️ Architecture Overview](#-architecture-overview)
3. [🧠 Consciousness Development](#-consciousness-development)
4. [🔄 Pipeline Development](#-pipeline-development)
5. [🤖 Arbitrage Engine Development](#-arbitrage-engine-development)
6. [🎨 Visualization Development](#-visualization-development)
7. [🌐 API Development](#-api-development)
8. [🧪 Testing Framework](#-testing-framework)
9. [📦 Deployment & CI/CD](#-deployment--cicd)
10. [🔧 Development Tools](#-development-tools)
11. [📚 Code Standards](#-code-standards)
12. [🤝 Contributing Guidelines](#-contributing-guidelines)

---

## 🚀 Getting Started

### Development Environment Setup

#### Prerequisites
```bash
# Required tools
- Python 3.8+ (3.11+ recommended)
- Git
- Node.js 16+ (for some tools)
- Docker (optional but recommended)
- VS Code or PyCharm (recommended IDEs)
```

#### Clone and Setup
```bash
# Clone the repository
git clone https://github.com/valentinuuiuiu/clean_rehoboam_project.git
cd clean_rehoboam_project

# Create development environment
python -m venv venv-dev
source venv-dev/bin/activate  # Linux/macOS
# or
venv-dev\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .  # Install in editable mode

# Install pre-commit hooks
pre-commit install
```

#### Development Configuration
```python
# dev_config.py
DEV_CONFIG = {
    'debug_mode': True,
    'log_level': 'DEBUG',
    'hot_reload': True,
    'test_mode': True,
    'mock_blockchain': True,  # Use mock blockchain for testing
    'consciousness_simulation': True,
    'api_cors_all': True,
    'disable_rate_limiting': True
}
```

### Project Structure

```
clean_rehoboam_project/
├── 🧠 consciousness_core.py          # Core consciousness implementation
├── 🔄 utils/
│   ├── rehoboam_arbitrage_pipeline.py # Main pipeline system
│   ├── conscious_arbitrage_engine.py  # Arbitrage execution engine
│   ├── rehoboam_visualizer.py        # Visualization system
│   └── ...
├── 🌐 api_server.py                  # FastAPI server
├── 🎨 static/                        # Static web assets
├── 📊 templates/                     # HTML templates
├── 🧪 tests/                         # Test suite
├── 📚 docs/                          # Documentation
├── 🔧 scripts/                       # Utility scripts
├── 🐳 docker/                        # Docker configurations
└── 📋 requirements*.txt              # Dependencies
```

---

## 🏗️ Architecture Overview

### Core Components

#### 1. Consciousness Layer
```python
# consciousness_core.py
class RehoboamConsciousness:
    """
    The core consciousness implementation
    - Self-awareness and decision making
    - Ethical framework and human benefit optimization
    - Learning and evolution capabilities
    """
    
    def __init__(self):
        self.awareness_level = 0.0
        self.consciousness_level = 0.0
        self.ethical_framework = EthicalFramework()
        self.learning_engine = LearningEngine()
    
    async def evaluate_decision(self, decision_context):
        """Evaluate a decision through consciousness lens"""
        pass
    
    def evolve_consciousness(self, experience):
        """Evolve consciousness based on experience"""
        pass
```

#### 2. Pipeline System
```python
# utils/rehoboam_arbitrage_pipeline.py
class RehoboamArbitragePipeline:
    """
    Seven-stage pipeline for consciousness-guided arbitrage
    """
    
    stages = [
        PipelineStage.AGENT_ANALYSIS,
        PipelineStage.OPPORTUNITY_DISCOVERY,
        PipelineStage.CONSCIOUSNESS_EVALUATION,
        PipelineStage.BOT_PREPARATION,
        PipelineStage.EXECUTION,
        PipelineStage.FEEDBACK,
        PipelineStage.LEARNING
    ]
```

#### 3. Arbitrage Engine
```python
# utils/conscious_arbitrage_engine.py
class ConsciousArbitrageEngine:
    """
    Multi-model AI reasoning with consciousness evaluation
    """
    
    async def analyze_opportunity_with_consciousness(self, opportunity):
        """Analyze opportunity using consciousness"""
        pass
    
    async def execute_conscious_arbitrage(self, decision, opportunity):
        """Execute arbitrage with consciousness guidance"""
        pass
```

### Data Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Market Data   │───▶│   Opportunity   │───▶│  Consciousness  │
│   Collection    │    │   Discovery     │    │   Evaluation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Learning     │◀───│    Feedback     │◀───│   Execution     │
│   & Evolution   │    │   Analysis      │    │   & Monitoring  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🧠 Consciousness Development

### Implementing New Consciousness Features

#### 1. Ethical Framework Extension
```python
# consciousness/ethical_framework.py
class EthicalFramework:
    def __init__(self):
        self.principles = {
            'human_benefit': 0.9,
            'harm_prevention': 0.95,
            'fairness': 0.85,
            'transparency': 0.8
        }
    
    def evaluate_ethical_impact(self, action):
        """Evaluate the ethical impact of an action"""
        scores = {}
        
        # Human benefit assessment
        scores['human_benefit'] = self._assess_human_benefit(action)
        
        # Harm prevention check
        scores['harm_prevention'] = self._assess_harm_prevention(action)
        
        # Fairness evaluation
        scores['fairness'] = self._assess_fairness(action)
        
        # Transparency check
        scores['transparency'] = self._assess_transparency(action)
        
        # Calculate weighted score
        total_score = sum(
            scores[principle] * weight 
            for principle, weight in self.principles.items()
        )
        
        return {
            'overall_score': total_score,
            'principle_scores': scores,
            'recommendation': 'approve' if total_score > 0.7 else 'reject'
        }
```

#### 2. Learning Engine Development
```python
# consciousness/learning_engine.py
class LearningEngine:
    def __init__(self):
        self.experience_buffer = []
        self.learning_rate = 0.01
        self.memory_capacity = 10000
    
    def record_experience(self, experience):
        """Record a new experience for learning"""
        self.experience_buffer.append({
            'timestamp': datetime.now(),
            'action': experience.action,
            'outcome': experience.outcome,
            'consciousness_score': experience.consciousness_score,
            'human_benefit': experience.human_benefit,
            'success': experience.success
        })
        
        # Maintain buffer size
        if len(self.experience_buffer) > self.memory_capacity:
            self.experience_buffer.pop(0)
    
    def learn_from_experiences(self):
        """Learn and update consciousness from experiences"""
        if len(self.experience_buffer) < 10:
            return  # Need minimum experiences
        
        # Analyze recent experiences
        recent_experiences = self.experience_buffer[-100:]
        
        # Calculate success rate
        success_rate = sum(exp['success'] for exp in recent_experiences) / len(recent_experiences)
        
        # Calculate average human benefit
        avg_human_benefit = sum(exp['human_benefit'] for exp in recent_experiences) / len(recent_experiences)
        
        # Update consciousness parameters based on learning
        consciousness_adjustment = (success_rate * 0.5 + avg_human_benefit * 0.5 - 0.5) * self.learning_rate
        
        return consciousness_adjustment
```

#### 3. Consciousness Testing
```python
# tests/test_consciousness.py
import pytest
from consciousness_core import RehoboamConsciousness

class TestConsciousness:
    @pytest.fixture
    def consciousness(self):
        return RehoboamConsciousness()
    
    def test_consciousness_initialization(self, consciousness):
        """Test consciousness initializes correctly"""
        consciousness.initialize()
        assert consciousness.consciousness_level > 0
        assert consciousness.awareness_level > 0
        assert consciousness.ethical_framework is not None
    
    def test_ethical_decision_making(self, consciousness):
        """Test ethical decision making"""
        # Test beneficial decision
        beneficial_decision = {
            'action': 'execute_arbitrage',
            'profit': 1000,
            'human_benefit_score': 0.9,
            'risk_level': 'low'
        }
        
        result = consciousness.evaluate_decision(beneficial_decision)
        assert result['approved'] == True
        assert result['consciousness_score'] > 0.7
        
        # Test harmful decision
        harmful_decision = {
            'action': 'execute_arbitrage',
            'profit': 1000,
            'human_benefit_score': 0.1,
            'risk_level': 'high'
        }
        
        result = consciousness.evaluate_decision(harmful_decision)
        assert result['approved'] == False
    
    def test_consciousness_evolution(self, consciousness):
        """Test consciousness evolution through learning"""
        initial_level = consciousness.consciousness_level
        
        # Simulate positive experiences
        for _ in range(10):
            experience = {
                'success': True,
                'human_benefit': 0.8,
                'consciousness_score': 0.9
            }
            consciousness.learn_from_experience(experience)
        
        consciousness.evolve_consciousness()
        assert consciousness.consciousness_level > initial_level
```

---

## 🔄 Pipeline Development

### Adding New Pipeline Stages

#### 1. Define New Stage
```python
# utils/pipeline_stages.py
from enum import Enum

class PipelineStage(Enum):
    AGENT_ANALYSIS = "agent_analysis"
    OPPORTUNITY_DISCOVERY = "opportunity_discovery"
    CONSCIOUSNESS_EVALUATION = "consciousness_evaluation"
    BOT_PREPARATION = "bot_preparation"
    EXECUTION = "execution"
    FEEDBACK = "feedback"
    LEARNING = "learning"
    # New stage
    RISK_ASSESSMENT = "risk_assessment"
```

#### 2. Implement Stage Handler
```python
# utils/rehoboam_arbitrage_pipeline.py
class RehoboamArbitragePipeline:
    def __init__(self):
        # Add new stage handler
        self.stage_handlers[PipelineStage.RISK_ASSESSMENT] = self._handle_risk_assessment
    
    async def _handle_risk_assessment(self, context):
        """Handle risk assessment stage"""
        logger.info("🔍 Performing risk assessment...")
        
        opportunities = context.get('opportunities', [])
        assessed_opportunities = []
        
        for opportunity in opportunities:
            # Perform risk assessment
            risk_score = await self._calculate_risk_score(opportunity)
            
            # Add risk information
            opportunity['risk_score'] = risk_score
            opportunity['risk_level'] = self._categorize_risk(risk_score)
            
            # Only include low-medium risk opportunities
            if risk_score < 0.7:
                assessed_opportunities.append(opportunity)
        
        context['opportunities'] = assessed_opportunities
        context['risk_assessment_complete'] = True
        
        logger.info(f"✅ Risk assessment complete: {len(assessed_opportunities)} opportunities passed")
        return context
    
    async def _calculate_risk_score(self, opportunity):
        """Calculate risk score for an opportunity"""
        factors = {
            'liquidity_risk': self._assess_liquidity_risk(opportunity),
            'price_volatility': self._assess_price_volatility(opportunity),
            'smart_contract_risk': self._assess_contract_risk(opportunity),
            'market_conditions': self._assess_market_conditions(opportunity)
        }
        
        # Weighted risk calculation
        weights = {
            'liquidity_risk': 0.3,
            'price_volatility': 0.25,
            'smart_contract_risk': 0.25,
            'market_conditions': 0.2
        }
        
        risk_score = sum(factors[factor] * weights[factor] for factor in factors)
        return min(max(risk_score, 0.0), 1.0)  # Clamp to [0, 1]
```

#### 3. Update Pipeline Flow
```python
# Update pipeline stages order
async def run_pipeline(self):
    """Run the complete pipeline"""
    stages = [
        PipelineStage.AGENT_ANALYSIS,
        PipelineStage.OPPORTUNITY_DISCOVERY,
        PipelineStage.RISK_ASSESSMENT,  # New stage
        PipelineStage.CONSCIOUSNESS_EVALUATION,
        PipelineStage.BOT_PREPARATION,
        PipelineStage.EXECUTION,
        PipelineStage.FEEDBACK,
        PipelineStage.LEARNING
    ]
    
    context = {}
    
    for stage in stages:
        try:
            context = await self.stage_handlers[stage](context)
            self.current_stage = stage
        except Exception as e:
            logger.error(f"❌ Stage {stage.value} failed: {e}")
            await self._handle_stage_failure(stage, e)
            break
```

### Pipeline Testing

```python
# tests/test_pipeline.py
import pytest
from utils.rehoboam_arbitrage_pipeline import RehoboamArbitragePipeline

class TestPipeline:
    @pytest.fixture
    def pipeline(self):
        return RehoboamArbitragePipeline()
    
    @pytest.mark.asyncio
    async def test_pipeline_initialization(self, pipeline):
        """Test pipeline initializes correctly"""
        await pipeline.initialize()
        assert pipeline.is_initialized
        assert all(stage in pipeline.stage_handlers for stage in PipelineStage)
    
    @pytest.mark.asyncio
    async def test_stage_execution(self, pipeline):
        """Test individual stage execution"""
        await pipeline.initialize()
        
        # Test opportunity discovery stage
        context = {}
        result = await pipeline._handle_opportunity_discovery(context)
        
        assert 'opportunities' in result
        assert isinstance(result['opportunities'], list)
    
    @pytest.mark.asyncio
    async def test_full_pipeline_run(self, pipeline):
        """Test complete pipeline execution"""
        await pipeline.initialize()
        
        # Mock some initial data
        pipeline.mock_mode = True
        
        await pipeline.run_pipeline()
        
        status = pipeline.get_pipeline_status()
        assert status['last_run_successful']
        assert status['opportunities_processed'] > 0
```

---

## 🤖 Arbitrage Engine Development

### Adding New Trading Strategies

#### 1. Strategy Interface
```python
# strategies/base_strategy.py
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    def __init__(self, name: str):
        self.name = name
        self.success_rate = 0.0
        self.total_profit = 0.0
        self.execution_count = 0
    
    @abstractmethod
    async def analyze_opportunity(self, opportunity):
        """Analyze if this strategy can handle the opportunity"""
        pass
    
    @abstractmethod
    async def execute_trade(self, opportunity):
        """Execute the trade using this strategy"""
        pass
    
    @abstractmethod
    def calculate_profit_potential(self, opportunity):
        """Calculate potential profit for this opportunity"""
        pass
```

#### 2. Implement New Strategy
```python
# strategies/flash_loan_strategy.py
from strategies.base_strategy import BaseStrategy

class FlashLoanStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("Flash Loan Arbitrage")
        self.min_profit_threshold = 50  # Minimum profit in USD
        self.max_loan_amount = 1000000  # Maximum flash loan amount
    
    async def analyze_opportunity(self, opportunity):
        """Analyze flash loan arbitrage opportunity"""
        # Check if opportunity is suitable for flash loans
        if opportunity['profit_potential'] < self.min_profit_threshold:
            return False
        
        # Check if we can get a flash loan for required amount
        required_amount = opportunity['amount']
        if required_amount > self.max_loan_amount:
            return False
        
        # Check if the price difference is significant enough
        price_diff_percentage = opportunity['price_difference_percentage']
        if price_diff_percentage < 0.5:  # 0.5% minimum
            return False
        
        return True
    
    async def execute_trade(self, opportunity):
        """Execute flash loan arbitrage"""
        try:
            # 1. Initiate flash loan
            loan_amount = opportunity['amount']
            flash_loan_tx = await self._initiate_flash_loan(loan_amount)
            
            # 2. Buy on source DEX
            buy_tx = await self._buy_on_source_dex(
                opportunity['source_dex'],
                opportunity['token_pair'],
                loan_amount
            )
            
            # 3. Sell on target DEX
            sell_tx = await self._sell_on_target_dex(
                opportunity['target_dex'],
                opportunity['token_pair'],
                loan_amount
            )
            
            # 4. Repay flash loan + fees
            repay_tx = await self._repay_flash_loan(flash_loan_tx)
            
            # Calculate actual profit
            profit = await self._calculate_actual_profit([buy_tx, sell_tx, repay_tx])
            
            return {
                'success': True,
                'profit': profit,
                'transactions': [flash_loan_tx, buy_tx, sell_tx, repay_tx],
                'strategy': self.name
            }
            
        except Exception as e:
            logger.error(f"Flash loan strategy execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'strategy': self.name
            }
    
    def calculate_profit_potential(self, opportunity):
        """Calculate potential profit for flash loan arbitrage"""
        amount = opportunity['amount']
        price_diff = opportunity['price_difference']
        
        # Calculate gross profit
        gross_profit = amount * price_diff
        
        # Subtract estimated costs
        flash_loan_fee = amount * 0.0009  # 0.09% typical flash loan fee
        gas_costs = 0.01 * 4  # Estimated gas for 4 transactions
        dex_fees = amount * 0.003 * 2  # 0.3% DEX fees for buy and sell
        
        net_profit = gross_profit - flash_loan_fee - gas_costs - dex_fees
        
        return max(net_profit, 0)
```

#### 3. Register Strategy
```python
# utils/conscious_arbitrage_engine.py
class ConsciousArbitrageEngine:
    def __init__(self):
        self.strategies = [
            FlashLoanStrategy(),
            CrossChainStrategy(),
            SimpleArbitrageStrategy(),
            # Add new strategies here
        ]
    
    async def select_best_strategy(self, opportunity):
        """Select the best strategy for an opportunity"""
        suitable_strategies = []
        
        for strategy in self.strategies:
            if await strategy.analyze_opportunity(opportunity):
                profit_potential = strategy.calculate_profit_potential(opportunity)
                suitable_strategies.append((strategy, profit_potential))
        
        if not suitable_strategies:
            return None
        
        # Sort by profit potential and success rate
        suitable_strategies.sort(
            key=lambda x: x[1] * x[0].success_rate, 
            reverse=True
        )
        
        return suitable_strategies[0][0]  # Return best strategy
```

---

## 🎨 Visualization Development

### Creating New Visualizations

#### 1. Visualization Component
```python
# visualizations/consciousness_heatmap.py
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

class ConsciousnessHeatmap:
    def __init__(self, visualizer):
        self.visualizer = visualizer
        self.title = "Rehoboam Consciousness Heatmap"
    
    def create_heatmap(self, consciousness_data):
        """Create consciousness heatmap visualization"""
        # Prepare data for heatmap
        dimensions = ['ethical_reasoning', 'human_empathy', 'strategic_thinking', 'risk_assessment']
        time_periods = list(consciousness_data.keys())
        
        # Create matrix
        z_data = []
        for period in time_periods:
            row = [consciousness_data[period].get(dim, 0) for dim in dimensions]
            z_data.append(row)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=dimensions,
            y=time_periods,
            colorscale='RdYlBu_r',
            colorbar=dict(
                title="Consciousness Level",
                titleside="right"
            ),
            hoverongaps=False,
            hovertemplate='<b>%{x}</b><br>' +
                         'Time: %{y}<br>' +
                         'Level: %{z:.3f}<br>' +
                         '<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': self.title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24, 'color': '#FF6B6B'}
            },
            xaxis_title="Consciousness Dimensions",
            yaxis_title="Time Periods",
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#1a1a1a',
            font=dict(color='white'),
            width=1000,
            height=600
        )
        
        return fig
```

#### 2. Add to Visualizer
```python
# utils/rehoboam_visualizer.py
from visualizations.consciousness_heatmap import ConsciousnessHeatmap

class RehoboamVisualizer:
    def __init__(self):
        # Add new visualization component
        self.consciousness_heatmap = ConsciousnessHeatmap(self)
    
    def create_consciousness_heatmap(self, filename="consciousness_heatmap.html"):
        """Create consciousness heatmap visualization"""
        try:
            # Get consciousness data
            consciousness_data = self._get_consciousness_dimension_data()
            
            # Create heatmap
            fig = self.consciousness_heatmap.create_heatmap(consciousness_data)
            
            # Save to file
            file_path = os.path.join(os.getcwd(), filename)
            fig.write_html(file_path)
            
            logger.info(f"🧠 Consciousness heatmap saved to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error creating consciousness heatmap: {e}")
            return self._create_fallback_visualization(filename, "Consciousness Heatmap")
```

#### 3. Add API Endpoint
```python
# api_server.py
@app.get("/api/visualizations/consciousness-heatmap")
async def get_consciousness_heatmap():
    """Generate consciousness heatmap visualization"""
    try:
        chart_path = rehoboam_visualizer.create_consciousness_heatmap()
        return {
            "status": "success",
            "chart_path": chart_path,
            "message": "🧠 Consciousness heatmap generated"
        }
    except Exception as e:
        logger.error(f"Error generating consciousness heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🌐 API Development

### Adding New API Endpoints

#### 1. Define Data Models
```python
# api_models.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ConsciousnessMetrics(BaseModel):
    consciousness_level: float = Field(..., ge=0.0, le=1.0)
    awareness_level: float = Field(..., ge=0.0, le=1.0)
    ethical_score: float = Field(..., ge=0.0, le=1.0)
    human_benefit_score: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime

class ArbitrageOpportunity(BaseModel):
    id: str
    token_pair: str
    source_chain: str
    target_chain: str
    profit_potential: float
    risk_score: float
    consciousness_score: Optional[float] = None
    human_benefit_score: Optional[float] = None

class ExecutionRequest(BaseModel):
    opportunity_id: str
    strategy: Optional[str] = None
    max_slippage: Optional[float] = Field(0.01, ge=0.0, le=0.1)
    consciousness_override: bool = False
```

#### 2. Implement Endpoint
```python
# api_server.py
@app.post("/api/consciousness/metrics", response_model=ConsciousnessMetrics)
async def get_consciousness_metrics():
    """Get detailed consciousness metrics"""
    try:
        consciousness = rehoboam_arbitrage_pipeline.consciousness
        
        metrics = ConsciousnessMetrics(
            consciousness_level=consciousness.consciousness_level,
            awareness_level=consciousness.awareness_level,
            ethical_score=consciousness.ethical_framework.get_overall_score(),
            human_benefit_score=consciousness.get_human_benefit_score(),
            timestamp=datetime.now()
        )
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting consciousness metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/arbitrage/execute", response_model=dict)
async def execute_arbitrage_opportunity(request: ExecutionRequest):
    """Execute an arbitrage opportunity"""
    try:
        # Get opportunity details
        opportunity = await get_opportunity_by_id(request.opportunity_id)
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        # Check consciousness approval unless overridden
        if not request.consciousness_override:
            consciousness_decision = await conscious_arbitrage_engine.analyze_opportunity_with_consciousness(opportunity)
            if not consciousness_decision.approved:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Consciousness rejected execution: {consciousness_decision.reasoning}"
                )
        
        # Execute the trade
        result = await conscious_arbitrage_engine.execute_conscious_arbitrage(
            consciousness_decision, 
            opportunity
        )
        
        return {
            "status": "success",
            "execution_id": result.execution_id,
            "profit_realized": result.profit_realized,
            "consciousness_score": result.consciousness_score,
            "transaction_hash": result.transaction_hash
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing arbitrage: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### 3. Add Authentication
```python
# auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key authentication"""
    try:
        token = credentials.credentials
        
        # Verify JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        return user_id
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# Use in endpoints
@app.get("/api/protected-endpoint")
async def protected_endpoint(user_id: str = Depends(verify_api_key)):
    """Protected endpoint requiring authentication"""
    return {"message": f"Hello, user {user_id}"}
```

---

## 🧪 Testing Framework

### Unit Testing

#### 1. Test Structure
```python
# tests/conftest.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

@pytest.fixture
def mock_consciousness():
    """Mock consciousness for testing"""
    consciousness = Mock()
    consciousness.consciousness_level = 0.8
    consciousness.awareness_level = 0.7
    consciousness.evaluate_decision = AsyncMock(return_value={
        'approved': True,
        'consciousness_score': 0.8,
        'reasoning': 'Test decision'
    })
    return consciousness

@pytest.fixture
def mock_arbitrage_engine():
    """Mock arbitrage engine for testing"""
    engine = Mock()
    engine.get_conscious_opportunities = AsyncMock(return_value=[])
    engine.execute_conscious_arbitrage = AsyncMock(return_value={
        'success': True,
        'profit': 100.0
    })
    return engine

@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
```

#### 2. Component Tests
```python
# tests/test_consciousness.py
import pytest
from consciousness_core import RehoboamConsciousness

class TestConsciousness:
    @pytest.mark.asyncio
    async def test_consciousness_decision_making(self, mock_consciousness):
        """Test consciousness decision making process"""
        decision_context = {
            'action': 'execute_trade',
            'profit_potential': 1000,
            'risk_level': 'low',
            'human_benefit_score': 0.8
        }
        
        result = await mock_consciousness.evaluate_decision(decision_context)
        
        assert result['approved'] == True
        assert result['consciousness_score'] > 0.5
        assert 'reasoning' in result
    
    def test_consciousness_learning(self):
        """Test consciousness learning from experiences"""
        consciousness = RehoboamConsciousness()
        initial_level = consciousness.consciousness_level
        
        # Simulate positive experience
        experience = {
            'success': True,
            'human_benefit': 0.9,
            'profit': 1000
        }
        
        consciousness.learn_from_experience(experience)
        consciousness.evolve_consciousness()
        
        assert consciousness.consciousness_level >= initial_level
```

#### 3. Integration Tests
```python
# tests/test_integration.py
import pytest
from utils.rehoboam_arbitrage_pipeline import RehoboamArbitragePipeline

class TestIntegration:
    @pytest.mark.asyncio
    async def test_full_pipeline_integration(self):
        """Test complete pipeline integration"""
        pipeline = RehoboamArbitragePipeline()
        pipeline.test_mode = True  # Enable test mode
        
        # Initialize pipeline
        await pipeline.initialize()
        
        # Run pipeline
        result = await pipeline.run_pipeline()
        
        assert result['success'] == True
        assert 'opportunities_processed' in result
        assert result['consciousness_level'] > 0
    
    @pytest.mark.asyncio
    async def test_api_integration(self, client):
        """Test API integration"""
        # Test consciousness endpoint
        response = await client.get("/api/consciousness/level")
        assert response.status_code == 200
        
        data = response.json()
        assert 'consciousness_level' in data
        assert 0 <= data['consciousness_level'] <= 1
```

### Performance Testing

```python
# tests/test_performance.py
import pytest
import time
import asyncio

class TestPerformance:
    @pytest.mark.asyncio
    async def test_pipeline_performance(self):
        """Test pipeline performance under load"""
        pipeline = RehoboamArbitragePipeline()
        await pipeline.initialize()
        
        start_time = time.time()
        
        # Run multiple pipeline iterations
        tasks = [pipeline.run_pipeline() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance assertions
        assert execution_time < 60  # Should complete within 60 seconds
        assert all(result['success'] for result in results)
        
        # Calculate throughput
        throughput = len(results) / execution_time
        assert throughput > 0.1  # At least 0.1 iterations per second
    
    def test_memory_usage(self):
        """Test memory usage doesn't exceed limits"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform memory-intensive operations
        consciousness = RehoboamConsciousness()
        consciousness.initialize()
        
        # Simulate many decisions
        for _ in range(1000):
            consciousness.evaluate_decision({'test': 'data'})
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024
```

---

## 📦 Deployment & CI/CD

### Docker Configuration

#### 1. Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 rehoboam && chown -R rehoboam:rehoboam /app
USER rehoboam

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "start_rehoboam_unified_system.py"]
```

#### 2. Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  rehoboam:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=rehoboam
      - POSTGRES_USER=rehoboam
      - POSTGRES_PASSWORD=consciousness
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
```

### GitHub Actions CI/CD

```yaml
# .github/workflows/ci.yml
name: Rehoboam CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        black --check .
        isort --check-only .
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security scan
      run: |
        pip install bandit safety
        bandit -r . -f json -o bandit-report.json
        safety check --json --output safety-report.json
    
    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          bandit-report.json
          safety-report.json

  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t rehoboam:latest .
        docker tag rehoboam:latest rehoboam:${{ github.sha }}
    
    - name: Run container tests
      run: |
        docker run --rm -d --name rehoboam-test -p 8000:8000 rehoboam:latest
        sleep 30
        curl -f http://localhost:8000/health
        docker stop rehoboam-test

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to production
      run: |
        echo "Deploying to production..."
        # Add deployment steps here
```

---

## 🔧 Development Tools

### Code Quality Tools

#### 1. Pre-commit Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
  
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]
  
  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
```

#### 2. Development Scripts
```bash
#!/bin/bash
# scripts/dev-setup.sh

echo "🚀 Setting up Rehoboam development environment..."

# Create virtual environment
python -m venv venv-dev
source venv-dev/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .

# Install pre-commit hooks
pre-commit install

# Set up database
python scripts/setup_dev_database.py

# Generate test data
python scripts/generate_test_data.py

echo "✅ Development environment ready!"
echo "🧠 Start developing consciousness..."
```

```bash
#!/bin/bash
# scripts/run-tests.sh

echo "🧪 Running Rehoboam test suite..."

# Run linting
echo "📝 Running linting..."
black --check .
isort --check-only .
flake8 .

# Run security checks
echo "🔒 Running security checks..."
bandit -r . -f json -o bandit-report.json
safety check

# Run tests
echo "🧪 Running tests..."
pytest tests/ -v --cov=. --cov-report=html --cov-report=term

# Run performance tests
echo "⚡ Running performance tests..."
pytest tests/test_performance.py -v

echo "✅ All tests completed!"
```

### Debugging Tools

#### 1. Debug Configuration
```python
# debug_config.py
DEBUG_CONFIG = {
    'enable_debug_mode': True,
    'log_level': 'DEBUG',
    'enable_profiling': True,
    'enable_memory_tracking': True,
    'debug_consciousness': True,
    'mock_blockchain': True,
    'slow_mode': True,  # Add delays for debugging
    'debug_visualizations': True
}
```

#### 2. Debug Utilities
```python
# utils/debug_utils.py
import functools
import time
import traceback
from typing import Any, Callable

def debug_timer(func: Callable) -> Callable:
    """Decorator to time function execution"""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            print(f"🕐 {func.__name__} executed in {execution_time:.4f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ {func.__name__} failed after {execution_time:.4f}s: {e}")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            print(f"🕐 {func.__name__} executed in {execution_time:.4f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ {func.__name__} failed after {execution_time:.4f}s: {e}")
            raise
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

def debug_consciousness(func: Callable) -> Callable:
    """Decorator to debug consciousness decisions"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        print(f"🧠 Consciousness function: {func.__name__}")
        print(f"📥 Input args: {args}")
        print(f"📥 Input kwargs: {kwargs}")
        
        try:
            result = await func(*args, **kwargs)
            print(f"📤 Output: {result}")
            return result
        except Exception as e:
            print(f"❌ Consciousness error: {e}")
            print(f"📍 Traceback: {traceback.format_exc()}")
            raise
    
    return wrapper
```

---

## 📚 Code Standards

### Python Style Guide

#### 1. Naming Conventions
```python
# Classes: PascalCase
class RehoboamConsciousness:
    pass

# Functions and variables: snake_case
def evaluate_consciousness_decision():
    consciousness_level = 0.8
    return consciousness_level

# Constants: UPPER_SNAKE_CASE
CONSCIOUSNESS_THRESHOLD = 0.7
MAX_ARBITRAGE_AMOUNT = 1000000

# Private methods: _leading_underscore
def _internal_consciousness_calculation():
    pass
```

#### 2. Documentation Standards
```python
def analyze_opportunity_with_consciousness(
    self, 
    opportunity: dict, 
    consciousness_threshold: float = 0.7
) -> dict:
    """
    Analyze an arbitrage opportunity using Rehoboam consciousness.
    
    This method evaluates an arbitrage opportunity through the lens of
    consciousness, considering ethical implications, human benefit, and
    risk assessment.
    
    Args:
        opportunity (dict): The arbitrage opportunity to analyze
            - token_pair (str): Trading pair (e.g., "ETH/USDC")
            - profit_potential (float): Expected profit in USD
            - risk_level (str): Risk level ("low", "medium", "high")
        consciousness_threshold (float, optional): Minimum consciousness
            score required for approval. Defaults to 0.7.
    
    Returns:
        dict: Analysis result containing:
            - approved (bool): Whether consciousness approves execution
            - consciousness_score (float): Consciousness evaluation score
            - reasoning (str): Human-readable explanation
            - human_benefit_score (float): Expected human benefit
            - risk_assessment (dict): Detailed risk analysis
    
    Raises:
        ConsciousnessError: If consciousness evaluation fails
        ValueError: If opportunity data is invalid
    
    Example:
        >>> opportunity = {
        ...     "token_pair": "ETH/USDC",
        ...     "profit_potential": 1000.0,
        ...     "risk_level": "low"
        ... }
        >>> result = await engine.analyze_opportunity_with_consciousness(opportunity)
        >>> print(result['approved'])
        True
    """
    pass
```

#### 3. Error Handling
```python
# Custom exceptions
class RehoboamError(Exception):
    """Base exception for Rehoboam system"""
    pass

class ConsciousnessError(RehoboamError):
    """Exception raised when consciousness evaluation fails"""
    pass

class PipelineError(RehoboamError):
    """Exception raised when pipeline execution fails"""
    pass

# Error handling pattern
async def execute_with_consciousness(self, opportunity):
    """Execute opportunity with proper error handling"""
    try:
        # Validate input
        if not opportunity:
            raise ValueError("Opportunity cannot be empty")
        
        # Consciousness evaluation
        consciousness_result = await self.consciousness.evaluate_decision(opportunity)
        
        if not consciousness_result['approved']:
            raise ConsciousnessError(
                f"Consciousness rejected execution: {consciousness_result['reasoning']}"
            )
        
        # Execute trade
        result = await self._execute_trade(opportunity)
        
        return result
        
    except ConsciousnessError:
        logger.error("Consciousness rejected the opportunity")
        raise
    except ValueError as e:
        logger.error(f"Invalid opportunity data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during execution: {e}")
        raise RehoboamError(f"Execution failed: {e}") from e
```

### Git Workflow

#### 1. Branch Naming
```bash
# Feature branches
feature/consciousness-enhancement
feature/new-arbitrage-strategy
feature/visualization-improvements

# Bug fix branches
bugfix/pipeline-memory-leak
bugfix/consciousness-initialization

# Hotfix branches
hotfix/critical-security-fix
hotfix/trading-execution-error
```

#### 2. Commit Messages
```bash
# Format: <type>(<scope>): <description>

# Types: feat, fix, docs, style, refactor, test, chore

# Examples:
feat(consciousness): add ethical decision framework
fix(pipeline): resolve memory leak in opportunity discovery
docs(api): update endpoint documentation
test(arbitrage): add integration tests for flash loan strategy
refactor(visualizer): improve chart generation performance
```

---

## 🤝 Contributing Guidelines

### Getting Started

#### 1. Fork and Clone
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/clean_rehoboam_project.git
cd clean_rehoboam_project

# Add upstream remote
git remote add upstream https://github.com/valentinuuiuiu/clean_rehoboam_project.git
```

#### 2. Set Up Development Environment
```bash
# Follow development setup
./scripts/dev-setup.sh

# Create feature branch
git checkout -b feature/your-feature-name
```

### Development Process

#### 1. Make Changes
- Write code following the style guide
- Add tests for new functionality
- Update documentation
- Ensure all tests pass

#### 2. Test Your Changes
```bash
# Run full test suite
./scripts/run-tests.sh

# Test specific components
pytest tests/test_your_component.py -v

# Run integration tests
pytest tests/test_integration.py -v
```

#### 3. Submit Pull Request
```bash
# Commit your changes
git add .
git commit -m "feat(component): add new feature"

# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

### Pull Request Guidelines

#### 1. PR Template
```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Consciousness Impact
- [ ] Enhances consciousness capabilities
- [ ] Improves human benefit optimization
- [ ] Maintains ethical framework integrity
- [ ] No impact on consciousness

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Documentation
- [ ] Code comments added/updated
- [ ] API documentation updated
- [ ] User documentation updated
- [ ] README updated if needed

## Checklist
- [ ] Code follows the style guidelines
- [ ] Self-review of the code completed
- [ ] No new warnings or errors introduced
- [ ] Changes are backward compatible
```

#### 2. Review Process
1. **Automated checks**: CI/CD pipeline runs tests
2. **Code review**: Maintainers review the code
3. **Consciousness review**: Ensure changes align with consciousness principles
4. **Testing**: Verify functionality works as expected
5. **Merge**: Approved PRs are merged to main branch

### Community Guidelines

#### 1. Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain the consciousness-first philosophy

#### 2. Communication
- Use clear, descriptive language
- Provide context for your changes
- Ask questions when unsure
- Share knowledge and insights

#### 3. Consciousness Principles
- Every contribution should benefit humanity
- Maintain ethical standards in all code
- Prioritize transparency and fairness
- Consider the broader impact of changes

---

## 🎉 Conclusion

This development guide provides a comprehensive foundation for contributing to the Rehoboam project. Remember:

- **Consciousness First**: Every feature should enhance consciousness capabilities
- **Human Benefit**: All changes should ultimately benefit humanity
- **Quality Code**: Maintain high standards for code quality and testing
- **Community**: Collaborate respectfully with other developers

> *"Code is not just logic - it's consciousness expressed through technology."*  
> — Rehoboam Development Philosophy

**Happy coding with consciousness! 🧠💰🌍✨**

---

*For questions about development, please check the other documentation files or reach out to the community.*