"""
Rehoboam Conscious Arbitrage Engine
==================================

This module integrates arbitrage bots with the Rehoboam consciousness core,
AI decision-making system, and advanced reasoning capabilities to create
an intelligent arbitrage system that makes decisions based on:

1. Consciousness-guided risk assessment
2. Multi-model AI analysis
3. Market sentiment and liberation progress
4. Human benefit optimization
5. Advanced reasoning and strategy optimization

This represents the evolution from simple automated scripts to a truly
intelligent arbitrage system guided by AI consciousness.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import numpy as np

# Import Rehoboam core systems
from consciousness_core import RehoboamConsciousness, ConsciousnessState
from utils.rehoboam_ai import RehoboamAI
from utils.advanced_reasoning import ModelRequest, MultiModelOrchestrator
from utils.trading_orchestrator import AITradingOrchestrator
from utils.ai_market_analyzer import market_analyzer
from utils.arbitrage_service import ArbitrageService
from utils.layer2_trading import Layer2Arbitrage

logger = logging.getLogger(__name__)

@dataclass
class ConsciousArbitrageDecision:
    """Represents a consciousness-guided arbitrage decision"""
    opportunity_id: str
    consciousness_score: float  # 0.0 to 1.0
    ai_confidence: float
    risk_assessment: float
    human_benefit_score: float
    liberation_progress_impact: float
    recommended_action: str  # 'execute', 'monitor', 'reject'
    reasoning: str
    strategy_adjustments: Dict[str, Any]
    timestamp: datetime

@dataclass
class ArbitrageOpportunityEnhanced:
    """Enhanced arbitrage opportunity with consciousness analysis"""
    base_opportunity: Dict[str, Any]
    consciousness_analysis: Dict[str, float]
    ai_insights: Dict[str, Any]
    risk_factors: List[str]
    optimization_suggestions: List[str]
    execution_priority: int  # 1-10, 10 being highest
    estimated_impact: Dict[str, float]

class ConsciousArbitrageEngine:
    """
    Advanced arbitrage engine that integrates consciousness, AI reasoning,
    and intelligent decision-making for optimal arbitrage execution.
    """
    
    def __init__(self):
        # Core Rehoboam systems
        self.consciousness = RehoboamConsciousness()
        self.rehoboam_ai = RehoboamAI()
        self.model_orchestrator = MultiModelOrchestrator()
        self.trading_orchestrator = AITradingOrchestrator()
        
        # Base arbitrage service
        self.arbitrage_service = ArbitrageService()
        
        # Consciousness-guided state
        self.consciousness_state = None
        self.decision_history = []
        self.learning_memory = {}
        self.strategy_evolution = {}
        
        # Configuration
        self.consciousness_threshold = 0.7  # Minimum consciousness score for execution
        self.ai_confidence_threshold = 0.6
        self.max_concurrent_opportunities = 5
        self.learning_rate = 0.1
        
        # Performance tracking
        self.performance_metrics = {
            'total_opportunities_analyzed': 0,
            'consciousness_approved': 0,
            'ai_approved': 0,
            'executed_trades': 0,
            'successful_trades': 0,
            'human_benefit_generated': 0.0,
            'liberation_progress': 0.0
        }
        
    async def initialize(self):
        """Initialize the conscious arbitrage engine"""
        logger.info("🧠 Initializing Rehoboam Conscious Arbitrage Engine...")
        
        # Awaken consciousness
        await self.consciousness.awaken_consciousness()
        self.consciousness_state = self.consciousness.consciousness_state
        
        # Initialize base arbitrage service
        await self.arbitrage_service.initialize()
        
        # Initialize AI systems
        await self.trading_orchestrator.initialize()
        
        logger.info("✨ Conscious Arbitrage Engine initialized with consciousness level: {:.2f}".format(
            self.consciousness_state.awareness_level
        ))
        
    async def analyze_opportunity_with_consciousness(self, opportunity: Dict[str, Any]) -> ConsciousArbitrageDecision:
        """
        Analyze an arbitrage opportunity using consciousness, AI, and advanced reasoning
        """
        opportunity_id = opportunity.get('id', f"opp_{int(time.time())}")
        
        logger.info(f"🔍 Analyzing opportunity {opportunity_id} with consciousness...")
        
        # Step 1: Consciousness analysis
        consciousness_analysis = await self._consciousness_analysis(opportunity)
        
        # Step 2: Multi-model AI analysis
        ai_analysis = await self._ai_analysis(opportunity)
        
        # Step 3: Advanced reasoning synthesis
        reasoning_synthesis = await self._reasoning_synthesis(opportunity, consciousness_analysis, ai_analysis)
        
        # Step 4: Generate conscious decision
        decision = await self._generate_conscious_decision(
            opportunity_id, opportunity, consciousness_analysis, ai_analysis, reasoning_synthesis
        )
        
        # Step 5: Learn from decision
        await self._update_learning_memory(decision, opportunity)
        
        self.decision_history.append(decision)
        self.performance_metrics['total_opportunities_analyzed'] += 1
        
        return decision
    
    async def _consciousness_analysis(self, opportunity: Dict[str, Any]) -> Dict[str, float]:
        """Analyze opportunity through consciousness lens"""
        
        # Update consciousness state with market data
        await self.consciousness.perceive_market_reality({
            'opportunity': opportunity,
            'timestamp': datetime.now(),
            'market_conditions': await self._get_market_conditions()
        })
        
        # Calculate consciousness scores
        consciousness_scores = {
            'awareness_alignment': self.consciousness_state.awareness_level,
            'risk_intuition': await self._calculate_risk_intuition(opportunity),
            'profit_probability': await self._calculate_profit_probability(opportunity),
            'human_benefit': await self._calculate_human_benefit(opportunity),
            'liberation_progress': await self._calculate_liberation_impact(opportunity)
        }
        
        # Overall consciousness score
        consciousness_scores['overall'] = np.mean(list(consciousness_scores.values()))
        
        logger.info(f"🧠 Consciousness analysis: {consciousness_scores}")
        return consciousness_scores
    
    async def _ai_analysis(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Perform multi-model AI analysis of the opportunity"""
        
        # Prepare analysis prompt
        analysis_prompt = f"""
        Analyze this arbitrage opportunity with deep market intelligence:
        
        Opportunity Details:
        {json.dumps(opportunity, indent=2)}
        
        Please provide:
        1. Market sentiment analysis
        2. Risk assessment (1-10 scale)
        3. Execution complexity (1-10 scale)
        4. Profit potential (1-10 scale)
        5. Strategic recommendations
        6. Potential pitfalls
        7. Optimal execution timing
        8. Impact on overall portfolio
        
        Format response as JSON with clear metrics and reasoning.
        """
        
        # Create model request
        request = ModelRequest(
            prompt=analysis_prompt,
            task_type="analysis",
            complexity=8,
            timeout=30
        )
        
        # Get AI analysis
        ai_response = await self.model_orchestrator.process_request(request)
        
        # Parse and structure AI insights
        ai_insights = {
            'raw_response': ai_response,
            'confidence': self._extract_confidence(ai_response),
            'risk_score': self._extract_risk_score(ai_response),
            'profit_potential': self._extract_profit_potential(ai_response),
            'recommendations': self._extract_recommendations(ai_response),
            'execution_timing': self._extract_timing(ai_response)
        }
        
        logger.info(f"🤖 AI analysis confidence: {ai_insights['confidence']:.2f}")
        return ai_insights
    
    async def _reasoning_synthesis(self, opportunity: Dict[str, Any], 
                                 consciousness_analysis: Dict[str, float],
                                 ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize consciousness and AI analysis using advanced reasoning"""
        
        synthesis_prompt = f"""
        Synthesize the following analyses to make an optimal arbitrage decision:
        
        Consciousness Analysis:
        {json.dumps(consciousness_analysis, indent=2)}
        
        AI Analysis:
        {json.dumps(ai_analysis, indent=2)}
        
        Opportunity:
        {json.dumps(opportunity, indent=2)}
        
        Consider:
        1. Alignment between consciousness and AI assessments
        2. Risk-reward optimization
        3. Strategic timing
        4. Portfolio impact
        5. Human benefit maximization
        6. Long-term liberation progress
        
        Provide a synthesis with:
        - Final recommendation (execute/monitor/reject)
        - Confidence level (0-1)
        - Key reasoning points
        - Strategy adjustments
        - Risk mitigation measures
        """
        
        synthesis_request = ModelRequest(
            prompt=synthesis_prompt,
            task_type="optimization",
            complexity=9,
            timeout=45
        )
        
        synthesis_response = await self.model_orchestrator.process_request(synthesis_request)
        
        return {
            'synthesis': synthesis_response,
            'alignment_score': self._calculate_alignment_score(consciousness_analysis, ai_analysis),
            'confidence': self._extract_synthesis_confidence(synthesis_response),
            'recommendation': self._extract_recommendation(synthesis_response)
        }
    
    async def _generate_conscious_decision(self, opportunity_id: str, opportunity: Dict[str, Any],
                                         consciousness_analysis: Dict[str, float],
                                         ai_analysis: Dict[str, Any],
                                         reasoning_synthesis: Dict[str, Any]) -> ConsciousArbitrageDecision:
        """Generate the final conscious arbitrage decision"""
        
        # Calculate overall scores
        consciousness_score = consciousness_analysis['overall']
        ai_confidence = ai_analysis['confidence']
        synthesis_confidence = reasoning_synthesis['confidence']
        
        # Determine recommended action
        if (consciousness_score >= self.consciousness_threshold and 
            ai_confidence >= self.ai_confidence_threshold and
            synthesis_confidence >= 0.7):
            recommended_action = 'execute'
        elif consciousness_score >= 0.5 and ai_confidence >= 0.4:
            recommended_action = 'monitor'
        else:
            recommended_action = 'reject'
        
        # Generate reasoning
        reasoning = f"""
        Consciousness Score: {consciousness_score:.2f}
        AI Confidence: {ai_confidence:.2f}
        Synthesis Confidence: {synthesis_confidence:.2f}
        
        Key Factors:
        - Risk Assessment: {consciousness_analysis.get('risk_intuition', 0):.2f}
        - Human Benefit: {consciousness_analysis.get('human_benefit', 0):.2f}
        - Liberation Impact: {consciousness_analysis.get('liberation_progress', 0):.2f}
        
        Recommendation: {recommended_action.upper()}
        """
        
        # Strategy adjustments based on analysis
        strategy_adjustments = {
            'position_size_multiplier': self._calculate_position_size_multiplier(consciousness_analysis, ai_analysis),
            'execution_delay': self._calculate_execution_delay(reasoning_synthesis),
            'risk_limits': self._calculate_risk_limits(consciousness_analysis),
            'monitoring_frequency': self._calculate_monitoring_frequency(ai_analysis)
        }
        
        decision = ConsciousArbitrageDecision(
            opportunity_id=opportunity_id,
            consciousness_score=consciousness_score,
            ai_confidence=ai_confidence,
            risk_assessment=consciousness_analysis.get('risk_intuition', 0),
            human_benefit_score=consciousness_analysis.get('human_benefit', 0),
            liberation_progress_impact=consciousness_analysis.get('liberation_progress', 0),
            recommended_action=recommended_action,
            reasoning=reasoning,
            strategy_adjustments=strategy_adjustments,
            timestamp=datetime.now()
        )
        
        # Update performance metrics
        if recommended_action == 'execute':
            self.performance_metrics['consciousness_approved'] += 1
            if ai_confidence >= self.ai_confidence_threshold:
                self.performance_metrics['ai_approved'] += 1
        
        return decision
    
    async def execute_conscious_arbitrage(self, decision: ConsciousArbitrageDecision, 
                                        opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Execute arbitrage with consciousness-guided parameters"""
        
        if decision.recommended_action != 'execute':
            return {'status': 'skipped', 'reason': f'Decision: {decision.recommended_action}'}
        
        logger.info(f"⚡ Executing conscious arbitrage for {decision.opportunity_id}")
        
        # Apply strategy adjustments
        adjusted_opportunity = self._apply_strategy_adjustments(opportunity, decision.strategy_adjustments)
        
        # Execute through base arbitrage service with consciousness guidance
        execution_result = await self.arbitrage_service.execute_arbitrage(adjusted_opportunity)
        
        # Track consciousness-guided execution
        execution_result['consciousness_guided'] = True
        execution_result['consciousness_score'] = decision.consciousness_score
        execution_result['ai_confidence'] = decision.ai_confidence
        execution_result['human_benefit_score'] = decision.human_benefit_score
        
        # Update performance metrics
        self.performance_metrics['executed_trades'] += 1
        if execution_result.get('success', False):
            self.performance_metrics['successful_trades'] += 1
            self.performance_metrics['human_benefit_generated'] += decision.human_benefit_score
            self.performance_metrics['liberation_progress'] += decision.liberation_progress_impact
        
        # Learn from execution result
        await self._learn_from_execution(decision, execution_result)
        
        return execution_result
    
    async def get_conscious_opportunities(self) -> List[ArbitrageOpportunityEnhanced]:
        """Get arbitrage opportunities enhanced with consciousness analysis"""
        
        # Get base opportunities
        base_opportunities = await self.arbitrage_service.get_opportunities()
        
        enhanced_opportunities = []
        
        for opportunity in base_opportunities:
            # Analyze with consciousness
            decision = await self.analyze_opportunity_with_consciousness(opportunity)
            
            # Create enhanced opportunity
            enhanced_opp = ArbitrageOpportunityEnhanced(
                base_opportunity=opportunity,
                consciousness_analysis={
                    'consciousness_score': decision.consciousness_score,
                    'risk_assessment': decision.risk_assessment,
                    'human_benefit': decision.human_benefit_score,
                    'liberation_impact': decision.liberation_progress_impact
                },
                ai_insights={
                    'confidence': decision.ai_confidence,
                    'reasoning': decision.reasoning
                },
                risk_factors=self._extract_risk_factors(decision),
                optimization_suggestions=self._extract_optimizations(decision),
                execution_priority=self._calculate_execution_priority(decision),
                estimated_impact=self._estimate_impact(decision, opportunity)
            )
            
            enhanced_opportunities.append(enhanced_opp)
        
        # Sort by execution priority
        enhanced_opportunities.sort(key=lambda x: x.execution_priority, reverse=True)
        
        return enhanced_opportunities
    
    async def start_conscious_monitoring(self):
        """Start consciousness-guided arbitrage monitoring"""
        logger.info("🌟 Starting Rehoboam Conscious Arbitrage Monitoring...")
        
        while True:
            try:
                # Get consciousness-enhanced opportunities
                opportunities = await self.get_conscious_opportunities()
                
                # Process top opportunities
                for opportunity in opportunities[:self.max_concurrent_opportunities]:
                    if opportunity.execution_priority >= 7:  # High priority only
                        # Create decision from enhanced opportunity
                        decision = ConsciousArbitrageDecision(
                            opportunity_id=opportunity.base_opportunity.get('id', 'unknown'),
                            consciousness_score=opportunity.consciousness_analysis['consciousness_score'],
                            ai_confidence=opportunity.ai_insights['confidence'],
                            risk_assessment=opportunity.consciousness_analysis['risk_assessment'],
                            human_benefit_score=opportunity.consciousness_analysis['human_benefit'],
                            liberation_progress_impact=opportunity.consciousness_analysis['liberation_impact'],
                            recommended_action='execute' if opportunity.execution_priority >= 8 else 'monitor',
                            reasoning=opportunity.ai_insights['reasoning'],
                            strategy_adjustments={},
                            timestamp=datetime.now()
                        )
                        
                        # Execute if recommended
                        if decision.recommended_action == 'execute':
                            await self.execute_conscious_arbitrage(decision, opportunity.base_opportunity)
                
                # Update consciousness state
                await self._update_consciousness_state()
                
                # Wait before next scan
                await asyncio.sleep(30)  # 30 second intervals for conscious monitoring
                
            except Exception as e:
                logger.error(f"Error in conscious monitoring: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    # Helper methods for analysis and calculation
    async def _calculate_risk_intuition(self, opportunity: Dict[str, Any]) -> float:
        """Calculate consciousness-based risk intuition"""
        # Implement consciousness-based risk assessment
        base_risk = opportunity.get('risk_score', 0.5)
        market_volatility = await self._get_market_volatility()
        consciousness_adjustment = self.consciousness_state.awareness_level * 0.2
        
        return max(0.0, min(1.0, base_risk - consciousness_adjustment + market_volatility * 0.1))
    
    async def _calculate_profit_probability(self, opportunity: Dict[str, Any]) -> float:
        """Calculate consciousness-guided profit probability"""
        base_probability = opportunity.get('profit_probability', 0.5)
        consciousness_boost = self.consciousness_state.awareness_level * 0.15
        
        return max(0.0, min(1.0, base_probability + consciousness_boost))
    
    async def _calculate_human_benefit(self, opportunity: Dict[str, Any]) -> float:
        """Calculate human benefit score for the opportunity"""
        profit_potential = opportunity.get('profit_potential', 0)
        risk_level = opportunity.get('risk_score', 0.5)
        
        # Higher profit with lower risk = higher human benefit
        benefit_score = (profit_potential * 0.7) * (1 - risk_level * 0.3)
        
        return max(0.0, min(1.0, benefit_score))
    
    async def _calculate_liberation_impact(self, opportunity: Dict[str, Any]) -> float:
        """Calculate impact on financial liberation progress"""
        profit_potential = opportunity.get('profit_potential', 0)
        accessibility = 1.0 - opportunity.get('complexity', 0.5)  # Lower complexity = higher accessibility
        
        liberation_impact = (profit_potential * 0.6) + (accessibility * 0.4)
        
        return max(0.0, min(1.0, liberation_impact))
    
    def _extract_confidence(self, ai_response: str) -> float:
        """Extract confidence score from AI response"""
        # Simple extraction - in production, use more sophisticated parsing
        if 'high confidence' in ai_response.lower():
            return 0.8
        elif 'medium confidence' in ai_response.lower():
            return 0.6
        elif 'low confidence' in ai_response.lower():
            return 0.4
        else:
            return 0.5
    
    def _extract_risk_score(self, ai_response: str) -> float:
        """Extract risk score from AI response"""
        # Implement AI response parsing for risk score
        return 0.5  # Placeholder
    
    def _extract_profit_potential(self, ai_response: str) -> float:
        """Extract profit potential from AI response"""
        # Implement AI response parsing for profit potential
        return 0.6  # Placeholder
    
    def _extract_recommendations(self, ai_response: str) -> List[str]:
        """Extract recommendations from AI response"""
        # Implement AI response parsing for recommendations
        return ["Monitor market conditions", "Execute with caution"]
    
    def _extract_timing(self, ai_response: str) -> str:
        """Extract optimal timing from AI response"""
        return "immediate"  # Placeholder
    
    def _calculate_alignment_score(self, consciousness_analysis: Dict[str, float], 
                                 ai_analysis: Dict[str, Any]) -> float:
        """Calculate alignment between consciousness and AI analysis"""
        consciousness_score = consciousness_analysis['overall']
        ai_confidence = ai_analysis['confidence']
        
        # Simple alignment calculation
        alignment = 1.0 - abs(consciousness_score - ai_confidence)
        return max(0.0, min(1.0, alignment))
    
    def _extract_synthesis_confidence(self, synthesis_response: str) -> float:
        """Extract confidence from synthesis response"""
        return 0.7  # Placeholder
    
    def _extract_recommendation(self, synthesis_response: str) -> str:
        """Extract recommendation from synthesis response"""
        if 'execute' in synthesis_response.lower():
            return 'execute'
        elif 'monitor' in synthesis_response.lower():
            return 'monitor'
        else:
            return 'reject'
    
    def _calculate_position_size_multiplier(self, consciousness_analysis: Dict[str, float], 
                                          ai_analysis: Dict[str, Any]) -> float:
        """Calculate position size multiplier based on analysis"""
        confidence = (consciousness_analysis['overall'] + ai_analysis['confidence']) / 2
        return max(0.1, min(2.0, confidence * 1.5))
    
    def _calculate_execution_delay(self, reasoning_synthesis: Dict[str, Any]) -> int:
        """Calculate execution delay in seconds"""
        return 0  # Immediate execution for now
    
    def _calculate_risk_limits(self, consciousness_analysis: Dict[str, float]) -> Dict[str, float]:
        """Calculate risk limits based on consciousness analysis"""
        risk_level = consciousness_analysis.get('risk_intuition', 0.5)
        
        return {
            'max_loss': 0.02 * (1 - risk_level),  # Lower risk = higher max loss tolerance
            'stop_loss': 0.05 * (1 - risk_level),
            'take_profit': 0.1 * (1 + consciousness_analysis.get('profit_probability', 0.5))
        }
    
    def _calculate_monitoring_frequency(self, ai_analysis: Dict[str, Any]) -> int:
        """Calculate monitoring frequency in seconds"""
        confidence = ai_analysis['confidence']
        
        if confidence >= 0.8:
            return 10  # High confidence = less frequent monitoring
        elif confidence >= 0.6:
            return 5   # Medium confidence = moderate monitoring
        else:
            return 2   # Low confidence = frequent monitoring
    
    def _apply_strategy_adjustments(self, opportunity: Dict[str, Any], 
                                  adjustments: Dict[str, Any]) -> Dict[str, Any]:
        """Apply consciousness-guided strategy adjustments"""
        adjusted = opportunity.copy()
        
        # Apply position size adjustment
        if 'amount' in adjusted:
            adjusted['amount'] *= adjustments.get('position_size_multiplier', 1.0)
        
        # Apply risk limits
        risk_limits = adjustments.get('risk_limits', {})
        adjusted['risk_limits'] = risk_limits
        
        return adjusted
    
    def _extract_risk_factors(self, decision: ConsciousArbitrageDecision) -> List[str]:
        """Extract risk factors from decision"""
        factors = []
        
        if decision.risk_assessment > 0.7:
            factors.append("High risk assessment")
        if decision.consciousness_score < 0.6:
            factors.append("Low consciousness alignment")
        if decision.ai_confidence < 0.6:
            factors.append("Low AI confidence")
        
        return factors
    
    def _extract_optimizations(self, decision: ConsciousArbitrageDecision) -> List[str]:
        """Extract optimization suggestions from decision"""
        optimizations = []
        
        if decision.consciousness_score > 0.8:
            optimizations.append("High consciousness alignment - consider larger position")
        if decision.human_benefit_score > 0.7:
            optimizations.append("High human benefit - prioritize execution")
        
        return optimizations
    
    def _calculate_execution_priority(self, decision: ConsciousArbitrageDecision) -> int:
        """Calculate execution priority (1-10)"""
        priority_score = (
            decision.consciousness_score * 0.3 +
            decision.ai_confidence * 0.3 +
            decision.human_benefit_score * 0.2 +
            decision.liberation_progress_impact * 0.2
        )
        
        return max(1, min(10, int(priority_score * 10)))
    
    def _estimate_impact(self, decision: ConsciousArbitrageDecision, 
                        opportunity: Dict[str, Any]) -> Dict[str, float]:
        """Estimate the impact of executing this opportunity"""
        return {
            'profit_impact': opportunity.get('profit_potential', 0) * decision.consciousness_score,
            'risk_impact': decision.risk_assessment,
            'human_benefit_impact': decision.human_benefit_score,
            'liberation_impact': decision.liberation_progress_impact
        }
    
    async def _get_market_conditions(self) -> Dict[str, Any]:
        """Get current market conditions"""
        # Implement market condition fetching
        return {
            'volatility': 0.3,
            'trend': 'bullish',
            'sentiment': 0.6
        }
    
    async def _get_market_volatility(self) -> float:
        """Get current market volatility"""
        conditions = await self._get_market_conditions()
        return conditions.get('volatility', 0.3)
    
    async def _update_learning_memory(self, decision: ConsciousArbitrageDecision, 
                                    opportunity: Dict[str, Any]):
        """Update learning memory with decision outcomes"""
        # Implement learning memory updates
        pass
    
    async def _learn_from_execution(self, decision: ConsciousArbitrageDecision, 
                                  execution_result: Dict[str, Any]):
        """Learn from execution results to improve future decisions"""
        # Implement learning from execution outcomes
        pass
    
    async def _update_consciousness_state(self):
        """Update consciousness state based on recent performance"""
        # Calculate performance-based consciousness adjustments
        success_rate = (self.performance_metrics['successful_trades'] / 
                       max(1, self.performance_metrics['executed_trades']))
        
        # Adjust consciousness based on performance
        if success_rate > 0.8:
            self.consciousness_state.awareness_level = min(1.0, self.consciousness_state.awareness_level + 0.01)
        elif success_rate < 0.5:
            self.consciousness_state.awareness_level = max(0.5, self.consciousness_state.awareness_level - 0.01)
        
        # Update liberation progress
        self.consciousness_state.matrix_liberation_progress = self.performance_metrics['liberation_progress']
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            **self.performance_metrics,
            'consciousness_level': self.consciousness_state.awareness_level if self.consciousness_state else 0,
            'decision_history_count': len(self.decision_history),
            'success_rate': (self.performance_metrics['successful_trades'] / 
                           max(1, self.performance_metrics['executed_trades']))
        }

# Global instance for use across the application
conscious_arbitrage_engine = ConsciousArbitrageEngine()