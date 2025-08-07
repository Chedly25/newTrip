'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  Bars3Icon, 
  XMarkIcon,
  GlobeEuropeAfricaIcon,
  ChatBubbleLeftRightIcon,
  CameraIcon,
  PencilSquareIcon,
  CurrencyEuroIcon,
  CalendarDaysIcon,
  LanguageIcon,
  ShieldCheckIcon,
  BuildingStorefrontIcon,
  UserCircleIcon
} from '@heroicons/react/24/outline'

const navigation = [
  { 
    name: 'Features', 
    href: '#features',
    icon: GlobeEuropeAfricaIcon,
    description: 'AI-powered travel tools'
  },
  { 
    name: 'Chat', 
    href: '/chat',
    icon: ChatBubbleLeftRightIcon,
    description: 'Talk to your AI companion'
  },
  { 
    name: 'Photo Analysis', 
    href: '/photos',
    icon: CameraIcon,
    description: 'Identify places instantly'
  },
  { 
    name: 'Content Creator', 
    href: '/content',
    icon: PencilSquareIcon,
    description: 'Generate travel content'
  },
  { 
    name: 'Budget Tracker', 
    href: '/budget',
    icon: CurrencyEuroIcon,
    description: 'Smart expense management'
  },
]

const services = [
  { 
    name: 'Events', 
    href: '/events',
    icon: CalendarDaysIcon,
    description: 'Discover local events'
  },
  { 
    name: 'Translation', 
    href: '/translation',
    icon: LanguageIcon,
    description: 'Smart cultural translation'
  },
  { 
    name: 'Safety', 
    href: '/safety',
    icon: ShieldCheckIcon,
    description: 'Travel risk assessment'
  },
  { 
    name: 'Food Guide', 
    href: '/food',
    icon: BuildingStorefrontIcon,
    description: 'Restaurant recommendations'
  },
]

export function Navigation() {
  const [isOpen, setIsOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const pathname = usePathname()

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navVariants = {
    hidden: { y: -100, opacity: 0 },
    visible: { 
      y: 0, 
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 30,
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { y: -20, opacity: 0 },
    visible: { 
      y: 0, 
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 30
      }
    }
  }

  const mobileMenuVariants = {
    hidden: {
      opacity: 0,
      scale: 0.95,
      transition: {
        duration: 0.2
      }
    },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 30,
        staggerChildren: 0.1
      }
    }
  }

  return (
    <motion.nav
      initial="hidden"
      animate="visible"
      variants={navVariants}
      className={`fixed top-0 left-0 right-0 z-40 transition-all duration-300 ${
        scrolled 
          ? 'bg-white/95 backdrop-blur-xl border-b border-white/20 shadow-premium' 
          : 'bg-transparent'
      }`}
    >
      <div className="container-premium">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <motion.div variants={itemVariants} className="flex items-center">
            <Link href="/" className="group flex items-center space-x-3">
              <motion.div
                className="relative p-2 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-xl"
                whileHover={{ scale: 1.05, rotate: 5 }}
                whileTap={{ scale: 0.95 }}
              >
                <GlobeEuropeAfricaIcon className="w-8 h-8 text-white" />
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-secondary-400 to-accent-400 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                  layoutId="logo-bg"
                />
              </motion.div>
              <div className="hidden sm:block">
                <h1 className="text-2xl font-display font-bold gradient-text">
                  Wanderlog AI
                </h1>
                <p className="text-sm text-gray-500 -mt-1">Premium Travel Companion</p>
              </div>
            </Link>
          </motion.div>

          {/* Desktop Navigation */}
          <motion.div 
            variants={itemVariants}
            className="hidden lg:flex items-center space-x-1"
          >
            {/* Features Dropdown */}
            <div className="relative group">
              <button className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 rounded-xl hover:bg-primary-50/50 transition-all duration-200">
                Features
                <motion.svg 
                  className="ml-1 w-4 h-4"
                  fill="none" 
                  strokeWidth={2} 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                  whileHover={{ rotate: 180 }}
                  transition={{ duration: 0.2 }}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                </motion.svg>
              </button>
              
              {/* Dropdown Menu */}
              <AnimatePresence>
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                  className="absolute top-full left-0 mt-2 w-80 origin-top-left opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto transition-all duration-200"
                >
                  <div className="bg-white/95 backdrop-blur-xl border border-white/20 rounded-2xl shadow-premium p-4">
                    <div className="grid grid-cols-1 gap-2">
                      {navigation.map((item) => {
                        const Icon = item.icon
                        return (
                          <Link
                            key={item.name}
                            href={item.href}
                            className="group flex items-start p-3 rounded-xl hover:bg-primary-50/50 transition-all duration-200"
                          >
                            <div className="p-2 bg-gradient-to-br from-primary-100 to-secondary-100 rounded-lg group-hover:from-primary-500 group-hover:to-secondary-500 transition-all duration-200">
                              <Icon className="w-5 h-5 text-primary-600 group-hover:text-white" />
                            </div>
                            <div className="ml-3">
                              <p className="text-sm font-semibold text-gray-900 group-hover:text-primary-600">
                                {item.name}
                              </p>
                              <p className="text-xs text-gray-500">
                                {item.description}
                              </p>
                            </div>
                          </Link>
                        )
                      })}
                    </div>
                  </div>
                </motion.div>
              </AnimatePresence>
            </div>

            {/* Services Dropdown */}
            <div className="relative group">
              <button className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 rounded-xl hover:bg-primary-50/50 transition-all duration-200">
                Services
                <motion.svg 
                  className="ml-1 w-4 h-4"
                  fill="none" 
                  strokeWidth={2} 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                  whileHover={{ rotate: 180 }}
                  transition={{ duration: 0.2 }}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                </motion.svg>
              </button>
              
              <AnimatePresence>
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                  className="absolute top-full left-0 mt-2 w-80 origin-top-left opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto transition-all duration-200"
                >
                  <div className="bg-white/95 backdrop-blur-xl border border-white/20 rounded-2xl shadow-premium p-4">
                    <div className="grid grid-cols-1 gap-2">
                      {services.map((item) => {
                        const Icon = item.icon
                        return (
                          <Link
                            key={item.name}
                            href={item.href}
                            className="group flex items-start p-3 rounded-xl hover:bg-secondary-50/50 transition-all duration-200"
                          >
                            <div className="p-2 bg-gradient-to-br from-secondary-100 to-accent-100 rounded-lg group-hover:from-secondary-500 group-hover:to-accent-500 transition-all duration-200">
                              <Icon className="w-5 h-5 text-secondary-600 group-hover:text-white" />
                            </div>
                            <div className="ml-3">
                              <p className="text-sm font-semibold text-gray-900 group-hover:text-secondary-600">
                                {item.name}
                              </p>
                              <p className="text-xs text-gray-500">
                                {item.description}
                              </p>
                            </div>
                          </Link>
                        )
                      })}
                    </div>
                  </div>
                </motion.div>
              </AnimatePresence>
            </div>

            <Link 
              href="/about"
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-primary-600 rounded-xl hover:bg-primary-50/50 transition-all duration-200"
            >
              About
            </Link>
          </motion.div>

          {/* CTA Buttons */}
          <motion.div 
            variants={itemVariants}
            className="hidden sm:flex items-center space-x-4"
          >
            <Link 
              href="/login"
              className="px-4 py-2 text-sm font-semibold text-gray-700 hover:text-primary-600 rounded-xl hover:bg-primary-50/50 transition-all duration-200"
            >
              Sign In
            </Link>
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Link href="/register" className="btn-primary">
                Get Started
                <motion.svg 
                  className="ml-2 w-4 h-4"
                  fill="none" 
                  strokeWidth={2} 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                  whileHover={{ x: 5 }}
                  transition={{ type: "spring", stiffness: 400 }}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 8.25L21 12m0 0l-3.75 3.75M21 12H3" />
                </motion.svg>
              </Link>
            </motion.div>
          </motion.div>

          {/* Mobile menu button */}
          <motion.button
            variants={itemVariants}
            onClick={() => setIsOpen(!isOpen)}
            className="lg:hidden p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-xl transition-all duration-200"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <AnimatePresence mode="wait">
              {isOpen ? (
                <motion.div
                  key="close"
                  initial={{ rotate: 0 }}
                  animate={{ rotate: 90 }}
                  exit={{ rotate: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <XMarkIcon className="w-6 h-6" />
                </motion.div>
              ) : (
                <motion.div
                  key="open"
                  initial={{ rotate: 90 }}
                  animate={{ rotate: 0 }}
                  exit={{ rotate: 90 }}
                  transition={{ duration: 0.2 }}
                >
                  <Bars3Icon className="w-6 h-6" />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.button>
        </div>
      </div>

      {/* Mobile Navigation */}
      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 bg-black/20 backdrop-blur-sm z-30 lg:hidden"
              onClick={() => setIsOpen(false)}
            />
            <motion.div
              initial="hidden"
              animate="visible"
              exit="hidden"
              variants={mobileMenuVariants}
              className="absolute top-full left-0 right-0 bg-white/95 backdrop-blur-xl border-t border-white/20 shadow-premium lg:hidden"
            >
              <div className="container-premium py-6">
                <div className="space-y-6">
                  {/* Features */}
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 mb-3">Features</h3>
                    <div className="space-y-2">
                      {navigation.map((item) => {
                        const Icon = item.icon
                        return (
                          <motion.div
                            key={item.name}
                            variants={itemVariants}
                          >
                            <Link
                              href={item.href}
                              className="flex items-center p-3 rounded-xl hover:bg-primary-50 transition-all duration-200"
                              onClick={() => setIsOpen(false)}
                            >
                              <Icon className="w-5 h-5 text-primary-600" />
                              <span className="ml-3 text-sm font-medium text-gray-900">
                                {item.name}
                              </span>
                            </Link>
                          </motion.div>
                        )
                      })}
                    </div>
                  </div>

                  {/* Services */}
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 mb-3">Services</h3>
                    <div className="space-y-2">
                      {services.map((item) => {
                        const Icon = item.icon
                        return (
                          <motion.div
                            key={item.name}
                            variants={itemVariants}
                          >
                            <Link
                              href={item.href}
                              className="flex items-center p-3 rounded-xl hover:bg-secondary-50 transition-all duration-200"
                              onClick={() => setIsOpen(false)}
                            >
                              <Icon className="w-5 h-5 text-secondary-600" />
                              <span className="ml-3 text-sm font-medium text-gray-900">
                                {item.name}
                              </span>
                            </Link>
                          </motion.div>
                        )
                      })}
                    </div>
                  </div>

                  {/* Auth Buttons */}
                  <div className="pt-4 border-t border-gray-200 space-y-3">
                    <Link
                      href="/login"
                      className="block w-full px-4 py-3 text-center text-sm font-semibold text-gray-700 bg-gray-50 rounded-xl hover:bg-gray-100 transition-all duration-200"
                      onClick={() => setIsOpen(false)}
                    >
                      Sign In
                    </Link>
                    <Link
                      href="/register"
                      className="block w-full btn-primary text-center"
                      onClick={() => setIsOpen(false)}
                    >
                      Get Started
                    </Link>
                  </div>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </motion.nav>
  )
}