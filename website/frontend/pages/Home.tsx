import { Link } from '@inertiajs/react'
import { MainLayout } from '@/components/Layout'
import { useState } from 'react'

interface HomeProps {
  installCommand: string
}

function InstallCommand({ command }: { command: string }) {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(command)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <button
      onClick={copyToClipboard}
      className="group relative flex h-12 items-center bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 font-mono text-sm text-slate-300 hover:border-slate-600 transition cursor-pointer"
    >
      <span className="text-sky-400 mr-2">$</span>
      <span>{command}</span>
      <svg
        className={`ml-4 w-4 h-4 transition ${copied ? 'text-green-400' : 'text-slate-500 group-hover:text-white'}`}
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
        />
      </svg>
      <span
        className={`absolute -top-8 left-1/2 -translate-x-1/2 bg-black text-white text-xs py-1 px-2 rounded transition-opacity duration-300 ${
          copied ? 'opacity-100' : 'opacity-0'
        }`}
      >
        Copied!
      </span>
    </button>
  )
}

export default function Home({ installCommand }: HomeProps) {
  return (
    <MainLayout>
      {/* Hero section */}
      <section className="relative overflow-hidden flex items-center justify-center flex-1 w-full">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center py-20 lg:py-32">
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6">
            <span className="text-primary-500">Inertia.js</span> for Python
          </h1>

          <p className="text-xl text-gray-800 max-w-2xl mx-auto mb-10">
            Build modern single-page apps with Django, Flask, and FastAPI - no API required
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-4 items-center">
            <Link
              href="/docs"
              className="px-8 h-12 flex items-center text-white rounded-lg font-bold hover:opacity-90 transition bg-primary-500"
            >
              Get Started
            </Link>
            <InstallCommand command={installCommand} />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12">
        <div className="px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-6">
          <Link href="/" className="flex items-center">
            <img src="/static/logo-full.svg" alt="Cross-Inertia" className="h-6" />
          </Link>
          <div className="flex gap-8 text-sm text-gray-800">
            <Link href="/docs" className="hover:text-gray-600 transition">
              Documentation
            </Link>
            <a
              href="https://github.com/patrick91/cross-inertia"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-gray-600 transition"
            >
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </MainLayout>
  )
}
