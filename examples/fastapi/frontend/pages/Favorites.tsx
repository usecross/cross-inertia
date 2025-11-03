import { Link, router } from '@inertiajs/react'
import Layout from '../components/Layout'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Heart, MapPin, Trash2 } from 'lucide-react'
import type { FavoritesPageProps, Cat } from '../types'

interface CatCardProps {
  cat: Cat
  onRemove: (catId: number) => void
}

function CatCard({ cat, onRemove }: CatCardProps) {
  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      <div className="aspect-square overflow-hidden bg-gray-100">
        <img
          src={cat.photo}
          alt={cat.name}
          className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
        />
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
          <Heart className="h-5 w-5 text-red-500 fill-current" />
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
      <CardFooter className="flex gap-2">
        <Button asChild className="flex-1">
          <Link href={`/cats/${cat.id}`}>
            View Profile
          </Link>
        </Button>
        <Button 
          variant="destructive" 
          size="icon"
          onClick={() => onRemove(cat.id)}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </CardFooter>
    </Card>
  )
}

function EmptyState() {
  return (
    <div className="text-center py-16">
      <div className="mb-6">
        <Heart className="h-24 w-24 mx-auto text-gray-300" />
      </div>
      <h2 className="text-2xl font-bold mb-2">No Favorites Yet</h2>
      <p className="text-muted-foreground mb-6 max-w-md mx-auto">
        You haven't added any cats to your favorites. Browse our available cats and click the heart icon to save your favorites!
      </p>
      <Button asChild>
        <Link href="/browse">
          Browse Cats
        </Link>
      </Button>
    </div>
  )
}

export default function Favorites({ title, cats, total }: FavoritesPageProps) {
  const handleRemoveFavorite = (catId: number) => {
    // Use partial reload to only update the cats list
    router.post(`/favorites/${catId}/remove`, {}, {
      preserveScroll: true,
      only: ['cats', 'total'],
    })
  }

  return (
    <Layout title={title}>
      {cats.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          <div className="mb-6">
            <p className="text-muted-foreground">
              You have {total} {total === 1 ? 'cat' : 'cats'} in your favorites
            </p>
          </div>

          {/* Cat Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {cats.map((cat) => (
              <CatCard 
                key={cat.id} 
                cat={cat} 
                onRemove={handleRemoveFavorite}
              />
            ))}
          </div>
        </>
      )}
    </Layout>
  )
}
