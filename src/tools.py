"""
Tool wrappers for MCP server integration with AutoGen agents.
Provides simple function interfaces for agents to search papers, save reports, and send emails.
"""
import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path


# Ensure MCP server modules are importable
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


# Global paper tracker for collecting all papers retrieved during analysis
_paper_tracker = []


def _track_papers(papers: List[Dict]):
    """
    Track papers retrieved during analysis.

    Args:
        papers: List of paper dictionaries from ArXiv search
    """
    global _paper_tracker
    for paper in papers:
        # Avoid duplicates based on arxiv_id
        arxiv_id = paper.get('arxiv_id')
        if arxiv_id and not any(p.get('arxiv_id') == arxiv_id for p in _paper_tracker):
            _paper_tracker.append(paper)


def get_tracked_papers() -> List[Dict]:
    """
    Get all papers tracked during this analysis session.

    Returns:
        List of unique paper dictionaries
    """
    global _paper_tracker
    return _paper_tracker


def reset_paper_tracker():
    """Reset the paper tracker for a new analysis session."""
    global _paper_tracker
    _paper_tracker = []


def search_arxiv(query: str, max_results: int = 20) -> str:
    """
    Search ArXiv for research papers by keyword or topic.

    Use this to find papers on:
    - LLM models (e.g., "Llama 3", "GPT-4", "Claude")
    - Agentic frameworks (e.g., "ReAct", "Reflexion", "tool use")
    - Training techniques (e.g., "RLHF", "DPO", "Constitutional AI")
    - Architectures (e.g., "transformer", "attention mechanism")

    Args:
        query: Search query with keywords or topics
        max_results: Maximum number of papers to return (default: 20)

    Returns:
        Formatted string with paper information including:
        - Title, authors, ArXiv ID
        - Abstract (truncated)
        - Categories, publication date
        - URLs (abstract page and PDF)

    Example:
        >>> search_arxiv("ReAct framework reasoning", max_results=5)
    """
    try:
        from mcp_servers.arxiv_server.arxiv_tools import ArxivSearchTool, format_papers_for_agent

        api_base = os.getenv("ARXIV_API_BASE", "http://export.arxiv.org/api/query")
        default_max = int(os.getenv("ARXIV_MAX_RESULTS", "20"))

        arxiv_tool = ArxivSearchTool(api_base=api_base, max_results=default_max)
        papers = arxiv_tool.search(query=query, max_results=max_results)

        # Track papers for bibliography
        _track_papers(papers)

        return format_papers_for_agent(papers)

    except Exception as e:
        return f"Error searching ArXiv: {str(e)}\n\nPlease try rephrasing your query or reducing max_results."


def search_arxiv_by_author(author_name: str, max_results: int = 10) -> str:
    """
    Search ArXiv papers by author name.

    Args:
        author_name: Author's full or partial name (e.g., "Yann LeCun", "Hinton")
        max_results: Maximum number of papers to return (default: 10)

    Returns:
        Formatted string with paper information

    Example:
        >>> search_arxiv_by_author("Ilya Sutskever", max_results=5)
    """
    try:
        from mcp_servers.arxiv_server.arxiv_tools import ArxivSearchTool, format_papers_for_agent

        api_base = os.getenv("ARXIV_API_BASE", "http://export.arxiv.org/api/query")
        default_max = int(os.getenv("ARXIV_MAX_RESULTS", "20"))

        arxiv_tool = ArxivSearchTool(api_base=api_base, max_results=default_max)
        papers = arxiv_tool.search_by_author(author_name=author_name, max_results=max_results)

        # Track papers for bibliography
        _track_papers(papers)

        return format_papers_for_agent(papers)

    except Exception as e:
        return f"Error searching ArXiv by author: {str(e)}"


def get_arxiv_paper(arxiv_id: str) -> str:
    """
    Get detailed information about a specific ArXiv paper by ID.

    Args:
        arxiv_id: ArXiv paper ID (e.g., "2301.12345" or "2301.12345v1")

    Returns:
        Formatted string with detailed paper information

    Example:
        >>> get_arxiv_paper("2303.08774")  # ReAct paper
    """
    try:
        from mcp_servers.arxiv_server.arxiv_tools import ArxivSearchTool, format_papers_for_agent

        api_base = os.getenv("ARXIV_API_BASE", "http://export.arxiv.org/api/query")
        arxiv_tool = ArxivSearchTool(api_base=api_base)

        paper = arxiv_tool.get_paper_details(arxiv_id=arxiv_id)

        # Track paper for bibliography
        _track_papers([paper])

        return format_papers_for_agent([paper])

    except Exception as e:
        return f"Error retrieving ArXiv paper {arxiv_id}: {str(e)}"


def save_report(
    report_content: str,
    query: str,
    referenced_papers: Optional[List[Dict]] = None,
    metadata: Optional[Dict] = None,
    format: str = "markdown"
) -> str:
    """
    Save research analysis report to local storage.

    Use this after the Synthesizer creates the final balanced analysis.
    Reports are saved to the OUTPUT_DIR configured in environment (.env).

    Args:
        report_content: The complete report content (markdown formatted)
        query: The original research query that generated this report
        referenced_papers: Optional list of ArXiv papers to include in bibliography
        metadata: Optional dict with info about analysis (agents used, models, etc.)
        format: Output format - "markdown" (default), "pdf", "json", or "txt"

    Returns:
        Status message with file path and details

    Example:
        >>> save_report(
        ...     report_content="# Research Analysis\\n...",
        ...     query="Analyze ReAct framework",
        ...     referenced_papers=[{...}],
        ...     metadata={"agents": ["PerformanceAnalyst", "CritiqueAgent", "Synthesizer"]},
        ...     format="markdown"
        ... )
    """
    try:
        from mcp_servers.storage_server.storage_tools import ReportStorage

        output_dir = os.getenv("OUTPUT_DIR", "outputs/reports")
        storage = ReportStorage(output_dir=output_dir)

        result = storage.save_report(
            report_content=report_content,
            query=query,
            referenced_papers=referenced_papers,
            metadata=metadata or {},
            format=format
        )

        if result["status"] == "success":
            return f"""[OK] Report saved successfully!

File: {result['filename']}
Path: {result['filepath']}
Size: {result['size_bytes']} bytes
Format: {result['format']}
Timestamp: {result['timestamp']}

The report is ready for review or email delivery."""
        else:
            return f"[ERROR] Error saving report: {result['message']}"

    except Exception as e:
        return f"[ERROR] Error in save_report: {str(e)}"


def send_report_email(
    subject: str,
    report_content: str,
    to_address: Optional[str] = None,
    report_format: str = "markdown"
) -> str:
    """
    Send research analysis report via email.

    Use this after saving the report to deliver it to the user.
    If to_address is not provided, uses EMAIL_TO from environment.

    Args:
        subject: Email subject line (e.g., "Research Analysis: ReAct Framework")
        report_content: The report content to send (markdown recommended)
        to_address: Recipient email (optional, uses EMAIL_TO env var if not provided)
        report_format: Format - "markdown" (default, converts to HTML), "html", or "plain"

    Returns:
        Status message indicating success or failure

    Example:
        >>> send_report_email(
        ...     subject="Research Analysis: RLHF vs DPO",
        ...     report_content="# Analysis\\n...",
        ...     report_format="markdown"
        ... )

    Note:
        Requires SMTP configuration in .env file:
        - SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
        - EMAIL_FROM, EMAIL_TO (optional if to_address provided)
    """
    try:
        from mcp_servers.email_server.email_tools import EmailSender

        # Get email configuration
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        username = os.getenv("SMTP_USERNAME", "")
        password = os.getenv("SMTP_PASSWORD", "")
        from_address = os.getenv("EMAIL_FROM", "")

        # Use provided to_address or fall back to env variable
        recipient = to_address or os.getenv("EMAIL_TO", "")

        if not recipient:
            return """[ERROR] No recipient email address provided.

Please either:
1. Provide to_address parameter, OR
2. Set EMAIL_TO in your .env file

Email delivery skipped. Report is still saved locally."""

        if not all([smtp_server, username, password, from_address]):
            return """[ERROR] Email configuration incomplete.

Required in .env file:
- SMTP_SERVER, SMTP_PORT
- SMTP_USERNAME, SMTP_PASSWORD
- EMAIL_FROM

Email delivery skipped. Report is still saved locally."""

        email_sender = EmailSender(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            username=username,
            password=password,
            from_address=from_address
        )

        result = email_sender.send_report(
            to_address=recipient,
            subject=subject,
            report_content=report_content,
            report_format=report_format
        )

        if result["status"] == "success":
            return f"""[OK] Email sent successfully!

To: {recipient}
Subject: {subject}
Timestamp: {result['timestamp']}

The research analysis has been delivered."""
        else:
            return f"[ERROR] Error sending email: {result['message']}"

    except Exception as e:
        return f"[ERROR] Error in send_report_email: {str(e)}\n\nReport is still saved locally."


# Tool definitions for AutoGen function calling
# These define the schema that AutoGen uses to understand how to call the tools

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_arxiv",
            "description": "Search ArXiv for research papers by keyword or topic. Returns paper metadata including title, authors, abstract, categories, and URLs. Use this to find papers on LLM models, agentic frameworks (ReAct, Reflexion, etc.), training techniques (RLHF, DPO), or specific research topics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query with keywords or topics. Examples: 'ReAct reasoning agent', 'RLHF alignment', 'Llama 3 architecture', 'chain-of-thought prompting'"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of papers to return. Default is 20. Use 10 for quick searches, 20-30 for comprehensive analysis.",
                        "default": 20
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_arxiv_by_author",
            "description": "Search ArXiv papers by author name. Useful for finding work by specific researchers or tracking contributions from a research group.",
            "parameters": {
                "type": "object",
                "properties": {
                    "author_name": {
                        "type": "string",
                        "description": "Author's full or partial name. Examples: 'Yann LeCun', 'Geoffrey Hinton', 'Sutskever'"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of papers to return. Default is 10.",
                        "default": 10
                    }
                },
                "required": ["author_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_arxiv_paper",
            "description": "Get detailed information about a specific ArXiv paper by its ID. Use this when you have the paper ID and need full details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "arxiv_id": {
                        "type": "string",
                        "description": "ArXiv paper ID, e.g., '2301.12345' or '2301.12345v1'. Can be found in paper URLs or search results."
                    }
                },
                "required": ["arxiv_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_report",
            "description": "Save the research analysis report to local storage. Use this after the Synthesizer creates the final balanced analysis. Reports are timestamped and saved to the configured output directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "report_content": {
                        "type": "string",
                        "description": "The complete report content in markdown format. Should include all sections: Executive Summary, Innovations, Critical Analysis, Balanced Assessment, and Recommendations."
                    },
                    "query": {
                        "type": "string",
                        "description": "The original research query that generated this report. Used for filename generation and metadata."
                    },
                    "referenced_papers": {
                        "type": "array",
                        "description": "Optional list of ArXiv paper dictionaries to include in the bibliography. Papers are automatically tracked during searches.",
                        "items": {
                            "type": "object"
                        }
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Optional metadata dictionary with information about the analysis process (agents used, models, timestamp, etc.)"
                    },
                    "format": {
                        "type": "string",
                        "description": "Output format for the report. Options: 'markdown' (default), 'pdf', 'latex', 'json', 'txt'",
                        "enum": ["markdown", "pdf", "latex", "json", "txt"],
                        "default": "markdown"
                    }
                },
                "required": ["report_content", "query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_report_email",
            "description": "Send the research analysis report via email. Use this after saving the report to deliver it to the user. Email is optional - if configuration is missing, the report is still saved locally.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "Email subject line. Should be descriptive, e.g., 'Research Analysis: ReAct Framework for LLM Reasoning'"
                    },
                    "report_content": {
                        "type": "string",
                        "description": "The report content to send. Markdown is recommended as it will be converted to HTML for better email rendering."
                    },
                    "to_address": {
                        "type": "string",
                        "description": "Recipient email address. Optional - if not provided, uses EMAIL_TO from environment configuration."
                    },
                    "report_format": {
                        "type": "string",
                        "description": "Format of the report content. Options: 'markdown' (converts to HTML), 'html', 'plain'",
                        "enum": ["markdown", "html", "plain"],
                        "default": "markdown"
                    }
                },
                "required": ["subject", "report_content"]
            }
        }
    }
]


# Mapping of function names to actual Python functions
TOOL_FUNCTIONS = {
    "search_arxiv": search_arxiv,
    "search_arxiv_by_author": search_arxiv_by_author,
    "get_arxiv_paper": get_arxiv_paper,
    "save_report": save_report,
    "send_report_email": send_report_email,
}
