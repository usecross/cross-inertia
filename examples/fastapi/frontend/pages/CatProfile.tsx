import { Link, Head, router } from '@inertiajs/react'
import Layout from '../components/Layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Heart, MapPin, Calendar, DollarSign, Home, Dog, Users } from 'lucide-react'
import type { CatProfilePageProps } from '../types'

export default function CatProfile({ cat, shelter, similar_cats = [] }: CatProfilePageProps) {
  const handleToggleFavorite = () => {
    // POST to toggle endpoint - server will redirect back to cat profile
    // Inertia will automatically follow the redirect
    router.post(`/favorites/${cat.id}/toggle`, {}, {
      preserveScroll: true,
    })
  }

  return (
    <>
      <Head title={`${cat.name} - ${cat.age} year old ${cat.breed} for adoption | PurrfectHome`}>
        <meta name="description" content={cat.short_description} />
        <meta property="og:title" content={`Meet ${cat.name} - Adopt This ${cat.breed}`} />
        <meta property="og:description" content={cat.short_description} />
        <meta property="og:image" content={cat.photo} />
        <meta property="og:type" content="website" />
      </Head>
      
      <Layout>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Hero Image */}
          <Card className="overflow-hidden">
            <div className="aspect-video bg-gray-100 relative">
              <img
                src={cat.photo}
                alt={cat.name}
                className="w-full h-full object-cover"
              />
              {cat.photographer && (
                <div className="absolute bottom-0 right-0 bg-black/50 text-white text-xs px-2 py-1 rounded-tl">
                  Photo by{' '}
                  <a
                    href={cat.photographer_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline hover:text-gray-200"
                  >
                    {cat.photographer}
                  </a>
                  {' '}on{' '}
                  <a
                    href="https://unsplash.com?utm_source=cross-inertia&utm_medium=referral"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline hover:text-gray-200"
                  >
                    Unsplash
                  </a>
                </div>
              )}
            </div>
          </Card>

          {/* About Section */}
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-3xl">{cat.name}</CardTitle>
                  <CardDescription className="text-lg mt-1">
                    {cat.age} {cat.age === 1 ? 'year' : 'years'} old • {cat.gender} • {cat.breed}
                  </CardDescription>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className={cat.is_favorited ? 'text-red-500' : 'text-gray-400'}
                  onClick={handleToggleFavorite}
                >
                  <Heart className={`h-6 w-6 ${cat.is_favorited ? 'fill-current' : ''}`} />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Personality</h3>
                <div className="flex flex-wrap gap-2">
                  {cat.personality.map((trait) => (
                    <Badge key={trait} variant="secondary">
                      {trait}
                    </Badge>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="font-semibold mb-2">About {cat.name}</h3>
                <p className="text-muted-foreground leading-relaxed">
                  {cat.full_story}
                </p>
              </div>

              <div>
                <h3 className="font-semibold mb-2">Good With</h3>
                <div className="flex gap-4">
                  <div className={`flex items-center gap-2 ${cat.good_with_kids ? 'text-green-600' : 'text-gray-400'}`}>
                    <Users className="h-4 w-4" />
                    <span className="text-sm">Kids</span>
                  </div>
                  <div className={`flex items-center gap-2 ${cat.good_with_dogs ? 'text-green-600' : 'text-gray-400'}`}>
                    <Dog className="h-4 w-4" />
                    <span className="text-sm">Dogs</span>
                  </div>
                  <div className={`flex items-center gap-2 ${cat.good_with_cats ? 'text-green-600' : 'text-gray-400'}`}>
                    <Home className="h-4 w-4" />
                    <span className="text-sm">Other Cats</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Similar Cats */}
          {similar_cats.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Similar Cats</CardTitle>
                <CardDescription>You might also like these cats</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {similar_cats.map((similarCat) => (
                    <Link
                      key={similarCat.id}
                      href={`/cats/${similarCat.id}`}
                      className="group"
                    >
                      <div className="aspect-square rounded-lg overflow-hidden bg-gray-100 mb-2">
                        <img
                          src={similarCat.photo}
                          alt={similarCat.name}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                        />
                      </div>
                      <p className="font-medium text-sm group-hover:text-primary">
                        {similarCat.name}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {similarCat.age} {similarCat.age === 1 ? 'year' : 'years'} • {similarCat.breed}
                      </p>
                    </Link>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Adoption Info */}
          <Card className="sticky top-6">
            <CardHeader>
              <CardTitle>Adoption Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3 text-sm">
                <DollarSign className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="font-semibold text-2xl">${cat.adoption_fee}</p>
                  <p className="text-muted-foreground">Adoption Fee</p>
                </div>
              </div>

              <div className="flex items-center gap-3 text-sm">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="font-medium">Available Since</p>
                  <p className="text-muted-foreground">
                    {new Date(cat.available_since).toLocaleDateString()}
                  </p>
                </div>
              </div>

              <Button asChild className="w-full" size="lg">
                <Link href={`/cats/${cat.id}/apply`}>
                  Apply to Adopt {cat.name}
                </Link>
              </Button>
            </CardContent>
          </Card>

          {/* Shelter Info */}
          <Card>
            <CardHeader>
              <CardTitle>Shelter Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="font-semibold">{shelter.name}</p>
                <div className="flex items-start gap-2 text-sm text-muted-foreground mt-1">
                  <MapPin className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <div>
                    <p>{shelter.address}</p>
                    <p>{shelter.city}, {shelter.state}</p>
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t space-y-2 text-sm">
                <p>
                  <span className="text-muted-foreground">Phone: </span>
                  <a href={`tel:${shelter.phone}`} className="hover:underline">
                    {shelter.phone}
                  </a>
                </p>
                <p>
                  <span className="text-muted-foreground">Email: </span>
                  <a href={`mailto:${shelter.email}`} className="hover:underline">
                    {shelter.email}
                  </a>
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      </Layout>
    </>
  )
}
