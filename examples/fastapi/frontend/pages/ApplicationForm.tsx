import { useForm, Head, usePage } from '@inertiajs/react'
import Layout from '../components/Layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import type { ApplicationFormPageProps } from '../types'

export default function ApplicationForm({ cat }: ApplicationFormPageProps) {
  const page = usePage<any>()
  const { data, setData, post, processing, errors, recentlySuccessful } = useForm({
    full_name: '',
    email: '',
    phone: '',
    address: '',
    why_adopt: '',
  })
  
  // TEMPORARY: Access errors directly from page props as fallback
  const pageErrors = page.props.errors || {}
  const displayErrors = Object.keys(errors).length > 0 ? errors : pageErrors


  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    post(`/cats/${cat.id}/apply`, {
      preserveScroll: (page) => Object.keys(page.props.errors || {}).length > 0,
    })
  }

  return (
    <>
      <Head title={`Apply to Adopt ${cat.name} | PurrfectHome`} />

      <Layout>
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">Adoption Application</h1>
            <p className="text-muted-foreground">
              Apply to adopt {cat.name}. We'll review your application and get back to you soon!
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Cat Info Sidebar */}
            <div className="lg:col-span-1">
              <Card className="sticky top-6">
                <CardHeader className="pb-4">
                  <CardTitle className="text-lg">You're Applying For</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="aspect-square rounded-lg overflow-hidden bg-muted mb-4">
                    <img
                      src={cat.photo}
                      alt={cat.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <h3 className="font-semibold text-xl mb-2">{cat.name}</h3>
                  <div className="space-y-2 text-sm text-muted-foreground">
                    <p>{cat.age} {cat.age === 1 ? 'year' : 'years'} old • {cat.breed}</p>
                    <p className="font-semibold text-foreground">
                      Adoption Fee: ${cat.adoption_fee}
                    </p>
                    <div className="flex flex-wrap gap-1 pt-2">
                      {cat.personality.slice(0, 3).map((trait) => (
                        <Badge key={trait} variant="secondary" className="text-xs">
                          {trait}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Application Form */}
            <div className="lg:col-span-2">
              <form onSubmit={handleSubmit} className="space-y-6">
                {recentlySuccessful && (
                  <Card className="border-green-500 bg-green-50 dark:bg-green-950">
                    <CardContent className="pt-6">
                      <p className="text-green-800 dark:text-green-200 font-medium">
                        ✓ Application submitted successfully! We'll contact you soon.
                      </p>
                    </CardContent>
                  </Card>
                )}

                {/* Personal Information */}
                <Card>
                  <CardHeader>
                    <CardTitle>Personal Information</CardTitle>
                    <CardDescription>Tell us about yourself</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="full_name">Full Name *</Label>
                      <Input
                        id="full_name"
                        value={data.full_name}
                        onChange={(e) => setData('full_name', e.target.value)}
                        placeholder="John Doe"
                        className={displayErrors.full_name ? 'border-red-500' : ''}
                      />
                      {displayErrors.full_name && (
                        <p className="text-sm text-red-500 mt-1">{displayErrors.full_name}</p>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="email">Email *</Label>
                        <Input
                          id="email"
                          type="email"
                          value={data.email}
                          onChange={(e) => setData('email', e.target.value)}
                          placeholder="john@example.com"
                          className={displayErrors.email ? 'border-red-500' : ''}
                        />
                        {displayErrors.email && (
                          <p className="text-sm text-red-500 mt-1">{displayErrors.email}</p>
                        )}
                      </div>

                      <div>
                        <Label htmlFor="phone">Phone *</Label>
                        <Input
                          id="phone"
                          type="tel"
                          value={data.phone}
                          onChange={(e) => setData('phone', e.target.value)}
                          placeholder="(555) 123-4567"
                          className={displayErrors.phone ? 'border-red-500' : ''}
                        />
                        {displayErrors.phone && (
                          <p className="text-sm text-red-500 mt-1">{displayErrors.phone}</p>
                        )}
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="address">Address *</Label>
                      <Input
                        id="address"
                        value={data.address}
                        onChange={(e) => setData('address', e.target.value)}
                        placeholder="123 Main St, City, State ZIP"
                        className={displayErrors.address ? 'border-red-500' : ''}
                      />
                      {displayErrors.address && (
                        <p className="text-sm text-red-500 mt-1">{displayErrors.address}</p>
                      )}
                    </div>
                  </CardContent>
                </Card>

                {/* Why Adopt */}
                <Card>
                  <CardHeader>
                    <CardTitle>Why Do You Want to Adopt {cat.name}?</CardTitle>
                    <CardDescription>
                      Tell us why you'd be a great match (minimum 50 characters)
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div>
                      <textarea
                        id="why_adopt"
                        value={data.why_adopt}
                        onChange={(e) => setData('why_adopt', e.target.value)}
                        placeholder="I'm looking for a companion who..."
                        rows={6}
                        className={`w-full px-3 py-2 border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-ring ${
                          displayErrors.why_adopt ? 'border-red-500' : 'border-input'
                        }`}
                      />
                      <div className="flex justify-between items-center mt-2">
                        <div>
                          {displayErrors.why_adopt && (
                            <p className="text-sm text-red-500">{displayErrors.why_adopt}</p>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {data.why_adopt.length} characters
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Submit Button */}
                <div className="flex gap-4">
                  <Button
                    type="submit"
                    disabled={processing}
                    className="flex-1"
                  >
                    {processing ? 'Submitting...' : 'Submit Application'}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => window.history.back()}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </Layout>
    </>
  )
}
