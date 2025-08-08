'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'

const footerLinks = {
  product: [
    { name: 'Fonctionnalités', href: '#features' },
    { name: 'Tarification', href: '#pricing' },
    { name: 'API', href: '/api/docs' },
    { name: 'Démo', href: '#demo' },
  ],
  company: [
    { name: 'À propos', href: '#about' },
    { name: 'Blog', href: '#blog' },
    { name: 'Carrières', href: '#careers' },
    { name: 'Presse', href: '#press' },
  ],
  resources: [
    { name: 'Documentation', href: '#docs' },
    { name: 'Guides', href: '#guides' },
    { name: 'Support', href: '#support' },
    { name: 'Statut', href: '#status' },
  ],
  legal: [
    { name: 'Confidentialité', href: '#privacy' },
    { name: 'Conditions', href: '#terms' },
    { name: 'Cookies', href: '#cookies' },
    { name: 'Licences', href: '#licenses' },
  ],
}

const socialLinks = [
  {
    name: 'Twitter',
    href: '#',
    icon: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
        <path d="M6.29 18.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0020 3.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.073 4.073 0 01.8 7.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 010 16.407a11.616 11.616 0 006.29 1.84" />
      </svg>
    ),
  },
  {
    name: 'GitHub',
    href: 'https://github.com/Chedly25/newTrip',
    icon: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
        <path fillRule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clipRule="evenodd" />
      </svg>
    ),
  },
  {
    name: 'LinkedIn',
    href: '#',
    icon: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
        <path fillRule="evenodd" d="M16.338 16.338H13.67V12.16c0-.995-.017-2.277-1.387-2.277-1.39 0-1.601 1.086-1.601 2.207v4.248H8.014v-8.59h2.559v1.174h.037c.356-.675 1.227-1.387 2.526-1.387 2.703 0 3.203 1.778 3.203 4.092v4.711zM5.005 6.575a1.548 1.548 0 11-.003-3.096 1.548 1.548 0 01.003 3.096zm-1.337 9.763H6.34v-8.59H3.667v8.59zM17.668 1H2.328C1.595 1 1 1.581 1 2.298v15.403C1 18.418 1.595 19 2.328 19h15.34c.734 0 1.332-.582 1.332-1.299V2.298C19 1.581 18.402 1 17.668 1z" clipRule="evenodd" />
      </svg>
    ),
  },
]

export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute top-10 right-10 w-32 h-32 border border-blue-400/20 rounded-full"
        />
        <motion.div
          animate={{
            x: [-50, 50, -50],
            y: [0, -30, 0],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute bottom-20 left-10 w-24 h-24 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-full blur-xl"
        />
      </div>

      <div className="container-premium relative z-10">
        <div className="py-16">
          {/* Main footer content */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-8 mb-12">
            {/* Brand section */}
            <div className="lg:col-span-2">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
              >
                <Link href="/" className="group">
                  <motion.h3 
                    whileHover={{ scale: 1.05 }}
                    className="text-2xl font-display font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent mb-4"
                  >
                    Wanderlog AI
                  </motion.h3>
                </Link>
                <p className="text-gray-300 mb-6 leading-relaxed">
                  Découvrez les trésors cachés de la France avec l'intelligence artificielle la plus avancée. 
                  Des expériences authentiques, personnalisées pour chaque voyageur.
                </p>
                
                {/* Social links */}
                <div className="flex space-x-4">
                  {socialLinks.map((item) => (
                    <motion.a
                      key={item.name}
                      href={item.href}
                      whileHover={{ scale: 1.2, y: -2 }}
                      whileTap={{ scale: 0.9 }}
                      className="text-gray-400 hover:text-white transition-colors duration-200 p-2 rounded-full hover:bg-white/10"
                      target={item.name === 'GitHub' ? '_blank' : undefined}
                      rel={item.name === 'GitHub' ? 'noopener noreferrer' : undefined}
                    >
                      <span className="sr-only">{item.name}</span>
                      {item.icon}
                    </motion.a>
                  ))}
                </div>
              </motion.div>
            </div>

            {/* Link sections */}
            {Object.entries(footerLinks).map(([category, links], index) => (
              <div key={category}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                >
                  <h4 className="text-lg font-semibold text-white mb-4 capitalize">
                    {category === 'product' && 'Produit'}
                    {category === 'company' && 'Entreprise'}
                    {category === 'resources' && 'Ressources'}
                    {category === 'legal' && 'Légal'}
                  </h4>
                  <ul className="space-y-2">
                    {links.map((link) => (
                      <li key={link.name}>
                        <motion.div
                          whileHover={{ x: 5 }}
                          transition={{ duration: 0.2 }}
                        >
                          <Link
                            href={link.href}
                            className="text-gray-300 hover:text-white transition-colors duration-200 text-sm"
                          >
                            {link.name}
                          </Link>
                        </motion.div>
                      </li>
                    ))}
                  </ul>
                </motion.div>
              </div>
            ))}
          </div>

          {/* Newsletter signup */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 mb-12"
          >
            <div className="max-w-2xl mx-auto text-center">
              <h4 className="text-xl font-semibold text-white mb-2">
                Restez informé des dernières découvertes
              </h4>
              <p className="text-gray-300 mb-6">
                Recevez nos recommandations exclusives et les nouveaux lieux secrets directement dans votre boîte mail.
              </p>
              <div className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
                <input
                  type="email"
                  placeholder="votre-email@exemple.com"
                  className="flex-1 px-4 py-3 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                />
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-full font-semibold hover:from-blue-600 hover:to-purple-700 transition-all duration-200"
                >
                  S'abonner
                </motion.button>
              </div>
            </div>
          </motion.div>

          {/* Bottom section */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="border-t border-white/10 pt-8"
          >
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <div className="text-gray-300 text-sm">
                © {currentYear} Wanderlog AI. Tous droits réservés.
              </div>
              
              <div className="flex items-center gap-6 text-sm text-gray-300">
                <motion.span
                  whileHover={{ scale: 1.05 }}
                  className="flex items-center gap-2"
                >
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="w-2 h-2 bg-green-400 rounded-full"
                  />
                  Alimenté par Claude AI
                </motion.span>
                
                <span className="text-gray-500">|</span>
                
                <motion.span
                  whileHover={{ scale: 1.05 }}
                  className="flex items-center gap-2"
                >
                  🇫🇷 Fait en France avec ❤️
                </motion.span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </footer>
  )
}