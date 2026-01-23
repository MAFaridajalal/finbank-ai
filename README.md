# FinBank AI - Multi-Agent Banking System

A demonstration application showcasing **multi-agent AI orchestration** for banking operations. Features an LLM-powered orchestrator that intelligently routes tasks to specialized sub-agents using MCP (Model Context Protocol).

## 🎯 Purpose

This is a **demo application** designed to showcase:
- Multi-agent orchestration patterns
- LLM-powered task planning and routing
- Agent collaboration for complex queries
- MCP server integration
- Banking-grade validation and edge case handling

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Angular 18 + TypeScript)           │
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
│  │ Query │ │ CRUD  │ │Analyt │ │Search │ │ Risk  │ │Export │  │
│  │ Agent │ │ Agent │ │ Agent │ │ Agent │ │ Agent │ │ Agent │  │
│  └───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘  │
│                              ↓                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              LLM PROVIDERS (switchable)                    │  │
│  │    OpenAI  │  Claude  │  Ollama (default)                 │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    SQLite DATABASE (Demo)                       │
│  customers │ accounts │ transactions │ branches │ tiers         │
└─────────────────────────────────────────────────────────────────┘
```

## ✨ Features

### Multi-Agent System
- **Orchestrator**: LLM-powered task planning and intelligent agent routing
- **7 Specialized Agents**:
  - **Query Agent**: Customer and account lookups, data retrieval
  - **CRUD Agent**: Create, update, delete operations with validation
  - **Analytics Agent**: Financial calculations, metrics, aggregations
  - **Search Agent**: Fuzzy search, partial name matching
  - **Transaction Agent**: Transaction history and analysis
  - **Risk Agent**: Risk assessment and fraud detection
  - **Export Agent**: Report generation (CSV, PDF)

### Banking Features
- ✅ Customer registration with validation (duplicate detection)
- ✅ Banking-grade data integrity (email/phone uniqueness)
- ✅ Safety rules (prevent deletion of customers with active accounts)
- ✅ Case-insensitive search
- ✅ Multi-agent collaboration for complex queries
- ✅ Real-time WebSocket chat interface

### Technical Features
- 🔄 Multiple LLM providers (Ollama, OpenAI, Claude)
- 🎯 Regex-based data extraction (more reliable than LLM)
- 🔌 WebSocket streaming for real-time updates
- 🐳 Docker support
- 🧪 Comprehensive test suite (85.7% pass rate)
- 📝 VS Code debugging configuration

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Ollama** (for local LLM) - [Install Ollama](https://ollama.ai)
- **Git**

Optional:
- Docker & Docker Compose
- OpenAI API key (if not using Ollama)
- Claude API key (if not using Ollama)

## 🚀 Quick Start (5 minutes)

### Option 1: Local Development (Recommended for Demo)

1. **Clone the repository**
   ```bash
   git clone https://github.com/MAFaridajalal/finbank-ai.git
   cd finbank-ai
   ```

2. **Set up Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env if needed (default uses Ollama)
   ```

4. **Install Ollama and pull the model**
   ```bash
   # Install from https://ollama.ai
   ollama pull llama3.2
   ```

5. **Initialize database with seed data**
   ```bash
   python seed_data.py
   ```

6. **Start the backend**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **In a new terminal, set up Frontend**
   ```bash
   cd frontend
   npm install
   ng serve
   ```

8. **Access the application**
   - Frontend: http://localhost:4200
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Docker Compose

```bash
# Start all services
docker-compose up -d

# Seed database
docker-compose exec backend python seed_data.py

# Access at http://localhost:4200
```

## 📚 Documentation

- **[TESTING_REPORT.md](TESTING_REPORT.md)** - Comprehensive test results and analysis
- **[CHAT_COMMANDS_REFERENCE.md](CHAT_COMMANDS_REFERENCE.md)** - All available chat commands
- **[DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md)** - VS Code debugging setup
- **[VSCODE_DEBUGGING_GUIDE.md](VSCODE_DEBUGGING_GUIDE.md)** - Detailed debugging instructions

## 🎮 Try It Out

### Sample Chat Commands

**Basic Queries:**
```
List all customers
Show customer 1
How many customers do we have?
Show all Premium tier customers
```

**Search:**
```
Find customer John Smith
Search for customers named Erik
```

**Analytics:**
```
Calculate total balance across all accounts
Show customer distribution by tier
What's the average account balance?
```

**CRUD Operations:**
```
Add a new customer named John Doe with email john@bank.com, phone 555-1234
Update customer 5, change email to new@email.com
Delete customer 14
```

**Complex Multi-Agent Queries:**
```
Show me full details of all Premium tier users
Find high-value customers and assess their risk
Calculate total balance for VIP tier customers
```

**Banking Edge Cases:**
```
Delete customer John Smith (will fail safely if has accounts)
Find customer ERIK MOL (case-insensitive)
```

See **[CHAT_COMMANDS_REFERENCE.md](CHAT_COMMANDS_REFERENCE.md)** for complete list.

## 🗂️ Project Structure

```
finbank-ai/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── agents/            # 7 specialized agents
│   │   │   ├── query_agent.py
│   │   │   ├── crud_agent.py
│   │   │   ├── analytics_agent.py
│   │   │   ├── search_agent.py
│   │   │   ├── transaction_agent.py
│   │   │   ├── risk_agent.py
│   │   │   └── export_agent.py
│   │   ├── llm/               # LLM providers
│   │   │   ├── ollama_provider.py
│   │   │   ├── openai_provider.py
│   │   │   └── claude_provider.py
│   │   ├── orchestrator.py    # Main orchestrator
│   │   ├── main.py            # FastAPI app
│   │   └── database.py        # SQLAlchemy setup
│   ├── requirements.txt
│   └── seed_data.py           # Sample data
├── frontend/                   # Angular 18 frontend
│   ├── src/app/
│   │   ├── components/        # UI components
│   │   │   ├── chat/
│   │   │   ├── dashboard/
│   │   │   ├── data-browser/
│   │   │   └── register/
│   │   └── services/          # API services
│   └── package.json
├── mcp-server/                # MCP server implementation
├── infra/                     # Infrastructure (K8s, Terraform)
├── TESTING_REPORT.md          # Test results
├── CHAT_COMMANDS_REFERENCE.md # Command reference
└── README.md                  # This file
```

## ⚙️ Configuration

### Environment Variables

Create `.env` file in backend directory:

```env
# LLM Provider (ollama, openai, or claude)
DEFAULT_LLM_PROVIDER=ollama

# Ollama (default, no API key needed)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2

# OpenAI (optional)
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4

# Claude (optional)
ANTHROPIC_API_KEY=your-api-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Database (SQLite for demo)
DATABASE_URL=sqlite:///./finbank.db
```

## 🧪 Testing

Run comprehensive test suite:

```bash
cd backend
source venv/bin/activate
python test_crud_operations.py
```

**Test Results: 12/14 tests passing (85.7%)**

See [TESTING_REPORT.md](TESTING_REPORT.md) for detailed results.

## 🎯 Demo Tips

1. **Start with simple queries** to see single-agent execution
2. **Try complex queries** to see multi-agent collaboration
3. **Test edge cases** (duplicate emails, delete with accounts)
4. **Monitor backend logs** to see agent routing
5. **Use VS Code debugging** to trace execution flow

## 🐛 Debugging

VS Code debugging is pre-configured:

1. Open VS Code in the project root
2. Press F5 to start debugging
3. Set breakpoints in orchestrator or agents
4. See [DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md) for details

## 📊 Architecture Highlights

### Orchestrator Pattern
- Receives user query
- Uses LLM to create execution plan
- Routes tasks to appropriate agents
- Aggregates results
- Returns formatted response

### Agent Collaboration
- **Sequential**: Task B waits for Task A result
- **Parallel**: Independent tasks run simultaneously
- **Error Handling**: Graceful degradation on agent failure

### Banking Safety
- Prevents deletion of customers with active accounts
- Validates email/phone uniqueness
- Case-insensitive searches
- Transaction rollback on errors

## 🚧 Known Limitations

1. **UPDATE by name via chat** - Orchestrator task rephrasing issue
   - **Workaround**: Use customer ID instead

2. **DELETE by name via chat** - Name parsing issue
   - **Workaround**: Use customer ID instead

3. **LLM extraction** - llama3.2 sometimes returns code instead of JSON
   - **Solution**: Implemented regex-based extraction as fallback

See [TESTING_REPORT.md](TESTING_REPORT.md) for complete analysis.

## 🔮 Future Enhancements

For demo/architecture improvements:
- Agent performance visualization dashboard
- MCP server registry and discovery UI
- Agent communication flow diagram
- Load balancing demo with multiple agent instances
- Streaming agent responses visualization
- Interactive agent testing playground

See [CHAT_COMMANDS_REFERENCE.md](CHAT_COMMANDS_REFERENCE.md) for detailed enhancement suggestions.

## 📄 License

This is a demo/educational project.

## 🤝 Contributing

This is a demonstration project. Feel free to fork and experiment!

## 📧 Contact

For questions about the architecture or implementation, see the documentation files or open an issue.

---

**Built with:** Python 3.11, FastAPI, Angular 18, SQLite, Ollama

**Purpose:** Multi-agent orchestration architecture demonstration

**Test Coverage:** 85.7% (12/14 tests passing)

**Repository:** https://github.com/MAFaridajalal/finbank-ai
