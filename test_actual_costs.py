"""
Test actual cost tracking with OpenRouter API.
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
print("Testing Actual Cost Tracking from OpenRouter")
print("=" * 80)

# Reset tracker
reset_global_tracker()

# Enable usage tracking
print("\n[STEP 1] Enabling usage tracking...")
success = patch_autogen_for_usage_tracking()
if not success:
    print("   [ERROR] Failed to enable usage tracking")
    sys.exit(1)
print("   [OK] Tracking enabled")

# Make test API call
print("\n[STEP 2] Making test API call...")
try:
    import openai

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("   [ERROR] No API key found")
        sys.exit(1)

    openai.api_key = api_key
    openai.api_base = "https://openrouter.ai/api/v1"

    response = openai.ChatCompletion.create(
        model="deepseek/deepseek-chat",
        messages=[{"role": "user", "content": "Say hello in 5 words."}],
        max_tokens=15
    )

    print(f"   [OK] Response: {response['choices'][0]['message']['content']}")
    print(f"   [OK] Response ID: {response.get('id')}")

except Exception as e:
    print(f"   [ERROR] API call failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check captured data
print("\n[STEP 3] Checking captured data...")
tracker = get_global_tracker()
summary = tracker.get_summary()

print(f"   Tokens: {summary['total_tokens']}")
print(f"   Generation IDs captured: {len(summary['generation_ids'])}")
if summary['generation_ids']:
    print(f"   First ID: {summary['generation_ids'][0]}")

# Query actual costs
print("\n[STEP 4] Querying actual costs from OpenRouter...")
actual_costs = tracker.get_actual_costs(api_key)

if actual_costs:
    print(f"\n   [SUCCESS] Retrieved actual costs!")
    print(f"   Number of generations: {actual_costs['count']}")
    print(f"   Total actual cost: ${actual_costs['total_cost']:.6f}")

    for gen in actual_costs['generations']:
        print(f"\n   Generation {gen['id']}:")
        print(f"      Model: {gen['model']}")
        print(f"      Cost: ${gen['cost']:.6f}")
        print(f"      Tokens: {gen['prompt_tokens'] + gen['completion_tokens']}")
else:
    print("   [WARNING] Could not retrieve actual costs")

# Query account credits
print("\n[STEP 5] Querying account credits...")
credits_info = tracker.get_account_credits(api_key)

if credits_info:
    print(f"\n   [SUCCESS] Retrieved credits info!")
    print(f"   Total Credits: ${credits_info['total_credits']:.2f}")
    print(f"   Total Usage:   ${credits_info['total_usage']:.2f}")
    print(f"   Remaining:     ${credits_info['remaining']:.2f}")
else:
    print("   [WARNING] Could not retrieve credits")

print("\n" + "=" * 80)
print("[COMPLETE] Test finished successfully!")
print("=" * 80)
