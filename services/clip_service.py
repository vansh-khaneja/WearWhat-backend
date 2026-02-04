import json
import os
import requests
from io import BytesIO

import torch
import clip
from PIL import Image

from config import MINIO_ENDPOINT, MINIO_PUBLIC_URL, MINIO_SECURE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAGS_DIR = os.path.join(BASE_DIR, "tags")


def load_json(filename: str) -> dict:
    with open(os.path.join(TAGS_DIR, filename), "r") as f:
        return json.load(f)


# Load tag definitions
CLIP_LABELS = load_json("clip_labels.json")

# CLIP model setup
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)


def encode_labels(labels_dict: dict) -> dict:
    """Pre-encode text labels for CLIP."""
    encoded = {}
    with torch.no_grad():
        for key, prompts in labels_dict.items():
            tokens = clip.tokenize(prompts).to(device)
            feats = model.encode_text(tokens)
            feats /= feats.norm(dim=-1, keepdim=True)
            encoded[key] = feats.mean(dim=0)
    return encoded


def predict_from_image(image_features, encoded_labels: dict, threshold: float = 0.20) -> tuple:
    """
    Predict best matching label from encoded labels.
    Returns: (best_label, score)
    """
    scores = {}
    for label, text_feat in encoded_labels.items():
        score = torch.cosine_similarity(
            image_features, text_feat.unsqueeze(0)
        ).item()
        scores[label] = score

    best_label = max(scores, key=scores.get)
    best_score = scores[best_label]

    return (best_label, best_score) if best_score >= threshold else (None, best_score)


# Pre-encode all CLIP labels on startup
print("Loading CLIP labels...")

ENCODED_CATEGORY_GROUPS = encode_labels(CLIP_LABELS["categoryGroups"])
ENCODED_COLORS = encode_labels(CLIP_LABELS["colors"])
ENCODED_PATTERNS = encode_labels(CLIP_LABELS["patterns"])
ENCODED_MATERIALS = encode_labels(CLIP_LABELS["materials"])
ENCODED_SEASONS = encode_labels(CLIP_LABELS["seasons"])
ENCODED_OCCASIONS = encode_labels(CLIP_LABELS["occasions"])

# Encode categories per group
ENCODED_CATEGORIES = {}
for group, categories in CLIP_LABELS["categories"].items():
    ENCODED_CATEGORIES[group] = encode_labels(categories)

# Encode specific attributes
ENCODED_SPECIFIC_ATTRS = {}
for attr_name, attr_values in CLIP_LABELS["specificAttributes"].items():
    ENCODED_SPECIFIC_ATTRS[attr_name] = encode_labels(attr_values)

print("CLIP labels loaded.")


def get_image_features(image_url: str):
    """Download image and extract CLIP features."""
    # Convert public URL to internal URL for Docker networking
    protocol = "https" if MINIO_SECURE else "http"
    public_prefix = f"{protocol}://{MINIO_PUBLIC_URL}/"
    internal_prefix = f"{protocol}://{MINIO_ENDPOINT}/"

    internal_url = image_url.replace(public_prefix, internal_prefix)

    response = requests.get(internal_url)
    image = Image.open(BytesIO(response.content)).convert("RGB")
    image_input = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image_input)

    image_features /= image_features.norm(dim=-1, keepdim=True)
    return image_features


def get_text_embedding(text: str) -> list:
    """
    Get CLIP embedding for a text prompt.

    Args:
        text: Text description (e.g., "blue formal shirt")

    Returns:
        512-dim embedding as list
    """
    with torch.no_grad():
        tokens = clip.tokenize([text]).to(device)
        text_features = model.encode_text(tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)

    return text_features.cpu().numpy().flatten().tolist()


def get_specific_attributes_for_group(group_key: str, image_features) -> dict:
    """Get specific attributes for a category group using CLIP."""
    attributes = {}

    if group_key == "upperWear":
        # Neckline
        neckline, _ = predict_from_image(image_features, ENCODED_SPECIFIC_ATTRS["neckline"], threshold=0.15)
        if neckline:
            attributes["neckline"] = neckline

        # Sleeve length
        sleeve, _ = predict_from_image(image_features, ENCODED_SPECIFIC_ATTRS["sleeveLength"], threshold=0.15)
        if sleeve:
            attributes["sleeveLength"] = sleeve

        # Top length
        top_length, _ = predict_from_image(image_features, ENCODED_SPECIFIC_ATTRS["topLength"], threshold=0.15)
        if top_length:
            attributes["topLength"] = top_length

    elif group_key == "bottomWear":
        # Fit
        fit, _ = predict_from_image(image_features, ENCODED_SPECIFIC_ATTRS["fit"], threshold=0.15)
        if fit:
            attributes["fit"] = fit

        # Length
        length, _ = predict_from_image(image_features, ENCODED_SPECIFIC_ATTRS["bottomLength"], threshold=0.15)
        if length:
            attributes["length"] = length

        # Rise
        rise, _ = predict_from_image(image_features, ENCODED_SPECIFIC_ATTRS["rise"], threshold=0.15)
        if rise:
            attributes["rise"] = rise

    elif group_key == "outerWear":
        # Thickness
        thickness, _ = predict_from_image(image_features, ENCODED_SPECIFIC_ATTRS["thickness"], threshold=0.15)
        if thickness:
            attributes["thickness"] = thickness

    elif group_key == "footwear":
        # Usage type
        usage, _ = predict_from_image(image_features, ENCODED_SPECIFIC_ATTRS["footwearUsage"], threshold=0.15)
        if usage:
            attributes["usageType"] = usage

    return attributes


def generate_tags(image_url: str) -> dict:
    """
    Generate tags for a clothing image using CLIP.

    All predictions made by CLIP:
    - categoryGroup
    - category (within the group)
    - color, pattern, material, season, occasion
    - specific attributes (neckline, fit, etc.)

    Returns:
    {
        "categoryGroup": "upperWear",
        "category": "T-Shirt",
        "attributes": {
            "color": "Blue",
            "pattern": "Solid",
            "material": "Cotton",
            "season": "Summer",
            "occasion": "Casual",
            "neckline": "Round",
            "sleeveLength": "Short Sleeve",
            "topLength": "Waist"
        }
    }
    """
    # Get image features once
    image_features = get_image_features(image_url)

    # Predict category group
    group_key, _ = predict_from_image(image_features, ENCODED_CATEGORY_GROUPS, threshold=0.20)
    if not group_key:
        group_key = "otherItems"

    # Predict category within the group
    category = None
    if group_key in ENCODED_CATEGORIES:
        category, _ = predict_from_image(image_features, ENCODED_CATEGORIES[group_key], threshold=0.15)

    if not category:
        category = "Other"

    # Predict generic attributes
    color, _ = predict_from_image(image_features, ENCODED_COLORS, threshold=0.15)
    pattern, _ = predict_from_image(image_features, ENCODED_PATTERNS, threshold=0.15)
    material, _ = predict_from_image(image_features, ENCODED_MATERIALS, threshold=0.15)
    season, _ = predict_from_image(image_features, ENCODED_SEASONS, threshold=0.15)
    occasion, _ = predict_from_image(image_features, ENCODED_OCCASIONS, threshold=0.15)

    # Build attributes
    attributes = {
        "color": color or "Unknown",
        "pattern": pattern or "Solid",
        "material": material or "Unknown",
        "season": season or "All Season",
        "occasion": occasion or "Casual"
    }

    # Add specific attributes based on category group
    specific_attrs = get_specific_attributes_for_group(group_key, image_features)
    attributes.update(specific_attrs)

    # Convert embedding to list for storage
    embedding = image_features.cpu().numpy().flatten().tolist()

    return {
        "categoryGroup": group_key,
        "category": category,
        "attributes": attributes,
        "embedding": embedding
    }
