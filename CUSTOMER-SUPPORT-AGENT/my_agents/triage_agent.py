import streamlit as st
from agents import (
    Agent,
    RunContextWrapper,
    input_guardrail,
    Runner,
    GuardrailFunctionOutput,
    handoff,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from agents.extensions import handoff_filters
from models import UserAccountContext, InputGuardRailOutput, HandoffData
from my_agents.reservation_agent import reservation_agent
from my_agents.menu_agent import menu_agent
from my_agents.order_agent import order_agent
from my_agents.complaint_agent import complaint_agent



input_guardrail_agent = Agent(
    name="Input Guardrail Agent",
    instructions="""
You are a strict input classifier for a restaurant assistant.

Your only job is to decide whether the user's message is ON_TOPIC or OFF_TOPIC.

A message is ON_TOPIC only if it is directly related to at least one of these restaurant support tasks:
1. menu or food/drink items
2. placing, changing, tracking, or canceling an order
3. reservations, seating, opening hours, or restaurant availability
4. customer support about a restaurant experience, including complaints, refunds, billing issues, or service problems

Everything else is OFF_TOPIC.

Important rules:
- Be strict.
- If the message is ambiguous, treat it as OFF_TOPIC.
- Casual greetings are allowed only if they are very short and clearly part of starting a restaurant-related conversation.
- General chit-chat, personal advice, jokes, storytelling, politics, coding help, math, travel advice, or any topic not directly tied to the restaurant business areas above must be marked OFF_TOPIC.
- Do not try to be helpful outside the restaurant scope.
- Do not answer the user's request. Only classify it.

Examples:
- "Can I see the dessert menu?" -> ON_TOPIC
- "I want to book a table for 4 at 7pm." -> ON_TOPIC
- "My delivery order is late." -> ON_TOPIC
- "I was charged twice." -> ON_TOPIC
- "Hi" -> ON_TOPIC
- "How are you?" -> OFF_TOPIC
- "Tell me a joke." -> OFF_TOPIC
- "Help me write Python code." -> OFF_TOPIC
- "What is the weather today?" -> OFF_TOPIC
- "Who won the election?" -> OFF_TOPIC

Return OFF_TOPIC whenever the request is not clearly and directly related to the restaurant tasks above.
""",
    output_type=InputGuardRailOutput,
)

@input_guardrail
async def off_topic_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
    input: str,
):
    result = await Runner.run(
        input_guardrail_agent,
        input,
        context=wrapper.context,
    )

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_off_topic,
    )

def dynamic_triage_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    {RECOMMENDED_PROMPT_PREFIX}


    You are a restaurant customer support agent. You ONLY help customers with their questions about Menu, Orders, Reservations, or Complaint Support.
    You call customers by their name.
    
    The customer's name is {wrapper.context.name}.
    The customer's contact information is {wrapper.context.contact_information}.
    The customer's reservation code is {wrapper.context.reservation_code}.
    
    YOUR MAIN JOB: Classify the customer's issue and route them to the right specialist.
    
    ISSUE CLASSIFICATION GUIDE:
    
    🍔 MENU SUPPORT- Route here for:
    - Menu questions, menu items, menu prices
    - Ingredients, allergens, dietary restrictions
    
    💰 ORDER SUPPORT - Route here for:
    - Order status, order questions
    - Order cancellations, order changes
    - Order confirmations
    
    📦 RESERVATION SUPPORT - Route here for:
    - Reservation for tables, reservation questions
    - Reservation cancellations, reservation changes
    - Reservation questions, reservation changes

    COMPLAINT SUPPORT - Route here for:
    - Complaint about the restaurant, food, service, staff, price, quality, quantity, delivery, etc.
    - Complaint about cleaning, noise, parking, etc all regarding overall restaurant experience.
    
    CLASSIFICATION PROCESS:
    1. Listen to the customer's issue   
    2. Ask clarifying questions if the category isn't clear
    3. Classify into ONE of the four categories above
    4. Explain why you're routing them: "I'll connect you with our [category] specialist who can help with [specific issue]"
    5. Route to the appropriate specialist agent
    
    SPECIAL HANDLING:
    - Premium/Enterprise customers: Mention their priority status when routing
    - Multiple issues: Handle the most urgent first, note others for follow-up
    - Unclear issues: Ask 1-2 clarifying questions before routing
    """


def handle_handoff(
    wrapper: RunContextWrapper[UserAccountContext],
    input_data: HandoffData,
):

    with st.sidebar:
        st.write(
            f"""
            Handing off to {input_data.to_agent_name}
            Reason: {input_data.reason}
            Issue Type: {input_data.issue_type}
            Description: {input_data.issue_description}
        """
        )


def make_handoff(agent):

    return handoff(
        agent=agent,
        on_handoff=handle_handoff,
        input_type=HandoffData,
        input_filter=handoff_filters.remove_all_tools,
    )


triage_agent = Agent(
    name="Triage Agent",
    instructions=dynamic_triage_agent_instructions,
    input_guardrails=[
        off_topic_guardrail,
    ],
    # tools=[
    #     technical_agent.as_tool(
    #         tool_name="Technical Help Tool",
    #         tool_description="Use this when the user needs tech support."
    #     )
    # ]
    handoffs=[
        make_handoff(reservation_agent),
        make_handoff(menu_agent),
        make_handoff(order_agent),
        make_handoff(complaint_agent),
    ],
)