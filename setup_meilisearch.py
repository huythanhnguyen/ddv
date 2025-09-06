#!/usr/bin/env python3
"""
Setup script for Meilisearch integration
This script helps install and configure Meilisearch for the DDV Product Advisor
"""

import os
import sys
import subprocess
import requests
import time
from pathlib import Path

def check_meilisearch_installed():
    """Check if Meilisearch is installed"""
    try:
        result = subprocess.run(['meilisearch', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Meilisearch is installed: {result.stdout.strip()}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ Meilisearch is not installed")
    return False

def install_meilisearch():
    """Install Meilisearch using the official installer"""
    print("📦 Installing Meilisearch...")
    
    try:
        # Download and run the official installer
        if sys.platform == "win32":
            # Windows installation
            print("🪟 Detected Windows - please install Meilisearch manually:")
            print("1. Download from: https://github.com/meilisearch/meilisearch/releases")
            print("2. Extract and add to PATH")
            print("3. Or use: winget install Meilisearch.Meilisearch")
            return False
        else:
            # Linux/macOS installation
            install_cmd = "curl -L https://install.meilisearch.com | sh"
            print(f"Running: {install_cmd}")
            result = subprocess.run(install_cmd, shell=True, check=True)
            print("✅ Meilisearch installed successfully")
            return True
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Meilisearch: {e}")
        return False

def check_meilisearch_running():
    """Check if Meilisearch server is running"""
    try:
        response = requests.get("http://localhost:7700/health", timeout=5)
        if response.status_code == 200:
            print("✅ Meilisearch server is running")
            return True
    except requests.RequestException:
        pass
    
    print("❌ Meilisearch server is not running")
    return False

def start_meilisearch():
    """Start Meilisearch server"""
    print("🚀 Starting Meilisearch server...")
    
    try:
        # Start Meilisearch in the background
        cmd = ["meilisearch", "--http-addr", "127.0.0.1:7700"]
        
        if sys.platform == "win32":
            # Windows - start in background
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            # Linux/macOS - start in background
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for server to start
        print("⏳ Waiting for Meilisearch to start...")
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            if check_meilisearch_running():
                print("✅ Meilisearch server started successfully")
                return True
            print(f"   Attempt {i+1}/30...")
        
        print("❌ Meilisearch server failed to start within 30 seconds")
        return False
        
    except Exception as e:
        print(f"❌ Failed to start Meilisearch: {e}")
        return False

def create_env_file():
    """Create or update .env file with Meilisearch configuration"""
    env_file = Path(".env")
    
    # Default Meilisearch configuration
    meilisearch_config = """
# Meilisearch Configuration
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_API_KEY=
"""
    
    if env_file.exists():
        # Read existing .env file
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Check if Meilisearch config already exists
        if "MEILISEARCH_URL" not in content:
            # Append Meilisearch config
            with open(env_file, 'a') as f:
                f.write(meilisearch_config)
            print("✅ Added Meilisearch configuration to .env file")
        else:
            print("✅ Meilisearch configuration already exists in .env file")
    else:
        # Create new .env file
        with open(env_file, 'w') as f:
            f.write(meilisearch_config)
        print("✅ Created .env file with Meilisearch configuration")

def test_meilisearch_connection():
    """Test connection to Meilisearch"""
    print("🧪 Testing Meilisearch connection...")
    
    try:
        import meilisearch
        
        client = meilisearch.Client("http://localhost:7700")
        health = client.health()
        print(f"✅ Meilisearch connection successful: {health}")
        
        # Test creating an index
        test_index = client.create_index("test_index", {"primaryKey": "id"})
        print("✅ Test index created successfully")
        
        # Clean up test index
        client.delete_index("test_index")
        print("✅ Test index cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Meilisearch connection test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🔧 Meilisearch Setup for DDV Product Advisor")
    print("=" * 50)
    
    # Step 1: Check if Meilisearch is installed
    if not check_meilisearch_installed():
        if not install_meilisearch():
            print("\n❌ Setup failed: Could not install Meilisearch")
            print("Please install Meilisearch manually and run this script again.")
            return False
    
    # Step 2: Check if Meilisearch server is running
    if not check_meilisearch_running():
        if not start_meilisearch():
            print("\n❌ Setup failed: Could not start Meilisearch server")
            print("Please start Meilisearch manually and run this script again.")
            return False
    
    # Step 3: Create/update .env file
    create_env_file()
    
    # Step 4: Test connection
    if not test_meilisearch_connection():
        print("\n❌ Setup failed: Could not connect to Meilisearch")
        return False
    
    print("\n🎉 Meilisearch setup completed successfully!")
    print("\nNext steps:")
    print("1. Run your DDV Product Advisor application")
    print("2. The system will automatically index your products")
    print("3. Enjoy fast, relevant search results!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

