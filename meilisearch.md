# Meilisearch API Documentation for LLMs

## Overview

Meilisearch is a fast, open-source search engine that provides powerful search capabilities through RESTful APIs. This documentation covers the core search functionality that LLMs can use to implement search features.

## Core Search Endpoints

### 1. Single Index Search

**Endpoint:** `POST /indexes/{index_uid}/search`

**Description:** Search for documents matching a specific query in a given index. This is the preferred endpoint when API authentication is required.

**Path Parameters:**
- `index_uid` (String, required): UID of the requested index

**Request Body Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | String | "" | Query string |
| `offset` | Integer | 0 | Number of documents to skip |
| `limit` | Integer | 20 | Maximum number of documents returned |
| `hitsPerPage` | Integer | 1 | Maximum documents per page |
| `page` | Integer | 1 | Request specific page of results |
| `filter` | String/Array | null | Filter queries by attribute values |
| `facets` | Array of strings | null | Display count of matches per facet |
| `attributesToRetrieve` | Array of strings | ["*"] | Attributes to display in returned documents |
| `attributesToHighlight` | Array of strings | null | Highlight matching terms in attributes |
| `highlightPreTag` | String | "<em>" | String inserted at start of highlighted term |
| `highlightPostTag` | String | "</em>" | String inserted at end of highlighted term |
| `sort` | Array of strings | null | Sort search results by attribute values |
| `matchingStrategy` | String | "last" | Strategy to match query terms (last/all/frequency) |
| `showRankingScore` | Boolean | false | Display global ranking score |
| `showRankingScoreDetails` | Boolean | false | Add detailed ranking score field |
| `rankingScoreThreshold` | Number | null | Exclude results below specified score (0.0-1.0) |
| `attributesToSearchOn` | Array of strings | ["*"] | Restrict search to specified attributes |
| `hybrid` | Object | null | Hybrid search with semantic ratio |
| `vector` | Array of numbers | null | Custom vector for search |
| `retrieveVectors` | Boolean | false | Return document and query embeddings |
| `locales` | Array of strings | [] | Explicitly state query language |

### 2. Multi-Search

**Endpoint:** `POST /multi-search`

**Description:** Perform multiple search queries on one or more indexes in a single HTTP request. Also known as federated search.

**Request Body Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `federation` | Object | If present and not null, returns a single list merging all search results across all specified queries |
| `queries` | Array of objects | Contains the list of search queries to perform. `indexUid` is required, all other parameters are optional |

**Federation Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `offset` | Integer | 0 | Number of documents to skip |
| `limit` | Integer | 20 | Maximum number of documents returned |
| `facetsByIndex` | Object of arrays | null | Display facet information for specified indexes |
| `mergeFacets` | Object | null | Display merged facet information |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `indexUid` | String | N/A | UID of the requested index (required) |
| `q` | String | "" | Query string |
| `offset` | Integer | 0 | Number of documents to skip |
| `limit` | Integer | 20 | Maximum number of documents returned |
| `filter` | String | null | Filter queries by attribute values |
| `facets` | Array of strings | null | Display count of matches per facet |
| `sort` | Array of strings | null | Sort search results by attribute values |
| `federationOptions` | Object | null | Configure federation settings for specific query |

**Non-Federated Multi-Search:**
```json
{
  "queries": [
    {
      "indexUid": "movies",
      "q": "pooh",
      "limit": 5
    },
    {
      "indexUid": "movies",
      "q": "nemo",
      "limit": 5
    },
    {
      "indexUid": "movie_ratings",
      "q": "us"
    }
  ]
}
```

**Federated Multi-Search:**
```json
{
  "federation": {},
  "queries": [
    {
      "indexUid": "movies",
      "q": "batman"
    },
    {
      "indexUid": "comics",
      "q": "batman"
    }
  ]
}
```

## Search Features

### Query Types

1. **Basic Search:**
   ```json
   {
     "q": "dragon"
   }
   ```

2. **Phrase Search:**
   ```json
   {
     "q": "\"dragon ball\""
   }
   ```

3. **Negative Search:**
   ```json
   {
     "q": "dragon -ball"
   }
   ```

4. **Placeholder Search:**
   ```json
   {
     "q": ""
   }
   ```

### Filtering

**Filter by Attribute:**
```json
{
  "q": "dragon",
  "filter": "genre = 'action'"
}
```

**Multiple Filters:**
```json
{
  "q": "dragon",
  "filter": "genre = 'action' AND year > 2000"
}
```

**Array Filters:**
```json
{
  "q": "dragon",
  "filter": "genre IN ['action', 'adventure']"
}
```

### Sorting

**Single Attribute:**
```json
{
  "q": "dragon",
  "sort": ["year:desc"]
}
```

**Multiple Attributes:**
```json
{
  "q": "dragon",
  "sort": ["year:desc", "title:asc"]
}
```

### Highlighting

```json
{
  "q": "dragon",
  "attributesToHighlight": ["title", "overview"],
  "highlightPreTag": "<mark>",
  "highlightPostTag": "</mark>"
}
```

### Faceted Search

```json
{
  "q": "dragon",
  "facets": ["genre", "year"],
  "filter": "genre = 'action'"
}
```

### Hybrid Search (AI-Powered)

```json
{
  "q": "kitchen utensils",
  "hybrid": {
    "semanticRatio": 0.9,
    "embedder": "EMBEDDER_NAME"
  }
}
```

### Vector Search

```json
{
  "vector": [0.1, 0.2, 0.3],
  "hybrid": {
    "embedder": "EMBEDDER_NAME"
  }
}
```

## Response Format

### Single Index Search Response

```json
{
  "hits": [
    {
      "id": 31072,
      "title": "Dragon",
      "overview": "In a desperate attempt to save her kingdom...",
      "genre": "action",
      "year": 2006,
      "_formatted": {
        "title": "<mark>Dragon</mark>",
        "overview": "In a desperate attempt to save her kingdom..."
      },
      "_rankingScore": 0.987654321
    }
  ],
  "offset": 0,
  "limit": 20,
  "estimatedTotalHits": 1000,
  "totalHits": 1000,
  "totalPages": 50,
  "hitsPerPage": 20,
  "page": 1,
  "facetDistribution": {
    "genre": {
      "action": 500,
      "adventure": 300,
      "drama": 200
    }
  },
  "facetStats": {
    "year": {
      "min": 1950,
      "max": 2023
    }
  },
  "processingTimeMs": 12,
  "query": "dragon"
}
```

### Non-Federated Multi-Search Response

```json
{
  "results": [
    {
      "indexUid": "movies",
      "hits": [
        {
          "id": 13682,
          "title": "Pooh's Heffalump Movie"
        }
      ],
      "query": "pooh",
      "processingTimeMs": 26,
      "limit": 5,
      "offset": 0,
      "estimatedTotalHits": 22
    },
    {
      "indexUid": "movies",
      "hits": [
        {
          "id": 12,
          "title": "Finding Nemo"
        }
      ],
      "query": "nemo",
      "processingTimeMs": 5,
      "limit": 5,
      "offset": 0,
      "estimatedTotalHits": 11
    }
  ]
}
```

### Federated Multi-Search Response

```json
{
  "hits": [
    {
      "id": 42,
      "title": "Batman returns",
      "overview": "...",
      "_federation": {
        "indexUid": "movies",
        "queriesPosition": 0,
        "weightedRankingScore": 1.0
      }
    },
    {
      "comicsId": "batman-killing-joke",
      "title": "Batman: the killing joke",
      "_federation": {
        "indexUid": "comics",
        "queriesPosition": 1,
        "weightedRankingScore": 0.98
      }
    }
  ],
  "processingTimeMs": 0,
  "limit": 20,
  "offset": 0,
  "estimatedTotalHits": 2,
  "facetsByIndex": {
    "movies": {
      "distribution": {
        "genre": {
          "action": 5,
          "drama": 3
        }
      }
    }
  }
}
```

### Response with Ranking Score Details

```json
{
  "hits": [
    {
      "id": 31072,
      "title": "Dragon",
      "_rankingScoreDetails": {
        "words": {
          "order": 0,
          "matchingWords": 4,
          "maxMatchingWords": 4,
          "score": 1.0
        },
        "typo": {
          "order": 2,
          "typoCount": 1,
          "maxTypoCount": 4,
          "score": 0.75
        },
        "name:asc": {
          "order": 1,
          "value": "Dragon"
        }
      }
    }
  ]
}
```

## Code Examples for LLMs

### Python Implementation

```python
import requests
from typing import Dict, List, Any, Optional

class MeilisearchClient:
    def __init__(self, url: str, api_key: Optional[str] = None):
        self.url = url.rstrip('/')
        self.headers = {'Content-Type': 'application/json'}
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def search(self, index_uid: str, query: str, **params) -> Dict[str, Any]:
        """Search documents in an index"""
        search_params = {'q': query, **params}
        response = requests.post(
            f'{self.url}/indexes/{index_uid}/search',
            headers=self.headers,
            json=search_params
        )
        response.raise_for_status()
        return response.json()
    
    def multi_search(self, queries: List[Dict[str, Any]], federation: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform multiple searches in one request"""
        payload = {'queries': queries}
        if federation is not None:
            payload['federation'] = federation
            
        response = requests.post(
            f'{self.url}/multi-search',
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def federated_search(self, queries: List[Dict[str, Any]], limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Perform federated search (merged results)"""
        federation = {'limit': limit, 'offset': offset}
        return self.multi_search(queries, federation)

# Usage examples
client = MeilisearchClient('http://localhost:7700')

# Basic search
results = client.search('products', 'iPhone 16 Pro')

# Search with filters
results = client.search('products', 'iPhone', filter='price < 30000000')

# Search with sorting
results = client.search('products', 'iPhone', sort=['price:asc'])

# Search with highlighting
results = client.search('products', 'iPhone', 
                       attributesToHighlight=['name', 'description'])

# Non-federated multi-search
results = client.multi_search([
    {'indexUid': 'products', 'q': 'iPhone', 'limit': 5},
    {'indexUid': 'accessories', 'q': 'case', 'limit': 3}
])

# Federated multi-search (merged results)
federated_results = client.federated_search([
    {'indexUid': 'products', 'q': 'iPhone'},
    {'indexUid': 'accessories', 'q': 'case'}
], limit=10)
```

### JavaScript Implementation

```javascript
class MeilisearchClient {
    constructor(url, apiKey = null) {
        this.url = url.replace(/\/$/, '');
        this.headers = {
            'Content-Type': 'application/json'
        };
        if (apiKey) {
            this.headers['Authorization'] = `Bearer ${apiKey}`;
        }
    }
    
    async search(indexUid, query, params = {}) {
        const searchParams = { q: query, ...params };
        const response = await fetch(`${this.url}/indexes/${indexUid}/search`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(searchParams)
        });
        
        if (!response.ok) {
            throw new Error(`Search failed: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    async multiSearch(queries, federation = null) {
        const payload = { queries };
        if (federation !== null) {
            payload.federation = federation;
        }
        
        const response = await fetch(`${this.url}/multi-search`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`Multi-search failed: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    async federatedSearch(queries, limit = 20, offset = 0) {
        const federation = { limit, offset };
        return await this.multiSearch(queries, federation);
    }
}

// Usage examples
const client = new MeilisearchClient('http://localhost:7700');

// Basic search
const results = await client.search('products', 'iPhone 16 Pro');

// Search with filters
const filteredResults = await client.search('products', 'iPhone', {
    filter: 'price < 30000000'
});

// Non-federated multi-search
const multiResults = await client.multiSearch([
    { indexUid: 'products', q: 'iPhone', limit: 5 },
    { indexUid: 'accessories', q: 'case', limit: 3 }
]);

// Federated multi-search (merged results)
const federatedResults = await client.federatedSearch([
    { indexUid: 'products', q: 'iPhone' },
    { indexUid: 'accessories', q: 'case' }
], 10);
```

## Advanced Features

### 1. Ranking Score Threshold

Filter out low-relevance results:

```json
{
  "q": "badman",
  "rankingScoreThreshold": 0.2
}
```

### 2. Custom Search Attributes

Restrict search to specific fields:

```json
{
  "q": "adventure",
  "attributesToSearchOn": ["overview"]
}
```

### 3. Query Locales

Explicitly set query language:

```json
{
  "q": "QUERY TEXT IN JAPANESE",
  "locales": ["jpn"]
}
```

### 4. Vector Retrieval

Get document embeddings:

```json
{
  "q": "kitchen utensils",
  "retrieveVectors": true,
  "hybrid": {
    "embedder": "EMBEDDER_NAME"
  }
}
```

## Error Handling

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `401`: Unauthorized (invalid API key)
- `404`: Index not found
- `422`: Invalid request body
- `500`: Internal server error

## Performance Tips

1. **Use POST for authenticated requests** - Better caching and performance
2. **Limit results** - Use `limit` parameter to control response size
3. **Use filters** - More efficient than post-processing
4. **Cache frequently used queries** - Meilisearch supports preflight caching
5. **Use ranking score threshold** - Filter out irrelevant results early

## Integration Patterns

### 1. Product Search

```python
def search_products(query: str, filters: Dict = None, sort: str = None):
    params = {'limit': 20}
    if filters:
        filter_str = ' AND '.join([f"{k} = '{v}'" for k, v in filters.items()])
        params['filter'] = filter_str
    if sort:
        params['sort'] = [sort]
    
    return client.search('products', query, **params)
```

### 2. Multi-Index Search

```python
def search_all_categories(query: str):
    """Search across multiple product categories"""
    queries = [
        {'indexUid': 'phones', 'q': query, 'limit': 5},
        {'indexUid': 'laptops', 'q': query, 'limit': 5},
        {'indexUid': 'accessories', 'q': query, 'limit': 3}
    ]
    
    # Non-federated: separate results for each category
    return client.multi_search(queries)

def search_unified(query: str):
    """Federated search with merged results"""
    queries = [
        {'indexUid': 'phones', 'q': query},
        {'indexUid': 'laptops', 'q': query},
        {'indexUid': 'accessories', 'q': query}
    ]
    
    # Federated: single merged result list
    return client.federated_search(queries, limit=20)
```

### 3. Faceted Navigation

```python
def get_faceted_results(query: str, selected_facets: Dict):
    params = {
        'facets': ['category', 'brand', 'price_range'],
        'limit': 20
    }
    
    if selected_facets:
        filters = []
        for facet, value in selected_facets.items():
            filters.append(f"{facet} = '{value}'")
        params['filter'] = ' AND '.join(filters)
    
    return client.search('products', query, **params)
```

### 4. Auto-complete

```python
def get_suggestions(query: str, limit: int = 5):
    return client.search('products', query, 
                        limit=limit,
                        attributesToRetrieve=['name', 'brand'])
```

## Best Practices

1. **Index Design**: Structure your documents for optimal search
2. **Query Optimization**: Use appropriate filters and sorting
3. **Error Handling**: Always handle API errors gracefully
4. **Caching**: Implement client-side caching for frequent queries
5. **Monitoring**: Track search performance and user behavior
6. **Security**: Use API keys for production environments

---

*This documentation is based on Meilisearch API reference and is designed for LLM consumption and code generation.*
