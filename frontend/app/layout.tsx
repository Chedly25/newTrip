import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { Navigation } from '@/components/navigation/Navigation'
import { Footer } from '@/components/layout/Footer'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Wanderlog AI - Premium Travel Companion',
  description: 'Experience France like never before with our AI-powered travel companion. Get personalized recommendations, smart translations, and expert local insights.',
  keywords: 'travel, AI, France, recommendations, itinerary, local insights, premium travel app',
  authors: [{ name: 'Wanderlog AI Team' }],
  creator: 'Wanderlog AI',
  publisher: 'Wanderlog AI',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://wanderlog-ai.herokuapp.com'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'Wanderlog AI - Premium Travel Companion',
    description: 'Experience France like never before with our AI-powered travel companion.',
    url: 'https://wanderlog-ai.herokuapp.com',
    siteName: 'Wanderlog AI',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Wanderlog AI - Premium Travel Companion',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Wanderlog AI - Premium Travel Companion',
    description: 'Experience France like never before with our AI-powered travel companion.',
    images: ['/twitter-image.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-site-verification-code',
  },
}

interface RootLayoutProps {
  children: React.ReactNode
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html 
      lang="en" 
      className={`${inter.variable} ${jetbrainsMono.variable} scroll-smooth`}
      suppressHydrationWarning
    >
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#0ea5e9" />
        <meta name="color-scheme" content="light dark" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
      </head>
      <body className="font-sans antialiased bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 min-h-screen">
        <Providers>
          {/* Background Gradient Animation */}
          <div className="fixed inset-0 overflow-hidden pointer-events-none">
            <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-primary-100/20 via-secondary-100/20 to-accent-100/20 rotate-12 animate-float"></div>
            <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-accent-100/20 via-primary-100/20 to-secondary-100/20 -rotate-12 animate-float" style={{ animationDelay: '2s' }}></div>
          </div>
          
          {/* Main Content */}
          <div className="relative z-10">
            <Navigation />
            <main className="min-h-screen">
              {children}
            </main>
            <Footer />
          </div>
          
          {/* Floating Elements for Premium Feel */}
          <div className="fixed top-20 left-10 w-4 h-4 bg-gradient-to-r from-primary-400 to-secondary-400 rounded-full opacity-30 animate-float pointer-events-none"></div>
          <div className="fixed top-40 right-16 w-3 h-3 bg-gradient-to-r from-accent-400 to-primary-400 rounded-full opacity-40 animate-float pointer-events-none" style={{ animationDelay: '1s' }}></div>
          <div className="fixed bottom-32 left-20 w-2 h-2 bg-gradient-to-r from-secondary-400 to-accent-400 rounded-full opacity-50 animate-float pointer-events-none" style={{ animationDelay: '3s' }}></div>
        </Providers>
      </body>
    </html>
  )
}