#!/usr/bin/env python3
"""
Simple Meilisearch-compatible server using Python
This provides a basic search functionality that mimics Meilisearch API
"""

import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os

class MeilisearchHandler(BaseHTTPRequestHandler):
    """HTTP handler that mimics Meilisearch API"""
    
    def __init__(self, *args, **kwargs):
        self.products_file = "profiles/merged_products.json"
        self.products_data = self.load_products_data()
        super().__init__(*args, **kwargs)
    
    def load_products_data(self):
        """Load products data from JSON file"""
        try:
            with open(self.products_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading products data: {e}")
            return []
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/health":
            self.send_health_response()
        elif path == "/indexes":
            self.send_indexes_response()
        elif path.startswith("/indexes/"):
            self.send_index_response(path)
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/indexes":
            self.create_index()
        elif path.startswith("/indexes/") and "/search" in path:
            self.search_documents()
        elif path.startswith("/indexes/") and "/documents" in path:
            self.add_documents()
        else:
            self.send_error(404, "Not Found")
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path.startswith("/indexes/"):
            self.delete_index(path)
        else:
            self.send_error(404, "Not Found")
    
    def send_health_response(self):
        """Send health check response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {"status": "available"}
        self.wfile.write(json.dumps(response).encode())
    
    def send_indexes_response(self):
        """Send list of indexes"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Return available indexes
        indexes = [
            {
                "uid": "products",
                "primaryKey": "id",
                "createdAt": "2024-01-01T00:00:00.000Z",
                "updatedAt": "2024-01-01T00:00:00.000Z"
            }
        ]
        
        response = {"results": indexes}
        self.wfile.write(json.dumps(response).encode())
    
    def send_index_response(self, path):
        """Send index information"""
        index_name = path.split("/")[-1]
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "uid": index_name,
            "primaryKey": "id",
            "createdAt": "2024-01-01T00:00:00.000Z",
            "updatedAt": "2024-01-01T00:00:00.000Z"
        }
        self.wfile.write(json.dumps(response).encode())
    
    def create_index(self):
        """Create a new index"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        self.send_response(201)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "uid": data.get('uid', 'products'),
            "primaryKey": data.get('primaryKey', 'id'),
            "createdAt": "2024-01-01T00:00:00.000Z",
            "updatedAt": "2024-01-01T00:00:00.000Z"
        }
        self.wfile.write(json.dumps(response).encode())
    
    def search_documents(self):
        """Search documents in the index"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        query = data.get('q', '').lower()
        limit = data.get('limit', 20)
        offset = data.get('offset', 0)
        
        # Search in products data
        results = []
        if self.products_data:
            try:
                for product in self.products_data:
                    # Search in name, brand, category, and description
                    searchable_text = f"{product.get('name', '')} {product.get('brand', '')} {product.get('category', '')} {product.get('description', '')}".lower()
                    
                    if query in searchable_text:
                        results.append(product)
                
                # Apply pagination
                total_hits = len(results)
                results = results[offset:offset + limit]
                
            except Exception as e:
                print(f"Search error: {e}")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "hits": results,
            "offset": offset,
            "limit": limit,
            "estimatedTotalHits": total_hits,
            "totalHits": total_hits,
            "totalPages": (total_hits + limit - 1) // limit,
            "hitsPerPage": limit,
            "page": (offset // limit) + 1,
            "facetDistribution": {},
            "facetStats": {},
            "processingTimeMs": 1,
            "query": query
        }
        self.wfile.write(json.dumps(response).encode())
    
    def add_documents(self):
        """Add documents to the index"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        # For this simple implementation, we just return success
        # In a real implementation, you would store the documents
        self.send_response(202)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "taskUid": 1,
            "indexUid": "products",
            "status": "succeeded",
            "type": "documentAdditionOrUpdate",
            "details": {
                "receivedDocuments": len(data) if isinstance(data, list) else 1,
                "indexedDocuments": len(data) if isinstance(data, list) else 1
            }
        }
        self.wfile.write(json.dumps(response).encode())
    
    def delete_index(self, path):
        """Delete an index"""
        self.send_response(202)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {"taskUid": 1, "indexUid": path.split("/")[-1], "status": "succeeded"}
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass

def start_server(port=7700):
    """Start the Meilisearch-compatible server"""
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, MeilisearchHandler)
    
    print(f"Starting Meilisearch-compatible server on http://127.0.0.1:{port}")
    print("This server provides basic search functionality")
    print("Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.shutdown()

if __name__ == "__main__":
    start_server()
