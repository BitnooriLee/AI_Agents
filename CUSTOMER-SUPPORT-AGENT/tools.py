import streamlit as st
from agents import function_tool, AgentHooks, Agent, Tool, RunContextWrapper
from models import UserAccountContext
import random
from datetime import datetime, timedelta


# =============================================================================
# RESERVATION SUPPORT TOOLS
# =============================================================================

@function_tool
def make_reservation(
    context: UserAccountContext, reservation_code: str
) -> str:
    """
    Make a reservation for the customer.

    Args:
        reservation_date: Reservation date
        reservation_time: Reservation time
        reservation_party_size: Reservation party size
    """
    return f"🔍 Reservation status for {reservation_code}:\n" + "Reservation status: " + random.choice(["Confirmed", "Cancelled", "Pending"])

@function_tool
def reservation_check(
    context: UserAccountContext, reservation_code: str
) -> str:
    """
    Check the status of the customer's reservation.

    Args:
        reservation_code: Reservation code to check
    """
    return f"🔍 Reservation status for {reservation_code}:\n" + "Reservation status: " + random.choice(["Confirmed", "Cancelled", "Pending"])

@function_tool
def reservation_cancel(context: UserAccountContext, reservation_code: str) -> str:
    """
    Cancel the customer's reservation.

    Args:
        reservation_code: Reservation code to cancel
    """
    return f"🔍 Reservation cancelled for {reservation_code}:\n" + "Reservation cancelled: " + random.choice(["Confirmed", "Cancelled", "Pending"])

@function_tool
def reservation_change(context: UserAccountContext, reservation_code: str, new_reservation_code: str) -> str:
    """
    Change the customer's reservation.

    Args:
        reservation_code: Reservation code to change
        new_reservation_code: New reservation code
    """
    return f"🔍 Reservation changed for {reservation_code}:\n" + "Reservation changed: " + new_reservation_code

# =============================================================================
# MENU SUPPORT TOOLS
# =============================================================================


@function_tool
def lookup_menu_information(context: UserAccountContext, months_back: int = 6) -> str:
    """
    Look up customer's menu information.

    Args:
        menu_information: Menu information to look up
        menu_prices: Menu prices to look up
        menu_ingredients: Menu ingredients to look up
        menu_allergens: Menu allergens to look up
        menu_dietary_restrictions: Menu dietary restrictions to look up
    """
    return f"🍔 Menu Information:\n" + "Menu items: " + random.choice(["Burgers", "Pizza", "Salads", "Desserts"]) + "\n" + "Menu prices: " + random.choice(["$10", "$15", "$20", "$25"]) + "\n" + "Menu ingredients: " + random.choice(["Beef", "Cheese", "Lettuce", "Tomatoes"]) + "\n" + "Menu allergens: " + random.choice(["Gluten", "Eggs", "Milk", "Soy"]) + "\n" + "Menu dietary restrictions: " + random.choice(["Vegan", "Vegetarian", "Gluten-free", "Kosher"])


# =============================================================================
# ORDER SUPPORT TOOLS
# =============================================================================


@function_tool
def lookup_order_status(context: UserAccountContext, order_number: str) -> str:
    """
    Look up the current status and details of an order.

    Args:
        order_number: Customer's order number
    """
    statuses = ["processing", "cancelled", "delivered"]
    current_status = random.choice(statuses)

    tracking_number = f"1Z{random.randint(100000, 999999)}"
    estimated_delivery = datetime.now() + timedelta(days=random.randint(1, 5))

    return f"""
📦 Order Status: {order_number}
🏷️ Status: {current_status.title()}
    """.strip()



# =============================================================================
# ACCOUNT MANAGEMENT TOOLS
# =============================================================================


@function_tool
def reset_user_password(context: UserAccountContext, email: str) -> str:
    """
    Send password reset instructions to the customer's email.

    Args:
        email: Email address to send reset instructions
    """
    reset_token = f"RST-{random.randint(100000, 999999)}"

    return f"""
🔐 Password reset initiated
📧 Reset link sent to: {email}
🔗 Reset token: {reset_token}
⏰ Link expires in: 1 hour
🛡️ For security, link is single-use only
    """.strip()


@function_tool
def enable_two_factor_auth(context: UserAccountContext, method: str = "app") -> str:
    """
    Help customer set up two-factor authentication.

    Args:
        method: 2FA method (app, sms, email)
    """
    setup_code = f"2FA-{random.randint(100000, 999999)}"

    return f"""
🔒 Two-Factor Authentication Setup
📱 Method: {method.upper()}
🔑 Setup code: {setup_code}
📧 Instructions sent to: {context.email}
⚡ Enhanced security activated
    """.strip()


@function_tool
def update_account_email(
    context: UserAccountContext, old_email: str, new_email: str
) -> str:
    """
    Process account email address change.

    Args:
        old_email: Current email address
        new_email: New email address
    """
    verification_code = f"VER-{random.randint(100000, 999999)}"

    return f"""
📧 Email update requested
📤 From: {old_email}
📥 To: {new_email}
🔐 Verification code: {verification_code}
⏰ Code expires in: 30 minutes
✅ Change will be activated after verification
    """.strip()


@function_tool
def deactivate_account(
    context: UserAccountContext, reason: str, feedback: str = ""
) -> str:
    """
    Process account deactivation request.

    Args:
        reason: Reason for account deactivation
        feedback: Optional feedback from customer
    """
    return f"""
⚠️ Account deactivation initiated
👤 Account: {context.customer_id}
📝 Reason: {reason}
💬 Feedback: {feedback if feedback else 'None provided'}
⏰ Account will be deactivated in 24 hours
🔄 Can be reactivated within 30 days
📧 Confirmation sent to: {context.email}
    """.strip()


@function_tool
def export_account_data(context: UserAccountContext, data_types: str) -> str:
    """
    Generate export of customer's account data.

    Args:
        data_types: Types of data to export (profile, orders, billing, etc.)
    """
    export_id = f"EXP-{random.randint(100000, 999999)}"

    return f"""
📊 Data export requested
🔗 Export ID: {export_id}
📋 Data types: {data_types}
⏱️ Processing time: 2-4 hours
📧 Download link will be sent to: {context.email}
🔒 Link expires in: 7 days
    """.strip()


class AgentToolUsageLoggingHooks(AgentHooks):

    async def on_tool_start(
        self,
        context: RunContextWrapper[UserAccountContext],
        agent: Agent[UserAccountContext],
        tool: Tool,
    ):
        with st.sidebar:
            st.write(f"🔧 **{agent.name}** starting tool: `{tool.name}`")

    async def on_tool_end(
        self,
        context: RunContextWrapper[UserAccountContext],
        agent: Agent[UserAccountContext],
        tool: Tool,
        result: str,
    ):
        with st.sidebar:
            st.write(f"🔧 **{agent.name}** used tool: `{tool.name}`")
            st.code(result)

    async def on_handoff(
        self,
        context: RunContextWrapper[UserAccountContext],
        agent: Agent[UserAccountContext],
        source: Agent[UserAccountContext],
    ):
        with st.sidebar:
            st.write(f"🔄 Handoff: **{source.name}** → **{agent.name}**")

    async def on_start(
        self,
        context: RunContextWrapper[UserAccountContext],
        agent: Agent[UserAccountContext],
    ):
        with st.sidebar:
            st.write(f"🚀 **{agent.name}** activated")

    async def on_end(
        self,
        context: RunContextWrapper[UserAccountContext],
        agent: Agent[UserAccountContext],
        output,
    ):
        with st.sidebar:
            st.write(f"🏁 **{agent.name}** completed")