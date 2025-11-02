"""
Mock data for PurrfectHome demo
Loads pre-generated cat adoption data from JSON file
"""

import json
from pathlib import Path

# Load data from JSON file
_data_file = Path(__file__).parent / "cats_data.json"

try:
    with open(_data_file) as f:
        _data = json.load(f)
    
    # Transform cats data to match frontend expectations
    CATS = []
    for cat in _data["cats"]:
        # Handle personality - convert string to array if needed
        personality = cat.get("personality", "Friendly")
        if isinstance(personality, str):
            # Convert string to array of traits
            personality = [trait.strip() for trait in personality.split(",")]
        
        # Map JSON fields to frontend-expected fields
        transformed_cat = {
            "id": cat["id"],
            "name": cat["name"],
            "age": cat["age"],
            "breed": cat["breed"],
            "color": cat.get("color", "Mixed"),
            "gender": cat.get("gender", "female"),
            "photo": cat.get("image", ""),
            "photo_id": cat.get("photo_id"),
            "photographer": cat.get("photographer"),
            "photographer_url": cat.get("photographer_url"),
            "short_description": cat.get("description", ""),
            "full_story": cat.get("description", "A wonderful cat looking for a loving home."),
            "personality": personality,
            "good_with_kids": cat.get("good_with_kids", True),
            "good_with_dogs": cat.get("good_with_dogs", True),
            "good_with_cats": cat.get("good_with_cats", True),
            "adoption_fee": cat.get("adoption_fee", 150),
            "shelter_name": cat.get("shelter", "Happy Tails Shelter"),
            "shelter_city": _data["shelters"][0]["location"] if _data["shelters"] else "Springfield",
            "available_since": "2024-01-01",
            "adoption_status": cat.get("adoption_status", "available"),
        }
        CATS.append(transformed_cat)
    
    SHELTERS = _data["shelters"]
    print(f"✓ Loaded {len(CATS)} cats and {len(SHELTERS)} shelters from cats_data.json")
except Exception as e:
    print(f"✗ Failed to load cats_data.json: {e}")
    import traceback
    traceback.print_exc()
    CATS = []
    SHELTERS = []


def get_all_cats() -> list[dict]:
    """Get all cats"""
    return CATS


def get_cat_by_id(cat_id: int) -> dict | None:
    """Get a cat by ID"""
    for cat in CATS:
        if cat["id"] == cat_id:
            return cat
    return None


def get_shelter_by_name(shelter_name: str) -> dict | None:
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
