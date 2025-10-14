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
from tools import TOOL_FUNCTIONS


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


def create_research_analysis_workflow(query: str) -> str:
    """
    Create and execute the research analysis workflow.

    Args:
        query: Research query from user (e.g., "Analyze ReAct framework")

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

Please analyze this research topic using the following workflow:

1. **Performance Analyst**: Search ArXiv for relevant papers. Analyze:
   - What makes the work unique and innovative
   - Technical details (architecture, techniques, methods)
   - Why these approaches work (theoretical foundation)
   - Practical benefits and advantages
   - Any benchmark results or SOTA achievements

2. **Critique Agent**: Search ArXiv for papers and related work. Analyze:
   - Reproducibility challenges
   - Computational costs and resource requirements
   - Failure modes and limitations
   - Generalization issues
   - Ethical concerns or biases
   - When approaches don't work well

3. **Synthesizer**: After receiving both analyses, create a balanced, comprehensive report with:
   - Executive Summary
   - Innovations & Contributions (from Performance Analyst)
   - Critical Analysis (from Critique Agent)
   - Balanced Assessment (tradeoffs, when to use/avoid)
   - Recommendations (for researchers, practitioners, and the field)

4. **UserProxy**: Save the final report and send email notification (if configured).

Use the search_arxiv tool to find relevant papers. Be thorough and specific in your analysis.

Begin the analysis now."""

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
        usage_metric = None

        # Look for the synthesizer's final report
        for msg in reversed(messages):
            if msg.get("name") == "Synthesizer" and "# Research Analysis" in msg.get("content", ""):
                final_report = msg.get("content")
                usage_metric = msg.get("usage")
                break

        if final_report:
            print("\n" + "="*80)
            print("[SUCCESS] Analysis Complete!\n")
            print(f"Usage used: {usage_metric}")
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
        result = create_research_analysis_workflow(args.query)

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
