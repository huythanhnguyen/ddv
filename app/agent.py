"""
Root agent orchestrator for DDV Product Advisor - Refactored
Keeps high-level coordination minimal and delegates detailed behavior to
sub-agents with improved error handling and initialization
"""

import logging
from google.adk.agents import Agent

from app.config import config
from app.prompt import ROOT_AGENT_INSTR
from app.sub_agents.product import simplified_product_agent
from app.tools.tools_manager import tools_manager

logger = logging.getLogger(__name__)

def initialize_agents():
    """Initialize all agents and tools"""
    try:
        logger.info("🚀 Initializing DDV Product Advisor agents...")
        
        # Initialize tools manager first
        if not tools_manager.initialize():
            logger.error("❌ Failed to initialize tools manager")
            return False
        
        logger.info("✅ DDV Product Advisor agents initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error initializing agents: {e}")
        return False

# Root agent for DDV Product Advisor - simplified ADK framework pattern
ddv_product_advisor = Agent(
    name="ddv_product_advisor",
    model=config.primary_model,
    # Short, non-overlapping description; all behavioral rules live in ROOT_AGENT_INSTR
    description="Root điều phối tư vấn mua điện thoại Di Động Việt; trả lời ngắn gọn, rõ ràng.",
    instruction=ROOT_AGENT_INSTR,
    tools=[],  # Root agent không gọi tool trực tiếp; uỷ quyền cho sub-agents
    sub_agents=[simplified_product_agent],
    output_key="ddv_advisor_response",
)

# Initialize agents on import
initialize_agents()

# This is required for ADK web UI to find the agent
root_agent = ddv_product_advisor

logger.info("✅ Root agent configured and ready")
