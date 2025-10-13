"""
MCP Server for Email functionality.
Exposes tools for sending research analysis reports via email.
"""
import os
import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
from email_tools import EmailSender


# Initialize Email sender with environment variables
def get_email_sender() -> EmailSender:
    """Create EmailSender instance from environment variables."""
    return EmailSender(
        smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        username=os.getenv("SMTP_USERNAME", ""),
        password=os.getenv("SMTP_PASSWORD", ""),
        from_address=os.getenv("EMAIL_FROM", "")
    )


# Create MCP server
app = Server("email-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available email tools."""
    return [
        Tool(
            name="send_report_email",
            description="Send a research analysis report via email. Use this to deliver the final synthesized report to the user.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to_address": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line"
                    },
                    "report_content": {
                        "type": "string",
                        "description": "The complete report content (in markdown format)"
                    },
                    "report_format": {
                        "type": "string",
                        "description": "Format of the report (markdown, html, or plain)",
                        "enum": ["markdown", "html", "plain"],
                        "default": "markdown"
                    }
                },
                "required": ["to_address", "subject", "report_content"]
            }
        ),
        Tool(
            name="test_email_connection",
            description="Test the SMTP email connection without sending an email. Useful for verifying configuration.",
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
        email_sender = get_email_sender()

        if name == "send_report_email":
            to_address = arguments.get("to_address")
            subject = arguments.get("subject")
            report_content = arguments.get("report_content")
            report_format = arguments.get("report_format", "markdown")

            # Validate inputs
            if not to_address:
                to_address = os.getenv("EMAIL_TO", "")
                if not to_address:
                    raise ValueError("No recipient email address provided")

            result = email_sender.send_report(
                to_address=to_address,
                subject=subject,
                report_content=report_content,
                report_format=report_format
            )

            if result["status"] == "success":
                response = f"✅ {result['message']}\nTimestamp: {result['timestamp']}"
            else:
                response = f"❌ {result['message']}\nTimestamp: {result['timestamp']}"

            return [TextContent(
                type="text",
                text=response
            )]

        elif name == "test_email_connection":
            result = email_sender.test_connection()

            if result["status"] == "success":
                response = f"✅ {result['message']}"
            else:
                response = f"❌ {result['message']}"

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
