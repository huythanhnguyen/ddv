"""Product Agent for DDV Product Advisor - Simplified ADK Framework Implementation"""

from google.adk.agents import Agent

from app.config import config
from app.sub_agents.product.prompt import PRODUCT_AGENT_INSTR, PRODUCT_AGENT_DESCRIPTION
from app.sub_agents.product.tools import (
    product_search_tool,
    price_analysis_tool,
    store_location_tool,
    product_compare_tool,
    store_availability_tool,
    integrated_recommendation_tool
)

# Define the Product Agent following simplified ADK framework pattern
product_agent = Agent(
    name="product_advisor_agent",
    model=config.worker_model,
    description=PRODUCT_AGENT_DESCRIPTION,
    instruction=PRODUCT_AGENT_INSTR,
    tools=[
        product_search_tool,
        price_analysis_tool,
        store_location_tool,
        product_compare_tool,
        store_availability_tool,
        integrated_recommendation_tool
    ],
    output_key="product_advisor_response",
)
