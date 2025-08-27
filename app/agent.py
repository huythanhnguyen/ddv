"""Root agent orchestrator for DDV Product Advisor.

Keeps high-level coordination minimal and delegates detailed behavior to
`ROOT_AGENT_INSTR` and sub-agents. Avoids duplicating prompt logic here.
"""

from google.adk.agents import Agent

from app.config import config
from app.prompt import ROOT_AGENT_INSTR
from app.sub_agents.product.agent import product_agent

# Root agent for DDV Product Advisor - simplified ADK framework pattern
ddv_product_advisor = Agent(
    name="ddv_product_advisor",
    model=config.primary_model,
    # Short, non-overlapping description; all behavioral rules live in ROOT_AGENT_INSTR
    description="Root điều phối tư vấn mua điện thoại Di Động Việt; trả lời ngắn gọn, rõ ràng.",
    instruction=ROOT_AGENT_INSTR,
    tools=[],  # Root agent không gọi tool trực tiếp; uỷ quyền cho sub-agents
    sub_agents=[product_agent],
    output_key="ddv_advisor_response",
)

# This is required for ADK web UI to find the agent
root_agent = ddv_product_advisor
