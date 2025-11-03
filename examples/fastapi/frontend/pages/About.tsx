import Layout from '../components/Layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface AboutProps {
  title: string
  description: string
  tech_stack: Record<string, string>
}

export default function About({ title, description, tech_stack }: AboutProps) {
  return (
    <Layout title={title}>
      <p className="text-lg text-muted-foreground mb-8">{description}</p>

      <h2 className="text-2xl font-bold mb-4">Technology Stack</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {Object.entries(tech_stack).map(([key, value]) => (
          <Card key={key}>
            <CardHeader>
              <CardTitle className="text-lg">{key}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xl font-bold">{value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="bg-yellow-50 dark:bg-yellow-950 border-yellow-200 dark:border-yellow-800">
        <CardHeader>
          <CardTitle>Why Inertia.js?</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Inertia.js allows you to build modern single-page apps using classic server-side routing and controllers.
            You get all the benefits of client-side rendering without the complexity of building an API.
          </p>
        </CardContent>
      </Card>
    </Layout>
  )
}
