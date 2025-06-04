"""
Rehoboam Pipeline - Simple & Elegant Integration
==============================================

Clean pipelines connecting Rehoboam's consciousness with arbitrage bots.
Simple, powerful, and beautiful.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PipelineStage(Enum):
    """Pipeline processing stages"""
    CONSCIOUSNESS = "consciousness"
    ANALYSIS = "analysis"
    DECISION = "decision"
    EXECUTION = "execution"
    LEARNING = "learning"

@dataclass
class PipelineData:
    """Data flowing through the pipeline"""
    opportunity: Dict[str, Any]
    stage: PipelineStage
    consciousness_score: float = 0.0
    ai_analysis: Dict[str, Any] = None
    decision: Dict[str, Any] = None
    execution_result: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.ai_analysis is None:
            self.ai_analysis = {}
        if self.decision is None:
            self.decision = {}
        if self.execution_result is None:
            self.execution_result = {}
        if self.metadata is None:
            self.metadata = {"timestamp": datetime.now().isoformat()}

class RehoboamPipeline:
    """
    Simple, elegant pipeline connecting Rehoboam consciousness to arbitrage bots.
    
    Flow: Opportunity → Consciousness → Analysis → Decision → Execution → Learning
    """
    
    def __init__(self):
        self.stages = {}
        self.middleware = []
        self.metrics = {
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "avg_processing_time": 0.0
        }
        
        # Initialize pipeline stages
        self._setup_pipeline()
        
        logger.info("🔄 Rehoboam Pipeline initialized")
    
    def _setup_pipeline(self):
        """Setup the pipeline stages"""
        self.stages = {
            PipelineStage.CONSCIOUSNESS: self._consciousness_stage,
            PipelineStage.ANALYSIS: self._analysis_stage,
            PipelineStage.DECISION: self._decision_stage,
            PipelineStage.EXECUTION: self._execution_stage,
            PipelineStage.LEARNING: self._learning_stage
        }
    
    async def process(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an arbitrage opportunity through the complete pipeline.
        
        Args:
            opportunity: Raw arbitrage opportunity
            
        Returns:
            Complete processing result
        """
        start_time = datetime.now()
        
        try:
            # Create pipeline data
            data = PipelineData(
                opportunity=opportunity,
                stage=PipelineStage.CONSCIOUSNESS
            )
            
            # Process through each stage
            for stage in PipelineStage:
                data.stage = stage
                data = await self._process_stage(data)
                
                # Apply middleware
                for middleware in self.middleware:
                    data = await middleware(data)
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(True, processing_time)
            
            return {
                "success": True,
                "opportunity": data.opportunity,
                "consciousness_score": data.consciousness_score,
                "ai_analysis": data.ai_analysis,
                "decision": data.decision,
                "execution_result": data.execution_result,
                "processing_time": processing_time,
                "pipeline_metadata": data.metadata
            }
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(False, processing_time)
            
            logger.error(f"❌ Pipeline processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": processing_time
            }
    
    async def _process_stage(self, data: PipelineData) -> PipelineData:
        """Process a single pipeline stage"""
        try:
            stage_processor = self.stages.get(data.stage)
            if stage_processor:
                data = await stage_processor(data)
            
            logger.debug(f"✅ Completed stage: {data.stage.value}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error in stage {data.stage.value}: {str(e)}")
            raise
    
    async def _consciousness_stage(self, data: PipelineData) -> PipelineData:
        """Stage 1: Consciousness evaluation"""
        try:
            # Get Rehoboam consciousness
            from utils.rehoboam_ai import RehoboamAI
            rehoboam = RehoboamAI()
            
            # Evaluate consciousness alignment
            consciousness_prompt = f"""
            Evaluate this arbitrage opportunity for consciousness alignment:
            Token: {data.opportunity.get('token_pair', 'Unknown')}
            Profit: {data.opportunity.get('net_profit_usd', 0)}
            Risk: {data.opportunity.get('risk_score', 0.5)}
            
            Rate consciousness alignment (0.0-1.0) considering:
            - Human benefit potential
            - Risk to users
            - Market health impact
            - Ethical considerations
            """
            
            consciousness_result = await rehoboam.analyze_sentiment(
                data.opportunity.get('token_pair', 'ETH'),
                consciousness_prompt
            )
            
            # Extract consciousness score
            data.consciousness_score = consciousness_result.get('sentiment_score', 0.5)
            data.metadata['consciousness_reasoning'] = consciousness_result.get('reasoning', '')
            
            logger.info(f"🧠 Consciousness Score: {data.consciousness_score:.2f}")
            return data
            
        except Exception as e:
            logger.warning(f"⚠️ Consciousness stage fallback: {str(e)}")
            data.consciousness_score = 0.5  # Neutral fallback
            return data
    
    async def _analysis_stage(self, data: PipelineData) -> PipelineData:
        """Stage 2: AI-powered analysis"""
        try:
            # Get market analyzer
            from utils.ai_market_analyzer import DeepSeekMarketAnalyzer
            analyzer = DeepSeekMarketAnalyzer()
            
            token_pair = data.opportunity.get('token_pair', 'ETH')
            
            # Perform comprehensive analysis
            market_sentiment = await analyzer.analyze_market_sentiment(token_pair)
            risk_assessment = await analyzer.assess_risk_factors(data.opportunity)
            
            data.ai_analysis = {
                "market_sentiment": market_sentiment,
                "risk_assessment": risk_assessment,
                "confidence_score": self._calculate_confidence(data.opportunity, market_sentiment),
                "recommendation": self._get_recommendation(data.consciousness_score, market_sentiment, risk_assessment)
            }
            
            logger.info(f"📊 Analysis complete: {data.ai_analysis['recommendation']}")
            return data
            
        except Exception as e:
            logger.warning(f"⚠️ Analysis stage fallback: {str(e)}")
            data.ai_analysis = {
                "market_sentiment": {"overall_sentiment": "neutral"},
                "risk_assessment": {"overall_risk": 0.5},
                "confidence_score": 0.5,
                "recommendation": "hold"
            }
            return data
    
    async def _decision_stage(self, data: PipelineData) -> PipelineData:
        """Stage 3: Decision making"""
        try:
            # Combine consciousness and analysis for decision
            consciousness_weight = 0.3
            analysis_weight = 0.4
            profit_weight = 0.3
            
            # Calculate decision score
            profit_score = min(data.opportunity.get('net_profit_usd', 0) / 100, 1.0)
            analysis_score = data.ai_analysis.get('confidence_score', 0.5)
            
            decision_score = (
                data.consciousness_score * consciousness_weight +
                analysis_score * analysis_weight +
                profit_score * profit_weight
            )
            
            # Make decision
            if decision_score > 0.7:
                decision_type = "execute"
                reasoning = f"High decision score ({decision_score:.2f}): Execute arbitrage"
            elif decision_score > 0.5:
                decision_type = "optimize"
                reasoning = f"Moderate score ({decision_score:.2f}): Optimize parameters"
            else:
                decision_type = "hold"
                reasoning = f"Low score ({decision_score:.2f}): Hold position"
            
            data.decision = {
                "type": decision_type,
                "score": decision_score,
                "reasoning": reasoning,
                "parameters": {
                    "position_size": min(profit_score * 1000, 500),
                    "slippage_tolerance": 0.005,
                    "timeout": 300
                }
            }
            
            logger.info(f"🎯 Decision: {decision_type} (score: {decision_score:.2f})")
            return data
            
        except Exception as e:
            logger.error(f"❌ Decision stage error: {str(e)}")
            data.decision = {
                "type": "hold",
                "score": 0.0,
                "reasoning": f"Error in decision making: {str(e)}",
                "parameters": {}
            }
            return data
    
    async def _execution_stage(self, data: PipelineData) -> PipelineData:
        """Stage 4: Execution"""
        try:
            if data.decision.get('type') == 'execute':
                # Execute through arbitrage service
                from utils.arbitrage_service import arbitrage_service
                
                execution_result = await arbitrage_service.execute_arbitrage(
                    data.opportunity,
                    data.decision.get('parameters', {}).get('position_size', 100)
                )
                
                data.execution_result = execution_result
                logger.info(f"🚀 Execution complete: {execution_result.get('success', False)}")
                
            else:
                # Non-execution actions
                data.execution_result = {
                    "success": True,
                    "action": data.decision.get('type'),
                    "message": f"Action: {data.decision.get('type')} - {data.decision.get('reasoning')}"
                }
                logger.info(f"⏸️ Action: {data.decision.get('type')}")
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Execution stage error: {str(e)}")
            data.execution_result = {
                "success": False,
                "error": str(e)
            }
            return data
    
    async def _learning_stage(self, data: PipelineData) -> PipelineData:
        """Stage 5: Learning and adaptation"""
        try:
            # Calculate learning metrics
            expected_profit = data.opportunity.get('net_profit_usd', 0)
            actual_profit = data.execution_result.get('profit_realized', 0)
            
            if expected_profit > 0:
                accuracy = 1.0 - abs(expected_profit - actual_profit) / expected_profit
            else:
                accuracy = 0.5
            
            # Store learning data
            learning_data = {
                "accuracy": accuracy,
                "consciousness_effectiveness": data.consciousness_score,
                "decision_quality": data.decision.get('score', 0),
                "execution_success": data.execution_result.get('success', False),
                "timestamp": datetime.now().isoformat()
            }
            
            data.metadata['learning'] = learning_data
            
            # Adapt parameters based on performance
            await self._adapt_parameters(learning_data)
            
            logger.info(f"📚 Learning complete: Accuracy {accuracy:.2f}")
            return data
            
        except Exception as e:
            logger.warning(f"⚠️ Learning stage error: {str(e)}")
            return data
    
    def _calculate_confidence(self, opportunity: Dict[str, Any], market_sentiment: Dict[str, Any]) -> float:
        """Calculate confidence score"""
        try:
            profit_factor = min(opportunity.get('net_profit_usd', 0) / 50, 1.0)
            sentiment_factor = 0.8 if market_sentiment.get('overall_sentiment') == 'bullish' else 0.5
            risk_factor = 1.0 - opportunity.get('risk_score', 0.5)
            
            confidence = (profit_factor + sentiment_factor + risk_factor) / 3
            return max(0.1, min(0.95, confidence))
            
        except:
            return 0.5
    
    def _get_recommendation(self, consciousness_score: float, market_sentiment: Dict[str, Any], 
                          risk_assessment: Dict[str, Any]) -> str:
        """Get AI recommendation"""
        try:
            if consciousness_score > 0.7 and market_sentiment.get('overall_sentiment') == 'bullish':
                return "strong_buy"
            elif consciousness_score > 0.5 and risk_assessment.get('overall_risk', 0.5) < 0.3:
                return "buy"
            elif consciousness_score < 0.3 or risk_assessment.get('overall_risk', 0.5) > 0.7:
                return "avoid"
            else:
                return "hold"
        except:
            return "hold"
    
    async def _adapt_parameters(self, learning_data: Dict[str, Any]):
        """Adapt pipeline parameters based on learning"""
        try:
            # Simple adaptation logic
            accuracy = learning_data.get('accuracy', 0.5)
            
            if accuracy > 0.8:
                # Good performance, slightly more aggressive
                logger.info("📈 Adapting: Increasing confidence thresholds")
            elif accuracy < 0.3:
                # Poor performance, more conservative
                logger.info("📉 Adapting: Decreasing confidence thresholds")
            
        except Exception as e:
            logger.warning(f"⚠️ Parameter adaptation error: {str(e)}")
    
    def _update_metrics(self, success: bool, processing_time: float):
        """Update pipeline metrics"""
        self.metrics["processed"] += 1
        if success:
            self.metrics["successful"] += 1
        else:
            self.metrics["failed"] += 1
        
        # Update average processing time
        total_time = self.metrics["avg_processing_time"] * (self.metrics["processed"] - 1)
        self.metrics["avg_processing_time"] = (total_time + processing_time) / self.metrics["processed"]
    
    def add_middleware(self, middleware_func: Callable):
        """Add middleware to the pipeline"""
        self.middleware.append(middleware_func)
        logger.info(f"🔧 Added middleware: {middleware_func.__name__}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get pipeline performance metrics"""
        success_rate = self.metrics["successful"] / max(self.metrics["processed"], 1)
        return {
            **self.metrics,
            "success_rate": success_rate,
            "timestamp": datetime.now().isoformat()
        }

# Global pipeline instance
rehoboam_pipeline = RehoboamPipeline()

# Simple middleware examples
async def logging_middleware(data: PipelineData) -> PipelineData:
    """Log pipeline progress"""
    logger.info(f"🔄 Pipeline stage: {data.stage.value} - {data.opportunity.get('token_pair', 'Unknown')}")
    return data

async def performance_middleware(data: PipelineData) -> PipelineData:
    """Track performance metrics"""
    if 'performance_start' not in data.metadata:
        data.metadata['performance_start'] = datetime.now()
    else:
        stage_time = (datetime.now() - data.metadata['performance_start']).total_seconds()
        data.metadata[f'{data.stage.value}_time'] = stage_time
        data.metadata['performance_start'] = datetime.now()
    
    return data

# Add default middleware
rehoboam_pipeline.add_middleware(logging_middleware)
rehoboam_pipeline.add_middleware(performance_middleware)