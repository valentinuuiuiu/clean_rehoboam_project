"""
Script pentru pornirea agentului de tranzacționare în mod complet automat.
"""
import os
import asyncio
import logging
import argparse
from datetime import datetime

from auto_trading_agent import AutomatedTradingAgent

# Configurare logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"trading_bot_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("TradingRunner")

async def run_agent(simulation_mode: bool):
    """
    Rulează agentul de tranzacționare în modul specificat.
    
    Args:
        simulation_mode: Dacă este True, rulează în modul simulare. 
                         Dacă este False, rulează în modul real de tranzacționare.
    """
    # Setăm modul de simulare
    os.environ["SIMULATION_MODE"] = str(simulation_mode).lower()
    
    logger.info("=" * 80)
    logger.info(f"PORNIREA AGENTULUI DE TRANZACȚIONARE AUTOMATĂ ÎN MOD {'SIMULARE' if simulation_mode else 'REAL'}")
    logger.info("=" * 80)
    
    # Afișăm avertisment important pentru modul real
    if not simulation_mode:
        logger.warning("!!! ATENȚIE !!! Agentul rulează în modul REAL de tranzacționare!")
        logger.warning("Tranzacțiile vor fi executate pe blockchain cu fonduri reale!")
        logger.warning("Apăsați CTRL+C pentru a opri agentul în orice moment.")
        logger.warning("=" * 80)
    
    # Inițializăm agentul
    agent = AutomatedTradingAgent()
    
    # Afișăm configurația curentă
    logger.info(f"Tokeni activi: {agent.enabled_tokens}")
    logger.info(f"Rețele suportate: {agent.enabled_networks}")
    logger.info(f"Interval de verificare a pieței: {agent.check_interval} secunde")
    logger.info(f"Limită maximă de tranzacții pe zi: {agent.max_trades_per_day}")
    
    try:
        # Rulăm monitorizarea continuă a piețelor
        await agent.monitor_markets()
    except KeyboardInterrupt:
        logger.info("Agentul a fost oprit manual de utilizator.")
    except Exception as e:
        logger.error(f"Eroare fatală în agentul de tranzacționare: {str(e)}")
        raise

async def main():
    """Funcția principală pentru procesarea argumentelor și pornirea agentului."""
    parser = argparse.ArgumentParser(description='Agent de tranzacționare automată')
    parser.add_argument('--simulation', action='store_true', 
                        help='Rulează în modul simulare (implicit: simulare)')
    parser.add_argument('--real', action='store_true',
                        help='Rulează în modul real de tranzacționare (ATENȚIE: Va folosi fonduri reale!)')
    
    args = parser.parse_args()
    
    # Decidem modul de rulare bazat pe argumente
    simulation_mode = True  # Implicit folosim simularea pentru siguranță
    
    if args.real:
        simulation_mode = False
    
    # Rulăm agentul
    await run_agent(simulation_mode)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAgent oprit manual.")
    except Exception as e:
        print(f"Eroare fatală: {str(e)}")