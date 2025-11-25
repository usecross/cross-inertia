import React from 'react'
import { useForm, usePage } from '@inertiajs/react'
import Layout from '../components/Layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { AlertCircle, LogIn, UserPlus, CheckCircle } from 'lucide-react'

interface ErrorBagsDemoProps {
  title: string
  message: string
  errors?: {
    login?: Record<string, string>
    register?: Record<string, string>
  } & Record<string, string>
}

interface SharedProps {
  flash?: {
    message?: string
    category?: string
  }
  [key: string]: unknown
}

export default function ErrorBagsDemo({ title, message, errors = {} }: ErrorBagsDemoProps) {
  const { props } = usePage<SharedProps>()
  const flash = props.flash

  // Login form with error bag
  const loginForm = useForm({
    email: '',
    password: '',
  })

  // Register form with error bag
  const registerForm = useForm({
    name: '',
    email: '',
    password: '',
  })

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    loginForm.post('/error-bags-demo/login', {
      errorBag: 'login',
    })
  }

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault()
    registerForm.post('/error-bags-demo/register', {
      errorBag: 'register',
    })
  }

  // Get errors for each form (scoped by error bag)
  const loginErrors = errors.login || {}
  const registerErrors = errors.register || {}

  return (
    <Layout title={title}>
      <p className="text-muted-foreground mb-8">{message}</p>

      {/* Success Flash Message */}
      {flash?.message && (
        <div className="bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-md p-4 mb-6 max-w-4xl" data-testid="success-message">
          <div className="flex items-center gap-2 text-green-700 dark:text-green-300">
            <CheckCircle className="h-5 w-5" />
            <span className="font-medium">{flash.message}</span>
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6 max-w-4xl">
        {/* Login Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <LogIn className="h-5 w-5" />
              Login Form
            </CardTitle>
            <CardDescription>
              Uses error bag: <code className="bg-muted px-1 rounded">login</code>
            </CardDescription>
          </CardHeader>
          <CardContent>
            {Object.keys(loginErrors).length > 0 && (
              <div className="bg-destructive/10 border border-destructive/30 rounded-md p-3 mb-4" data-testid="login-errors">
                <div className="flex items-center gap-2 text-destructive font-medium mb-2">
                  <AlertCircle className="h-4 w-4" />
                  Login Errors
                </div>
                <ul className="space-y-1 text-sm text-destructive">
                  {Object.entries(loginErrors).map(([field, error]) => (
                    <li key={field}>
                      <strong className="capitalize">{field}:</strong> {error}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="login-email">Email</Label>
                <Input
                  id="login-email"
                  type="text"
                  value={loginForm.data.email}
                  onChange={(e) => loginForm.setData('email', e.target.value)}
                  className={loginErrors.email ? 'border-destructive' : ''}
                  placeholder="Enter your email"
                  data-testid="login-email"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="login-password">Password</Label>
                <Input
                  id="login-password"
                  type="password"
                  value={loginForm.data.password}
                  onChange={(e) => loginForm.setData('password', e.target.value)}
                  className={loginErrors.password ? 'border-destructive' : ''}
                  placeholder="Enter your password"
                  data-testid="login-password"
                />
              </div>

              <Button type="submit" disabled={loginForm.processing} className="w-full" data-testid="login-submit">
                {loginForm.processing ? 'Logging in...' : 'Login'}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Register Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <UserPlus className="h-5 w-5" />
              Register Form
            </CardTitle>
            <CardDescription>
              Uses error bag: <code className="bg-muted px-1 rounded">register</code>
            </CardDescription>
          </CardHeader>
          <CardContent>
            {Object.keys(registerErrors).length > 0 && (
              <div className="bg-destructive/10 border border-destructive/30 rounded-md p-3 mb-4" data-testid="register-errors">
                <div className="flex items-center gap-2 text-destructive font-medium mb-2">
                  <AlertCircle className="h-4 w-4" />
                  Registration Errors
                </div>
                <ul className="space-y-1 text-sm text-destructive">
                  {Object.entries(registerErrors).map(([field, error]) => (
                    <li key={field}>
                      <strong className="capitalize">{field}:</strong> {error}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <form onSubmit={handleRegister} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="register-name">Name</Label>
                <Input
                  id="register-name"
                  type="text"
                  value={registerForm.data.name}
                  onChange={(e) => registerForm.setData('name', e.target.value)}
                  className={registerErrors.name ? 'border-destructive' : ''}
                  placeholder="Enter your name"
                  data-testid="register-name"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="register-email">Email</Label>
                <Input
                  id="register-email"
                  type="text"
                  value={registerForm.data.email}
                  onChange={(e) => registerForm.setData('email', e.target.value)}
                  className={registerErrors.email ? 'border-destructive' : ''}
                  placeholder="Enter your email"
                  data-testid="register-email"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="register-password">Password</Label>
                <Input
                  id="register-password"
                  type="password"
                  value={registerForm.data.password}
                  onChange={(e) => registerForm.setData('password', e.target.value)}
                  className={registerErrors.password ? 'border-destructive' : ''}
                  placeholder="Enter your password (min 8 chars)"
                  data-testid="register-password"
                />
              </div>

              <Button type="submit" disabled={registerForm.processing} className="w-full" data-testid="register-submit">
                {registerForm.processing ? 'Registering...' : 'Register'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>

      <Card className="max-w-4xl mt-6 bg-muted/50">
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">
            <strong>How Error Bags Work:</strong> Each form uses a different <code className="bg-background px-1 rounded">errorBag</code> option.
            When validation fails, the server returns errors scoped under that key. This allows multiple forms on the same page
            to have independent validation errors without conflicts.
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            Without error bags: <code className="bg-background px-1 rounded">errors = {'{ email: "Invalid" }'}</code>
          </p>
          <p className="text-sm text-muted-foreground">
            With error bag "login": <code className="bg-background px-1 rounded">errors = {'{ login: { email: "Invalid" } }'}</code>
          </p>
        </CardContent>
      </Card>
    </Layout>
  )
}
