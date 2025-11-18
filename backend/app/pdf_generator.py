"""
Professional PDF Report Generator
Generates high-quality, scientifically-formatted research reports

Design inspired by:
- Nature journal formatting
- IEEE publication standards
- Academic research papers
- Professional consulting reports
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
)
from reportlab.pdfgen import canvas
from datetime import datetime
import re
import os


class ScientificReportCanvas(canvas.Canvas):
    """Custom canvas for scientific report styling with headers/footers"""

    def __init__(self, *args, **kwargs):
        self.report_title = kwargs.pop('report_title', 'Research Report')
        self.report_author = kwargs.pop('report_author', 'Agent Management Platform')
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, total_pages):
        """Draw professional header and footer"""
        page_num = self._pageNumber

        # Only add decorations after cover page
        if page_num <= 1:
            return

        self.saveState()

        # Footer
        self.setFont('Helvetica', 9)
        self.setFillColor(colors.HexColor('#666666'))

        # Page number (centered)
        self.drawCentredString(
            letter[0] / 2.0,
            0.5 * inch,
            f"Page {page_num} of {total_pages}"
        )

        # Report title (left) - truncate if too long
        title_text = self.report_title[:50]
        if len(self.report_title) > 50:
            title_text += "..."
        self.drawString(
            0.75 * inch,
            0.5 * inch,
            title_text
        )

        # Date (right)
        self.drawRightString(
            letter[0] - 0.75 * inch,
            0.5 * inch,
            datetime.now().strftime('%B %Y')
        )

        # Header line
        self.setStrokeColor(colors.HexColor('#1976D2'))
        self.setLineWidth(0.5)
        self.line(
            0.75 * inch,
            letter[1] - 0.6 * inch,
            letter[0] - 0.75 * inch,
            letter[1] - 0.6 * inch
        )

        self.restoreState()


class PDFReportGenerator:
    """Generate high-quality PDF research reports"""

    def __init__(self, output_dir="/home/rpas/research_reports/pdfs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.page_width, self.page_height = letter
        self.margin = 0.75 * inch
        self.content_width = self.page_width - (2 * self.margin)

        # Professional color scheme
        self.colors = {
            'primary': colors.HexColor('#1976D2'),      # Professional blue
            'secondary': colors.HexColor('#424242'),    # Dark gray
            'accent': colors.HexColor('#FF6F00'),       # Accent orange
            'text': colors.HexColor('#212121'),         # Near black
            'light_gray': colors.HexColor('#F5F5F5'),  # Light background
        }

        # Setup professional styles
        self.styles = self._create_professional_styles()

    def _create_professional_styles(self):
        """Create professional document styles"""
        styles = getSampleStyleSheet()

        # Cover Title - Large, prominent
        styles.add(ParagraphStyle(
            name='CoverTitle',
            parent=styles['Title'],
            fontSize=28,
            textColor=self.colors['primary'],
            spaceAfter=0.3 * inch,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=34
        ))

        # Cover Subtitle
        styles.add(ParagraphStyle(
            name='CoverSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=self.colors['secondary'],
            spaceAfter=0.5 * inch,
            alignment=TA_CENTER,
            fontName='Helvetica',
            leading=18
        ))

        # Section Heading (H1) - Professional blue
        styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=self.colors['primary'],
            spaceBefore=0.3 * inch,
            spaceAfter=0.15 * inch,
            fontName='Helvetica-Bold',
            leftIndent=0
        ))

        # Subsection Heading (H2)
        styles.add(ParagraphStyle(
            name='SubsectionHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=self.colors['secondary'],
            spaceBefore=0.2 * inch,
            spaceAfter=0.1 * inch,
            fontName='Helvetica-Bold'
        ))

        # Sub-subsection (H3)
        styles.add(ParagraphStyle(
            name='SubSubHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=self.colors['text'],
            spaceBefore=0.15 * inch,
            spaceAfter=0.08 * inch,
            fontName='Helvetica-Bold'
        ))

        # Body Text - Serif for readability
        styles.add(ParagraphStyle(
            name='BodyText',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.colors['text'],
            alignment=TA_JUSTIFY,
            spaceAfter=0.12 * inch,
            fontName='Times-Roman',
            leading=14
        ))

        # Citation/Reference
        styles.add(ParagraphStyle(
            name='Citation',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.colors['secondary'],
            leftIndent=0.25 * inch,
            spaceAfter=0.08 * inch,
            fontName='Times-Roman',
            leading=12
        ))

        return styles

    def _create_cover_page(self, title: str, subtitle: str, author: str, date: str):
        """Generate professional cover page"""
        story = []

        # Add vertical space
        story.append(Spacer(1, 2 * inch))

        # Main title
        story.append(Paragraph(title, self.styles['CoverTitle']))

        # Subtitle/description
        if subtitle:
            story.append(Paragraph(subtitle, self.styles['CoverSubtitle']))

        # Add space
        story.append(Spacer(1, 0.3 * inch))

        # Author and date info
        info_text = f"""
        <para align=center>
        <font name="Helvetica" size=12 color="#424242">
        <b>Prepared by:</b> {author}<br/>
        <b>Date:</b> {date}<br/>
        <b>Classification:</b> Research Report
        </font>
        </para>
        """
        story.append(Paragraph(info_text, self.styles['Normal']))

        # Add footer space
        story.append(Spacer(1, 1.5 * inch))

        # Disclaimer/footer
        footer_text = """
        <para align=center>
        <font name="Helvetica" size=9 color="#999999">
        <i>This report was generated using AI-assisted research.<br/>
        Please verify all information for critical applications.</i>
        </font>
        </para>
        """
        story.append(Paragraph(footer_text, self.styles['Normal']))

        # Page break after cover
        story.append(PageBreak())

        return story

    def _parse_markdown_to_flowables(self, markdown_text: str):
        """Convert markdown to ReportLab flowables with enhanced formatting"""
        story = []
        lines = markdown_text.split('\n')
        current_paragraph = []

        for line in lines:
            stripped = line.strip()

            # H1 headings
            if line.startswith('# ') and not line.startswith('## '):
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    story.append(Paragraph(self._format_inline(para_text), self.styles['BodyText']))
                    current_paragraph = []
                heading_text = line[2:].strip()
                story.append(Paragraph(self._escape_html(heading_text), self.styles['SectionHeading']))

            # H2 headings
            elif line.startswith('## ') and not line.startswith('### '):
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    story.append(Paragraph(self._format_inline(para_text), self.styles['BodyText']))
                    current_paragraph = []
                heading_text = line[3:].strip()
                story.append(Paragraph(self._escape_html(heading_text), self.styles['SubsectionHeading']))

            # H3 headings
            elif line.startswith('### '):
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    story.append(Paragraph(self._format_inline(para_text), self.styles['BodyText']))
                    current_paragraph = []
                heading_text = line[4:].strip()
                story.append(Paragraph(self._escape_html(heading_text), self.styles['SubSubHeading']))

            # Bullet points
            elif stripped.startswith('- ') or stripped.startswith('* '):
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    story.append(Paragraph(self._format_inline(para_text), self.styles['BodyText']))
                    current_paragraph = []
                bullet_text = '• ' + self._format_inline(stripped[2:])
                story.append(Paragraph(bullet_text, self.styles['BodyText']))

            # Numbered lists
            elif re.match(r'^\d+\.\s', stripped):
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    story.append(Paragraph(self._format_inline(para_text), self.styles['BodyText']))
                    current_paragraph = []
                story.append(Paragraph(self._format_inline(stripped), self.styles['Citation']))

            # Empty lines
            elif not stripped:
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    story.append(Paragraph(self._format_inline(para_text), self.styles['BodyText']))
                    current_paragraph = []
                story.append(Spacer(1, 0.08 * inch))

            # Regular text
            else:
                current_paragraph.append(stripped)

        # Add remaining paragraph
        if current_paragraph:
            para_text = ' '.join(current_paragraph)
            story.append(Paragraph(self._format_inline(para_text), self.styles['BodyText']))

        return story

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'))

    def _format_inline(self, text: str) -> str:
        """Process inline markdown formatting (bold, italic, code)"""
        # Escape HTML first
        text = self._escape_html(text)

        # Bold: **text**
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)

        # Italic: *text*
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)

        # Inline code: `text`
        text = re.sub(r'`(.+?)`', r'<font name="Courier" size=10>\1</font>', text)

        return text

    def markdown_to_pdf(self, markdown_content: str, title: str, agent_name: str, metadata: dict = None) -> str:
        """
        Convert markdown research report to professional PDF

        Args:
            markdown_content: Markdown-formatted research content
            title: Report title
            agent_name: Name of the agent that generated the report
            metadata: Additional metadata

        Returns:
            Path to generated PDF file
        """
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in title)[:50]
        filename = f"{agent_name.replace(' ', '_')}_{safe_title}_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        # Create document with custom canvas
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin,
            title=title,
            author=agent_name
        )

        # Build story
        story = []

        # Cover page
        date_str = datetime.now().strftime('%B %d, %Y')
        subtitle = "AI-Generated Research Report"
        story.extend(self._create_cover_page(title, subtitle, agent_name, date_str))

        # Main content
        story.extend(self._parse_markdown_to_flowables(markdown_content))

        # Build PDF with custom canvas
        doc.build(
            story,
            canvasmaker=lambda *args, **kwargs: ScientificReportCanvas(
                *args,
                report_title=title,
                report_author=agent_name,
                **kwargs
            )
        )

        print(f"   📄 PDF generated: {filename}")
        return filepath


# Singleton instance
pdf_generator = PDFReportGenerator()
