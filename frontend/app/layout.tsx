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
      <body>
        <Providers>
          {/* Background floating elements */}
          <div style={{ position: 'fixed', inset: '0', overflow: 'hidden', pointerEvents: 'none', zIndex: 1 }}>
            <div className="animate-float" style={{ 
              position: 'absolute', 
              top: '20%', 
              left: '10%', 
              width: '1rem', 
              height: '1rem', 
              background: 'linear-gradient(45deg, #3b82f6, #8b5cf6)', 
              borderRadius: '50%', 
              opacity: 0.3 
            }}></div>
            <div className="animate-float" style={{ 
              position: 'absolute', 
              top: '40%', 
              right: '16%', 
              width: '0.75rem', 
              height: '0.75rem', 
              background: 'linear-gradient(45deg, #f59e0b, #3b82f6)', 
              borderRadius: '50%', 
              opacity: 0.4,
              animationDelay: '1s'
            }}></div>
          </div>
          
          {/* Main Content */}
          <div style={{ position: 'relative', zIndex: 10 }}>
            <Navigation />
            <main style={{ minHeight: '100vh' }}>
              {children}
            </main>
            <Footer />
          </div>
        </Providers>
      </body>
    </html>
  )
}