"""Simplified Product Agent for DDV Product Advisor - Focus on Search Functionality"""

from google.adk.agents import Agent

from ...config import config
from .simplified_prompt import SIMPLIFIED_PRODUCT_AGENT_INSTR, SIMPLIFIED_PRODUCT_AGENT_DESCRIPTION
from .simplified_tools import (
    enhanced_product_search_tool,
    simplified_product_compare_tool,
    basic_price_analysis_tool
)

# Define the Simplified Product Agent following simplified ADK framework pattern
simplified_product_agent = Agent(
    name="simplified_product_advisor_agent",
    model=config.worker_model,
    description=SIMPLIFIED_PRODUCT_AGENT_DESCRIPTION,
    instruction=SIMPLIFIED_PRODUCT_AGENT_INSTR,
    tools=[
        enhanced_product_search_tool
    ],
    output_key="simplified_product_advisor_response",
)
