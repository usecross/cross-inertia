import { Head, Link } from '@inertiajs/react'
import { useState, useCallback, useEffect } from 'react'

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
      className="group relative flex items-center bg-black border border-black px-4 py-3 font-mono text-sm text-white hover:bg-white hover:text-black transition-colors cursor-pointer"
    >
      <span className="text-primary-500 mr-2">$</span>
      <span>{command}</span>
      <svg
        className={`ml-4 w-4 h-4 transition ${copied ? 'text-green-400' : 'opacity-50 group-hover:opacity-100'}`}
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
        className={`absolute -top-8 left-1/2 -translate-x-1/2 bg-black text-white text-xs py-1 px-2 transition-opacity duration-300 ${
          copied ? 'opacity-100' : 'opacity-0'
        }`}
      >
        Copied!
      </span>
    </button>
  )
}

function Logo({ showFull = false }: { showFull?: boolean }) {
  return (
    <Link href="/" className="flex items-center h-8">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 273.61 56.25" className="h-8">
        <rect fill="#658c58" x="0" width="56.25" height="56.25"/>
        <g
          fill="#658c58"
          className="transition-opacity duration-300"
          style={{ opacity: showFull ? 1 : 0 }}
        >
          <path d="M65.17,6.72h12.73v8.64h-12.73V6.72ZM65.17,18.24h12.67v31.61h-12.67v-31.61Z"/>
          <path d="M82,18.24h12.67l-.38,8.45h.13c1.47-5.5,4.93-8.96,11.97-8.96,7.81,0,11.97,4.42,11.97,12.35v19.77h-12.67v-16.58c0-3.46-1.86-4.99-4.99-4.99-3.71,0-6.02,2.24-6.02,6.85v14.72h-12.67v-31.61Z"/>
          <path d="M155.47,35.84h-21.31c.32,4.54,2.18,6.27,5.63,6.27,2.88,0,4.67-1.15,4.86-3.84h10.81c-.13,7.49-5.7,12.09-16.25,12.09-12.22,0-17.79-6.53-17.79-16,0-10.88,6.85-16.64,17.92-16.64,10.05,0,16.13,4.99,16.13,15.17v2.94ZM144.65,29.82c0-2.88-1.79-4.35-4.86-4.35s-4.86,1.41-5.44,5.18h10.3v-.83Z"/>
          <path d="M158.86,18.24h12.67l-.38,8.83h.13c1.28-5.63,4.29-9.34,10.37-9.34,6.66,0,9.86,4.1,9.86,12.61,0,2.3-.19,5.5-.32,7.29h-10.88c.13-1.47.13-3.2.13-4.16,0-3.65-1.34-5.12-3.71-5.12-3.13,0-5.18,2.62-5.18,8.26v13.25h-12.67v-31.61Z"/>
          <path d="M197.64,38.72v-10.94h-4.35v-9.54h3.46c1.73,0,2.5-.83,2.69-3.13l.45-4.03h10.43v7.17h9.34v9.54h-9.34v9.73c0,2.62,1.22,3.46,4.8,3.46,1.47,0,3.33-.19,4.16-.38v9.09c-.96.26-3.84.7-7.3.7-10.62,0-14.33-4.48-14.33-11.65Z"/>
          <path d="M223.12,6.72h12.74v8.64h-12.74V6.72ZM223.12,18.24h12.67v31.61h-12.67v-31.61Z"/>
          <path d="M239.56,41.15c0-4.99,3.39-8.64,11.26-8.64h10.11v-2.3c0-2.94-1.54-4.22-4.86-4.22-2.82,0-4.35,1.28-4.35,3.46,0,.13,0,.64.06,1.28h-11.07c-.13-.64-.19-1.41-.19-2.11,0-6.72,5.31-10.88,16.19-10.88,11.46,0,16.89,5.12,16.89,13.5v18.62h-12.67c.19-1.34.38-4.03.38-6.02h-.06c-.96,3.97-4.1,6.53-9.98,6.53-7.81,0-11.71-3.78-11.71-9.21ZM260.94,38.46v-.83h-6.53c-2.11,0-3.33,1.02-3.33,2.56,0,1.92,1.54,3.01,4.1,3.01,3.58,0,5.76-1.73,5.76-4.74Z"/>
        </g>
        <polygon fill="#ffffff" points="44.15 36.09 36.15 28.09 44.04 20.19 36.05 12.2 28.15 20.09 20.17 12.11 12.18 20.1 20.16 28.09 12.07 36.17 20.07 44.17 28.15 36.08 36.15 44.08 44.15 36.09"/>
      </svg>
    </Link>
  )
}

type HighlightKey = 'name' | 'email' | null

function Hl({
  k,
  children,
  highlighted,
  setHighlighted,
  className = '',
}: {
  k: HighlightKey
  children: React.ReactNode
  highlighted: HighlightKey
  setHighlighted: (key: HighlightKey) => void
  className?: string
}) {
  const isActive = highlighted === k
  return (
    <span
      onMouseEnter={() => setHighlighted(k)}
      onMouseLeave={() => setHighlighted(null)}
      className={`relative rounded px-1 -mx-1 cursor-default ${className}`}
    >
      <span
        className="absolute -inset-x-1 rounded bg-primary-500/30 border border-primary-500"
        style={{
          top: '-3px',
          bottom: '-3px',
          opacity: isActive ? 1 : 0,
          transition: 'opacity 300ms ease-out',
        }}
      />
      <span className="relative">{children}</span>
    </span>
  )
}

function InteractiveCodeExample() {
  const [highlighted, setHighlighted] = useState<HighlightKey>(null)

  return (
    <section className="border-t border-black">
      <div className="grid grid-cols-12">
        <div className="col-span-12 lg:col-span-6 p-6 lg:p-12 border-b lg:border-b-0 lg:border-r border-black bg-black text-white">
          <div className="text-sm font-mono uppercase tracking-widest text-gray-400 mb-4">
            Backend
          </div>
          <pre className="font-mono text-sm lg:text-base overflow-x-auto leading-relaxed">
            <code>
              <span className="text-purple-400">@app.get</span>(<span className="text-green-400">"/users/&#123;id&#125;"</span>){'\n'}
              <span className="text-pink-400">async def</span> <span className="text-blue-300">show_user</span>({'\n'}
              {'    '}id: <span className="text-cyan-400">int</span>,{'\n'}
              {'    '}inertia: <span className="text-cyan-400">InertiaDep</span>{'\n'}
              ):{'\n'}
              {'    '}user = <span className="text-pink-400">await</span> get_user(id){'\n'}
              {'    '}<span className="text-pink-400">return</span> inertia.render({'\n'}
              {'        '}<span className="text-green-400">"Users/Show"</span>,{'\n'}
              {'        '}&#123;{'\n'}
              {'            '}<Hl k="name" highlighted={highlighted} setHighlighted={setHighlighted}><span className="text-green-400">"name"</span>: user.name,</Hl>{'\n'}
              {'            '}<Hl k="email" highlighted={highlighted} setHighlighted={setHighlighted}><span className="text-green-400">"email"</span>: user.email,</Hl>{'\n'}
              {'        '}&#125;{'\n'}
              {'    '})
            </code>
          </pre>
        </div>
        <div className="col-span-12 lg:col-span-6 p-6 lg:p-12 bg-gray-50">
          <div className="text-sm font-mono uppercase tracking-widest text-gray-500 mb-4">
            Frontend
          </div>
          <pre className="font-mono text-sm lg:text-base overflow-x-auto leading-relaxed">
            <code>
              <span className="text-pink-600">interface</span> <span className="text-cyan-600">Props</span> &#123;{'\n'}
              {'  '}<Hl k="name" highlighted={highlighted} setHighlighted={setHighlighted}>name:</Hl> <span className="text-cyan-600">string</span>{'\n'}
              {'  '}<Hl k="email" highlighted={highlighted} setHighlighted={setHighlighted}>email:</Hl> <span className="text-cyan-600">string</span>{'\n'}
              &#125;{'\n'}
              {'\n'}
              <span className="text-pink-600">export default function</span> <span className="text-blue-600">Show</span>(&#123; <Hl k="name" highlighted={highlighted} setHighlighted={setHighlighted}>name,</Hl> <Hl k="email" highlighted={highlighted} setHighlighted={setHighlighted}>email</Hl> &#125;: <span className="text-cyan-600">Props</span>) &#123;{'\n'}
              {'  '}<span className="text-pink-600">return</span> ({'\n'}
              {'    '}<span className="text-green-700">&lt;Layout&gt;</span>{'\n'}
              {'      '}<span className="text-green-700">&lt;h1&gt;</span>&#123;<Hl k="name" highlighted={highlighted} setHighlighted={setHighlighted}>name</Hl>&#125;<span className="text-green-700">&lt;/h1&gt;</span>{'\n'}
              {'      '}<span className="text-green-700">&lt;p&gt;</span>&#123;<Hl k="email" highlighted={highlighted} setHighlighted={setHighlighted}>email</Hl>&#125;<span className="text-green-700">&lt;/p&gt;</span>{'\n'}
              {'    '}<span className="text-green-700">&lt;/Layout&gt;</span>{'\n'}
              {'  '}){'\n'}
              &#125;
            </code>
          </pre>
        </div>
      </div>
    </section>
  )
}

interface Strawberry {
  id: number
  x: number
  y: number
  angle: number
  velocity: number
  spin: number
  scale: number
}

function StrawberryConfetti({ children }: { children: React.ReactNode }) {
  const [strawberries, setStrawberries] = useState<Strawberry[]>([])
  const [isActive, setIsActive] = useState(false)

  const triggerBurst = useCallback(() => {
    if (isActive) return
    setIsActive(true)

    const newStrawberries: Strawberry[] = []
    const count = 15

    for (let i = 0; i < count; i++) {
      // Burst in all directions from center
      const angle = (i / count) * Math.PI * 2 + (Math.random() - 0.5) * 0.5
      newStrawberries.push({
        id: Date.now() + i,
        x: 50, // Start from center
        y: 50,
        angle,
        velocity: 80 + Math.random() * 60, // Distance to travel
        spin: (Math.random() - 0.5) * 720, // Random rotation
        scale: 0.7 + Math.random() * 0.6,
      })
    }
    setStrawberries(newStrawberries)

    setTimeout(() => {
      setStrawberries([])
      setIsActive(false)
    }, 1000)
  }, [isActive])

  return (
    <span
      className="relative inline-block"
      onMouseEnter={triggerBurst}
    >
      {children}
      <span className="absolute inset-0 pointer-events-none overflow-visible">
        {strawberries.map((s) => {
          const endX = s.x + Math.cos(s.angle) * s.velocity
          const endY = s.y + Math.sin(s.angle) * s.velocity

          return (
            <span
              key={s.id}
              className="absolute"
              style={{
                left: '50%',
                top: '50%',
                fontSize: `${s.scale}rem`,
                transform: 'translate(-50%, -50%)',
                animation: `strawberryBurst 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards`,
                '--end-x': `${(endX - 50)}px`,
                '--end-y': `${(endY - 50)}px`,
                '--spin': `${s.spin}deg`,
              } as React.CSSProperties}
            >
              🍓
            </span>
          )
        })}
      </span>
    </span>
  )
}


export default function Home({ installCommand }: HomeProps) {
  const [showFullLogo, setShowFullLogo] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      // Show full logo after scrolling past the hero logo
      setShowFullLogo(window.scrollY > 250)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div className="min-h-screen bg-white">
      <Head title="Inertia.js for Python" />
      {/* Navigation */}
      <nav className="fixed w-full z-50 bg-white border-b border-black">
        <div className="px-6 lg:px-12">
          <div className="flex justify-between h-16 items-center">
            <Logo showFull={showFullLogo} />
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

      {/* Hero Section - Swiss Grid Layout */}
      <section className="pt-16">
        <div className="grid grid-cols-12">
          {/* Left content area */}
          <div className="col-span-12 lg:col-span-7 flex flex-col justify-between p-6 lg:p-12 border-r-0 lg:border-r border-black">
            {/* Main headline */}
            <div className="pt-8 lg:pt-16">
              <div className="mb-4 text-sm font-mono uppercase tracking-widest text-gray-500">
                Python + Inertia.js
              </div>
              <h1 className="mb-8">
                <img
                  src="/static/logo-full.svg"
                  alt="Cross-Inertia"
                  className="h-auto w-auto max-w-[580px]"
                />
              </h1>
              <p className="text-xl lg:text-2xl text-gray-700 max-w-xl leading-relaxed">
                Build modern single-page applications with Django, Flask, and FastAPI.
                No API required.
              </p>
            </div>

            {/* Bottom actions */}
            <div className="flex flex-col sm:flex-row gap-4 pb-8 lg:pb-16">
              <Link
                href="/docs"
                className="inline-flex items-center justify-center px-8 py-4 bg-black text-white font-bold text-lg hover:bg-primary-500 transition-colors border border-black"
              >
                Get Started
              </Link>
              <InstallCommand command={installCommand} />
            </div>
          </div>

          {/* Right decorative area - Framework blueprints */}
          <div className="col-span-12 lg:col-span-5 bg-primary-500 hidden lg:block">
            <img
              src="/static/hero-frameworks.jpg"
              alt="Framework blueprints - FastAPI, Vue, Svelte, Django, React, Flask"
              className="w-full h-auto"
            />
          </div>
        </div>
      </section>

      {/* Features Section - Grid-based */}
      <section className="border-t border-black">
        <div className="grid grid-cols-12">
          {/* Section header */}
          <div className="col-span-12 lg:col-span-4 p-6 lg:p-12 border-b lg:border-b-0 lg:border-r border-black">
            <div className="text-sm font-mono uppercase tracking-widest text-gray-500 mb-4">
              Why Cross-Inertia
            </div>
            <h2 className="text-4xl lg:text-5xl font-bold tracking-tight">
              Modern
              <br />
              Monoliths
            </h2>
          </div>

          {/* Features grid */}
          <div className="col-span-12 lg:col-span-8 grid grid-cols-1 sm:grid-cols-2">
            <div className="p-6 lg:p-8 border-b sm:border-r border-black">
              <div className="text-6xl font-bold text-primary-500 mb-4">01</div>
              <h3 className="text-xl font-bold mb-2">No API Needed</h3>
              <p className="text-gray-600">
                Skip building a separate REST or <StrawberryConfetti>GraphQL</StrawberryConfetti> API. Your controllers return page components directly.
              </p>
            </div>
            <div className="p-6 lg:p-8 border-b border-black">
              <div className="text-6xl font-bold text-primary-500 mb-4">02</div>
              <h3 className="text-xl font-bold mb-2">Server-Side Routing</h3>
              <p className="text-gray-600">
                Use your familiar Python routing. No client-side router needed.
              </p>
            </div>
            <div className="p-6 lg:p-8 border-b sm:border-b-0 sm:border-r border-black">
              <div className="text-6xl font-bold text-primary-500 mb-4">03</div>
              <h3 className="text-xl font-bold mb-2">Full SPA Experience</h3>
              <p className="text-gray-600">
                Users get the speed and responsiveness of a single-page app without the complexity.
              </p>
            </div>
            <div className="p-6 lg:p-8">
              <div className="text-6xl font-bold text-primary-500 mb-4">04</div>
              <h3 className="text-xl font-bold mb-2">SEO Friendly</h3>
              <p className="text-gray-600">
                With server-side rendering support, your pages are fully indexable by search engines.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Code example section */}
      <InteractiveCodeExample />

      {/* CTA Section */}
      <section className="border-t border-black">
        <div className="grid grid-cols-12 items-center">
          <div className="col-span-12 lg:col-span-8 p-6 lg:p-12">
            <h2 className="text-4xl lg:text-6xl font-bold tracking-tight mb-4">
              Ready to start?
            </h2>
            <p className="text-xl text-gray-600 mb-8 max-w-2xl">
              Get up and running with Cross-Inertia in minutes. Check out our documentation to learn more.
            </p>
            <Link
              href="/docs"
              className="inline-flex items-center justify-center px-8 py-4 bg-primary-500 text-white font-bold text-lg hover:bg-black transition-colors border border-primary-500 hover:border-black"
            >
              Read the Docs
            </Link>
          </div>
          <Link
            href="/docs"
            className="col-span-12 lg:col-span-4 h-full bg-primary-500 hidden lg:flex items-center justify-center p-12 hover:bg-black transition-colors"
          >
            <div className="text-white text-8xl font-bold">
              &rarr;
            </div>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-black py-8">
        <div className="px-6 lg:px-12 flex flex-col md:flex-row justify-between items-center gap-6">
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
