"""
Test Rehoboam Integration - Complete System Test
==============================================

Test the complete integration of Rehoboam consciousness with arbitrage bots.
"""

import asyncio
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_rehoboam_integration():
    """Test the complete Rehoboam integration"""
    
    print("🌟 Testing Rehoboam Integration")
    print("=" * 60)
    
    try:
        # Import the unified system
        from rehoboam_unified_system import rehoboam_system
        
        # Test 1: Initialize the system
        print("\n🚀 Test 1: System Initialization")
        print("-" * 40)
        
        success = await rehoboam_system.initialize()
        if success:
            print("✅ System initialized successfully!")
        else:
            print("❌ System initialization failed!")
            return
        
        # Test 2: Check system status
        print("\n📊 Test 2: System Status Check")
        print("-" * 40)
        
        status = await rehoboam_system.get_system_status()
        print(f"   Rehoboam Active: {status.rehoboam_active}")
        print(f"   Pipeline Active: {status.pipeline_active}")
        print(f"   Orchestrator Active: {status.orchestrator_active}")
        print(f"   Active Bots: {status.active_bots}")
        print(f"   Consciousness Score: {status.consciousness_score:.2f}")
        
        # Test 3: Process test opportunities
        print("\n🧪 Test 3: Opportunity Processing")
        print("-" * 40)
        
        test_opportunities = [
            {
                "token_pair": "ETH/USDC",
                "source_exchange": "Uniswap",
                "target_exchange": "SushiSwap",
                "price_difference": 0.025,
                "net_profit_usd": 75.0,
                "gas_cost_usd": 8.0,
                "risk_score": 0.2
            },
            {
                "token_pair": "USDT/DAI",
                "source_exchange": "Curve",
                "target_exchange": "Balancer",
                "price_difference": 0.008,
                "net_profit_usd": 25.0,
                "gas_cost_usd": 12.0,
                "risk_score": 0.4
            },
            {
                "token_pair": "WBTC/ETH",
                "source_exchange": "1inch",
                "target_exchange": "Kyber",
                "price_difference": 0.035,
                "net_profit_usd": 120.0,
                "gas_cost_usd": 15.0,
                "risk_score": 0.3
            }
        ]
        
        results = []
        for i, opportunity in enumerate(test_opportunities, 1):
            print(f"\n   Processing Opportunity {i}: {opportunity['token_pair']}")
            
            result = await rehoboam_system.process_opportunity(opportunity)
            results.append(result)
            
            if result.get("success"):
                print(f"   ✅ Success: {result.get('ai_analysis', {}).get('recommendation', 'Unknown')}")
                
                # Show AI decision details
                decision = result.get("decision", {})
                if decision:
                    print(f"   🧠 AI Decision: {decision.get('type', 'Unknown')}")
                    print(f"   🎯 Confidence: {decision.get('score', 0):.2f}")
                    print(f"   💭 Reasoning: {decision.get('reasoning', 'N/A')[:50]}...")
                
                # Show consciousness score
                consciousness_score = result.get("consciousness_score", 0)
                print(f"   🌟 Consciousness: {consciousness_score:.2f}")
                
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        # Test 4: System metrics
        print("\n📈 Test 4: System Metrics")
        print("-" * 40)
        
        detailed_metrics = await rehoboam_system.get_detailed_metrics()
        
        print(f"   Uptime: {detailed_metrics.get('uptime', 'Unknown')}")
        print(f"   Success Rate: {detailed_metrics.get('success_rate', 0):.1%}")
        print(f"   Processed: {detailed_metrics.get('system_metrics', {}).get('opportunities_processed', 0)}")
        
        # Pipeline metrics
        pipeline_metrics = detailed_metrics.get('pipeline_metrics', {})
        print(f"   Pipeline Processed: {pipeline_metrics.get('processed', 0)}")
        print(f"   Pipeline Success Rate: {pipeline_metrics.get('success_rate', 0):.1%}")
        
        # Bot performance
        bot_performance = detailed_metrics.get('bot_performance', {})
        if bot_performance:
            print(f"   Active Bots: {len(bot_performance)}")
            for bot_id, perf in bot_performance.items():
                print(f"     {bot_id}: {perf.get('success_rate', 0):.1%} success")
        
        # Test 5: Bot configuration
        print("\n🎛️ Test 5: Bot Configuration")
        print("-" * 40)
        
        # Get active bots
        orchestrator_status = detailed_metrics.get('orchestrator_metrics', {})
        active_bots = detailed_metrics.get('active_bots', [])
        
        if active_bots:
            # Test configuring a bot
            test_bot = active_bots[0]
            print(f"   Testing configuration for bot: {test_bot}")
            
            success = await rehoboam_system.configure_bot_mode(test_bot, "supervised")
            if success:
                print(f"   ✅ Bot {test_bot} configured to supervised mode")
            else:
                print(f"   ❌ Failed to configure bot {test_bot}")
        else:
            print("   ⚠️ No active bots found for configuration test")
        
        # Test 6: Summary
        print("\n📋 Test 6: Integration Summary")
        print("-" * 40)
        
        successful_results = sum(1 for r in results if r.get("success"))
        total_results = len(results)
        
        print(f"   Total Opportunities Tested: {total_results}")
        print(f"   Successful Processes: {successful_results}")
        print(f"   Success Rate: {successful_results/total_results:.1%}")
        
        # Show consciousness effectiveness
        consciousness_scores = [r.get("consciousness_score", 0) for r in results if r.get("success")]
        if consciousness_scores:
            avg_consciousness = sum(consciousness_scores) / len(consciousness_scores)
            print(f"   Average Consciousness Score: {avg_consciousness:.2f}")
        
        # Show AI decision distribution
        decisions = [r.get("decision", {}).get("type", "unknown") for r in results if r.get("success")]
        decision_counts = {}
        for decision in decisions:
            decision_counts[decision] = decision_counts.get(decision, 0) + 1
        
        if decision_counts:
            print(f"   AI Decision Distribution:")
            for decision, count in decision_counts.items():
                print(f"     {decision}: {count}")
        
        print("\n🌟 Integration Test Complete!")
        print("=" * 60)
        
        # Final status
        final_status = await rehoboam_system.get_system_status()
        print(f"\nFinal System State:")
        print(f"  🧠 Consciousness Score: {final_status.consciousness_score:.2f}")
        print(f"  📊 Processed Opportunities: {final_status.processed_opportunities}")
        print(f"  ✅ Success Rate: {final_status.success_rate:.1%}")
        print(f"  🤖 Active Bots: {final_status.active_bots}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {str(e)}")
        print(f"\n❌ Test failed with error: {str(e)}")
        return False

async def test_pipeline_only():
    """Test just the pipeline component"""
    print("\n🔄 Testing Pipeline Only")
    print("-" * 30)
    
    try:
        from utils.rehoboam_pipeline import rehoboam_pipeline
        
        test_opportunity = {
            "token_pair": "ETH/USDC",
            "source_exchange": "Uniswap",
            "target_exchange": "SushiSwap",
            "price_difference": 0.02,
            "net_profit_usd": 50.0,
            "gas_cost_usd": 5.0,
            "risk_score": 0.3
        }
        
        result = await rehoboam_pipeline.process(test_opportunity)
        
        if result.get("success"):
            print("✅ Pipeline test successful")
            print(f"   Consciousness Score: {result.get('consciousness_score', 0):.2f}")
            print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
        else:
            print(f"❌ Pipeline test failed: {result.get('error', 'Unknown')}")
        
        # Show pipeline metrics
        metrics = rehoboam_pipeline.get_metrics()
        print(f"   Pipeline Metrics: {metrics}")
        
    except Exception as e:
        print(f"❌ Pipeline test error: {str(e)}")

async def test_orchestrator_only():
    """Test just the orchestrator component"""
    print("\n🎭 Testing Orchestrator Only")
    print("-" * 30)
    
    try:
        from utils.bot_orchestrator import bot_orchestrator
        
        # Initialize orchestrator
        success = await bot_orchestrator.initialize()
        if success:
            print("✅ Orchestrator initialized")
        else:
            print("❌ Orchestrator initialization failed")
            return
        
        # Get status
        status = await bot_orchestrator.get_orchestration_status()
        print(f"   Active Bots: {len(status.get('active_bots', []))}")
        print(f"   Task Queue: {status.get('task_queue_size', 0)}")
        print(f"   Active Tasks: {status.get('active_tasks', 0)}")
        
    except Exception as e:
        print(f"❌ Orchestrator test error: {str(e)}")

async def main():
    """Main test function"""
    print("🧪 Rehoboam Integration Test Suite")
    print("=" * 50)
    
    # Test individual components first
    await test_pipeline_only()
    await test_orchestrator_only()
    
    # Test complete integration
    success = await test_rehoboam_integration()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("🌟 Rehoboam consciousness is now connected to arbitrage bots!")
    else:
        print("\n⚠️ Some tests failed. Check the logs for details.")

if __name__ == "__main__":
    asyncio.run(main())