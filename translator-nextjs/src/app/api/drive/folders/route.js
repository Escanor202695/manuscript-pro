import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';


export async function GET() {
  try {
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
    
    const response = await drive.files.list({
      q: "mimeType='application/vnd.google-apps.folder' and trashed = false",
      fields: 'files(id, name)',
      pageSize: 100
    });
    
    return NextResponse.json({ folders: response.data.files || [] });
  } catch (error) {
    console.error('Error fetching folders:', error);
    return NextResponse.json(
      { error: 'Failed to fetch folders' },
      { status: 500 }
    );
  }
}
