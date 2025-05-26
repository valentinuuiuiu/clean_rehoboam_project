"""
Script de test pentru agentul de tranzacționare automată
"""
import asyncio
import argparse
import logging
from datetime import datetime

from auto_trading_agent import AutomatedTradingAgent
from trading_agent import TradingAgent

# Configurare logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"trading_bot_test_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("AutomatedTradingTest")

async def run_single_test():
    """Rulează un singur test al agentului de tranzacționare automată."""
    logger.info("Inițializare test pentru agentul de tranzacționare automată...")
    
    # Forțăm modul simulare pentru teste
    import os
    os.environ["SIMULATION_MODE"] = "true"
    
    # Inițializăm agentul
    agent = AutomatedTradingAgent()
    
    # Verificăm prețurile pentru fiecare token suportat
    logger.info(f"Verificare prețuri pentru {len(agent.enabled_tokens)} tokens...")
    
    for token in agent.enabled_tokens[:3]:  # Primele 3 token-uri pentru test rapid
        price = agent.agent.get_latest_price(token)
        logger.info(f"Preț curent pentru {token}: ${price:.2f}")
    
    # Testăm analiza pentru un token
    logger.info("Testare analiză pentru ETH...")
    await agent._analyze_token("ETH")
    
    # Testăm detectarea oportunităților de arbitraj
    logger.info("Verificare oportunități de arbitraj...")
    await agent._check_arbitrage_opportunities()
    
    logger.info("Test finalizat cu succes!")
    return True

async def run_continuous_test(duration_seconds=60):
    """Rulează un test continuu al agentului pentru o perioadă limitată."""
    logger.info(f"Pornire test continuu pentru {duration_seconds} secunde...")
    
    # Forțăm modul simulare pentru teste
    import os
    os.environ["SIMULATION_MODE"] = "true"
    
    # Inițializăm agentul cu un interval de verificare mai scurt pentru teste
    agent = AutomatedTradingAgent()
    agent.check_interval = 10  # 10 secunde între verificări pentru testare
    
    # Start time
    import time
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration_seconds:
            # Pentru teste, analizăm un singur token și verificăm arbitrajul
            logger.info(f"Ciclu de testare la {time.time() - start_time:.1f} secunde")
            await agent._analyze_token("ETH")
            await agent._check_arbitrage_opportunities()
            
            # Așteptăm între verificări
            await asyncio.sleep(agent.check_interval)
    
    except KeyboardInterrupt:
        logger.info("Test oprit manual")
    
    logger.info("Test continuu finalizat!")
    return True

async def run_trading_simulation():
    """Simulează o tranzacție folosind agentul de trading."""
    logger.info("Simulare tranzacție...")
    
    # Inițializăm agentul direct
    import os
    os.environ["SIMULATION_MODE"] = "true"
    agent = TradingAgent()
    
    # Simulăm o tranzacție de vânzare
    token = "ETH"
    amount = 1
    side = "sell"
    network = "ethereum"
    
    price = agent.get_latest_price(token)
    logger.info(f"Preț curent pentru {token}: ${price:.2f}")
    
    # Executăm tranzacția
    logger.info(f"Executare tranzacție: {side} {amount} {token} pe {network}")
    result = agent.trade_tokens(amount, side, network)
    
    if result:
        logger.info("Tranzacție simulată cu succes!")
    else:
        logger.error(f"Eroare la simularea tranzacției: {agent.safety_checks.last_error}")
    
    return result

async def main():
    """Funcția principală care procesează argumentele și rulează testele."""
    parser = argparse.ArgumentParser(description='Teste pentru agentul de tranzacționare automată')
    parser.add_argument('--test-type', choices=['single', 'continuous', 'trade'], default='single',
                        help='Tipul de test: single (test rapid), continuous (test continuu), trade (simulare tranzacție)')
    parser.add_argument('--duration', type=int, default=60,
                        help='Durata testului continuu în secunde (pentru testul continuu)')
    
    args = parser.parse_args()
    
    if args.test_type == 'single':
        await run_single_test()
    elif args.test_type == 'continuous':
        await run_continuous_test(args.duration)
    elif args.test_type == 'trade':
        await run_trading_simulation()

if __name__ == "__main__":
    asyncio.run(main())