# FinBank AI - Multi-Agent Banking Assistant

A demonstration application showcasing multi-agent AI orchestration for banking and finance operations. Features a main AI orchestrator that delegates tasks to specialized sub-agents for customer queries, transactions, analytics, fraud detection, and more.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Angular 17 + TypeScript)           │
│       Chat UI  │  Dashboard  │  Data Browser  │  Settings       │
└─────────────────────────────────────────────────────────────────┘
                              ↕ WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI + Python)                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                 ORCHESTRATOR                               │  │
│  │    Receives request → Plans tasks → Routes to agents       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐  │
│  │ Query │ │ Trans │ │Analyt │ │Search │ │ Risk  │ │Export │  │
│  │ Agent │ │ Agent │ │ Agent │ │ Agent │ │ Agent │ │ Agent │  │
│  └───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘  │
│                              ↓                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              LLM PROVIDERS (switchable)                    │  │
│  │    OpenAI  │  Claude  │  Azure OpenAI  │  Ollama          │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    AZURE SQL DATABASE                           │
│  customers │ accounts │ transactions │ branches │ loans │ cards │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **Multi-Agent Orchestration**: Main orchestrator routes requests to specialized agents
- **6 Specialized Agents**:
  - **Query Agent**: Customer and account lookups
  - **Transaction Agent**: Deposits, withdrawals, transfers
  - **Analytics Agent**: Financial reports and statistics
  - **Search Agent**: Find customers and accounts by name
  - **Risk Agent**: Fraud detection and suspicious activity monitoring
  - **Export Agent**: Generate statements and CSV reports
- **Multiple LLM Providers**: Switch between OpenAI, Claude, Azure OpenAI, or Ollama
- **Real-time Updates**: WebSocket streaming for agent status and responses
- **Modern UI**: Angular 17 with Material Design
- **MCP Server**: Model Context Protocol integration for extended tool access

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Angular 17, TypeScript, Angular Material |
| Backend | Python 3.11, FastAPI, SQLAlchemy |
| Database | Azure SQL (Serverless) |
| LLM | OpenAI / Claude / Ollama (switchable) |
| MCP | Python MCP SDK |
| Infrastructure | Terraform, AKS, Azure Container Registry |

## Prerequisites

- Node.js 20+
- Python 3.11+
- Docker & Docker Compose
- Azure CLI (for deployment)
- Terraform (for infrastructure)

## Quick Start (Local Development)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd finbank-ai
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:4200
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

5. **Seed sample data**
   ```bash
   docker-compose exec backend python seed_data.py
   ```

## Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
ng serve
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQL connection string | (required) |
| `OPENAI_API_KEY` | OpenAI API key | (optional) |
| `ANTHROPIC_API_KEY` | Anthropic API key | (optional) |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI key | (optional) |
| `OLLAMA_HOST` | Ollama server URL | http://localhost:11434 |
| `DEFAULT_LLM_PROVIDER` | Default LLM to use | openai |

## Sample Queries

Try these queries in the chat interface:

```
"Show me all customers"
"What's John Smith's total balance across all accounts?"
"Transfer $500 from John's checking to his savings"
"How many transactions happened at Downtown branch this week?"
"Show me suspicious transactions over $10,000"
"Generate a transaction report for this month"
```

## Azure Deployment

### 1. Deploy Infrastructure

```bash
cd infra
terraform init
terraform plan -var="sql_admin_password=YourSecurePassword123!"
terraform apply -var="sql_admin_password=YourSecurePassword123!"
```

### 2. Build and Push Docker Images

```bash
# Get ACR credentials from Terraform output
ACR_NAME=$(terraform output -raw acr_login_server)

# Login to ACR
az acr login --name $ACR_NAME

# Build and push
docker build -t $ACR_NAME/finbank-backend:latest ./backend
docker build -t $ACR_NAME/finbank-frontend:latest ./frontend
docker build -t $ACR_NAME/finbank-mcp:latest ./mcp-server

docker push $ACR_NAME/finbank-backend:latest
docker push $ACR_NAME/finbank-frontend:latest
docker push $ACR_NAME/finbank-mcp:latest
```

### 3. Deploy to AKS

```bash
# Get AKS credentials
az aks get-credentials --resource-group rg-finbank-ai-dev --name aks-finbank-ai-dev

# Update secrets in deployment.yaml with real values
kubectl apply -f infra/k8s/

# Get external IP
kubectl get svc finbank-frontend -n finbank
```

## Project Structure

```
finbank-ai/
├── frontend/                 # Angular 17 application
│   ├── src/app/
│   │   ├── components/       # UI components
│   │   ├── services/         # API and WebSocket services
│   │   └── models/           # TypeScript interfaces
│   └── Dockerfile
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── agents/           # Specialized AI agents
│   │   ├── llm/              # LLM provider implementations
│   │   ├── orchestrator.py   # Main AI orchestrator
│   │   └── main.py           # FastAPI entry point
│   └── Dockerfile
├── mcp-server/               # MCP server for banking tools
├── infra/                    # Terraform & Kubernetes configs
│   ├── main.tf
│   └── k8s/
├── docker-compose.yml        # Local development setup
└── README.md
```

## Cost Estimate (Azure)

| Resource | Tier | Monthly Cost |
|----------|------|--------------|
| AKS (1 node B2s) | Free control plane | ~$30 |
| Azure SQL | Serverless (auto-pause) | ~$5-15 |
| Container Registry | Basic | ~$5 |
| Public IP | Standard | ~$5 |
| **Total** | | **~$50/month** |

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
