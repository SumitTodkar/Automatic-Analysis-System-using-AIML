"""
Industry-Level Business Analysis Report Generator
Format: DATA → GRAPH → INSIGHT → ACTION → IMPACT
Fonts:  Poppins (headings) + Inter (body)
"""
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Image, PageBreak, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.colors import HexColor
import json, re
from dataclasses import dataclass

from core.config.paths import path_config
from core.config.constants import PDF_CONSTANTS
from core.logging.logger import get_logger, log_execution
from domain.exceptions.custom import PDFGenerationError
from .pdf_styles import get_custom_styles

logger = get_logger(__name__)

# ── Palette ────────────────────────────────────────────────────────────────────
NAVY       = HexColor('#0A1628')
BLUE       = HexColor('#1D4ED8')
BLUE_LT    = HexColor('#3B82F6')
ACCENT_BG  = HexColor('#EFF6FF')
GREEN      = HexColor('#16A34A')
GREEN_BG   = HexColor('#F0FDF4')
AMBER      = HexColor('#D97706')
AMBER_BG   = HexColor('#FFFBEB')
RED        = HexColor('#DC2626')
TEXT       = HexColor('#111827')
MUTED      = HexColor('#6B7280')
BORDER     = HexColor('#E5E7EB')
BG_LIGHT   = HexColor('#F9FAFB')
WHITE      = HexColor('#FFFFFF')
STRIPE1    = HexColor('#F0F9FF')
STRIPE2    = HexColor('#FFFFFF')


@dataclass
class TOCEntry:
    title: str
    level: int
    page_number: Optional[int] = None


class DynamicTOC:
    def __init__(self):
        self.entries: List[TOCEntry] = []
        self._page = 1
        self._toc_pages = 0

    @property
    def current_page(self):
        return self._page + self._toc_pages

    def add_entry(self, title: str, level: int):
        self.entries.append(TOCEntry(title, level, self._page + self._toc_pages))

    def increment_page(self, n=1):
        self._page += n

    def set_toc_pages(self, n: int):
        self._toc_pages = n
        for e in self.entries:
            if e.page_number is not None:
                e.page_number += n

    def create_toc_content(self, styles) -> List:
        els = []
        els.append(Paragraph("Table of Contents", styles['CustomChapterTitle']))
        els.append(HRFlowable(width="100%", thickness=1.5, color=BLUE))
        els.append(Spacer(1, 0.15*inch))
        for e in self.entries:
            if e.title in ("Cover", "Table of Contents"):
                continue
            indent = "    " * (e.level - 1)
            title = f"{indent}{e.title}"
            dots = "." * max(3, 63 - len(title))
            line = f"{title}{dots}{e.page_number}"
            sname = {1: 'CustomTOCEntry', 2: 'CustomTOCEntry2', 3: 'CustomTOCEntry3'}.get(e.level, 'CustomTOCEntry')
            els.append(Paragraph(line, styles[sname]))
        els.append(PageBreak())
        return els

    def reset(self):
        self._page = 1
        self._toc_pages = 0
        self.entries = []


class PDFGenerator:
    W = A4[0]

    def __init__(self):
        self.styles = get_custom_styles()
        self.toc = DynamicTOC()
        self.report_title = "Business Analysis Report"

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _valid_graph(self, p: str) -> bool:
        try:
            path = Path(p)
            return path.exists() and path.is_file() and path.stat().st_size > 0
        except Exception:
            return False

    def _load_stats(self, stem: str) -> Dict:
        files = list(path_config.STATS_DIR.glob(f"{stem}*_stats.json"))
        if not files:
            return {}
        try:
            with open(sorted(files)[-1]) as f:
                return json.load(f)
        except Exception:
            return {}

    def _parse_sections(self, content: Dict) -> List[Dict]:
        result = []
        for s in content.get('sections', []):
            if not isinstance(s, dict):
                continue
            h = s.get('heading', '').strip()
            b = s.get('content', '').strip()
            # Never render raw JSON
            if b.startswith('{') or b.startswith('['):
                continue
            if h and b:
                result.append({'heading': h, 'content': b})
        return result

    def _fmt_title(self, t: str, max_len: int = 55) -> str:
        """Smart title truncation — cuts at word boundary."""
        t = t.strip('"\' ').strip()
        words = t.replace('_', ' ').split()
        title = ' '.join(w.capitalize() for w in words)
        if len(title) <= max_len:
            return title
        cut = title[:max_len].rsplit(' ', 1)[0]
        return cut + '...'

    # ── Header / Footer ────────────────────────────────────────────────────────
    def create_header_footer(self, canvas, doc):
        canvas.saveState()
        w, h = A4
        m = PDF_CONSTANTS['MARGIN']

        # Top bar
        canvas.setFillColor(NAVY)
        canvas.rect(m, h - 46, w - 2*m, 16, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont('Helvetica-Bold', 8)
        canvas.drawString(m + 8, h - 36, self.report_title)
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(w - m - 8, h - 36,
                               datetime.now().strftime("%B %d, %Y"))

        # Bottom line + page number
        canvas.setFillColor(BORDER)
        canvas.rect(m, 36, w - 2*m, 0.8, fill=1, stroke=0)
        canvas.setFillColor(MUTED)
        canvas.setFont('Helvetica', 7.5)
        canvas.drawCentredString(w/2, 22, f"Page {doc.page}  ·  Confidential Business Report")
        canvas.restoreState()

    # ── Cover Page ─────────────────────────────────────────────────────────────
    def create_cover_page(self) -> List:
        els = []
        self.toc.add_entry("Cover", 1)

        # Hero block
        hero = Table(
            [[Paragraph(self.report_title, self.styles['CustomMainTitle'])]],
            colWidths=[6.5*inch]
        )
        hero.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), NAVY),
            ('TOPPADDING', (0,0), (-1,-1), 52),
            ('BOTTOMPADDING', (0,0), (-1,-1), 52),
            ('LEFTPADDING', (0,0), (-1,-1), 28),
            ('RIGHTPADDING', (0,0), (-1,-1), 28),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))

        sub = Table(
            [[Paragraph(
                f'<font color="#1D4ED8"><b>AI-Powered Business Intelligence</b></font>'
                f'  &nbsp;·&nbsp;  '
                f'<font color="#6B7280">{datetime.now().strftime("%B %d, %Y")}</font>',
                self.styles['CustomHeader']
            )]],
            colWidths=[6.5*inch]
        )
        sub.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), ACCENT_BG),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))

        els.append(Spacer(1, 1.0*inch))
        els.append(hero)
        els.append(sub)
        els.append(Spacer(1, 0.3*inch))
        els.append(HRFlowable(width="100%", thickness=2, color=BLUE))
        els.append(Spacer(1, 0.4*inch))

        # Quick stats placeholder row
        summary_items = [
            ("📊", "Automated Analysis"),
            ("🤖", "AI-Generated Insights"),
            ("📈", "Actionable Recommendations"),
            ("💼", "Business-Ready Format"),
        ]
        pill_data = [[Paragraph(f'{i} {t}', self.styles['CustomBullet']) for i, t in summary_items]]
        pill_table = Table(pill_data, colWidths=[1.6*inch]*4)
        pill_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
            ('BOX', (0,0), (-1,-1), 1, BORDER),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        els.append(pill_table)
        els.append(Spacer(1, 1.6*inch))
        els.append(Paragraph(
            '<font color="#9CA3AF"><i>This report was automatically generated. '
            'Validate insights with domain experts before making decisions.</i></font>',
            self.styles['CustomCaption']
        ))
        els.append(PageBreak())
        self.toc.increment_page()
        return els

    # ── KPI Cards ──────────────────────────────────────────────────────────────
    def _kpi_cards(self, stats: Dict) -> Optional[Table]:
        ORDER = ['total', 'total_records', 'count', 'mean', 'median',
                 'max', 'outlier_count', 'top_category', 'min']
        LABELS = {
            'total': 'Total', 'mean': 'Average', 'median': 'Median',
            'count': 'Count', 'total_records': 'Records',
            'min': 'Minimum', 'max': 'Maximum',
            'outlier_count': 'Outliers', 'top_category': 'Top Category',
        }
        cards = []
        for k in ORDER:
            if k not in stats:
                continue
            v = stats[k]
            if isinstance(v, float):
                val = f"{v:,.2f}"
            elif isinstance(v, int):
                val = f"{v:,}"
            else:
                val = str(v)[:18]
            cards.append({'label': LABELS.get(k, k), 'value': val})
            if len(cards) == 4:
                break
        if not cards:
            return None
        n = len(cards)
        cw = 6.5 * inch / n
        top_row = [[Paragraph(c['value'], self.styles['CustomKPIValue']) for c in cards]]
        bot_row = [[Paragraph(c['label'],  self.styles['CustomKPILabel']) for c in cards]]
        t = Table(top_row + bot_row, colWidths=[cw]*n)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), ACCENT_BG),
            ('BOX', (0,0), (-1,-1), 1.2, BLUE_LT),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        return t

    # ── Stats Summary Table ────────────────────────────────────────────────────
    def _stats_table(self, stats: Dict) -> Optional[Table]:
        SKIP = {'question','note','error','columns','numeric_columns',
                'categorical_columns','total_records'}
        LABEL_MAP = {
            'mean':'Average','median':'Median','std':'Std Deviation',
            'min':'Minimum','max':'Maximum','count':'Record Count',
            'total':'Total','outlier_count':'Outliers Detected',
            'skewness':'Data Skewness','correlation':'Correlation',
            'top_category':'Top Category',
        }
        rows = [[
            Paragraph('<b>Metric</b>', self.styles['CustomBodyText']),
            Paragraph('<b>Value</b>',  self.styles['CustomBodyText']),
            Paragraph('<b>Insight</b>', self.styles['CustomBodyText']),
        ]]
        def _insight(k, v):
            try:
                if k == 'std':
                    return 'High variability' if float(v) > 10 else 'Consistent data'
                if k == 'skewness':
                    fv = float(v)
                    if fv > 1:   return 'Right-skewed — few high outliers pull avg up'
                    if fv < -1:  return 'Left-skewed — a few very low values'
                    return 'Symmetric distribution'
                if k == 'outlier_count':
                    return f'⚠️ {v} anomalies — investigate' if int(v) > 0 else '✅ No outliers found'
                if k == 'correlation':
                    a = abs(float(v))
                    return ('Strong' if a > 0.7 else 'Moderate' if a > 0.4 else 'Weak') + ' relationship'
                if k == 'mean':    return 'Typical transaction value'
                if k == 'median':  return 'Mid-point — 50% above, 50% below'
                if k == 'min':     return 'Lowest recorded value'
                if k == 'max':     return 'Highest recorded value'
                if k == 'total':   return 'Sum of all records'
            except Exception:
                pass
            return ''
        for k, v in stats.items():
            if k in SKIP:
                continue
            label = LABEL_MAP.get(k, k.replace('_',' ').title())
            val   = f"{v:,.2f}" if isinstance(v, float) else (f"{v:,}" if isinstance(v, int) else str(v)[:30])
            insight = _insight(k, v)
            rows.append([
                Paragraph(label, self.styles['CustomBodyText']),
                Paragraph(f'<b>{val}</b>', self.styles['CustomBodyText']),
                Paragraph(f'<i>{insight}</i>', self.styles['CustomBodyText']),
            ])
        if len(rows) <= 1:
            return None
        t = Table(rows, colWidths=[2.0*inch, 1.6*inch, 2.9*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), NAVY),
            ('TEXTCOLOR', (0,0), (-1,0), WHITE),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9.5),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [STRIPE1, STRIPE2]),
            ('GRID', (0,0), (-1,-1), 0.4, BORDER),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        return t

    # ── Callout Box ────────────────────────────────────────────────────────────
    def _callout(self, icon: str, title: str, lines: List[str],
                 bg=ACCENT_BG, border=BLUE) -> Table:
        rows = [[Paragraph(f'{icon}  <b>{title}</b>', self.styles['CustomCallout'])]]
        for line in lines:
            rows.append([Paragraph(f'• {line}', self.styles['CustomBullet'])])
        t = Table(rows, colWidths=[6.3*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg),
            ('BOX', (0,0), (-1,-1), 1.5, border),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 14),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        return t

    # ── Insight Card (What / Why / Action) ────────────────────────────────────
    def _insight_card(self, number: int, what: str, why: str, action: str) -> Table:
        num_cell = Paragraph(f'<b>{number}</b>', self.styles['CustomKPIValue'])
        content = [
            Paragraph(f'<b>{what}</b>', self.styles['CustomInsightWhat']),
            Paragraph(f'→ {why}', self.styles['CustomInsightWhy']),
            Paragraph(f'✓ Action: {action}', self.styles['CustomInsightAction']),
        ]
        t = Table([[num_cell, content]], colWidths=[0.5*inch, 6.0*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
            ('BOX', (0,0), (-1,-1), 1, BORDER),
            ('LINEABOVE', (0,0), (-1,0), 3, BLUE),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        return t

    # ── Recommendations Table ──────────────────────────────────────────────────
    def _recommendations_table(self, recs: List[str]) -> Table:
        priority_labels = ['🔴 High', '🟡 Medium', '🟢 Low']
        impacts = ['Immediate revenue impact', 'Short-term improvement', 'Long-term optimization']
        rows = [[
            Paragraph('<b>Priority</b>', self.styles['CustomBodyText']),
            Paragraph('<b>Action</b>',   self.styles['CustomBodyText']),
            Paragraph('<b>Expected Impact</b>', self.styles['CustomBodyText']),
        ]]
        for i, rec in enumerate(recs[:5]):
            rows.append([
                Paragraph(priority_labels[min(i, 2)], self.styles['CustomBodyText']),
                Paragraph(rec, self.styles['CustomBodyText']),
                Paragraph(impacts[min(i, 2)], self.styles['CustomBodyText']),
            ])
        t = Table(rows, colWidths=[1.1*inch, 3.8*inch, 1.6*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), NAVY),
            ('TEXTCOLOR', (0,0), (-1,0), WHITE),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9.5),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [BG_LIGHT, WHITE]),
            ('GRID', (0,0), (-1,-1), 0.4, BORDER),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,-1), 7),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        return t

    # ── Executive Summary ──────────────────────────────────────────────────────
    def create_executive_summary(self, data: List[Dict]) -> List:
        els = []
        self.toc.add_entry("Executive Summary", 1)
        els.append(Paragraph("Executive Summary", self.styles['CustomChapterTitle']))
        els.append(HRFlowable(width="100%", thickness=2, color=BLUE))
        els.append(Spacer(1, 0.12*inch))

        # Objective block
        self.toc.add_entry("Objective", 2)
        els.append(Paragraph("Objective", self.styles['CustomSectionTitle']))
        els.append(Paragraph(
            "This report provides an automated, AI-powered business intelligence analysis "
            "of the provided dataset. It covers distribution analysis, category performance, "
            "trend identification, relationship analysis, and anomaly detection — each with "
            "specific actionable recommendations.",
            self.styles['CustomBodyText']
        ))
        els.append(Spacer(1, 0.1*inch))

        # Key Insights TL;DR
        findings = []
        all_recs  = []
        for d in data:
            c = d.get('content', {})
            for s in self._parse_sections(c):
                if any(k in s['heading'] for k in ('Metric', 'Overview', 'Summary', 'Key')):
                    findings.append(s['content'][:180])
                if any(k in s['heading'] for k in ('Recommendation', 'Action')):
                    # split by numbered items or dots
                    parts = re.split(r'\d+\.\s+|\.\s+', s['content'])
                    for p in parts:
                        p = p.strip()
                        if len(p) > 20:
                            all_recs.append(p[:140])

        if findings:
            self.toc.add_entry("Key Findings", 2)
            els.append(Paragraph("Key Findings", self.styles['CustomSectionTitle']))
            box = self._callout("🔑", "Top Insights", findings[:4])
            els.append(box)
            els.append(Spacer(1, 0.1*inch))

        if all_recs:
            self.toc.add_entry("Top Recommendations", 2)
            els.append(Paragraph("Top Recommendations", self.styles['CustomSectionTitle']))
            for rec in all_recs[:3]:
                els.append(Paragraph(f'✓  {rec}', self.styles['CustomActionable']))

        els.append(PageBreak())
        self.toc.increment_page()
        return els

    # ── Analysis Chapter ───────────────────────────────────────────────────────
    def create_analysis_chapters(self, data: List[Dict]) -> List:
        els = []
        for i, d in enumerate(data, 1):
            try:
                content = d.get('content', {})
                question = content.get('question', f'Analysis {i}')
                title = self._fmt_title(question)
                ch_title = f"{i}. {title}"
                stem = Path(d.get('graph_path', '')).stem

                self.toc.add_entry(ch_title, 1)
                els.append(Paragraph(ch_title, self.styles['CustomChapterTitle']))
                els.append(HRFlowable(width="100%", thickness=2, color=BLUE))
                els.append(Spacer(1, 0.12*inch))

                # ── 1. GRAPH ───────────────────────────────────────────────────
                gp = d.get('graph_path')
                if gp and self._valid_graph(gp):
                    try:
                        img = Image(gp,
                                    width=PDF_CONSTANTS['MAX_IMAGE_WIDTH'],
                                    height=0.714*PDF_CONSTANTS['MAX_IMAGE_WIDTH'])
                        img_wrap = Table([[img]], colWidths=[PDF_CONSTANTS['MAX_IMAGE_WIDTH']])
                        img_wrap.setStyle(TableStyle([
                            ('ALIGN',  (0,0), (-1,-1), 'CENTER'),
                            ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
                            ('BOX',    (0,0), (-1,-1), 1, BORDER),
                            ('TOPPADDING',    (0,0), (-1,-1), 8),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                        ]))
                        els.append(img_wrap)
                        els.append(Paragraph(f"Figure {i}: {title}", self.styles['CustomCaption']))
                    except Exception as e:
                        logger.error(f"Image error ch{i}: {e}")

                # ── 2. KPI CARDS ───────────────────────────────────────────────
                stats = self._load_stats(stem)
                kpis = self._kpi_cards(stats)
                if kpis:
                    self.toc.add_entry("Key Metrics", 2)
                    els.append(Paragraph("Key Metrics", self.styles['CustomSectionTitle']))
                    els.append(kpis)
                    els.append(Spacer(1, 0.12*inch))

                # ── 3. SECTIONS from description ───────────────────────────────
                sections = self._parse_sections(content)
                insights_block = []
                rec_lines = []

                for sec in sections:
                    h = sec['heading']
                    b = sec['content']

                    if any(k in h for k in ('Recommendation', 'Action', 'Next Step')):
                        # collect for recommendations table
                        parts = re.split(r'\d+\.\s+', b)
                        for p in parts:
                            p = p.strip().rstrip('.')
                            if len(p) > 15:
                                rec_lines.append(p[:160])

                    elif any(k in h for k in ('Impact', 'Business Impact')):
                        self.toc.add_entry(h, 2)
                        els.append(Paragraph(h, self.styles['CustomSectionTitle']))
                        impact_box = Table(
                            [[Paragraph(f'💰  {b}', self.styles['CustomImpact'])]],
                            colWidths=[6.3*inch]
                        )
                        impact_box.setStyle(TableStyle([
                            ('BACKGROUND', (0,0), (-1,-1), AMBER_BG),
                            ('BOX', (0,0), (-1,-1), 1.5, AMBER),
                            ('TOPPADDING', (0,0), (-1,-1), 10),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                            ('LEFTPADDING', (0,0), (-1,-1), 14),
                        ]))
                        els.append(impact_box)
                        els.append(Spacer(1, 0.08*inch))

                    elif any(k in h for k in ('Insight', 'Finding', 'Pattern', 'Key')):
                        insights_block.append((h, b))

                    else:
                        self.toc.add_entry(h, 2)
                        els.append(Paragraph(h, self.styles['CustomSectionTitle']))
                        els.append(Paragraph(b, self.styles['CustomBodyText']))
                        els.append(Spacer(1, 0.08*inch))

                # ── 4. INSIGHT CARDS (What / Why / Action) ────────────────────
                if insights_block:
                    self.toc.add_entry("Key Insights", 2)
                    els.append(Paragraph("Key Insights", self.styles['CustomSectionTitle']))
                    for idx, (h, b) in enumerate(insights_block[:3], 1):
                        sentences = [s.strip() for s in re.split(r'\.\s+', b) if len(s.strip()) > 10]
                        what   = sentences[0] if sentences else b[:80]
                        why    = sentences[1] if len(sentences) > 1 else "See chart above for details"
                        action = sentences[2] if len(sentences) > 2 else "Take targeted action based on this finding"
                        els.append(self._insight_card(idx, what, why, action))
                        els.append(Spacer(1, 0.06*inch))

                # ── 5. RECOMMENDATIONS TABLE ───────────────────────────────────
                if rec_lines:
                    self.toc.add_entry("Recommendations", 2)
                    els.append(Paragraph("Actionable Recommendations", self.styles['CustomSectionTitle']))
                    els.append(self._recommendations_table(rec_lines))
                    els.append(Spacer(1, 0.1*inch))

                # ── 6. STATS TABLE ─────────────────────────────────────────────
                if stats:
                    self.toc.add_entry("Statistical Summary", 2)
                    els.append(Paragraph("Statistical Summary", self.styles['CustomSectionTitle']))
                    st = self._stats_table(stats)
                    if st:
                        els.append(st)
                    els.append(Spacer(1, 0.08*inch))

                els.append(PageBreak())
                self.toc.increment_page()

            except Exception as e:
                logger.error(f"Chapter {i} error: {e}")

        return els

    # ── Conclusions ────────────────────────────────────────────────────────────
    def create_conclusions(self, data: List[Dict]) -> List:
        els = []
        self.toc.add_entry("Next Steps & Limitations", 1)
        els.append(Paragraph("Next Steps & Limitations", self.styles['CustomChapterTitle']))
        els.append(HRFlowable(width="100%", thickness=2, color=BLUE))
        els.append(Spacer(1, 0.12*inch))

        els.append(Paragraph(
            "This analysis was generated automatically using AI models. All insights are "
            "based on the provided data and should be reviewed by domain experts before "
            "making strategic business decisions.",
            self.styles['CustomBodyText']
        ))
        els.append(Spacer(1, 0.1*inch))

        # Next Steps table
        next_steps = [
            ("1", "Validate", "Confirm key findings with your team and domain experts"),
            ("2", "Investigate", "Dig deeper into any outliers or anomalies identified"),
            ("3", "Monitor", "Set up regular reporting to track key metrics over time"),
            ("4", "Act",      "Implement the top 3 recommendations with highest ROI"),
            ("5", "Iterate",  "Re-run this analysis monthly to track progress"),
        ]
        rows = [[
            Paragraph('<b>#</b>', self.styles['CustomBodyText']),
            Paragraph('<b>Action</b>', self.styles['CustomBodyText']),
            Paragraph('<b>Description</b>', self.styles['CustomBodyText']),
        ]]
        for num, action, desc in next_steps:
            rows.append([
                Paragraph(f'<b>{num}</b>', self.styles['CustomBodyText']),
                Paragraph(f'<b>{action}</b>', self.styles['CustomActionable']),
                Paragraph(desc, self.styles['CustomBodyText']),
            ])
        t = Table(rows, colWidths=[0.4*inch, 1.2*inch, 4.9*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), NAVY),
            ('TEXTCOLOR', (0,0), (-1,0), WHITE),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9.5),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [GREEN_BG, WHITE]),
            ('GRID', (0,0), (-1,-1), 0.4, BORDER),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,-1), 7),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        els.append(t)
        els.append(PageBreak())
        return els

    # ── Load Data ──────────────────────────────────────────────────────────────
    def _load_analysis_data(self) -> List[Dict]:
        result = []
        for jf in sorted(path_config.DESCRIPTION_DIR.glob('*.json')):
            try:
                with open(jf) as f:
                    c = json.load(f)
                gp = path_config.GRAPHS_DIR / f"{jf.stem}.png"
                if not self._valid_graph(str(gp)):
                    logger.warning(f"Missing graph: {jf.name}")
                    continue
                result.append({"content": c, "graph_path": str(gp)})
            except Exception as e:
                logger.error(f"Load error {jf}: {e}")
        try:
            result.sort(key=lambda x: int(x["content"].get("question","").split()[0]))
        except Exception:
            pass
        return result

    # ── Generate ───────────────────────────────────────────────────────────────
    @log_execution
    def generate_pdf(self, report_title: str = "Business Analysis Report") -> str:
        try:
            self.report_title = report_title
            self.toc = DynamicTOC()
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out = path_config.OUTPUT_DIR / f"analysis_report_{ts}.pdf"

            doc = SimpleDocTemplate(
                str(out), pagesize=A4,
                rightMargin=PDF_CONSTANTS['MARGIN'],
                leftMargin=PDF_CONSTANTS['MARGIN'],
                topMargin=PDF_CONSTANTS['MARGIN'] + 22,
                bottomMargin=PDF_CONSTANTS['MARGIN'] + 22
            )

            content = []
            content.extend(self.create_cover_page())

            data = self._load_analysis_data()
            if not data:
                raise PDFGenerationError("No valid analysis data found")

            toc_start = len(content)
            content.append(PageBreak())

            content.extend(self.create_executive_summary(data))
            content.extend(self.create_analysis_chapters(data))
            content.extend(self.create_conclusions(data))

            n = len(self.toc.entries)
            toc_pages = max(1, (n * 18 + 80) // 680 + 1)
            self.toc.set_toc_pages(toc_pages)
            content[toc_start:toc_start+1] = self.toc.create_toc_content(self.styles)

            doc.build(content,
                      onFirstPage=self.create_header_footer,
                      onLaterPages=self.create_header_footer)

            logger.info(f"Generated PDF: {out}")
            return str(out)

        except Exception as e:
            logger.error(f"PDF failed: {e}")
            raise PDFGenerationError(str(e))


@log_execution
def generate_pdf(report_title: str = "Business Analysis Report") -> str:
    try:
        return PDFGenerator().generate_pdf(report_title=report_title)
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise PDFGenerationError(str(e))