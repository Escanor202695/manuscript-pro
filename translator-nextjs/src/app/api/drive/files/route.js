import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';


export async function GET(request) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const folderId = searchParams.get('folderId');
    const driveLink = searchParams.get('driveLink');
    
    let actualFolderId = folderId;
    
    // If drive link provided, extract ID
    if (driveLink) {
      const extracted = extractDriveId(driveLink);
      actualFolderId = extracted.id;
    }
    
    if (!actualFolderId) {
      return NextResponse.json(
        { error: 'Folder ID or Drive link required' },
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
    
    // First, check if it's a folder or file
    const metadata = await drive.files.get({
      fileId: actualFolderId,
      fields: 'id, name, mimeType'
    });
    
    const isFolder = metadata.data.mimeType === 'application/vnd.google-apps.folder';
    
    if (!isFolder) {
      // It's a single file
      return NextResponse.json({
        type: 'file',
        file: {
          id: metadata.data.id,
          name: metadata.data.name,
          mimeType: metadata.data.mimeType
        }
      });
    }
    
    // It's a folder, get files in it
    const supportedTypes = [
      'application/vnd.google-apps.document',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/pdf'
    ];
    
    const query = `'${actualFolderId}' in parents and trashed = false and (${supportedTypes.map(type => `mimeType='${type}'`).join(' or ')})`;
    
    const response = await drive.files.list({
      q: query,
      fields: 'files(id, name, mimeType, size, modifiedTime)',
      pageSize: 100
    });
    
    return NextResponse.json({
      type: 'folder',
      folderName: metadata.data.name,
      files: response.data.files || []
    });
  } catch (error) {
    console.error('Error fetching files:', error);
    return NextResponse.json(
      { error: 'Failed to fetch files: ' + error.message },
      { status: 500 }
    );
  }
}
