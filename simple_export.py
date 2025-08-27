#!/usr/bin/env python3
"""
Simple export script to update JSON files from SQLite database
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime

def main():
    """Export data from SQLite to JSON"""
    root = Path('.')
    db_path = root / 'ddv.sqlite3'
    
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return
    
    print(f"Exporting from database: {db_path}")
    
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    try:
        # Export products
        print("Exporting products...")
        products = []
        rows = cur.execute("""
            SELECT id, name, brand, category, price_vnd, price_listed_vnd, 
                   url, installment_available, sku, availability, screen_size, 
                   screen_tech, resolution, camera_main, camera_front, os, 
                   chipset, cpu_cores, gpu, ram, storage, network, sim, 
                   bluetooth, usb, wifi, gps, battery
            FROM products
            ORDER BY id
        """).fetchall()
        
        for row in rows:
            product = {
                "id": row[0],
                "name": row[1],
                "brand": row[2],
                "category": row[3],
                "price_vnd": row[4],
                "price_listed_vnd": row[5],
                "url": row[6],
                "installment_available": row[7],
                "sku": row[8],
                "availability": row[9],
                "screen_size": row[10],
                "screen_tech": row[11],
                "resolution": row[12],
                "camera_main": row[13],
                "camera_front": row[14],
                "os": row[15],
                "chipset": row[16],
                "cpu_cores": row[17],
                "gpu": row[18],
                "ram": row[19],
                "storage": row[20],
                "network": row[21],
                "sim": row[22],
                "bluetooth": row[23],
                "usb": row[24],
                "wifi": row[25],
                "gps": row[26],
                "battery": row[27],
                "images": [],
                "colors": [],
                "storage_options": [],
                "camera_features": [],
                "promotions": []
            }
            
            # Get related images
            images = cur.execute("SELECT url FROM product_images WHERE product_id = ?", (row[0],)).fetchall()
            product["images"] = [img[0] for img in images]
            
            # Get related colors
            colors = cur.execute("SELECT color FROM product_colors WHERE product_id = ?", (row[0],)).fetchall()
            product["colors"] = [col[0] for col in colors]
            
            # Get related storage options
            storage_opts = cur.execute("SELECT option FROM product_storage_options WHERE product_id = ?", (row[0],)).fetchall()
            product["storage_options"] = [opt[0] for opt in storage_opts]
            
            # Get related camera features
            camera_feats = cur.execute("SELECT feature FROM product_camera_features WHERE product_id = ?", (row[0],)).fetchall()
            product["camera_features"] = [feat[0] for feat in camera_feats]
            
            products.append(product)
        
        print(f"Found {len(products)} products")
        
        # Check iPhone 16 Pro Max
        iphone = next((p for p in products if p['id'] == 'iphone-16-pro-max'), None)
        if iphone:
            print(f"iPhone 16 Pro Max - price_vnd: {iphone['price_vnd']}, availability: {iphone['availability']}")
        
        # Write products.json
        profiles_dir = root / 'profiles'
        with open(profiles_dir / 'products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"Exported {len(products)} products to products.json")
        
    except Exception as e:
        print(f"Error during export: {e}")
        raise
    finally:
        con.close()

if __name__ == "__main__":
    main()
