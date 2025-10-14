# Multi-agent Research System 

## Project Overview

This is an AutoGen-based multi-agent research analysis system designed to help keep up with the rapid pace of LLM and agentic framework research. The system uses specialized agents with distinct analytical perspectives (Performance Analyst, Critique Agent, Synthesizer) to create comprehensive, objective reviews that highlight both contributions and limitations of research papers.

**Scope**: Covers LLM models, agentic frameworks (e.g., ReAct, Chain-of-Thought), training techniques (RL, SFT, RLHF), and architectural innovations.

## Environment Setup

### Required Environment Variables
Create a `.env` file based on [.env.example](.env.example):

```bash
# OpenRouter API for AutoGen agents
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Model assignments for each agent
PERFORMANCE_ANALYST_MODEL=deepseek/deepseek-chat
CRITIQUE_AGENT_MODEL=deepseek/deepseek-chat
SYNTHESIZER_MODEL=anthropic/claude-3.5-sonnet

# SMTP configuration for email delivery
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@example.com

# ArXiv API configuration
ARXIV_API_BASE=http://export.arxiv.org/api/query
ARXIV_MAX_RESULTS=10

# Report storage location
OUTPUT_DIR=outputs/reports
```

### Installation
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Unix/macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Development Commands

### Running the System

```bash
# Run the complete research analysis workflow
python src/main.py "Analyze the ReAct framework for LLM reasoning"

# Example queries
python src/main.py "Summarize Llama 3.1 architecture and training techniques"
python src/main.py "Compare recent RLHF vs DPO alignment methods"
python src/main.py "Analyze Constitutional AI approach"

# Run individual MCP servers (for testing)
python src/mcp_servers/arxiv_server/server.py
python src/mcp_servers/email_server/server.py
python src/mcp_servers/storage_server/server.py
```

### Testing
```bash
# Run all tests
pytest

# Run with async support and verbose output
pytest -v

# Run specific test files
pytest tests/test_agents.py
pytest tests/test_arxiv_server.py
pytest tests/test_email_server.py

# Run with coverage
pytest --cov=src tests/
```

## Key Implementation Details

### AutoGen Configuration
- Uses `config_list` with OpenRouter API key for LLM access
- Each agent has a specialized `system_message` defining its analytical perspective
- Agents are registered with specific models (deepseek for analysis, Claude for synthesis)
- Temperature and max_tokens configured per agent based on task requirements


### Conversation Flow Pattern
```
User Proxy: Initiates with research query
  ↓
[Parallel Execution]
Performance Analyst:
  - Searches papers on the topic
  - Analyzes innovations, techniques, benefits
  - Documents what makes work unique

Critique Agent:
  - Searches papers and related work
  - Identifies limitations, costs, challenges
  - Documents reproducibility concerns
  ↓
Synthesizer:
  - Combines both perspectives
  - Creates balanced, comprehensive analysis
  - Provides contextualized recommendations
  ↓
User Proxy:
  - Saves report (Storage Tool)
  - Sends email notification (Email Tool)
```

### Tool Integration
- **Search Tool**: Calls ArXiv MCP server to retrieve papers
  - Supports keyword search, author search, paper ID lookup
  - Returns structured metadata including abstracts, categories, URLs
- **Storage Tool**: Saves reports with metadata and references
  - Tracks which agents contributed, models used, timestamp
- **Email Tool**: Triggers email delivery of final report
  - Converts markdown to HTML for rich email formatting
- All tools are registered with AutoGen agents using tool registration API
- MCP servers communicate via stdio protocol


## File Organization

```
src/
  agents/              # Agent definitions and system messages
    performance_analyst.py    # Analyzes innovations, techniques, benefits
    critique_agent.py         # Analyzes limitations, costs, concerns
    synthesizer.py           # Creates balanced synthesis
    user_proxy.py            # Orchestrates workflow
  mcp_servers/         # Tool servers
    arxiv_server/      # Paper search and retrieval
      server.py        # MCP server implementation
      arxiv_tools.py   # ArXiv API integration
      __init__.py
    email_server/      # Report delivery
      server.py        # MCP server implementation
      email_tools.py   # SMTP functionality
      __init__.py
    storage_server/    # Report storage
      server.py        # MCP server implementation
      storage_tools.py # File storage with PDF generation
      __init__.py
  main.py              # Entry point, orchestrates GroupChat
  tools.py             # Tool registration and wrappers
outputs/
  reports/             # Generated analysis reports
config/                # AutoGen configuration
tests/                 # Unit and integration tests
.env.example           # Environment variable template
requirements.txt       # Python dependencies
```
## Future Implementations

- Additional agent perspectives (e.g., Reproducibility Agent, Ethics Agent, Benchmarking Agent)
- Support for non-ArXiv sources (Google Scholar, Semantic Scholar, Papers with Code)
- Interactive website (user asks follow-up questions, agents provide deeper analysis)
- Automated scheduling (daily/weekly research digests on specific topics)
- Citation graph analysis (track how papers build on each other)
- Trending topic detection (identify emerging research directions)
- Multi-paper comparison mode (side-by-side analysis of competing approaches)
