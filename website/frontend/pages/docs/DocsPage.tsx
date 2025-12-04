import { DocsLayout } from '@/components/Layout'
import { Markdown } from '@/components/Markdown'

interface DocsPageProps {
  content: {
    title: string
    description: string
    body: string
  }
}

export default function DocsPage({ content }: DocsPageProps) {
  return (
    <DocsLayout title={content?.title ?? ''} description={content?.description}>
      <Markdown content={content?.body ?? ''} />
    </DocsLayout>
  )
}
