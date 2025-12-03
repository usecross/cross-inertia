import { useEffect, useState } from 'react'
import { cn } from '@/lib/utils'

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
      const { codeToHtml } = await import('shiki')
      const highlighted = await codeToHtml(code.trim(), {
        lang: language,
        theme: 'github-dark',
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
    <div className={cn('group relative overflow-hidden rounded-lg', className)}>
      {filename && (
        <div className="flex items-center gap-2 border-b border-gray-700 bg-gray-800 px-4 py-2 text-sm text-gray-400">
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
        className="absolute right-2 top-2 z-10 rounded-md bg-gray-700/50 px-2 py-1 text-xs text-gray-400 opacity-0 transition-opacity hover:bg-gray-600 hover:text-white group-hover:opacity-100"
      >
        {copied ? 'Copied!' : 'Copy'}
      </button>
      {html ? (
        <div
          className={cn(
            'overflow-x-auto text-sm',
            showLineNumbers && '[&_code]:grid [&_code]:grid-cols-[auto_1fr]'
          )}
          dangerouslySetInnerHTML={{ __html: html }}
        />
      ) : (
        <pre className="overflow-x-auto bg-gray-900 p-4 text-sm text-gray-300">
          <code>{code.trim()}</code>
        </pre>
      )}
    </div>
  )
}

// Simple inline code component
export function InlineCode({ children }: { children: React.ReactNode }) {
  return (
    <code className="rounded bg-gray-100 px-1.5 py-0.5 text-sm font-medium text-gray-800 dark:bg-gray-800 dark:text-gray-200">
      {children}
    </code>
  )
}
