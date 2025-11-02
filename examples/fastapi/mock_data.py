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
    CATS = _data["cats"]
    SHELTERS = _data["shelters"]
    print(f"✓ Loaded {len(CATS)} cats and {len(SHELTERS)} shelters from cats_data.json")
except Exception as e:
    print(f"✗ Failed to load cats_data.json: {e}")
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
            cat for cat in filtered
            if any(p in cat["personality"] for p in personality)
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
        c for c in CATS
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
