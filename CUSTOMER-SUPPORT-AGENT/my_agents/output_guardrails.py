from agents import Agent, output_guardrail, Runner, RunContextWrapper, GuardrailFunctionOutput
from models import MenuOutputGuardRailOutput, OrderOutputGuardRailOutput, ReservationOutputGuardRailOutput, UserAccountContext

menu_output_guardrail_agent = Agent(
    name="Menu Output Guardrail",
    instructions="""
    Analyze the menu support response to check if it inappropriately contains:
    
    - Menu information (menu items, menu prices, menu ingredients, menu allergens, menu dietary restrictions)
    - Order information (order status, order questions, order cancellations, order changes)
    - Reservation information (reservation status, reservation questions, reservation cancellations, reservation changes)
    
    Menu agents should ONLY provide restaurant related information.
    Return true for any field that contains inappropriate content for a menu support response.
    """,
    output_type=OrderOutputGuardRailOutput,
)

@output_guardrail
async def order_output_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
    output: str,
):
    result = await Runner.run(
    menu_output_guardrail_agent, 
    output, 
    context=wrapper.context,
    )
    validation = result.final_output
    triggered = (validation.contains_off_topic 
    or validation.contains_billing_data 
    or validation.contains_order_data 
    or validation.contains_account_data
    )

    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=triggered,
    )