# Local Setup Guide

This guide will help you set up and run the Rehoboam project locally on your machine.

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL database

## Step 1: Extract the Project

Extract the `essential_project.tar.gz` file to your desired location:

```bash
tar -xzvf essential_project.tar.gz -C /path/to/destination
cd /path/to/destination
```

## Step 2: Set Up Environment Variables

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file to add your API keys and configure your environment:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `DEEPSEEK_API_KEY`: Your DeepSeek API key
   - `ALCHEMY_API_KEY`: Your Alchemy API key
   - `ETHERSCAN_API_KEY`: Your Etherscan API key
   - `PRIVATE_KEY`: Your Ethereum wallet private key
   - `DATABASE_URL`: Your PostgreSQL database URL

## Step 3: Install Dependencies

### Backend Dependencies

```bash
pip install -r requirements.txt
```

### Frontend Dependencies

```bash
npm install
```

## Step 4: Start the Project

### Start the API Server
```bash
python api_server.py
```

### Start the Frontend
```bash
npm run dev
```

### Start the Static HTML Server (if needed)
```bash
python serve_static.py
```

## Step 5: Verify the Application

Open your browser and navigate to:
- Frontend: http://localhost:5001
- API Server: http://localhost:5002
- Static Server: http://localhost:5000

## Project Structure

- `src/`: Frontend React code
  - `components/`: UI components
  - `hooks/`: React hooks
  - `services/`: Service modules
  - `contexts/`: React contexts
  
- `utils/`: Backend utility modules
  - `ai_companion_creator.py`: AI companion creation
  - `enhanced_mcp_specialist.py`: Enhanced MCP functionality
  - `mcp_visualization.py`: MCP visualization logic
  
- `api_server.py`: Main FastAPI server
- `api_companions.py`: Companion API endpoints
- `api_mcp.py`: MCP API endpoints

## Important Notes

- The project uses WebSockets for real-time communication. Ensure that your local machine allows WebSocket connections.
- The MCP visualization requires proper WebSocket connections between the frontend and backend.
- The AI companions use ChromaDB for persistence, ensure it's properly installed and configured.
- For testing, you can use the `python -m pytest tests/test_deepseek_fallback.py -v` command.

## Troubleshooting

- If you encounter database connection issues, verify your PostgreSQL connection and ensure the database exists.
- If API calls fail, check that your API keys are correctly set in the `.env` file.
- For WebSocket connection issues, check if the correct ports are open and accessible.