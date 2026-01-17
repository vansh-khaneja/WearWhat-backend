import json
import os
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAGS_DIR = os.path.join(BASE_DIR, "tags")

def load_json(filename: str) -> dict:
    with open(os.path.join(TAGS_DIR, filename), "r") as f:
        return json.load(f)

CATEGORIES = load_json("categories.json")
GENERIC_ATTRIBUTES = load_json("generic_attributes.json")
SPECIFIC_ATTRIBUTES = load_json("specific_attributes.json")

def generate_tags(image_url: str) -> dict:
    """
    Generate tags for a clothing image.

    TODO: Replace this mock implementation with actual CLIP model inference.
    Currently returns random tags from the predefined tag structure.

    Returns a structured dict like:
    {
        "categoryGroup": "upperWear",
        "category": "T-Shirt",
        "attributes": {
            "color": "Blue",
            "season": "Summer",
            "material": "Cotton",
            "pattern": "Solid",
            "occasion": "Casual",
            "neckline": "Round",
            "sleeveLength": "Short Sleeve",
            "topLength": "Waist"
        }
    }
    """
    # Mock: randomly pick a category group and category
    category_groups = CATEGORIES["categoryGroups"]
    group_key = random.choice(list(category_groups.keys()))
    group = category_groups[group_key]
    category = random.choice([c for c in group["categories"] if c != "ETC"])

    # Build attributes from generic attributes
    attributes = {}
    for attr_name, attr_values in GENERIC_ATTRIBUTES.items():
        valid_values = [v for v in attr_values if v != "ETC"]
        if valid_values:
            attributes[attr_name] = random.choice(valid_values)

    # Add specific attributes based on category group
    if group_key in SPECIFIC_ATTRIBUTES:
        specific = SPECIFIC_ATTRIBUTES[group_key]
        for attr_name, attr_values in specific.items():
            if isinstance(attr_values, list) and attr_values:
                valid_values = [v for v in attr_values if v != "ETC"]
                if valid_values:
                    attributes[attr_name] = random.choice(valid_values)

    return {
        "categoryGroup": group_key,
        "category": category,
        "attributes": attributes
    }
