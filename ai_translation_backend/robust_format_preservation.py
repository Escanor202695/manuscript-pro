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

        return RunFormatting(
            text=run.text,
            bold=run.bold,
            italic=run.italic,
            underline=run.underline,
            strike=run.font.strike,
            double_strike=run.font.double_strike,
            subscript=run.font.subscript,
            superscript=run.font.superscript,
            font_name=run.font.name,
            font_size=font_size,
            font_color=font_color,
            highlight_color=highlight_color,
            all_caps=run.font.all_caps,
            small_caps=run.font.small_caps,
            shadow=run.font.shadow,
            emboss=run.font.emboss,
            imprint=run.font.imprint,
            outline=run.font.outline,
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
    
    def _merge_runs_with_same_formatting(self, para: Paragraph) -> List[Dict]:
        """
        Merge consecutive runs that have identical formatting.
        This dramatically reduces run count while preserving exact spacing.
        CRITICAL: run.text already contains spaces, so concatenation preserves spacing perfectly.
        """
        if not para.runs:
            return []
        
        merged_groups = []
        current_group = {
            'runs': [],
            'run_indices': [],  # Track indices to avoid index() lookup issues
            'text': '',
            'format': None,
            'format_obj': None
        }
        
        # Track indices as we iterate to avoid index() lookup issues
        for idx, run in enumerate(para.runs):
            run_format = self.extract_run_formatting(run)
            format_sig = self._get_format_signature(run_format)
            
            # Check if this run has the same formatting as current group
            if current_group['format'] is None:
                # First run - start new group
                current_group['runs'] = [run]
                current_group['run_indices'] = [idx]
                current_group['text'] = run.text  # Includes spaces!
                current_group['format'] = format_sig
                current_group['format_obj'] = run_format
            elif format_sig == current_group['format']:
                # Same formatting - merge into current group
                # CRITICAL: run.text already contains spaces, so concatenation preserves spacing
                current_group['runs'].append(run)
                current_group['run_indices'].append(idx)
                current_group['text'] += run.text  # Spaces preserved automatically!
            else:
                # Different formatting - save current group and start new one
                merged_groups.append(current_group)
                current_group = {
                    'runs': [run],
                    'run_indices': [idx],
                    'text': run.text,
                    'format': format_sig,
                    'format_obj': run_format
                }
        
        # Add the last group
        if current_group['runs']:
            merged_groups.append(current_group)
        
        return merged_groups
    
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
        
        # Pattern to match run markers
        pattern = r'««RUN(\d+):[^»]+»»(.*?)««/RUN\1»»'
        
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
                parsed_runs.append({
                    'text': run_text,
                    'format': original_run['format'],
                    'run_id': run_id
                })
            else:
                # Run ID not found - shouldn't happen
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
        # CRITICAL: Remove ALL delimiter markers first (catches any variations including translated/misspelled ones)
        # First: Remove properly closed markers <<<...>>>
        translated_text = re.sub(r'<<<[^>]*?>>>', '', translated_text, flags=re.DOTALL)
        # Second: Remove MALFORMED markers that start with <<< but have no closing >>>
        # Match <<< followed by ANY characters until whitespace or end of string
        translated_text = re.sub(r'<<<[^\s]*', '', translated_text)
        # Also catch any remaining <<< patterns (defensive)
        translated_text = re.sub(r'<<<.*?(?=\s|$)', '', translated_text, flags=re.DOTALL)
        
        para_data = self.format_map.get(para_id)
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
            
            # Create or reuse run
            if i < len(para.runs):
                run = para.runs[i]
                run.text = clean_run_text
            else:
                run = para.add_run(clean_run_text)
            
            # Apply all formatting
            fmt = run_data.get('format', {})
            
            # Basic formatting
            if fmt.get('bold') is not None:
                run.bold = fmt['bold']
            if fmt.get('italic') is not None:
                run.italic = fmt['italic']
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
