"""
Basic tests for the research agent system.
Run with: pytest tests/test_basic.py -v
"""
import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def test_imports():
    """Test that all modules can be imported."""
    try:
        from agents import create_performance_analyst, create_critique_agent, create_synthesizer
        from tools import search_arxiv, save_report, TOOL_DEFINITIONS
        from config import get_openrouter_config, validate_environment
        assert True
    except ImportError as e:
        assert False, f"Import failed: {e}"


def test_tool_definitions():
    """Test that tool definitions are properly formatted."""
    from tools import TOOL_DEFINITIONS, TOOL_FUNCTIONS

    # Check we have tools defined
    assert len(TOOL_DEFINITIONS) > 0, "No tool definitions found"

    # Check each tool has required fields
    for tool in TOOL_DEFINITIONS:
        assert "type" in tool
        assert tool["type"] == "function"
        assert "function" in tool

        func = tool["function"]
        assert "name" in func
        assert "description" in func
        assert "parameters" in func

        # Check function name is in TOOL_FUNCTIONS
        assert func["name"] in TOOL_FUNCTIONS, f"Function {func['name']} not in TOOL_FUNCTIONS"


def test_agent_system_messages():
    """Test that agent system messages are defined."""
    from agents import (
        PERFORMANCE_ANALYST_SYSTEM_MESSAGE,
        CRITIQUE_AGENT_SYSTEM_MESSAGE,
        SYNTHESIZER_SYSTEM_MESSAGE
    )

    assert len(PERFORMANCE_ANALYST_SYSTEM_MESSAGE) > 100
    assert len(CRITIQUE_AGENT_SYSTEM_MESSAGE) > 100
    assert len(SYNTHESIZER_SYSTEM_MESSAGE) > 100

    # Check key content
    assert "Performance Analyst" in PERFORMANCE_ANALYST_SYSTEM_MESSAGE
    assert "Critique Agent" in CRITIQUE_AGENT_SYSTEM_MESSAGE
    assert "Synthesizer" in SYNTHESIZER_SYSTEM_MESSAGE


def test_environment_validation():
    """Test environment validation function."""
    from config import validate_environment

    validation = validate_environment()

    assert isinstance(validation, dict)
    assert "openrouter_api_key" in validation
    assert "email_configured" in validation
    assert "output_dir_configured" in validation


def test_arxiv_tool_basic():
    """Test ArXiv tool can be imported and has proper structure."""
    from mcp_servers.arxiv_server.arxiv_tools import ArxivSearchTool

    tool = ArxivSearchTool()
    assert tool.api_base is not None
    assert tool.max_results > 0


def test_storage_tool_basic():
    """Test Storage tool can be imported and initializes."""
    from mcp_servers.storage_server.storage_tools import ReportStorage

    storage = ReportStorage(output_dir="outputs/reports")
    assert storage.output_dir is not None


def test_email_tool_basic():
    """Test Email tool can be imported and initializes."""
    from mcp_servers.email_server.email_tools import EmailSender

    # Just test initialization, don't send actual email
    sender = EmailSender(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        username="test@example.com",
        password="test_password",
        from_address="test@example.com"
    )

    assert sender.smtp_server == "smtp.gmail.com"
    assert sender.smtp_port == 587


if __name__ == "__main__":
    """Run tests manually."""
    import pytest
    pytest.main([__file__, "-v"])
