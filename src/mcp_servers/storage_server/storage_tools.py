"""
Storage tools for saving research analysis reports locally.
Supports both Markdown and PDF formats.
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
    import markdown2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class ReportStorage:
    """Tool for storing research analysis reports locally."""

    def __init__(self, output_dir: str = "outputs/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_report(
        self,
        report_content: str,
        query: str,
        referenced_papers: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None,
        format: str = "pdf"
    ) -> Dict[str, str]:
        """
        Save a research analysis report to local storage.

        Args:
            report_content: The complete report content
            query: The original research query
            referenced_papers: List of ArXiv papers referenced in the analysis
            metadata: Additional metadata about the report
            format: Output format (pdf, markdown, json, txt)

        Returns:
            Dictionary with file path and status
        """
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_query = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in query)
            safe_query = safe_query[:50]  # Limit filename length

            # Add references section if papers are provided
            full_content = report_content
            if referenced_papers:
                references_section = self._format_references(referenced_papers)
                full_content = f"{report_content}\n\n{references_section}"

            if format == "pdf":
                if not PDF_AVAILABLE:
                    # Fall back to markdown if PDF libraries not available
                    format = "markdown"
                    filename = f"{timestamp}_{safe_query}.md"
                    filepath = self.output_dir / filename
                    return self._save_markdown(filepath, query, full_content, metadata)
                else:
                    filename = f"{timestamp}_{safe_query}.pdf"
                    filepath = self.output_dir / filename
                    return self._save_pdf(filepath, query, full_content, metadata)

            elif format == "markdown":
                filename = f"{timestamp}_{safe_query}.md"
                filepath = self.output_dir / filename
                return self._save_markdown(filepath, query, full_content, metadata)

            elif format == "json":
                filename = f"{timestamp}_{safe_query}.json"
                filepath = self.output_dir / filename
                return self._save_json(filepath, query, full_content, referenced_papers, metadata)

            else:  # txt
                filename = f"{timestamp}_{safe_query}.txt"
                filepath = self.output_dir / filename
                return self._save_text(filepath, query, full_content, metadata)

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to save report: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def _format_references(self, papers: List[Dict]) -> str:
        """Format referenced papers section."""
        references = "\n\n---\n\n## Referenced Papers\n\n"
        references += "The following papers from ArXiv were referenced in this analysis:\n\n"

        for i, paper in enumerate(papers, 1):
            references += f"**[{i}] {paper.get('title', 'Unknown Title')}**\n"
            authors = paper.get('authors', [])
            if authors:
                if len(authors) <= 3:
                    references += f"*Authors:* {', '.join(authors)}\n"
                else:
                    references += f"*Authors:* {', '.join(authors[:3])} et al. ({len(authors)} authors)\n"

            if paper.get('published'):
                references += f"*Published:* {paper['published']}\n"

            references += f"*ArXiv ID:* {paper.get('arxiv_id', 'N/A')}\n"
            references += f"*URL:* {paper.get('abs_url', 'N/A')}\n"
            references += f"*PDF:* {paper.get('pdf_url', 'N/A')}\n"

            if paper.get('categories'):
                references += f"*Categories:* {', '.join(paper['categories'])}\n"

            references += "\n"

        return references

    def _save_markdown(self, filepath: Path, query: str, content: str, metadata: Optional[Dict]) -> Dict:
        """Save report as Markdown file."""
        header = f"""# Research Analysis Report

**Query:** {query}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Format:** Markdown

---

"""
        full_content = header + content

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)

        return {
            "status": "success",
            "filepath": str(filepath),
            "filename": filepath.name,
            "format": "markdown",
            "size_bytes": filepath.stat().st_size,
            "timestamp": datetime.now().isoformat()
        }

    def _save_pdf(self, filepath: Path, query: str, content: str, metadata: Optional[Dict]) -> Dict:
        """Save report as PDF file."""
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Container for the 'Flowable' objects
        elements = []

        # Define styles
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#2c3e50',
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor='#34495e',
            spaceAfter=12,
            spaceBefore=12
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        )

        # Title
        elements.append(Paragraph("Research Analysis Report", title_style))
        elements.append(Spacer(1, 12))

        # Metadata
        metadata_text = f"<b>Query:</b> {query}<br/><b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elements.append(Paragraph(metadata_text, body_style))
        elements.append(Spacer(1, 20))

        # Convert markdown to HTML for better PDF rendering
        html_content = markdown2.markdown(content, extras=['tables', 'fenced-code-blocks'])

        # Split content into paragraphs and add to PDF
        paragraphs = html_content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                # Clean up HTML tags for reportlab
                para = para.replace('<p>', '').replace('</p>', '')
                para = para.replace('<strong>', '<b>').replace('</strong>', '</b>')
                para = para.replace('<em>', '<i>').replace('</em>', '</i>')

                try:
                    elements.append(Paragraph(para, body_style))
                    elements.append(Spacer(1, 6))
                except:
                    # If paragraph fails, add as plain text
                    pass

        # Build PDF
        doc.build(elements)

        return {
            "status": "success",
            "filepath": str(filepath),
            "filename": filepath.name,
            "format": "pdf",
            "size_bytes": filepath.stat().st_size,
            "timestamp": datetime.now().isoformat()
        }

    def _save_json(self, filepath: Path, query: str, content: str, papers: Optional[List[Dict]], metadata: Optional[Dict]) -> Dict:
        """Save report as JSON file."""
        report_data = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "report_content": content,
            "referenced_papers": papers or [],
            "metadata": metadata or {}
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        return {
            "status": "success",
            "filepath": str(filepath),
            "filename": filepath.name,
            "format": "json",
            "size_bytes": filepath.stat().st_size,
            "timestamp": datetime.now().isoformat()
        }

    def _save_text(self, filepath: Path, query: str, content: str, metadata: Optional[Dict]) -> Dict:
        """Save report as plain text file."""
        header = f"""Research Analysis Report

Query: {query}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

"""
        full_content = header + content

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)

        return {
            "status": "success",
            "filepath": str(filepath),
            "filename": filepath.name,
            "format": "text",
            "size_bytes": filepath.stat().st_size,
            "timestamp": datetime.now().isoformat()
        }

    def list_reports(self, limit: int = 10) -> List[Dict]:
        """
        List recently saved reports.

        Args:
            limit: Maximum number of reports to return

        Returns:
            List of report metadata dictionaries
        """
        try:
            reports = []

            # Get all report files sorted by modification time
            files = sorted(
                self.output_dir.glob("*"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            for filepath in files[:limit]:
                if filepath.is_file():
                    reports.append({
                        "filename": filepath.name,
                        "filepath": str(filepath),
                        "size_bytes": filepath.stat().st_size,
                        "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
                        "extension": filepath.suffix
                    })

            return reports

        except Exception as e:
            return [{
                "error": f"Failed to list reports: {str(e)}"
            }]

    def get_report(self, filename: str) -> Dict[str, str]:
        """
        Retrieve a specific report by filename.

        Args:
            filename: Name of the report file

        Returns:
            Dictionary with report content and metadata
        """
        try:
            filepath = self.output_dir / filename

            if not filepath.exists():
                return {
                    "status": "error",
                    "message": f"Report not found: {filename}"
                }

            # Only read text-based formats
            if filepath.suffix in ['.md', '.txt', '.json']:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = "[Binary file - cannot display content]"

            return {
                "status": "success",
                "filename": filename,
                "filepath": str(filepath),
                "content": content,
                "size_bytes": filepath.stat().st_size,
                "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to retrieve report: {str(e)}"
            }

    def delete_report(self, filename: str) -> Dict[str, str]:
        """
        Delete a specific report by filename.

        Args:
            filename: Name of the report file to delete

        Returns:
            Dictionary with status and message
        """
        try:
            filepath = self.output_dir / filename

            if not filepath.exists():
                return {
                    "status": "error",
                    "message": f"Report not found: {filename}"
                }

            filepath.unlink()

            return {
                "status": "success",
                "message": f"Report deleted: {filename}",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete report: {str(e)}"
            }

    def get_storage_info(self) -> Dict:
        """
        Get information about the storage directory.

        Returns:
            Dictionary with storage statistics
        """
        try:
            files = list(self.output_dir.glob("*"))
            total_size = sum(f.stat().st_size for f in files if f.is_file())

            return {
                "output_directory": str(self.output_dir),
                "total_reports": len(files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "pdf_support": PDF_AVAILABLE
            }

        except Exception as e:
            return {
                "error": f"Failed to get storage info: {str(e)}"
            }
