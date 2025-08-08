'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'

export function CTASection() {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <section className="section-premium bg-gradient-to-br from-blue-600 via-purple-700 to-indigo-800 text-white relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          animate={{
            x: [-100, 100, -100],
            y: [-50, 50, -50],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute top-20 left-20 w-64 h-64 bg-blue-400 rounded-full opacity-10 blur-3xl"
        />
        <motion.div
          animate={{
            x: [100, -100, 100],
            y: [50, -50, 50],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute bottom-20 right-20 w-96 h-96 bg-purple-400 rounded-full opacity-10 blur-3xl"
        />
        
        {/* Floating particles */}
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            animate={{
              y: [-20, 20, -20],
              rotate: [0, 360],
            }}
            transition={{
              duration: 3 + i,
              repeat: Infinity,
              ease: "easeInOut",
              delay: i * 0.5
            }}
            className={`absolute w-4 h-4 bg-white rounded-full opacity-20`}
            style={{
              top: `${20 + (i * 10)}%`,
              left: `${10 + (i * 15)}%`,
            }}
          />
        ))}
      </div>

      <div className="container-premium relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-4xl mx-auto"
        >
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            whileInView={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mb-8"
          >
            <h2 className="text-5xl font-display font-bold mb-6 bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent">
              Découvrez la France Authentique
            </h2>
            <p className="text-xl text-blue-100 leading-relaxed max-w-3xl mx-auto">
              Laissez notre IA révéler les trésors cachés de France. Des villages oubliés aux restaurants secrets, 
              créez des souvenirs inoubliables avec des expériences uniques et personnalisées.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="flex flex-col sm:flex-row gap-6 justify-center items-center"
          >
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onHoverStart={() => setIsHovered(true)}
              onHoverEnd={() => setIsHovered(false)}
              className="group relative bg-white text-blue-600 px-8 py-4 rounded-full font-semibold text-lg shadow-2xl hover:shadow-3xl transition-all duration-300 overflow-hidden"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: isHovered ? 1 : 0 }}
                transition={{ duration: 0.3 }}
                className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
              />
              <span className={`relative z-10 transition-colors duration-300 ${isHovered ? 'text-white' : 'text-blue-600'}`}>
                Commencer l'Aventure
              </span>
              <motion.div
                animate={{ x: isHovered ? 5 : 0 }}
                className={`inline-block ml-2 transition-colors duration-300 ${isHovered ? 'text-white' : 'text-blue-600'}`}
              >
                →
              </motion.div>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="group border-2 border-white text-white px-8 py-4 rounded-full font-semibold text-lg hover:bg-white hover:text-blue-600 transition-all duration-300"
            >
              Voir la Démo
              <motion.div
                whileHover={{ rotate: 15 }}
                className="inline-block ml-2"
              >
                ▶
              </motion.div>
            </motion.button>
          </motion.div>

          {/* Trust indicators */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="mt-12 flex flex-wrap justify-center items-center gap-8 text-blue-200"
          >
            <div className="flex items-center gap-2">
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="w-5 h-5 bg-green-400 rounded-full"
              />
              <span className="text-sm">1000+ Lieux Secrets Découverts</span>
            </div>
            <div className="flex items-center gap-2">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                className="w-5 h-5 bg-yellow-400 rounded-full"
              />
              <span className="text-sm">IA Alimentée par Claude</span>
            </div>
            <div className="flex items-center gap-2">
              <motion.div
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="w-5 h-5 bg-pink-400 rounded-full"
              />
              <span className="text-sm">Expériences 100% Personnalisées</span>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}