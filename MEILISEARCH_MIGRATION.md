# Meilisearch Migration Guide

This guide explains how to migrate from Gemini AI search to Meilisearch for the DDV Product Advisor system.

## Overview

We're migrating from Gemini AI search to Meilisearch for the following benefits:

- **Faster search**: Sub-50ms search response times
- **Better performance**: No API rate limits or costs
- **Advanced filtering**: Built-in faceted search and filtering
- **Typo tolerance**: Automatic typo correction
- **Hybrid search**: Combines full-text and semantic search
- **Vietnamese support**: Optimized for Vietnamese language

## Migration Steps

### 1. Install Meilisearch

#### Option A: Using the setup script (Recommended)
```bash
python setup_meilisearch.py
```

#### Option B: Manual installation

**Windows:**
```bash
# Using winget
winget install Meilisearch.Meilisearch

# Or download from: https://github.com/meilisearch/meilisearch/releases
```

**Linux/macOS:**
```bash
curl -L https://install.meilisearch.com | sh
```

### 2. Start Meilisearch Server

```bash
# Start Meilisearch server
meilisearch --http-addr 127.0.0.1:7700
```

The server will be available at `http://localhost:7700`

### 3. Install Python Dependencies

```bash
pip install meilisearch
```

### 4. Configuration

The system will automatically use the following default configuration:

```python
# In app/config.py
@dataclass
class MeilisearchConfig:
    url: str = "http://localhost:7700"
    api_key: Optional[str] = None  # Optional for development
    index_name: str = "ddv_products"
    max_results: int = 20
    timeout: int = 30
```

You can override these settings using environment variables:

```bash
export MEILISEARCH_URL="http://localhost:7700"
export MEILISEARCH_API_KEY="your-api-key"  # Optional
```

### 5. Test the Migration

```bash
python test_meilisearch_migration.py
```

## Code Changes

### Before (Gemini Search)
```python
from .gemini_search_engine import GeminiSearchEngine

class EnhancedProductStore:
    def __init__(self):
        self.search_engine = GeminiSearchEngine()
    
    def search_products(self, query: str, limit: int = 20):
        return self.search_engine.search_products(query, limit)
```

### After (Meilisearch)
```python
from .meilisearch_engine import MeilisearchEngine

class EnhancedProductStore:
    def __init__(self):
        self.search_engine = MeilisearchEngine()
    
    def search_products(self, query: str, filters: Dict = None, limit: int = 20):
        return self.search_engine.search_products(query, filters, limit)
```

## New Features

### 1. Advanced Filtering
```python
# Filter by brand
results = store.search_products("phone", filters={'brand': 'Apple'})

# Filter by price range
results = store.search_products("phone", filters={
    'price_min': 5000000,
    'price_max': 15000000
})

# Filter by discount
results = store.search_products("phone", filters={'min_discount': 10})
```

### 2. Sorting
```python
# Sort by price (ascending)
results = store.search_products("phone", sort=["price.current:asc"])

# Sort by discount (descending)
results = store.search_products("phone", sort=["price.discount_percentage:desc"])
```

### 3. Search Metadata
```python
results = store.search_products("iPhone")
for product in results:
    print(f"Relevance: {product['search_metadata']['relevance_score']}")
    print(f"Highlighted: {product['search_metadata']['formatted']}")
```

## Performance Comparison

| Feature | Gemini Search | Meilisearch |
|---------|---------------|-------------|
| Search Speed | 2-5 seconds | <50ms |
| API Costs | Per request | Free |
| Rate Limits | Yes | No |
| Filtering | Post-processing | Native |
| Typo Tolerance | Limited | Advanced |
| Vietnamese Support | Good | Excellent |

## Troubleshooting

### Meilisearch Server Not Starting
```bash
# Check if port 7700 is available
netstat -an | grep 7700

# Start with different port
meilisearch --http-addr 127.0.0.1:7701
```

### Connection Errors
```bash
# Test connection
curl http://localhost:7700/health

# Check logs
meilisearch --log-level DEBUG
```

### Index Issues
```python
# Reindex all products
from app.tools.enhanced_product_store import enhanced_data_store
enhanced_data_store.reindex_products()
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MEILISEARCH_URL` | `http://localhost:7700` | Meilisearch server URL |
| `MEILISEARCH_API_KEY` | `None` | API key (optional for development) |

## Production Deployment

### 1. Set up Meilisearch with API Key
```bash
# Generate master key
meilisearch --master-key="your-master-key"

# Set environment variable
export MEILISEARCH_API_KEY="your-master-key"
```

### 2. Configure for Production
```python
# In production config
MEILISEARCH_URL = "https://your-meilisearch-instance.com"
MEILISEARCH_API_KEY = "your-production-key"
```

### 3. Docker Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  meilisearch:
    image: getmeili/meilisearch:latest
    ports:
      - "7700:7700"
    environment:
      - MEILI_MASTER_KEY=your-master-key
    volumes:
      - meilisearch_data:/meili_data

volumes:
  meilisearch_data:
```

## Rollback Plan

If you need to rollback to Gemini search:

1. Comment out Meilisearch imports in `enhanced_product_store.py`
2. Uncomment Gemini search imports
3. Restart the application

The old Gemini search code is preserved in `gemini_search_engine.py` for reference.

## Support

For issues with Meilisearch:
- [Meilisearch Documentation](https://docs.meilisearch.com/)
- [Meilisearch GitHub](https://github.com/meilisearch/meilisearch)
- [Meilisearch Discord](https://discord.gg/meilisearch)

