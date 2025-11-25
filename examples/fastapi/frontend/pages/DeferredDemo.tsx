import { Deferred } from '@inertiajs/react'
import Layout from '../components/Layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface Analytics {
  total_cats: number
  total_shelters: number
  breeds_count: number
  average_age: number
}

interface Notification {
  id: number
  message: string
  time: string
}

interface Cat {
  id: number
  name: string
  breed: string
  age: number
}

interface DeferredDemoProps {
  title: string
  message: string
  timestamp: string
  analytics?: Analytics
  notifications?: Notification[]
  recommendations?: Cat[]
}

function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-8">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      <span className="ml-2 text-muted-foreground">Loading...</span>
    </div>
  )
}

export default function DeferredDemo({
  title,
  message,
  timestamp,
  analytics,
  notifications,
  recommendations,
}: DeferredDemoProps) {
  return (
    <Layout title={title}>
      <p className="text-lg text-muted-foreground mb-8">{message}</p>

      {/* Timestamp (regular prop - loaded immediately) */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Initial Load (Regular Prop)</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-2">
            The timestamp below is a regular prop - loaded with the initial page.
          </p>
          <p className="text-2xl font-mono" data-testid="timestamp">
            {timestamp}
          </p>
        </CardContent>
      </Card>

      {/* Deferred analytics and notifications (default group) */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Deferred Props - Default Group</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4">
            These props are wrapped with <code className="bg-muted px-1 rounded">defer()</code>.
            They load automatically after the page renders.
          </p>

          <Deferred data={['analytics', 'notifications']} fallback={<LoadingSpinner />}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              {analytics && (
                <>
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Total Cats</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-3xl font-bold" data-testid="total-cats">
                        {analytics.total_cats}
                      </p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Total Shelters</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-3xl font-bold" data-testid="total-shelters">
                        {analytics.total_shelters}
                      </p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Average Age</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-3xl font-bold" data-testid="average-age">
                        {analytics.average_age} years
                      </p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Breeds</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-3xl font-bold" data-testid="breeds-count">
                        {analytics.breeds_count}
                      </p>
                    </CardContent>
                  </Card>
                </>
              )}
            </div>

            {notifications && notifications.length > 0 && (
              <div>
                <h3 className="font-semibold mb-2">Notifications</h3>
                <div className="space-y-2">
                  {notifications.map((notif) => (
                    <div
                      key={notif.id}
                      className="p-3 bg-muted rounded-lg flex justify-between"
                    >
                      <span>{notif.message}</span>
                      <span className="text-muted-foreground text-sm">{notif.time}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Deferred>
        </CardContent>
      </Card>

      {/* Deferred recommendations (sidebar group) */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Deferred Props - Sidebar Group</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4">
            This prop uses <code className="bg-muted px-1 rounded">defer(get_recommendations, group="sidebar")</code>.
            It loads in parallel with the default group.
          </p>

          <Deferred data="recommendations" fallback={<LoadingSpinner />}>
            {recommendations && recommendations.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {recommendations.map((cat) => (
                  <Card key={cat.id}>
                    <CardHeader>
                      <CardTitle className="text-lg">{cat.name}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-muted-foreground">
                        {cat.breed}, {cat.age} years old
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </Deferred>
        </CardContent>
      </Card>

      <Card className="bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
        <CardHeader>
          <CardTitle>How Deferred Props Work</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">defer() - Automatic Deferred Loading</h3>
            <p className="text-muted-foreground mb-2">
              <strong>Backend:</strong> <code className="bg-muted px-1 rounded">defer(get_analytics)</code>
            </p>
            <p className="text-muted-foreground mb-2">
              <strong>Behavior:</strong> Excluded on initial load, automatically fetched after page renders
            </p>
            <p className="text-muted-foreground">
              <strong>Frontend:</strong> Use <code className="bg-muted px-1 rounded">&lt;Deferred data="analytics"&gt;</code> to render with loading state
            </p>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Groups - Parallel Loading</h3>
            <p className="text-muted-foreground mb-2">
              <strong>Backend:</strong> <code className="bg-muted px-1 rounded">defer(get_data, group="sidebar")</code>
            </p>
            <p className="text-muted-foreground">
              <strong>Behavior:</strong> Props in different groups load in parallel for better performance
            </p>
          </div>

          <div>
            <h3 className="font-semibold mb-2">vs optional()</h3>
            <p className="text-muted-foreground">
              Unlike <code className="bg-muted px-1 rounded">optional()</code> which requires manual <code className="bg-muted px-1 rounded">router.reload()</code>,
              deferred props load automatically after the page mounts.
            </p>
          </div>
        </CardContent>
      </Card>
    </Layout>
  )
}
