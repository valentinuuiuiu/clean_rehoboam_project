# Ghid de utilizare a Agentului de Tranzacționare Automată

Acest document explică cum să folosiți agentul de tranzacționare automată pentru executarea de tranzacții pe diferite blockchain-uri.

## Prezentare generală

Agentul automat de tranzacționare este un sistem care:

1. Monitorizează continuu piețele cripto
2. Identifică oportunități de tranzacționare folosind algoritmi avansați
3. Execută tranzacții automat atunci când găsește oportunități profitabile
4. Funcționează pe mai multe rețele blockchain pentru a maximiza profitul

## Configurarea și pornirea agentului

Agentul poate rula în două moduri:
- **Mod de simulare**: Toate tranzacțiile sunt simulate, fără a folosi fonduri reale
- **Mod real**: Tranzacțiile sunt executate pe blockchain, folosind fonduri reale

### Pornirea în mod de simulare (recomandat)

```bash
python run_full_trading_agent.py --simulation
```

### Pornirea în mod real (folosește fonduri reale, atenție!)

```bash
python run_full_trading_agent.py --real
```

## Testarea agentului

Pentru a testa funcționalitatea agentului fără a rula continuu:

### Test rapid

```bash
python test_automated_trading.py --test-type single
```

### Test continuu pentru o anumită durată

```bash
python test_automated_trading.py --test-type continuous --duration 120
```

### Testare simulare tranzacție

```bash
python test_automated_trading.py --test-type trade
```

## Configurarea parametrilor

Parametrii de configurare se găsesc în fișierul `config.py`. Ajustați acești parametri pentru a personaliza comportamentul agentului:

- Limita de slippage
- Dimensiunea tranzacțiilor
- Limita de preț pentru gas
- Numărul maxim de tranzacții pe zi
- Rețelele și token-urile suportate

## Fișiere principale

- `auto_trading_agent.py` - Clasa principală a agentului automat
- `run_full_trading_agent.py` - Script pentru pornirea agentului
- `test_automated_trading.py` - Script pentru teste
- `config.py` - Parametri de configurare
- `trading_agent.py` - Agent de bază pentru tranzacționare
- `trading_bot_*.log` - Fișiere de log generate automat

## Troubleshooting și rezolvarea problemelor

### Erori cu cheia privată

Dacă întâmpinați erori legate de cheia privată, verificați dacă:
- Cheia privată este în formatul corect (32 bytes, fără prefixul 0x)
- Cheia este setată corect ca variabilă de mediu

### Erori de conectare la rețele

Verificați:
- Că aveți cheile API setate corect (ALCHEMY_API_KEY, INFURA_API_KEY)
- Rețelele configurate în `config.py` sunt disponibile
- Nu există probleme temporare cu furnizorii de RPC

### Optimizarea agentului

Pentru a optimiza performanța agentului:
- Ajustați parametrii de risc din `config.py`
- Modificați intervalul de verificare a pieței (MARKET_CHECK_INTERVAL)
- Filtrați tokenii și rețelele pentru a le include doar pe cele relevante pentru strategia dvs.

## Limitări curente

- Agentul rulează în modul simulare dacă întâmpină orice erori la inițializarea modului real
- Nu pot fi executate simultan mai multe instanțe ale agentului pe aceeași mașină
- Algoritmul de arbitraj este limitat la diferențele de preț și nu ia în considerare complexitatea deplină a strategiilor de arbitraj

## Exemple de utilizare avansată

### Configurarea unei strategii personalizate

Modificați metodele `_should_execute_strategy` și `_calculate_position_size` din clasa `AutomatedTradingAgent` pentru a personaliza logica de tranzacționare.

### Adăugarea de tokeni și rețele

Actualizați listele `SUPPORTED_TOKENS` și `SUPPORTED_NETWORKS` din `config.py` pentru a adăuga suport pentru noi tokeni și rețele blockchain.