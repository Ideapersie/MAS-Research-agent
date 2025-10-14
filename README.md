<<<<<<< HEAD
# Research Agent System

Multi-agent system for comprehensive LLM and agentic framework research analysis. Uses specialized AI agents with distinct perspectives (Performance Analyst, Critique Agent, Synthesizer) to create balanced, objective research reviews.

## Features

- 🔍 **Automated Paper Discovery**: Searches ArXiv for relevant research
- 🤖 **Multi-Agent Analysis**: Three specialized agents with distinct perspectives
- 📊 **Balanced Reports**: Combines innovations and limitations into comprehensive analysis
- 💰 **Budget-Friendly**: ~$0.02-0.05 per analysis with default configuration
- 📧 **Email Delivery**: Optional email notifications with reports
- 📝 **Multiple Formats**: Markdown, PDF, JSON, and TXT output

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API key (get from https://openrouter.ai/)
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

# 3. Run analysis
python src/main.py "Analyze the ReAct framework for LLM reasoning"
```

**See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed setup instructions.**

## What It Does

Analyzes research papers from three perspectives:

1. **Performance Analyst**: Identifies innovations, techniques, and benefits
   - Architecture innovations, training methods (RL, RLHF, DPO)
   - Agentic frameworks (ReAct, Reflexion, tool use)
   - Why techniques work and their practical advantages

2. **Critique Agent**: Identifies limitations, challenges, and concerns
   - Reproducibility issues, computational costs
   - Failure modes, generalization limits
   - Ethical concerns, when approaches break down

3. **Synthesizer**: Creates balanced, actionable synthesis
   - Combines both perspectives objectively
   - Contextualizes within research landscape
   - Provides recommendations for researchers and practitioners

## Example Usage

```bash
# Analyze agentic framework
python src/main.py "Analyze ReAct framework for reasoning and tool use"

# Compare alignment techniques
python src/main.py "Compare RLHF and DPO alignment methods"

# Study model architecture
python src/main.py "Summarize Llama 3 architecture and training"

# Check configuration
python src/main.py --status

# See cost estimates
python src/main.py --cost
```

## Cost (Budget-Conscious)

Default configuration: **$0.02-0.05 per analysis**

- Performance Analyst: DeepSeek Chat
- Critique Agent: DeepSeek Chat
- Synthesizer: Gemini Flash 1.5

**100 analyses ≈ $2-5** | See [GETTING_STARTED.md](GETTING_STARTED.md) for cost optimization tips.

## Requirements

- **Required**: OpenRouter API key (https://openrouter.ai/)
- **Optional**: Gmail SMTP credentials (for email delivery)
- Python 3.8+

## Documentation

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Setup and usage guide
- **[CLAUDE.md](CLAUDE.md)** - Architecture and development guide
- **[.env.example](.env.example)** - Configuration template

## Project Structure

```
src/
  agents/              # Agent definitions (Performance, Critique, Synthesizer)
  mcp_servers/         # Tool servers (ArXiv, Storage, Email)
  main.py              # Entry point with GroupChat orchestration
  tools.py             # Tool wrappers for agent integration
  config.py            # Configuration management
outputs/
  reports/             # Generated analysis reports
```

## Technology Stack

- **AutoGen**: Multi-agent orchestration
- **OpenRouter**: LLM API access (budget-friendly)
- **ArXiv API**: Research paper discovery
- **MCP Protocol**: Tool server architecture

## License

MIT License - See LICENSE file for details
