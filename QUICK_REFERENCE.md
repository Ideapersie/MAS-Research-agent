# Quick Reference Card

## Setup (One-Time)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env: Add your OPENROUTER_API_KEY from https://openrouter.ai/

# 3. Test
python src/config.py
```

## Common Commands

```bash
# Run analysis
python src/main.py "YOUR RESEARCH QUERY"

# Check configuration
python src/main.py --status

# Check cost estimate
python src/main.py --cost

# Run tests
pytest tests/ -v
```

## Example Queries

```bash
# Agentic Frameworks
python src/main.py "Analyze the ReAct framework for LLM reasoning and tool use"
python src/main.py "Compare ReAct, Reflexion, and ReWOO frameworks"

# Training Techniques
python src/main.py "Compare RLHF and DPO alignment techniques"
python src/main.py "Explain Constitutional AI approach for LLM alignment"

# Model Architectures
python src/main.py "Summarize Llama 3 architecture and training innovations"
python src/main.py "Analyze GPT-4 multimodal capabilities"

# Specific Techniques
python src/main.py "Explain chain-of-thought prompting techniques"
python src/main.py "Analyze mixture of experts (MoE) architecture"
```

## File Locations

```
.env                          # Your configuration (API keys)
outputs/reports/              # Generated reports
src/main.py                   # Entry point
src/agents/                   # Agent definitions
src/mcp_servers/              # Tool servers
```

## Configuration (.env)

### Required
```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### Models (Budget Default)
```bash
PERFORMANCE_ANALYST_MODEL=deepseek/deepseek-chat
CRITIQUE_AGENT_MODEL=deepseek/deepseek-chat
SYNTHESIZER_MODEL=google/gemini-flash-1.5
```

### Optional (Email)
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@example.com
```

## Cost Reference

| Configuration | Per Analysis | 100 Analyses |
|--------------|-------------|-------------|
| DeepSeek + Gemini (default) | $0.02-0.05 | $2-5 |
| All DeepSeek | $0.01-0.03 | $1-3 |
| DeepSeek + Claude Haiku | $0.05-0.15 | $5-15 |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "API key not found" | Add `OPENROUTER_API_KEY` to `.env` |
| "No papers found" | Try broader search terms |
| Import errors | Activate venv: `venv\Scripts\activate` |
| Email fails | Email is optional - reports still saved |

## Output Format

Reports saved to: `outputs/reports/TIMESTAMP_query_name.md`

Contains:
- Executive Summary
- Innovations & Contributions
- Critical Analysis
- Balanced Assessment
- Recommendations
- Referenced Papers

## Agent Roles

🎯 **Performance Analyst**: What's innovative? Why does it work?
🔍 **Critique Agent**: What are the limitations? When does it fail?
⚖️ **Synthesizer**: Balanced view with recommendations

## Need Help?

- Setup Guide: [GETTING_STARTED.md](GETTING_STARTED.md)
- Architecture: [CLAUDE.md](CLAUDE.md)
- Full Docs: [README.md](README.md)
