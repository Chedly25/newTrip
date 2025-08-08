'use client'

import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'

const testimonials = [
  {
    id: 1,
    name: "Marie Dubois",
    location: "Paris",
    avatar: "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face&auto=format&q=80",
    rating: 5,
    text: "Wanderlog AI découvre les vrais trésors cachés de France. J'ai trouvé des endroits magiques que même mes amis parisiens ne connaissaient pas!"
  },
  {
    id: 2,
    name: "Thomas Martin",
    location: "Lyon",
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face&auto=format&q=80",
    rating: 5,
    text: "L'IA comprend parfaitement mes goûts. Chaque recommandation était parfaite - des restaurants authentiques aux monuments secrets."
  },
  {
    id: 3,
    name: "Sophie Leclerc",
    location: "Provence",
    avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face&auto=format&q=80",
    rating: 5,
    text: "Grâce à Wanderlog AI, j'ai redécouvert ma propre région! Des villages oubliés et des sentiers secrets que je n'avais jamais explorés."
  }
]

export function TestimonialsSection() {
  const [currentTestimonial, setCurrentTestimonial] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length)
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <section className="section-premium bg-gradient-to-br from-purple-50 via-pink-50 to-rose-50 relative overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          animate={{
            rotate: 360,
          }}
          transition={{
            duration: 60,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute top-10 right-10 w-32 h-32 bg-gradient-to-br from-purple-200 to-pink-200 rounded-full opacity-20"
        />
        <motion.div
          animate={{
            rotate: -360,
          }}
          transition={{
            duration: 45,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute bottom-20 left-10 w-24 h-24 bg-gradient-to-br from-rose-200 to-purple-200 rounded-full opacity-20"
        />
      </div>

      <div className="container-premium relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl font-display font-bold text-gray-900 mb-4">
            Témoignages de nos Explorateurs
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Découvrez comment Wanderlog AI transforme l'expérience de voyage en France
          </p>
        </motion.div>

        <div className="max-w-4xl mx-auto">
          <div className="relative min-h-[300px] flex items-center justify-center">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={testimonial.id}
                initial={{ opacity: 0, scale: 0.8, rotateY: 90 }}
                animate={{
                  opacity: currentTestimonial === index ? 1 : 0,
                  scale: currentTestimonial === index ? 1 : 0.8,
                  rotateY: currentTestimonial === index ? 0 : 90,
                }}
                transition={{
                  duration: 0.6,
                  ease: "easeInOut"
                }}
                className={`absolute inset-0 ${
                  currentTestimonial === index ? 'pointer-events-auto' : 'pointer-events-none'
                }`}
              >
                <div className="glass-card p-8 text-center">
                  <div className="flex justify-center mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <motion.svg
                        key={i}
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: i * 0.1 }}
                        className="w-6 h-6 text-yellow-400 mx-1"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </motion.svg>
                    ))}
                  </div>

                  <p className="text-lg text-gray-700 mb-8 italic leading-relaxed">
                    "{testimonial.text}"
                  </p>

                  <div className="flex items-center justify-center">
                    <motion.img
                      whileHover={{ scale: 1.1 }}
                      src={testimonial.avatar}
                      alt={testimonial.name}
                      className="w-16 h-16 rounded-full mr-4 object-cover shadow-lg"
                    />
                    <div className="text-left">
                      <h4 className="text-lg font-semibold text-gray-900">
                        {testimonial.name}
                      </h4>
                      <p className="text-gray-600">{testimonial.location}</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Testimonial indicators */}
          <div className="flex justify-center mt-8 space-x-2">
            {testimonials.map((_, index) => (
              <motion.button
                key={index}
                whileHover={{ scale: 1.2 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => setCurrentTestimonial(index)}
                className={`w-3 h-3 rounded-full transition-all duration-300 ${
                  currentTestimonial === index
                    ? 'bg-purple-500 scale-125'
                    : 'bg-gray-300 hover:bg-gray-400'
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}