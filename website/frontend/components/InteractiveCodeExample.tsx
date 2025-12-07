import { useState } from 'react'

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
        className="absolute -inset-x-1 rounded border border-primary-500"
        style={{
          top: '-3px',
          bottom: '-3px',
          opacity: isActive ? 1 : 0,
          transition: 'opacity 300ms ease-out',
          backgroundColor: 'color-mix(in srgb, var(--color-primary-500, #648C57) 30%, transparent)',
        }}
      />
      <span className="relative">{children}</span>
    </span>
  )
}

export function InteractiveCodeExample() {
  const [highlighted, setHighlighted] = useState<HighlightKey>(null)

  return (
    <section className="border-t border-gray-200">
      <div className="grid grid-cols-12">
        <div className="col-span-12 lg:col-span-6 p-4 lg:p-10 border-b lg:border-b-0 lg:border-r border-gray-200 bg-black text-white">
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
        <div className="col-span-12 lg:col-span-6 p-4 lg:p-10 bg-gray-50">
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
