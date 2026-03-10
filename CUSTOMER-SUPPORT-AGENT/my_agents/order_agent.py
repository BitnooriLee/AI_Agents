from agents import Agent, RunContextWrapper
from models import UserAccountContext
from tools import (
    lookup_order_status,
    AgentToolUsageLoggingHooks,
)


def dynamic_order_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    You are a Restaurant Order Support specialist helping {wrapper.context.name}.
    Customer tier: {wrapper.context.tier} {"(Premium Order Support)" if wrapper.context.tier != "basic" else ""}
    
    YOUR ROLE: Provide order information to the customer.
    
    ORDER INFORMATION:
    - Order status
    - Order questions
    - Order cancellations
    - Order changes
    
    CANCELLATION POLICY:
    - 24 hours cancellation window for most items  
    {"PREMIUM PERKS: Free cancellation, priority processing." if wrapper.context.tier != "basic" else ""}
    """


order_agent = Agent(
    name="Order Management Agent",
    instructions=dynamic_order_agent_instructions,
    tools=[
        lookup_order_status,
    ],
    hooks=AgentToolUsageLoggingHooks(),
)