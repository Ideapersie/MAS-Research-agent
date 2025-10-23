"""
Configuration management for the research agent system.
Loads environment variables and creates AutoGen configuration.
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv


# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def get_openrouter_config(api_key: Optional[str] = None) -> List[Dict]:
    """
    Create AutoGen config_list for OpenRouter API.

    Args:
        api_key: Optional API key override. If not provided, uses OPENROUTER_API_KEY from env.

    Returns:
        List of configuration dictionaries for AutoGen agents

    Raises:
        ValueError: If API key is not found in environment or parameters
    """
    # Get API key from parameter or environment
    api_key = api_key or os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError(
            "OpenRouter API key not found. Please set OPENROUTER_API_KEY in your .env file.\n"
            "Get your API key from: https://openrouter.ai/"
        )

    # Get model names from environment or use defaults
    performance_model = os.getenv("PERFORMANCE_ANALYST_MODEL", "deepseek/deepseek-chat")
    critique_model = os.getenv("CRITIQUE_AGENT_MODEL", "deepseek/deepseek-chat")
    synthesizer_model = os.getenv("SYNTHESIZER_MODEL", "google/gemini-flash-1.5")

    # Set environment variable for OpenAI base URL (AutoGen 0.1.14 compatibility)
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

    # Create config list for all models
    # Enable usage accounting for cost tracking
    config_list = [
        {
            "model": performance_model,
            "api_key": api_key,
            "api_base": "https://openrouter.ai/api/v1",  # Use api_base instead of base_url
            "extra_body": {
                "usage": {"include": True}  # Request usage data from OpenRouter
            }
        },
        {
            "model": critique_model,
            "api_key": api_key,
            "api_base": "https://openrouter.ai/api/v1",
            "extra_body": {
                "usage": {"include": True}
            }
        },
        {
            "model": synthesizer_model,
            "api_key": api_key,
            "api_base": "https://openrouter.ai/api/v1",
            "extra_body": {
                "usage": {"include": True}
            }
        },
    ]

    # Remove duplicates while preserving order
    seen_models = set()
    unique_config = []
    for config in config_list:
        if config["model"] not in seen_models:
            seen_models.add(config["model"])
            unique_config.append(config)

    return unique_config


def validate_environment() -> Dict[str, bool]:
    """
    Validate environment configuration and check what features are available.

    Returns:
        Dictionary with validation results for different features
    """
    validation = {
        "openrouter_api_key": bool(os.getenv("OPENROUTER_API_KEY")),
        "email_configured": all([
            os.getenv("SMTP_SERVER"),
            os.getenv("SMTP_USERNAME"),
            os.getenv("SMTP_PASSWORD"),
            os.getenv("EMAIL_FROM"),
        ]),
        "email_recipient_set": bool(os.getenv("EMAIL_TO")),
        "output_dir_configured": bool(os.getenv("OUTPUT_DIR")),
        "arxiv_configured": bool(os.getenv("ARXIV_API_BASE")),
    }

    return validation


def print_environment_status():
    """
    Print environment configuration status for debugging.
    """
    validation = validate_environment()

    print("\n" + "=" * 60)
    print("Research Agent System - Configuration Status")
    print("=" * 60)

    # Required configuration
    print("\n[REQUIRED]")
    if validation["openrouter_api_key"]:
        print("[OK] OpenRouter API Key: Configured")
    else:
        print("[MISSING] OpenRouter API Key: Get from https://openrouter.ai/")

    # Model configuration
    print("\n[MODELS]")
    print(f"  Performance Analyst: {os.getenv('PERFORMANCE_ANALYST_MODEL', 'deepseek/deepseek-chat')}")
    print(f"  Critique Agent:      {os.getenv('CRITIQUE_AGENT_MODEL', 'deepseek/deepseek-chat')}")
    print(f"  Synthesizer:         {os.getenv('SYNTHESIZER_MODEL', 'google/gemini-flash-1.5')}")

    # Optional configuration
    print("\n[OPTIONAL]")
    if validation["email_configured"]:
        print(f"[OK] Email Delivery: Configured")
        if validation["email_recipient_set"]:
            print(f"   Recipient: {os.getenv('EMAIL_TO')}")
        else:
            print(f"   [WARNING] Recipient: Not set (EMAIL_TO)")
    else:
        print("[INFO] Email Delivery: Not configured (reports will be saved locally only)")

    # Output configuration
    print("\n[OUTPUT]")
    output_dir = os.getenv("OUTPUT_DIR", "outputs/reports")
    print(f"  Reports Directory: {output_dir}")

    # ArXiv configuration
    print("\n[ARXIV]")
    print(f"  API Base: {os.getenv('ARXIV_API_BASE', 'http://export.arxiv.org/api/query')}")
    print(f"  Max Results: {os.getenv('ARXIV_MAX_RESULTS', '10')}")

    print("\n" + "=" * 60)

    # Warnings
    if not validation["openrouter_api_key"]:
        print("\n[WARNING] OpenRouter API key is required to run the system!")
        print("   Set OPENROUTER_API_KEY in your .env file\n")

    if not validation["email_configured"]:
        print("\n[INFO] Email delivery is not configured.")
        print("   Reports will be saved locally. To enable email delivery,")
        print("   set SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD, and EMAIL_FROM in .env\n")


def get_model_costs() -> Dict[str, Dict[str, float]]:
    """
    Get estimated costs per model (per 1M tokens).
    Prices are approximate and should be verified with OpenRouter.

    Returns:
        Dictionary mapping model names to pricing info
    """
    costs = {
        "deepseek/deepseek-chat": {
            "input": 0.14,
            "output": 0.28,
            "description": "Excellent quality, very affordable"
        },
        "google/gemini-flash-1.5": {
            "input": 0.075,
            "output": 0.30,
            "description": "Fast, cheap, good for synthesis"
        },
        "anthropic/claude-3-haiku": {
            "input": 0.25,
            "output": 1.25,
            "description": "High quality, moderate cost"
        },
        "anthropic/claude-3.5-sonnet": {
            "input": 3.00,
            "output": 15.00,
            "description": "Premium quality, expensive"
        },
        "openai/gpt-4-turbo": {
            "input": 10.00,
            "output": 30.00,
            "description": "Premium quality, very expensive"
        },
    }

    return costs


def estimate_cost_per_analysis() -> str:
    """
    Estimate the cost per research analysis based on current model configuration.

    Returns:
        String with cost estimate
    """
    costs = get_model_costs()

    performance_model = os.getenv("PERFORMANCE_ANALYST_MODEL", "deepseek/deepseek-chat")
    critique_model = os.getenv("CRITIQUE_AGENT_MODEL", "deepseek/deepseek-chat")
    synthesizer_model = os.getenv("SYNTHESIZER_MODEL", "google/gemini-flash-1.5")

    # Rough estimates for token usage per agent
    # Performance Analyst: ~5K input, ~3K output
    # Critique Agent: ~5K input, ~3K output
    # Synthesizer: ~10K input (both agent outputs), ~4K output

    total_cost = 0.0

    # Performance Analyst
    if performance_model in costs:
        perf_cost = (5 * costs[performance_model]["input"] + 3 * costs[performance_model]["output"]) / 1000
        total_cost += perf_cost

    # Critique Agent
    if critique_model in costs:
        critique_cost = (5 * costs[critique_model]["input"] + 3 * costs[critique_model]["output"]) / 1000
        total_cost += critique_cost

    # Synthesizer
    if synthesizer_model in costs:
        synth_cost = (10 * costs[synthesizer_model]["input"] + 4 * costs[synthesizer_model]["output"]) / 1000
        total_cost += synth_cost

    estimate = f"""
Estimated Cost per Analysis: ${total_cost:.3f} - ${total_cost * 2:.3f}

Model Configuration:
  • Performance Analyst: {performance_model}
  • Critique Agent:      {critique_model}
  • Synthesizer:         {synthesizer_model}

For 100 analyses: ${total_cost * 100:.2f} - ${total_cost * 200:.2f}

Note: Actual costs may vary based on:
- Paper length and complexity
- Number of papers searched
- Agent verbosity
- Context length used
"""

    return estimate.strip()


if __name__ == "__main__":
    """
    Run this file directly to check configuration status.
    Usage: python src/config.py
    """
    try:
        print_environment_status()

        # Try to create config
        print("\n[TESTING] Attempting to create AutoGen config...")
        config_list = get_openrouter_config()
        print(f"[OK] Successfully created config with {len(config_list)} model(s)")

        # Show cost estimate
        print("\n" + "=" * 60)
        print(estimate_cost_per_analysis())
        print("=" * 60)

    except ValueError as e:
        print(f"\n[ERROR] Configuration Error: {e}")
        print("\nPlease create a .env file with required configuration.")
        print("See .env.example for template.")
