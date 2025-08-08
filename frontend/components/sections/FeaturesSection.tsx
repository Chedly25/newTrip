'use client'

import { motion } from 'framer-motion'

export function FeaturesSection() {
  return (
    <section className="section" style={{ background: 'white' }}>
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-8"
        >
          <h2 className="text-4xl font-bold mb-4" style={{ color: '#1f2937' }}>
            AI-Powered Travel Features
          </h2>
          <p className="text-xl" style={{ color: '#4b5563', maxWidth: '48rem', margin: '0 auto' }}>
            Experience France with cutting-edge AI technology that understands local culture and hidden gems.
          </p>
        </motion.div>
      </div>
    </section>
  )
}