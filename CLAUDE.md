# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AutoGen-based multi-agent research analysis system designed to help keep up with the rapid pace of LLM and agentic framework research. The system uses specialized agents with distinct analytical perspectives (Performance Analyst, Critique Agent, Synthesizer) to create comprehensive, objective reviews that highlight both contributions and limitations of research papers.

**Scope**: Covers LLM models, agentic frameworks (e.g., ReAct, Chain-of-Thought), training techniques (RL, SFT, RLHF), and architectural innovations.

## Core Architecture

### Multi-Agent Design Pattern

The system implements a three-agent collaboration pattern:

1. **Performance Analyst Agent**: Comprehensive analysis of contributions and innovations
   - **Beyond benchmarks**: Analyzes what makes the work unique, novel techniques employed
   - **Model analysis**: Architecture innovations, training methodologies (RL, SFT, RLHF, DPO), scaling laws
   - **Framework analysis**: Agentic patterns (ReAct, ReWOO, Reflexion), reasoning approaches, tool use
   - **Techniques**: Prompt engineering, fine-tuning strategies, inference optimizations
   - **Benefits**: Why these approaches work, theoretical foundations, practical advantages
   - Example outputs: "Uses Constitutional AI for alignment", "Novel attention mechanism reduces memory by X%", "ReAct framework enables better tool selection through reasoning traces"

2. **Critique Agent**: Deep analysis of limitations, challenges, and concerns
   - **Beyond failure modes**: Analyzes reproducibility, generalization limits, cost-benefit tradeoffs
   - **Model critique**: Training data concerns, inference costs, failure cases, bias issues
   - **Framework critique**: Scalability limits, complexity overhead, when patterns break down
   - **Techniques critique**: Reproducibility challenges, hyperparameter sensitivity, computational requirements
   - **Practical concerns**: Deployment challenges, ethical considerations, over-claimed capabilities
   - Example outputs: "ReAct framework adds 3-5x inference cost", "Benefits diminish on out-of-distribution tasks", "Requires proprietary data not available for reproduction"

3. **Synthesizer Agent**: Creates balanced, comprehensive synthesis
   - Combines perspectives from both analyst agents
   - Produces objective review highlighting innovations alongside limitations
   - Contextualizes findings within broader research landscape
   - Provides actionable insights and recommendations
   - Output format: Structured markdown reports

4. **User Proxy**: Orchestrates the workflow and triggers tools

### Agent Orchestration (GroupChat)
- Uses AutoGen's GroupChat and GroupChatManager
- Conversation flow: User Proxy → Performance Analyst & Critique Agent (parallel analysis) → Synthesizer → User Proxy
- GroupChatManager coordinates agent turns and maintains conversation context

### MCP Server Integration

Three MCP servers provide tools accessible to agents:

1. **ArXiv Server** ([src/mcp_servers/arxiv_server/](src/mcp_servers/arxiv_server/))
   - Tools: `search_arxiv`, `search_arxiv_by_author`, `get_arxiv_paper`
   - Used by analyst agents to retrieve research papers
   - API: ArXiv REST API with feedparser for XML parsing
   - Searches across CS.AI, CS.CL, CS.LG categories

2. **Storage Server** ([src/mcp_servers/storage_server/](src/mcp_servers/storage_server/))
   - Tools: `save_report`, `list_reports`, `get_report`, `delete_report`, `get_storage_info`
   - Saves analysis reports in multiple formats (PDF, markdown, JSON, TXT)
   - Auto-generates references section for cited papers with full metadata
   - Supports custom metadata for tracking analysis provenance

3. **Email Server** ([src/mcp_servers/email_server/](src/mcp_servers/email_server/))
   - Tools: `send_report_email`, `test_email_connection`
   - Delivers final synthesized reports via email with notifications
   - Supports markdown-to-HTML conversion for rich formatting
   - Handles both plain text and multipart MIME messages

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

### Agent System Messages (Critical)

When modifying agent behavior, focus on the `system_message` prompts:

**Performance Analyst**: Must analyze:
- Architectural innovations and what makes them unique
- Training techniques (RL, SFT, RLHF, DPO) and their benefits
- Agentic framework patterns (ReAct, Reflexion, tool use)
- Novel approaches to reasoning, memory, planning
- Why techniques work theoretically and practically
- Efficiency gains and optimization strategies

**Critique Agent**: Must analyze:
- Reproducibility challenges and data requirements
- Computational costs and scalability limits
- Failure modes and edge cases
- Generalization limitations
- Ethical concerns and bias issues
- When frameworks/techniques break down
- Over-claimed capabilities vs. actual performance

**Synthesizer**: Must provide:
- Balanced integration of both perspectives
- Contextualization within broader research trends
- Actionable insights for practitioners
- Clear recommendations with caveats

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

### Report Generation
Final reports are markdown-formatted with these sections:
- **Executive Summary**: High-level overview of findings
- **Innovations & Contributions**: From Performance Analyst
  - Architecture/framework details
  - Training techniques and methodologies
  - What makes the approach unique
  - Theoretical and practical benefits
- **Critical Analysis**: From Critique Agent
  - Limitations and failure modes
  - Reproducibility concerns
  - Cost-benefit analysis
  - Ethical considerations
- **Balanced Synthesis**: From Synthesizer
  - Integration of perspectives
  - Contextualization within research landscape
  - Recommendations for practitioners
- **References**: Auto-generated with full ArXiv paper metadata

Reports saved to `outputs/reports/` with timestamp-based filenames.

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

## Important Implementation Notes

### AutoGen GroupChat Setup
- Register all agents in GroupChat: `[user_proxy, performance_analyst, critique_agent, synthesizer]`
- GroupChatManager controls turn-taking and conversation flow
- Set `max_round` appropriately to allow full analysis cycle (suggested: 10-15)
- Use speaker selection strategies to ensure both analysts contribute before synthesis

### Tool Function Registration
- Tools must be registered with agents using `@user_proxy.register_for_execution()`
- Tool schemas must match MCP tool input schemas
- Handle async tool calls if MCP servers are async
- Implement error handling for tool failures

### ArXiv API Usage
- Query format: `all:{query}` for general search, `au:{name}` for author search
- Rate limiting: ArXiv has request limits (~1 request per 3 seconds), implement delays if needed
- Paper metadata includes: title, authors, abstract, categories, published date, PDF URL, DOI
- For agentic frameworks, search terms like "ReAct", "agent", "tool use", "reasoning"
- For training techniques, search "RLHF", "reinforcement learning", "supervised fine-tuning"

### Error Handling
- All MCP tool calls should have try-except blocks
- Return descriptive error messages to agents for context
- Log failures for debugging (agents may retry or adjust strategy)
- Handle network timeouts gracefully

### SMTP Configuration
- Gmail requires "App Passwords" (not regular password)
- Enable 2FA and generate App Password in Google Account settings
- Test email connection before running full workflow: use `test_email_connection` tool
- Email delivery is optional; reports always saved locally first

### PDF Generation
- Requires reportlab and markdown2 packages
- Falls back to markdown if PDF libraries unavailable
- PDF styling uses custom ParagraphStyle for headers and body text
- Long abstracts may need pagination handling

## Typical Workflow Example

1. User provides research query: "Analyze the ReAct framework for LLM reasoning and tool use"
2. User Proxy initiates GroupChat with query
3. Performance Analyst:
   - Searches ArXiv for ReAct paper and related work
   - Extracts: synergy of reasoning + acting, thought-action-observation traces
   - Analyzes benefits: improved decision-making, interpretability, dynamic tool selection
   - Documents: combines chain-of-thought with action execution
4. Critique Agent:
   - Searches for limitations and follow-up work
   - Identifies: 3-5x inference cost, prompt sensitivity, requires strong base model
   - Documents: failure on ambiguous tasks, tool selection errors, scaling challenges
5. Synthesizer:
   - Combines findings into balanced review
   - Context: builds on chain-of-thought, influences subsequent frameworks (ReWOO, Reflexion)
   - Recommendations: use for tasks requiring tool interaction, consider cost tradeoffs
6. User Proxy:
   - Saves report to `outputs/reports/20231015_143022_ReAct_framework_analysis.md`
   - Generates PDF version
   - Emails report to configured recipient with subject "Research Analysis: ReAct Framework"

## Future Extensions

- Additional agent perspectives (e.g., Reproducibility Agent, Ethics Agent, Benchmarking Agent)
- Support for non-ArXiv sources (Google Scholar, Semantic Scholar, Papers with Code)
- Interactive refinement (user asks follow-up questions, agents provide deeper analysis)
- Automated scheduling (daily/weekly research digests on specific topics)
- Citation graph analysis (track how papers build on each other)
- Trending topic detection (identify emerging research directions)
- Multi-paper comparison mode (side-by-side analysis of competing approaches)
