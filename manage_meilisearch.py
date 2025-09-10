#!/usr/bin/env python3
"""
Meilisearch Management Script
Provides easy commands to start, stop, and check Meilisearch server
"""

import subprocess
import sys
import time
import requests
import json
import os
from pathlib import Path

class MeilisearchManager:
    def __init__(self):
        self.server_script = "simple_meilisearch_server.py"
        self.base_url = "http://localhost:7700"
        self.products_file = "profiles/merged_products.json"
        self.output_file = "meili.out"
        self.error_file = "meili.err"
    
    def start_server(self):
        """Start Meilisearch server in background"""
        print("🚀 Starting Meilisearch server...")
        
        # Check if already running
        if self.is_running():
            print("✅ Meilisearch server is already running")
            return True
        
        try:
            # Start server in background
            subprocess.Popen([
                "python", self.server_script
            ], stdout=open(self.output_file, 'w'), 
               stderr=open(self.error_file, 'w'),
               creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            # Wait for server to start
            print("⏳ Waiting for server to start...")
            for i in range(30):
                time.sleep(1)
                if self.is_running():
                    print("✅ Meilisearch server started successfully")
                    return True
                print(f"   Attempt {i+1}/30...")
            
            print("❌ Server failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop Meilisearch server"""
        print("🛑 Stopping Meilisearch server...")
        
        try:
            # Find and kill Python processes running the server
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if 'python.exe' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        pid = parts[1]
                        try:
                            subprocess.run(['taskkill', '/PID', pid, '/F'], 
                                         capture_output=True)
                            print(f"✅ Killed process {pid}")
                        except:
                            pass
            
            print("✅ Meilisearch server stopped")
            return True
            
        except Exception as e:
            print(f"❌ Failed to stop server: {e}")
            return False
    
    def is_running(self):
        """Check if server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def status(self):
        """Check server status"""
        print("🔍 Checking Meilisearch server status...")
        
        if self.is_running():
            print("✅ Server is running")
            
            # Get server info
            try:
                response = requests.get(f"{self.base_url}/indexes")
                indexes = response.json().get('results', [])
                print(f"📊 Available indexes: {len(indexes)}")
                
                for index in indexes:
                    print(f"   - {index['uid']} (primary key: {index['primaryKey']})")
                
                # Test search
                search_response = requests.post(f"{self.base_url}/indexes/products/search", 
                                              json={'q': 'test', 'limit': 1})
                if search_response.status_code == 200:
                    result = search_response.json()
                    print(f"🔍 Search test: {result['totalHits']} total documents indexed")
                
            except Exception as e:
                print(f"⚠️  Could not get detailed status: {e}")
        else:
            print("❌ Server is not running")
    
    def setup_data(self):
        """Setup data in the index"""
        print("📦 Setting up data in Meilisearch...")
        
        if not self.is_running():
            print("❌ Server is not running. Please start it first.")
            return False
        
        try:
            # Create products index
            print("Creating products index...")
            response = requests.post(f"{self.base_url}/indexes", 
                                   json={'uid': 'products', 'primaryKey': 'id'})
            if response.status_code == 201:
                print("✅ Products index created")
            else:
                print(f"⚠️  Index creation response: {response.status_code}")
            
            # Load and add products data
            if Path(self.products_file).exists():
                print(f"Loading data from {self.products_file}...")
                with open(self.products_file, 'r', encoding='utf-8') as f:
                    products = json.load(f)
                
                print(f"Adding {len(products)} products to index...")
                response = requests.post(f"{self.base_url}/indexes/products/documents", 
                                       json=products)
                if response.status_code == 202:
                    result = response.json()
                    print(f"✅ Added {result['details']['indexedDocuments']} products to index")
                else:
                    print(f"❌ Failed to add products: {response.status_code}")
            else:
                print(f"❌ Products file not found: {self.products_file}")
                
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
        
        return True
    
    def search(self, query, limit=5):
        """Perform a search"""
        if not self.is_running():
            print("❌ Server is not running")
            return
        
        try:
            response = requests.post(f"{self.base_url}/indexes/products/search", 
                                   json={'q': query, 'limit': limit})
            if response.status_code == 200:
                result = response.json()
                print(f"🔍 Search results for '{query}':")
                print(f"📊 Total hits: {result['totalHits']}")
                
                for i, hit in enumerate(result['hits'], 1):
                    price = hit.get('price', {}).get('current', 0)
                    print(f"{i}. {hit['name']} - {hit['brand']} - {price:,} VND")
            else:
                print(f"❌ Search failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Search error: {e}")

def main():
    manager = MeilisearchManager()
    
    if len(sys.argv) < 2:
        print("Meilisearch Manager")
        print("Usage: python manage_meilisearch.py <command>")
        print("\nCommands:")
        print("  start    - Start Meilisearch server")
        print("  stop     - Stop Meilisearch server")
        print("  status   - Check server status")
        print("  setup    - Setup data in the index")
        print("  search   - Search for products (usage: search <query> [limit])")
        print("  restart  - Restart the server")
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        manager.start_server()
    elif command == "stop":
        manager.stop_server()
    elif command == "status":
        manager.status()
    elif command == "setup":
        manager.setup_data()
    elif command == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else "phone"
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        manager.search(query, limit)
    elif command == "restart":
        manager.stop_server()
        time.sleep(2)
        manager.start_server()
        time.sleep(3)
        manager.setup_data()
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
