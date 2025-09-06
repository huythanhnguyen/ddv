"""
Health Check Tool for DDV Product Advisor
Provides system health monitoring and diagnostics
"""

import logging
import time
from typing import Dict, Any, Optional
from pathlib import Path

from .tools_manager import tools_manager

logger = logging.getLogger(__name__)

def system_health_check() -> Dict[str, Any]:
    """
    Perform comprehensive system health check
    
    Returns:
        Dict containing health status of all components
    """
    health_status = {
        "timestamp": time.time(),
        "overall_status": "unknown",
        "components": {},
        "errors": [],
        "warnings": []
    }
    
    try:
        # Check tools manager
        tools_health = tools_manager.health_check()
        health_status["components"]["tools_manager"] = tools_health
        
        if not tools_health.get("tools_manager_initialized", False):
            health_status["errors"].append("Tools manager not initialized")
        
        # Check Meilisearch connection
        try:
            import requests
            response = requests.get("http://localhost:7700/health", timeout=5)
            if response.status_code == 200:
                health_status["components"]["meilisearch"] = {
                    "status": "healthy",
                    "response": response.json()
                }
            else:
                health_status["components"]["meilisearch"] = {
                    "status": "unhealthy",
                    "status_code": response.status_code
                }
                health_status["errors"].append(f"Meilisearch returned status {response.status_code}")
        except Exception as e:
            health_status["components"]["meilisearch"] = {
                "status": "unreachable",
                "error": str(e)
            }
            health_status["errors"].append(f"Meilisearch unreachable: {e}")
        
        # Check data files
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / "profiles"
        merged_products_file = data_dir / "merged_products.json"
        
        if merged_products_file.exists():
            file_size = merged_products_file.stat().st_size
            health_status["components"]["data_files"] = {
                "status": "healthy",
                "merged_products_file": str(merged_products_file),
                "file_size_bytes": file_size
            }
        else:
            health_status["components"]["data_files"] = {
                "status": "missing",
                "merged_products_file": str(merged_products_file)
            }
            health_status["errors"].append("Merged products file not found")
        
        # Determine overall status
        if health_status["errors"]:
            health_status["overall_status"] = "unhealthy"
        elif health_status["warnings"]:
            health_status["overall_status"] = "degraded"
        else:
            health_status["overall_status"] = "healthy"
        
        logger.info(f"Health check completed: {health_status['overall_status']}")
        
    except Exception as e:
        health_status["overall_status"] = "error"
        health_status["errors"].append(f"Health check failed: {e}")
        logger.error(f"Health check failed: {e}")
    
    return health_status

def quick_health_check() -> bool:
    """
    Perform quick health check
    
    Returns:
        True if system is healthy, False otherwise
    """
    try:
        # Check if tools manager is initialized
        if not tools_manager.is_initialized:
            return False
        
        # Check Meilisearch connection
        import requests
        response = requests.get("http://localhost:7700/health", timeout=2)
        return response.status_code == 200
        
    except Exception:
        return False

def get_system_stats() -> Dict[str, Any]:
    """
    Get system statistics
    
    Returns:
        Dict containing system statistics
    """
    stats = {
        "timestamp": time.time(),
        "tools_manager": {},
        "meilisearch": {},
        "data_files": {}
    }
    
    try:
        # Get tools manager stats
        if tools_manager.is_initialized:
            stats["tools_manager"] = tools_manager.get_search_stats()
        
        # Get Meilisearch stats
        try:
            import requests
            response = requests.get("http://localhost:7700/indexes/ddv_products/stats", timeout=5)
            if response.status_code == 200:
                stats["meilisearch"] = response.json()
        except Exception as e:
            stats["meilisearch"] = {"error": str(e)}
        
        # Get data file stats
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / "profiles"
        merged_products_file = data_dir / "merged_products.json"
        
        if merged_products_file.exists():
            file_stat = merged_products_file.stat()
            stats["data_files"] = {
                "merged_products_file": str(merged_products_file),
                "file_size_bytes": file_stat.st_size,
                "last_modified": file_stat.st_mtime
            }
        
    except Exception as e:
        stats["error"] = str(e)
        logger.error(f"Error getting system stats: {e}")
    
    return stats


