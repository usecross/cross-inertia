import { Link, usePage } from '@inertiajs/react'
import { cn } from '@/lib/utils'
import { ReactNode, useState } from 'react'

interface NavItem {
  title: string
  href: string
}

interface NavSection {
  title: string
  items: NavItem[]
}

interface SharedProps {
  nav: NavSection[]
  currentPath: string
}

function Logo() {
  return (
    <Link href="/" className="flex items-center">
      <img src="/static/logo.svg" alt="Cross-Inertia" className="h-8" />
    </Link>
  )
}

function Sidebar({ nav, currentPath }: SharedProps) {
  return (
    <nav className="space-y-8">
      {nav.map((section) => (
        <div key={section.title}>
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
            {section.title}
          </h3>
          <ul className="space-y-1 border-l border-slate-200">
            {section.items.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    'block border-l-2 py-1 pl-4 text-sm transition-colors -ml-px',
                    currentPath === item.href
                      ? 'border-slate-900 text-slate-900 font-medium'
                      : 'border-transparent text-slate-600 hover:border-slate-400 hover:text-slate-900'
                  )}
                >
                  {item.title}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  )
}

function MobileMenuButton({ onClick, isOpen }: { onClick: () => void; isOpen: boolean }) {
  return (
    <button
      onClick={onClick}
      className="inline-flex items-center justify-center rounded-md p-2 text-white/80 hover:text-white hover:bg-white/10 lg:hidden"
      aria-expanded={isOpen}
    >
      <span className="sr-only">{isOpen ? 'Close menu' : 'Open menu'}</span>
      {isOpen ? (
        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      ) : (
        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      )}
    </button>
  )
}

interface DocsLayoutProps {
  children: ReactNode
  title: string
  description?: string
}

export function DocsLayout({ children, title, description }: DocsLayoutProps) {
  const { nav, currentPath } = usePage<{ props: SharedProps }>().props as unknown as SharedProps
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Fixed colored navigation */}
      <nav className="fixed w-full z-50 backdrop-blur-md bg-primary-500">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-4">
              <MobileMenuButton onClick={() => setMobileMenuOpen(!mobileMenuOpen)} isOpen={mobileMenuOpen} />
              <Logo />
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <Link
                href="/docs"
                className="hover:underline underline-offset-2 decoration-1 transition text-gray-200"
              >
                Docs
              </Link>
              <a
                href="https://github.com/patrick91/cross-inertia"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-200 hover:text-white transition"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    fillRule="evenodd"
                    d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                    clipRule="evenodd"
                  />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile sidebar */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="fixed inset-0 bg-black/50" onClick={() => setMobileMenuOpen(false)} />
          <div className="fixed inset-y-0 left-0 w-64 overflow-y-auto bg-white p-6 pt-20">
            <Sidebar nav={nav} currentPath={currentPath} />
          </div>
        </div>
      )}

      {/* Main content area */}
      <div className="bg-white pt-16 w-full flex-1">
        <div className="mx-auto max-w-8xl px-4 py-8 sm:px-6 lg:px-8 lg:py-12">
          <div className="lg:grid lg:grid-cols-12 lg:gap-x-12 xl:gap-x-16">
            {/* Desktop sidebar */}
            <aside className="hidden lg:col-span-2 lg:block">
              <nav className="sticky top-24 space-y-8 max-h-[calc(100vh-8rem)] overflow-y-auto pb-8">
                <Sidebar nav={nav} currentPath={currentPath} />
              </nav>
            </aside>

            {/* Main content */}
            <main className="lg:col-span-7 lg:pl-8 xl:pl-12">
              <article className="prose md:prose-lg prose-headings:mt-0 prose-headings:mb-2 prose-p:mt-4 prose-li:my-1">
                {children}
              </article>
            </main>

            {/* TOC column (placeholder for future) */}
            <aside className="hidden lg:col-span-3 lg:block">
              {/* Table of contents could go here */}
            </aside>
          </div>
        </div>
      </div>

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
    </div>
  )
}

export function MainLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Fixed colored navigation */}
      <nav className="fixed w-full z-50 backdrop-blur-md bg-primary-500">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <Logo />
            <div className="hidden md:flex items-center space-x-8">
              <Link
                href="/docs"
                className="hover:underline underline-offset-2 decoration-1 transition text-gray-200"
              >
                Docs
              </Link>
              <a
                href="https://github.com/patrick91/cross-inertia"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-200 hover:text-white transition"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    fillRule="evenodd"
                    d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                    clipRule="evenodd"
                  />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content with top padding for fixed nav */}
      <main className="flex flex-col flex-1 pt-16">
        {children}
      </main>
    </div>
  )
}
