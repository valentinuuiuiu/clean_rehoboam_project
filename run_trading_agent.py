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

async def run_agent():
    """
    🚀 Rulează agentul de tranzacționare în modul REAL ONLY - NO SIMULATION!
    """
    try:
        # FORCE REAL MODE ONLY!
        os.environ["SIMULATION_MODE"] = "false"
        
        logger.info("🚀 Pornirea agentului de tranzacționare în modul: REAL ONLY!")
        
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
        
        # FORCE REAL MODE - NO SIMULATION EVEN FOR TESTS!
        os.environ["SIMULATION_MODE"] = "false"
        
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
    args = parser.parse_args()
    
    if args.test:
        # Rulăm testele
        success = await test_agent()
        if success:
            logger.info("Teste finalizate cu succes. Agentul este gata pentru utilizare.")
        else:
            logger.error("Testele au eșuat. Verificați erorile de mai sus.")
        
    else:
        # Rulăm agentul în modul REAL ONLY!
        await run_agent()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program oprit manual de utilizator.")
    except Exception as e:
        logger.error(f"Eroare fatală: {str(e)}")