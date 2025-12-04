import { Head, Link, usePage } from '@inertiajs/react'
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

function Logo({ inverted = false }: { inverted?: boolean }) {
  return (
    <Link href="/" className="flex items-center">
      <img
        src={inverted ? '/static/logo-inverted.svg' : '/static/logo.svg'}
        alt="Cross-Inertia"
        className="h-8"
      />
    </Link>
  )
}

function Sidebar({ nav, currentPath }: SharedProps) {
  return (
    <nav className="space-y-8">
      {nav.map((section) => (
        <div key={section.title}>
          <h3 className="mb-3 text-xs font-mono uppercase tracking-widest text-gray-500">
            {section.title}
          </h3>
          <ul className="space-y-1 border-l-2 border-gray-200">
            {section.items.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    'block border-l-2 py-1.5 pl-4 text-sm transition-colors -ml-0.5',
                    currentPath === item.href
                      ? 'border-primary-500 text-black font-bold'
                      : 'border-transparent text-gray-600 hover:border-black hover:text-black'
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
      className="inline-flex items-center justify-center p-2 -ml-2 text-black hover:text-primary-500 lg:hidden"
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
      <Head title={title} />
      {/* Fixed navigation */}
      <nav className="fixed w-full z-50 bg-white border-b border-black">
        <div className="px-4 lg:px-10">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-2">
              <MobileMenuButton onClick={() => setMobileMenuOpen(!mobileMenuOpen)} isOpen={mobileMenuOpen} />
              <Logo inverted />
            </div>
            <div className="flex items-center space-x-8">
              <Link
                href="/docs"
                className="text-black font-medium hover:text-primary-500 transition-colors"
              >
                Docs
              </Link>
              <a
                href="https://github.com/patrick91/cross-inertia"
                target="_blank"
                rel="noopener noreferrer"
                className="text-black hover:text-primary-500 transition-colors"
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
          <div className="fixed inset-y-0 left-0 w-72 overflow-y-auto bg-white px-4 lg:px-10 py-6 pt-20 border-r border-black">
            <Sidebar nav={nav} currentPath={currentPath} />
          </div>
        </div>
      )}

      {/* Main content area */}
      <div className="bg-white pt-16 w-full flex-1">
        <div className="grid grid-cols-12">
          {/* Desktop sidebar */}
          <aside className="hidden lg:block lg:col-span-3 xl:col-span-2 border-r border-black min-h-[calc(100vh-4rem)]">
            <nav className="sticky top-16 px-4 lg:px-10 py-6 max-h-[calc(100vh-4rem)] overflow-y-auto">
              <Sidebar nav={nav} currentPath={currentPath} />
            </nav>
          </aside>

          {/* Main content */}
          <main className="col-span-12 lg:col-span-9 xl:col-span-10 p-4 lg:px-10 lg:py-6">
            <article className="prose prose-lg max-w-3xl prose-headings:font-bold prose-headings:tracking-tight prose-h1:text-4xl prose-h1:border-b-2 prose-h1:border-black prose-h1:pb-4 prose-h1:mb-8 prose-h2:text-2xl prose-h2:mt-12 first:prose-h2:mt-0 prose-h3:text-xl prose-a:text-primary-500 prose-a:no-underline hover:prose-a:underline prose-code:bg-gray-100 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:before:content-none prose-code:after:content-none">
              {children}
            </article>
          </main>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-black py-8">
        <div className="px-4 lg:px-10 flex flex-col md:flex-row justify-between items-center gap-6">
          <Link href="/">
            <img src="/static/logo-full.svg" alt="Cross-Inertia" className="h-5" />
          </Link>
          <div className="flex gap-8 text-sm text-gray-600">
            <Link href="/docs" className="hover:text-black transition-colors">
              Documentation
            </Link>
            <a
              href="https://github.com/patrick91/cross-inertia"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-black transition-colors"
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
      {/* Fixed navigation */}
      <nav className="fixed w-full z-50 bg-white border-b border-black">
        <div className="px-4 lg:px-10">
          <div className="flex justify-between h-16 items-center">
            <Logo />
            <div className="flex items-center space-x-8">
              <Link
                href="/docs"
                className="text-black font-medium hover:text-primary-500 transition-colors"
              >
                Docs
              </Link>
              <a
                href="https://github.com/patrick91/cross-inertia"
                target="_blank"
                rel="noopener noreferrer"
                className="text-black hover:text-primary-500 transition-colors"
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
