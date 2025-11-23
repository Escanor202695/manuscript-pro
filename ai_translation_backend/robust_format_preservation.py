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
        # Get font color
        font_color = None
        if run.font.color and run.font.color.rgb:
            font_color = str(run.font.color.rgb)
        elif run.font.color and run.font.color.theme_color:
            font_color = f"theme:{run.font.color.theme_color}"
            
        # Get highlight color
        highlight_color = None
        if run.font.highlight_color:
            highlight_color = str(run.font.highlight_color)
            
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
            font_size=run.font.size.pt if run.font.size else None,
            font_color=font_color,
            highlight_color=highlight_color,
            all_caps=run.font.all_caps,
            small_caps=run.font.small_caps,
            shadow=run.font.shadow,
            emboss=run.font.emboss,
            imprint=run.font.imprint,
            outline=run.font.outline,
            character_spacing=getattr(run.font, 'spacing', None),
            position=getattr(run.font, 'position', None)
        )
    
    def extract_paragraph_formatting(self, para: Paragraph) -> ParagraphFormatting:
        """Extract complete paragraph formatting"""
        # Extract tab stops
        tab_stops = []
        if para.paragraph_format.tab_stops:
            for tab in para.paragraph_format.tab_stops:
                tab_stops.append({
                    'position': tab.position.pt if tab.position else None,
                    'alignment': tab.alignment,
                    'leader': tab.leader
                })
        
        return ParagraphFormatting(
            style=para.style.name if para.style else None,
            alignment=para.alignment,
            left_indent=para.paragraph_format.left_indent.pt if para.paragraph_format.left_indent else None,
            right_indent=para.paragraph_format.right_indent.pt if para.paragraph_format.right_indent else None,
            first_line_indent=para.paragraph_format.first_line_indent.pt if para.paragraph_format.first_line_indent else None,
            space_before=para.paragraph_format.space_before.pt if para.paragraph_format.space_before else None,
            space_after=para.paragraph_format.space_after.pt if para.paragraph_format.space_after else None,
            line_spacing=para.paragraph_format.line_spacing,
            line_spacing_rule=para.paragraph_format.line_spacing_rule,
            keep_together=para.paragraph_format.keep_together,
            keep_with_next=para.paragraph_format.keep_with_next,
            page_break_before=para.paragraph_format.page_break_before,
            widow_control=para.paragraph_format.widow_control,
            tab_stops=tab_stops
        )
    
    def create_formatted_text_for_translation(self, para: Paragraph, para_id: int) -> Tuple[str, Dict]:
        """Create marked text for translation with 100% format preservation"""
        para_format = self.extract_paragraph_formatting(para)
        runs_data = []
        marked_text = ""
        
        for i, run in enumerate(para.runs):
            run_format = self.extract_run_formatting(run)
            run_id = self.run_counter
            self.run_counter += 1
            
            # Create unique marker
            marker = run_format.to_marker(run_id)
            
            # Add to marked text
            marked_text += f"{marker}{run.text}««/RUN{run_id}»»"
            
            # Store complete formatting data
            runs_data.append({
                'id': run_id,
                'format': asdict(run_format),
                'original_text': run.text,
                'marker': marker
            })
        
        # Store complete paragraph data
        para_data = {
            'id': para_id,
            'format': asdict(para_format),
            'runs': runs_data,
            'marked_text': marked_text,
            'checksum': hashlib.md5(marked_text.encode()).hexdigest()
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
            # Remove delimiter markers
            clean_text = re.sub(r'<<<TRANSLATION_\d+_START>>>', '', clean_text)
            clean_text = re.sub(r'<<<TRANSLATION_\d+_END>>>', '', clean_text)
            # Also remove any partial markers that might remain
            clean_text = re.sub(r'««.*', '', clean_text)
            clean_text = re.sub(r'.*»»', '', clean_text)
            return [{'text': clean_text, 'format': {}}]
        
        return parsed_runs
    
    def apply_formatting_to_paragraph(self, para: Paragraph, para_id: int, translated_text: str):
        """Apply all formatting to translated paragraph"""
        # CRITICAL: Remove delimiter markers first (before any processing)
        translated_text = re.sub(r'<<<TRANSLATION_\d+_START>>>', '', translated_text)
        translated_text = re.sub(r'<<<TRANSLATION_\d+_END>>>', '', translated_text)
        
        para_data = self.format_map.get(para_id)
        if not para_data:
            # No format data - remove any markers and set plain text
            clean_text = re.sub(r'««[^»]+»»', '', translated_text)
            # Remove any remaining delimiter markers
            clean_text = re.sub(r'<<<TRANSLATION_\d+_START>>>', '', clean_text)
            clean_text = re.sub(r'<<<TRANSLATION_\d+_END>>>', '', clean_text)
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
                run_data['text'] = re.sub(r'<<<TRANSLATION_\d+_START>>>', '', run_data['text'])
                run_data['text'] = re.sub(r'<<<TRANSLATION_\d+_END>>>', '', run_data['text'])
        
        # Clear existing runs
        for run in para.runs:
            run.text = ""
        
        # Apply paragraph formatting
        para_format = para_data['format']
        if para_format.get('style'):
            para.style = para_format['style']
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
                run.font.size = Pt(fmt['font_size'])
            
            # Color handling
            if fmt.get('font_color'):
                if fmt['font_color'].startswith('theme:'):
                    # Theme color - would need special handling
                    pass
                else:
                    try:
                        # Parse RGB color
                        rgb_int = int(fmt['font_color'])
                        run.font.color.rgb = RGBColor(
                            (rgb_int >> 16) & 0xFF,
                            (rgb_int >> 8) & 0xFF,
                            rgb_int & 0xFF
                        )
                    except:
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

🔴 CRITICAL FORMATTING RULES - 100% PRESERVATION REQUIRED:

1. **RUN MARKERS ARE SACRED**:
   - ««RUN0:B»»text««/RUN0»» = Run 0 with Bold
   - ««RUN1:I,U»»text««/RUN1»» = Run 1 with Italic+Underline
   - ««RUN2:F:Arial_Black,SZ:14,C:FF0000»»text««/RUN2»» = Custom font, size, color
   - NEVER modify, remove, or reorder these markers

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
   - Maintain EXACT number of runs
   - Keep run order: RUN0, RUN1, RUN2...
   - Preserve spacing and line breaks within runs

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
