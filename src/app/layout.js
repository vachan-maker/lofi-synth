import { AuthProvider } from './context/AuthContext'
import './globals.css'

export const metadata = {
  title: 'Lofi Synth',
  description: 'Your music app',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen transition-colors duration-500 bg-gradient-to-br from-rose-200 via-purple-100 to-white">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
