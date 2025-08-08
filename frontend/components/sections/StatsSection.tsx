'use client'

import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'

const stats = [
  {
    id: 1,
    number: 2847,
    label: "Lieux Secrets Découverts",
    icon: "🏛️",
    color: "from-blue-500 to-indigo-600"
  },
  {
    id: 2,
    number: 15000,
    label: "Voyageurs Satisfaits",
    icon: "👥",
    color: "from-purple-500 to-pink-600"
  },
  {
    id: 3,
    number: 892,
    label: "Restaurants Authentiques",
    icon: "🍽️",
    color: "from-green-500 to-emerald-600"
  },
  {
    id: 4,
    number: 247,
    label: "Villages Cachés",
    icon: "🏘️",
    color: "from-orange-500 to-red-600"
  }
]

function CountUpNumber({ end, duration = 2000 }: { end: number; duration?: number }) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let startTime: number
    let animationFrame: number

    const updateCount = (timestamp: number) => {
      if (!startTime) startTime = timestamp
      const progress = (timestamp - startTime) / duration

      if (progress < 1) {
        setCount(Math.floor(end * progress))
        animationFrame = requestAnimationFrame(updateCount)
      } else {
        setCount(end)
      }
    }

    animationFrame = requestAnimationFrame(updateCount)

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame)
      }
    }
  }, [end, duration])

  return <span>{count.toLocaleString()}</span>
}

export function StatsSection() {
  const [inView, setInView] = useState(false)

  return (
    <section className="section-premium bg-gradient-to-br from-gray-50 to-blue-50 relative overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }} />
      </div>

      {/* Floating geometric shapes */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{
            rotate: 360,
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute top-20 left-10 w-16 h-16 border-2 border-blue-200 rotate-45 opacity-30"
        />
        <motion.div
          animate={{
            rotate: -360,
            y: [0, -20, 0],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute top-40 right-20 w-12 h-12 bg-purple-200 rounded-full opacity-40"
        />
        <motion.div
          animate={{
            rotate: 180,
            x: [0, 30, 0],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute bottom-32 left-1/4 w-8 h-20 bg-gradient-to-t from-green-200 to-emerald-200 opacity-30"
        />
      </div>

      <div className="container-premium relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          onViewportEnter={() => setInView(true)}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl font-display font-bold text-gray-900 mb-4">
            L'Intelligence Artificielle au Service du Voyage
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Des chiffres qui témoignent de notre engagement à révéler les trésors cachés de la France
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.id}
              initial={{ opacity: 0, y: 50, scale: 0.8 }}
              whileInView={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{ 
                y: -10,
                scale: 1.05,
                transition: { duration: 0.2 }
              }}
              className="group"
            >
              <div className="glass-card p-8 text-center h-full relative overflow-hidden">
                {/* Animated background gradient */}
                <motion.div
                  initial={{ scale: 0, rotate: 0 }}
                  whileInView={{ scale: 1, rotate: 360 }}
                  transition={{ duration: 1, delay: index * 0.2 }}
                  className={`absolute inset-0 bg-gradient-to-br ${stat.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}
                />
                
                {/* Icon with floating animation */}
                <motion.div
                  animate={{ 
                    y: [0, -10, 0],
                    rotate: [0, 5, 0, -5, 0]
                  }}
                  transition={{ 
                    duration: 4,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: index * 0.5
                  }}
                  className="text-4xl mb-4 relative z-10"
                >
                  {stat.icon}
                </motion.div>

                {/* Animated number */}
                <motion.div
                  className="text-4xl font-bold text-gray-900 mb-2 relative z-10"
                  whileInView={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  {inView ? (
                    <CountUpNumber end={stat.number} duration={2000 + index * 200} />
                  ) : (
                    0
                  )}
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 2.5 + index * 0.1 }}
                    className="text-2xl"
                  >
                    +
                  </motion.span>
                </motion.div>

                {/* Label */}
                <p className="text-gray-600 font-medium leading-tight relative z-10">
                  {stat.label}
                </p>

                {/* Hover effect particles */}
                <div className="absolute inset-0 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  {[...Array(5)].map((_, i) => (
                    <motion.div
                      key={i}
                      initial={{ scale: 0, x: 0, y: 0 }}
                      whileHover={{
                        scale: [0, 1, 0],
                        x: [0, Math.random() * 100 - 50],
                        y: [0, Math.random() * 100 - 50],
                      }}
                      transition={{
                        duration: 1,
                        delay: i * 0.1,
                        ease: "easeOut"
                      }}
                      className={`absolute w-2 h-2 bg-gradient-to-r ${stat.color} rounded-full top-1/2 left-1/2`}
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Additional info section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="mt-16 text-center"
        >
          <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-8 max-w-4xl mx-auto shadow-lg">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Alimenté par l'IA Claude d'Anthropic
            </h3>
            <p className="text-gray-600 leading-relaxed">
              Notre technologie d'intelligence artificielle avancée analyse en temps réel des milliers de sources 
              pour vous offrir les recommandations les plus authentiques et personnalisées. Chaque suggestion 
              est adaptée à vos goûts, votre budget et vos préférences culturelles.
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  )
}