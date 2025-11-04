import { Link, usePage } from '@inertiajs/react'
import React from 'react'
import { Heart, Home, User, X } from 'lucide-react'

interface LayoutProps {
  children: React.ReactNode
  title?: string
}

interface SharedProps {
  auth: {
    user: {
      id: number
      name: string
      email: string
    }
  }
  favorites_count: number
  flash: {
    message?: string
    category?: 'success' | 'error' | 'warning' | 'info'
  }
  [key: string]: unknown
}

export default function Layout({ children, title }: LayoutProps) {
  const { auth, favorites_count, flash } = usePage<SharedProps>().props
  const [showFlash, setShowFlash] = React.useState(!!flash.message)

  // Auto-hide flash message after 5 seconds
  React.useEffect(() => {
    if (flash.message) {
      setShowFlash(true)
      const timer = setTimeout(() => setShowFlash(false), 5000)
      return () => clearTimeout(timer)
    }
  }, [flash.message])

  const flashColors = {
    success: 'bg-green-50 text-green-800 border-green-200',
    error: 'bg-red-50 text-red-800 border-red-200',
    warning: 'bg-yellow-50 text-yellow-800 border-yellow-200',
    info: 'bg-blue-50 text-blue-800 border-blue-200',
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="bg-black text-white border-b border-zinc-800">
        <div className="container mx-auto flex items-center justify-between px-6 py-4">
          <h1 className="text-xl font-semibold">
            <Link href="/browse" className="hover:text-zinc-300 transition-colors">
              PurrfectHome
            </Link>
          </h1>
          <div className="flex items-center gap-6">
            <Link 
              href="/browse" 
              className="text-sm hover:text-zinc-300 transition-colors flex items-center gap-2"
            >
              <Home className="h-4 w-4" />
              Browse
            </Link>
            <Link 
              href="/favorites" 
              className="text-sm hover:text-zinc-300 transition-colors flex items-center gap-2"
            >
              <Heart className="h-4 w-4" />
              Favorites
              {favorites_count > 0 && (
                <span className="bg-white text-black text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
                  {favorites_count}
                </span>
              )}
            </Link>
            <div className="flex items-center gap-2 text-sm text-zinc-300">
              <User className="h-4 w-4" />
              {auth.user.name}
            </div>
          </div>
        </div>
      </nav>

      {/* Flash Messages */}
      {showFlash && flash.message && (
        <div className="container mx-auto max-w-7xl px-6 mt-4">
          <div className={`flex items-center justify-between p-4 rounded-lg border ${flashColors[flash.category || 'info']}`}>
            <p className="font-medium">{flash.message}</p>
            <button 
              onClick={() => setShowFlash(false)}
              className="ml-4 hover:opacity-70 transition-opacity"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      <main className="container mx-auto max-w-7xl px-6 py-8">
        {title && <h1 className="text-3xl font-bold mb-8">{title}</h1>}
        {children}
      </main>
      <footer className="border-t mt-12">
        <div className="container mx-auto px-6 py-8 text-center text-sm text-muted-foreground">
          <p>PurrfectHome - A demo showcasing Inertia.js with FastAPI</p>
          <p className="mt-2 text-xs text-zinc-400">Version: scroll-fix-v2</p>
        </div>
      </footer>
    </div>
  )
}
