#!/usr/bin/env python3
"""
Script to run ADK web server
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables
os.environ.setdefault("GEMINI_API_KEY", "AIzaSyBvQZvQZvQZvQZvQZvQZvQZvQZvQZvQZvQ")
os.environ.setdefault("MEILISEARCH_URL", "http://localhost:7700")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")

try:
    from google.adk.runners import Runner
    from app.agent import root_agent
    
    print("🚀 Starting DDV Product Advisor Web Server...")
    print("=" * 50)
    
    # Create and run the web server
    runner = Runner()
    runner.run(agent=root_agent, port=8000, host="0.0.0.0")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure all dependencies are installed")
except Exception as e:
    print(f"❌ Error starting server: {e}")
    sys.exit(1)
