"""
Quick test to verify save_report() function works correctly.
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from tools import save_report
from datetime import datetime

# Test data
test_report = """# Research Analysis: Test Report

## Executive Summary
This is a test report to verify the save_report function works correctly.

## Key Findings
- Report saving mechanism functional
- Metadata properly attached
- Timestamp correctly formatted

## Conclusion
If you see this file in outputs/reports/, the save function is working!
"""

test_query = "Test query for save_report function"

test_metadata = {
    "agents": ["Test"],
    "timestamp": datetime.now().isoformat(),
    "test": True
}

print("=" * 80)
print("Testing save_report() function")
print("=" * 80)
print(f"\nReport length: {len(test_report)} characters")
print(f"Query: {test_query}")
print(f"Metadata: {test_metadata}")
print("\nCalling save_report()...")
print("-" * 80)

try:
    result = save_report(
        report_content=test_report,
        query=test_query,
        metadata=test_metadata,
        format="markdown"
    )

    print("\nResult:")
    print(result)
    print("\n" + "=" * 80)
    print("[SUCCESS] Test completed!")
    print("Check outputs/reports/ for the saved file")
    print("=" * 80)

except Exception as e:
    print(f"\n[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
