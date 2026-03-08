import { useState } from 'react'
import { router } from '@inertiajs/react'
import Layout from '../components/Layout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface Offer {
  code: string
  description: string
}

interface OnceDemoProps {
  title: string
  message: string
  request_count: number
  timestamp: string
  once_evaluations: number
  offer: Offer
}

export default function OnceDemo({
  title,
  message,
  request_count,
  timestamp,
  once_evaluations,
  offer,
}: OnceDemoProps) {
  const [loadingDiagnostics, setLoadingDiagnostics] = useState(false)
  const [loadingOffer, setLoadingOffer] = useState(false)

  const reloadDiagnostics = () => {
    setLoadingDiagnostics(true)
    router.reload({
      only: ['request_count', 'timestamp', 'once_evaluations'],
      onFinish: () => setLoadingDiagnostics(false),
    })
  }

  const refreshOffer = () => {
    setLoadingOffer(true)
    router.reload({
      only: ['offer', 'request_count', 'timestamp', 'once_evaluations'],
      onFinish: () => setLoadingOffer(false),
    })
  }

  return (
    <Layout title={title}>
      <p className="text-lg text-muted-foreground mb-8">{message}</p>

      <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Remembered Once Prop</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-lg border border-zinc-200 bg-zinc-50 p-4">
              <p className="text-sm uppercase tracking-wide text-zinc-500">Offer code</p>
              <p className="mt-2 text-3xl font-semibold" data-testid="offer-code">
                {offer.code}
              </p>
              <p className="mt-3 text-sm text-zinc-600" data-testid="offer-description">
                {offer.description}
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <Button
                data-testid="reload-diagnostics"
                disabled={loadingDiagnostics}
                onClick={reloadDiagnostics}
                variant="outline"
              >
                {loadingDiagnostics ? 'Reloading...' : 'Reload Diagnostics'}
              </Button>
              <Button
                data-testid="refresh-offer"
                disabled={loadingOffer}
                onClick={refreshOffer}
              >
                {loadingOffer ? 'Refreshing...' : 'Refresh Offer'}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Server Diagnostics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm text-zinc-600">
            <div>
              <p className="uppercase tracking-wide text-zinc-500">Route requests</p>
              <p className="mt-1 text-2xl font-semibold text-zinc-900" data-testid="request-count">
                {request_count}
              </p>
            </div>
            <div>
              <p className="uppercase tracking-wide text-zinc-500">Once evaluations</p>
              <p
                className="mt-1 text-2xl font-semibold text-zinc-900"
                data-testid="once-evaluations"
              >
                {once_evaluations}
              </p>
            </div>
            <div>
              <p className="uppercase tracking-wide text-zinc-500">Last response</p>
              <p className="mt-1 font-mono text-xs text-zinc-700" data-testid="timestamp">
                {timestamp}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-8 border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle>How to read this demo</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-zinc-700">
          <p>
            <code className="rounded bg-white px-1 py-0.5">Reload Diagnostics</code> triggers a
            partial reload that does not request the once prop. The browser should keep the
            existing offer value, and the server should not evaluate it again.
          </p>
          <p>
            <code className="rounded bg-white px-1 py-0.5">Refresh Offer</code> explicitly requests
            the once prop, so the server evaluates it again and the offer code changes.
          </p>
        </CardContent>
      </Card>
    </Layout>
  )
}
