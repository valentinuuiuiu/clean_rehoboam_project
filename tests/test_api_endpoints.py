"""Test suite for API endpoints."""
import pytest
import aiohttp
import asyncio
from datetime import datetime, timedelta

class TestAPIEndpoints:
    """Test all API endpoints for functionality and error handling."""
    
    @pytest.fixture
    async def session(self):
        async with aiohttp.ClientSession() as session:
            yield session
            
    @pytest.fixture
    async def auth_token(self, session):
        """Get authentication token for protected endpoints."""
        async with session.post(
            'http://localhost:8000/api/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'test123'
            }
        ) as response:
            data = await response.json()
            assert response.status == 200
            return data['token']

    async def test_market_analysis(self, session, auth_token):
        """Test market analysis endpoint."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        async with session.get(
            'http://localhost:8000/api/market/analysis',
            params={'token': 'ETH', 'timeframe': '1h'},
            headers=headers
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert 'sentiment' in data
            assert 'prediction' in data
            assert 'confidence' in data

    async def test_trading_execution(self, session, auth_token):
        """Test trade execution endpoint."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        order = {
            'token': 'ETH',
            'amount': 0.1,
            'type': 'buy',
            'price': 2500.00
        }
        async with session.post(
            'http://localhost:8000/api/trading/execute',
            json=order,
            headers=headers
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert data['success'] is True
            assert 'transaction_hash' in data

    async def test_portfolio_summary(self, session, auth_token):
        """Test portfolio summary endpoint."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        async with session.get(
            'http://localhost:8000/api/portfolio/summary',
            headers=headers
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert 'total_value' in data
            assert 'assets' in data
            assert 'performance' in data

    async def test_arbitrage_opportunities(self, session, auth_token):
        """Test arbitrage opportunities endpoint."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        async with session.get(
            'http://localhost:8000/api/chains/opportunities',
            headers=headers
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert isinstance(data, list)
            if len(data) > 0:
                opportunity = data[0]
                assert 'source_chain' in opportunity
                assert 'target_chain' in opportunity
                assert 'price_difference' in opportunity
                assert 'estimated_profit' in opportunity

    async def test_ai_sentiment(self, session, auth_token):
        """Test AI sentiment analysis endpoint."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        async with session.get(
            'http://localhost:8000/api/ai/sentiment',
            params={'token': 'ETH'},
            headers=headers
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert 'sentiment' in data
            assert 'confidence' in data
            assert 'risk_level' in data

    async def test_rate_limiting(self, session, auth_token):
        """Test rate limiting functionality."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        # Make multiple requests quickly
        tasks = []
        for _ in range(10):
            task = session.get(
                'http://localhost:8000/api/market/analysis',
                params={'token': 'ETH', 'timeframe': '1h'},
                headers=headers
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        rate_limited = any(
            isinstance(resp, aiohttp.ClientResponseError) and resp.status == 429
            for resp in responses
        )
        assert rate_limited, "Rate limiting not working as expected"

    async def test_error_handling(self, session, auth_token):
        """Test error handling for invalid requests."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        # Test invalid token
        async with session.get(
            'http://localhost:8000/api/market/analysis',
            params={'token': 'INVALID_TOKEN', 'timeframe': '1h'},
            headers=headers
        ) as response:
            assert response.status == 400
            data = await response.json()
            assert 'error' in data
            assert data['success'] is False

        # Test invalid timeframe
        async with session.get(
            'http://localhost:8000/api/market/analysis',
            params={'token': 'ETH', 'timeframe': 'invalid'},
            headers=headers
        ) as response:
            assert response.status == 400
            data = await response.json()
            assert 'error' in data
            assert data['success'] is False

    async def test_websocket_connection(self):
        """Test WebSocket connection and data streaming."""
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect('ws://localhost:8000/api/websocket/market') as ws:
                await ws.send_json({
                    'action': 'subscribe',
                    'channel': 'market',
                    'symbols': ['ETH']
                })
                
                # Wait for initial message
                msg = await ws.receive_json()
                assert 'type' in msg
                assert msg['type'] in ['subscription_success', 'market_update']

                # Wait for market update
                msg = await ws.receive_json()
                assert 'type' in msg
                assert 'data' in msg
                assert 'timestamp' in msg

if __name__ == '__main__':
    pytest.main([__file__, '-v'])