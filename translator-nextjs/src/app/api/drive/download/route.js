import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';


export async function GET(request) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const fileId = searchParams.get('fileId');
    const mimeType = searchParams.get('mimeType');
    
    if (!fileId) {
      return NextResponse.json(
        { error: 'File ID required' },
        { status: 400 }
      );
    }
    
    const cookieStore = cookies();
    const tokensCookie = cookieStore.get('drive_tokens');
    
    if (!tokensCookie) {
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      );
    }
    
    const tokens = JSON.parse(tokensCookie.value);
    const oauth2Client = createOAuth2Client();
    oauth2Client.setCredentials(tokens);
    
    const drive = getDriveService(oauth2Client);
    
    // Google Workspace file types that need export
    const workspaceTypes = {
      'application/vnd.google-apps.document': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    };
    
    let response;
    
    if (workspaceTypes[mimeType]) {
      // Export Google Workspace file
      response = await drive.files.export(
        {
          fileId: fileId,
          mimeType: workspaceTypes[mimeType]
        },
        { responseType: 'arraybuffer' }
      );
    } else {
      // Download regular file
      response = await drive.files.get(
        {
          fileId: fileId,
          alt: 'media'
        },
        { responseType: 'arraybuffer' }
      );
    }
    
    // Return file as base64 (to send via JSON)
    const buffer = Buffer.from(response.data);
    const base64 = buffer.toString('base64');
    
    return NextResponse.json({
      data: base64,
      size: buffer.length
    });
  } catch (error) {
    console.error('Error downloading file:', error);
    return NextResponse.json(
      { error: 'Failed to download file: ' + error.message },
      { status: 500 }
    );
  }
}
