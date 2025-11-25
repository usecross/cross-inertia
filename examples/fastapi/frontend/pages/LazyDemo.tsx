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
  statistics?: Statistics // Lazy prop - only present after partial reload
}

export default function LazyDemo({ title, message, statistics }: LazyDemoProps) {
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

      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Lazy Props Demo</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4">
            The statistics below are loaded lazily. They are NOT included in the initial page load,
            reducing initial payload size. Click the button to load them via a partial reload.
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
        <CardContent>
          <p className="text-muted-foreground mb-2">
            <strong>Backend:</strong> The statistics prop is wrapped with <code className="bg-muted px-1 rounded">lazy(get_statistics)</code>
          </p>
          <p className="text-muted-foreground mb-2">
            <strong>Initial load:</strong> Lazy props are excluded, keeping the response small
          </p>
          <p className="text-muted-foreground">
            <strong>Partial reload:</strong> Using <code className="bg-muted px-1 rounded">router.reload(&#123; only: ['statistics'] &#125;)</code> triggers
            evaluation of the lazy prop
          </p>
        </CardContent>
      </Card>
    </Layout>
  )
}
