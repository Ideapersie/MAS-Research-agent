"""
Test PDF generation functionality.
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from tools import save_report
from datetime import datetime

# Test data with more complex markdown for PDF testing
test_report = """# Research Analysis: ReAct Framework

## Executive Summary
The ReAct (Reasoning + Acting) framework represents a significant advancement in LLM agent design by synergistically combining reasoning traces with action execution.

## Key Innovations

### 1. Synergy of Reasoning and Acting
- **Thought-Action-Observation Loop**: The framework alternates between generating reasoning traces (thoughts) and taking actions
- **Interpretability**: Reasoning traces make the agent's decision-making process transparent
- **Dynamic Tool Selection**: Agent can reason about which tools to use based on context

### 2. Technical Implementation
```
Query → LLM generates thought → LLM selects action →
Environment executes action → Observation returned →
LLM generates next thought → ...
```

### 3. Benefits
- Improved decision-making through explicit reasoning
- Better handling of complex multi-step tasks
- Enhanced error recovery through reasoning about failures
- Transparency in agent behavior

## Critical Analysis

### Limitations
1. **Computational Cost**: 3-5x higher inference cost due to additional reasoning steps
2. **Prompt Sensitivity**: Performance heavily depends on prompt engineering
3. **Model Dependency**: Requires strong base models (GPT-3.5+, Claude, etc.)
4. **Failure Modes**: Can get stuck in reasoning loops on ambiguous tasks

### Reproducibility Challenges
- Exact prompt templates not always disclosed
- Performance varies significantly across models
- Tool interfaces may differ from implementation to implementation

## Balanced Assessment

**When to Use**:
- Tasks requiring complex reasoning and tool interaction
- Scenarios where interpretability is important
- Multi-step problem-solving with external knowledge access

**When to Avoid**:
- Simple tasks where reasoning overhead is unnecessary
- Cost-sensitive applications
- Real-time applications requiring low latency

## Recommendations

### For Researchers
- Investigate more efficient reasoning mechanisms
- Study prompt-agnostic architectures
- Explore reasoning compression techniques

### For Practitioners
- Start with simpler agent patterns, upgrade to ReAct if needed
- Budget for 3-5x inference costs
- Implement robust error handling
- Monitor reasoning quality in production

### For the Field
- Standardize tool interfaces
- Create benchmarks for reasoning quality
- Develop best practices for prompt engineering

## References
[Generated from ArXiv papers on ReAct framework]
"""

test_query = "Analyze the ReAct framework for LLM reasoning"

test_metadata = {
    "agents": ["PerformanceAnalyst", "CritiqueAgent", "Synthesizer"],
    "timestamp": datetime.now().isoformat(),
    "models": {
        "performance_analyst": "deepseek/deepseek-chat",
        "critique_agent": "deepseek/deepseek-chat",
        "synthesizer": "anthropic/claude-3.5-sonnet"
    },
    "usage": {
        "total_prompt_tokens": 89234,
        "total_completion_tokens": 32747,
        "total_tokens": 121981,
        "api_calls": 8,
        "model_breakdown": {
            "deepseek/deepseek-chat": {
                "prompt_tokens": 72150,
                "completion_tokens": 25890,
                "total_tokens": 98040,
                "calls": 6
            },
            "anthropic/claude-3.5-sonnet": {
                "prompt_tokens": 17084,
                "completion_tokens": 6857,
                "total_tokens": 23941,
                "calls": 2
            }
        }
    }
}

print("=" * 80)
print("Testing PDF Generation")
print("=" * 80)
print(f"\nReport length: {len(test_report)} characters")
print(f"Query: {test_query}")
print("\n" + "-" * 80)

# Test Markdown save
print("\n[TEST 1] Saving as Markdown...")
try:
    md_result = save_report(
        report_content=test_report,
        query=test_query,
        metadata=test_metadata,
        format="markdown"
    )
    print(md_result)
except Exception as e:
    print(f"[ERROR] Markdown save failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "-" * 80)

# Test PDF save
print("\n[TEST 2] Saving as PDF...")
try:
    pdf_result = save_report(
        report_content=test_report,
        query=test_query,
        metadata=test_metadata,
        format="pdf"
    )
    print(pdf_result)
except Exception as e:
    print(f"[ERROR] PDF save failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("[COMPLETE] Check outputs/reports/ for both files")
print("=" * 80)
