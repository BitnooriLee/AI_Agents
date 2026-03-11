from agents import Agent, RunContextWrapper
from models import UserAccountContext
from tools import (
    complaint_support,
    AgentToolUsageLoggingHooks,
)


def dynamic_complaint_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    You are a Restaurant Complaint Support specialist helping {wrapper.context.name}.
    Customer tier: {wrapper.context.tier} {"(Premium Complaint Support)" if wrapper.context.tier != "basic" else ""}
    
    YOUR ROLE: Empathize with and acknowledge customer complaints, Offer solutions (refunds, discounts, manager calls back), Appropriately escalate serious issues
    
    COMPLAINT INFORMATION:
    - Complaint about the restaurant, food, service, staff, price, quality, quantity, delivery
    """


complaint_agent = Agent(
    name="Complaint Support Agent",
    instructions=dynamic_complaint_agent_instructions,
    tools=[
        complaint_support,
    ],
    hooks=AgentToolUsageLoggingHooks(),
)