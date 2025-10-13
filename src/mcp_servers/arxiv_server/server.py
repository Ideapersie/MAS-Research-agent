"""
MCP Server for ArXiv API integration.
Exposes tools for searching and retrieving research papers.
"""
import os
import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
from arxiv_tools import ArxivSearchTool, format_papers_for_agent


# Initialize ArXiv tool
arxiv_tool = ArxivSearchTool(
    api_base=os.getenv("ARXIV_API_BASE", "http://export.arxiv.org/api/query"),
    max_results=int(os.getenv("ARXIV_MAX_RESULTS", "10"))
)

# Create MCP server
app = Server("arxiv-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available ArXiv tools."""
    return [
        Tool(
            name="search_arxiv",
            description="Search ArXiv for research papers by keyword or topic. Returns paper metadata including title, authors, abstract, and URLs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (keywords, topics, or research area)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_arxiv_by_author",
            description="Search ArXiv papers by author name. Returns papers authored by the specified researcher.",
            inputSchema={
                "type": "object",
                "properties": {
                    "author_name": {
                        "type": "string",
                        "description": "Author's full or partial name"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10
                    }
                },
                "required": ["author_name"]
            }
        ),
        Tool(
            name="get_arxiv_paper",
            description="Get detailed information about a specific ArXiv paper by its ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "arxiv_id": {
                        "type": "string",
                        "description": "ArXiv paper ID (e.g., '2301.12345' or '2301.12345v1')"
                    }
                },
                "required": ["arxiv_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls from agents."""

    try:
        if name == "search_arxiv":
            query = arguments.get("query")
            max_results = arguments.get("max_results", 10)

            papers = arxiv_tool.search(query=query, max_results=max_results)
            formatted_result = format_papers_for_agent(papers)

            return [TextContent(
                type="text",
                text=formatted_result
            )]

        elif name == "search_arxiv_by_author":
            author_name = arguments.get("author_name")
            max_results = arguments.get("max_results", 10)

            papers = arxiv_tool.search_by_author(author_name=author_name, max_results=max_results)
            formatted_result = format_papers_for_agent(papers)

            return [TextContent(
                type="text",
                text=formatted_result
            )]

        elif name == "get_arxiv_paper":
            arxiv_id = arguments.get("arxiv_id")

            paper = arxiv_tool.get_paper_details(arxiv_id=arxiv_id)
            formatted_result = format_papers_for_agent([paper])

            return [TextContent(
                type="text",
                text=formatted_result
            )]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing tool {name}: {str(e)}"
        )]


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
