// TypeScript types for PurrfectHome demo
// These define the contract between backend (Python) and frontend (React)

export interface Cat {
  id: number
  name: string
  age: number
  breed: string
  color: string
  gender: 'male' | 'female'
  photo: string
  short_description: string
  full_story: string
  personality: string[]
  good_with_kids: boolean
  good_with_dogs: boolean
  good_with_cats: boolean
  adoption_fee: number
  shelter_name: string
  shelter_city: string
  available_since: string
  is_favorited: boolean
  photographer?: string
  photographer_url?: string
  photo_id?: string
}

export interface Shelter {
  id: number
  name: string
  address: string
  city: string
  state: string
  phone: string
  email: string
}

export interface User {
  id: number
  name: string
  email: string
  favoritesCount: number
}

// Page Props (what backend returns for each page)

export interface BrowsePageProps {
  title: string
  cats: Cat[] | { data: Cat[] }  // Support both flat array and wrapped format for infinite scroll
  total: number
  page: number
  perPage: number
  has_more: boolean
  filters: {
    breed?: string
    age?: string
    personality?: string[]
  }
}

export interface CatProfilePageProps {
  title: string
  cat: Cat
  shelter: Shelter
  similar_cats: Cat[]
}

export interface FavoritesPageProps {
  title: string
  cats: Cat[]
  total: number
}

export interface ApplicationFormPageProps {
  title: string
  cat: Cat
}
