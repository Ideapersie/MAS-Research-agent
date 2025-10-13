"""
Email tools for sending research analysis reports.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
from datetime import datetime


class EmailSender:
    """Tool for sending emails via SMTP."""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_address: str
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_address = from_address

    def send_report(
        self,
        to_address: str,
        subject: str,
        report_content: str,
        report_format: str = "markdown"
    ) -> Dict[str, str]:
        """
        Send a research analysis report via email.

        Args:
            to_address: Recipient email address
            subject: Email subject line
            report_content: The report content to send
            report_format: Format of the report (markdown, html, plain)

        Returns:
            Dictionary with status and message
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_address
            msg['To'] = to_address
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

            # Add content based on format
            if report_format == "html":
                html_part = MIMEText(report_content, 'html')
                msg.attach(html_part)
            elif report_format == "markdown":
                # Send markdown as plain text with proper formatting
                text_part = MIMEText(report_content, 'plain', 'utf-8')
                msg.attach(text_part)

                # Optionally convert markdown to HTML for better rendering
                try:
                    html_content = self._markdown_to_html(report_content)
                    html_part = MIMEText(html_content, 'html', 'utf-8')
                    msg.attach(html_part)
                except:
                    pass  # Fall back to plain text only
            else:
                text_part = MIMEText(report_content, 'plain', 'utf-8')
                msg.attach(text_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return {
                "status": "success",
                "message": f"Email sent successfully to {to_address}",
                "timestamp": datetime.now().isoformat()
            }

        except smtplib.SMTPAuthenticationError:
            return {
                "status": "error",
                "message": "SMTP authentication failed. Check username and password.",
                "timestamp": datetime.now().isoformat()
            }
        except smtplib.SMTPException as e:
            return {
                "status": "error",
                "message": f"SMTP error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send email: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def _markdown_to_html(self, markdown_content: str) -> str:
        """
        Basic markdown to HTML conversion for email rendering.
        For production, consider using a library like markdown2 or mistune.
        """
        html = markdown_content

        # Basic conversions
        import re

        # Headers
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # Bold
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)

        # Italic
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)

        # Code blocks
        html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)

        # Inline code
        html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)

        # Line breaks
        html = html.replace('\n\n', '</p><p>')

        # Wrap in basic HTML structure
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
                h2 {{ color: #34495e; margin-top: 20px; }}
                h3 {{ color: #7f8c8d; }}
                code {{ background-color: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
                pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                strong {{ color: #2c3e50; }}
            </style>
        </head>
        <body>
            <p>{html}</p>
        </body>
        </html>
        """

        return html

    def test_connection(self) -> Dict[str, str]:
        """
        Test SMTP connection without sending an email.

        Returns:
            Dictionary with status and message
        """
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.username, self.password)

            return {
                "status": "success",
                "message": "SMTP connection successful"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"SMTP connection failed: {str(e)}"
            }
