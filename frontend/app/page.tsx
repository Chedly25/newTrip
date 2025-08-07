'use client'

import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'
import { HeroSection } from '@/components/sections/HeroSection'
import { FeaturesSection } from '@/components/sections/FeaturesSection'
import { ServicesSection } from '@/components/sections/ServicesSection'
import { TestimonialsSection } from '@/components/sections/TestimonialsSection'
import { CTASection } from '@/components/sections/CTASection'
import { StatsSection } from '@/components/sections/StatsSection'

export default function HomePage() {
  const [heroRef, heroInView] = useInView({ threshold: 0.1, triggerOnce: true })
  const [featuresRef, featuresInView] = useInView({ threshold: 0.1, triggerOnce: true })
  const [servicesRef, servicesInView] = useInView({ threshold: 0.1, triggerOnce: true })
  const [statsRef, statsInView] = useInView({ threshold: 0.1, triggerOnce: true })
  const [testimonialsRef, testimonialsInView] = useInView({ threshold: 0.1, triggerOnce: true })
  const [ctaRef, ctaInView] = useInView({ threshold: 0.1, triggerOnce: true })

  const sectionVariants = {
    hidden: { 
      opacity: 0, 
      y: 50 
    },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: {
        duration: 0.8,
        ease: [0.25, 0.1, 0.25, 1],
      }
    }
  }

  return (
    <div className="relative overflow-hidden">
      {/* Hero Section */}
      <motion.section
        ref={heroRef}
        initial="hidden"
        animate={heroInView ? "visible" : "hidden"}
        variants={sectionVariants}
        className="relative"
      >
        <HeroSection />
      </motion.section>

      {/* Features Section */}
      <motion.section
        ref={featuresRef}
        initial="hidden"
        animate={featuresInView ? "visible" : "hidden"}
        variants={sectionVariants}
        className="relative"
      >
        <FeaturesSection />
      </motion.section>

      {/* Services Section */}
      <motion.section
        ref={servicesRef}
        initial="hidden"
        animate={servicesInView ? "visible" : "hidden"}
        variants={sectionVariants}
        className="relative"
      >
        <ServicesSection />
      </motion.section>

      {/* Stats Section */}
      <motion.section
        ref={statsRef}
        initial="hidden"
        animate={statsInView ? "visible" : "hidden"}
        variants={sectionVariants}
        className="relative"
      >
        <StatsSection />
      </motion.section>

      {/* Testimonials Section */}
      <motion.section
        ref={testimonialsRef}
        initial="hidden"
        animate={testimonialsInView ? "visible" : "hidden"}
        variants={sectionVariants}
        className="relative"
      >
        <TestimonialsSection />
      </motion.section>

      {/* CTA Section */}
      <motion.section
        ref={ctaRef}
        initial="hidden"
        animate={ctaInView ? "visible" : "hidden"}
        variants={sectionVariants}
        className="relative"
      >
        <CTASection />
      </motion.section>

      {/* Floating Action Button */}
      <motion.div
        className="fixed bottom-8 right-8 z-50"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 2, type: "spring", stiffness: 260, damping: 20 }}
      >
        <button className="group relative p-4 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-2xl shadow-premium hover:shadow-premium-lg transition-all duration-300 hover:-translate-y-1">
          <motion.div
            className="absolute inset-0 rounded-2xl bg-gradient-to-r from-primary-400 to-primary-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
            layoutId="fab-bg"
          />
          <motion.svg
            className="relative w-6 h-6"
            fill="none"
            strokeWidth={2}
            stroke="currentColor"
            viewBox="0 0 24 24"
            whileHover={{ rotate: 90 }}
            transition={{ duration: 0.3 }}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h8m-8 0V8m0 4v4m0-4H4m4 0h4" />
          </motion.svg>
          
          {/* Ripple Effect */}
          <div className="absolute inset-0 rounded-2xl bg-white/20 scale-0 group-active:scale-100 transition-transform duration-200" />
          
          {/* Tooltip */}
          <div className="absolute bottom-full right-0 mb-3 px-3 py-1 bg-gray-900 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
            Start Planning
          </div>
        </button>
      </motion.div>

      {/* Scroll Progress Indicator */}
      <motion.div
        className="fixed top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary-500 via-secondary-500 to-accent-500 transform-gpu origin-left z-50"
        style={{ scaleX: 0 }}
        whileInView={{ scaleX: 1 }}
        transition={{ duration: 0.3 }}
      />
    </div>
  )
}