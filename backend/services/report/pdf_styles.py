from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os, urllib.request, tempfile

from core.logging.logger import get_logger
from domain.exceptions.custom import PDFGenerationError

logger = get_logger(__name__)

# ── Google Fonts download helper ───────────────────────────────────────────────
_FONT_URLS = {
    "Poppins-Regular":    "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf",
    "Poppins-Bold":       "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf",
    "Poppins-SemiBold":   "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-SemiBold.ttf",
    "Inter-Regular":      "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf",
    "Inter-Bold":         "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf",
}

_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")


def _ensure_font_dir():
    os.makedirs(_FONT_DIR, exist_ok=True)


def _font_path(name: str) -> str:
    return os.path.join(_FONT_DIR, f"{name}.ttf")


def _try_download(name: str, url: str) -> bool:
    path = _font_path(name)
    if os.path.exists(path):
        return True
    try:
        logger.info(f"Downloading font {name}...")
        urllib.request.urlretrieve(url, path)
        return True
    except Exception as e:
        logger.warning(f"Could not download {name}: {e}")
        return False


def _register_fonts():
    """
    Try to register Poppins + Inter.
    Falls back to Helvetica gracefully.
    """
    _ensure_font_dir()

    # --- Poppins ---
    heading_regular = "Poppins-Regular"
    heading_bold    = "Poppins-Bold"
    heading_semi    = "Poppins-SemiBold"

    poppins_ok = False
    for name in [heading_regular, heading_bold, heading_semi]:
        url = _FONT_URLS.get(name, "")
        if _try_download(name, url):
            try:
                pdfmetrics.registerFont(TTFont(name, _font_path(name)))
                poppins_ok = True
            except Exception as e:
                logger.warning(f"Could not register {name}: {e}")

    # --- Inter (variable font — use for both weights) ---
    inter_ok = False
    inter_name = "Inter-Regular"
    inter_bold  = "Inter-Bold"
    if _try_download("Inter-Regular", _FONT_URLS["Inter-Regular"]):
        try:
            pdfmetrics.registerFont(TTFont(inter_name, _font_path("Inter-Regular")))
            pdfmetrics.registerFont(TTFont(inter_bold,  _font_path("Inter-Regular")))
            inter_ok = True
        except Exception as e:
            logger.warning(f"Could not register Inter: {e}")

    H_REG  = "Poppins-Regular"  if poppins_ok else "Helvetica"
    H_BOLD = "Poppins-Bold"     if poppins_ok else "Helvetica-Bold"
    H_SEMI = "Poppins-SemiBold" if poppins_ok else "Helvetica-Bold"
    B_REG  = "Inter-Regular"    if inter_ok   else "Helvetica"
    B_BOLD = "Inter-Bold"       if inter_ok   else "Helvetica-Bold"

    logger.info(f"Fonts → Heading: {H_BOLD}, Body: {B_REG}")
    return H_REG, H_BOLD, H_SEMI, B_REG, B_BOLD


def get_custom_styles():
    try:
        H_REG, H_BOLD, H_SEMI, B_REG, B_BOLD = _register_fonts()

        styles = getSampleStyleSheet()

        # ── Palette ────────────────────────────────────────────────────────────
        NAVY        = HexColor('#0A1628')
        BLUE        = HexColor('#1D4ED8')
        BLUE_LIGHT  = HexColor('#3B82F6')
        ACCENT_BG   = HexColor('#EFF6FF')
        GREEN       = HexColor('#16A34A')
        GREEN_BG    = HexColor('#F0FDF4')
        AMBER       = HexColor('#D97706')
        AMBER_BG    = HexColor('#FFFBEB')
        RED         = HexColor('#DC2626')
        TEXT        = HexColor('#111827')
        MUTED       = HexColor('#6B7280')
        BORDER      = HexColor('#E5E7EB')
        BG_LIGHT    = HexColor('#F9FAFB')
        WHITE       = HexColor('#FFFFFF')

        # ── Headings (Poppins) ─────────────────────────────────────────────────
        styles.add(ParagraphStyle(
            name='CustomMainTitle',
            fontName=H_BOLD, fontSize=34,
            textColor=WHITE, alignment=TA_CENTER,
            leading=42, spaceAfter=16, spaceBefore=16
        ))
        styles.add(ParagraphStyle(
            name='CustomChapterTitle',
            fontName=H_BOLD, fontSize=20,
            textColor=NAVY, leading=28,
            spaceBefore=18, spaceAfter=8, keepWithNext=True
        ))
        styles.add(ParagraphStyle(
            name='CustomSectionTitle',
            fontName=H_SEMI, fontSize=13,
            textColor=BLUE, leading=20,
            spaceBefore=14, spaceAfter=5, keepWithNext=True
        ))
        styles.add(ParagraphStyle(
            name='CustomSubsectionTitle',
            fontName=H_SEMI, fontSize=11,
            textColor=BLUE_LIGHT, leading=16,
            spaceBefore=10, spaceAfter=4, keepWithNext=True
        ))
        styles.add(ParagraphStyle(
            name='CustomKPILabel',
            fontName=H_SEMI, fontSize=9,
            textColor=MUTED, alignment=TA_CENTER, leading=12
        ))
        styles.add(ParagraphStyle(
            name='CustomKPIValue',
            fontName=H_BOLD, fontSize=24,
            textColor=BLUE, alignment=TA_CENTER, leading=30
        ))
        styles.add(ParagraphStyle(
            name='CustomKeyMetric',
            fontName=H_BOLD, fontSize=22,
            textColor=BLUE, alignment=TA_CENTER, leading=28
        ))
        styles.add(ParagraphStyle(
            name='CustomMetricLabel',
            fontName=B_REG, fontSize=9,
            textColor=MUTED, alignment=TA_CENTER, leading=12
        ))

        # ── Body (Inter) ───────────────────────────────────────────────────────
        styles.add(ParagraphStyle(
            name='CustomBodyText',
            fontName=B_REG, fontSize=10.5,
            textColor=TEXT, alignment=TA_JUSTIFY,
            leading=17, spaceBefore=4, spaceAfter=4
        ))
        styles.add(ParagraphStyle(
            name='CustomBullet',
            fontName=B_REG, fontSize=10.5,
            textColor=TEXT, leading=17,
            spaceBefore=3, spaceAfter=3,
            leftIndent=14, bulletIndent=4
        ))
        styles.add(ParagraphStyle(
            name='CustomActionable',
            fontName=B_BOLD, fontSize=10.5,
            textColor=GREEN, leading=17,
            spaceBefore=3, spaceAfter=3, leftIndent=14
        ))
        styles.add(ParagraphStyle(
            name='CustomImpact',
            fontName=B_REG, fontSize=10,
            textColor=AMBER, leading=16,
            spaceBefore=4, spaceAfter=4, leftIndent=8
        ))
        styles.add(ParagraphStyle(
            name='CustomCallout',
            fontName=H_SEMI, fontSize=11,
            textColor=NAVY, leading=17,
            spaceBefore=4, spaceAfter=4, leftIndent=12
        ))
        styles.add(ParagraphStyle(
            name='CustomInsightWhat',
            fontName=B_BOLD, fontSize=10.5,
            textColor=NAVY, leading=16,
            spaceBefore=6, spaceAfter=2, leftIndent=8
        ))
        styles.add(ParagraphStyle(
            name='CustomInsightWhy',
            fontName=B_REG, fontSize=10,
            textColor=MUTED, leading=15,
            spaceBefore=1, spaceAfter=1, leftIndent=20
        ))
        styles.add(ParagraphStyle(
            name='CustomInsightAction',
            fontName=B_BOLD, fontSize=10,
            textColor=GREEN, leading=15,
            spaceBefore=1, spaceAfter=6, leftIndent=20
        ))
        styles.add(ParagraphStyle(
            name='CustomCaption',
            fontName=B_REG, fontSize=9,
            textColor=MUTED, alignment=TA_CENTER,
            leading=13, spaceBefore=4, spaceAfter=14
        ))
        styles.add(ParagraphStyle(
            name='CustomHeader',
            fontName=B_REG, fontSize=9,
            textColor=MUTED, alignment=TA_CENTER, leading=11
        ))

        # ── TOC ────────────────────────────────────────────────────────────────
        styles.add(ParagraphStyle(
            name='CustomTOCEntry',
            fontName=B_REG, fontSize=11,
            textColor=TEXT, leading=19, spaceAfter=3
        ))
        styles.add(ParagraphStyle(
            name='CustomTOCEntry2',
            fontName=B_REG, fontSize=10,
            textColor=MUTED, leading=16, spaceAfter=2, leftIndent=18
        ))
        styles.add(ParagraphStyle(
            name='CustomTOCEntry3',
            fontName=B_REG, fontSize=9.5,
            textColor=MUTED, leading=14, spaceAfter=1, leftIndent=36
        ))

        # ── Legacy aliases ─────────────────────────────────────────────────────
        for alias, base in [
            ('CustomDataPoint', 'CustomBullet'),
            ('CustomCalculation', 'CustomBodyText'),
            ('CustomExecutiveSummary', 'CustomBodyText'),
            ('CustomKeyFinding', 'CustomBullet'),
            ('CustomConclusion', 'CustomActionable'),
            ('CustomNextSteps', 'CustomActionable'),
        ]:
            styles.add(ParagraphStyle(name=alias, parent=styles[base]))

        logger.info("Custom styles generated successfully (Poppins + Inter)")
        return styles

    except Exception as e:
        logger.error(f"Failed to generate styles: {e}")
        raise PDFGenerationError(f"Style generation failed: {e}")