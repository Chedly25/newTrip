'use client'

import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { 
  SparklesIcon, 
  PlayIcon,
  GlobeEuropeAfricaIcon,
  ChatBubbleLeftRightIcon,
  CameraIcon,
  CurrencyEuroIcon 
} from '@heroicons/react/24/outline'

const features = [
  {
    icon: ChatBubbleLeftRightIcon,
    name: 'AI Travel Companion',
    description: 'Your personal French travel expert',
    color: 'from-blue-500 to-cyan-500'
  },
  {
    icon: CameraIcon,
    name: 'Photo Recognition',
    description: 'Identify places instantly',
    color: 'from-purple-500 to-pink-500'
  },
  {
    icon: CurrencyEuroIcon,
    name: 'Smart Budgeting',
    description: 'AI-powered expense tracking',
    color: 'from-orange-500 to-red-500'
  },
  {
    icon: GlobeEuropeAfricaIcon,
    name: 'Cultural Insights',
    description: 'Deep local knowledge',
    color: 'from-green-500 to-emerald-500'
  }
]

const testimonialQuotes = [
  "This AI changed how I travel in France!",
  "The local insights are incredible",
  "Best travel companion I've ever had",
  "Discovered hidden gems everywhere"
]

export function HeroSection() {
  const [currentQuote, setCurrentQuote] = useState(0)
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentQuote((prev) => (prev + 1) % testimonialQuotes.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({
        x: e.clientX / window.innerWidth,
        y: e.clientY / window.innerHeight
      })
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 10,
        duration: 0.8
      }
    }
  }

  const floatingVariants = {
    hidden: { opacity: 0, scale: 0 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        type: "spring",
        stiffness: 260,
        damping: 20,
        delay: 1.5
      }
    }
  }

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Gradient Orbs */}
        <motion.div
          className="absolute -top-40 -left-40 w-80 h-80 bg-gradient-to-r from-primary-400/30 to-secondary-400/30 rounded-full blur-3xl"
          animate={{
            x: mousePosition.x * 100,
            y: mousePosition.y * 50,
            rotate: 360
          }}
          transition={{
            type: "spring",
            stiffness: 50,
            damping: 30,
            rotate: { duration: 20, repeat: Infinity, ease: "linear" }
          }}
        />
        <motion.div
          className="absolute -bottom-40 -right-40 w-80 h-80 bg-gradient-to-r from-accent-400/30 to-primary-400/30 rounded-full blur-3xl"
          animate={{
            x: -mousePosition.x * 80,
            y: -mousePosition.y * 60,
            rotate: -360
          }}
          transition={{
            type: "spring",
            stiffness: 50,
            damping: 30,
            rotate: { duration: 25, repeat: Infinity, ease: "linear" }
          }}
        />
        
        {/* Floating Shapes */}
        {Array.from({ length: 6 }).map((_, i) => (
          <motion.div
            key={i}
            className={`absolute w-4 h-4 bg-gradient-to-r ${
              i % 3 === 0 ? 'from-primary-400 to-secondary-400' :
              i % 3 === 1 ? 'from-secondary-400 to-accent-400' :
              'from-accent-400 to-primary-400'
            } rounded-full opacity-60`}
            style={{
              left: `${20 + i * 15}%`,
              top: `${30 + i * 10}%`
            }}
            animate={{
              y: [0, -20, 0],
              rotate: [0, 180, 360],
              scale: [1, 1.2, 1]
            }}
            transition={{
              duration: 3 + i * 0.5,
              repeat: Infinity,
              delay: i * 0.2
            }}
          />
        ))}
      </div>

      <div className="container-premium relative z-10">
        <motion.div
          initial="hidden"
          animate="visible"
          variants={containerVariants}
          className="text-center space-y-8"
        >
          {/* Badge */}
          <motion.div variants={itemVariants} className="flex justify-center">
            <motion.div
              className="inline-flex items-center px-4 py-2 bg-white/80 backdrop-blur-lg border border-white/30 rounded-full shadow-premium"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <SparklesIcon className="w-4 h-4 text-primary-500 mr-2" />
              <span className="text-sm font-semibold gradient-text">
                Powered by Advanced AI
              </span>
              <motion.div
                className="ml-2 w-2 h-2 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full"
                animate={{ scale: [1, 1.5, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
            </motion.div>
          </motion.div>

          {/* Main Heading */}
          <motion.div variants={itemVariants} className="space-y-4">
            <motion.h1 
              className="text-5xl sm:text-6xl lg:text-7xl font-display font-bold text-gray-900 leading-tight"
              initial={{ scale: 0.5 }}
              animate={{ scale: 1 }}
              transition={{ 
                type: "spring", 
                stiffness: 260, 
                damping: 20,
                delay: 0.5
              }}
            >
              Experience{' '}
              <motion.span
                className="gradient-text relative"
                animate={{ backgroundPosition: ['0%', '100%', '0%'] }}
                transition={{ duration: 8, repeat: Infinity }}
                style={{ backgroundSize: '400%' }}
              >
                France
                <motion.div
                  className="absolute -top-2 -right-2 w-6 h-6"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                >
                  <SparklesIcon className="w-6 h-6 text-accent-500" />
                </motion.div>
              </motion.span>
              <br />
              Like Never Before
            </motion.h1>
            
            <motion.p 
              className="text-xl lg:text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed"
              variants={itemVariants}
            >
              Your AI-powered travel companion that understands France's culture, 
              speaks the language, and reveals hidden gems only locals know about.
            </motion.p>
          </motion.div>

          {/* Rotating Testimonial */}
          <motion.div 
            variants={itemVariants}
            className="flex justify-center"
          >
            <div className="relative h-16 flex items-center">
              <motion.div
                key={currentQuote}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="text-lg font-medium text-gray-700 italic"
              >
                "{testimonialQuotes[currentQuote]}"
              </motion.div>
            </div>
          </motion.div>

          {/* CTA Buttons */}
          <motion.div 
            variants={itemVariants}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4"
          >
            <motion.div
              whileHover={{ scale: 1.05, boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)" }}
              whileTap={{ scale: 0.95 }}
              className="relative group"
            >
              <Link href="/chat" className="btn-primary text-lg px-8 py-4 relative z-10">
                Start Your Journey
                <motion.svg 
                  className="ml-2 w-5 h-5"
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
              
              {/* Animated Border */}
              <motion.div
                className="absolute inset-0 rounded-xl bg-gradient-to-r from-primary-400 via-secondary-400 to-accent-400 p-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                animate={{ rotate: 360 }}
                transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
              />
            </motion.div>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="group flex items-center px-6 py-3 text-lg font-semibold text-gray-700 hover:text-primary-600 bg-white/80 backdrop-blur-lg border border-white/30 rounded-xl shadow-sm hover:shadow-premium transition-all duration-300"
            >
              <motion.div
                className="relative p-2 mr-3 bg-gradient-to-r from-gray-100 to-gray-200 rounded-lg group-hover:from-primary-500 group-hover:to-secondary-500 transition-all duration-300"
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.5 }}
              >
                <PlayIcon className="w-5 h-5 text-gray-600 group-hover:text-white" />
              </motion.div>
              Watch Demo
            </motion.button>
          </motion.div>

          {/* Feature Cards */}
          <motion.div 
            variants={itemVariants}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 pt-16"
          >
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <motion.div
                  key={feature.name}
                  variants={floatingVariants}
                  custom={index}
                  whileHover={{ 
                    y: -10,
                    scale: 1.05,
                    transition: { type: "spring", stiffness: 400 }
                  }}
                  className="group relative p-6 bg-white/80 backdrop-blur-lg border border-white/30 rounded-2xl shadow-premium hover:shadow-premium-lg transition-all duration-300"
                >
                  <motion.div
                    className={`inline-flex p-3 bg-gradient-to-r ${feature.color} rounded-xl mb-4 text-white group-hover:scale-110 transition-transform duration-300`}
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.6 }}
                  >
                    <Icon className="w-6 h-6" />
                  </motion.div>
                  
                  <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors duration-300">
                    {feature.name}
                  </h3>
                  
                  <p className="text-sm text-gray-600 group-hover:text-gray-700 transition-colors duration-300">
                    {feature.description}
                  </p>

                  {/* Hover Glow Effect */}
                  <motion.div
                    className="absolute inset-0 rounded-2xl bg-gradient-to-r from-primary-500/20 to-secondary-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                    layoutId={`glow-${index}`}
                  />
                </motion.div>
              )
            })}
          </motion.div>
        </motion.div>
      </div>

      {/* Scroll Indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2 }}
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="flex flex-col items-center text-gray-400"
        >
          <span className="text-sm font-medium mb-2">Scroll to explore</span>
          <motion.div
            className="w-6 h-10 border-2 border-gray-300 rounded-full p-1"
            whileHover={{ borderColor: "rgb(59 130 246)" }}
          >
            <motion.div
              className="w-1 h-3 bg-gradient-to-b from-primary-500 to-secondary-500 rounded-full mx-auto"
              animate={{ y: [0, 12, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            />
          </motion.div>
        </motion.div>
      </motion.div>
    </section>
  )
}