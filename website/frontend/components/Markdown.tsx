import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'
import { CodeBlock } from './CodeBlock'

interface MarkdownProps {
  content: string
}

export function Markdown({ content }: MarkdownProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeRaw]}
      components={{
        // Custom code block rendering with syntax highlighting
        code({ node, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '')
          const isInline = !match && !className

          if (isInline) {
            return (
              <code
                className="rounded bg-gray-100 px-1.5 py-0.5 text-sm font-medium text-gray-800 dark:bg-gray-800 dark:text-gray-200"
                {...props}
              >
                {children}
              </code>
            )
          }

          return (
            <CodeBlock
              code={String(children).replace(/\n$/, '')}
              language={match ? match[1] : 'text'}
            />
          )
        },
        // Custom link styling
        a({ href, children }) {
          const isExternal = href?.startsWith('http')
          return (
            <a
              href={href}
              className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
              {...(isExternal ? { target: '_blank', rel: 'noopener noreferrer' } : {})}
            >
              {children}
            </a>
          )
        },
        // Tables
        table({ children }) {
          return (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">{children}</table>
            </div>
          )
        },
        th({ children }) {
          return (
            <th className="border-b border-gray-200 bg-gray-50 px-4 py-2 font-semibold dark:border-gray-700 dark:bg-gray-800">
              {children}
            </th>
          )
        },
        td({ children }) {
          return (
            <td className="border-b border-gray-200 px-4 py-2 dark:border-gray-700">
              {children}
            </td>
          )
        },
      }}
    >
      {content}
    </ReactMarkdown>
  )
}
