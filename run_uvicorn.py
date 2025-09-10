#!/usr/bin/env python3
"""
Script to run the application with uvicorn directly
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
    import uvicorn
    from app.agent import root_agent
    
    print("🚀 Starting DDV Product Advisor with Uvicorn...")
    print("=" * 50)
    print(f"🌐 Server will be available at: http://localhost:8000")
    print(f"🤖 Agent: {root_agent.name}")
    print("=" * 50)
    
    # Run with uvicorn
    uvicorn.run(
        "app.agent:root_agent",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure all dependencies are installed")
except Exception as e:
    print(f"❌ Error starting server: {e}")
    sys.exit(1)
