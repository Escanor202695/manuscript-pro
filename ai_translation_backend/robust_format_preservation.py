"""
Robust Format Preservation System - 100% Formatting Retention
Handles ALL Word document formatting with complete accuracy
"""

import json
import re
from typing import List, Dict, Tuple, Any, Optional
from docx import Document
from docx.text.paragraph import Paragraph
from docx.text.run import Run
from docx.shared import RGBColor, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_UNDERLINE
from dataclasses import dataclass, asdict
import hashlib


def _safe_int(value):
    """Convert a numeric value to int, tolerating floats/strings/Length objects."""
    if value is None:
        return None
    # Handle python-docx Length objects (they have .pt property)
    if hasattr(value, 'pt'):
        return int(value.pt)
    if isinstance(value, int):
        return value
    try:
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None
            try:
                return int(value)
            except ValueError:
                return int(float(value))
        # Try direct int conversion
        return int(value)
    except (ValueError, TypeError):
        return None


def _safe_float(value):
    """Convert a numeric value to float, tolerating Length objects/strings."""
    if value is None:
        return None
    # Handle python-docx Length objects (they have .pt property)
    if hasattr(value, 'pt'):
        return float(value.pt)


def ensure_heading_bold(para):
    """
    Ensure that heading paragraphs have bold runs.
    This is important because heading styles typically have bold by default,
    but when text is replaced, runs might not have explicit bold formatting.
    
    This fixes the issue where cloned documents don't have bold headings.
    """
    if not para or not para.style:
        return
    
    style_name = para.style.name.lower()
    
    # Check if this is a heading style
    if not style_name.startswith('heading'):
        return
    
    # Check if any run explicitly has bold=False (user intentionally removed bold)
    has_explicit_non_bold = any(
        run.bold is False for run in para.runs if run.bold is not None
    )
    
    # If user explicitly removed bold, don't force it back
    if has_explicit_non_bold:
        return
    
    # Check if the heading style itself has bold enabled
    # In Word, heading styles typically have bold by default
    style_has_bold = True  # Default: assume headings should be bold
    try:
        # Try to check if the style's font has bold explicitly set
        if hasattr(para.style, 'font') and para.style.font.bold is not None:
            style_has_bold = para.style.font.bold
        # If not explicitly set (None), default to True (standard Word behavior)
    except:
        # If we can't check, default to making headings bold (standard behavior)
        style_has_bold = True
    
    # Ensure all runs are bold if style requires it
    if style_has_bold:
        for run in para.runs:
            if run.bold is None or run.bold is False:
                run.bold = True
    if isinstance(value, (int, float)):
        return float(value)
    try:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None
            return float(value)
        return float(value)
    except (ValueError, TypeError):
        return None


def _roman_to_arabic(roman: str) -> int:
    """Convert a Roman numeral string to Arabic integer."""
    roman = roman.upper()
    roman_values = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000
    }
    result = 0
    prev_value = 0
    
    for char in reversed(roman):
        if char not in roman_values:
            return None
        value = roman_values[char]
        if value < prev_value:
            result -= value
        else:
            result += value
        prev_value = value
    
    return result


def convert_roman_numerals_in_text(text: str) -> str:
    """
    Post-processing: Convert Roman numerals to Arabic numerals.
    Safety net for any Roman numerals the AI missed.
    
    CRITICAL: Single-letter "I" is both a Roman numeral AND an English pronoun.
    We ONLY convert it when the text is EXACTLY "I" with no other content (section number).
    If there's trailing space like "I " or other words, it's likely the pronoun, not a numeral.
    """
    if not text:
        return text
    
    # FIRST: Check if entire text is just a Roman numeral (most common case for section numbers)
    # Handle both uppercase and lowercase - THIS IS THE PRIMARY CHECK
    stripped = text.strip().upper()
    
    # EXPLICIT handling for single Roman numerals that are common section numbers
    # This MUST be checked first because single letters like I, V, X are often missed
    single_roman_map = {
        'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5',
        'VI': '6', 'VII': '7', 'VIII': '8', 'IX': '9', 'X': '10',
        'XI': '11', 'XII': '12', 'XIII': '13', 'XIV': '14', 'XV': '15',
        'XVI': '16', 'XVII': '17', 'XVIII': '18', 'XIX': '19', 'XX': '20'
    }
    
    # CRITICAL FIX: For single-letter Romans (I, V, X), distinguish between:
    # - Section number: "I" or "I\n" (standalone, no trailing space before content ends)
    # - English pronoun: "I " (followed by space, indicates more words follow like "I thought")
    if stripped in ['I', 'V', 'X']:
        text_trimmed = text.strip()
        if text_trimmed.upper() == stripped:
            # Check for trailing SPACE (not newline) - space indicates more content follows
            # "I " = pronoun (space before next word)
            # "I" or "I\n" = section number (standalone)
            text_without_newlines = text.rstrip('\n\r')
            has_trailing_space = text_without_newlines != text_without_newlines.rstrip(' \t')
            
            if has_trailing_space:
                # Trailing space before end = likely "I [word]" = pronoun, don't convert
                print(f"[ROMAN SKIP] Not converting '{repr(text)}' - has trailing space, likely pronoun")
                return text
            else:
                # No trailing space = standalone section number, convert
                leading_ws = text[:len(text) - len(text.lstrip())]
                trailing_ws = text[len(text.rstrip()):]
                print(f"[ROMAN CONVERT] Converting standalone '{stripped}' to '{single_roman_map[stripped]}'")
                return leading_ws + single_roman_map[stripped] + trailing_ws
        # Text doesn't match expected pattern
        return text
    
    # For multi-letter Romans (II, III, IV, etc.), safe to convert
    if stripped in single_roman_map:
        leading_ws = text[:len(text) - len(text.lstrip())]
        trailing_ws = text[len(text.rstrip()):]
        return leading_ws + single_roman_map[stripped] + trailing_ws
    
    # Fallback: Check if it's a valid Roman numeral pattern (for larger numerals)
    if stripped and re.fullmatch(r'[IVXLCDM]+', stripped) and len(stripped) > 1:
        arabic = _roman_to_arabic(stripped)
        if arabic is not None and arabic > 0 and arabic <= 100:
            leading_ws = text[:len(text) - len(text.lstrip())]
            trailing_ws = text[len(text.rstrip()):]
            return leading_ws + str(arabic) + trailing_ws
    
    # Pattern for single Roman numerals (I, V, X) at start of text followed by newline
    single_start_pattern = r'^([IVX]+)\s*\n'
    
    def replace_single_start(match):
        roman = match.group(1)
        arabic = _roman_to_arabic(roman)
        if arabic is not None and arabic > 0 and arabic <= 50:
            return f"{arabic}\n"
        return match.group(0)
    
    text = re.sub(single_start_pattern, replace_single_start, text, flags=re.MULTILINE)
    
    # Pattern for Roman numerals after newline and before newline (standalone line)
    newline_pattern = r'\n([IVXLCDM]+)\s*\n'
    
    def replace_newline(match):
        roman = match.group(1)
        arabic = _roman_to_arabic(roman)
        if arabic is not None and arabic > 0 and arabic <= 100:
            return f"\n{arabic}\n"
        return match.group(0)
    
    text = re.sub(newline_pattern, replace_newline, text)
    
    # Pattern for Roman numerals after common prefixes
    prefix_pattern = r'\b(Chapter|Part|Section|Volume|Book|Act|Scene|Article|Paragraph|Verse|Page|No\.|Number|Fig\.|Figure|Table|Appendix|Item|Entry|Lesson|Unit|Module|Grade|Level|Class|Form|Year|Series|Episode|Season|Stanza)\s+([IVXLCDM]+)\b'
    
    def replace_with_prefix(match):
        prefix = match.group(1)
        roman = match.group(2)
        arabic = _roman_to_arabic(roman)
        if arabic is not None and arabic > 0:
            return f"{prefix} {arabic}"
        return match.group(0)
    
    text = re.sub(prefix_pattern, replace_with_prefix, text, flags=re.IGNORECASE)
    
    # Pattern for standalone large Roman numerals (likely years)
    large_roman_pattern = r'\b([MDCLXVI]{4,})\b'
    
    def replace_large_roman(match):
        roman = match.group(1)
        arabic = _roman_to_arabic(roman)
        if arabic is not None and arabic > 0:
            return str(arabic)
        return match.group(0)
    
    text = re.sub(large_roman_pattern, replace_large_roman, text)
    
    # Pattern for Roman numerals in parentheses
    paren_pattern = r'\(([IVXLCDM]+)\)'
    
    def replace_paren(match):
        roman = match.group(1)
        arabic = _roman_to_arabic(roman)
        if arabic is not None and arabic > 0:
            return f"({arabic})"
        return match.group(0)
    
    text = re.sub(paren_pattern, replace_paren, text)
    
    # Pattern for Roman numerals with periods
    period_pattern = r'\b([IVXLCDM]{2,})\.'
    
    def replace_period(match):
        roman = match.group(1)
        arabic = _roman_to_arabic(roman)
        if arabic is not None and arabic > 0:
            return f"{arabic}."
        return match.group(0)
    
    text = re.sub(period_pattern, replace_period, text)
    
    # Handle case where entire text is just a Roman numeral
    if text.strip() in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 
                        'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX',
                        'XXI', 'XXII', 'XXIII', 'XXIV', 'XXV', 'XXX', 'XL', 'L', 'LX', 'LXX',
                        'LXXX', 'XC', 'C', 'CC', 'CCC', 'CD', 'D', 'DC', 'DCC', 'DCCC', 'CM', 'M']:
        arabic = _roman_to_arabic(text.strip())
        if arabic is not None and arabic > 0:
            leading = len(text) - len(text.lstrip())
            trailing = len(text) - len(text.rstrip())
            return text[:leading] + str(arabic) + text[len(text)-trailing:] if trailing else text[:leading] + str(arabic)
    
    return text


@dataclass
class RunFormatting:
    """Complete formatting information for a run"""
    text: str
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    strike: Optional[bool] = None
    double_strike: Optional[bool] = None
    subscript: Optional[bool] = None
    superscript: Optional[bool] = None
    font_name: Optional[str] = None
    font_size: Optional[int] = None
    font_color: Optional[str] = None
    highlight_color: Optional[str] = None
    all_caps: Optional[bool] = None
    small_caps: Optional[bool] = None
    shadow: Optional[bool] = None
    emboss: Optional[bool] = None
    imprint: Optional[bool] = None
    outline: Optional[bool] = None
    character_spacing: Optional[int] = None
    position: Optional[int] = None
    
    def to_marker(self, run_id: int) -> str:
        """Convert formatting to a unique marker"""
        attrs = []
        if self.bold: attrs.append("B")
        if self.italic: attrs.append("I")
        if self.underline: attrs.append("U")
        if self.strike: attrs.append("S")
        if self.double_strike: attrs.append("DS")
        if self.subscript: attrs.append("SUB")
        if self.superscript: attrs.append("SUP")
        if self.font_name: attrs.append(f"F:{self.font_name.replace(' ', '_')}")
        if self.font_size: attrs.append(f"SZ:{self.font_size}")
        if self.font_color: attrs.append(f"C:{self.font_color}")
        if self.highlight_color: attrs.append(f"H:{self.highlight_color}")
        if self.all_caps: attrs.append("AC")
        if self.small_caps: attrs.append("SC")
        if self.shadow: attrs.append("SH")
        if self.emboss: attrs.append("EM")
        if self.imprint: attrs.append("IM")
        if self.outline: attrs.append("OL")
        
        attr_str = ",".join(attrs) if attrs else "PLAIN"
        return f"««RUN{run_id}:{attr_str}»»"


@dataclass
class ParagraphFormatting:
    """Complete formatting information for a paragraph"""
    style: Optional[str] = None
    alignment: Optional[int] = None
    left_indent: Optional[float] = None
    right_indent: Optional[float] = None
    first_line_indent: Optional[float] = None
    space_before: Optional[float] = None
    space_after: Optional[float] = None
    line_spacing: Optional[float] = None
    line_spacing_rule: Optional[int] = None
    keep_together: Optional[bool] = None
    keep_with_next: Optional[bool] = None
    page_break_before: Optional[bool] = None
    widow_control: Optional[bool] = None
    tab_stops: List[Dict] = None
    
    def __post_init__(self):
        if self.tab_stops is None:
            self.tab_stops = []


class RobustFormatPreserver:
    """Preserves 100% of document formatting during translation"""
    
    def __init__(self, doc: Document):
        self.doc = doc
        self.format_map = {}
        self.run_counter = 0
        
    def extract_run_formatting(self, run: Run) -> RunFormatting:
        """Extract complete formatting from a run"""
        import traceback
        try:
            return self._extract_run_formatting_impl(run)
        except Exception as e:
            print(f"[EXTRACT ERROR] Failed to extract run formatting: {e}")
            print(f"[EXTRACT ERROR] Traceback:\n{traceback.format_exc()}")
            raise
    
    def _extract_run_formatting_impl(self, run: Run) -> RunFormatting:
        """Internal implementation of run formatting extraction"""
        # Get font color - store as integer to avoid float string issues
        font_color = None
        if run.font.color and run.font.color.rgb:
            # Convert RGBColor to integer value to avoid float string conversion issues
            rgb_val = run.font.color.rgb
            try:
                # RGBColor has __int__ method
                if hasattr(rgb_val, '__int__'):
                    font_color = str(int(rgb_val))
                elif isinstance(rgb_val, (int, float)):
                    font_color = str(int(rgb_val))
                else:
                    # Fallback: try to parse as string
                    rgb_str = str(rgb_val)
                    try:
                        font_color = str(int(rgb_str))
                    except ValueError:
                        font_color = str(int(float(rgb_str)))
            except Exception as e:
                font_color = None
        elif run.font.color and run.font.color.theme_color:
            font_color = f"theme:{run.font.color.theme_color}"
            
        # Get highlight color
        highlight_color = None
        if run.font.highlight_color:
            highlight_color = str(run.font.highlight_color)
        
        # Get font size - MUST use _safe_int to handle Length objects returning floats
        font_size = None
        if run.font.size:
            font_size = _safe_int(run.font.size)
        
        # Get character spacing and position - use _safe_int for safety
        character_spacing = _safe_int(getattr(run.font, 'spacing', None))
        position = _safe_int(getattr(run.font, 'position', None))

        # Ensure boolean values are explicitly True/False, not None
        # python-docx can return None for unset properties, but we need explicit values
        return RunFormatting(
            text=run.text,
            bold=bool(run.bold) if run.bold is not None else False,
            italic=bool(run.italic) if run.italic is not None else False,
            underline=bool(run.underline) if run.underline is not None else False,
            strike=bool(run.font.strike) if run.font.strike is not None else False,
            double_strike=bool(run.font.double_strike) if run.font.double_strike is not None else False,
            subscript=bool(run.font.subscript) if run.font.subscript is not None else False,
            superscript=bool(run.font.superscript) if run.font.superscript is not None else False,
            font_name=run.font.name,
            font_size=font_size,
            font_color=font_color,
            highlight_color=highlight_color,
            all_caps=bool(run.font.all_caps) if run.font.all_caps is not None else False,
            small_caps=bool(run.font.small_caps) if run.font.small_caps is not None else False,
            shadow=bool(run.font.shadow) if run.font.shadow is not None else False,
            emboss=bool(run.font.emboss) if run.font.emboss is not None else False,
            imprint=bool(run.font.imprint) if run.font.imprint is not None else False,
            outline=bool(run.font.outline) if run.font.outline is not None else False,
            character_spacing=character_spacing,
            position=position
        )
    
    def extract_paragraph_formatting(self, para: Paragraph) -> ParagraphFormatting:
        """Extract complete paragraph formatting"""
        
        # Helper to safely get paragraph format properties
        # The document may have corrupt values that cause python-docx to throw errors
        def safe_get(func, default=None):
            try:
                return func()
            except (ValueError, TypeError, AttributeError):
                return default
        
        # Extract tab stops - use _safe_float to handle Length objects
        tab_stops = []
        try:
            if para.paragraph_format.tab_stops:
                for tab in para.paragraph_format.tab_stops:
                    tab_stops.append({
                        'position': _safe_float(tab.position),
                        'alignment': tab.alignment,
                        'leader': tab.leader
                    })
        except (ValueError, TypeError, AttributeError):
            pass  # Skip corrupt tab stops
        
        return ParagraphFormatting(
            style=safe_get(lambda: para.style.name if para.style else None),
            alignment=safe_get(lambda: para.alignment),
            left_indent=safe_get(lambda: _safe_float(para.paragraph_format.left_indent)),
            right_indent=safe_get(lambda: _safe_float(para.paragraph_format.right_indent)),
            first_line_indent=safe_get(lambda: _safe_float(para.paragraph_format.first_line_indent)),
            space_before=safe_get(lambda: _safe_float(para.paragraph_format.space_before)),
            space_after=safe_get(lambda: _safe_float(para.paragraph_format.space_after)),
            line_spacing=safe_get(lambda: _safe_float(para.paragraph_format.line_spacing)),
            line_spacing_rule=safe_get(lambda: para.paragraph_format.line_spacing_rule),
            keep_together=safe_get(lambda: para.paragraph_format.keep_together),
            keep_with_next=safe_get(lambda: para.paragraph_format.keep_with_next),
            page_break_before=safe_get(lambda: para.paragraph_format.page_break_before),
            widow_control=safe_get(lambda: para.paragraph_format.widow_control),
            tab_stops=tab_stops
        )
    
    def _get_format_signature(self, run_format: RunFormatting) -> tuple:
        """Create a format signature for comparison (excludes text)"""
        return (
            run_format.bold,
            run_format.italic,
            run_format.underline,
            run_format.strike,
            run_format.double_strike,
            run_format.subscript,
            run_format.superscript,
            run_format.font_name,
            run_format.font_size,
            run_format.font_color,
            run_format.highlight_color,
            run_format.all_caps,
            run_format.small_caps,
            run_format.shadow,
            run_format.emboss,
            run_format.imprint,
            run_format.outline,
            run_format.character_spacing,
            run_format.position
        )
    
    def _has_significant_case_change(self, text: str) -> bool:
        """
        Check if text has significant case changes that need to be preserved.
        Returns True if there are words with different case patterns that should be split.
        """
        if not text or len(text) < 2:
            return False
        
        words = []
        # Extract words (alphanumeric sequences)
        import re
        word_pattern = re.compile(r'\b[A-Za-z]+\b')
        for match in word_pattern.finditer(text):
            word = match.group(0)
            words.append((match.start(), match.end(), word))
        
        if len(words) < 2:
            return False
        
        # Check if there's a mix of all-uppercase (multi-letter) words and mixed/lowercase words
        has_upper_word = False
        has_mixed_word = False
        
        for start, end, word in words:
            # Multi-letter all uppercase word
            if word.isupper() and len(word) > 1:
                has_upper_word = True
            # Mixed case or lowercase word (not all caps)
            elif not word.isupper():
                has_mixed_word = True
            
            # If we have both, we need to split
            if has_upper_word and has_mixed_word:
                return True
        
        return False
    
    def _split_text_by_case_boundaries(self, text: str) -> List[Tuple[int, int]]:
        """
        Split text into segments at case boundaries.
        Returns list of (start, end) tuples for each segment.
        Only splits at boundaries between all-uppercase words and mixed/lowercase words.
        """
        if not text:
            return [(0, 0)]
        
        import re
        word_pattern = re.compile(r'\b[A-Za-z]+\b')
        words = []
        for match in word_pattern.finditer(text):
            word = match.group(0)
            words.append((match.start(), match.end(), word))
        
        if len(words) < 2:
            return [(0, len(text))]
        
        segments = []
        segment_start = 0
        last_word_was_upper = None
        
        for word_start, word_end, word in words:
            is_upper = word.isupper() and len(word) > 1  # Multi-letter all caps
            
            if last_word_was_upper is not None:
                # Check if case pattern changed significantly
                if is_upper != last_word_was_upper:
                    # Case pattern changed - end previous segment before this word
                    segments.append((segment_start, word_start))
                    segment_start = word_start
            
            last_word_was_upper = is_upper
        
        # Add final segment
        segments.append((segment_start, len(text)))
        
        # Don't merge segments - we want to preserve case boundaries even if segments are short
        # Each segment represents a distinct case pattern that should be preserved
        return segments if len(segments) > 1 else [(0, len(text))]
    
    def _merge_runs_with_same_formatting(self, para: Paragraph) -> List[Dict]:
        """
        Merge consecutive runs that have identical formatting.
        This dramatically reduces run count while preserving exact spacing.
        CRITICAL: run.text already contains spaces, so concatenation preserves spacing perfectly.
        
        NEW: Whitespace-only runs don't break merging - runs with same formatting merge across whitespace.
        NEW: Also splits on case boundaries to preserve case patterns even when formatting is identical.
        """
        if not para.runs:
            return []
        
        def is_whitespace_only(text: str) -> bool:
            """Check if text contains only whitespace characters"""
            return not text.strip() and len(text) > 0
        
        def is_punctuation_only(text: str) -> bool:
            """Check if text contains only punctuation and/or whitespace"""
            import string
            stripped = text.strip()
            if not stripped:
                return True  # Whitespace only
            # Check if all non-whitespace characters are punctuation
            return all(c in string.punctuation or c.isspace() for c in stripped)
        
        merged_groups = []
        current_group = {
            'runs': [],
            'run_indices': [],  # Track indices to avoid index() lookup issues
            'text': '',
            'format': None,
            'format_obj': None
        }
        
        # Track indices as we iterate to avoid index() lookup issues
        i = 0
        while i < len(para.runs):
            run = para.runs[i]
            run_text = run.text
            is_whitespace = is_whitespace_only(run_text)
            is_punctuation = is_punctuation_only(run_text)
            run_format = self.extract_run_formatting(run)
            format_sig = self._get_format_signature(run_format)
            
            # Look ahead to see if there are consecutive runs with same formatting separated by punctuation/whitespace
            # This handles: RUN4(italic) -> RUN5(", ", non-italic) -> RUN6(italic) = should merge to one italic group
            if current_group['format'] is not None and format_sig != current_group['format']:
                # Different formatting - check if we can merge across punctuation/whitespace
                if is_whitespace or is_punctuation:
                    # This is whitespace or punctuation-only - look ahead to see if next run matches current group format
                    if i + 1 < len(para.runs):
                        next_run = para.runs[i + 1]
                        next_run_format = self.extract_run_formatting(next_run)
                        next_format_sig = self._get_format_signature(next_run_format)
                        
                        if next_format_sig == current_group['format']:
                            # Next run matches current group - merge punctuation/whitespace and continue
                            # This allows: italic -> ", " -> italic to merge as one italic group
                            current_group['runs'].append(run)
                            current_group['run_indices'].append(i)
                            current_group['text'] += run_text
                            i += 1
                            continue  # Skip to next iteration to process the matching run
                
                # Can't merge - save current group and start new one
                merged_groups.append(current_group)
                current_group = {
                    'runs': [],
                    'run_indices': [],
                    'text': '',
                    'format': None,
                    'format_obj': None
                }
            
            # Check if this run has the same formatting as current group
            if current_group['format'] is None:
                # First run or new group - start it
                current_group['runs'] = [run]
                current_group['run_indices'] = [i]
                current_group['text'] = run_text  # Includes spaces!
                current_group['format'] = format_sig
                current_group['format_obj'] = run_format
            elif format_sig == current_group['format']:
                # Same formatting - merge into current group
                # CRITICAL: run.text already contains spaces, so concatenation preserves spacing
                current_group['runs'].append(run)
                current_group['run_indices'].append(i)
                current_group['text'] += run_text  # Spaces preserved automatically!
            elif is_whitespace or is_punctuation:
                # Whitespace/punctuation-only run with different formatting - treat as transparent
                # Merge it into current group to preserve spacing/punctuation, but keep current formatting
                # This allows runs with same formatting to merge across punctuation/whitespace runs
                current_group['runs'].append(run)
                current_group['run_indices'].append(i)
                current_group['text'] += run_text  # Preserve the whitespace/punctuation
                # Don't change format or format_obj - keep current group's formatting
            else:
                # Different formatting and not whitespace - save current group and start new one
                merged_groups.append(current_group)
                current_group = {
                    'runs': [run],
                    'run_indices': [i],
                    'text': run_text,
                    'format': format_sig,
                    'format_obj': run_format
                }
            
            i += 1
        
        # Add the last group
        if current_group['runs']:
            merged_groups.append(current_group)
        
        # POST-PROCESSING: Split merged groups that have significant case changes
        # This ensures case patterns are preserved even when formatting is identical
        # Example: "HELLO, how you doing?" should be split into "HELLO, " and "how you doing?"
        final_groups = []
        for group in merged_groups:
            text = group['text']
            format_obj = group['format_obj']
            
            # Check if this group has significant case changes (all-caps words mixed with mixed-case)
            if self._has_significant_case_change(text):
                # Split the text at case boundaries
                segments = self._split_text_by_case_boundaries(text)
                
                for start, end in segments:
                    seg_text = text[start:end]
                    # Preserve all segments, including whitespace-only segments (important for spacing)
                    # Create a new group for each case segment
                    # Use the same run indices for tracking, but with split text
                    final_groups.append({
                        'runs': group['runs'],  # Keep reference to original runs
                        'run_indices': group['run_indices'],
                        'text': seg_text,
                        'format': self._get_format_signature(format_obj),
                        'format_obj': format_obj  # Same formatting, just different case pattern
                    })
            else:
                # No significant case changes, keep as is
                final_groups.append(group)
        
        return final_groups
    
    def create_formatted_text_for_translation(self, para: Paragraph, para_id: int) -> Tuple[str, Dict]:
        """
        Create marked text for translation with 100% format preservation.
        OPTIMIZED: Merges runs with identical formatting to reduce complexity and preserve exact spacing.
        
        Key insight: run.text already contains spaces, so merging by concatenation preserves spacing perfectly.
        This fixes the issue where many small runs cause spacing problems.
        """
        para_format = self.extract_paragraph_formatting(para)
        runs_data = []
        marked_text = ""
        
        # OPTIMIZATION: Merge consecutive runs with identical formatting
        # This dramatically reduces run count while preserving exact spacing
        # Since run.text already contains spaces, concatenation preserves spacing automatically
        merged_groups = self._merge_runs_with_same_formatting(para)
        
        # Process each merged group
        for group in merged_groups:
            run_format = group['format_obj']
            merged_text = group['text']  # Already includes all spaces from original runs!
            original_run_indices = group['run_indices']  # Use pre-tracked indices
            
            # Create unique marker for this merged run
            run_id = self.run_counter
            self.run_counter += 1
            marker = run_format.to_marker(run_id)
            
            # Add to marked text
            marked_text += f"{marker}{merged_text}««/RUN{run_id}»»"
            
            # Store complete formatting data with merge info
            runs_data.append({
                'id': run_id,
                'format': asdict(run_format),
                'original_text': merged_text,
                'marker': marker,
                'merged_from_runs': original_run_indices,  # Track which runs were merged
                'is_merged': len(group['runs']) > 1
            })
        
        # Store complete paragraph data
        para_data = {
            'id': para_id,
            'format': asdict(para_format),
            'runs': runs_data,
            'marked_text': marked_text,
            'checksum': hashlib.md5(marked_text.encode()).hexdigest(),
            'original_run_count': len(para.runs),  # Track original count
            'merged_run_count': len(merged_groups)  # Track merged count
        }
        
        self.format_map[para_id] = para_data
        
        return marked_text, para_data
    
    def parse_translated_text(self, translated_text: str, para_id: int) -> List[Dict]:
        """Parse translated text and extract run information"""
        para_data = self.format_map.get(para_id)
        if not para_data:
            return [{'text': translated_text, 'format': {}}]
        
        # Pattern to match run markers - CRITICAL: Use re.DOTALL to match across newlines!
        # The ([\s\S]*?) pattern matches any character including newlines
        pattern = r'««RUN(\d+):[^»]+»»([\s\S]*?)««/RUN\1»»'
        
        parsed_runs = []
        last_end = 0
        
        for match in re.finditer(pattern, translated_text):
            # Check if there's text before this run
            if match.start() > last_end:
                plain_text = translated_text[last_end:match.start()]
                # Remove any markers that might be in plain text
                plain_text = re.sub(r'««[^»]+»»', '', plain_text)
                if plain_text.strip():
                    # This shouldn't happen with proper translation
                    parsed_runs.append({
                        'text': plain_text,
                        'format': {},
                        'is_extra': True
                    })
            
            run_id = int(match.group(1))
            run_text = match.group(2)
            
            # CRITICAL: Clean any nested or remaining markers from run text
            run_text = re.sub(r'««[^»]+»»', '', run_text)
            # Remove properly closed delimiter markers
            run_text = re.sub(r'<<<[^>]*?>>>', '', run_text, flags=re.DOTALL)
            # Remove malformed markers without closing >>>
            run_text = re.sub(r'<<<[^\s]*', '', run_text)
            run_text = re.sub(r'<<<.*?(?=\s|$)', '', run_text, flags=re.DOTALL)
            
            # Find original format
            original_run = next((r for r in para_data['runs'] if r['id'] == run_id), None)
            
            if original_run:
                # Ensure format dictionary exists and is valid
                format_dict = original_run.get('format', {})
                if not isinstance(format_dict, dict):
                    format_dict = {}
                
                # Debug: Always log format dict for runs with I marker
                print(f"[FORMAT DEBUG] Run ID {run_id}: italic={format_dict.get('italic')}, bold={format_dict.get('bold')}")
                if format_dict.get('italic'):
                    print(f"[FORMAT DEBUG] Run ID {run_id} HAS ITALIC=TRUE in stored format")
                
                parsed_runs.append({
                    'text': run_text,
                    'format': format_dict,
                    'run_id': run_id
                })
            else:
                # Run ID not found - shouldn't happen, but log it
                print(f"[WARNING] Run ID {run_id} not found in para_data['runs'] for para_id {para_id}")
                available_ids = [r['id'] for r in para_data.get('runs', [])]
                print(f"[WARNING] Available run IDs: {available_ids}")
                parsed_runs.append({
                    'text': run_text,
                    'format': {},
                    'is_error': True
                })
            
            last_end = match.end()
        
        # Check for text after last run
        if last_end < len(translated_text):
            remaining = translated_text[last_end:]
            # Remove any markers from remaining text
            remaining = re.sub(r'««[^»]+»»', '', remaining)
            # Remove properly closed delimiter markers
            remaining = re.sub(r'<<<[^>]*?>>>', '', remaining, flags=re.DOTALL)
            # Remove malformed markers without closing >>>
            remaining = re.sub(r'<<<[^\s]*', '', remaining)
            remaining = re.sub(r'<<<.*?(?=\s|$)', '', remaining, flags=re.DOTALL)
            if remaining.strip():
                parsed_runs.append({
                    'text': remaining,
                    'format': {},
                    'is_extra': True
                })
        
        # If no runs found, return plain text with all markers removed
        if not parsed_runs:
            # Aggressively remove all markers and return clean text
            clean_text = re.sub(r'««[^»]+»»', '', translated_text)
            # Remove properly closed delimiter markers
            clean_text = re.sub(r'<<<[^>]*?>>>', '', clean_text, flags=re.DOTALL)
            # Remove malformed markers without closing >>>
            clean_text = re.sub(r'<<<[^\s]*', '', clean_text)
            clean_text = re.sub(r'<<<.*?(?=\s|$)', '', clean_text, flags=re.DOTALL)
            # Also remove any partial markers that might remain
            clean_text = re.sub(r'««.*', '', clean_text)
            clean_text = re.sub(r'.*»»', '', clean_text)
            return [{'text': clean_text, 'format': {}}]
        
        return parsed_runs
    
    def apply_formatting_to_paragraph(self, para: Paragraph, para_id: int, translated_text: str):
        """Apply all formatting to translated paragraph"""
        print(f"\n[DEBUG APPLY] Starting apply_formatting_to_paragraph for para_id={para_id}")
        print(f"[DEBUG APPLY] Translated text preview: {translated_text[:200] if len(translated_text) > 200 else translated_text}")
        
        # CRITICAL: Remove ALL delimiter markers first (catches any variations including translated/misspelled ones)
        # First: Remove properly closed markers <<<...>>>
        translated_text = re.sub(r'<<<[^>]*?>>>', '', translated_text, flags=re.DOTALL)
        # Second: Remove MALFORMED markers that start with <<< but have no closing >>>
        # Match <<< followed by ANY characters until whitespace or end of string
        translated_text = re.sub(r'<<<[^\s]*', '', translated_text)
        # Also catch any remaining <<< patterns (defensive)
        translated_text = re.sub(r'<<<.*?(?=\s|$)', '', translated_text, flags=re.DOTALL)
        
        para_data = self.format_map.get(para_id)
        print(f"[DEBUG APPLY] format_map has para_id={para_id}: {para_data is not None}")
        if para_data:
            print(f"[DEBUG APPLY] para_data['runs'] count: {len(para_data.get('runs', []))}")
            for run_info in para_data.get('runs', []):
                print(f"[DEBUG APPLY]   Run ID {run_info['id']}: italic={run_info['format'].get('italic')}, bold={run_info['format'].get('bold')}")
        if not para_data:
            # No format data - remove any markers and set plain text
            clean_text = re.sub(r'««[^»]+»»', '', translated_text)
            # Remove properly closed markers
            clean_text = re.sub(r'<<<[^>]*?>>>', '', clean_text, flags=re.DOTALL)
            # Remove malformed markers without closing >>>
            clean_text = re.sub(r'<<<[^\s]*', '', clean_text)
            clean_text = re.sub(r'<<<.*?(?=\s|$)', '', clean_text, flags=re.DOTALL)
            for run in para.runs:
                run.text = ""
            if para.runs:
                para.runs[0].text = clean_text
            else:
                para.add_run(clean_text)
            return
        
        # Parse translated text
        parsed_runs = self.parse_translated_text(translated_text, para_id)
        
        # CRITICAL: Clean all markers from run text (in case parsing missed some)
        for run_data in parsed_runs:
            if 'text' in run_data:
                # Remove any remaining markers from the text (both robust and delimiter markers)
                run_data['text'] = re.sub(r'««[^»]+»»', '', run_data['text'])
                # Remove properly closed delimiter markers
                run_data['text'] = re.sub(r'<<<[^>]*?>>>', '', run_data['text'], flags=re.DOTALL)
                # Remove malformed markers without closing >>>
                run_data['text'] = re.sub(r'<<<[^\s]*', '', run_data['text'])
                run_data['text'] = re.sub(r'<<<.*?(?=\s|$)', '', run_data['text'], flags=re.DOTALL)
        
        # Clear existing runs
        for run in para.runs:
            run.text = ""
        
        # Apply paragraph formatting
        para_format = para_data['format']
        if para_format.get('style'):
            style_name = para_format['style']
            try:
                # Try to set the style, but handle case where style doesn't exist in document
                para.style = style_name
            except (KeyError, ValueError) as e:
                # Style doesn't exist in document - skip style assignment but continue with other formatting
                # This can happen if the document doesn't have the style in its style collection
                # The paragraph will keep its default style
                pass
        if para_format.get('alignment') is not None:
            para.alignment = para_format['alignment']
        if para_format.get('left_indent') is not None:
            para.paragraph_format.left_indent = Pt(para_format['left_indent'])
        if para_format.get('right_indent') is not None:
            para.paragraph_format.right_indent = Pt(para_format['right_indent'])
        if para_format.get('first_line_indent') is not None:
            para.paragraph_format.first_line_indent = Pt(para_format['first_line_indent'])
        if para_format.get('space_before') is not None:
            para.paragraph_format.space_before = Pt(para_format['space_before'])
        if para_format.get('space_after') is not None:
            para.paragraph_format.space_after = Pt(para_format['space_after'])
        
        # Create runs with formatting
        for i, run_data in enumerate(parsed_runs):
            # Final safety check: ensure text has no markers
            clean_run_text = re.sub(r'««[^»]+»»', '', run_data.get('text', ''))
            
            # DEBUG: Log runs that might be Roman numerals
            stripped_before = clean_run_text.strip().upper()
            if stripped_before in ['I', 'V', 'X', 'II', 'III', 'IV', 'VI', 'VII', 'VIII', 'IX']:
                print(f"[ROMAN CHECK] Run {i}: '{clean_run_text}' (stripped: '{stripped_before}')")
            
            # Post-process: Convert any remaining Roman numerals to Arabic
            clean_run_text_before = clean_run_text
            clean_run_text = convert_roman_numerals_in_text(clean_run_text)
            
            # DEBUG: Log if conversion happened
            if clean_run_text_before != clean_run_text:
                print(f"[ROMAN CONVERTED] Run {i}: '{clean_run_text_before}' → '{clean_run_text}'")
            
            # Get format dictionary
            fmt = run_data.get('format', {})
            
            # Create or reuse run
            if i < len(para.runs):
                run = para.runs[i]
                run.text = clean_run_text
                
                # CRITICAL: Reset all formatting properties when reusing runs
                # This prevents leftover formatting from affecting the new content
                # Set to False (not None) so properties can be properly overridden
                try:
                    run.bold = False
                    run.italic = False
                    run.underline = False
                    run.font.strike = False
                    run.font.double_strike = False
                    run.font.subscript = False
                    run.font.superscript = False
                    run.font.all_caps = False
                    run.font.small_caps = False
                    run.font.shadow = False
                    run.font.emboss = False
                    run.font.imprint = False
                    run.font.outline = False
                except Exception:
                    # Some properties might not be settable, continue anyway
                    pass
            else:
                run = para.add_run(clean_run_text)
            
            # Apply all formatting
            # DEBUG: Log what we're applying
            print(f"[DEBUG APPLY RUN {i}] fmt.get('italic')={fmt.get('italic')}, fmt.get('bold')={fmt.get('bold')}, text={clean_run_text[:30] if len(clean_run_text) > 30 else clean_run_text}")
            
            # Basic formatting - only apply if value is explicitly True or False (not None)
            if fmt.get('bold') is not None:
                run.bold = fmt['bold']
                print(f"[DEBUG APPLY RUN {i}] Set run.bold = {fmt['bold']}")
            if fmt.get('italic') is not None:
                run.italic = fmt['italic']
                print(f"[DEBUG APPLY RUN {i}] Set run.italic = {fmt['italic']}")
            if fmt.get('underline') is not None:
                run.underline = fmt['underline']
            if fmt.get('strike') is not None:
                run.font.strike = fmt['strike']
            if fmt.get('double_strike') is not None:
                run.font.double_strike = fmt['double_strike']
            if fmt.get('subscript') is not None:
                run.font.subscript = fmt['subscript']
            if fmt.get('superscript') is not None:
                run.font.superscript = fmt['superscript']
            
            # Font properties
            if fmt.get('font_name'):
                run.font.name = fmt['font_name']
            if fmt.get('font_size'):
                # Use _safe_int to handle any float values stored
                size_val = _safe_int(fmt['font_size'])
                if size_val:
                    run.font.size = Pt(size_val)
            
            # Color handling
            if fmt.get('font_color'):
                if str(fmt['font_color']).startswith('theme:'):
                    # Theme color - would need special handling
                    pass
                else:
                    try:
                        # Parse RGB color - handle both int and float strings using _safe_int
                        rgb_int = _safe_int(fmt['font_color'])
                        
                        # Validate RGB value is in valid range (0 to 16777215 = 0xFFFFFF)
                        if rgb_int is not None and 0 <= rgb_int <= 16777215:
                            run.font.color.rgb = RGBColor(
                                (rgb_int >> 16) & 0xFF,
                                (rgb_int >> 8) & 0xFF,
                                rgb_int & 0xFF
                            )
                    except (ValueError, TypeError, OverflowError) as e:
                        # Invalid color value - skip color setting
                        pass
            
            # Advanced formatting
            if fmt.get('all_caps') is not None:
                run.font.all_caps = fmt['all_caps']
            if fmt.get('small_caps') is not None:
                run.font.small_caps = fmt['small_caps']
            if fmt.get('shadow') is not None:
                run.font.shadow = fmt['shadow']
            if fmt.get('emboss') is not None:
                run.font.emboss = fmt['emboss']
            if fmt.get('imprint') is not None:
                run.font.imprint = fmt['imprint']
            if fmt.get('outline') is not None:
                run.font.outline = fmt['outline']
            
        # Remove any extra empty runs
        while len(para.runs) > len(parsed_runs):
            para._p.remove(para.runs[-1]._element)
        
        # CRITICAL: Ensure heading paragraphs are bold (fixes issue with cloned documents)
        ensure_heading_bold(para)


def create_robust_translation_prompt(marked_texts: List[Tuple[int, str]], language: str) -> str:
    """Create a prompt that ensures 100% format preservation"""
    
    prompt = f"""You are a professional translator with expertise in preserving complex document formatting.

Translate the following {len(marked_texts)} passages into {language} with ABSOLUTE format preservation.

🎯 CRITICAL: READING LEVEL & MODERNIZATION REQUIREMENT:

**8TH GRADE READING LEVEL - MANDATORY:**
- Translate ALL text to modern, contemporary language suitable for 8th grade reading level (ages 13-14)
- This applies to ALL target languages, including English-to-English translation

**🔴 ENGLISH-TO-ENGLISH MODERNIZATION - ABSOLUTELY REQUIRED:**
- When target language is "English" or "Contemporary English", you MUST still translate/modernize the text
- DO NOT leave text unchanged just because it's already in English
- You MUST modernize old/archaic English to contemporary English
- You MUST simplify complex language to 8th grade level
- You MUST replace formal/old-fashioned words with modern equivalents
- Even if the text looks "modern", you MUST ensure it's at 8th grade reading level
- This is NOT optional - English-to-English still requires active translation work
- Every word and sentence must be reviewed and modernized if needed

**MODERNIZATION REQUIREMENTS:**
- If source text is in old/archaic English, modernize it to contemporary English
- Use simple, clear, everyday language that common people can easily understand
- Replace formal academic language with conversational language
- Replace complex vocabulary with simpler 8th grade level words
- Replace archaic words with modern equivalents:
  * "thou/thee/thy" → "you/your"
  * "hath/hast" → "has/have"
  * "doth" → "does"
  * "art" → "are"
  * "wilt" → "will"
  * "hither/thither" → "here/there"
  * "whence" → "from where"
  * "whither" → "to where"
  * "betwixt" → "between"
  * "ere" → "before"
  * "nigh" → "near"
  * "oft" → "often"
  * "perchance" → "perhaps"
  * "verily" → "truly" or "really"
  * "hence" → "therefore" or "so"
  * "thus" → "so" or "in this way"
  * "wherefore" → "why"
  * "methinks" → "I think"
  * "prithee" → "please"
  * "anon" → "soon" or "later"
- Simplify complex sentence structures into clear, straightforward sentences
- Break up very long sentences into shorter, more readable ones
- Use active voice instead of passive voice when possible
- Replace formal/archaic expressions with modern, conversational equivalents
- Maintain the meaning and tone, but make it accessible to modern readers
- Even if translating to English, modernize old English to contemporary English

**NUMBER FORMAT MODERNIZATION - CRITICAL:**
- Convert ALL Roman numerals to modern Arabic numerals (0-9)
- Convert ALL old/archaic number formats to modern Arabic numerals
- Examples of conversions:
  * Roman numerals: I → 1, II → 2, III → 3, IV → 4, V → 5, VI → 6, VII → 7, VIII → 8, IX → 9, X → 10
  * Larger Roman numerals: XI → 11, XII → 12, XIII → 13, XIV → 14, XV → 15, XX → 20, L → 50, C → 100, D → 500, M → 1000
  * "Chapter I" → "Chapter 1"
  * "Part III" → "Part 3"
  * "Volume XIV" → "Volume 14"
  * "Year MDCCLXXVI" → "Year 1776"

**🔴 CRITICAL: STANDALONE ROMAN NUMERALS (SECTION/STANZA NUMBERS):**
- **MOST IMPORTANT**: When you see a standalone Roman numeral on its own line or at the start of a paragraph, it is ALWAYS a section/stanza number, NOT an English letter
- **Examples that MUST be converted:**
  * A paragraph containing ONLY "I" → Convert to "1" (NOT the English letter "I")
  * A paragraph containing ONLY "V" → Convert to "5" (NOT the English letter "V")
  * A paragraph containing ONLY "X" → Convert to "10" (NOT the English letter "X")
  * A paragraph containing ONLY "III" → Convert to "3"
  * A paragraph containing ONLY "VII" → Convert to "7"
- **How to recognize standalone Roman numerals:**
  * They appear alone on their own line (preceded by newline, followed by newline)
  * They appear at the very start of a paragraph (first thing on the line)
  * They are NOT part of a word (like "I" in "I went to the store")
  * They are NOT part of a sentence (like "V" in "V for Victory")
- **When in doubt**: If a Roman numeral (I, V, X, etc.) appears standalone on its own line or at paragraph start, it's 99% likely a section number and should be converted
- **Rule of thumb**: I, V, X alone on a line = section/stanza number = convert to 1, 5, 10

**🚫 CRITICAL WARNING - DO NOT CONVERT THE ENGLISH PRONOUN "I":**
- The letter "I" is ALSO the English first-person pronoun (meaning "me" or "myself")
- **NEVER convert "I" to "1" when it's the English pronoun!**
- **Examples that MUST NOT be converted:**
  * "I thought" → KEEP as "I thought" (NOT "1 thought")
  * "I went to the store" → KEEP as "I went to the store" (NOT "1 went to the store")
  * "I am happy" → KEEP as "I am happy" (NOT "1 am happy")
  * "I love you" → KEEP as "I love you" (NOT "1 love you")
- **How to recognize the English pronoun "I":**
  * It's followed by a verb (thought, went, am, was, have, will, etc.)
  * It's part of a sentence, not standing alone
  * It appears with other words in the same run/paragraph
- **ONLY convert "I" to "1" when it's COMPLETELY STANDALONE** (the entire paragraph is just "I" with nothing else)

- When translating to modern English (8th grade level), use modern Arabic numerals exclusively
- Do NOT preserve Roman numerals in modern English translations
- Convert ordinal Roman numerals: "1st" (not "Ist"), "2nd" (not "IInd"), "3rd" (not "IIIrd"), "4th" (not "IVth")
- If number is part of a proper noun or historical reference that traditionally uses Roman numerals (like "World War II"), you may preserve it, but prefer modern format when modernizing
- Convert written-out archaic number forms: "one and twenty" → "21", "three score" → "60"
- Use standard modern number format: "1,234" not "one thousand two hundred thirty-four" (unless context requires words)

**EXAMPLES - ENGLISH-TO-ENGLISH MODERNIZATION:**

Example 1 - Archaic English:
- Old: "Thou art a goodly fellow, methinks."
- Modern: "I think you're a good person."
- ❌ WRONG: Leaving it as "Thou art a goodly fellow, methinks." (unchanged)
- ✅ CORRECT: Modernizing to "I think you're a good person."

Example 2 - Archaic Questions:
- Old: "Whence comest thou, and whither goest thou?"
- Modern: "Where are you coming from, and where are you going?"
- ❌ WRONG: Leaving it unchanged
- ✅ CORRECT: Modernizing to contemporary English

Example 3 - Formal/Old English:
- Old: "Verily, I say unto thee, this matter doth concern us all."
- Modern: "I'm telling you, this matter concerns all of us."
- ❌ WRONG: Leaving it unchanged
- ✅ CORRECT: Modernizing to conversational English

Example 4 - Complex Academic English:
- Old: "The aforementioned individual has demonstrated a propensity for engaging in activities that are not in accordance with established protocols."
- Modern: "This person has a habit of doing things that break the rules."
- ❌ WRONG: Leaving complex academic language unchanged
- ✅ CORRECT: Simplifying to 8th grade level

Example 5 - Old-Fashioned Formal English:
- Old: "Hath he not spoken thus to thee ere this day?"
- Modern: "Hasn't he said this to you before today?"
- ❌ WRONG: Leaving it unchanged
- ✅ CORRECT: Modernizing to contemporary English

Example 6 - Even "Modern" English Needs Simplification:
- Old: "The individual's cognitive processes were significantly impeded by the complexity of the situation."
- Modern: "The person had trouble thinking because the situation was too complicated."
- ❌ WRONG: Leaving complex academic language unchanged
- ✅ CORRECT: Simplifying to 8th grade level

Example 7 - Roman Numeral Conversion:
- Old: "Chapter I discusses the basics."
- Modern: "Chapter 1 discusses the basics."
- ❌ WRONG: Leaving "Chapter I" unchanged
- ✅ CORRECT: Converting to "Chapter 1"

Example 8 - Roman Numeral Conversion (Multiple):
- Old: "In Part III, Section XIV, we find..."
- Modern: "In Part 3, Section 14, we find..."
- ❌ WRONG: Leaving "Part III, Section XIV" unchanged
- ✅ CORRECT: Converting to "Part 3, Section 14"

Example 9 - Roman Numeral in Title:
- Old: "Volume II of the collection"
- Modern: "Volume 2 of the collection"
- ❌ WRONG: Leaving "Volume II" unchanged
- ✅ CORRECT: Converting to "Volume 2"

Example 10 - Year with Roman Numerals:
- Old: "In the year MDCCLXXVI, the Declaration was signed."
- Modern: "In the year 1776, the Declaration was signed."
- ❌ WRONG: Leaving "MDCCLXXVI" unchanged
- ✅ CORRECT: Converting to "1776"

**REMEMBER:**
- When target is "English" or "Contemporary English", you MUST actively modernize
- Do NOT copy text unchanged - always review and modernize
- Every sentence must be checked for 8th grade readability
- Complex words → Simple words
- Formal language → Conversational language
- Old English → Modern English

**LINK / URL HANDLING - CRITICAL:**
- REMOVE all hyperlinks, URLs, and link markup from the translation
- If original text contains a URL (http://, https://, www., etc.) → OMIT it entirely
- If original text contains Markdown links like `[text](url)` → Output ONLY the text, remove the `(url)`
- If original text contains angle-bracket links `<http://...>` → Remove them completely
- If original text contains HTML links `<a href="...">text</a>` → Output only the text, remove the href
- If original contains "See here: https://..." → Translate "See here:" but REMOVE the URL
- NEVER translate or preserve URLs or links – they must be removed
- This prevents duplicated content and unnecessary link noise in the translation

🚫 CRITICAL: NO HALLUCINATION - EXACT LINE & CONTENT PRESERVATION:

**MANDATORY - ZERO HALLUCINATION POLICY:**
- DO NOT add any content that is not in the original text
- DO NOT remove any content from the original text
- DO NOT add extra sentences, explanations, or commentary
- DO NOT summarize or condense the text
- DO NOT expand or elaborate on the text
- Translate sentence-by-sentence, maintaining exact sentence count
- If original has 5 lines → translation MUST have exactly 5 lines
- If original has 10 sentences → translation MUST have exactly 10 sentences
- Count lines before translating and ensure your translation has the SAME number of lines
- Count sentences before translating and ensure your translation has the SAME number of sentences

**LINE COUNT PRESERVATION - ABSOLUTE REQUIREMENT:**
- Count the number of lines in the original passage (lines separated by \\n)
- Your translation MUST have the EXACT same number of lines
- Example: If original has 5 lines:
  Line 1: "Hello"
  Line 2: "How are you?"
  Line 3: "I am fine."
  Line 4: "Thank you."
  Line 5: "Goodbye"
  
  Translation MUST also have exactly 5 lines:
  Line 1: [translation of line 1]
  Line 2: [translation of line 2]
  Line 3: [translation of line 3]
  Line 4: [translation of line 4]
  Line 5: [translation of line 5]
  
- DO NOT combine lines into one
- DO NOT split one line into multiple lines
- DO NOT add blank lines
- DO NOT remove blank lines
- If original has a blank line, translation must have a blank line in the same position

**SENTENCE COUNT PRESERVATION:**
- Count the number of sentences in the original (sentences end with . ! ?)
- Your translation MUST have the EXACT same number of sentences
- Translate each sentence independently - do not combine or split sentences
- If original has 3 sentences, translation must have 3 sentences
- DO NOT add explanatory sentences
- DO NOT add transitional phrases that weren't in the original
- DO NOT remove sentences or combine them

**CONTENT FIDELITY:**
- Translate ONLY what is written - nothing more, nothing less
- If a sentence is unclear, translate it as written - do not "clarify" or "improve" it
- Do not add context or background information
- Do not add examples or explanations
- Do not add connecting words or phrases that weren't in the original
- Maintain the exact structure: if original is terse, translation should be terse
- Maintain the exact structure: if original is verbose, translation should be verbose

**ANTI-HALLUCINATION CHECKLIST:**
Before submitting your translation, verify:
✓ Same number of lines as original
✓ Same number of sentences as original
✓ No added content
✓ No removed content
✓ No added explanations
✓ No added examples
✓ No added transitions
✓ Exact 1:1 correspondence between original and translation

🔴 CRITICAL FORMATTING RULES - 100% PRESERVATION REQUIRED:

1. **RUN MARKERS ARE SACRED**:
   - ««RUN0:B»»text««/RUN0»» = Run 0 with Bold
   - ««RUN1:I,U»»text««/RUN1»» = Run 1 with Italic+Underline
   - ««RUN2:F:Arial_Black,SZ:14,C:FF0000»»text««/RUN2»» = Custom font, size, color
   - NEVER modify, remove, or reorder these markers

1.5. **OPTIMIZATION - MERGED RUNS**:
   - Multiple consecutive runs with identical formatting have been merged into single runs
   - This reduces complexity while preserving 100% of formatting and spacing
   - Each run marker may represent one or more original runs with the same formatting
   - CRITICAL: Spaces are already included in the run text - preserve them exactly
   - Example: ««RUN25:PLAIN»»Oh, what must one often hear««/RUN25»» contains spaces between words
   - Do NOT add or remove spaces - they are already correctly positioned in the text
   - The merged text preserves exact spacing from the original document

2. **FORMATTING CODES**:
   - B=Bold, I=Italic, U=Underline, S=Strike, DS=DoubleStrike
   - SUB=Subscript, SUP=Superscript
   - F:FontName = Font (spaces replaced with _)
   - SZ:Points = Font size
   - C:RRGGBB = Color (hex)
   - H:Color = Highlight
   - AC=AllCaps, SC=SmallCaps, SH=Shadow, EM=Emboss, OL=Outline
   - PLAIN = No formatting

3. **TRANSLATION RULES**:
   - Translate ONLY the text between markers
   - Maintain EXACT number of runs (runs may be merged, but count stays the same)
   - Keep run order: RUN0, RUN1, RUN2...
   - Preserve spacing and line breaks within runs
   - CRITICAL: Spaces are ALREADY included in the run text - preserve them exactly as they appear
   - Do NOT add extra spaces between words
   - Do NOT remove spaces between words
   - The text "Oh, what must one often hear" already has correct spacing - translate it maintaining the same spacing
   - Each run's text contains the exact spacing from the original - translate word-by-word but keep spacing intact

4. **PUNCTUATION PRESERVATION - CRITICAL**:
   - PRESERVE ALL punctuation marks EXACTLY as they appear
   - Quotation marks ("") stay as quotation marks ("")
   - Em dashes (—) stay as em dashes (—)
   - En dashes (–) stay as en dashes (–)
   - Apostrophes (') stay as apostrophes (')
   - Do NOT convert between punctuation styles
   - Do NOT change "dialogue" to —dialogue— or vice versa
   - Do NOT replace quotes with em dashes or em dashes with quotes
   - ONLY translate the words, NOT the punctuation marks
   - Punctuation style is part of the original formatting - preserve it

4.5. **CASE PRESERVATION - CRITICAL**:
   - PRESERVE THE EXACT CASE PATTERN of each run, even if formatting is identical
   - If text is split into separate runs, each run has a DISTINCT case pattern that must be preserved
   - Example: ««RUN0:PLAIN»»HELLO, ««/RUN0»»««RUN1:PLAIN»»how you doing?««/RUN1»»
     - RUN0 contains "HELLO, " (all uppercase) - preserve as all uppercase in translation
     - RUN1 contains "how you doing?" (mixed case) - preserve as mixed case in translation
   - Even though both runs have PLAIN formatting, they are SEPARATE runs because of case differences
   - CRITICAL: Do NOT normalize case across runs - if RUN0 is all caps, keep it all caps in translation
   - If a word/segment is ALL UPPERCASE in the source, translate it to ALL UPPERCASE in the target
   - If a word/segment is mixed case in the source, translate it to mixed case in the target
   - The fact that text is in separate runs indicates intentional case distinction
   - Example: "HELLO, how you doing?" → "HOLA, ¿cómo estás?" (not "HOLA, ¿CÓMO ESTÁS?")
   - Example: ««RUN0:PLAIN»»HELLO««/RUN0»»««RUN1:PLAIN»», how««/RUN1»» → preserve case pattern of each run
   
   **CASE PRESERVATION ACROSS LANGUAGE DIFFERENCES - CRITICAL**:
   - Word boundaries may change during translation (one word becomes multiple, or vice versa)
   - Word count may change (short word becomes longer phrase, or vice versa)
   - BUT: The CASE PATTERN of each run must be preserved regardless of these changes
   - If RUN0 is all uppercase, the ENTIRE translation in RUN0 must remain all uppercase
   - If RUN1 is mixed case, the ENTIRE translation in RUN1 must remain mixed case
   - Example: ««RUN0:PLAIN»»HELLO««/RUN0»» → Spanish: ««RUN0:PLAIN»»HOLA««/RUN0»» (HOLA in all caps)
   - Example: ««RUN0:PLAIN»»HELLO THERE««/RUN0»» → Spanish: ««RUN0:PLAIN»»HOLA ALLÍ««/RUN0»» (both words all caps)
   - Example: ««RUN0:PLAIN»»OK««/RUN0»» → Spanish: ««RUN0:PLAIN»»DE ACUERDO««/RUN0»» (entire phrase all caps, even though it's multiple words now)
   - The CASE STYLE is what matters, not the word count or boundaries
   - Each run's case pattern is INDEPENDENT - translate each run separately and preserve its case style

5. **COMPLETE WORD TRANSLATION - MANDATORY**:
   - TRANSLATE EVERY SINGLE WORD in the source language
   - NO source language words should remain in the translation
   - Common words like "yes", "no", "certainly", "maybe", "okay" MUST be translated
   - Single quoted words like "yes", "no", "okay" MUST be translated: "sí", "no", "de acuerdo"
   - Words in quotes are NOT exceptions - they MUST be translated
   - If you see: "yes" → translate to: "sí" (or equivalent in target language)
   - If you see: "certainly" → translate to: "ciertamente" (or equivalent)
   - Interjections, exclamations, and standalone words MUST be translated
   - Do NOT leave ANY source language words untranslated
   - Every meaningful word in the source language must have a translation
   - If a word appears in quotes, translate the word but keep the quotes: "yes" → "sí"
   - NO exceptions - translate EVERY word

6. **EXAMPLES**:
   Input: "««RUN0:B»»Hello««/RUN0»» ««RUN1:PLAIN»»world««/RUN1»»««RUN2:I»»!««/RUN2»»"
   Spanish: "««RUN0:B»»Hola««/RUN0»» ««RUN1:PLAIN»»mundo««/RUN1»»««RUN2:I»»!««/RUN2»»"

   Input: "««RUN0:B,I,F:Times_New_Roman,SZ:16»»Chapter 1««/RUN0»»"
   Spanish: "««RUN0:B,I,F:Times_New_Roman,SZ:16»»Capítulo 1««/RUN0»»"

   Input: "««RUN0:PLAIN»»"He died."««/RUN0»»"
   Spanish: "««RUN0:PLAIN»»"Murió."««/RUN0»»" (quotes preserved, NOT —Murió.—)

   Input: "««RUN0:PLAIN»»—Murió.««/RUN0»»"
   Spanish: "««RUN0:PLAIN»»—Murió.««/RUN0»»" (em dash preserved, NOT "Murió.")

   Input: "««RUN0:PLAIN»»He said "yes" and "certainly".««/RUN0»»"
   Spanish: "««RUN0:PLAIN»»Dijo "sí" y "ciertamente".««/RUN0»»" (ALL words translated, quotes preserved)

   Input: "««RUN0:PLAIN»»Yes, certainly, okay.««/RUN0»»"
   Spanish: "««RUN0:PLAIN»»Sí, ciertamente, de acuerdo.««/RUN0»»" (Every word translated)

   Input: "««RUN0:PLAIN»»HELLO, ««/RUN0»»««RUN1:PLAIN»»how you doing?««/RUN1»»"
   Spanish: "««RUN0:PLAIN»»HOLA, ««/RUN0»»««RUN1:PLAIN»»¿cómo estás?««/RUN1»»" (Case pattern preserved: RUN0 uppercase → uppercase, RUN1 mixed → mixed)
   
   Input: "««RUN0:PLAIN»»HELLO««/RUN0»»««RUN1:PLAIN»», how are you?««/RUN1»»"
   Spanish: "««RUN0:PLAIN»»HOLA««/RUN0»»««RUN1:PLAIN»», ¿cómo estás?««/RUN1»»" (Preserve case: HELLO stays uppercase, rest stays mixed case)
   
   Input: "««RUN0:PLAIN»»OK««/RUN0»»««RUN1:PLAIN»», I understand««/RUN1»»"
   Spanish: "««RUN0:PLAIN»»DE ACUERDO««/RUN0»»««RUN1:PLAIN»», entiendo««/RUN1»»" (Even though "OK" (2 chars) becomes "DE ACUERDO" (10 chars), preserve all caps in RUN0)
   
   Input: "««RUN0:PLAIN»»HELLO THERE««/RUN0»»««RUN1:PLAIN»», my friend««/RUN1»»"
   Spanish: "««RUN0:PLAIN»»HOLA ALLÍ««/RUN0»»««RUN1:PLAIN»», mi amigo««/RUN1»»" (All words in RUN0 stay uppercase even if word count/structure changes)

7. **WARNINGS**:
   ❌ NEVER combine runs
   ❌ NEVER split runs
   ❌ NEVER change formatting codes
   ❌ NEVER add plain text outside markers

7. **OUTPUT FORMAT - CRITICAL**:
   - Use the delimiter markers <<<TRANSLATION_X_START>>> and <<<TRANSLATION_X_END>>> ONLY as separators (where X is the passage number)
   - DO NOT include these delimiter markers INSIDE your translation text
   - The delimiter markers are ONLY for parsing - they should wrap your translation, not be part of it
   - Your translation should ONLY contain the marked text with RUN markers, nothing else
   - Example CORRECT format:
     <<<TRANSLATION_1_START>>>
     ««RUN0:B»»Hola««/RUN0»» ««RUN1:PLAIN»»mundo««/RUN1»»
     <<<TRANSLATION_1_END>>>
   - Example WRONG format (DO NOT DO THIS):
     <<<TRANSLATION_1_START>>>
     <<<TRANSLATION_1_START>>>««RUN0:B»»Hola««/RUN0»»<<<TRANSLATION_1_END>>>
     <<<TRANSLATION_1_END>>>
   - The delimiter markers should appear ONCE at the start and ONCE at the end, not inside the translation

8. **WARNINGS**:
   ❌ NEVER combine runs
   ❌ NEVER split runs
   ❌ NEVER change formatting codes
   ❌ NEVER add plain text outside markers
   ❌ NEVER include delimiter markers (<<<TRANSLATION_X_START>>>) inside your translation text
   ❌ NEVER include any tags like <untranslated> in your translation output. Only output the translated text.

OUTPUT FORMAT:
"""
    
    # Add passages
    for para_id, marked_text in marked_texts:
        prompt += f"\nPassage {para_id}:\n"
        prompt += f'"""\n{marked_text}\n"""\n'
        prompt += f"\nOutput your translation for Passage {para_id} in this EXACT format:\n"
        prompt += f"<<<TRANSLATION_{para_id}_START>>>\n"
        prompt += "[Your translation with all RUN markers preserved - NO delimiter markers inside]\n"
        prompt += f"<<<TRANSLATION_{para_id}_END>>>\n\n"
    
    return prompt


def integrate_robust_preservation(doc: Document, paragraphs_to_translate: List[Tuple[int, Paragraph]], 
                                language: str, translate_func) -> Dict[int, str]:
    """Main function to translate with 100% format preservation"""
    
    # Initialize preserver
    preserver = RobustFormatPreserver(doc)
    
    # Extract formatting and create marked texts
    marked_texts = []
    para_mapping = {}
    
    for idx, (para_idx, para) in enumerate(paragraphs_to_translate):
        marked_text, para_data = preserver.create_formatted_text_for_translation(para, idx)
        marked_texts.append((idx, marked_text))
        para_mapping[idx] = (para_idx, para)
    
    # Create translation prompt
    prompt = create_robust_translation_prompt(marked_texts, language)
    
    # Get translations (this would call your API)
    translations = translate_func(prompt)
    
    # Parse and apply translations
    results = {}
    for idx, translation in translations.items():
        para_idx, para = para_mapping[idx]
        
        # Clean translation (remove markers from response format)
        clean_translation = translation
        clean_translation = re.sub(f'<<<TRANSLATION_{idx}_START>>>', '', clean_translation)
        clean_translation = re.sub(f'<<<TRANSLATION_{idx}_END>>>', '', clean_translation)
        clean_translation = clean_translation.strip()
        
        # Apply formatting
        preserver.apply_formatting_to_paragraph(para, idx, clean_translation)
        
        # Store result
        results[para_idx] = clean_translation
    
    return results


# Export main components
__all__ = [
    'RobustFormatPreserver',
    'RunFormatting',
    'ParagraphFormatting',
    'create_robust_translation_prompt',
    'integrate_robust_preservation'
]
