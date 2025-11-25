import { useState } from 'react'
import { router } from '@inertiajs/react'
import Layout from '../components/Layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

interface Statistics {
  total_cats: number
  total_shelters: number
  breeds: string[]
  average_age: number
}

interface LazyDemoProps {
  title: string
  message: string
  statistics?: Statistics // Optional prop - only present after partial reload
  timestamp: string // Always prop - always included, even in partial reloads
}

export default function LazyDemo({ title, message, statistics, timestamp }: LazyDemoProps) {
  const [loading, setLoading] = useState(false)

  const loadStatistics = () => {
    setLoading(true)
    router.reload({
      only: ['statistics'],
      onFinish: () => setLoading(false),
    })
  }

  return (
    <Layout title={title}>
      <p className="text-lg text-muted-foreground mb-8">{message}</p>

      {/* Always prop: timestamp */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Always Prop Demo</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-2">
            The timestamp below is wrapped with <code className="bg-muted px-1 rounded">always()</code>.
            It's included in every response, even during partial reloads.
          </p>
          <p className="text-2xl font-mono" data-testid="timestamp">
            {timestamp}
          </p>
        </CardContent>
      </Card>

      {/* Optional prop: statistics */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Optional Prop Demo</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4">
            The statistics below are wrapped with <code className="bg-muted px-1 rounded">optional()</code>.
            They are NOT included in the initial page load, reducing initial payload size.
            Click the button to load them via a partial reload.
          </p>

          {!statistics ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground mb-4" data-testid="not-loaded-message">
                Statistics not yet loaded
              </p>
              <Button
                onClick={loadStatistics}
                disabled={loading}
                data-testid="load-statistics-button"
              >
                {loading ? 'Loading...' : 'Load Statistics'}
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4" data-testid="statistics-container">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Total Cats</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold" data-testid="total-cats">{statistics.total_cats}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Total Shelters</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold" data-testid="total-shelters">{statistics.total_shelters}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Average Age</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold" data-testid="average-age">
                    {statistics.average_age.toFixed(1)} years
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Breeds</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground" data-testid="breeds-count">
                    {statistics.breeds.length} unique breeds
                  </p>
                </CardContent>
              </Card>
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
        <CardHeader>
          <CardTitle>How it works</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">optional() - Deferred Loading</h3>
            <p className="text-muted-foreground mb-2">
              <strong>Backend:</strong> <code className="bg-muted px-1 rounded">optional(get_statistics)</code>
            </p>
            <p className="text-muted-foreground mb-2">
              <strong>Behavior:</strong> Excluded on initial load, only included when explicitly requested
            </p>
            <p className="text-muted-foreground">
              <strong>Usage:</strong> <code className="bg-muted px-1 rounded">router.reload(&#123; only: ['statistics'] &#125;)</code>
            </p>
          </div>

          <div>
            <h3 className="font-semibold mb-2">always() - Persistent Props</h3>
            <p className="text-muted-foreground mb-2">
              <strong>Backend:</strong> <code className="bg-muted px-1 rounded">always(get_timestamp)</code>
            </p>
            <p className="text-muted-foreground mb-2">
              <strong>Behavior:</strong> Always included, even during partial reloads
            </p>
            <p className="text-muted-foreground">
              <strong>Use case:</strong> Flash messages, notifications, CSRF tokens
            </p>
          </div>
        </CardContent>
      </Card>
    </Layout>
  )
}
