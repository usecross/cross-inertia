import { Link, router } from '@inertiajs/react'
import Layout from '../components/Layout'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Heart, MapPin } from 'lucide-react'
import type { BrowsePageProps, Cat } from '../types'

interface CatCardProps {
  cat: Cat
  onToggleFavorite: (catId: number) => void
}

function CatCard({ cat, onToggleFavorite }: CatCardProps) {
  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      <div className="aspect-square overflow-hidden bg-gray-100 relative group">
        <img
          src={cat.photo}
          alt={cat.name}
          className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
        />
        {cat.photographer && (
          <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-white text-xs px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity">
            Photo by{' '}
            <a
              href={cat.photographer_url}
              target="_blank"
              rel="noopener noreferrer"
              className="underline hover:text-gray-200"
              onClick={(e) => e.stopPropagation()}
            >
              {cat.photographer}
            </a>
            {' '}on Unsplash
          </div>
        )}
      </div>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-xl">{cat.name}</CardTitle>
            <CardDescription className="flex items-center gap-1 mt-1">
              <MapPin className="h-3 w-3" />
              {cat.shelter_city}
            </CardDescription>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className={cat.is_favorited ? 'text-red-500' : 'text-gray-400'}
            onClick={() => onToggleFavorite(cat.id)}
          >
            <Heart className={cat.is_favorited ? 'fill-current' : ''} />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-1 mb-3">
          {cat.personality.slice(0, 3).map((trait) => (
            <Badge key={trait} variant="secondary" className="text-xs">
              {trait}
            </Badge>
          ))}
        </div>
        <p className="text-sm text-muted-foreground line-clamp-2">
          {cat.short_description}
        </p>
        <div className="mt-3 flex items-center justify-between text-sm">
          <span className="text-muted-foreground">
            {cat.age} {cat.age === 1 ? 'year' : 'years'} old
          </span>
          <span className="font-semibold">${cat.adoption_fee}</span>
        </div>
      </CardContent>
      <CardFooter>
        <Button asChild className="w-full">
          <Link href={`/cats/${cat.id}`}>
            View Profile
          </Link>
        </Button>
      </CardFooter>
    </Card>
  )
}

export default function Browse({ title, cats, total, page, has_more, filters }: BrowsePageProps) {
  // Extract cats array from the data wrapper
  const catsData = Array.isArray(cats) ? cats : cats.data
  
  const handleToggleFavorite = (catId: number) => {
    // Build query string to preserve current page and filters
    const params = new URLSearchParams()
    params.set('page', page.toString())
    if (filters.breed) params.set('breed', filters.breed)
    if (filters.age) params.set('age_range', filters.age)
    
    // POST to toggle endpoint - server will redirect back to /browse
    // Inertia will automatically follow the redirect
    router.post(`/favorites/${catId}/toggle?${params.toString()}`, {}, {
      preserveScroll: true,
    })
  }

  const handleLoadMore = () => {
    // Load more cats using infinite scroll
    // The backend will merge new cats with existing ones
    const params = new URLSearchParams()
    params.set('page', (page + 1).toString())
    if (filters.breed) params.set('breed', filters.breed)
    if (filters.age) params.set('age_range', filters.age)
    
    router.visit(`/browse?${params.toString()}`, {
      preserveScroll: true,
      preserveState: true,
      only: ['cats', 'page', 'has_more'], // Only fetch these props for infinite scroll
    })
  }

  return (
    <Layout title={title}>
      <div className="mb-6">
        <p className="text-muted-foreground">
          Showing {catsData.length} of {total} adorable cats available for adoption
        </p>
      </div>

      {/* Cat Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {catsData.map((cat) => (
          <CatCard key={cat.id} cat={cat} onToggleFavorite={handleToggleFavorite} />
        ))}
      </div>

      {/* Load More Button (Infinite Scroll) */}
      {has_more && (
        <div className="flex justify-center">
          <Button
            variant="outline"
            size="lg"
            onClick={handleLoadMore}
            className="min-w-[200px]"
          >
            Load More Cats
          </Button>
        </div>
      )}

      {/* Empty State */}
      {catsData.length === 0 && (
        <div className="text-center py-12">
          <p className="text-lg text-muted-foreground">No cats found. Try adjusting your filters!</p>
        </div>
      )}
    </Layout>
  )
}
