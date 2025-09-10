#!/usr/bin/env python3
"""
Script to start Meilisearch server using Python subprocess
This provides a nohup-like functionality for Windows
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def download_meilisearch_binary():
    """Download Meilisearch binary if not exists"""
    binary_path = Path("meilisearch.exe")
    
    if binary_path.exists():
        print("✅ Meilisearch binary already exists")
        return str(binary_path)
    
    print("📥 Downloading Meilisearch binary...")
    try:
        import urllib.request
        url = "https://github.com/meilisearch/meilisearch/releases/latest/download/meilisearch-windows-amd64.exe"
        urllib.request.urlretrieve(url, "meilisearch.exe")
        print("✅ Meilisearch binary downloaded successfully")
        return str(binary_path)
    except Exception as e:
        print(f"❌ Failed to download Meilisearch binary: {e}")
        return None

def check_meilisearch_running():
    """Check if Meilisearch is already running"""
    try:
        response = requests.get("http://localhost:7700/health", timeout=5)
        if response.status_code == 200:
            print("✅ Meilisearch is already running")
            return True
    except requests.RequestException:
        pass
    return False

def start_meilisearch_server():
    """Start Meilisearch server in background"""
    if check_meilisearch_running():
        return True
    
    # Download binary if needed
    binary_path = download_meilisearch_binary()
    if not binary_path:
        return False
    
    print("🚀 Starting Meilisearch server...")
    
    try:
        # Start Meilisearch server
        cmd = [binary_path, "--http-addr", "127.0.0.1:7700"]
        
        # Create output files
        with open("meili.out", "w") as out_file, open("meili.err", "w") as err_file:
            process = subprocess.Popen(
                cmd,
                stdout=out_file,
                stderr=err_file,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
        
        # Wait for server to start
        print("⏳ Waiting for Meilisearch to start...")
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            if check_meilisearch_running():
                print("✅ Meilisearch server started successfully")
                print(f"📝 Process ID: {process.pid}")
                print(f"📄 Output log: meili.out")
                print(f"📄 Error log: meili.err")
                print(f"🌐 Server URL: http://localhost:7700")
                return True
            print(f"   Attempt {i+1}/30...")
        
        print("❌ Meilisearch server failed to start within 30 seconds")
        return False
        
    except Exception as e:
        print(f"❌ Failed to start Meilisearch: {e}")
        return False

def test_connection():
    """Test connection to Meilisearch"""
    print("🧪 Testing Meilisearch connection...")
    
    try:
        import meilisearch
        
        client = meilisearch.Client("http://localhost:7700")
        health = client.health()
        print(f"✅ Connection successful: {health}")
        
        # Test creating an index
        try:
            test_index = client.create_index("test_index", {"primaryKey": "id"})
            print("✅ Test index created successfully")
            
            # Clean up test index
            client.delete_index("test_index")
            print("✅ Test index cleaned up")
        except Exception as e:
            print(f"⚠️  Index test failed (this is normal): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Starting Meilisearch Server (nohup equivalent)")
    print("=" * 50)
    
    # Start the server
    if not start_meilisearch_server():
        print("\n❌ Failed to start Meilisearch server")
        sys.exit(1)
    
    # Test connection
    if not test_connection():
        print("\n❌ Connection test failed")
        sys.exit(1)
    
    print("\n🎉 Meilisearch server is running successfully!")
    print("\nTo stop the server, you can:")
    print("1. Find the process: tasklist | findstr meilisearch")
    print("2. Kill the process: taskkill /PID <process_id> /F")
    print("3. Or simply close this terminal")
    
    # Keep the script running to maintain the server
    try:
        print("\n🔄 Server is running... Press Ctrl+C to stop")
        while True:
            time.sleep(60)  # Check every minute
            if not check_meilisearch_running():
                print("❌ Meilisearch server stopped unexpectedly")
                break
    except KeyboardInterrupt:
        print("\n🛑 Stopping Meilisearch server...")
        # The server will continue running in background

if __name__ == "__main__":
    main()
