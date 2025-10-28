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
    from .pdf_formatter import ProfessionalPDFFormatter
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# LaTeX generation
from .latex_formatter import LaTeXFormatter


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
                    # Pass referenced_papers to PDF generator (don't append to content for PDF)
                    return self._save_pdf(filepath, query, report_content, metadata, referenced_papers)

            elif format == "markdown":
                filename = f"{timestamp}_{safe_query}.md"
                filepath = self.output_dir / filename
                return self._save_markdown(filepath, query, full_content, metadata)

            elif format == "latex":
                filename = f"{timestamp}_{safe_query}.tex"
                filepath = self.output_dir / filename
                # Also generate .bib file
                bib_filename = f"{timestamp}_{safe_query}.bib"
                bib_filepath = self.output_dir / bib_filename
                return self._save_latex(filepath, bib_filepath, query, report_content, metadata, referenced_papers)

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
        """Format referenced papers section with clickable links."""
        references = "\n\n---\n\n## References\n\n"
        references += "The following research papers were referenced in this analysis:\n\n"

        for i, paper in enumerate(papers, 1):
            # Paper title with index
            title = paper.get('title', 'Unknown Title')
            references += f"### [{i}] {title}\n\n"

            # Authors
            authors = paper.get('authors', [])
            if authors:
                if len(authors) <= 3:
                    references += f"**Authors:** {', '.join(authors)}\n\n"
                else:
                    references += f"**Authors:** {', '.join(authors[:3])} et al. ({len(authors)} total authors)\n\n"

            # Publication date
            if paper.get('published'):
                # Format date nicely if it's a full timestamp
                pub_date = paper['published']
                if 'T' in pub_date:  # ISO format datetime
                    pub_date = pub_date.split('T')[0]  # Just get YYYY-MM-DD
                references += f"**Published:** {pub_date}\n\n"

            # ArXiv ID
            arxiv_id = paper.get('arxiv_id', 'N/A')
            references += f"**ArXiv ID:** {arxiv_id}\n\n"

            # Clickable links
            abs_url = paper.get('abs_url', '')
            pdf_url = paper.get('pdf_url', '')

            if abs_url or pdf_url:
                references += "**Links:**\n"
                if abs_url:
                    references += f"- [View Abstract]({abs_url})\n"
                if pdf_url:
                    references += f"- [Download PDF]({pdf_url})\n"
                references += "\n"

            # Categories
            if paper.get('categories'):
                categories = ', '.join(paper['categories'])
                references += f"**Categories:** {categories}\n\n"

            # DOI if available
            if paper.get('doi'):
                doi = paper['doi']
                references += f"**DOI:** [{doi}](https://doi.org/{doi})\n\n"

            # Abstract preview (first 200 characters)
            if paper.get('summary'):
                abstract = paper['summary']
                if len(abstract) > 300:
                    abstract = abstract[:300] + "..."
                references += f"**Abstract:** {abstract}\n\n"

            references += "---\n\n"

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

    def _save_pdf(self, filepath: Path, query: str, content: str, metadata: Optional[Dict],
                  referenced_papers: Optional[List[Dict]] = None) -> Dict:
        """Save report as PDF file using professional formatter."""
        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=50,
            bottomMargin=50
        )

        # Initialize professional formatter
        formatter = ProfessionalPDFFormatter()

        # Clean content - remove markdown code fence if present
        content = self._clean_markdown_fence(content)

        # Container for all flowable objects
        elements = []

        # 1. Title page with usage table and metadata
        elements.extend(formatter.create_title_page(query, metadata))

        # 2. Extract abstract if present (first paragraph after # heading)
        abstract = self._extract_abstract(content)
        if abstract:
            elements.extend(formatter.create_abstract(abstract))

        # 3. Page break before content
        elements.append(PageBreak())

        # 4. Parse and add main content
        content_elements = formatter.parse_markdown_to_flowables(content, metadata)
        elements.extend(content_elements)

        # 5. Add referenced papers section if provided
        if referenced_papers:
            elements.append(PageBreak())
            elements.extend(formatter.create_references(referenced_papers))

        # 6. Build the PDF
        doc.build(elements)

        return {
            "status": "success",
            "filepath": str(filepath),
            "filename": filepath.name,
            "format": "pdf",
            "size_bytes": filepath.stat().st_size,
            "timestamp": datetime.now().isoformat()
        }

    def _clean_markdown_fence(self, content: str) -> str:
        """Remove markdown code fence wrapper if present."""
        lines = content.strip().split('\n')

        # Check if content is wrapped in ```markdown ... ```
        if lines and lines[0].strip().startswith('```'):
            # Remove first line (opening fence)
            lines = lines[1:]

            # Remove last line if it's a closing fence
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]

            return '\n'.join(lines)

        return content

    def _extract_abstract(self, content: str) -> Optional[str]:
        """Extract abstract/executive summary from content."""
        lines = content.split('\n')

        # Look for Executive Summary or Abstract section
        in_abstract = False
        abstract_lines = []

        for line in lines:
            if '## Executive Summary' in line or '## Abstract' in line:
                in_abstract = True
                continue
            elif in_abstract and line.startswith('##'):
                # Hit next section
                break
            elif in_abstract and line.strip():
                abstract_lines.append(line.strip())

        if abstract_lines:
            return ' '.join(abstract_lines)

        return None

    def _save_latex(self, tex_filepath: Path, bib_filepath: Path, query: str, content: str,
                    metadata: Optional[Dict], referenced_papers: Optional[List[Dict]] = None) -> Dict:
        """Save report as LaTeX file with BibTeX bibliography."""
        # Initialize LaTeX formatter
        formatter = LaTeXFormatter()

        # Extract base name (without extension) for bibliography reference
        bib_basename = bib_filepath.stem  # e.g., "20241028_104852_report" from "20241028_104852_report.bib"

        # Generate LaTeX and BibTeX content
        latex_content, bibtex_content = formatter.generate_document(
            content=content,
            query=query,
            metadata=metadata,
            referenced_papers=referenced_papers,
            bib_basename=bib_basename
        )

        # Save .tex file
        with open(tex_filepath, 'w', encoding='utf-8') as f:
            f.write(latex_content)

        # Always save .bib file (even if empty) to match .tex bibliography reference
        bib_saved = False
        if bibtex_content:
            with open(bib_filepath, 'w', encoding='utf-8') as f:
                f.write(bibtex_content)
            bib_saved = True
            print(f"[LATEX] BibTeX bibliography saved to: {bib_filepath}")
        else:
            # Create empty .bib file with explanatory comment
            empty_bib_content = """% Empty BibTeX file
% WARNING: No papers were tracked during analysis
% This usually means:
%   1. The agents did not call search_arxiv tools
%   2. The ArXiv search returned 0 results
%   3. Paper tracking failed for some reason
%
% To fix: Ensure agents use search_arxiv, search_arxiv_by_author, or get_arxiv_paper tools
"""
            with open(bib_filepath, 'w', encoding='utf-8') as f:
                f.write(empty_bib_content)
            bib_saved = True
            print(f"[LATEX] ⚠️  WARNING: Created empty BibTeX file (no papers tracked): {bib_filepath}")

        # Validate files were created
        if not tex_filepath.exists():
            raise IOError(f"Failed to create LaTeX file: {tex_filepath}")

        if not bib_filepath.exists():
            raise IOError(f"Failed to create BibTeX file: {bib_filepath}")

        return {
            "status": "success",
            "filepath": str(tex_filepath),
            "bib_filepath": str(bib_filepath) if bib_saved else None,
            "filename": tex_filepath.name,
            "format": "latex",
            "size_bytes": tex_filepath.stat().st_size,
            "timestamp": datetime.now().isoformat(),
            "message": f"LaTeX document generated successfully. Compile with: pdflatex {tex_filepath.name} && bibtex {bib_basename} && pdflatex {tex_filepath.name} && pdflatex {tex_filepath.name}"
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
