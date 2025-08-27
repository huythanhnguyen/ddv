import json
import os
import re
import time
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup


REQUEST_TIMEOUT_SECONDS = 25
REQUEST_RETRIES = 2
REQUEST_RETRY_BACKOFF_SECONDS = 2


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


def parse_price(text: str) -> Optional[int]:
    if not text:
        return None
    digits_only = re.sub(r"[^0-9]", "", text)
    if not digits_only:
        return None
    try:
        return int(digits_only)
    except Exception:
        return None


def http_get(url: str) -> Optional[str]:
    last_err: Optional[Exception] = None
    for attempt in range(REQUEST_RETRIES + 1):
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS, headers={
                "User-Agent": "Mozilla/5.0 (compatible; ddv-bot/1.0)"
            })
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            last_err = e
            if attempt < REQUEST_RETRIES:
                time.sleep(REQUEST_RETRY_BACKOFF_SECONDS * (attempt + 1))
            else:
                print(f"[WARN] GET failed for {url}: {e}")
    return None


def parse_detail_page(html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")

    data: Dict[str, Any] = {
        "images": [],
        "colors": [],
        "storage_options": [],
        "sku": None,
        "availability": None,
        "price_vnd": None,
        "price_listed_vnd": None,
        "promotions": [],
        "installment_available": None,
        # Technical specifications
        "screen_size": None,
        "screen_tech": None,
        "resolution": None,
        "camera_main": None,
        "camera_front": None,
        "camera_features": [],
        "os": None,
        "chipset": None,
        "cpu_cores": None,
        "gpu": None,
        "ram": None,
        "storage": None,
        "network": None,
        "sim": None,
        "bluetooth": None,
        "usb": None,
        "wifi": None,
        "gps": None,
        "battery": None,
    }

    # Images
    for img in soup.select("img[src*='files/products/']"):
        src = img.get("src")
        if src and src not in data["images"]:
            data["images"].append(src)

    # Basic price block
    price_texts: List[str] = []
    for sel in [
        ".price", ".special-price", ".price-current", ".product-info-price", ".old-price",
    ]:
        for n in soup.select(sel):
            txt = n.get_text(" ", strip=True)
            if txt:
                price_texts.append(txt)
    prices = [p for p in (parse_price(t) for t in price_texts) if p]
    if prices:
        data["price_vnd"] = prices[0]
        if len(prices) > 1:
            data["price_listed_vnd"] = prices[1]

    # Promotions + installment
    promo_texts: List[str] = []
    for sel in [".promo", ".khuyenmai", ".uu-dai", "#promotion", ".box-promotion", ".promotion"]:
        for n in soup.select(sel):
            t = n.get_text(" ", strip=True)
            if t:
                promo_texts.append(t)
    if promo_texts:
        data["promotions"] = list({t for t in promo_texts})
        if any(("trả góp" in t.lower()) or ("0%" in t) for t in promo_texts):
            data["installment_available"] = True

    # Availability heuristics (very light)
    avail = soup.find(string=re.compile(r"còn hàng|hết hàng|preorder|đặt trước", re.IGNORECASE))
    if avail:
        data["availability"] = str(avail).strip()[:160]

    # Technical specifications section
    spec_anchor = soup.find(string=re.compile(r"Thông số kỹ thuật|Specifications|Thông tin sản phẩm", re.IGNORECASE))
    spec_texts: List[str] = []
    if spec_anchor and getattr(spec_anchor, "parent", None):
        parent = spec_anchor.parent
        for node in parent.find_all_next(string=True):
            if node.parent and node.parent.name in ["p", "div", "span", "li", "h3", "h4", "td", "th"]:
                text = node.strip()
                if text and len(text) > 1:
                    spec_texts.append(text)
            if len(spec_texts) > 200:
                break

    current_category: Optional[str] = None
    for text in spec_texts:
        lower = text.lower()
        # category cues
        if any(k in lower for k in ["màn hình", "screen"]):
            current_category = "screen"
            continue
        if "camera" in lower or "máy ảnh" in lower:
            current_category = "camera"
            continue
        if any(k in lower for k in ["hệ điều hành", "ios", "android", "cpu", "chip", "gpu"]):
            current_category = "system"
            continue
        if any(k in lower for k in ["bộ nhớ", "ram", "storage", "lưu trữ"]):
            current_category = "memory"
            continue
        if any(k in lower for k in ["kết nối", "network", "sim", "bluetooth", "usb", "wifi", "gps"]):
            current_category = "connectivity"
            continue
        if any(k in lower for k in ["pin", "battery", "sạc"]):
            current_category = "battery"
            continue

        if current_category == "screen":
            if ("inch" in lower) and not data["screen_size"]:
                data["screen_size"] = text
            elif any(k in lower for k in ["oled", "amoled", "ips", "retina", "ltpo", "super", "lcd"]) and not data["screen_tech"]:
                data["screen_tech"] = text
            elif ("pixel" in lower or "x" in text) and not data["resolution"] and re.search(r"\d+\s*[xX]\s*\d+", text):
                data["resolution"] = text

        elif current_category == "camera":
            if ("mp" in lower) and not data["camera_main"] and any(k in lower for k in ["sau", "fusion", "ultra", "tele", "main"]):
                data["camera_main"] = text
            elif ("mp" in lower) and not data["camera_front"] and any(k in lower for k in ["trước", "front", "true depth", "truedeph"]):
                data["camera_front"] = text
            elif any(k in lower for k in ["ois", "tele", "ultra wide", "macro", "4k", "true depth", "proraw", "hdr"]):
                if text not in data["camera_features"]:
                    data["camera_features"].append(text)

        elif current_category == "system":
            if ("ios" in lower or "android" in lower) and not data["os"]:
                data["os"] = text
            elif any(k in lower for k in ["a18", "a17", "snapdragon", "mediatek", "exynos"]) and not data["chipset"]:
                data["chipset"] = text
            elif ("lõi" in lower or "core" in lower) and not data["cpu_cores"]:
                data["cpu_cores"] = text
            elif "gpu" in lower and not data["gpu"]:
                data["gpu"] = text

        elif current_category == "memory":
            if "ram" in lower and not data["ram"]:
                data["ram"] = text
            elif not data["storage"] and re.search(r"\b(\d+\s?gb|1tb|2tb|256gb|512gb)\b", lower):
                data["storage"] = text

        elif current_category == "connectivity":
            if not data["network"] and re.search(r"\b(5g|4g)\b", lower):
                data["network"] = text
            elif not data["sim"] and "sim" in lower:
                data["sim"] = text
            elif not data["bluetooth"] and "bluetooth" in lower:
                data["bluetooth"] = text
            elif not data["usb"] and "usb" in lower:
                data["usb"] = text
            elif not data["wifi"] and ("wifi" in lower or "wi-fi" in lower):
                data["wifi"] = text
            elif not data["gps"] and "gps" in lower:
                data["gps"] = text

        elif current_category == "battery":
            if not data["battery"] and ("pin" in lower or "battery" in lower or "sạc" in lower):
                data["battery"] = text

    return data


def enrich_products(existing: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    updated: List[Dict[str, Any]] = []
    for idx, item in enumerate(existing):
        url = item.get("url")
        if not url:
            updated.append(item)
            continue
        print(f"[{idx+1}/{len(existing)}] Enriching: {url}")
        html = http_get(url)
        if not html:
            updated.append(item)
            continue
        try:
            detail = parse_detail_page(html)
        except Exception as e:
            print(f"  [WARN] parse failed: {e}")
            updated.append(item)
            continue

        merged = dict(item)

        # Merge technical fields if missing or clearly better
        for key in TECH_FIELDS + [
            "images", "colors", "storage_options", "sku", "availability",
            "price_vnd", "price_listed_vnd", "promotions", "installment_available",
        ]:
            new_val = detail.get(key)
            old_val = merged.get(key)
            if key in ["images", "colors", "storage_options", "camera_features", "promotions"]:
                # merge arrays uniquely
                new_list = list({*(old_val or []), *(new_val or [])}) if (old_val or new_val) else (old_val or [])
                merged[key] = new_list
            else:
                if new_val and (not old_val or str(old_val).strip() in {"", "null", "None"}):
                    merged[key] = new_val

        updated.append(merged)

    return updated


def main() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    products_path = os.path.join(repo_root, "profiles", "products.json")
    if not os.path.exists(products_path):
        raise FileNotFoundError(f"Not found: {products_path}")

    with open(products_path, "r", encoding="utf-8") as f:
        products: List[Dict[str, Any]] = json.load(f)

    enriched = enrich_products(products)

    with open(products_path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(enriched)} products to {products_path}")


if __name__ == "__main__":
    main()


