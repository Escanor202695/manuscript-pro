import './globals.css'

export const metadata = {
  title: 'Drive Document Translator',
  description: 'Translate documents from Google Drive using AI',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
