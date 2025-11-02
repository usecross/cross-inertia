import { Link } from '@inertiajs/react'
import React from 'react'

interface LayoutProps {
  children: React.ReactNode
  title?: string
}

export default function Layout({ children, title }: LayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b bg-slate-900 text-white">
        <div className="container mx-auto flex items-center gap-8 px-6 py-4">
          <h1 className="text-2xl font-bold">
            <Link href="/" className="hover:text-slate-200 transition-colors">
              Inertia Demo
            </Link>
          </h1>
          <div className="flex gap-6">
            <Link href="/" className="hover:text-slate-200 transition-colors">
              Home
            </Link>
            <Link href="/about" className="hover:text-slate-200 transition-colors">
              About
            </Link>
            <Link href="/users" className="hover:text-slate-200 transition-colors">
              Users
            </Link>
            <Link href="/form" className="hover:text-slate-200 transition-colors">
              Form
            </Link>
          </div>
        </div>
      </nav>
      <main className="container mx-auto max-w-6xl px-6 py-8">
        {title && <h1 className="text-4xl font-bold mb-8">{title}</h1>}
        {children}
      </main>
    </div>
  )
}
