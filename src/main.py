"""
Main entry point for the Research Agent System.
Orchestrates multi-agent collaboration for LLM research analysis.
"""
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from autogen import UserProxyAgent, GroupChat, GroupChatManager
from config import get_openrouter_config, print_environment_status, validate_environment
from agents import create_performance_analyst, create_critique_agent, create_synthesizer
from tools import TOOL_FUNCTIONS, get_tracked_papers, reset_paper_tracker
from usage_tracker import patch_autogen_for_usage_tracking, get_global_tracker, reset_global_tracker


def extract_usage_from_messages(messages: list) -> dict:
    """
    Extract usage data from conversation messages.

    AutoGen 0.1.14 doesn't always expose usage in message metadata,
    so we look for it in various places and aggregate.

    Args:
        messages: List of conversation messages from GroupChat

    Returns:
        Dictionary with aggregated usage data:
        - total_prompt_tokens: Total tokens in prompts
        - total_completion_tokens: Total tokens in completions
        - total_tokens: Total tokens used
        - model_breakdown: Usage by model
    """
    usage_data = {
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
        "total_tokens": 0,
        "model_breakdown": {}
    }

    for msg in messages:
        # Try to extract usage from message metadata
        msg_usage = None

        # Check different possible locations for usage data
        if isinstance(msg, dict):
            # Direct usage field
            if "usage" in msg and msg["usage"]:
                msg_usage = msg["usage"]
            # Usage in metadata
            elif "metadata" in msg and isinstance(msg["metadata"], dict):
                if "usage" in msg["metadata"]:
                    msg_usage = msg["metadata"]["usage"]

        # Aggregate usage if found
        if msg_usage and isinstance(msg_usage, dict):
            usage_data["total_prompt_tokens"] += msg_usage.get("prompt_tokens", 0)
            usage_data["total_completion_tokens"] += msg_usage.get("completion_tokens", 0)
            usage_data["total_tokens"] += msg_usage.get("total_tokens", 0)

            # Track by model if available
            model = msg.get("model", "unknown")
            if model not in usage_data["model_breakdown"]:
                usage_data["model_breakdown"][model] = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            usage_data["model_breakdown"][model]["prompt_tokens"] += msg_usage.get("prompt_tokens", 0)
            usage_data["model_breakdown"][model]["completion_tokens"] += msg_usage.get("completion_tokens", 0)
            usage_data["model_breakdown"][model]["total_tokens"] += msg_usage.get("total_tokens", 0)

    return usage_data


def create_user_proxy_with_tools():
    """
    Create User Proxy agent with tool execution capabilities.

    Returns:
        UserProxyAgent configured with tools
    """
    user_proxy = UserProxyAgent(
        name="UserProxy",
        human_input_mode="NEVER",  # Fully automated
        max_consecutive_auto_reply=15,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False,  # We don't need code execution
        function_map=TOOL_FUNCTIONS  # Map function names to actual functions
    )

    return user_proxy


def create_research_analysis_workflow(query: str, output_format: str = "all") -> str:
    """
    Create and execute the research analysis workflow.

    Args:
        query: Research query from user (e.g., "Analyze ReAct framework")
        output_format: Output format - "markdown", "pdf", "latex", or "all" (default: "all")

    Returns:
        String with the workflow results

    Workflow:
        1. User Proxy initiates with query
        2. Performance Analyst searches papers and analyzes innovations
        3. Critique Agent searches papers and analyzes limitations
        4. Synthesizer combines both perspectives into balanced report
        5. User Proxy saves report and sends email (if configured)
    """
    # Validate environment
    validation = validate_environment()
    if not validation["openrouter_api_key"]:
        raise ValueError(
            "OpenRouter API key not found. Please set OPENROUTER_API_KEY in .env file.\n"
            "Get your key from: https://openrouter.ai/"
        )

    print("\n" + "="*80)
    print("Research Agent System - Multi-Agent Analysis")
    print("="*80)
    print(f"\nQuery: {query}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*80 + "\n")

    # Patch AutoGen for usage tracking BEFORE creating agents
    print("[USAGE] Enabling usage tracking...")
    patch_success = patch_autogen_for_usage_tracking()
    if patch_success:
        print("   [OK] Usage tracking enabled\n")
    else:
        print("   [WARNING] Usage tracking not available\n")

    # Reset tracker for this analysis
    reset_global_tracker()
    reset_paper_tracker()

    # Get initial account credits (before analysis)
    api_key = os.getenv("OPENROUTER_API_KEY")
    tracker = get_global_tracker()
    initial_credits = tracker.get_account_credits(api_key)

    if initial_credits:
        print(f"[CREDITS] Initial Balance: ${initial_credits['remaining']:.2f}\n")

    # Get configuration
    config_list = get_openrouter_config()

    # Create agents
    print("[INIT] Initializing agents...")
    performance_analyst = create_performance_analyst(config_list)
    critique_agent = create_critique_agent(config_list)
    synthesizer = create_synthesizer(config_list)
    user_proxy = create_user_proxy_with_tools()

    print(f"   [OK] Performance Analyst ({os.getenv('PERFORMANCE_ANALYST_MODEL', 'deepseek/deepseek-chat')})")
    print(f"   [OK] Critique Agent ({os.getenv('CRITIQUE_AGENT_MODEL', 'deepseek/deepseek-chat')})")
    print(f"   [OK] Synthesizer ({os.getenv('SYNTHESIZER_MODEL', 'google/gemini-flash-1.5')})")
    print(f"   [OK] User Proxy (Tool Executor)")

    # Note: In AutoGen 0.1.14, tools are registered only with UserProxy via function_map
    # Assistant agents don't need direct tool access - they request tools through UserProxy

    # Create GroupChat
    print("\n[GROUPCHAT] Creating GroupChat...")
    groupchat = GroupChat(
        agents=[user_proxy, performance_analyst, critique_agent, synthesizer],
        messages=[],
        max_round=20,  # Limit conversation rounds
    )

    # Create GroupChat Manager
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config={"config_list": config_list}
    )

    print("   [OK] GroupChat initialized with 4 agents\n")

    # Initial message to start the workflow
    initial_message = f"""Research Query: {query}

Please analyze this research topic using the following workflow with COMPREHENSIVE coverage:

1. **Performance Analyst**:
   - Search ArXiv MULTIPLE TIMES with different related queries (15-20 papers minimum total)
   - Search for: main topic, predecessor papers, competing approaches, survey papers, applications
   - For each paper, analyze in detail:
     * What makes the work unique and innovative
     * Technical deep-dive: architecture details, mathematical formulations, key equations
     * Training methodologies: algorithms, hyperparameters, loss functions
     * Theoretical foundations: why approaches work, complexity analysis
     * Quantitative results: benchmark tables with specific numbers, ablation studies
     * Practical benefits with concrete metrics (speed, cost, memory)
   - Cite papers inline as [Paper 1], [Paper 2], etc.
   - Track ALL papers retrieved for the final bibliography

2. **Critique Agent**:
   - Search ArXiv MULTIPLE TIMES for critical perspectives (15-20 papers minimum total)
   - Search for: limitations, failure modes, critical reviews, alternative approaches
   - For each paper, analyze in detail:
     * Reproducibility: specific compute requirements (GPU types, hours, costs in $)
     * Cost-benefit analysis with quantitative comparisons
     * Failure modes with specific examples and error rates
     * Generalization limits with performance drops on OOD data
     * Scalability issues and deployment challenges
     * Ethical concerns with measured metrics (bias scores, toxicity rates)
   - Cite papers inline as [Paper 1], [Paper 2], etc.
   - Track ALL papers retrieved for the final bibliography

3. **Synthesizer**:
   - After receiving both comprehensive analyses, create a DETAILED, PROFESSIONAL report with:
     * Executive Summary (2-3 paragraphs)
     * Key Papers (top 3-5 most important)
     * Technical Deep-Dive: Innovations & Contributions (with subsections)
       - Architecture & Framework Design (equations, parameter counts)
       - Training Techniques & Methodologies (hyperparameters, loss functions)
       - Theoretical Foundations (mathematical justification)
       - Quantitative Results & Benchmarks (tables with numbers)
       - Practical Benefits & Applications (concrete metrics)
     * Critical Analysis: Limitations & Challenges (with subsections)
       - Reproducibility Assessment (compute costs, missing details)
       - Cost-Benefit Analysis (quantitative comparisons)
       - Failure Modes & Edge Cases (specific examples)
       - Generalization & Robustness (OOD performance)
       - Scalability & Practical Deployment
       - Ethical Concerns & Risks
     * Comparison with Related Work (table format)
     * Balanced Assessment (context, tradeoffs, when to use/avoid)
     * Recommendations (for researchers, practitioners, and the field)
     * Conclusion (summary and final assessment)
   - Use inline citations [Paper N] throughout the entire report
   - Aim for 2-3x longer, more detailed reports than before
   - Include ALL quantitative data, equations, and technical details

4. **UserProxy**:
   - Collect all papers cited by both analysts
   - Save the final report with complete bibliography (handled automatically)
   - Send email notification (if configured)

IMPORTANT INSTRUCTIONS:
- Search for 15-20 papers minimum per analyst (total 30-40 papers)
- Use multiple related search queries to get comprehensive coverage
- Cite papers inline throughout your analysis as [Paper 1], [Paper 2], etc.
- Include ALL quantitative data: numbers, metrics, costs, performance figures
- Provide deep technical details: equations, architectures, algorithms
- The final report should be comprehensive like an academic survey paper

Begin the comprehensive analysis now."""

    print("[START] Starting multi-agent analysis...\n")
    print("="*80)

    try:
        # Initiate the conversation
        user_proxy.initiate_chat(
            manager,
            message=initial_message
        )

        # Extract the final report from conversation
        messages = groupchat.messages
        final_report = None

        # First attempt: Look for standard report format with static title
        print("\n[EXTRACTION] Searching for Synthesizer report...")
        for msg in reversed(messages):
            content = msg.get("content", "")
            if msg.get("name") == "Synthesizer":
                # Look for the static title format: "# Research Analysis:"
                if "# Research Analysis:" in content:
                    final_report = content
                    print(f"[INFO] Found report with standard title format ({len(content)} chars)")
                    break

        # Fallback: Get last substantial message from Synthesizer
        if not final_report:
            print("[WARNING] Standard report title not found, using fallback...")
            for msg in reversed(messages):
                content = msg.get("content", "")
                if msg.get("name") == "Synthesizer" and len(content) > 500:
                    final_report = content
                    print(f"[INFO] Using last Synthesizer message as report ({len(content)} chars)")
                    break

        # Additional fallback: Look for ANY message with report-like structure
        if not final_report:
            print("[WARNING] No substantial Synthesizer message found, searching for report indicators...")
            for msg in reversed(messages):
                content = msg.get("content", "")
                if msg.get("name") == "Synthesizer":
                    # Check for report section indicators
                    if any(indicator in content for indicator in [
                        "## Executive Summary",
                        "## Key Papers",
                        "## Technical Deep-Dive",
                        "## Critical Analysis",
                        "## Recommendations"
                    ]):
                        final_report = content
                        print(f"[INFO] Found report based on section indicators ({len(content)} chars)")
                        break

        # Debug: Show message analysis if nothing found
        if not final_report:
            print("\n[DEBUG] No report extracted. Analyzing recent messages:")
            for i, msg in enumerate(reversed(messages[-5:]), 1):
                agent_name = msg.get('name', 'Unknown')
                content_length = len(msg.get('content', ''))
                preview = msg.get('content', '')[:100].replace('\n', ' ')
                print(f"  [{i}] Agent: {agent_name}, Length: {content_length} chars")
                print(f"      Preview: {preview}...")
            print()

        # Get usage data from global tracker (captured during API calls)
        tracker = get_global_tracker()
        usage_summary = tracker.get_summary()

        # Convert to the expected format with api_calls included
        usage_data = {
            "total_prompt_tokens": usage_summary["total_prompt_tokens"],
            "total_completion_tokens": usage_summary["total_completion_tokens"],
            "total_tokens": usage_summary["total_tokens"],
            "api_calls": usage_summary["api_calls"],  # Include API calls count
            "model_breakdown": usage_summary["model_breakdown"]
        }

        if final_report:
            # Save the report programmatically
            from tools import save_report

            print("\n" + "="*80)
            print("[SAVING] Saving report to disk...")

            # Get all tracked papers for bibliography
            tracked_papers = get_tracked_papers()
            print(f"[PAPERS] Collected {len(tracked_papers)} unique papers for bibliography")

            # Warn if no papers were tracked
            if len(tracked_papers) == 0:
                print("\n" + "="*80)
                print("⚠️  WARNING: NO PAPERS WERE TRACKED!")
                print("="*80)
                print("This means:")
                print("  • Agents did not call search_arxiv tools")
                print("  • Or ArXiv searches returned 0 results")
                print("  • BibTeX file will be empty")
                print("  • Citations in report may be hallucinated")
                print("\nTo fix: Check that agents are using search_arxiv, search_arxiv_by_author,")
                print("        or get_arxiv_paper tools to retrieve actual papers.")
                print("="*80 + "\n")

            # Include usage data in metadata
            metadata = {
                "agents": ["PerformanceAnalyst", "CritiqueAgent", "Synthesizer"],
                "timestamp": datetime.now().isoformat(),
                "models": {
                    "performance_analyst": os.getenv('PERFORMANCE_ANALYST_MODEL', 'deepseek/deepseek-chat'),
                    "critique_agent": os.getenv('CRITIQUE_AGENT_MODEL', 'deepseek/deepseek-chat'),
                    "synthesizer": os.getenv('SYNTHESIZER_MODEL', 'google/gemini-flash-1.5')
                },
                "usage": usage_data,  # Always include usage data in metadata
                "papers_analyzed": len(tracked_papers)  # Track number of papers
            }

            # Add cost and credits info if available
            if initial_credits:
                metadata["initial_credits"] = initial_credits['remaining']

            # Save in requested format(s)
            formats_to_save = []
            if output_format == "all":
                formats_to_save = ["markdown", "pdf", "latex"]
            else:
                formats_to_save = [output_format]

            for fmt in formats_to_save:
                result = save_report(
                    report_content=final_report,
                    query=query,
                    referenced_papers=tracked_papers,  # Pass all tracked papers
                    metadata=metadata,
                    format=fmt
                )
                print(f"\n[{fmt.upper()}]")
                print(result)

            print("\n" + "="*80)
            print("[SUCCESS] Analysis Complete!\n")

            # Display usage information
            if usage_data["total_tokens"] > 0:
                print("[USAGE] Token Usage:")
                print(f"   Prompt Tokens:     {usage_data['total_prompt_tokens']:,}")
                print(f"   Completion Tokens: {usage_data['total_completion_tokens']:,}")
                print(f"   Total Tokens:      {usage_data['total_tokens']:,}")
                print(f"   Total API Calls:   {usage_summary['api_calls']}")

                if usage_data["model_breakdown"]:
                    print("\n[USAGE] Breakdown by Model:")
                    for model, usage in usage_data["model_breakdown"].items():
                        if usage["total_tokens"] > 0:
                            print(f"   {model}:")
                            print(f"      Prompt: {usage['prompt_tokens']:,} tokens")
                            print(f"      Completion: {usage['completion_tokens']:,} tokens")
                            print(f"      Total: {usage['total_tokens']:,} tokens")
                            print(f"      Calls: {usage['calls']}")

                # Get actual costs from OpenRouter
                print("\n[COST] Querying actual costs from OpenRouter...")
                api_key = os.getenv("OPENROUTER_API_KEY")

                # Get final account credits (after analysis)
                final_credits = tracker.get_account_credits(api_key)

                if final_credits and initial_credits:
                    # Calculate actual cost from credit difference
                    actual_cost = initial_credits['remaining'] - final_credits['remaining']
                    print(f"   Actual Cost for this Analysis: ${actual_cost:.6f} USD")
                    print(f"   (Calculated from credit balance difference)")
                else:
                    # Try generation endpoint as fallback
                    actual_costs = tracker.get_actual_costs(api_key)
                    if actual_costs:
                        print(f"   Actual Cost (from {actual_costs['count']} API calls):")
                        print(f"   TOTAL: ${actual_costs['total_cost']:.6f} USD")
                    else:
                        print("   [WARNING] Could not retrieve actual costs")
                        print("   Falling back to estimates...")
                        cost_estimate = tracker.estimate_cost()
                        if cost_estimate:
                            print(f"   Estimated TOTAL: ~${cost_estimate['total_cost']:.6f} USD")

                # Display account credits summary
                print("\n[CREDITS] OpenRouter Account Summary:")
                
                if final_credits:
                    print(f"   --")
                    print(f"   Before Analysis:   ${initial_credits['remaining']:.2f}")
                    print(f"   After Analysis:    ${final_credits['remaining']:.2f}")
                    print(f"   Cost:              ${initial_credits['remaining'] - final_credits['remaining']:.6f}")
                    print(f"   --")
                else:
                    print("   [WARNING] Could not retrieve account credits")
            else:
                print("[INFO] Usage data not available")
                print("   Usage tracking may have failed to initialize")
                print("   Check if OpenAI client is compatible with usage tracking patch")

            print("="*80)
            return final_report
        else:
            print("\n" + "="*80)
            print("[WARNING] Analysis completed but report format unexpected")
            print("="*80)
            return "Analysis completed. Check console output for details."

    except Exception as e:
        print(f"\n[ERROR] Error during analysis: {str(e)}")
        raise


def main():
    """
    Main function - parse arguments and run the research analysis.
    """
    parser = argparse.ArgumentParser(
        description="Research Agent System - Multi-agent LLM research analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py "Analyze the ReAct framework for LLM reasoning"
  python src/main.py "Compare RLHF and DPO alignment techniques"
  python src/main.py "Summarize Llama 3 architecture and training"
  python src/main.py "Analyze GPT-4 architecture" --format latex
  python src/main.py "Study Constitutional AI" --format markdown
  python src/main.py --status  # Check configuration
        """
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Research query to analyze (e.g., 'Analyze ReAct framework')"
    )

    parser.add_argument(
        "--status",
        action="store_true",
        help="Check configuration status and exit"
    )

    parser.add_argument(
        "--cost",
        action="store_true",
        help="Show estimated cost per analysis and exit"
    )

    parser.add_argument(
        "--format",
        choices=["markdown", "pdf", "latex", "all"],
        default="all",
        help="Output format for the report (default: all)"
    )

    args = parser.parse_args()

    # Handle status check
    if args.status:
        print_environment_status()
        sys.exit(0)

    # Handle cost estimate
    if args.cost:
        from config import estimate_cost_per_analysis
        print(estimate_cost_per_analysis())
        sys.exit(0)

    # Require query if not checking status
    if not args.query:
        parser.print_help()
        print("\n[ERROR] Please provide a research query")
        print("\nExample: python src/main.py \"Analyze the ReAct framework\"")
        sys.exit(1)

    try:
        # Run the analysis
        result = create_research_analysis_workflow(args.query, args.format)

        print("\n" + "="*80)
        print("[REPORT] FINAL REPORT")
        print("="*80)
        print(result)
        print("="*80)

        print("\n[SUCCESS] Analysis completed successfully!")
        print(f"Reports are saved in: {os.getenv('OUTPUT_DIR', 'outputs/reports')}")

        if validate_environment()["email_configured"]:
            print("[EMAIL] Email notification sent (if configured)")

    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Analysis interrupted by user")
        sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your .env file configuration")
        print("2. Run: python src/main.py --status")
        print("3. Verify your OpenRouter API key is valid")
        sys.exit(1)


if __name__ == "__main__":
    main()
