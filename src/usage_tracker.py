"""
Usage tracking utilities for AutoGen 0.1.14 with OpenRouter.

AutoGen 0.1.14 doesn't expose usage data in message metadata,
so we need to intercept API responses directly.
"""
import os
import requests
from typing import Dict, Optional, List
from functools import wraps


class UsageTracker:
    """
    Global usage tracker for capturing OpenRouter API usage data.

    AutoGen 0.1.14 doesn't expose usage in message metadata,
    so we patch the OpenAI client to capture usage from raw responses.
    """

    def __init__(self):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0
        self.model_breakdown = {}
        self.generation_ids = []

    def add_usage(self, usage_data: Dict, model: Optional[str] = None, generation_id: Optional[str] = None):
        """
        Add usage data from an API response.

        Args:
            usage_data: Usage dictionary from OpenAI/OpenRouter response
            model: Model name (optional)
            generation_id: OpenRouter generation ID for later queries (optional)
        """
        if not usage_data:
            return

        prompt_tokens = usage_data.get("prompt_tokens", 0)
        completion_tokens = usage_data.get("completion_tokens", 0)
        total_tokens = usage_data.get("total_tokens", 0)

        # Aggregate totals
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_tokens += total_tokens

        # Track by model
        if model:
            if model not in self.model_breakdown:
                self.model_breakdown[model] = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "calls": 0
                }
            self.model_breakdown[model]["prompt_tokens"] += prompt_tokens
            self.model_breakdown[model]["completion_tokens"] += completion_tokens
            self.model_breakdown[model]["total_tokens"] += total_tokens
            self.model_breakdown[model]["calls"] += 1

        # Track generation IDs for later queries
        if generation_id:
            self.generation_ids.append(generation_id)

    def get_summary(self) -> Dict:
        """
        Get usage summary.

        Returns:
            Dictionary with aggregated usage data
        """
        return {
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_tokens,
            "model_breakdown": self.model_breakdown,
            "generation_ids": self.generation_ids,
            "api_calls": sum(m["calls"] for m in self.model_breakdown.values()) if self.model_breakdown else 0
        }

    def reset(self):
        """Reset all counters."""
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0
        self.model_breakdown = {}
        self.generation_ids = []

    def estimate_cost(self) -> Optional[Dict]:
        """
        Estimate cost based on tracked usage.
        Uses OpenRouter pricing (approximate).

        Returns:
            Dictionary with cost estimates per model and total
        """
        # Approximate OpenRouter pricing per 1M tokens (USD)
        pricing = {
            "deepseek/deepseek-chat": {"input": 0.14, "output": 0.28},
            "google/gemini-flash-1.5": {"input": 0.075, "output": 0.30},
            "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25},
            "anthropic/claude-3.5-sonnet": {"input": 3.00, "output": 15.00},
        }

        cost_breakdown = {}
        total_cost = 0.0

        for model, usage in self.model_breakdown.items():
            if model in pricing:
                input_cost = (usage["prompt_tokens"] / 1_000_000) * pricing[model]["input"]
                output_cost = (usage["completion_tokens"] / 1_000_000) * pricing[model]["output"]
                model_cost = input_cost + output_cost

                cost_breakdown[model] = {
                    "input_cost": input_cost,
                    "output_cost": output_cost,
                    "total_cost": model_cost
                }
                total_cost += model_cost

        if not cost_breakdown:
            return None

        return {
            "breakdown": cost_breakdown,
            "total_cost": total_cost,
            "currency": "USD"
        }

    def get_actual_costs(self, api_key: str) -> Optional[Dict]:
        """
        Get actual costs from OpenRouter using generation IDs.

        Queries OpenRouter's generation endpoint for each tracked generation
        to get the real cost data instead of estimates.

        Args:
            api_key: OpenRouter API key

        Returns:
            Dictionary with actual cost data per generation and total, or None if no generation IDs
        """
        if not self.generation_ids:
            return None

        generations = []
        total_cost = 0.0

        for gen_id in self.generation_ids:
            try:
                url = f"https://openrouter.ai/api/v1/generation?id={gen_id}"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                }

                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                data = response.json()

                # Extract actual cost
                gen_cost = float(data.get('total_cost', 0))
                total_cost += gen_cost

                generations.append({
                    "id": gen_id,
                    "model": data.get('model'),
                    "cost": gen_cost,
                    "prompt_tokens": data.get('tokens_prompt', 0),
                    "completion_tokens": data.get('tokens_completion', 0),
                })

            except Exception as e:
                # If query fails, skip this generation
                print(f"[WARNING] Could not query cost for generation {gen_id}: {e}")
                continue

        if not generations:
            return None

        return {
            "generations": generations,
            "total_cost": total_cost,
            "currency": "GBP",
            "count": len(generations)
        }

    def get_account_credits(self, api_key: str) -> Optional[Dict]:
        """
        Get OpenRouter account credits information.

        Queries the /api/v1/credits endpoint to get total credits,
        usage, and remaining balance.

        Args:
            api_key: OpenRouter API key

        Returns:
            Dictionary with credits info or None if request fails
        """
        try:
            url = "https://openrouter.ai/api/v1/credits"
            headers = {
                "Authorization": f"Bearer {api_key}",
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Extract credits data
            credits_data = data.get('data', {})
            total_credits = float(credits_data.get('total_credits', 0))
            total_usage = float(credits_data.get('total_usage', 0))
            remaining = total_credits - total_usage

            return {
                "total_credits": total_credits,
                "total_usage": total_usage,
                "remaining": remaining,
                "currency": "GBP"
            }

        except Exception as e:
            print(f"[WARNING] Could not query account credits: {e}")
            return None


# Global tracker instance
_global_tracker = UsageTracker()


def get_global_tracker() -> UsageTracker:
    """Get the global usage tracker instance."""
    return _global_tracker


def reset_global_tracker():
    """Reset the global usage tracker."""
    _global_tracker.reset()


def patch_autogen_for_usage_tracking():
    """
    Patch AutoGen's OpenAI client to capture usage data.

    AutoGen 0.1.14 uses OpenAI 0.28.1 (pre-v1 API).
    This function monkey-patches the ChatCompletion.create method
    to intercept responses and extract usage data.

    Call this BEFORE creating any AutoGen agents.
    """
    try:
        import openai

        # AutoGen 0.1.14 uses old OpenAI API (0.28.1)
        # Patch the ChatCompletion.create method
        if not hasattr(openai.ChatCompletion, '_original_create'):
            original_create = openai.ChatCompletion.create
            openai.ChatCompletion._original_create = original_create

            def create_with_usage_tracking(*args, **kwargs):
                """Wrapper that captures usage data from responses."""
                # Call original method
                response = openai.ChatCompletion._original_create(*args, **kwargs)

                # Extract usage data if available
                # OpenAI 0.28.1 returns dict-like objects
                if isinstance(response, dict) and 'usage' in response:
                    usage_dict = {
                        "prompt_tokens": response['usage'].get('prompt_tokens', 0),
                        "completion_tokens": response['usage'].get('completion_tokens', 0),
                        "total_tokens": response['usage'].get('total_tokens', 0)
                    }

                    # Get model from response or kwargs
                    model = response.get('model', kwargs.get('model', 'unknown'))

                    # Capture generation ID from response (OpenRouter includes this)
                    generation_id = response.get('id')

                    # Track usage
                    _global_tracker.add_usage(usage_dict, model=model, generation_id=generation_id)

                return response

            # Apply patch
            openai.ChatCompletion.create = create_with_usage_tracking

            return True

    except Exception as e:
        print(f"[WARNING] Failed to patch AutoGen for usage tracking: {e}")
        import traceback
        traceback.print_exc()
        return False


def unpatch_autogen():
    """Restore original OpenAI client methods."""
    try:
        import openai

        if hasattr(openai.ChatCompletion, '_original_create'):
            openai.ChatCompletion.create = openai.ChatCompletion._original_create
            delattr(openai.ChatCompletion, '_original_create')
            return True
    except Exception as e:
        print(f"[WARNING] Failed to unpatch AutoGen: {e}")
        return False
