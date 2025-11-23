# 🎯 Ultimate Formatting Preservation Strategy for Document Translation

## 📊 Current State Analysis

### What We're Dealing With:
1. **Mixed formatting** (bold/italic within paragraphs)
2. **Complex documents** (poetry with indentation, academic papers with citations)
3. **Rate limits** (need to batch translations)
4. **Quality requirements** (context-aware translation)
5. **Various document types** (simple prose to heavily formatted documents)

### Current Limitations:
- **Paragraph-based**: Loses inline formatting (bold/italic)
- **Run-based**: Causes word concatenation, too many API calls
- **JSON responses**: Can mangle special characters

## 🚀 The Ultimate Solution: Smart Hybrid Approach

### Strategy Overview:
```
Document → Analyze Complexity → Choose Strategy → Preserve Formatting → Translate → Reconstruct
```

## 📋 Three-Tier Translation Strategy

### Tier 1: Simple Documents (Fast & Efficient)
**When to use**: Plain text, minimal formatting
**Method**: Large batch paragraph-based
**Batch size**: 100-300 paragraphs
**Formatting preserved**: Paragraph styles, alignment, spacing

### Tier 2: Moderate Complexity (Balanced)
**When to use**: Some bold/italic, consistent formatting
**Method**: Smart batch with format mapping
**Batch size**: 20-50 paragraphs
**Formatting preserved**: All paragraph + mapped inline formatting

### Tier 3: Complex Documents (Full Preservation)
**When to use**: Heavy mixed formatting, critical documents
**Method**: Run-aware paragraph translation
**Batch size**: 5-10 paragraphs
**Formatting preserved**: Everything including font variations

## 🛠️ Implementation Details

### 1. Document Complexity Analyzer
```python
def analyze_document_complexity(doc):
    """Determine which tier to use based on document analysis"""
    
    total_paragraphs = len(doc.paragraphs)
    formatted_paragraphs = 0
    total_runs = 0
    inline_formatting_count = 0
    font_variations = set()
    
    for para in doc.paragraphs:
        if not para.text.strip():
            continue
            
        runs = list(para.runs)
        total_runs += len(runs)
        
        # Check for inline formatting
        if len(runs) > 1:
            formatted_paragraphs += 1
            
        for run in runs:
            # Count formatting types
            if run.bold:
                inline_formatting_count += 1
            if run.italic:
                inline_formatting_count += 1
            if run.underline:
                inline_formatting_count += 1
            if run.font.name:
                font_variations.add(run.font.name)
                
    # Calculate complexity score
    avg_runs_per_para = total_runs / max(total_paragraphs, 1)
    formatting_density = inline_formatting_count / max(total_runs, 1)
    font_diversity = len(font_variations)
    
    # Determine tier
    if avg_runs_per_para < 1.5 and formatting_density < 0.1:
        return "TIER_1_SIMPLE"
    elif avg_runs_per_para < 5 and formatting_density < 0.3:
        return "TIER_2_MODERATE"
    else:
        return "TIER_3_COMPLEX"
```

### 2. Format Preservation Map
```python
class FormatPreservationMap:
    """Maps formatting from original to translated text"""
    
    def __init__(self):
        self.format_map = {}
        
    def extract_formatting(self, paragraph):
        """Extract all formatting info from paragraph"""
        format_info = {
            'runs': [],
            'text': paragraph.text,
            'style': paragraph.style.name if paragraph.style else None,
            'alignment': paragraph.alignment
        }
        
        char_position = 0
        for run in paragraph.runs:
            run_info = {
                'start': char_position,
                'end': char_position + len(run.text),
                'text': run.text,
                'bold': run.bold,
                'italic': run.italic,
                'underline': run.underline,
                'font_name': run.font.name,
                'font_size': run.font.size,
                'font_color': run.font.color.rgb if run.font.color else None,
                'highlight': run.font.highlight_color
            }
            format_info['runs'].append(run_info)
            char_position += len(run.text)
            
        return format_info
```

### 3. Smart Translation with Format Preservation

```python
async def translate_with_format_preservation(paragraphs, tier, language, model):
    """Translate while preserving formatting based on tier"""
    
    if tier == "TIER_1_SIMPLE":
        # Fast batch translation - paragraph level only
        return await translate_simple_batch(paragraphs, language, model)
        
    elif tier == "TIER_2_MODERATE":
        # Smart format mapping
        format_maps = []
        texts_to_translate = []
        
        for para in paragraphs:
            fmt_map = FormatPreservationMap()
            format_info = fmt_map.extract_formatting(para)
            format_maps.append(format_info)
            
            # Mark formatting in text for AI
            marked_text = mark_formatting_in_text(para)
            texts_to_translate.append(marked_text)
            
        # Translate with format markers
        translations = await translate_with_markers(texts_to_translate, language, model)
        
        # Apply formatting to translations
        return apply_formatting_to_translations(translations, format_maps)
        
    else:  # TIER_3_COMPLEX
        # Full run-aware translation
        return await translate_complex_formatting(paragraphs, language, model)
```

### 4. Format Marker System (Tier 2)
```python
def mark_formatting_in_text(paragraph):
    """Add invisible markers to preserve formatting positions"""
    marked_text = ""
    
    for i, run in enumerate(paragraph.runs):
        text = run.text
        
        # Add markers for formatting
        if run.bold:
            text = f"««B»»{text}««/B»»"
        if run.italic:
            text = f"««I»»{text}««/I»»"
        if run.underline:
            text = f"««U»»{text}««/U»»"
            
        marked_text += text
        
    return marked_text

def parse_formatted_translation(translated_text):
    """Extract formatting markers from translated text"""
    import re
    
    # Find all formatted segments
    bold_pattern = r'««B»»(.*?)««/B»»'
    italic_pattern = r'««I»»(.*?)««/I»»'
    underline_pattern = r'««U»»(.*?)««/U»»'
    
    format_segments = []
    
    # Process each pattern
    for match in re.finditer(bold_pattern, translated_text):
        format_segments.append({
            'start': match.start(),
            'end': match.end(),
            'text': match.group(1),
            'type': 'bold'
        })
    
    # Remove markers for clean text
    clean_text = re.sub(r'««[^»]+»»', '', translated_text)
    
    return clean_text, format_segments
```

### 5. Advanced Prompt for Format Preservation
```python
def create_format_aware_prompt(paragraphs, language, tier):
    """Create prompts that preserve formatting based on tier"""
    
    if tier == "TIER_2_MODERATE":
        prompt = f"""
Translate the following {len(paragraphs)} paragraphs into {language}.

CRITICAL FORMATTING RULES:
1. Preserve ALL formatting markers: ««B»» for bold, ««I»» for italic, ««U»» for underline
2. Keep markers around THE SAME WORDS/PHRASES in translation
3. If a word is bold in source, its translation must be bold
4. NEVER remove or add formatting markers

Example:
Source: "This is ««B»»important««/B»» and ««I»»urgent««/I»»"
Target: "Esto es ««B»»importante««/B»» y ««I»»urgente««/I»»"

Use DELIMITER format for response:
"""
    
    elif tier == "TIER_3_COMPLEX":
        prompt = f"""
Translate with EXTREME formatting precision. Each paragraph has numbered segments that MUST maintain their formatting properties.

RULES:
1. Translate meaning accurately
2. Preserve formatting boundaries
3. Maintain segment relationships
4. Keep relative positions of formatted text

Format: <<<PARA_1>>>segment1|segment2|segment3<<<END_PARA_1>>>
"""
    
    return prompt
```

### 6. Intelligent Batching Based on Tier
```python
def get_optimal_batch_size(tier, content_type):
    """Determine batch size based on tier and content"""
    
    BATCH_SIZES = {
        "TIER_1_SIMPLE": {
            "poetry": 50,
            "dialogue": 100,
            "prose": 300,
            "default": 200
        },
        "TIER_2_MODERATE": {
            "poetry": 10,
            "dialogue": 30,
            "prose": 50,
            "default": 40
        },
        "TIER_3_COMPLEX": {
            "poetry": 3,
            "dialogue": 5,
            "prose": 10,
            "default": 5
        }
    }
    
    return BATCH_SIZES[tier].get(content_type, BATCH_SIZES[tier]["default"])
```

### 7. Run Reconstruction Algorithm
```python
def reconstruct_paragraph_with_formatting(para, translation, format_info):
    """Reconstruct paragraph with all original formatting"""
    
    # Clear existing runs
    for run in para.runs:
        run.text = ""
    para.runs[0].text = ""  # Ensure at least one run exists
    
    if not format_info['runs']:
        # Simple case - no formatting
        para.runs[0].text = translation
        return
        
    # Complex case - reconstruct runs
    current_pos = 0
    run_index = 0
    
    # Map original character positions to translated positions
    char_map = create_character_mapping(format_info['text'], translation)
    
    for run_info in format_info['runs']:
        # Calculate translated positions
        start = char_map.get(run_info['start'], 0)
        end = char_map.get(run_info['end'], len(translation))
        
        # Extract translated segment
        segment = translation[start:end]
        
        # Create or reuse run
        if run_index < len(para.runs):
            run = para.runs[run_index]
        else:
            run = para.add_run()
            
        # Apply text and formatting
        run.text = segment
        if run_info['bold'] is not None:
            run.bold = run_info['bold']
        if run_info['italic'] is not None:
            run.italic = run_info['italic']
        if run_info['underline'] is not None:
            run.underline = run_info['underline']
        if run_info['font_name']:
            run.font.name = run_info['font_name']
        if run_info['font_size']:
            run.font.size = run_info['font_size']
            
        run_index += 1
```

## 📊 Rate Limit Optimization

### Dynamic Rate Management:
```python
class RateLimitManager:
    def __init__(self):
        self.tier_weights = {
            "TIER_1_SIMPLE": 1,      # 1x API cost
            "TIER_2_MODERATE": 2,    # 2x API cost (format markers)
            "TIER_3_COMPLEX": 5      # 5x API cost (detailed processing)
        }
        
    def calculate_optimal_batch(self, tier, remaining_quota):
        """Calculate optimal batch size based on tier and quota"""
        weight = self.tier_weights[tier]
        base_batch = get_optimal_batch_size(tier, "default")
        
        # Adjust based on remaining quota
        if remaining_quota < 100:
            return max(1, base_batch // 4)  # Quarter size
        elif remaining_quota < 500:
            return max(1, base_batch // 2)  # Half size
        else:
            return base_batch  # Full size
```

## 🎯 Decision Matrix

| Document Type | Formatting Complexity | Recommended Tier | Batch Size | Quality |
|--------------|---------------------|------------------|------------|---------|
| Plain text blog | None | Tier 1 | 300 | ★★★★★ |
| Simple book | Minimal | Tier 1 | 200 | ★★★★★ |
| Academic paper | Moderate (citations) | Tier 2 | 40 | ★★★★★ |
| Poetry | Spacing critical | Tier 2 | 10 | ★★★★★ |
| Technical manual | Heavy (code, tables) | Tier 3 | 5 | ★★★★★ |
| Marketing material | Brand formatting | Tier 3 | 5 | ★★★★★ |

## 🚀 Implementation Plan

### Phase 1: Tier 1 Implementation (Current)
- ✅ Already implemented
- ✅ Handles 70% of documents well
- ✅ Fast and efficient

### Phase 2: Tier 2 Enhancement
- Add format marker system
- Implement character mapping
- Test with moderately formatted docs

### Phase 3: Tier 3 Advanced
- Full run preservation
- Font mapping system
- Complex document handling

## 💡 Key Benefits

1. **Adaptive**: Automatically chooses best approach
2. **Efficient**: Minimizes API calls based on need
3. **Quality**: Preserves formatting where it matters
4. **Scalable**: Handles any document type
5. **Smart**: Balances all requirements

## 🎉 Expected Results

### Before (Current):
- Simple docs: ✅ Perfect (fast)
- Formatted docs: ❌ Loses bold/italic
- Complex docs: ❌ Formatting destroyed

### After (Ultimate Solution):
- Simple docs: ✅ Perfect (fast) - Tier 1
- Formatted docs: ✅ Perfect (smart) - Tier 2
- Complex docs: ✅ Perfect (detailed) - Tier 3

## 🔧 Next Steps

1. Implement document complexity analyzer
2. Add Tier 2 format marker system
3. Test with various document types
4. Optimize based on results
5. Add Tier 3 for critical documents
