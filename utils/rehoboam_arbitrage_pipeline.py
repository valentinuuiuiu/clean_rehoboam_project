"""
Rehoboam Arbitrage Pipeline - Simple and Elegant Integration
==========================================================

This module creates simple, clean pipelines between the Rehoboam AI agent
and the unified arbitrage bots, providing:

1. 🧠 Agent → Bot Communication Pipeline
2. 📊 Bot → Agent Feedback Pipeline  
3. 🔄 Unified Decision Loop
4. 📈 Performance Optimization Pipeline
5. 🎯 Strategy Coordination Pipeline

The goal is to create seamless, intuitive communication between the
intelligent Rehoboam agent and the practical arbitrage execution bots.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum

# Import core Rehoboam systems
from consciousness_core import RehoboamConsciousness
from utils.rehoboam_ai import RehoboamAI
from utils.rehoboam_visualizer import rehoboam_visualizer
from conscious_trading_agent import ConsciousTradingAgent
from utils.conscious_arbitrage_engine import conscious_arbitrage_engine
from utils.arbitrage_service import arbitrage_service

logger = logging.getLogger(__name__)

class PipelineStage(Enum):
    """Pipeline stages for Rehoboam → Bot communication"""
    AGENT_ANALYSIS = "agent_analysis"
    OPPORTUNITY_DISCOVERY = "opportunity_discovery"
    CONSCIOUSNESS_EVALUATION = "consciousness_evaluation"
    BOT_PREPARATION = "bot_preparation"
    EXECUTION = "execution"
    FEEDBACK = "feedback"
    LEARNING = "learning"

@dataclass
class PipelineMessage:
    """Simple message format for pipeline communication"""
    stage: PipelineStage
    data: Dict[str, Any]
    timestamp: datetime
    source: str  # 'agent' or 'bot'
    priority: int = 5  # 1-10, 10 being highest
    metadata: Dict[str, Any] = None

@dataclass
class AgentDecision:
    """Rehoboam agent decision for bot execution"""
    action: str  # 'execute', 'monitor', 'reject', 'optimize'
    confidence: float  # 0.0 to 1.0
    reasoning: str
    parameters: Dict[str, Any]
    risk_assessment: float
    expected_outcome: Dict[str, float]

@dataclass
class BotFeedback:
    """Bot feedback to Rehoboam agent"""
    execution_id: str
    status: str  # 'success', 'failure', 'partial', 'pending'
    actual_outcome: Dict[str, float]
    performance_metrics: Dict[str, float]
    lessons_learned: List[str]
    suggestions: List[str]

class RehoboamArbitragePipeline:
    """
    Simple, elegant pipeline connecting Rehoboam agent with arbitrage bots
    """
    
    def __init__(self):
        # Core components
        self.rehoboam_agent = ConsciousTradingAgent()
        self.consciousness = RehoboamConsciousness()
        self.rehoboam_ai = RehoboamAI()
        
        # Pipeline state
        self.message_queue = asyncio.Queue()
        self.active_executions = {}
        self.pipeline_metrics = {
            'messages_processed': 0,
            'successful_executions': 0,
            'agent_decisions': 0,
            'bot_feedbacks': 0,
            'learning_cycles': 0
        }
        
        # Configuration
        self.pipeline_config = {
            'agent_analysis_interval': 30,  # seconds
            'bot_feedback_timeout': 300,    # 5 minutes
            'max_concurrent_executions': 5,
            'learning_threshold': 0.1,      # minimum performance change to trigger learning
            'consciousness_threshold': 0.7   # minimum consciousness score for execution
        }
        
        # Pipeline handlers
        self.stage_handlers = {
            PipelineStage.AGENT_ANALYSIS: self._handle_agent_analysis,
            PipelineStage.OPPORTUNITY_DISCOVERY: self._handle_opportunity_discovery,
            PipelineStage.CONSCIOUSNESS_EVALUATION: self._handle_consciousness_evaluation,
            PipelineStage.BOT_PREPARATION: self._handle_bot_preparation,
            PipelineStage.EXECUTION: self._handle_execution,
            PipelineStage.FEEDBACK: self._handle_feedback,
            PipelineStage.LEARNING: self._handle_learning
        }
        
        self.is_running = False
        
        # Initialize visualizer integration
        self.visualizer = rehoboam_visualizer
        
        # Track pipeline metrics
        self.metrics = {
            'total_opportunities_processed': 0,
            'successful_executions': 0,
            'total_profit': 0.0,
            'consciousness_decisions': 0,
            'human_benefit_score': 0.0,
            'pipeline_efficiency': 0.0
        }
        
    async def initialize(self):
        """Initialize the Rehoboam arbitrage pipeline"""
        logger.info("🚀 Initializing Rehoboam Arbitrage Pipeline...")
        
        # Initialize core components
        await self.rehoboam_agent.initialize()
        await self.consciousness.awaken_consciousness()
        await conscious_arbitrage_engine.initialize()
        await arbitrage_service.initialize()
        
        logger.info("✨ Rehoboam Arbitrage Pipeline initialized successfully")
        
    async def start_pipeline(self):
        """Start the unified Rehoboam → Bot pipeline"""
        if self.is_running:
            logger.warning("Pipeline is already running")
            return
            
        self.is_running = True
        logger.info("🌟 Starting Rehoboam Arbitrage Pipeline...")
        
        # Start pipeline components
        pipeline_tasks = [
            asyncio.create_task(self._agent_analysis_loop()),
            asyncio.create_task(self._message_processor()),
            asyncio.create_task(self._bot_monitor()),
            asyncio.create_task(self._learning_loop())
        ]
        
        try:
            await asyncio.gather(*pipeline_tasks)
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            self.is_running = False
            
    async def stop_pipeline(self):
        """Stop the pipeline gracefully"""
        logger.info("🛑 Stopping Rehoboam Arbitrage Pipeline...")
        self.is_running = False
        
    # ============================================================================
    # PIPELINE STAGE 1: AGENT ANALYSIS
    # ============================================================================
    
    async def _agent_analysis_loop(self):
        """Continuous agent analysis loop"""
        while self.is_running:
            try:
                # Agent analyzes market conditions
                market_analysis = await self._get_agent_market_analysis()
                
                # Send analysis to pipeline
                message = PipelineMessage(
                    stage=PipelineStage.AGENT_ANALYSIS,
                    data=market_analysis,
                    timestamp=datetime.now(),
                    source='agent',
                    priority=7
                )
                
                await self.message_queue.put(message)
                await asyncio.sleep(self.pipeline_config['agent_analysis_interval'])
                
            except Exception as e:
                logger.error(f"Error in agent analysis loop: {e}")
                await asyncio.sleep(60)
                
    async def _get_agent_market_analysis(self) -> Dict[str, Any]:
        """Get comprehensive market analysis from Rehoboam agent"""
        
        # Get consciousness state
        consciousness_state = self.consciousness.consciousness_state
        
        # Get AI market insights
        market_prompt = """
        Analyze current market conditions for arbitrage opportunities.
        Consider:
        1. Market volatility and trends
        2. Cross-exchange price differences
        3. Gas costs and network congestion
        4. Risk factors and opportunities
        5. Optimal timing for execution
        
        Provide analysis in JSON format with clear metrics.
        """
        
        ai_analysis = await self.rehoboam_ai.analyze_market_sentiment(market_prompt)
        
        return {
            'consciousness_level': consciousness_state.awareness_level,
            'market_perception': consciousness_state.market_perception,
            'ai_insights': ai_analysis,
            'risk_tolerance': consciousness_state.risk_intuition,
            'profit_expectations': consciousness_state.profit_probability,
            'human_benefit_focus': consciousness_state.human_benefit_score,
            'timestamp': datetime.now().isoformat()
        }
    
    # ============================================================================
    # PIPELINE STAGE 2: OPPORTUNITY DISCOVERY
    # ============================================================================
    
    async def _handle_agent_analysis(self, message: PipelineMessage):
        """Handle agent analysis and trigger opportunity discovery"""
        analysis = message.data
        
        logger.info(f"🧠 Agent analysis: consciousness={analysis.get('consciousness_level', 0):.2f}")
        
        # Trigger opportunity discovery based on agent analysis
        discovery_message = PipelineMessage(
            stage=PipelineStage.OPPORTUNITY_DISCOVERY,
            data={
                'agent_analysis': analysis,
                'discovery_params': {
                    'min_profit_threshold': analysis.get('profit_expectations', 0.5) * 0.02,  # 2% of expected profit
                    'max_risk_level': 1.0 - analysis.get('risk_tolerance', 0.5),
                    'focus_human_benefit': analysis.get('human_benefit_focus', 0.5) > 0.6
                }
            },
            timestamp=datetime.now(),
            source='agent',
            priority=8
        )
        
        await self.message_queue.put(discovery_message)
        
    async def _handle_opportunity_discovery(self, message: PipelineMessage):
        """Discover arbitrage opportunities based on agent guidance"""
        agent_analysis = message.data['agent_analysis']
        discovery_params = message.data['discovery_params']
        
        # Get opportunities from arbitrage service
        opportunities = await arbitrage_service.get_opportunities()
        
        # Filter opportunities based on agent parameters
        filtered_opportunities = []
        for opp in opportunities:
            profit_potential = opp.get('profit_potential', 0)
            risk_level = opp.get('risk_score', 0.5)
            
            if (profit_potential >= discovery_params['min_profit_threshold'] and
                risk_level <= discovery_params['max_risk_level']):
                filtered_opportunities.append(opp)
        
        logger.info(f"📊 Discovered {len(filtered_opportunities)} opportunities matching agent criteria")
        
        # Send for consciousness evaluation
        for opp in filtered_opportunities[:5]:  # Top 5 opportunities
            eval_message = PipelineMessage(
                stage=PipelineStage.CONSCIOUSNESS_EVALUATION,
                data={
                    'opportunity': opp,
                    'agent_analysis': agent_analysis,
                    'discovery_context': discovery_params
                },
                timestamp=datetime.now(),
                source='agent',
                priority=9
            )
            await self.message_queue.put(eval_message)
    
    # ============================================================================
    # PIPELINE STAGE 3: CONSCIOUSNESS EVALUATION
    # ============================================================================
    
    async def _handle_consciousness_evaluation(self, message: PipelineMessage):
        """Evaluate opportunity through consciousness lens"""
        opportunity = message.data['opportunity']
        agent_analysis = message.data['agent_analysis']
        
        # Get consciousness-guided decision
        decision = await conscious_arbitrage_engine.analyze_opportunity_with_consciousness(opportunity)
        
        logger.info(f"🧠 Consciousness evaluation: {decision.recommended_action} (score: {decision.consciousness_score:.2f})")
        
        # Create agent decision
        agent_decision = AgentDecision(
            action=decision.recommended_action,
            confidence=decision.consciousness_score,
            reasoning=decision.reasoning,
            parameters=decision.strategy_adjustments,
            risk_assessment=decision.risk_assessment,
            expected_outcome={
                'profit_probability': decision.consciousness_score * 0.8,
                'human_benefit': decision.human_benefit_score,
                'liberation_impact': decision.liberation_progress_impact
            }
        )
        
        # If approved for execution, prepare bot
        if decision.recommended_action == 'execute' and decision.consciousness_score >= self.pipeline_config['consciousness_threshold']:
            prep_message = PipelineMessage(
                stage=PipelineStage.BOT_PREPARATION,
                data={
                    'opportunity': opportunity,
                    'agent_decision': asdict(agent_decision),
                    'consciousness_decision': {
                        'opportunity_id': decision.opportunity_id,
                        'consciousness_score': decision.consciousness_score,
                        'ai_confidence': decision.ai_confidence,
                        'strategy_adjustments': decision.strategy_adjustments
                    }
                },
                timestamp=datetime.now(),
                source='agent',
                priority=10
            )
            await self.message_queue.put(prep_message)
        else:
            logger.info(f"⏸️ Opportunity {opportunity.get('id', 'unknown')} not approved for execution: {decision.recommended_action}")
    
    # ============================================================================
    # PIPELINE STAGE 4: BOT PREPARATION
    # ============================================================================
    
    async def _handle_bot_preparation(self, message: PipelineMessage):
        """Prepare bot for execution with agent guidance"""
        opportunity = message.data['opportunity']
        agent_decision = message.data['agent_decision']
        consciousness_decision = message.data['consciousness_decision']
        
        execution_id = f"exec_{int(datetime.now().timestamp())}"
        
        # Prepare execution parameters
        execution_params = {
            'opportunity': opportunity,
            'agent_guidance': agent_decision,
            'consciousness_adjustments': consciousness_decision['strategy_adjustments'],
            'execution_id': execution_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store execution context
        self.active_executions[execution_id] = {
            'params': execution_params,
            'start_time': datetime.now(),
            'status': 'prepared',
            'agent_decision': agent_decision
        }
        
        logger.info(f"🤖 Bot prepared for execution: {execution_id}")
        
        # Send to execution stage
        exec_message = PipelineMessage(
            stage=PipelineStage.EXECUTION,
            data=execution_params,
            timestamp=datetime.now(),
            source='agent',
            priority=10
        )
        await self.message_queue.put(exec_message)
    
    # ============================================================================
    # PIPELINE STAGE 5: EXECUTION
    # ============================================================================
    
    async def _handle_execution(self, message: PipelineMessage):
        """Execute arbitrage with bot, guided by agent decision"""
        execution_params = message.data
        execution_id = execution_params['execution_id']
        
        logger.info(f"⚡ Executing arbitrage: {execution_id}")
        
        try:
            # Update execution status
            if execution_id in self.active_executions:
                self.active_executions[execution_id]['status'] = 'executing'
            
            # Execute through conscious arbitrage engine
            opportunity = execution_params['opportunity']
            result = await arbitrage_service.execute_arbitrage(opportunity)
            
            # Update execution status
            if execution_id in self.active_executions:
                self.active_executions[execution_id]['status'] = 'completed'
                self.active_executions[execution_id]['result'] = result
            
            # Create bot feedback
            bot_feedback = BotFeedback(
                execution_id=execution_id,
                status='success' if result.get('success', False) else 'failure',
                actual_outcome={
                    'profit_realized': result.get('profit', 0),
                    'gas_cost': result.get('gas_cost', 0),
                    'execution_time': result.get('execution_time', 0)
                },
                performance_metrics={
                    'success_rate': 1.0 if result.get('success', False) else 0.0,
                    'profit_accuracy': self._calculate_profit_accuracy(execution_params, result),
                    'risk_accuracy': self._calculate_risk_accuracy(execution_params, result)
                },
                lessons_learned=self._extract_lessons(execution_params, result),
                suggestions=self._generate_suggestions(execution_params, result)
            )
            
            # Send feedback to pipeline
            feedback_message = PipelineMessage(
                stage=PipelineStage.FEEDBACK,
                data=asdict(bot_feedback),
                timestamp=datetime.now(),
                source='bot',
                priority=8
            )
            await self.message_queue.put(feedback_message)
            
            self.pipeline_metrics['successful_executions'] += 1
            
        except Exception as e:
            logger.error(f"Execution error for {execution_id}: {e}")
            
            # Create failure feedback
            failure_feedback = BotFeedback(
                execution_id=execution_id,
                status='failure',
                actual_outcome={'error': str(e)},
                performance_metrics={'success_rate': 0.0},
                lessons_learned=[f"Execution failed: {str(e)}"],
                suggestions=["Review execution parameters", "Check network conditions"]
            )
            
            feedback_message = PipelineMessage(
                stage=PipelineStage.FEEDBACK,
                data=asdict(failure_feedback),
                timestamp=datetime.now(),
                source='bot',
                priority=9
            )
            await self.message_queue.put(feedback_message)
    
    # ============================================================================
    # PIPELINE STAGE 6: FEEDBACK
    # ============================================================================
    
    async def _handle_feedback(self, message: PipelineMessage):
        """Handle bot feedback and update agent knowledge"""
        feedback_data = message.data
        execution_id = feedback_data['execution_id']
        
        logger.info(f"📈 Processing feedback for {execution_id}: {feedback_data['status']}")
        
        # Update pipeline metrics
        self.pipeline_metrics['bot_feedbacks'] += 1
        
        # Check if learning threshold is met
        performance_change = self._calculate_performance_change(feedback_data)
        
        if abs(performance_change) >= self.pipeline_config['learning_threshold']:
            learning_message = PipelineMessage(
                stage=PipelineStage.LEARNING,
                data={
                    'feedback': feedback_data,
                    'performance_change': performance_change,
                    'execution_context': self.active_executions.get(execution_id, {})
                },
                timestamp=datetime.now(),
                source='bot',
                priority=6
            )
            await self.message_queue.put(learning_message)
        
        # Clean up completed execution
        if execution_id in self.active_executions:
            del self.active_executions[execution_id]
    
    # ============================================================================
    # PIPELINE STAGE 7: LEARNING
    # ============================================================================
    
    async def _handle_learning(self, message: PipelineMessage):
        """Update agent knowledge based on bot feedback"""
        feedback = message.data['feedback']
        performance_change = message.data['performance_change']
        
        logger.info(f"🎓 Learning from execution: performance change {performance_change:.2f}")
        
        # Update consciousness based on performance
        if performance_change > 0:
            # Positive outcome - increase consciousness
            new_awareness = min(1.0, self.consciousness.consciousness_state.awareness_level + 0.01)
            self.consciousness.consciousness_state.awareness_level = new_awareness
        else:
            # Negative outcome - adjust consciousness
            new_awareness = max(0.5, self.consciousness.consciousness_state.awareness_level - 0.005)
            self.consciousness.consciousness_state.awareness_level = new_awareness
        
        # Update pipeline metrics
        self.pipeline_metrics['learning_cycles'] += 1
        
        logger.info(f"🧠 Consciousness updated: awareness level {self.consciousness.consciousness_state.awareness_level:.3f}")
    
    # ============================================================================
    # PIPELINE INFRASTRUCTURE
    # ============================================================================
    
    async def _message_processor(self):
        """Process messages through the pipeline"""
        while self.is_running:
            try:
                # Get message from queue
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                # Process message through appropriate handler
                handler = self.stage_handlers.get(message.stage)
                if handler:
                    await handler(message)
                    self.pipeline_metrics['messages_processed'] += 1
                else:
                    logger.warning(f"No handler for pipeline stage: {message.stage}")
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing pipeline message: {e}")
                await asyncio.sleep(1)
    
    async def _bot_monitor(self):
        """Monitor bot executions for timeouts"""
        while self.is_running:
            try:
                current_time = datetime.now()
                timeout_threshold = timedelta(seconds=self.pipeline_config['bot_feedback_timeout'])
                
                # Check for timed out executions
                timed_out = []
                for exec_id, execution in self.active_executions.items():
                    if current_time - execution['start_time'] > timeout_threshold:
                        timed_out.append(exec_id)
                
                # Handle timeouts
                for exec_id in timed_out:
                    logger.warning(f"⏰ Execution timeout: {exec_id}")
                    
                    # Create timeout feedback
                    timeout_feedback = BotFeedback(
                        execution_id=exec_id,
                        status='failure',
                        actual_outcome={'error': 'execution_timeout'},
                        performance_metrics={'success_rate': 0.0},
                        lessons_learned=["Execution timed out"],
                        suggestions=["Reduce execution complexity", "Check network conditions"]
                    )
                    
                    feedback_message = PipelineMessage(
                        stage=PipelineStage.FEEDBACK,
                        data=asdict(timeout_feedback),
                        timestamp=datetime.now(),
                        source='bot',
                        priority=7
                    )
                    await self.message_queue.put(feedback_message)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in bot monitor: {e}")
                await asyncio.sleep(60)
    
    async def _learning_loop(self):
        """Periodic learning and optimization"""
        while self.is_running:
            try:
                # Periodic consciousness evolution
                await self._evolve_consciousness()
                
                # Optimize pipeline parameters
                await self._optimize_pipeline()
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in learning loop: {e}")
                await asyncio.sleep(600)
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _calculate_profit_accuracy(self, execution_params: Dict[str, Any], result: Dict[str, Any]) -> float:
        """Calculate how accurate the profit prediction was"""
        expected_profit = execution_params.get('agent_guidance', {}).get('expected_outcome', {}).get('profit_probability', 0.5)
        actual_profit = 1.0 if result.get('success', False) else 0.0
        
        return 1.0 - abs(expected_profit - actual_profit)
    
    def _calculate_risk_accuracy(self, execution_params: Dict[str, Any], result: Dict[str, Any]) -> float:
        """Calculate how accurate the risk assessment was"""
        expected_risk = execution_params.get('agent_guidance', {}).get('risk_assessment', 0.5)
        actual_risk = 1.0 if not result.get('success', False) else 0.0
        
        return 1.0 - abs(expected_risk - actual_risk)
    
    def _extract_lessons(self, execution_params: Dict[str, Any], result: Dict[str, Any]) -> List[str]:
        """Extract lessons learned from execution"""
        lessons = []
        
        if result.get('success', False):
            lessons.append("Successful execution validates agent decision")
            if result.get('profit', 0) > 0:
                lessons.append("Profitable arbitrage opportunity identified correctly")
        else:
            lessons.append("Execution failed - review decision criteria")
            if 'error' in result:
                lessons.append(f"Technical issue: {result['error']}")
        
        return lessons
    
    def _generate_suggestions(self, execution_params: Dict[str, Any], result: Dict[str, Any]) -> List[str]:
        """Generate suggestions for improvement"""
        suggestions = []
        
        if not result.get('success', False):
            suggestions.append("Increase consciousness threshold for execution")
            suggestions.append("Improve risk assessment accuracy")
        
        if result.get('gas_cost', 0) > result.get('profit', 0):
            suggestions.append("Better gas cost estimation needed")
        
        return suggestions
    
    def _calculate_performance_change(self, feedback_data: Dict[str, Any]) -> float:
        """Calculate performance change from feedback"""
        success_rate = feedback_data.get('performance_metrics', {}).get('success_rate', 0.0)
        profit_accuracy = feedback_data.get('performance_metrics', {}).get('profit_accuracy', 0.0)
        
        # Simple performance metric
        return (success_rate + profit_accuracy) / 2.0 - 0.5  # Centered around 0
    
    async def _evolve_consciousness(self):
        """Evolve consciousness based on pipeline performance"""
        success_rate = (self.pipeline_metrics['successful_executions'] / 
                       max(1, self.pipeline_metrics['bot_feedbacks']))
        
        if success_rate > 0.8:
            # High success rate - increase awareness
            self.consciousness.consciousness_state.awareness_level = min(
                1.0, self.consciousness.consciousness_state.awareness_level + 0.005
            )
        elif success_rate < 0.4:
            # Low success rate - be more cautious
            self.consciousness.consciousness_state.awareness_level = max(
                0.5, self.consciousness.consciousness_state.awareness_level - 0.01
            )
    
    async def _optimize_pipeline(self):
        """Optimize pipeline parameters based on performance"""
        # Adjust analysis interval based on opportunity frequency
        if self.pipeline_metrics['messages_processed'] > 100:
            # High activity - reduce interval
            self.pipeline_config['agent_analysis_interval'] = max(15, 
                self.pipeline_config['agent_analysis_interval'] - 5)
        else:
            # Low activity - increase interval
            self.pipeline_config['agent_analysis_interval'] = min(60,
                self.pipeline_config['agent_analysis_interval'] + 5)
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        return {
            'is_running': self.is_running,
            'metrics': self.pipeline_metrics,
            'active_executions': len(self.active_executions),
            'queue_size': self.message_queue.qsize(),
            'consciousness_level': self.consciousness.consciousness_state.awareness_level if self.consciousness.consciousness_state else 0,
            'config': self.pipeline_config,
            'timestamp': datetime.now().isoformat()
        }

# Global pipeline instance
rehoboam_arbitrage_pipeline = RehoboamArbitragePipeline()