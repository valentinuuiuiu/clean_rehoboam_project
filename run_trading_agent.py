"""
Script pentru rularea agentului de tranzacționare automată.
"""
import os
import asyncio
import logging
from datetime import datetime
from auto_trading_agent import AutomatedTradingAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"trading_bot_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("TradingRunner")

async def run_agent(simulation_mode=False):
    """
    Rulează agentul de tranzacționare în modul specificat.
    
    Args:
        simulation_mode: Dacă este True, rulează în modul simulare. Dacă este False, rulează în modul real.
    """
    try:
        # Setăm modul simulare sau real în funcție de parametru
        os.environ["SIMULATION_MODE"] = str(simulation_mode).lower()
        
        logger.info(f"Pornirea agentului de tranzacționare în modul: {'SIMULARE' if simulation_mode else 'REAL'}")
        
        # Inițializăm agentul
        agent = AutomatedTradingAgent()
        
        # Rulăm monitorizarea continuă a piețelor
        await agent.monitor_markets()
        
    except Exception as e:
        logger.error(f"Eroare la rularea agentului: {str(e)}")
        raise

async def test_agent():
    """Execută un test rapid al agentului pentru a verifica funcționalitatea de bază."""
    try:
        logger.info("Începe testarea agentului de tranzacționare...")
        
        # Forțăm modul simulare pentru teste
        os.environ["SIMULATION_MODE"] = "true"
        
        # Inițializăm agentul
        agent = AutomatedTradingAgent()
        
        # Testăm analize pentru diferite token-uri
        for token in ["ETH", "BTC", "LINK"]:
            logger.info(f"Testarea analizei pentru {token}...")
            await agent._analyze_token(token)
        
        # Testăm oportunități de arbitraj
        logger.info("Testarea detectării oportunităților de arbitraj...")
        await agent._check_arbitrage_opportunities()
        
        logger.info("Testare completă. Agentul de tranzacționare funcționează corect.")
        
        return True
        
    except Exception as e:
        logger.error(f"Eroare la testarea agentului: {str(e)}")
        return False

async def main():
    """Funcția principală care rulează agentul."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Agent de tranzacționare automată')
    parser.add_argument('--test', action='store_true', help='Rulează doar teste de funcționalitate')
    parser.add_argument('--simulation', action='store_true', help='Rulează în modul simulare')
    args = parser.parse_args()
    
    if args.test:
        # Rulăm testele
        success = await test_agent()
        if success:
            logger.info("Teste finalizate cu succes. Agentul este gata pentru utilizare.")
        else:
            logger.error("Testele au eșuat. Verificați erorile de mai sus.")
        
    else:
        # Rulăm agentul în modul specificat
        await run_agent(simulation_mode=args.simulation)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program oprit manual de utilizator.")
    except Exception as e:
        logger.error(f"Eroare fatală: {str(e)}")