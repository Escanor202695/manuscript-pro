import { NextResponse } from 'next/server';


export async function POST(request) {
  try {
    console.log('[TRANSLATE] Starting translation request');
    const body = await request.json();
    const { fileData, fileName, language, model, apiKey } = body;
    
    console.log('[TRANSLATE] Request params:', { fileName, language, model, hasApiKey: !!apiKey, dataSize: fileData?.length });
    
    if (!fileData || !fileName || !language || !model || !apiKey) {
      return NextResponse.json(
        { error: 'Missing required parameters' },
        { status: 400 }
      );
    }
    
    // Convert base64 back to buffer
    const fileBuffer = Buffer.from(fileData, 'base64');
    console.log('[TRANSLATE] File buffer created, size:', fileBuffer.length);
    
    // Translate document
    console.log('[TRANSLATE] Starting translation...');
    const result = await translateDocument(
      fileBuffer,
      fileName,
      language,
      model,
      apiKey,
      null // progress callback not used in server-side
    );
    
    console.log('[TRANSLATE] Translation complete, creating DOCX...');
    // Create new DOCX with translated content
    const translatedDocxBuffer = await createDocxFromContent(result.translatedContent);
    
    // Convert to base64 for transfer
    const translatedBase64 = translatedDocxBuffer.toString('base64');
    
    console.log('[TRANSLATE] Success, returning response');
    return NextResponse.json({
      translatedDocument: translatedBase64,
      logs: result.logs,
      stats: result.stats
    });
  } catch (error) {
    console.error('[TRANSLATE] Error:', error);
    console.error('[TRANSLATE] Stack:', error.stack);
    return NextResponse.json(
      { error: 'Translation failed: ' + error.message },
      { status: 500 }
    );
  }
}

// Add support for streaming progress updates
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const maxDuration = 300; // 5 minutes timeout
