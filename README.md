# MAS Research Agent

A multi-agent system that reads the arXiv literature on an LLM or agentic-AI topic and writes a balanced research review: what the work gets right, where it breaks, and what a practitioner should take from it. Three agents with deliberately opposed briefs argue over the same papers so the final report is not a one-sided summary.

```bash
python src/main.py "Analyze the ReAct framework for LLM reasoning"
```

Sample output: [`outputs/samples/react_framework_analysis.pdf`](outputs/samples/react_framework_analysis.pdf), a 4-page LaTeX-typeset review with a BibTeX bibliography of the papers the agents actually retrieved.

## How it works

An AutoGen `GroupChat` runs four participants for up to 20 rounds:

| Agent | Brief | Default model |
|---|---|---|
| Performance Analyst | Searches arXiv several times (main topic, predecessors, competitors, surveys) and extracts the innovations, methods and reported gains | DeepSeek Chat |
| Critique Agent | Reads the same papers looking for reproducibility gaps, compute cost, failure modes and generalisation limits | DeepSeek Chat |
| Synthesizer | Reconciles the two into one review with recommendations | Gemini Flash 1.5 |
| User proxy | Executes tool calls on the agents' behalf | none |

The agents never call tools directly. They request them through the user proxy. Each tool family is also packaged as a standalone MCP server (`server.py` in each folder); in the main workflow, `tools.py` calls the same tool classes in-process:

- `mcp_servers/arxiv_server`: search by query or author, fetch paper details. Every paper returned is tracked so the bibliography lists only papers the agents saw.
- `mcp_servers/storage_server`: writes the report as Markdown, JSON, plain text, PDF (ReportLab) or LaTeX with a `.bib` file. The LaTeX formatter converts the agents' Markdown (headings, tables, bold, citations) and escapes special characters.
- `mcp_servers/email_server`: optional SMTP delivery of the finished report.

Models are routed through OpenRouter, so each agent's model is one environment variable (`PERFORMANCE_ANALYST_MODEL`, `CRITIQUE_AGENT_MODEL`, `SYNTHESIZER_MODEL`). `usage_tracker.py` patches AutoGen to record tokens per call and prints the cost of each run; `python src/main.py --cost` estimates it in advance. With the defaults a review costs roughly $0.02 to $0.05.

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env          # add OPENROUTER_API_KEY
python src/main.py "Compare RLHF and DPO alignment methods"
python src/main.py --status   # check configuration
```

Reports are written to `outputs/reports/` (gitignored). [GETTING_STARTED.md](GETTING_STARTED.md) covers email delivery, output formats and model choices; [CLAUDE.md](CLAUDE.md) is the architecture guide.

## Tests

The files in `tests/` are runnable check scripts rather than a pytest suite:

```bash
python tests/test_save_report.py         # Markdown/JSON/TXT saving
python tests/test_pdf_generation.py      # ReportLab PDF output
python tests/test_latex_generation.py    # Markdown to LaTeX + BibTeX
python tests/test_end_to_end_latex.py    # full LaTeX report, ready for pdflatex or Overleaf
```

`test_api_key.py` and `test_actual_costs.py` make real API calls and need a key.

## Project structure

```
src/
  agents/          Performance Analyst, Critique Agent, Synthesizer (system prompts + factories)
  mcp_servers/     arXiv, storage (PDF/LaTeX/Markdown) and email tool servers
  main.py          GroupChat orchestration and CLI
  tools.py         tool wrappers exposed to the agents, paper tracking
  usage_tracker.py token and cost accounting
  config.py        environment and model configuration
tests/
outputs/samples/   example report
```

## Limitations and next steps

- There is no quantitative evaluation yet. The next step is a grounding check: does each claim in the synthesis trace back to text in a retrieved paper, measured over a fixed set of topics, single agent against three agents.
- Built on AutoGen 0.1.x `GroupChat`, where speaker selection is left to the manager model. An explicit state graph (LangGraph or AutoGen 0.4) would make the analyse, critique, synthesise order deterministic.
- arXiv abstracts and metadata only; the agents do not read full paper text.
- The checks in `tests/` print results for a human to read; converting them to pytest assertions would let them run in CI.
