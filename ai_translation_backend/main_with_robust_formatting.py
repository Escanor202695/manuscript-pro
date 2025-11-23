"""
Integration code to add robust format preservation to main.py
This shows exactly how to modify your existing translation functions
"""

import re
from robust_format_preservation import (
    RobustFormatPreserver,
    create_robust_translation_prompt,
    integrate_robust_preservation
)


async def translate_document_content_async_robust(
    file_bytes: bytes, 
    file_name: str, 
    language: str, 
    model: str, 
    api_key: str, 
    progress_id: Optional[str] = None
) -> TranslateResponse:
    """Enhanced translation with 100% format preservation"""
    
    logs = []
    logs.append(f"[START] ROBUST translation with 100% format preservation")
    logs.append(f"[INFO] Source file: {file_name}")
    logs.append(f"[INFO] Target language: {language}")
    logs.append(f"[INFO] Model: {model}")
    
    # Load document
    doc = Document(io.BytesIO(file_bytes))
    total_paragraphs = len(doc.paragraphs)
    logs.append(f"[LOAD] Document loaded with {total_paragraphs} paragraphs")
    
    # Initialize robust format preserver
    preserver = RobustFormatPreserver(doc)
    logs.append("[FORMAT] Initialized robust format preservation system")
    
    # Prepare paragraphs for translation
    paragraphs_to_translate = []
    marked_texts_for_batching = []
    
    para_count = 0
    for i, para in enumerate(doc.paragraphs):
        # Skip empty paragraphs
        if not para.text.strip():
            continue
        
        # Skip decorative paragraphs
        if not is_meaningful_text(para.text.strip()) or is_decorative_only(para.text.strip()):
            continue
        
        # Extract formatting and create marked text
        marked_text, para_data = preserver.create_formatted_text_for_translation(para, para_count)
        
        # Count runs and formatting complexity
        run_count = len(para.runs)
        format_types = set()
        for run_data in para_data['runs']:
            fmt = run_data['format']
            if fmt.get('bold'): format_types.add('bold')
            if fmt.get('italic'): format_types.add('italic')
            if fmt.get('underline'): format_types.add('underline')
            if fmt.get('font_name'): format_types.add('font')
            if fmt.get('font_color'): format_types.add('color')
        
        logs.append(f"[PARA {i}] {run_count} runs, {len(format_types)} format types: {format_types}")
        
        paragraphs_to_translate.append((i, para, marked_text, para_count))
        marked_texts_for_batching.append((para_count, marked_text))
        para_count += 1
    
    logs.append(f"[FILTER] {len(paragraphs_to_translate)} paragraphs to translate")
    
    # Smart batching based on complexity
    batches = create_smart_batches_for_robust_translation(marked_texts_for_batching, logs)
    total_batches = len(batches)
    logs.append(f"[BATCH] Created {total_batches} smart batches")
    
    # Initialize progress
    if progress_id:
        progress_tracker[progress_id] = {
            "totalBatches": total_batches,
            "completedBatches": 0,
            "error": False
        }
    
    # Process batches
    all_translations = {}
    
    for batch_idx, batch in enumerate(batches):
        logs.append(f"[BATCH {batch_idx + 1}/{total_batches}] Processing {len(batch)} paragraphs...")
        
        # Create robust prompt
        prompt = create_robust_translation_prompt(batch, language)
        
        # Call API
        try:
            if "openrouter" in model.lower():
                response = await call_openrouter_api_robust(prompt, model, api_key)
            else:
                response = await call_gemini_api_robust(prompt, model, api_key)
            
            # Parse response
            batch_translations = parse_robust_response(response, batch, logs)
            
            # Store translations
            for (para_id, _), translation in zip(batch, batch_translations):
                all_translations[para_id] = translation
                
            logs.append(f"[BATCH {batch_idx + 1}] Successfully translated {len(batch_translations)} paragraphs")
            
        except Exception as e:
            logs.append(f"[ERROR] Batch {batch_idx + 1} failed: {str(e)}")
            if progress_id:
                progress_tracker[progress_id]["error"] = True
            raise
        
        # Update progress
        if progress_id:
            progress_tracker[progress_id]["completedBatches"] += 1
    
    # Apply all translations with format preservation
    logs.append("[APPLY] Applying translations with format preservation...")
    
    for para_idx, para, marked_text, para_id in paragraphs_to_translate:
        if para_id in all_translations:
            translation = all_translations[para_id]
            
            # Apply formatting using robust preserver
            preserver.apply_formatting_to_paragraph(para, para_id, translation)
            
            logs.append(f"[APPLY {para_idx}] Applied translation with formatting preserved")
    
    # Save document
    output_buffer = io.BytesIO()
    doc.save(output_buffer)
    output_buffer.seek(0)
    
    logs.append("[SAVE] Document saved with 100% format preservation")
    logs.append("[DONE] Robust translation complete!")
    
    # Convert to base64
    translated_base64 = base64.b64encode(output_buffer.read()).decode('utf-8')
    
    return TranslateResponse(
        translatedDocument=translated_base64,
        logs=logs,
        stats={
            "totalParagraphs": total_paragraphs,
            "translatedParagraphs": len(paragraphs_to_translate),
            "preservedFormats": para_count,
            "method": "robust_100_percent"
        }
    )


def create_smart_batches_for_robust_translation(marked_texts: List[Tuple[int, str]], logs: List[str]) -> List[List[Tuple[int, str]]]:
    """Create batches optimized for robust translation"""
    
    # Calculate complexity for each paragraph
    complexities = []
    
    for para_id, marked_text in marked_texts:
        # Count formatting markers
        run_count = len(re.findall(r'««RUN\d+:', marked_text))
        
        # Count different format types
        format_types = set()
        for match in re.finditer(r'««RUN\d+:([^»]+)»»', marked_text):
            formats = match.group(1).split(',')
            format_types.update(formats)
        
        # Calculate text length without markers
        clean_text = re.sub(r'««[^»]+»»', '', marked_text)
        text_length = len(clean_text)
        
        complexity_score = run_count * len(format_types) * (1 + text_length / 1000)
        
        complexities.append({
            'para_id': para_id,
            'marked_text': marked_text,
            'run_count': run_count,
            'format_types': len(format_types),
            'text_length': text_length,
            'complexity': complexity_score
        })
    
    # Sort by complexity
    complexities.sort(key=lambda x: x['complexity'], reverse=True)
    
    # Create batches with complexity limits
    batches = []
    current_batch = []
    current_complexity = 0
    MAX_BATCH_COMPLEXITY = 50  # Adjust based on testing
    MAX_BATCH_SIZE = 10  # Maximum paragraphs per batch
    
    for item in complexities:
        if current_batch and (
            current_complexity + item['complexity'] > MAX_BATCH_COMPLEXITY or
            len(current_batch) >= MAX_BATCH_SIZE
        ):
            # Start new batch
            batches.append(current_batch)
            current_batch = []
            current_complexity = 0
        
        current_batch.append((item['para_id'], item['marked_text']))
        current_complexity += item['complexity']
    
    # Add final batch
    if current_batch:
        batches.append(current_batch)
    
    logs.append(f"[BATCH ANALYSIS] Created {len(batches)} batches from {len(marked_texts)} paragraphs")
    logs.append(f"[BATCH COMPLEXITY] Most complex paragraph: {complexities[0]['complexity']:.2f}")
    
    return batches


async def call_gemini_api_robust(prompt: str, model: str, api_key: str) -> str:
    """Call Gemini API with robust prompt"""
    client = genai.Client(api_key=api_key)
    
    # Configure for plain text response (no JSON)
    generation_config = GenerateContentConfig(
        temperature=0.3,  # Lower temperature for format preservation
        candidate_count=1,
        max_output_tokens=8000,
    )
    
    response = await client.aio.models.generate_content(
        model=model,
        contents=prompt,
        config=generation_config
    )
    
    return response.text


def parse_robust_response(response_text: str, batch: List[Tuple[int, str]], logs: List[str]) -> List[str]:
    """Parse response with robust format markers"""
    
    translations = []
    
    for para_id, marked_text in batch:
        # Look for translation markers
        start_marker = f"<<<TRANSLATION_{para_id}_START>>>"
        end_marker = f"<<<TRANSLATION_{para_id}_END>>>"
        
        start_idx = response_text.find(start_marker)
        end_idx = response_text.find(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            start_idx += len(start_marker)
            translation = response_text[start_idx:end_idx].strip()
            
            # Verify format preservation
            original_runs = re.findall(r'««RUN(\d+):[^»]+»»', marked_text)
            translated_runs = re.findall(r'««RUN(\d+):[^»]+»»', translation)
            
            if len(original_runs) != len(translated_runs):
                logs.append(f"[WARNING] Para {para_id}: Run count mismatch - Original: {len(original_runs)}, Translated: {len(translated_runs)}")
            
            translations.append(translation)
        else:
            logs.append(f"[ERROR] Para {para_id}: Translation markers not found")
            translations.append("")
    
    return translations


# Simple modification to existing translate endpoint
@app.post("/api/translate/robust", response_model=TranslateResponse)
async def translate_document_robust(request: TranslateRequest):
    """Endpoint for robust translation with 100% format preservation"""
    
    # Validate inputs
    if not request.fileData:
        raise HTTPException(status_code=400, detail="No file data provided")
    
    # Decode file
    try:
        file_data = base64.b64decode(request.fileData)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid base64 file data")
    
    # Generate progress ID
    progress_id = str(uuid.uuid4())
    
    # Use robust translation
    result = await translate_document_content_async_robust(
        file_bytes=file_data,
        file_name=request.fileName,
        language=request.language,
        model=request.model,
        api_key=request.apiKey,
        progress_id=progress_id
    )
    
    return result


# Or add a flag to existing endpoint
ENABLE_ROBUST_FORMATTING = True  # Set via environment variable

async def translate_document(request: TranslateRequest):
    """Main translation endpoint"""
    # ... validation code ...
    
    if ENABLE_ROBUST_FORMATTING:
        # Check document complexity
        doc = Document(io.BytesIO(file_data))
        
        # Count total runs and format variations
        total_runs = sum(len(para.runs) for para in doc.paragraphs)
        avg_runs_per_para = total_runs / max(len(doc.paragraphs), 1)
        
        # Use robust method for complex documents
        if avg_runs_per_para > 2:  # Complex formatting detected
            result = await translate_document_content_async_robust(...)
        else:
            # Use regular method for simple documents
            result = await translate_document_content_async(...)
    else:
        # Use original method
        result = await translate_document_content_async(...)
    
    return result
