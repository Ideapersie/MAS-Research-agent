"""
Test LaTeX generation functionality.
"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from mcp_servers.storage_server.latex_formatter import LaTeXFormatter

# Test data - sample research report
test_report = """# Research Analysis: ReAct Framework for LLM Reasoning

## Executive Summary

The ReAct (Reasoning + Acting) framework [Paper 1] represents a significant advancement in LLM agent design by synergistically combining reasoning traces with action execution. Our analysis of 20+ papers reveals that ReAct improves task success rates by **25-30%** over baseline methods while providing interpretability through explicit reasoning chains. The framework implements a thought-action-observation loop that enables dynamic tool selection and error recovery. Training costs approximately $2,500 with 95% success rate on standard benchmarks.

Key innovations include the synergistic combination of chain-of-thought reasoning with action execution, achieving **89% accuracy** on HotpotQA tasks [Paper 2]. However, challenges remain around **computational cost** (3-5x inference overhead) and **prompt sensitivity** requiring careful engineering.

## Key Papers

1. **[Paper 1]** Yao et al., 2023: Original ReAct framework paper
2. **[Paper 2]** Shinn et al., 2023: Reflexion extension with self-reflection
3. **[Paper 3]** Wei et al., 2022: Chain-of-Thought prompting foundation

## Technical Deep-Dive: Innovations & Contributions

### Architecture & Framework Design

The ReAct framework operates through an iterative loop defined as:

\\[
\\text{Loop}: \\text{Thought}_t \\rightarrow \\text{Action}_t \\rightarrow \\text{Observation}_t \\rightarrow \\text{Thought}_{t+1}
\\]

Where each component serves a specific purpose:
- **Thought**: Generated reasoning trace explaining next action
- **Action**: Tool invocation or final answer
- **Observation**: Environment feedback from action

The framework uses temperature scheduling:

\\[
T(t) = T_0 \\cdot \\exp(-\\alpha t) + T_{\\min}
\\]

Where \\(T_0 = 0.7\\), \\(\\alpha = 0.01\\), and \\(T_{\\min} = 0.3\\).

### Training Techniques & Methodologies

Training configurations for optimal performance:

| Parameter | Value Range | Impact |
|-----------|-------------|---------|
| Context Window | 4096-8192 | Critical for multi-step |
| Max Steps | 7-15 | Task dependent |
| Temperature | 0.3-0.7 | Controls exploration |
| Top-p | 0.9-0.95 | Maintains diversity |

The training process involves:

1. **Supervised Fine-Tuning**: Train on human demonstrations
2. **Reinforcement Learning**: Optimize for task success
3. **Curriculum Learning**: Gradually increase difficulty

### Quantitative Results & Benchmarks

Performance comparison on standard benchmarks:

| Benchmark | Baseline | ReAct | Improvement |
|-----------|----------|-------|-------------|
| HotpotQA | 62% | 89% | +27 points |
| FEVER | 71% | 86% | +15 points |
| AlfWorld | 45% | 78% | +33 points |

## Critical Analysis: Limitations & Challenges

### Reproducibility Assessment

**Compute Requirements:**
- Minimum: 2x A100 GPUs (80GB each)
- Training time: 48-72 hours
- Estimated cost: **$2,400-3,600**

**Missing Details:**
- Exact prompt templates not fully disclosed
- Tool interface specifications unclear
- Hyperparameter sensitivity analysis incomplete

### Cost-Benefit Analysis

Computational overhead breakdown:

| Component | Token Usage | Cost Multiplier |
|-----------|-------------|-----------------|
| Reasoning | +200-400 | 2-3x |
| Tool Calls | +100-200 | 1.5-2x |
| Observation | +50-100 | 1.2-1.5x |
| **Total** | **+350-700** | **3-5x** |

### Failure Modes & Edge Cases

Common failure patterns:

- **Reasoning Loops**: Gets stuck repeating same thought (8% of cases)
- **Premature Termination**: Gives up before finding answer (12%)
- **Tool Misuse**: Selects inappropriate tool (15%)

## Comparison with Related Work

Evolution of agentic frameworks:

1. **Chain-of-Thought [Paper 3]**: Pure reasoning, no actions
2. **ReAct [Paper 1]**: Reasoning + acting synergy
3. **Reflexion [Paper 2]**: ReAct + self-reflection

## Recommendations

### For Researchers

1. Investigate more efficient reasoning mechanisms
2. Develop prompt-agnostic architectures
3. Study reasoning compression techniques:

\\[
\\mathcal{L}_{\\text{compress}} = \\mathcal{L}_{\\text{task}} + \\lambda \\mathcal{L}_{\\text{brevity}}
\\]

### For Practitioners

**Implementation Checklist:**
- Start with simple 2-3 tool setups
- Monitor reasoning quality metrics
- Implement cost controls and timeouts
- Use caching for repeated observations

**Cost Optimization:**
```python
# Cache observation results
cache = {}
def cached_observe(action):
    key = hash(action)
    if key in cache:
        return cache[key]
    result = execute(action)
    cache[key] = result
    return result
```

## Conclusion

ReAct represents a major step forward in agentic AI systems, offering practical improvements in multi-step reasoning tasks. The 25-30% accuracy gains justify the 3-5x cost increase for applications requiring high reliability. However, careful prompt engineering and cost monitoring are essential for production deployment.

Future work should focus on reducing computational overhead while maintaining reasoning quality, possibly through distillation or more efficient architectures.
"""

# Sample referenced papers
test_papers = [
    {
        'title': 'ReAct: Synergizing Reasoning and Acting in Language Models',
        'authors': ['Shunyu Yao', 'Jeffrey Zhao', 'Dian Yu', 'Nan Du', 'Izhak Shafran', 'Karthik Narasimhan', 'Yuan Cao'],
        'published': '2023-03-10T00:00:00Z',
        'arxiv_id': '2210.03629',
        'abs_url': 'https://arxiv.org/abs/2210.03629',
        'pdf_url': 'https://arxiv.org/pdf/2210.03629.pdf',
        'categories': ['cs.AI', 'cs.CL'],
        'summary': 'We present ReAct, a novel paradigm to synergize reasoning and acting in language models...'
    },
    {
        'title': 'Reflexion: Language Agents with Verbal Reinforcement Learning',
        'authors': ['Noah Shinn', 'Federico Cassano', 'Beck Labash', 'Ashwin Gopinath', 'Karthik Narasimhan', 'Shunyu Yao'],
        'published': '2023-10-20T00:00:00Z',
        'arxiv_id': '2303.11366',
        'abs_url': 'https://arxiv.org/abs/2303.11366',
        'pdf_url': 'https://arxiv.org/pdf/2303.11366.pdf',
        'categories': ['cs.AI', 'cs.LG'],
        'summary': 'Large language models (LLMs) have been increasingly used to interact with external environments...'
    },
    {
        'title': 'Chain-of-Thought Prompting Elicits Reasoning in Large Language Models',
        'authors': ['Jason Wei', 'Xuezhi Wang', 'Dale Schuurmans', 'Maarten Bosma', 'Brian Ichter', 'Fei Xia', 'Ed Chi', 'Quoc Le', 'Denny Zhou'],
        'published': '2022-01-28T00:00:00Z',
        'arxiv_id': '2201.11903',
        'abs_url': 'https://arxiv.org/abs/2201.11903',
        'pdf_url': 'https://arxiv.org/pdf/2201.11903.pdf',
        'categories': ['cs.CL', 'cs.AI'],
        'summary': 'We explore how generating a chain of thought can improve the ability of large language models...'
    }
]

test_metadata = {
    'agents': ['PerformanceAnalyst', 'CritiqueAgent', 'Synthesizer'],
    'timestamp': '2025-10-23T15:30:00',
    'models': {
        'performance_analyst': 'deepseek/deepseek-chat',
        'critique_agent': 'deepseek/deepseek-chat',
        'synthesizer': 'deepseek/deepseek-chat'
    },
    'usage': {
        'total_tokens': 45230,
        'api_calls': 12
    }
}

def main():
    print("=" * 80)
    print("Testing LaTeX Generation")
    print("=" * 80)

    # Test 1: Create formatter
    print("\n[TEST 1] Creating LaTeX formatter...")
    formatter = LaTeXFormatter()
    print("   [OK] Formatter created successfully")

    # Test 2: Generate LaTeX document
    print("\n[TEST 2] Generating LaTeX document...")
    try:
        latex_content, bibtex_content = formatter.generate_document(
            content=test_report,
            query="Analyze the ReAct framework for LLM reasoning",
            metadata=test_metadata,
            referenced_papers=test_papers,
            bib_basename="test_latex_output"  # Match the output filename
        )
        print(f"   [OK] LaTeX document generated ({len(latex_content)} chars)")
        print(f"   [OK] BibTeX file generated ({len(bibtex_content)} chars)")
    except Exception as e:
        print(f"   [ERROR] Failed to generate document: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 3: Check LaTeX structure
    print("\n[TEST 3] Validating LaTeX structure...")
    required_elements = [
        '\\documentclass',
        '\\begin{document}',
        '\\end{document}',
        '\\section',
        '\\begin{table}',
        '\\begin{itemize}',
        '\\cite{',
        '\\bibliography{test_latex_output}'  # Check for correct bibliography reference
    ]

    for element in required_elements:
        if element in latex_content:
            print(f"   [OK] Found: {element}")
        else:
            print(f"   [MISSING] Not found: {element}")

    # Test 4: Check BibTeX entries
    print("\n[TEST 4] Validating BibTeX structure...")
    required_bibtex = [
        '@article{paper1',
        '@article{paper2',
        '@article{paper3',
        'title={',
        'author={',
        'year={',
        'url={'
    ]

    for element in required_bibtex:
        if element in bibtex_content:
            print(f"   [OK] Found: {element}")
        else:
            print(f"   [MISSING] Not found: {element}")

    # Test 5: Save to file
    print("\n[TEST 5] Saving test outputs...")
    output_dir = project_root / "outputs" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    tex_file = output_dir / "test_latex_output.tex"
    bib_file = output_dir / "test_latex_output.bib"

    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    print(f"   [OK] Saved: {tex_file}")

    with open(bib_file, 'w', encoding='utf-8') as f:
        f.write(bibtex_content)
    print(f"   [OK] Saved: {bib_file}")

    # Test 6: Show preview
    print("\n[TEST 6] LaTeX Document Preview (first 50 lines):")
    print("-" * 80)
    for i, line in enumerate(latex_content.split('\n')[:50], 1):
        print(f"{i:3d} | {line}")
    print("-" * 80)

    print("\n[TEST 7] BibTeX Preview (first 30 lines):")
    print("-" * 80)
    for i, line in enumerate(bibtex_content.split('\n')[:30], 1):
        print(f"{i:3d} | {line}")
    print("-" * 80)

    # Final summary
    print("\n" + "=" * 80)
    print("[SUCCESS] LaTeX Generation Test Complete!")
    print("=" * 80)
    print(f"\nGenerated files:")
    print(f"  - {tex_file}")
    print(f"  - {bib_file}")
    print(f"\nTo compile the LaTeX document:")
    print(f"  1. cd {output_dir}")
    print(f"  2. pdflatex test_latex_output.tex")
    print(f"  3. bibtex test_latex_output")
    print(f"  4. pdflatex test_latex_output.tex")
    print(f"  5. pdflatex test_latex_output.tex")
    print(f"\nOr upload to Overleaf:")
    print(f"  - Upload both .tex and .bib files")
    print(f"  - Overleaf will compile automatically")
    print("=" * 80)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
