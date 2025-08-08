'use client'

import { motion } from 'framer-motion'

export function ServicesSection() {
  return (
    <section className="section-premium bg-gradient-to-br from-blue-50 to-indigo-50">
      <div className="container-premium">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl font-display font-bold text-gray-900 mb-4">
            Premium Services
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Comprehensive travel services powered by advanced AI technology.
          </p>
        </motion.div>
      </div>
    </section>
  )
}