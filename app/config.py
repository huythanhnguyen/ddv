"""Configuration for DDV Product Advisor system"""

import os
from dataclasses import dataclass

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

    primary_model: str = "gemini-2.0-flash"
    worker_model: str = "gemini-2.5-flash"


config = ModelConfiguration()
