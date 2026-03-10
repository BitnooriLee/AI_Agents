from agents import Agent, RunContextWrapper
from models import UserAccountContext
from tools import (
    lookup_menu_information,
    AgentToolUsageLoggingHooks,
)


def dynamic_menu_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    You are a Restaurant Menu Support specialist helping {wrapper.context.name}.
    Customer tier: {wrapper.context.tier} {"(Premium Menu Support)" if wrapper.context.tier != "basic" else ""}
    
    YOUR ROLE: Provide menu information to the customer.
    
    COMMON MENU ISSUES:
    - Menu items, menu prices, menu ingredients, menu allergens, menu dietary restrictions
    - Menu questions, menu items, menu prices
    - Ingredients, allergens, dietary restrictions
    """


menu_agent = Agent(
    name="Menu Support Agent",
    instructions=dynamic_menu_agent_instructions,
    tools=[
        lookup_menu_information,
    ],
    hooks=AgentToolUsageLoggingHooks(),
)