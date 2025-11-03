import Layout from '../components/Layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { CheckCircle2 } from 'lucide-react'

interface HomeProps {
  title: string
  message: string
  features: string[]
}

export default function Home({ title, message, features }: HomeProps) {
  return (
    <Layout title={title}>
      <p className="text-lg text-muted-foreground mb-8 leading-relaxed">
        {message}
      </p>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Features</CardTitle>
          <CardDescription>What's included in this demo</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-3">
            {features.map((feature, index) => (
              <li key={index} className="flex items-start gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                <span>{feature}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card className="border-l-4 border-l-primary bg-primary/5">
        <CardHeader>
          <CardTitle>Try It Out</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-4">Navigate using the menu above. Notice how:</p>
          <ul className="space-y-2 list-disc list-inside">
            <li>Pages load instantly without full page refreshes</li>
            <li>The URL updates correctly</li>
            <li>Browser back/forward buttons work</li>
            <li>You can still refresh the page and it works</li>
          </ul>
        </CardContent>
      </Card>
    </Layout>
  )
}
