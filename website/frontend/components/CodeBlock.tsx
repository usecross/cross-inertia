import { useEffect, useState } from 'react'
import { cn } from '@/lib/utils'
import { getHighlighter } from '@/lib/shiki'

interface CodeBlockProps {
  code: string
  language?: string
  filename?: string
  showLineNumbers?: boolean
  className?: string
}

export function CodeBlock({
  code,
  language = 'python',
  filename,
  showLineNumbers = false,
  className,
}: CodeBlockProps) {
  const [html, setHtml] = useState<string>('')
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    async function highlight() {
      const highlighter = await getHighlighter()
      const langs = highlighter.getLoadedLanguages()
      const lang = langs.includes(language) ? language : 'text'
      const highlighted = highlighter.codeToHtml(code.trim(), {
        lang,
        theme: 'github-dark-dimmed',
      })
      setHtml(highlighted)
    }
    highlight()
  }, [code, language])

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(code.trim())
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={cn('group relative overflow-hidden bg-black border border-black', className)}>
      {filename && (
        <div className="flex items-center gap-2 border-b border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-400">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          {filename}
        </div>
      )}
      <button
        onClick={copyToClipboard}
        className="absolute right-2 top-2 z-10 rounded-md bg-slate-700/50 px-2 py-1 text-xs text-slate-400 opacity-0 transition-opacity hover:bg-slate-600 hover:text-white group-hover:opacity-100"
      >
        {copied ? 'Copied!' : 'Copy'}
      </button>
      {html ? (
        <div
          className={cn(
            'overflow-x-auto text-sm [&_pre]:!m-0 [&_code]:!p-4',
            showLineNumbers && '[&_code]:grid [&_code]:grid-cols-[auto_1fr]'
          )}
          dangerouslySetInnerHTML={{ __html: html }}
        />
      ) : (
        <pre className="shiki overflow-x-auto !m-0 !bg-black">
          <code className="block p-4 text-sm leading-relaxed text-gray-300">{code.trim()}</code>
        </pre>
      )}
    </div>
  )
}

// Simple inline code component
export function InlineCode({ children }: { children: React.ReactNode }) {
  return (
    <code className="rounded bg-slate-100 px-1.5 py-0.5 text-sm font-medium text-slate-800">
      {children}
    </code>
  )
}
