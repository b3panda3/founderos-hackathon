import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'FounderOS — Multi-Agent AI Operating System',
  description: 'AI-powered operating system for startup founders with 6 specialized agents',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-dark-900">
        {children}
      </body>
    </html>
  )
}