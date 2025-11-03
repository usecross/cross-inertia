import { Link } from '@inertiajs/react'
import Layout from '../components/Layout'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AlertCircle, Home } from 'lucide-react'

interface ErrorProps {
  title: string
  message: string
}

export default function Error({ title, message }: ErrorProps) {
  return (
    <Layout title={title}>
      <Card className="border-destructive bg-destructive/5 max-w-2xl mx-auto">
        <CardContent className="pt-6 text-center">
          <AlertCircle className="h-16 w-16 text-destructive mx-auto mb-4" />
          <p className="text-xl text-destructive mb-6">
            {message}
          </p>
          <Button asChild>
            <Link href="/">
              <Home className="mr-2 h-4 w-4" />
              Go Home
            </Link>
          </Button>
        </CardContent>
      </Card>
    </Layout>
  )
}
