"""
Mock data for PurrfectHome demo
Cat adoption data for the example application
"""

from typing import Literal, TypedDict


class Cat(TypedDict):
    """Cat information."""

    id: int
    name: str
    breed: str
    age: int
    shelter: str
    description: str
    image: str
    photo_id: str
    photographer: str
    photographer_url: str
    color: str
    personality: list[str]
    adoption_status: Literal["available", "pending", "adopted"]


class Shelter(TypedDict):
    """Shelter information."""

    id: int
    name: str
    address: str
    city: str
    state: str
    phone: str
    email: str


# Raw cat data
_RAW_CATS: list[Cat] = [
    {
        "id": 1,
        "name": "Bean",
        "breed": "Brown Tabby",
        "age": 2,
        "shelter": "Happy Tails Shelter",
        "description": "Playful and curious, loves to explore",
        "image": "/static/cat-images/cat_1.jpg",
        "photo_id": "7GX5aICb5i4",
        "photographer": "Jae Park",
        "photographer_url": "https://unsplash.com/@jae_hyun?utm_source=cross-inertia&utm_medium=referral",
        "color": "Brown",
        "personality": ["playful", "curious", "social"],
        "adoption_status": "available",
    },
    {
        "id": 2,
        "name": "Olly",
        "breed": "Maine Coon",
        "age": 3,
        "shelter": "Furry Friends Sanctuary",
        "description": "Gentle giant, very fluffy and affectionate",
        "image": "/static/cat-images/cat_2.jpg",
        "photo_id": "13ky5Ycf0ts",
        "photographer": "Zoë Gayah Jonker",
        "photographer_url": "https://unsplash.com/@zoegayah?utm_source=cross-inertia&utm_medium=referral",
        "color": "Orange/Ginger",
        "personality": ["calm", "affectionate", "gentle"],
        "adoption_status": "available",
    },
    {
        "id": 3,
        "name": "Bob",
        "breed": "Gray Tabby",
        "age": 1,
        "shelter": "Paws & Claws Rescue",
        "description": "Friendly and sociable outdoor cat",
        "image": "/static/cat-images/cat_3.jpg",
        "photo_id": "l5truYNKmm8",
        "photographer": "Andrew Umansky",
        "photographer_url": "https://unsplash.com/@angur?utm_source=cross-inertia&utm_medium=referral",
        "color": "Gray",
        "personality": ["adventurous", "friendly", "outdoor-lover"],
        "adoption_status": "available",
    },
    {
        "id": 4,
        "name": "Snowball",
        "breed": "White Domestic Shorthair",
        "age": 2,
        "shelter": "Happy Tails Shelter",
        "description": "Sleepy and calm, loves cozy spots",
        "image": "/static/cat-images/cat_4.jpg",
        "photo_id": "uy5t-CJuIK4",
        "photographer": "Kari Shea",
        "photographer_url": "https://unsplash.com/@karishea?utm_source=cross-inertia&utm_medium=referral",
        "color": "White",
        "personality": ["quiet", "calm", "sleepy"],
        "adoption_status": "available",
    },
    {
        "id": 5,
        "name": "Whiskers",
        "breed": "Calico",
        "age": 4,
        "shelter": "Paws & Claws Rescue",
        "description": "Independent but loving, enjoys sunbathing",
        "image": "/static/cat-images/cat_5.jpg",
        "photo_id": "46TvM-BVrRI",
        "photographer": "Manja Vitolic",
        "photographer_url": "https://unsplash.com/@madhatterzone?utm_source=cross-inertia&utm_medium=referral",
        "color": "White and Brown",
        "personality": ["independent", "loving", "enjoys-sun"],
        "adoption_status": "available",
    },
    {
        "id": 6,
        "name": "Tiffany",
        "breed": "Ragdoll",
        "age": 1,
        "shelter": "Furry Friends Sanctuary",
        "description": "Extremely playful and acrobatic",
        "image": "/static/cat-images/cat_6.jpg",
        "photo_id": "ZCHj_2lJP00",
        "photographer": "Alvan Nee",
        "photographer_url": "https://unsplash.com/@alvannee?utm_source=cross-inertia&utm_medium=referral",
        "color": "White and Brown",
        "personality": ["energetic", "playful", "acrobatic"],
        "adoption_status": "available",
    },
    {
        "id": 7,
        "name": "Shadow",
        "breed": "Gray Tabby",
        "age": 3,
        "shelter": "Happy Tails Shelter",
        "description": "Quiet and observant, perfect lap cat",
        "image": "/static/cat-images/cat_7.jpg",
        "photo_id": "IbPxGLgJiMI",
        "photographer": "Mikhail Vasilyev",
        "photographer_url": "https://unsplash.com/@miklevasilyev?utm_source=cross-inertia&utm_medium=referral",
        "color": "Gray",
        "personality": ["gentle", "cuddly", "quiet"],
        "adoption_status": "available",
    },
    {
        "id": 8,
        "name": "Patches",
        "breed": "Calico Shorthair",
        "age": 2,
        "shelter": "Paws & Claws Rescue",
        "description": "Energetic and vocal, loves attention",
        "image": "/static/cat-images/cat_8.jpg",
        "photo_id": "oOFumNfUcUY",
        "photographer": "Susana Bartolome",
        "photographer_url": "https://unsplash.com/@susi50?utm_source=cross-inertia&utm_medium=referral",
        "color": "White, Brown, and Orange",
        "personality": ["chatty", "energetic", "attention-seeking"],
        "adoption_status": "available",
    },
    {
        "id": 9,
        "name": "Ginger",
        "breed": "Orange Tabby",
        "age": 1,
        "shelter": "Furry Friends Sanctuary",
        "description": "Sweet and gentle, great with kids",
        "image": "/static/cat-images/cat_9.jpg",
        "photo_id": "hxn2HjZHyQE",
        "photographer": "Eric Han",
        "photographer_url": "https://unsplash.com/@madeyes?utm_source=cross-inertia&utm_medium=referral",
        "color": "Orange",
        "personality": ["patient", "loving", "kid-friendly"],
        "adoption_status": "available",
    },
    {
        "id": 10,
        "name": "Smokey",
        "breed": "Brown Tabby",
        "age": 5,
        "shelter": "Happy Tails Shelter",
        "description": "Mature and cuddly, loves companionship",
        "image": "/static/cat-images/cat_10.jpg",
        "photo_id": "1l2waV8glIQ",
        "photographer": "Loan Dang",
        "photographer_url": "https://unsplash.com/@loandang?utm_source=cross-inertia&utm_medium=referral",
        "color": "Brown and Black",
        "personality": ["affectionate", "loyal", "senior"],
        "adoption_status": "pending",
    },
    {
        "id": 11,
        "name": "Simba",
        "breed": "Orange Domestic Shorthair",
        "age": 2,
        "shelter": "Paws & Claws Rescue",
        "description": "Bold and adventurous, always exploring",
        "image": "/static/cat-images/cat_11.jpg",
        "photo_id": "cQDu1G6lmRM",
        "photographer": "Amber Kipp",
        "photographer_url": "https://unsplash.com/@sadmax?utm_source=cross-inertia&utm_medium=referral",
        "color": "Orange",
        "personality": ["confident", "curious", "adventurous"],
        "adoption_status": "available",
    },
    {
        "id": 12,
        "name": "Oreo",
        "breed": "Tuxedo Cat",
        "age": 4,
        "shelter": "Furry Friends Sanctuary",
        "description": "Sophisticated and elegant, loves high perches",
        "image": "/static/cat-images/cat_12.jpg",
        "photo_id": "a7bdqjeG6M4",
        "photographer": "Mona Magnussen",
        "photographer_url": "https://unsplash.com/@kireinamona?utm_source=cross-inertia&utm_medium=referral",
        "color": "Black and White",
        "personality": ["regal", "dignified", "observant"],
        "adoption_status": "available",
    },
]

SHELTERS: list[Shelter] = [
    {
        "id": 1,
        "name": "Happy Tails Shelter",
        "address": "123 Adoption Lane",
        "city": "Springfield",
        "state": "IL",
        "phone": "(555) 123-4567",
        "email": "info@happytails.org",
    },
    {
        "id": 2,
        "name": "Paws & Claws Rescue",
        "address": "456 Rescue Road",
        "city": "Riverside",
        "state": "CA",
        "phone": "(555) 234-5678",
        "email": "contact@pawsandclaws.org",
    },
    {
        "id": 3,
        "name": "Furry Friends Sanctuary",
        "address": "789 Care Circle",
        "city": "Hillside",
        "state": "NY",
        "phone": "(555) 345-6789",
        "email": "hello@furryfriends.org",
    },
]

# Transform cats data to match frontend expectations
CATS = []
for cat in _RAW_CATS:
    # Map fields to frontend-expected fields
    transformed_cat = {
        "id": cat["id"],
        "name": cat["name"],
        "age": cat["age"],
        "breed": cat["breed"],
        "color": cat.get("color", "Mixed"),
        "gender": cat.get("gender", "female"),  # type: ignore
        "photo": cat.get("image", ""),
        "photo_id": cat.get("photo_id"),
        "photographer": cat.get("photographer"),
        "photographer_url": cat.get("photographer_url"),
        "short_description": cat.get("description", ""),
        "full_story": cat.get(
            "description", "A wonderful cat looking for a loving home."
        ),
        "personality": cat.get("personality", ["friendly"]),
        "good_with_kids": cat.get("good_with_kids", True),  # type: ignore
        "good_with_dogs": cat.get("good_with_dogs", True),  # type: ignore
        "good_with_cats": cat.get("good_with_cats", True),  # type: ignore
        "adoption_fee": cat.get("adoption_fee", 150),  # type: ignore
        "shelter_name": cat.get("shelter", "Happy Tails Shelter"),
        "shelter_city": SHELTERS[0]["city"] if SHELTERS else "Springfield",
        "available_since": "2024-01-01",
        "adoption_status": cat.get("adoption_status", "available"),
    }
    CATS.append(transformed_cat)

print(f"✓ Loaded {len(CATS)} cats and {len(SHELTERS)} shelters")


def get_all_cats() -> list[dict]:
    """Get all cats"""
    return CATS


def get_cat_by_id(cat_id: int) -> dict | None:
    """Get a cat by ID"""
    for cat in CATS:
        if cat["id"] == cat_id:
            return cat
    return None


def get_shelter_by_name(shelter_name: str) -> Shelter | None:
    """Get shelter info by name"""
    for shelter in SHELTERS:
        if shelter["name"] == shelter_name:
            return shelter
    return None


def filter_cats(
    breed: str | None = None,
    age_range: str | None = None,
    personality: list[str] | None = None,
) -> list[dict]:
    """Filter cats by criteria"""
    filtered = CATS.copy()

    if breed:
        filtered = [cat for cat in filtered if cat["breed"] == breed]

    if age_range:
        if age_range == "kitten":
            filtered = [cat for cat in filtered if cat["age"] <= 1]
        elif age_range == "young":
            filtered = [cat for cat in filtered if 1 < cat["age"] <= 3]
        elif age_range == "adult":
            filtered = [cat for cat in filtered if 3 < cat["age"] <= 7]
        elif age_range == "senior":
            filtered = [cat for cat in filtered if cat["age"] > 7]

    if personality:
        filtered = [
            cat for cat in filtered if any(p in cat["personality"] for p in personality)
        ]

    return filtered


def get_similar_cats(cat_id: int, limit: int = 6) -> list[dict]:
    """Get similar cats based on breed and age"""
    cat = get_cat_by_id(cat_id)
    if not cat:
        return []

    import random

    # Find cats with same breed or similar age
    similar = [
        c
        for c in CATS
        if c["id"] != cat_id
        and (c["breed"] == cat["breed"] or abs(c["age"] - cat["age"]) <= 2)
    ]

    # Return random selection
    return random.sample(similar, min(limit, len(similar)))


def paginate_cats(cats: list[dict], page: int = 1, per_page: int = 12) -> dict:
    """Paginate cat list"""
    total = len(cats)
    start = (page - 1) * per_page
    end = start + per_page

    return {
        "cats": cats[start:end],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }


# Mock user favorites (in-memory for demo)
USER_FAVORITES: set[int] = set()


def toggle_favorite(cat_id: int) -> bool:
    """Toggle favorite status for a cat. Returns new status."""
    if cat_id in USER_FAVORITES:
        USER_FAVORITES.remove(cat_id)
        return False
    else:
        USER_FAVORITES.add(cat_id)
        return True


def get_favorited_cats() -> list[dict]:
    """Get all favorited cats"""
    return [cat for cat in CATS if cat["id"] in USER_FAVORITES]


def is_favorited(cat_id: int) -> bool:
    """Check if a cat is favorited"""
    return cat_id in USER_FAVORITES
