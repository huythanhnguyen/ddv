import json
import os
from datetime import datetime
from typing import Any, Dict, List


def load_json(path: str) -> Any:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def build_placeholder_offer(product: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    name = product.get("name") or product.get("id")
    brand = product.get("brand", "")
    
    # Generate basic pricing structure
    pricing = {
        "current_prices": [],
        "price_note": "Giá và khuyến mãi sẽ được cập nhật",
        "payment_options": [
            "Trả góp 0% lãi suất",
            "Thu cũ đổi mới với giá thu cao",
            "Thanh toán tiền mặt hoặc thẻ"
        ]
    }
    
    # Add pricing based on available storage info
    if product.get("storage"):
        pricing["current_prices"].append({
            "variant": product["storage"],
            "price_vnd": None,
            "original_price_vnd": None,
            "discount_percentage": None,
            "currency": "VND"
        })
    
    # Generate basic promotion structure
    promotions = {
        "time_limited": [
            {
                "period": "Đang cập nhật",
                "description": "Khuyến mãi đặc biệt",
                "type": "special_offer"
            }
        ],
        "free_gifts": [
            {
                "item": "Phụ kiện chính hãng",
                "condition": "Tặng kèm khi mua sản phẩm",
                "type": "product_bundle"
            }
        ],
        "vouchers": [
            {
                "description": "Voucher giảm giá",
                "type": "discount_voucher"
            }
        ],
        "special_discounts": [
            {
                "description": "Giảm giá đặc biệt",
                "target": "Khách hàng mới",
                "type": "new_customer_discount"
            }
        ],
        "bundle_offers": [
            {
                "product": "Phụ kiện đi kèm",
                "discount": "Giảm giá khi mua combo",
                "type": "accessory_bundle"
            }
        ],
        "business_offers": [
            {
                "description": "Báo giá đặc biệt cho doanh nghiệp",
                "contact": "1800.6018",
                "type": "business_pricing"
            }
        ]
    }
    
    # Generate availability info
    availability = {
        "status": "in_stock",
        "delivery": "Giao hàng nhanh trong 2-24h",
        "warranty": "Bảo hành chính hãng 12 tháng"
    }
    
    return {
        "product_id": product.get("id"),
        "source_url": product.get("url"),
        "last_updated_at": now,
        "pricing": pricing,
        "promotions": promotions,
        "availability": availability
    }


def main() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    products_path = os.path.join(repo_root, "profiles", "products.json")
    offers_path = os.path.join(repo_root, "profiles", "offers.json")

    products: List[Dict[str, Any]] = load_json(products_path) or []
    offers: List[Dict[str, Any]] = load_json(offers_path) or []

    existing_ids = {o.get("product_id") for o in offers}
    added = 0
    updated = 0

    for p in products:
        pid = p.get("id")
        if not pid:
            continue
            
        if pid not in existing_ids:
            offers.append(build_placeholder_offer(p))
            existing_ids.add(pid)
            added += 1
        else:
            # Update existing offer if it's missing basic structure
            existing_offer = next((o for o in offers if o.get("product_id") == pid), None)
            if existing_offer and not existing_offer.get("promotions"):
                updated_offer = build_placeholder_offer(p)
                existing_offer.update(updated_offer)
                updated += 1

    save_json(offers_path, offers)
    print(f"Ensured offers for {len(products)} products. Added {added} new entries, updated {updated} existing entries → {offers_path}")


if __name__ == "__main__":
    main()
