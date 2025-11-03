import { Link } from '@inertiajs/react'
import Layout from '../../components/Layout'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ArrowLeft } from 'lucide-react'

interface User {
  id: number
  name: string
  email: string
  role: string
  joined: string
}

interface UsersShowProps {
  title: string
  user: User
}

export default function UsersShow({ title, user }: UsersShowProps) {
  return (
    <Layout title={title}>
      <div className="mb-6">
        <Button variant="ghost" asChild>
          <Link href="/users">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Users
          </Link>
        </Button>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="space-y-6">
            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Name
              </label>
              <p className="mt-1 text-2xl font-bold">{user.name}</p>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Email
              </label>
              <p className="mt-1 text-lg">{user.email}</p>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground block mb-2">
                Role
              </label>
              <Badge variant={user.role === 'Admin' ? 'default' : 'secondary'} className="text-sm px-3 py-1">
                {user.role}
              </Badge>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Joined
              </label>
              <p className="mt-1 text-lg">{user.joined}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </Layout>
  )
}
