#!/usr/bin/env python3
"""
Test script for refactored agents and tools
"""

import sys
import logging
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_tools_manager():
    """Test tools manager initialization and functionality"""
    print("🧪 Testing Tools Manager...")
    
    try:
        from app.tools.tools_manager import tools_manager
        
        # Test initialization
        if tools_manager.initialize():
            print("✅ Tools Manager initialized successfully")
        else:
            print("❌ Tools Manager initialization failed")
            return False
        
        # Test health check
        health = tools_manager.health_check()
        print(f"📊 Health check: {health.get('tools_manager_initialized', False)}")
        
        # Test search functionality
        results = tools_manager.search_products("iPhone", limit=3)
        print(f"🔍 Search test: Found {len(results)} products")
        
        return True
        
    except Exception as e:
        print(f"❌ Tools Manager test failed: {e}")
        return False

def test_product_tools():
    """Test product tools functionality"""
    print("\n🧪 Testing Product Tools...")
    
    try:
        from app.sub_agents.product.product_tools import (
            enhanced_product_search_tool,
            product_compare_tool,
            product_price_analysis_tool
        )
        
        # Test search tool
        print("🔍 Testing enhanced_product_search_tool...")
        search_result = enhanced_product_search_tool("iPhone 16")
        
        if search_result.get("success"):
            print(f"✅ Search tool: Found {search_result.get('total_found', 0)} products")
            
            # Test compare tool if we have products
            products = search_result.get("products", [])
            if len(products) >= 2:
                print("🔄 Testing product_compare_tool...")
                product_ids = [p.get("id") for p in products[:2]]
                compare_result = product_compare_tool(product_ids)
                
                if compare_result.get("success"):
                    print(f"✅ Compare tool: Compared {compare_result.get('comparison', {}).get('total_products', 0)} products")
                else:
                    print(f"❌ Compare tool failed: {compare_result.get('message', 'Unknown error')}")
            
            # Test price analysis tool if we have a product
            if products:
                print("💰 Testing product_price_analysis_tool...")
                price_result = product_price_analysis_tool(products[0].get("id"))
                
                if price_result.get("success"):
                    analysis = price_result.get("analysis", {})
                    print(f"✅ Price analysis: {analysis.get('product_name', 'Unknown')} - {analysis.get('current_price', 0):,} VND")
                else:
                    print(f"❌ Price analysis failed: {price_result.get('message', 'Unknown error')}")
        else:
            print(f"❌ Search tool failed: {search_result.get('message', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Product tools test failed: {e}")
        return False

def test_agent_initialization():
    """Test agent initialization"""
    print("\n🧪 Testing Agent Initialization...")
    
    try:
        from app.agent import ddv_product_advisor, root_agent
        from app.sub_agents.product.simplified_agent import simplified_product_agent
        
        # Test root agent
        print(f"✅ Root agent: {ddv_product_advisor.name}")
        print(f"✅ Root agent model: {ddv_product_advisor.model}")
        print(f"✅ Root agent sub-agents: {len(ddv_product_advisor.sub_agents)}")
        
        # Test simplified product agent
        print(f"✅ Product agent: {simplified_product_agent.name}")
        print(f"✅ Product agent tools: {len(simplified_product_agent.tools)}")
        
        # Test root_agent export
        if root_agent == ddv_product_advisor:
            print("✅ Root agent export correct")
        else:
            print("❌ Root agent export incorrect")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Agent initialization test failed: {e}")
        return False

def test_health_check():
    """Test health check functionality"""
    print("\n🧪 Testing Health Check...")
    
    try:
        from app.tools.health_check import system_health_check, quick_health_check, get_system_stats
        
        # Test quick health check
        quick_health = quick_health_check()
        print(f"⚡ Quick health check: {'✅ Healthy' if quick_health else '❌ Unhealthy'}")
        
        # Test system health check
        health = system_health_check()
        print(f"🏥 System health: {health.get('overall_status', 'unknown')}")
        
        if health.get("errors"):
            print(f"❌ Errors: {health['errors']}")
        
        if health.get("warnings"):
            print(f"⚠️ Warnings: {health['warnings']}")
        
        # Test system stats
        stats = get_system_stats()
        print(f"📊 System stats retrieved: {len(stats)} components")
        
        return True
        
    except Exception as e:
        print(f"❌ Health check test failed: {e}")
        return False

def test_imports():
    """Test all imports work correctly"""
    print("\n🧪 Testing Imports...")
    
    try:
        # Test tools imports
        from app.tools import (
            MeilisearchEngine,
            GeminiSearchEngine,
            EnhancedProductStore,
            enhanced_data_store,
            ToolsManager,
            tools_manager
        )
        print("✅ Tools imports successful")
        
        # Test agent imports
        from app.agent import ddv_product_advisor, root_agent
        from app.sub_agents.product import simplified_product_agent
        print("✅ Agent imports successful")
        
        # Test product tools imports
        from app.sub_agents.product.product_tools import (
            enhanced_product_search_tool,
            product_compare_tool,
            product_price_analysis_tool
        )
        print("✅ Product tools imports successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Refactored Agents and Tools Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Tools Manager", test_tools_manager),
        ("Product Tools", test_product_tools),
        ("Agent Initialization", test_agent_initialization),
        ("Health Check", test_health_check),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name} passed")
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Refactored code is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


