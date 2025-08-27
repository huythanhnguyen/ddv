import json
import os
import re
from typing import Any, Dict, List, Tuple


TECH_FIELDS = [
    "screen_size",
    "screen_tech",
    "resolution",
    "camera_main",
    "camera_front",
    "camera_features",
    "os",
    "chipset",
    "cpu_cores",
    "gpu",
    "ram",
    "storage",
    "network",
    "sim",
    "bluetooth",
    "usb",
    "wifi",
    "gps",
    "battery",
]


def normalize_model_key(name: str, url: str, pid: str) -> str:
    base = name or ""
    base = base.lower()
    # remove storage indicators
    base = re.sub(r"\b(\d+\s?gb|1tb|2tb)\b", "", base)
    # remove variant buzzwords
    base = re.sub(r"\b(cty|chinh hang|bhdt|da kich hoat|chinh-hang)\b", "", base)
    # collapse whitespace
    base = re.sub(r"\s+", " ", base).strip()
    if not base and url:
        slug = url.split("/")[-1].replace(".html", "")
        base = re.sub(r"-(\d+gb|1tb|2tb)\b", "", slug)
    if not base:
        base = pid.lower()
    return base


def title_from_slug(url: str) -> str:
    if not url:
        return ""
    slug = url.split("/")[-1].replace(".html", "")
    # replace separators
    slug = slug.replace("-", " ").replace("_", " ")
    # fix common brand capitalization
    words = []
    for w in slug.split():
        if w.lower() == "iphone":
            words.append("iPhone")
        elif w.lower() == "ipad":
            words.append("iPad")
        elif w.lower() == "ipod":
            words.append("iPod")
        elif w.lower() == "samsung":
            words.append("Samsung")
        elif w.lower() == "galaxy":
            words.append("Galaxy")
        else:
            words.append(w.capitalize())
    title = " ".join(words)
    # remove storage suffix tokens
    title = re.sub(r"\b(\d+\s?GB|1TB|2TB)\b", "", title, flags=re.IGNORECASE)
    # collapse spaces
    title = re.sub(r"\s+", " ", title).strip()
    return title


def pick_best_value(values: List[Any]) -> Any:
    # prefer first non-empty string or non-null
    for v in values:
        if isinstance(v, str) and v.strip():
            return v
        if v not in (None, "", "null", "None") and not isinstance(v, list):
            return v
    return None


def merge_lists(lists: List[List[str]]) -> List[str]:
    out: List[str] = []
    for lst in lists:
        for it in (lst or []):
            if it not in out:
                out.append(it)
    return out


def build_group_best(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    best: Dict[str, Any] = {}
    # scalar fields
    scalar_fields = [
        "price_vnd",
        "price_listed_vnd",
        "sku",
        "availability",
    ] + [f for f in TECH_FIELDS if f not in ["camera_features"]]
    list_fields = ["images", "colors", "storage_options", "promotions", "camera_features"]

    for f in scalar_fields:
        best[f] = pick_best_value([it.get(f) for it in items])

    for f in list_fields:
        best[f] = merge_lists([it.get(f) or [] for it in items])

    # installment_available: true if any true
    best["installment_available"] = any(bool(it.get("installment_available")) for it in items) or None
    return best


def enrich(products: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
    # group by normalized key
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for it in products:
        key = normalize_model_key(it.get("name", ""), it.get("url", ""), it.get("id", ""))
        groups.setdefault(key, []).append(it)

    # compute best per group
    group_best: Dict[str, Dict[str, Any]] = {k: build_group_best(v) for k, v in groups.items()}

    updated: List[Dict[str, Any]] = []
    changes = 0
    for it in products:
        merged = dict(it)
        key = normalize_model_key(it.get("name", ""), it.get("url", ""), it.get("id", ""))
        best = group_best.get(key, {})

        # name normalization from URL if needed
        url = merged.get("url") or ""
        if url:
            suggested = title_from_slug(url)
            if suggested and suggested.lower() != (merged.get("name") or "").lower():
                merged["name"] = suggested
                changes += 1

        # lists: union
        for f in ["images", "colors", "storage_options", "promotions", "camera_features"]:
            before = merged.get(f)
            combined = merge_lists([before or [], best.get(f) or []])
            if combined != (before or []):
                merged[f] = combined
                if combined:
                    changes += 1

        # scalars: fill if empty
        for f in [
            "price_vnd", "price_listed_vnd", "sku", "availability",
            *TECH_FIELDS
        ]:
            val = merged.get(f)
            if val in (None, "", "null", "None"):
                best_val = best.get(f)
                if best_val not in (None, "", "null", "None"):
                    merged[f] = best_val
                    changes += 1

        # installment_available
        if not merged.get("installment_available") and best.get("installment_available"):
            merged["installment_available"] = True
            changes += 1

        updated.append(merged)

    return updated, changes


def main() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    products_path = os.path.join(repo_root, "profiles", "products.json")
    if not os.path.exists(products_path):
        raise FileNotFoundError(products_path)
    with open(products_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    enriched, changes = enrich(products)
    with open(products_path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)
    print(f"Filled/merged {changes} fields across {len(enriched)} products → {products_path}")


if __name__ == "__main__":
    main()


