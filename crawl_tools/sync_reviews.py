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


def build_placeholder_review(product: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    name = product.get("name") or product.get("id")
    brand = product.get("brand", "")
    category = product.get("category", "")
    
    # Generate basic summary from available specs
    summary_parts = []
    if brand and category:
        summary_parts.append(f"{brand} {name} thuộc dòng {category}")
    
    if product.get("screen_size"):
        summary_parts.append(f"màn hình {product['screen_size']}")
    
    if product.get("screen_tech"):
        summary_parts.append(f"công nghệ {product['screen_tech']}")
    
    if product.get("camera_main"):
        summary_parts.append(f"camera {product['camera_main']}")
    
    if product.get("chipset"):
        summary_parts.append(f"chip {product['chipset']}")
    
    if product.get("storage"):
        summary_parts.append(f"bộ nhớ {product['storage']}")
    
    if product.get("os"):
        summary_parts.append(f"hệ điều hành {product['os']}")
    
    summary = ". ".join(summary_parts) + "." if summary_parts else f"Đánh giá chi tiết {name} - thông số kỹ thuật và trải nghiệm sử dụng."
    
    # Generate basic TOC
    toc = [
        f"{name} giá bao nhiêu?",
        f"Có nên mua {name} không?",
        f"Đánh giá {name} chi tiết",
        f"{name} có mấy màu?",
        f"So sánh {name} với các model khác",
        f"Mua {name} ở đâu tốt nhất?",
        "Câu hỏi thường gặp"
    ]
    
    # Generate basic sections
    sections = [
        {
            "id": "pricing",
            "title": f"1. {name} giá bao nhiêu?",
            "content": f"Thông tin giá {name} sẽ được cập nhật. Vui lòng liên hệ Di Động Việt để được báo giá chính xác và các ưu đãi hiện tại."
        },
        {
            "id": "should_buy",
            "title": f"2. Có nên mua {name} không?",
            "content": f"Để đưa ra quyết định mua {name}, bạn cần xem xét nhu cầu sử dụng, ngân sách và so sánh với các sản phẩm tương tự. Thông tin chi tiết sẽ được cập nhật."
        },
        {
            "id": "detail_review",
            "title": f"3. Đánh giá {name} chi tiết",
            "content": f"Đánh giá chi tiết về thiết kế, hiệu năng, camera, pin và trải nghiệm sử dụng {name} sẽ được cập nhật đầy đủ."
        },
        {
            "id": "colors",
            "title": f"4. {name} có mấy màu?",
            "content": f"Thông tin về các màu sắc có sẵn của {name} sẽ được cập nhật."
        },
        {
            "id": "compare",
            "title": f"5. So sánh {name} với các model khác",
            "content": f"So sánh chi tiết {name} với các sản phẩm cùng phân khúc sẽ được cập nhật."
        },
        {
            "id": "where_to_buy",
            "title": f"6. Mua {name} ở đâu tốt nhất?",
            "content": f"Thông tin về nơi mua {name} chính hãng, giá tốt và dịch vụ bảo hành sẽ được cập nhật."
        }
    ]
    
    # Generate basic pricing table if storage info available
    pricing_table = []
    if product.get("storage"):
        pricing_table.append({
            "variant": product["storage"],
            "price_current_vnd": None,
            "price_launch_vnd": None,
            "price_usd": None
        })
    
    # Generate basic colors if available
    colors = product.get("colors", [])
    
    # Generate basic comparisons
    comparisons = [
        {
            "title": f"{name} vs Model tương tự",
            "rows": [
                ["Màn hình", "Đang cập nhật", "Đang cập nhật", "Đang cập nhật"],
                ["Camera", "Đang cập nhật", "Đang cập nhật", "Đang cập nhật"],
                ["Pin", "Đang cập nhật", "Đang cập nhật", "Đang cập nhật"]
            ]
        }
    ]
    
    # Generate basic FAQs
    faqs = [
        {"q": f"{name} có chính hãng không?", "a": "Thông tin về nguồn gốc và bảo hành sẽ được cập nhật."},
        {"q": f"{name} có mấy phiên bản?", "a": "Thông tin về các phiên bản và cấu hình sẽ được cập nhật."},
        {"q": f"{name} có ưu đãi gì?", "a": "Thông tin về khuyến mãi và ưu đãi sẽ được cập nhật."}
    ]
    
    return {
        "product_id": product.get("id"),
        "source_url": product.get("url"),
        "title": f"Đánh giá {name}",
        "summary": summary,
        "toc": toc,
        "sections": sections,
        "pricing_table": pricing_table,
        "colors": colors,
        "comparisons": comparisons,
        "faqs": faqs,
        "last_updated_at": now,
    }


def main() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    products_path = os.path.join(repo_root, "profiles", "products.json")
    reviews_path = os.path.join(repo_root, "profiles", "reviews.json")

    products: List[Dict[str, Any]] = load_json(products_path) or []
    reviews: List[Dict[str, Any]] = load_json(reviews_path) or []

    existing_ids = {r.get("product_id") for r in reviews}
    added = 0
    updated = 0

    for p in products:
        pid = p.get("id")
        if not pid:
            continue
            
        if pid not in existing_ids:
            reviews.append(build_placeholder_review(p))
            existing_ids.add(pid)
            added += 1
        else:
            # Update existing review with basic content if it's empty
            existing_review = next((r for r in reviews if r.get("product_id") == pid), None)
            if existing_review and (not existing_review.get("summary") or existing_review.get("summary") == "Nội dung review sẽ được cập nhật."):
                updated_review = build_placeholder_review(p)
                existing_review.update(updated_review)
                updated += 1

    save_json(reviews_path, reviews)
    print(f"Ensured reviews for {len(products)} products. Added {added} new entries, updated {updated} existing entries → {reviews_path}")


if __name__ == "__main__":
    main()
