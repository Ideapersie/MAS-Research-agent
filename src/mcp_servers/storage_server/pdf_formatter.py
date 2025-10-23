"""
Professional PDF formatter for research analysis reports.
ArXiv-inspired design with tables, colored sections, and visual elements.
"""
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    HRFlowable, KeepTogether, Frame, PageTemplate
)
import markdown2


class ProfessionalPDFFormatter:
    """
    Professional PDF generator with ArXiv-inspired styling.

    Features:
    - Title page with metadata and usage table
    - Table of contents
    - Colored section headers
    - Info boxes (insights, benefits, warnings)
    - Professional tables
    - Code blocks
    - Referenced papers bibliography
    """

    def __init__(self):
        """Initialize formatter with color palette and styles."""
        # Color palette
        self.colors = {
            'primary': colors.HexColor('#2C3E50'),      # Dark blue
            'secondary': colors.HexColor('#3498DB'),    # Light blue
            'accent_orange': colors.HexColor('#F39C12'),  # Orange
            'accent_green': colors.HexColor('#27AE60'),   # Green
            'warning_red': colors.HexColor('#E74C3C'),    # Red
            'highlight_yellow': colors.HexColor('#F9E79F'), # Light yellow
            'code_bg': colors.HexColor('#ECF0F1'),      # Light gray
            'table_header': colors.HexColor('#BDC3C7'),  # Medium gray
            'table_alt': colors.HexColor('#F8F9F9'),    # Very light gray
        }

        # Create custom styles
        self.styles = self._create_styles()

    def _create_styles(self) -> Dict:
        """Create custom paragraph styles."""
        base_styles = getSampleStyleSheet()

        styles = {}

        # Title style
        styles['Title'] = ParagraphStyle(
            'CustomTitle',
            parent=base_styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=colors.white,
            spaceAfter=0,
            alignment=TA_CENTER,
            leftIndent=10,
            rightIndent=10,
        )

        # Subtitle style
        styles['Subtitle'] = ParagraphStyle(
            'CustomSubtitle',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=14,
            textColor=colors.white,
            spaceAfter=0,
            alignment=TA_CENTER,
        )

        # Section header (with colored bar background)
        styles['SectionHeader'] = ParagraphStyle(
            'SectionHeader',
            parent=base_styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.white,
            spaceAfter=0,
            spaceBefore=20,
            leftIndent=10,
            rightIndent=10,
        )

        # Subsection header
        styles['SubsectionHeader'] = ParagraphStyle(
            'SubsectionHeader',
            parent=base_styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=self.colors['primary'],
            spaceAfter=8,
            spaceBefore=12,
        )

        # Body text
        styles['Body'] = ParagraphStyle(
            'CustomBody',
            parent=base_styles['BodyText'],
            fontName='Times-Roman',
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=13,  # Line spacing
        )

        # Abstract text
        styles['Abstract'] = ParagraphStyle(
            'Abstract',
            parent=styles['Body'],
            fontName='Times-Italic',
            fontSize=11,
            leftIndent=30,
            rightIndent=30,
            spaceAfter=20,
        )

        # TOC entry
        styles['TOCEntry'] = ParagraphStyle(
            'TOCEntry',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=16,
            leftIndent=20,
        )

        # Code block
        styles['Code'] = ParagraphStyle(
            'Code',
            parent=base_styles['Code'],
            fontName='Courier',
            fontSize=9,
            leftIndent=20,
            rightIndent=20,
            spaceAfter=12,
            textColor=self.colors['primary'],
        )

        # Bullet list
        styles['Bullet'] = ParagraphStyle(
            'Bullet',
            parent=styles['Body'],
            leftIndent=30,
            bulletIndent=15,
            bulletFontName='Symbol',
        )

        # Footer
        styles['Footer'] = ParagraphStyle(
            'Footer',
            parent=base_styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
        )

        return styles

    def create_title_page(self, query: str, metadata: Optional[Dict] = None) -> List:
        """
        Create title page with header box, usage table, and abstract.

        Args:
            query: Research query
            metadata: Dictionary with usage data, models, etc.

        Returns:
            List of Flowable objects for title page
        """
        elements = []

        # Title box with colored background
        title_data = [[Paragraph("RESEARCH ANALYSIS REPORT", self.styles['Title'])]]
        title_table = Table(title_data, colWidths=[6.5*inch])
        title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.colors['primary']),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(title_table)
        elements.append(Spacer(1, 5))

        # Subtitle with query
        subtitle_data = [[Paragraph(f"Analysis of: {query}", self.styles['Subtitle'])]]
        subtitle_table = Table(subtitle_data, colWidths=[6.5*inch])
        subtitle_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.colors['secondary']),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(subtitle_table)
        elements.append(Spacer(1, 15))

        # Generated date
        gen_date = Paragraph(
            f"<font size=10>Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}</font>",
            self.styles['Body']
        )
        elements.append(gen_date)
        elements.append(Spacer(1, 15))

        # Usage summary table (if metadata provided)
        if metadata and 'usage' in metadata:
            usage = metadata['usage']

            usage_data = [
                ['API Usage & Cost Summary', ''],
                ['Total Tokens', f"{usage.get('total_tokens', 0):,}"],
                ['API Calls', str(usage.get('api_calls', 0))],
            ]

            # Add cost if available
            if 'actual_cost' in metadata:
                usage_data.append(['Actual Cost', f"${metadata['actual_cost']:.6f}"])

            # Add credits if available
            if 'credits_remaining' in metadata:
                usage_data.append(['Credits Remaining', f"${metadata['credits_remaining']:.2f}"])

            usage_table = Table(usage_data, colWidths=[2.5*inch, 2*inch])
            usage_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), self.colors['table_header']),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.colors['table_alt']]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(usage_table)
            elements.append(Spacer(1, 15))

        # Models used (if available)
        if metadata and 'models' in metadata:
            models = metadata['models']
            models_text = f"""<b>Models Used:</b><br/>
            • Performance Analyst: {models.get('performance_analyst', 'N/A')}<br/>
            • Critique Agent: {models.get('critique_agent', 'N/A')}<br/>
            • Synthesizer: {models.get('synthesizer', 'N/A')}"""
            elements.append(Paragraph(models_text, self.styles['Body']))
            elements.append(Spacer(1, 15))

        # Horizontal rule
        elements.append(HRFlowable(width="100%", thickness=2, color=self.colors['primary']))
        elements.append(Spacer(1, 15))

        return elements

    def create_abstract(self, abstract_text: str) -> List:
        """Create abstract section with proper formatting."""
        elements = []

        elements.append(Paragraph("<b>Abstract</b>", self.styles['Body']))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(abstract_text, self.styles['Abstract']))

        return elements

    def create_toc(self, sections: List[Tuple[str, int]]) -> List:
        """
        Create table of contents.

        Args:
            sections: List of (section_name, page_number) tuples

        Returns:
            List of Flowable objects for TOC
        """
        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph("TABLE OF CONTENTS", self.styles['SectionHeader']))
        elements.append(Spacer(1, 20))

        for section_name, page_num in sections:
            # Create TOC entry with dots
            toc_text = f"{section_name} {'.' * (70 - len(section_name))} {page_num}"
            elements.append(Paragraph(toc_text, self.styles['TOCEntry']))

        elements.append(PageBreak())

        return elements

    def create_section_header(self, title: str, section_type: str = 'default') -> List:
        """
        Create colored section header bar.

        Args:
            title: Section title
            section_type: Type for color ('executive', 'innovation', 'critical', 'recommendation', 'references')

        Returns:
            List of Flowable objects
        """
        elements = []

        # Choose color based on section type
        color_map = {
            'executive': self.colors['secondary'],
            'innovation': self.colors['secondary'],
            'critical': self.colors['accent_orange'],
            'recommendation': self.colors['accent_green'],
            'references': colors.HexColor('#9B59B6'),  # Purple
            'default': self.colors['primary'],
        }

        bg_color = color_map.get(section_type, color_map['default'])

        # Create section header with colored background
        header_data = [[Paragraph(title.upper(), self.styles['SectionHeader'])]]
        header_table = Table(header_data, colWidths=[6.5*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))

        elements.append(Spacer(1, 10))
        elements.append(header_table)
        elements.append(Spacer(1, 15))

        return elements

    def create_info_box(self, title: str, items: List[str], box_type: str = 'insight') -> List:
        """
        Create colored info box with icon.

        Args:
            title: Box title
            items: List of bullet points
            box_type: Type ('insight', 'benefit', 'warning', 'technical')

        Returns:
            List of Flowable objects
        """
        elements = []

        # Box styling based on type
        box_config = {
            'insight': {
                'icon': '[!]',
                'bg': self.colors['highlight_yellow'],
                'border': self.colors['accent_orange']
            },
            'benefit': {
                'icon': '[+]',
                'bg': colors.HexColor('#D5F4E6'),
                'border': self.colors['accent_green']
            },
            'warning': {
                'icon': '[!]',
                'bg': colors.HexColor('#FADBD8'),
                'border': self.colors['warning_red']
            },
            'technical': {
                'icon': '[i]',
                'bg': colors.HexColor('#D6EAF8'),
                'border': self.colors['secondary']
            }
        }

        config = box_config.get(box_type, box_config['insight'])

        # Build content
        content = f"<b>{config['icon']} {title}</b><br/>"
        for item in items:
            content += f"<font face='Symbol'>▸</font> {item}<br/>"

        box_para = Paragraph(content, self.styles['Body'])

        # Create table with border and background
        box_data = [[box_para]]
        box_table = Table(box_data, colWidths=[6*inch])
        box_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), config['bg']),
            ('BOX', (0, 0), (-1, -1), 1.5, config['border']),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))

        elements.append(box_table)
        elements.append(Spacer(1, 12))

        return elements

    def create_table_from_data(self, data: List[List[str]], headers: Optional[List[str]] = None) -> Table:
        """
        Create professional table with styling.

        Args:
            data: Table data (list of rows)
            headers: Optional header row

        Returns:
            Styled Table object
        """
        # Prepare data
        if headers:
            table_data = [headers] + data
            header_rows = 1
        else:
            table_data = data
            header_rows = 0

        # Calculate column widths
        num_cols = len(table_data[0]) if table_data else 1
        col_width = 6.5 * inch / num_cols

        # Create table
        table = Table(table_data, colWidths=[col_width] * num_cols)

        # Style
        style_commands = [
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]

        if header_rows > 0:
            style_commands.extend([
                ('BACKGROUND', (0, 0), (-1, header_rows-1), self.colors['table_header']),
                ('TEXTCOLOR', (0, 0), (-1, header_rows-1), colors.white),
                ('FONTNAME', (0, 0), (-1, header_rows-1), 'Helvetica-Bold'),
            ])

        # Alternating row colors for data
        if len(table_data) > header_rows:
            style_commands.append(
                ('ROWBACKGROUNDS', (0, header_rows), (-1, -1),
                 [colors.white, self.colors['table_alt']])
            )

        table.setStyle(TableStyle(style_commands))

        return table

    def create_code_block(self, code: str) -> List:
        """Create formatted code block with background."""
        elements = []

        # Clean code
        code = code.strip()

        code_para = Paragraph(f"<font face='Courier' size=9>{code}</font>", self.styles['Code'])

        code_data = [[code_para]]
        code_table = Table(code_data, colWidths=[6*inch])
        code_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.colors['code_bg']),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ]))

        elements.append(code_table)
        elements.append(Spacer(1, 12))

        return elements

    def create_references(self, papers: List[Dict]) -> List:
        """
        Create formatted references section.

        Args:
            papers: List of paper dictionaries with metadata

        Returns:
            List of Flowable objects
        """
        elements = []

        elements.extend(self.create_section_header("REFERENCED PAPERS", "references"))

        for i, paper in enumerate(papers, 1):
            # Reference number and title
            ref_text = f"<b>[{i}] {paper.get('title', 'Unknown Title')}</b><br/>"

            # Authors
            authors = paper.get('authors', [])
            if authors:
                if len(authors) <= 3:
                    ref_text += f"<i>Authors:</i> {', '.join(authors)}<br/>"
                else:
                    ref_text += f"<i>Authors:</i> {', '.join(authors[:3])} et al. ({len(authors)} authors)<br/>"

            # Publication info
            if paper.get('published'):
                ref_text += f"<i>Published:</i> {paper['published']}<br/>"

            # ArXiv ID
            ref_text += f"<i>ArXiv ID:</i> {paper.get('arxiv_id', 'N/A')}<br/>"

            # URL
            if paper.get('abs_url'):
                ref_text += f"<i>URL:</i> {paper['abs_url']}<br/>"

            elements.append(Paragraph(ref_text, self.styles['Body']))
            elements.append(Spacer(1, 15))

        return elements

    def parse_markdown_to_flowables(self, content: str, metadata: Optional[Dict] = None) -> List:
        """
        Parse markdown content and convert to styled PDF Flowables.

        Args:
            content: Markdown content
            metadata: Optional metadata for context

        Returns:
            List of Flowable objects
        """
        elements = []

        # Split content by sections
        lines = content.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Section headers (##)
            if line.startswith('## '):
                section_title = line[3:].strip()
                section_type = self._detect_section_type(section_title)
                elements.extend(self.create_section_header(section_title, section_type))

            # Subsection headers (###)
            elif line.startswith('### '):
                subsection_title = line[4:].strip()
                elements.append(Paragraph(subsection_title, self.styles['SubsectionHeader']))

            # Code blocks
            elif line.startswith('```'):
                # Collect code block
                i += 1
                code_lines = []
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                code = '\n'.join(code_lines)
                elements.extend(self.create_code_block(code))

            # Bullet lists
            elif line.startswith('- ') or line.startswith('* '):
                bullet_text = line[2:].strip()
                bullet_text = f"<font face='Symbol'>▸</font> {bullet_text}"
                elements.append(Paragraph(bullet_text, self.styles['Bullet']))

            # Horizontal rules
            elif line.startswith('---') or line.startswith('***'):
                elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
                elements.append(Spacer(1, 10))

            # Regular paragraphs
            elif line:
                # Convert markdown formatting
                formatted_line = self._format_markdown_inline(line)
                elements.append(Paragraph(formatted_line, self.styles['Body']))

            # Empty line - spacing
            else:
                if elements:  # Don't add space at the beginning
                    elements.append(Spacer(1, 6))

            i += 1

        return elements

    def _detect_section_type(self, title: str) -> str:
        """Detect section type from title for color coding."""
        title_lower = title.lower()

        if 'executive' in title_lower or 'summary' in title_lower:
            return 'executive'
        elif 'innovation' in title_lower or 'contribution' in title_lower:
            return 'innovation'
        elif 'critical' in title_lower or 'limitation' in title_lower or 'challenge' in title_lower:
            return 'critical'
        elif 'recommendation' in title_lower or 'conclusion' in title_lower:
            return 'recommendation'
        elif 'reference' in title_lower or 'citation' in title_lower or 'paper' in title_lower:
            return 'references'
        else:
            return 'default'

    def _format_markdown_inline(self, text: str) -> str:
        """Convert inline markdown formatting to HTML tags for reportlab."""
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)

        # Italic
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)

        # Inline code
        text = re.sub(r'`(.+?)`', r'<font face="Courier" size=9>\1</font>', text)

        return text
