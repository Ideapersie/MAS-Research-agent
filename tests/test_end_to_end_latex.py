"""
Test end-to-end LaTeX generation through storage_tools.
This validates the full pipeline without running the agents.
"""
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from mcp_servers.storage_server.storage_tools import ReportStorage

# Test data
test_report = """# Research Analysis: Test LaTeX Features

## Executive Summary

This test validates special character escaping: 25% discount for $100 items with #tags and _underscores. The **bold text** and *italic text* should render properly. Citations like [Paper 1] should work.

## Technical Details

Math subscripts should work: $T_0$, $\\alpha_t$, and $\\beta_{max}$.

Display math:
\\[
E = mc^2
\\]

## Results

| Metric | Value | Notes |
|--------|-------|-------|
| Accuracy | 95% | High performance |
| **Cost** | **$500** | Budget-friendly |
| Speed | 2.5x | **Faster** than baseline |

## Code Example

Inline code: `print("hello")` and block code:

```python
def test():
    return 42
```
"""

test_papers = [
    {
        'title': 'Test Paper One',
        'authors': ['Author A', 'Author B'],
        'arxiv_id': '2301.00001',
        'abs_url': 'https://arxiv.org/abs/2301.00001',
        'pdf_url': 'https://arxiv.org/pdf/2301.00001.pdf',
        'published': '2023-01-01T00:00:00Z',
        'categories': ['cs.AI']
    },
    {
        'title': 'Test Paper Two',
        'authors': ['Author C', 'Author D'],
        'arxiv_id': '2302.00002',
        'abs_url': 'https://arxiv.org/abs/2302.00002',
        'pdf_url': 'https://arxiv.org/pdf/2302.00002.pdf',
        'published': '2023-02-01T00:00:00Z',
        'categories': ['cs.LG']
    }
]

test_metadata = {
    'agents': ['Test'],
    'timestamp': '2025-10-28T00:00:00',
    'models': {'test': 'test-model'}
}

def main():
    print("=" * 80)
    print("End-to-End LaTeX Generation Test")
    print("=" * 80)

    # Initialize storage tool
    print("\n[TEST 1] Initializing storage tool...")
    storage = ReportStorage()
    print("   [OK] Storage tool initialized")

    # Save as LaTeX
    print("\n[TEST 2] Saving report as LaTeX format...")
    try:
        result = storage.save_report(
            report_content=test_report,
            query="Test LaTeX Features",
            referenced_papers=test_papers,
            metadata=test_metadata,
            format="latex"
        )

        if result['status'] == 'success':
            print(f"   [OK] LaTeX file saved: {result['filename']}")
            print(f"   [OK] BibTeX file saved: {result.get('bib_filepath', 'N/A')}")
            print(f"   [OK] File size: {result['size_bytes']} bytes")
        else:
            print(f"   [ERROR] Failed: {result}")
            return False

    except Exception as e:
        print(f"   [ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Verify files exist
    print("\n[TEST 3] Verifying generated files...")
    tex_path = Path(result['filepath'])
    bib_path = Path(result['bib_filepath'])

    if not tex_path.exists():
        print(f"   [ERROR] .tex file not found: {tex_path}")
        return False
    print(f"   [OK] .tex file exists")

    if not bib_path.exists():
        print(f"   [ERROR] .bib file not found: {bib_path}")
        return False
    print(f"   [OK] .bib file exists")

    # Verify filenames match (base name)
    if tex_path.stem != bib_path.stem:
        print(f"   [ERROR] Filename mismatch: {tex_path.stem} != {bib_path.stem}")
        return False
    print(f"   [OK] Filenames match: {tex_path.stem}")

    # Read and validate content
    print("\n[TEST 4] Validating LaTeX content...")
    tex_content = tex_path.read_text(encoding='utf-8')
    bib_content = bib_path.read_text(encoding='utf-8')

    # Check bibliography reference
    expected_bib_ref = f"\\bibliography{{{tex_path.stem}}}"
    if expected_bib_ref not in tex_content:
        print(f"   [ERROR] Bibliography reference incorrect")
        print(f"   Expected: {expected_bib_ref}")
        return False
    print(f"   [OK] Bibliography reference correct: {expected_bib_ref}")

    # Check special character escaping
    checks = [
        ('25\\%', 'Percentage escaping'),
        ('\\$100', 'Dollar sign escaping'),
        ('\\textbf{bold text}', 'Bold formatting'),
        ('\\textbf{Cost}', 'Bold in table'),
        ('\\textbf{\\$500}', 'Bold with escaped dollar sign'),
        ('\\textbf{Faster}', 'Bold in table cell'),
        ('\\cite{paper1}', 'Citation conversion'),
        ('@article{paper1', 'BibTeX entry 1'),
        ('@article{paper2', 'BibTeX entry 2'),
        ('$T_0$', 'Math subscript preservation'),
        ('$\\alpha_t$', 'Math subscript with Greek')
    ]

    all_ok = True
    for pattern, description in checks:
        if pattern.startswith('@article'):
            # Check in BibTeX
            if pattern in bib_content:
                print(f"   [OK] {description}: found")
            else:
                print(f"   [ERROR] {description}: not found")
                all_ok = False
        else:
            # Check in LaTeX
            if pattern in tex_content:
                print(f"   [OK] {description}: found")
            else:
                print(f"   [ERROR] {description}: not found in LaTeX")
                # Show context for debugging
                print(f"          Searching for: {pattern}")
                all_ok = False

    if not all_ok:
        return False

    print("\n" + "=" * 80)
    print("[SUCCESS] End-to-End LaTeX Test Passed!")
    print("=" * 80)
    print(f"\nGenerated files:")
    print(f"  - {tex_path}")
    print(f"  - {bib_path}")
    print(f"\nTo compile:")
    print(f"  cd {tex_path.parent}")
    print(f"  pdflatex {tex_path.name}")
    print(f"  bibtex {tex_path.stem}")
    print(f"  pdflatex {tex_path.name}")
    print(f"  pdflatex {tex_path.name}")
    print("=" * 80)

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
