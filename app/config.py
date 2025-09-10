"""Configuration for DDV Product Advisor system"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if we should use Vertex AI or AI Studio
use_vertexai = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "False").lower() == "true"

if use_vertexai:
    # Only import and setup Google Cloud credentials if using Vertex AI
    try:
        import google.auth
        _, project_id = google.auth.default()
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
        os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
    except Exception as e:
        print(f"Warning: Could not setup Google Cloud credentials: {e}")
        print("Falling back to AI Studio mode")
        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")
else:
    # Using Google AI Studio - no need for Google Cloud credentials
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")


@dataclass
class ModelConfiguration:
    """Configuration for DDV Product Advisor models and parameters."""

    # Use stable, supported Gemini models
    primary_model: str = "gemini-2.0-flash"
    worker_model: str = "gemini-2.0-flash"


@dataclass
class GeminiSearchConfig:
    """Configuration for Gemini AI Search Engine."""
    
    api_key: Optional[str] = None
    model: str = "gemini-2.0-flash"
    temperature: float = 0.3
    max_tokens: int = 4096
    max_results: int = 10
    cache_enabled: bool = True
    cache_ttl: int = 3600
    
    def __post_init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", self.api_key)


@dataclass
class MeilisearchConfig:
    """Configuration for Meilisearch Engine."""

    url: str = "http://localhost:7700"
    api_key: Optional[str] = None
    index_name: str = "products"  # Changed to match the index we created
    max_results: int = 20
    timeout: int = 30

    def __post_init__(self):
        self.url = os.getenv("MEILISEARCH_URL", self.url)
        # Don't require API key for local development
        self.api_key = os.getenv("MEILISEARCH_API_KEY", None)


config = ModelConfiguration()
gemini_search_config = GeminiSearchConfig()
meilisearch_config = MeilisearchConfig()
