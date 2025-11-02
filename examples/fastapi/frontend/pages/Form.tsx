import React from 'react'
import { useForm } from '@inertiajs/react'
import Layout from '../components/Layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { AlertCircle } from 'lucide-react'

interface FormProps {
  title: string
  message: string
  errors?: Record<string, string>
}

export default function Form({ title, message, errors = {} }: FormProps) {
  const { data, setData, post, processing } = useForm({
    name: '',
    email: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    post('/form')
  }

  return (
    <Layout title={title}>
      <p className="text-muted-foreground mb-8">{message}</p>

      {Object.keys(errors).length > 0 && (
        <Card className="border-destructive bg-destructive/5 mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5" />
              Validation Errors
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1 text-sm text-destructive">
              {Object.entries(errors).map(([field, error]) => (
                <li key={field}>
                  <strong className="font-semibold capitalize">{field}:</strong> {error}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Example Form</CardTitle>
          <CardDescription>Fill out the form below to see validation in action</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                type="text"
                value={data.name}
                onChange={(e) => setData('name', e.target.value)}
                className={errors.name ? 'border-destructive' : ''}
                placeholder="Enter your name"
              />
              {errors.name && (
                <p className="text-sm text-destructive">{errors.name}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={data.email}
                onChange={(e) => setData('email', e.target.value)}
                className={errors.email ? 'border-destructive' : ''}
                placeholder="Enter your email"
              />
              {errors.email && (
                <p className="text-sm text-destructive">{errors.email}</p>
              )}
            </div>

            <Button type="submit" disabled={processing} className="w-full sm:w-auto">
              {processing ? 'Submitting...' : 'Submit'}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card className="max-w-2xl mt-6 bg-muted/50">
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">
            <strong>Note:</strong> This form will always return validation errors to demonstrate error handling.
          </p>
        </CardContent>
      </Card>
    </Layout>
  )
}
