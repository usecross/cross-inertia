import React, { useState } from 'react'
import { useForm } from '@inertiajs/react'
import Layout from '../components/Layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'

interface PartialErrorsDemoProps {
  title: string
  message: string
  profile: { name: string }
}

export default function PartialErrorsDemo({ title, message, profile }: PartialErrorsDemoProps) {
  const form = useForm({ name: profile.name })
  const [result, setResult] = useState<'success' | 'error' | null>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    form.post('/partial-errors-demo', {
      only: ['profile'],
      onSuccess: () => setResult('success'),
      onError: () => setResult('error'),
    })
  }

  return (
    <Layout title={title}>
      <p className="text-muted-foreground mb-8">{message}</p>

      <Card className="max-w-md">
        <CardHeader>
          <CardTitle>Profile</CardTitle>
          <CardDescription>
            Saved name: <span data-testid="saved-name">{profile.name}</span>
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="partial-name">Name</Label>
              <Input
                id="partial-name"
                value={form.data.name}
                onChange={(e) => form.setData('name', e.target.value)}
                className={form.errors.name ? 'border-destructive' : ''}
                data-testid="partial-name"
              />
              {form.errors.name && (
                <p className="text-sm text-destructive" data-testid="partial-name-error">
                  {form.errors.name}
                </p>
              )}
            </div>

            <Button type="submit" disabled={form.processing} className="w-full" data-testid="partial-submit">
              {form.processing ? 'Saving...' : 'Save'}
            </Button>

            {result && (
              <p className="text-sm" data-testid="partial-result">
                {result}
              </p>
            )}
          </form>
        </CardContent>
      </Card>
    </Layout>
  )
}
