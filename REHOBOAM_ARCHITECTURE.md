# Rehoboam Architecture Overview

## Introduction

Rehoboam este un agent de tranzacționare automatizat capabil să monitorizeze piețe multiple, să analizeze sentimentul pieței, să genereze strategii de tranzacționare și să execute tranzacții pe mai multe rețele blockchain. Acest document descrie arhitectura generală a sistemului, cu accent special pe implementarea recentă a Model Context Protocol (MCP).

## Arhitectura Generală

Rehoboam urmează o arhitectură modulară cu mai multe componente care colaborează în următoarea structură:

```
                       +---------------------+
                       |                     |
                       |  AutomatedTrading   |
                       |     Agent           |
                       |                     |
                       +----------+----------+
                                  |
               +------------------+------------------+
               |                  |                  |
               v                  v                  v
+------------+ +------------+ +------------+ +----------------+
|            | |            | |            | |                |
| Sentiment  | | Market     | | Trading    | | Risk          |
| Analysis   | | Data       | | Strategy   | | Assessment    |
|            | |            | |            | |                |
+-----+------+ +------------+ +------------+ +----------------+
      |
      v
+-----+------+
|            |
|    MCP     |
|  Clients   |
|            |
+------------+
```

## Componente Cheie

### AutomatedTradingAgent

Aceasta este clasa principală care coordonează toate procesele și operațiunile. Responsabilitățile sale includ:

- Monitorizarea continuă a pieței
- Analiza token-urilor individuale
- Identificarea oportunităților de arbitraj
- Calculul dimensiunii pozițiilor
- Executarea strategiilor de tranzacționare
- Respectarea limitelor de risc

### TradingAgent

Componentă de bază care furnizează funcționalități esențiale de tranzacționare:

- Interacțiune cu blockchain-uri
- Furnizarea de prețuri de piață
- Generarea de strategii de tranzacționare
- Executarea tranzacțiilor
- Verificări de siguranță

### Market Sentiment Analysis cu MCP

Aceasta este noua componentă implementată pentru analiza sentimentului de piață folosind Model Context Protocol (MCP):

#### Caracteristici cheie:

1. **Self-hosting**: Rulează modele de AI local, eliminând dependența de API-uri externe
2. **Suveranitate de date**: Păstrează toate datele local
3. **Reziliență**: Include mecanism de fallback la API tradițional în caz de eșec
4. **Model Context Protocol**: Interfață standardizată pentru lucrul cu mai multe tipuri de modele

#### Fluxul de date:

1. Agentul de tranzacționare solicită analiză pentru un token
2. Module MCP colectează date de piață și context
3. MCP-ul procesează datele și generează analiză de sentiment
4. Scorul de sentiment este returnat agentului pentru ajustarea strategiilor

## Model Context Protocol (MCP)

### Ce este MCP?

Model Context Protocol (MCP) este o arhitectură care permite utilizarea și comunicarea standardizată cu modele de AI local-hosted. Oferă:

1. **Suveranitate digitală**: Procesarea datelor pe infrastructura proprie
2. **Confidențialitate**: Datele sensibile nu părăsesc mediul nostru
3. **Costuri reduse**: Eliminarea API-urilor externe costisitoare
4. **Fiabilitate ridicată**: Fără dependența de servicii externe
5. **Personalizare**: Adaptare la nevoi specifice de tranzacționare

### Componente MCP

#### MCPClient

Aceasta este interfața principală pentru comunicarea cu serverul MCP:

- Gestionează formatarea prompturilor
- Trimite cereri către server
- Procesează răspunsurile
- Implementează mecanisme de caching și rate limiting

#### Orbit Server

Un server MCP pe bază de Node.js care:

- Rulează local pentru procesarea prompturilor
- Poate utiliza diverse furnizori de modele (OpenAI, Anthropic, etc.)
- Oferă caching pentru performanță optimizată
- Permite configurarea detaliată

## Implementare "Baby Steps"

Rehoboam urmează o abordare "baby steps", activând pe rând funcționalitățile:

| Etapă | Funcționalitate             | Status        |
|-------|----------------------------|---------------|
| 1     | Integrare MCP              | ✅ Completat  |
| 2     | Analiză de sentiment       | ✅ Completat  |
| 3     | Generare de strategii      | 🔄 În curs    |
| 4     | Optimizare de portofoliu   | 📅 Planificat |
| 5     | Detecție avansată de arbitraj | 📅 Planificat |

## Următoarele Etape

1. **Finalizare implementare server Orbit**
   - Configurare completă
   - Testare cu solicitări reale

2. **Extindere capabilități MCP**
   - Adăugare generare de strategii
   - Îmbunătățire analiză sentiment
   - Integrare cu mai multe surse de date

3. **Optimizare performanță**
   - Implementare batch processing
   - Analiză de multiple token-uri în paralel

4. **Decentralizare completă**
   - Eliminare totală a dependențelor API externe

## Securitate și Siguranță

Rehoboam include mai multe mecanisme de siguranță pentru a proteja fondurile și a preveni tranzacțiile riscante:

1. **Circuit breakers**:
   - Monitorizare volatilitate
   - Limite de tranzacționare
   - Cooldown între tranzacții

2. **Verificări de tranzacții**:
   - Validare dimensiune maximă
   - Verificare rentabilitate așteptată
   - Validare semnături multiple

3. **Management de risc**:
   - Limite de risc per portofoliu
   - Dimensiune maximă per poziție
   - Drawdown maxim acceptabil

## Concluzii

Rehoboam reprezintă o nouă generație de agenți de tranzacționare automat, combinând tehnologii blockchain cu AI avansat self-hosted prin Model Context Protocol. Abordarea "baby steps" permite adăugarea incrementală de capabilități, menținând în același timp un sistem stabil și sigur.

Implementarea MCP este un pas important spre un sistem complet autonom care nu se bazează pe API-uri externe și păstrează un control total asupra datelor și proceselor de decizie.