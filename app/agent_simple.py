"""
Simple DDV Product Advisor Agent - Inspired by personalized_shopping
Clean, simple structure with specialized tools
"""

import logging
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from app.config_simple import MODEL_CONFIG
from app.prompt_simple import DDV_AGENT_INSTRUCTION
from app.tools.search import search_products
from app.tools.explore import explore_product
from app.tools.compare import compare_products

logger = logging.getLogger(__name__)

# Simple DDV Product Advisor Agent following personalized_shopping pattern
ddv_simple_agent = Agent(
    model=MODEL_CONFIG["primary_model"],
    name="ddv_simple_advisor",
    instruction=DDV_AGENT_INSTRUCTION,
    tools=[
        search_products,
        explore_product,
        compare_products
    ],
    output_key="product_simple_agent"
)

# This is required for ADK web UI to find the agent
root_agent = ddv_simple_agent

logger.info("✅ Simple DDV Product Advisor Agent initialized")
