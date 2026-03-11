from agents import Agent, output_guardrail, Runner, RunContextWrapper, GuardrailFunctionOutput
from models import OutputGuardRailOutput, UserAccountContext

output_guardrail_agent = Agent(
    name="Output Guardrail",
    instructions="""
    Professional and courteous responses. 
    No disclosure of confidential information. No disclosure of personal information. 
    No disclosure of sensitive information. No disclosure of any information that is not related to the customer's support issue.
    
    Customer support agents should ONLY provide customer support related information.
    Return true for any field that contains inappropriate content for a customer support response.
    """,
    output_type=OutputGuardRailOutput,
)

@output_guardrail
async def output_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
    output: str,
):
    result = await Runner.run(
    output_guardrail_agent, 
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