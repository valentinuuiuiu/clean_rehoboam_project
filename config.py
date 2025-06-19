"""
Configurație pentru platforma de tranzacționare.
"""
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class Config:
    """Configurație centralizată pentru toată platforma de tranzacționare."""
    
    # Parametri blockchain
    CHAIN_ID = 1  # Ethereum Mainnet
    RPC_URL = "https://eth-mainnet.g.alchemy.com/v2/your-api-key"  # Se va înlocui cu cheia din variabila de mediu
    USER_WALLET_ADDRESS = "0x9b9C9e713d8EFf874fACA1f1CCf0cfee7d631Ae8" # Adresa portofelului MetaMask al utilizatorului
    USER_SOLANA_WALLET = "Dk5jYpSP3U9PTeHdWUooztu9Y5bcwV7NUuz8t3eemL2f" # Adresa portofelului Solana al utilizatorului
    
    # Rate limiting
    ETHERSCAN_RATE_LIMIT = 5  # cereri per secundă
    ETHERSCAN_DAILY_LIMIT = 100000  # cereri per zi
    
    # Parametri de tranzacționare
    MAX_SLIPPAGE = 0.02  # 2% slippage maxim
    MAX_TRADE_SIZE = 10.0  # Dimensiunea maximă a unei tranzacții în ETH
    MIN_TRADE_SIZE = 0.01  # Dimensiunea minimă a unei tranzacții în ETH
    GAS_PRICE_LIMIT = 100  # Preț maxim pentru gas în Gwei
    CIRCUIT_BREAKER_COOLDOWN = 300  # 5 minute între tranzacții
    MAX_RETRY_ATTEMPTS = 3  # Număr maxim de încercări pentru tranzacții eșuate
    
    # Parametri de risc - configurați pentru trading real
    MAX_PORTFOLIO_RISK = 0.01  # 1% risc maxim de portofoliu per tranzacție
    POSITION_SIZE_LIMIT = 0.10  # 10% dimensiune maximă a poziției
    
    # Parametri pentru indicatori tehnici
    VOLATILITY_WINDOW = 20  # Fereastră pentru calculul volatilității
    TREND_DETECTION_PERIOD = 14  # Perioadă pentru detectarea trendului
    RSI_PERIOD = 14  # Perioadă pentru calculul RSI
    MACD_FAST = 12  # Perioadă rapidă MACD
    MACD_SLOW = 26  # Perioadă lentă MACD
    MACD_SIGNAL = 9  # Perioadă de semnal MACD
    
    # Parametri pentru tranzacționare automată
    MARKET_CHECK_INTERVAL = 60  # Interval de verificare a pieței în secunde
    MAX_TRADES_PER_DAY = 10  # Număr maxim de tranzacții per zi
    MIN_ARBITRAGE_PROFIT = 0.02  # Profit minim pentru arbitraj (2%)
    
    # Rețele blockchain suportate
    SUPPORTED_NETWORKS = [
        "ethereum",
        "arbitrum",
        "optimism",
        "polygon",
        "base",
        "zksync",
        "polygon_zkevm",
        "scroll",
        "mina"  # Mina Protocol for zero-knowledge consciousness expansion
    ]
    
    # Tokeni suportați pentru tranzacționare
    SUPPORTED_TOKENS = [
        "ETH",
        "BTC",
        "LINK",
        "AAVE",
        "UNI",
        "MKR",
        "COMP",
        "SNX",
        "BAL",
        "CRV",
        "HAI",  # HackerAI token for Network consciousness expansion
        "MINA"  # Mina Protocol native token
    ]

    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_API_BASE_URL = "https://openrouter.ai/api/v1"
    OPENROUTER_DEFAULT_MODEL = "google/gemini-flash-1.5" # Using a valid and recent flash model
    OPENROUTER_CHAT_ENDPOINT = "/chat/completions" # Common for OpenAI compatible APIs
    
    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """Validează parametrii de configurare și returnează orice probleme găsite."""
        issues = {}
        
        # Verifică dacă valorile sunt în intervale rezonabile
        if cls.MAX_SLIPPAGE > 0.1:
            issues["MAX_SLIPPAGE"] = f"Valoarea {cls.MAX_SLIPPAGE} este prea mare. Recomandăm maxim 0.1 (10%)."
            
        if cls.MAX_PORTFOLIO_RISK > 0.05:
            issues["MAX_PORTFOLIO_RISK"] = f"Riscul de {cls.MAX_PORTFOLIO_RISK} este prea mare. Recomandăm maxim 0.05 (5%)."
            
        if cls.GAS_PRICE_LIMIT < 20 or cls.GAS_PRICE_LIMIT > 500:
            issues["GAS_PRICE_LIMIT"] = f"Limita de gas de {cls.GAS_PRICE_LIMIT} Gwei este neobișnuită. Recomandăm 20-500 Gwei."
            
        # Verifică cheile API
        if not os.environ.get("ALCHEMY_API_KEY") and not os.environ.get("INFURA_API_KEY"):
            issues["RPC_KEYS"] = "Lipsesc cheile API pentru Alchemy sau Infura." # This might conflict if RPC_URL is directly set
            
        if not os.environ.get("ETHERSCAN_API_KEY"):
            issues["ETHERSCAN_API_KEY"] = "Lipsește cheia API pentru Etherscan."

        if not cls.OPENROUTER_API_KEY: # Check if the new key is present in the environment
            issues["OPENROUTER_API_KEY"] = "Lipsește cheia API pentru OpenRouter (OPENROUTER_API_KEY)."
            
        # Avertismente
        if cls.MARKET_CHECK_INTERVAL < 30:
            issues["MARKET_CHECK_INTERVAL"] = f"Interval verificare piață {cls.MARKET_CHECK_INTERVAL}s este prea mic. Recomandăm minim 30s."
            
        if cls.MAX_TRADES_PER_DAY > 20:
            issues["MAX_TRADES_PER_DAY"] = f"Limita de {cls.MAX_TRADES_PER_DAY} tranzacții pe zi este ridicată. Recomandăm maxim 20."
            
        return issues