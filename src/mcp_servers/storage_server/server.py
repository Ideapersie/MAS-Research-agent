"""
MCP Server for Report Storage functionality.
Exposes tools for saving and managing research analysis reports.
"""
import os
import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
from storage_tools import ReportStorage


# Initialize storage
storage = ReportStorage(
    output_dir=os.getenv("OUTPUT_DIR", "outputs/reports")
)

# Create MCP server
app = Server("storage-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available storage tools."""
    return [
        Tool(
            name="save_report",
            description="Save a research analysis report to local storage. Returns the file path where the report was saved.",
            inputSchema={
                "type": "object",
                "properties": {
                    "report_content": {
                        "type": "string",
                        "description": "The complete report content to save"
                    },
                    "query": {
                        "type": "string",
                        "description": "The original research query that generated this report"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Optional metadata about the report (agents used, models, etc.)"
                    },
                    "format": {
                        "type": "string",
                        "description": "Output format for the report",
                        "enum": ["markdown", "json", "txt"],
                        "default": "markdown"
                    }
                },
                "required": ["report_content", "query"]
            }
        ),
        Tool(
            name="list_reports",
            description="List recently saved reports with their metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of reports to return (default: 10)",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="get_report",
            description="Retrieve a specific report by filename.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the report file to retrieve"
                    }
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="delete_report",
            description="Delete a specific report by filename.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the report file to delete"
                    }
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="get_storage_info",
            description="Get information about the report storage directory (total reports, size, etc.).",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls from agents."""

    try:
        if name == "save_report":
            report_content = arguments.get("report_content")
            query = arguments.get("query")
            metadata = arguments.get("metadata", {})
            format = arguments.get("format", "markdown")

            result = storage.save_report(
                report_content=report_content,
                query=query,
                metadata=metadata,
                format=format
            )

            if result["status"] == "success":
                response = f"""✅ Report saved successfully!
File: {result['filename']}
Path: {result['filepath']}
Size: {result['size_bytes']} bytes
Timestamp: {result['timestamp']}"""
            else:
                response = f"❌ {result['message']}"

            return [TextContent(
                type="text",
                text=response
            )]

        elif name == "list_reports":
            limit = arguments.get("limit", 10)
            reports = storage.list_reports(limit=limit)

            if reports and "error" not in reports[0]:
                response = f"Found {len(reports)} report(s):\n\n"
                for i, report in enumerate(reports, 1):
                    response += f"{i}. {report['filename']}\n"
                    response += f"   Size: {report['size_bytes']} bytes\n"
                    response += f"   Modified: {report['modified']}\n"
                    response += f"   Path: {report['filepath']}\n\n"
            else:
                response = "No reports found or error occurred."

            return [TextContent(
                type="text",
                text=response
            )]

        elif name == "get_report":
            filename = arguments.get("filename")
            result = storage.get_report(filename=filename)

            if result["status"] == "success":
                response = f"""Report: {result['filename']}
Size: {result['size_bytes']} bytes
Modified: {result['modified']}

Content:
{result['content']}"""
            else:
                response = f"❌ {result['message']}"

            return [TextContent(
                type="text",
                text=response
            )]

        elif name == "delete_report":
            filename = arguments.get("filename")
            result = storage.delete_report(filename=filename)

            if result["status"] == "success":
                response = f"✅ {result['message']}"
            else:
                response = f"❌ {result['message']}"

            return [TextContent(
                type="text",
                text=response
            )]

        elif name == "get_storage_info":
            info = storage.get_storage_info()

            if "error" not in info:
                response = f"""Storage Information:
Directory: {info['output_directory']}
Total Reports: {info['total_reports']}
Total Size: {info['total_size_mb']} MB ({info['total_size_bytes']} bytes)"""
            else:
                response = f"❌ {info['error']}"

            return [TextContent(
                type="text",
                text=response
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
