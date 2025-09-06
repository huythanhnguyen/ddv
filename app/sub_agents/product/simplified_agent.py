"""
Simplified Product Agent for DDV Product Advisor - Refactored
Focus on search functionality with improved error handling and modularity
"""

import logging
from google.adk.agents import Agent

from ...config import config
from .simplified_prompt import SIMPLIFIED_PRODUCT_AGENT_INSTR, SIMPLIFIED_PRODUCT_AGENT_DESCRIPTION
from .product_tools import (
    enhanced_product_search_tool,
    product_compare_tool,
    product_price_analysis_tool
)

logger = logging.getLogger(__name__)

# Define the Simplified Product Agent following simplified ADK framework pattern
simplified_product_agent = Agent(
    name="simplified_product_advisor_agent",
    model=config.worker_model,
    description=SIMPLIFIED_PRODUCT_AGENT_DESCRIPTION,
    instruction=SIMPLIFIED_PRODUCT_AGENT_INSTR,
    tools=[
        enhanced_product_search_tool,
        product_compare_tool,
        product_price_analysis_tool
    ],
    output_key="simplified_product_advisor_response",
)

logger.info("✅ Simplified Product Agent initialized with refactored tools")
