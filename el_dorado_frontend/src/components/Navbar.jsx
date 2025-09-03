import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Home, Users, BarChart3, Hash, Video, Bot } from 'lucide-react'

const Navbar = () => {
  const location = useLocation()
  
  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/influencers', icon: Users, label: 'Influencers' },
    { path: '/analytics', icon: BarChart3, label: 'Analytics' },
    { path: '/hashtags', icon: Hash, label: 'Hashtags' },
    { path: '/transcription', icon: Video, label: 'Transcrição' },
    { path: '/ai-assistant', icon: Bot, label: 'AI Assistant' },
  ]

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <span className="text-xl font-bold text-gray-900">El Dorado</span>
          </div>

          {/* Navigation */}
          <div className="flex space-x-8">
            {navItems.map(({ path, icon: Icon, label }) => (
              <Link
                key={path}
                to={path}
                className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  location.pathname === path
                    ? 'text-primary-600 bg-primary-50'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </Link>
            ))}
          </div>

          {/* User Info */}
          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 bg-primary-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">ED</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar