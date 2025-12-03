import { Link } from '@inertiajs/react'
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

function Logo() {
  return (
    <Link href="/" className="flex items-center">
      <img src="/static/logo.svg" alt="Cross-Inertia" className="h-8" />
    </Link>
  )
}


export default function Home({ installCommand }: HomeProps) {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed w-full z-50 bg-white border-b border-black">
        <div className="px-6 lg:px-12">
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

      {/* Hero Section - Swiss Grid Layout */}
      <section className="pt-16 min-h-screen">
        <div className="grid grid-cols-12 min-h-[calc(100vh-4rem)]">
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
          <div className="col-span-12 lg:col-span-5 bg-primary-500 relative overflow-hidden hidden lg:block">
            <img
              src="/static/hero-frameworks.jpg"
              alt="Framework blueprints - FastAPI, Vue, Svelte, Django, React, Flask"
              className="w-full h-full object-cover"
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
                Skip building a separate REST or GraphQL API. Your controllers return page components directly.
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
                {'        '}&#123;<span className="text-green-400">"user"</span>: user&#125;{'\n'}
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
                {'  '}user: &#123; name: <span className="text-cyan-600">string</span>; email: <span className="text-cyan-600">string</span> &#125;{'\n'}
                &#125;{'\n'}
                {'\n'}
                <span className="text-pink-600">export default function</span> <span className="text-blue-600">Show</span>(&#123; user &#125;: <span className="text-cyan-600">Props</span>) &#123;{'\n'}
                {'  '}<span className="text-pink-600">return</span> ({'\n'}
                {'    '}<span className="text-green-700">&lt;Layout&gt;</span>{'\n'}
                {'      '}<span className="text-green-700">&lt;h1&gt;</span>&#123;user.name&#125;<span className="text-green-700">&lt;/h1&gt;</span>{'\n'}
                {'      '}<span className="text-green-700">&lt;p&gt;</span>&#123;user.email&#125;<span className="text-green-700">&lt;/p&gt;</span>{'\n'}
                {'    '}<span className="text-green-700">&lt;/Layout&gt;</span>{'\n'}
                {'  '}){'\n'}
                &#125;
              </code>
            </pre>
          </div>
        </div>
      </section>

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
          <div className="font-bold text-lg">
            <span className="text-primary-500">Cross</span>Inertia
          </div>
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
