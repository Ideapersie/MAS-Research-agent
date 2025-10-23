"""
Test usage tracking functionality with a simple API call.
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
print("Testing Usage Tracking")
print("=" * 80)

# Reset tracker
reset_global_tracker()

# Enable usage tracking
print("\n[STEP 1] Patching OpenAI client for usage tracking...")
success = patch_autogen_for_usage_tracking()
if success:
    print("   [OK] Usage tracking enabled")
else:
    print("   [ERROR] Failed to enable usage tracking")
    sys.exit(1)

# Make a test API call using OpenAI client directly
print("\n[STEP 2] Making test API call to OpenRouter...")
try:
    import openai

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("   [ERROR] No API key found in .env")
        sys.exit(1)

    # Configure OpenAI 0.28.1 for OpenRouter
    openai.api_key = api_key
    openai.api_base = "https://openrouter.ai/api/v1"

    response = openai.ChatCompletion.create(
        model="deepseek/deepseek-chat",
        messages=[
            {"role": "user", "content": "Say 'test successful' in exactly 3 words."}
        ],
        max_tokens=10
    )

    print(f"   [OK] Response: {response['choices'][0]['message']['content']}")

except Exception as e:
    print(f"   [ERROR] API call failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check if usage was tracked
print("\n[STEP 3] Checking captured usage data...")
tracker = get_global_tracker()
summary = tracker.get_summary()

print(f"\n   Total Tokens: {summary['total_tokens']}")
print(f"   Prompt Tokens: {summary['total_prompt_tokens']}")
print(f"   Completion Tokens: {summary['total_completion_tokens']}")
print(f"   API Calls: {summary['api_calls']}")

if summary['total_tokens'] > 0:
    print("\n   [SUCCESS] Usage tracking is working!")

    print("\n   Model Breakdown:")
    for model, usage in summary['model_breakdown'].items():
        print(f"      {model}:")
        print(f"         Prompt: {usage['prompt_tokens']} tokens")
        print(f"         Completion: {usage['completion_tokens']} tokens")
        print(f"         Total: {usage['total_tokens']} tokens")

    # Estimate cost
    cost_estimate = tracker.estimate_cost()
    if cost_estimate:
        print("\n   Cost Estimate:")
        print(f"      ${cost_estimate['total_cost']:.6f} USD")
else:
    print("\n   [WARNING] No usage data captured")
    print("   Usage tracking patch may not be working correctly")

print("\n" + "=" * 80)
print("[COMPLETE] Test finished")
print("=" * 80)
