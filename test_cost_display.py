"""
Test the actual cost display with before/after credits.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from usage_tracker import patch_autogen_for_usage_tracking, get_global_tracker, reset_global_tracker

print("=" * 80)
print("Testing Cost Display with Before/After Credits")
print("=" * 80)

# Reset and enable tracking
reset_global_tracker()
patch_autogen_for_usage_tracking()

api_key = os.getenv("OPENROUTER_API_KEY")
tracker = get_global_tracker()

# Get initial credits
print("\n[1] Getting initial account balance...")
initial_credits = tracker.get_account_credits(api_key)
if initial_credits:
    print(f"    Initial balance: ${initial_credits['remaining']:.2f}")
else:
    print("    [ERROR] Could not get initial credits")
    sys.exit(1)

# Make a few API calls
print("\n[2] Making test API calls...")
import openai
openai.api_key = api_key
openai.api_base = "https://openrouter.ai/api/v1"

for i in range(3):
    response = openai.ChatCompletion.create(
        model="deepseek/deepseek-chat",
        messages=[{"role": "user", "content": f"Count to {i+1}"}],
        max_tokens=10
    )
    print(f"    Call {i+1}: {response['choices'][0]['message']['content'][:30]}...")

# Get final credits
print("\n[3] Getting final account balance...")
final_credits = tracker.get_account_credits(api_key)
if final_credits:
    print(f"    Final balance: ${final_credits['remaining']:.2f}")
else:
    print("    [ERROR] Could not get final credits")
    sys.exit(1)

# Calculate and display
print("\n" + "=" * 80)
print("COST SUMMARY")
print("=" * 80)

actual_cost = initial_credits['remaining'] - final_credits['remaining']

print(f"\nBefore Analysis:   ${initial_credits['remaining']:.2f}")
print(f"After Analysis:    ${final_credits['remaining']:.2f}")
print(f"--")
print(f"Actual Cost:       ${actual_cost:.6f} USD")

# Get token usage
summary = tracker.get_summary()
print(f"\nTotal Tokens:      {summary['total_tokens']}")
print(f"API Calls:         {summary['api_calls']}")

if actual_cost > 0:
    cost_per_token = actual_cost / summary['total_tokens'] if summary['total_tokens'] > 0 else 0
    print(f"Cost per Token:    ${cost_per_token:.8f}")

print("\n" + "=" * 80)
print("[SUCCESS] Test completed!")
print("=" * 80)
