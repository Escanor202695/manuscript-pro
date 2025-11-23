"""
Enhanced Main.py Integration - Format Preservation Version
This shows how to integrate the format preservation module into your existing main.py
"""

# Add these imports to your existing imports
from format_preservation_module import (
    DocumentComplexityAnalyzer,
    FormatPreservationMap,
    SmartBatchManager,
    FormattingReconstructor
)

# Enhanced translate function with format preservation
async def translate_document_content_async_enhanced(
    file_bytes: bytes, 
    file_name: str, 
    language: str, 
    model: str, 
    api_key: str, 
    progress_id: Optional[str] = None
) -> TranslateResponse:
    """Enhanced translation with intelligent format preservation"""
    
    logs = []
    logs.append(f"[START] Enhanced translation for {file_name} to {language} using {model}")
    
    # Load document
    doc = Document(io.BytesIO(file_bytes))
    logs.append(f"[LOAD] Document loaded with {len(doc.paragraphs)} paragraphs")
    
    # Analyze document complexity
    analyzer = DocumentComplexityAnalyzer(doc)
    tier = analyzer.get_tier()
    analysis = analyzer.get_analysis()
    
    logs.append(f"[ANALYSIS] Document complexity: {tier}")
    logs.append(f"[ANALYSIS] Avg runs/para: {analysis['avg_runs_per_para']:.2f}, "
               f"Formatting density: {analysis['formatting_density']:.2%}")
    
    # Initialize format preservation
    format_preserver = FormatPreservationMap()
    
    # Process paragraphs based on tier
    paragraphs_to_translate = []
    format_maps = []
    
    for i, para in enumerate(doc.paragraphs):
        original = para.text
        
        # Skip empty paragraphs
        if not original.strip():
            continue
        
        # Skip decorative paragraphs
        if not is_meaningful_text(original.strip()) or is_decorative_only(original.strip()):
            continue
        
        # Extract formatting info
        format_info = format_preserver.extract_paragraph_formatting(para)
        format_maps.append((i, format_info))
        
        # Add markers based on tier
        if tier in ["TIER_2_MODERATE", "TIER_3_COMPLEX"]:
            marked_text = format_preserver.mark_formatting_in_text(para, tier)
            paragraphs_to_translate.append((i, para, marked_text))
        else:
            paragraphs_to_translate.append((i, para, original))
    
    logs.append(f"[FILTER] {len(paragraphs_to_translate)} paragraphs to translate")
    
    # Create smart batches
    is_long_doc = len(paragraphs_to_translate) > 50
    batches = SmartBatchManager.create_smart_batches(
        paragraphs_to_translate, tier, is_long_doc
    )
    
    logs.append(f"[BATCH] Created {len(batches)} smart batches for {tier}")
    
    # Initialize progress
    if progress_id:
        progress_tracker[progress_id] = {
            "totalBatches": len(batches),
            "completedBatches": 0,
            "error": False
        }
    
    # Process batches
    executor = ThreadPoolExecutor(max_workers=4)
    
    async def process_batch_enhanced(batch_idx, batch):
        """Process a batch with format preservation"""
        batch_logs = []
        batch_texts = [item[2] for item in batch]  # Get marked/original text
        
        # Create enhanced prompt based on tier
        prompt = create_enhanced_batch_prompt(batch_texts, language, tier)
        
        # Call API
        if "openrouter" in model.lower():
            batch_result = await call_openrouter_batch_async(
                executor, prompt, model, api_key, batch_logs
            )
        else:
            batch_result = await call_gemini_batch_async(
                executor, client, prompt, model, batch_logs
            )
        
        return batch_idx, batch, batch_result, batch_logs
    
    # Execute batches in parallel
    tasks = [process_batch_enhanced(idx, batch) for idx, batch in enumerate(batches)]
    results = await asyncio.gather(*tasks)
    
    # Apply translations with format preservation
    for batch_idx, batch, batch_result, batch_logs in results:
        logs.extend(batch_logs)
        
        if batch_result and 'text' in batch_result:
            # Parse response based on tier
            if tier == "TIER_1_SIMPLE":
                translations = parse_structured_response(
                    batch_result['text'], len(batch), logs
                )
            else:
                # Parse with format markers
                translations = parse_formatted_response(
                    batch_result['text'], len(batch), tier, logs
                )
            
            # Apply translations
            for (para_idx, para, _), translation in zip(batch, translations):
                if translation and translation.strip():
                    # Find format info
                    format_info = next(
                        (fi for idx, fi in format_maps if idx == para_idx), 
                        None
                    )
                    
                    if tier == "TIER_1_SIMPLE":
                        FormattingReconstructor.apply_simple_translation(
                            para, translation
                        )
                    elif tier == "TIER_2_MODERATE":
                        clean_text, format_segments = format_preserver.parse_marked_translation(
                            translation, tier
                        )
                        FormattingReconstructor.apply_moderate_translation(
                            para, clean_text, format_info, format_segments
                        )
                    else:  # TIER_3_COMPLEX
                        clean_text, format_segments = format_preserver.parse_marked_translation(
                            translation, tier
                        )
                        FormattingReconstructor.apply_complex_translation(
                            para, clean_text, format_info, format_segments
                        )
        
        # Update progress
        if progress_id:
            progress_tracker[progress_id]["completedBatches"] += 1
    
    # Save document
    output_buffer = io.BytesIO()
    doc.save(output_buffer)
    output_buffer.seek(0)
    
    logs.append(f"[DONE] Translation complete with {tier} format preservation")
    
    # Return response
    translated_base64 = base64.b64encode(output_buffer.read()).decode('utf-8')
    
    return TranslateResponse(
        translatedDocument=translated_base64,
        logs=logs,
        stats={
            "tier": tier,
            "totalBatches": len(batches),
            "paragraphCount": len(paragraphs_to_translate),
            "formatComplexity": analysis
        }
    )


def create_enhanced_batch_prompt(texts: List[str], language: str, tier: str) -> str:
    """Create format-aware prompts based on tier"""
    
    if tier == "TIER_1_SIMPLE":
        # Use existing delimiter-based prompt
        return create_batch_prompt(texts, language)
    
    elif tier == "TIER_2_MODERATE":
        prompt = f"""You are a professional translator. Translate {len(texts)} passages into {language}.

CRITICAL FORMAT PRESERVATION RULES:

1. PRESERVE ALL FORMAT MARKERS EXACTLY:
   - ««B»» and ««/B»» = Bold text markers
   - ««I»» and ««/I»» = Italic text markers  
   - ««U»» and ««/U»» = Underline text markers

2. TRANSLATION RULES:
   - Translate the text between markers
   - KEEP markers around the SAME semantic content
   - If "important" is bold in source, its translation must be bold
   - NEVER add or remove format markers

3. EXAMPLES:
   Source: "This is ««B»»very important««/B»» and ««I»»urgent««/I»»."
   Spanish: "Esto es ««B»»muy importante««/B»» y ««I»»urgente««/I»»."
   
   Source: "««B»»Chapter 1««/B»»: The ««I»»Beginning««/I»»"
   Spanish: "««B»»Capítulo 1««/B»»: El ««I»»Comienzo««/I»»"

OUTPUT FORMAT:
Use delimiter format - each translation surrounded by:
<<<TRANSLATION_START_X>>>
[Your translation with format markers preserved]
<<<TRANSLATION_END_X>>>

Where X is the passage number (starting from 1).

PASSAGES TO TRANSLATE:
"""
        
        # Add numbered passages
        for i, text in enumerate(texts, 1):
            prompt += f"\nPassage {i}:\n\"\"\"\n{text}\n\"\"\"\n"
        
        return prompt
    
    else:  # TIER_3_COMPLEX
        prompt = f"""You are a professional translator specializing in complex formatted documents.

Translate {len(texts)} passages into {language} with EXTREME format precision.

FORMAT MARKERS:
- ««R0»»text««/R0»» = Run 0 (plain text)
- ««R1:B»»text««/R1»» = Run 1 (bold)
- ««R2:I»»text««/R2»» = Run 2 (italic)
- ««R3:B,I»»text««/R3»» = Run 3 (bold + italic)
- ««R4:U»»text««/R4»» = Run 4 (underline)
- Additional: S=strike, SUB=subscript, SUP=superscript

CRITICAL RULES:
1. PRESERVE EXACT run structure - same number of runs
2. MAINTAIN run order - R0, R1, R2... must stay in sequence
3. KEEP format codes with appropriate translated content
4. TRANSLATE text inside markers, NOT the markers themselves

EXAMPLE:
Source: "««R0»»The ««/R0»»««R1:B»»quick««/R1»» ««R2»»brown ««/R2»»««R3:I»»fox««/R3»»"
Spanish: "««R0»»El ««/R0»»««R1:B»»rápido««/R1»» ««R2»»marrón ««/R2»»««R3:I»»zorro««/R3»»"

OUTPUT FORMAT:
<<<TRANSLATION_START_X>>>
[Translation with ALL run markers preserved exactly]
<<<TRANSLATION_END_X>>>

PASSAGES TO TRANSLATE:
"""
        
        for i, text in enumerate(texts, 1):
            prompt += f"\nPassage {i}:\n\"\"\"\n{text}\n\"\"\"\n"
        
        return prompt


def parse_formatted_response(response_text: str, expected_count: int, 
                           tier: str, logs: List[str]) -> List[str]:
    """Parse response with format markers preserved"""
    
    # First try delimiter parsing
    translations = []
    
    for i in range(1, expected_count + 1):
        start_marker = f"<<<TRANSLATION_START_{i}>>>"
        end_marker = f"<<<TRANSLATION_END_{i}>>>"
        
        start_idx = response_text.find(start_marker)
        end_idx = response_text.find(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            start_idx += len(start_marker)
            translation = response_text[start_idx:end_idx].strip()
            translations.append(translation)
        else:
            logs.append(f"[PARSE WARNING] Missing translation {i}")
            translations.append("")
    
    # If we got all translations, return them
    if len(translations) == expected_count:
        return translations
    
    # Fallback to other parsing methods
    logs.append("[PARSE] Delimiter parsing incomplete, trying fallback")
    return parse_structured_response(response_text, expected_count, logs)


# Integration points for main.py:

# 1. Add a configuration option to enable enhanced mode
ENABLE_FORMAT_PRESERVATION = True  # Can be set via environment variable

# 2. Modify the translate endpoint to use enhanced version
@app.post("/api/translate/enhanced", response_model=TranslateResponse)
async def translate_document_enhanced(request: TranslateRequest):
    """Enhanced translation endpoint with format preservation"""
    # ... validation code ...
    
    # Use enhanced translation
    result = await translate_document_content_async_enhanced(
        file_bytes=file_data,
        file_name=request.fileName,
        language=request.language,
        model=request.model,
        api_key=request.apiKey,
        progress_id=progress_id
    )
    
    return result

# 3. Or modify existing endpoint to conditionally use enhanced version
async def translate_document(request: TranslateRequest):
    """Main translation endpoint"""
    # ... validation code ...
    
    if ENABLE_FORMAT_PRESERVATION:
        # Use enhanced version
        result = await translate_document_content_async_enhanced(...)
    else:
        # Use original version
        result = await translate_document_content_async(...)
    
    return result
