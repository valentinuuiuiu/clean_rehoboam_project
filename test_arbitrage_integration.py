#!/usr/bin/env python3
"""
Test script for arbitrage service integration with the API server.
This script verifies that the arbitrage bots are properly connected to the backend.
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

class ArbitrageIntegrationTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_api_endpoints(self):
        """Test all arbitrage API endpoints."""
        print("🔍 Testing Arbitrage API Endpoints...")
        
        # Test opportunities endpoint
        try:
            async with self.session.get(f"{self.base_url}/api/arbitrage/opportunities?token=ETH&limit=5") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Opportunities endpoint: {len(data.get('opportunities', []))} opportunities found")
                else:
                    print(f"❌ Opportunities endpoint failed: {resp.status}")
        except Exception as e:
            print(f"❌ Opportunities endpoint error: {str(e)}")
        
        # Test strategies endpoint
        try:
            async with self.session.get(f"{self.base_url}/api/arbitrage/strategies") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Strategies endpoint: {len(data.get('strategies', []))} strategies found")
                else:
                    print(f"❌ Strategies endpoint failed: {resp.status}")
        except Exception as e:
            print(f"❌ Strategies endpoint error: {str(e)}")
        
        # Test bots status endpoint
        try:
            async with self.session.get(f"{self.base_url}/api/arbitrage/bots") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Bots status endpoint: {len(data.get('bots', {}))} bots registered")
                    return data.get('bots', {})
                else:
                    print(f"❌ Bots status endpoint failed: {resp.status}")
        except Exception as e:
            print(f"❌ Bots status endpoint error: {str(e)}")
        
        return {}
    
    async def test_bot_control(self, bot_id: str):
        """Test bot start/stop functionality."""
        print(f"\n🤖 Testing Bot Control for {bot_id}...")
        
        # Test starting a bot
        try:
            config = {"min_profit_threshold": 0.01, "max_trade_amount": 1000}
            async with self.session.post(
                f"{self.base_url}/api/arbitrage/bots/{bot_id}/start",
                json=config
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Bot start: {data.get('message', 'Success')}")
                else:
                    print(f"❌ Bot start failed: {resp.status}")
        except Exception as e:
            print(f"❌ Bot start error: {str(e)}")
        
        # Wait a moment
        await asyncio.sleep(2)
        
        # Test stopping the bot
        try:
            async with self.session.post(f"{self.base_url}/api/arbitrage/bots/{bot_id}/stop") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Bot stop: {data.get('message', 'Success')}")
                else:
                    print(f"❌ Bot stop failed: {resp.status}")
        except Exception as e:
            print(f"❌ Bot stop error: {str(e)}")
    
    async def test_monitoring_control(self):
        """Test monitoring start/stop functionality."""
        print("\n📊 Testing Monitoring Control...")
        
        # Test starting monitoring
        try:
            async with self.session.post(f"{self.base_url}/api/arbitrage/monitoring/start") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Monitoring start: {data.get('message', 'Success')}")
                else:
                    print(f"❌ Monitoring start failed: {resp.status}")
        except Exception as e:
            print(f"❌ Monitoring start error: {str(e)}")
        
        # Wait a moment
        await asyncio.sleep(2)
        
        # Test stopping monitoring
        try:
            async with self.session.post(f"{self.base_url}/api/arbitrage/monitoring/stop") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Monitoring stop: {data.get('message', 'Success')}")
                else:
                    print(f"❌ Monitoring stop failed: {resp.status}")
        except Exception as e:
            print(f"❌ Monitoring stop error: {str(e)}")
    
    async def test_websocket_connection(self):
        """Test WebSocket connection for real-time updates."""
        print("\n🔌 Testing WebSocket Connection...")
        
        try:
            import websockets
            
            uri = f"ws://localhost:8000/ws/arbitrage"
            async with websockets.connect(uri) as websocket:
                print("✅ WebSocket connected successfully")
                
                # Send a test message
                test_message = {
                    "type": "get_arbitrage",
                    "token": "ETH",
                    "limit": 3
                }
                await websocket.send(json.dumps(test_message))
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    print(f"✅ WebSocket response: {data.get('type', 'unknown')} message received")
                except asyncio.TimeoutError:
                    print("⚠️ WebSocket response timeout")
                
                # Test bot status request
                bot_message = {"type": "get_bots"}
                await websocket.send(json.dumps(bot_message))
                
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    print(f"✅ Bot status via WebSocket: {len(data.get('data', {}))} bots")
                except asyncio.TimeoutError:
                    print("⚠️ Bot status response timeout")
                
        except ImportError:
            print("⚠️ websockets library not available, skipping WebSocket test")
        except Exception as e:
            print(f"❌ WebSocket test error: {str(e)}")
    
    async def run_full_test(self):
        """Run the complete integration test suite."""
        print("🚀 Starting Arbitrage Integration Test Suite")
        print("=" * 50)
        
        # Test API endpoints
        bots = await self.test_api_endpoints()
        
        # Test bot control if bots are available
        if bots:
            bot_id = list(bots.keys())[0]
            await self.test_bot_control(bot_id)
        else:
            print("\n⚠️ No bots found, skipping bot control tests")
        
        # Test monitoring control
        await self.test_monitoring_control()
        
        # Test WebSocket connection
        await self.test_websocket_connection()
        
        print("\n" + "=" * 50)
        print("🏁 Integration test suite completed")

async def main():
    """Main test function."""
    print("Arbitrage Service Integration Tester")
    print("This script tests the integration between arbitrage bots and the API server")
    print()
    
    async with ArbitrageIntegrationTester() as tester:
        await tester.run_full_test()

if __name__ == "__main__":
    asyncio.run(main())