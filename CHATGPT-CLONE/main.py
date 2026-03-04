import dotenv

dotenv.load_dotenv()
from openai import OpenAI
import asyncio
import streamlit as st
<<<<<<< HEAD
from agents import Agent, Runner, SQLiteSession, WebSearchTool, FileSearchTool


client = OpenAI()

VECTOR_STORE_ID = "vs_697e40198c28819197e07822c03fc07f"

if "agent" not in st.session_state:
    st.session_state["agent"] = Agent(
        name="Life Coach",
        instructions="""
        You are a life coach.
        You are helping the user to achieve their goals.
        You are using the following tools:
            - Web Search Tool: Use this when the user asks a question that isn't in your training data. It's atool for motivational content, self-improvement tips, and habit-building advice. Use this to learn about current events.
            - File Search Tool: Use this tool when the user asks a question about facts related to themselves. Or when they ask questions about specific files.
        """,
        #tools=[WebSearchTool(), get_advice],
         tools=[
            WebSearchTool(),
            FileSearchTool(
                vector_store_ids=[VECTOR_STORE_ID],
                max_num_results=3,
            ),
        ],
    )
agent = st.session_state["agent"]
=======
from agents import Runner, SQLiteSession, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered
from models import UserAccountContext
from my_agents.triage_agent import triage_agent

client = OpenAI()

user_account_ctx = UserAccountContext(
    customer_id=1,
    name="nico",
    tier="basic",
)

>>>>>>> main

if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history",
        "customer-support-memory.db",
    )
session = st.session_state["session"]

if "agent" not in st.session_state:
    st.session_state["agent"] = triage_agent


async def paint_history():
    messages = await session.get_items()
    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                else:
                    if message["type"] == "message":
<<<<<<< HEAD
                        st.write(message["content"][0]["text"])
        if "type" in message:
            if message["type"] == "web_search_call":
                with st.chat_message("coach"):
                    st.write("🔍 Searched the web...")
            elif message["type"] == "file_search_call":
                with st.chat_message("coach"):
                    st.write("🗂️ Searched your files...")

asyncio.run(paint_history())

def update_status(status_container, event):
    status_messages = {
        "response.web_search_call.completed": ("✅ Web search completed.", "complete"),
        "response.web_search_call.in_progress": (
            "🔍 Starting web search...",
            "running",
        ),
        "response.web_search_call.searching": (
            "🔍 Web search in progress...",
            "running",
        ),
        "response.file_search_call.completed": (
            "✅ File search completed.",
            "complete",
        ),
        "response.file_search_call.in_progress": (
            "🗂️ Starting file search...",
            "running",
        ),
        "response.file_search_call.searching": (
            "🗂️ File search in progress...",
            "running",
        ),
        "response.completed": (" ", "complete"),
    }

    if event in status_messages:
        label, state = status_messages[event]
        status_container.update(label=label, state=state)

async def run_agent(message):
    with st.chat_message("coach"):
=======
                        st.write(message["content"][0]["text"].replace("$", "\$"))


asyncio.run(paint_history())


async def run_agent(message):

    with st.chat_message("ai"):
>>>>>>> main
        text_placeholder = st.empty()
        response = ""

<<<<<<< HEAD
        async for event in stream.stream_events():
            if event.type == "raw_response_event":
                
                update_status(status_container, event.data.type)
=======
        st.session_state["text_placeholder"] = text_placeholder

        try:
>>>>>>> main

            stream = Runner.run_streamed(
                st.session_state["agent"],
                message,
                session=session,
                context=user_account_ctx,
            )

            async for event in stream.stream_events():
                if event.type == "raw_response_event":

                    if event.data.type == "response.output_text.delta":
                        response += event.data.delta
                        text_placeholder.write(response.replace("$", "\$"))

                elif event.type == "agent_updated_stream_event":

                    if st.session_state["agent"].name != event.new_agent.name:
                        
                        st.write(f"🤖 Transfered from {st.session_state["agent"].name} to {event.new_agent.name}")

                        st.session_state["agent"] = event.new_agent

                        text_placeholder = st.empty()

                        st.session_state["text_placeholder"] = text_placeholder
                        response = ""

        except InputGuardrailTripwireTriggered:
            st.write("I can't help you with that.")


<<<<<<< HEAD
prompt =st.chat_input(
    "Write a message for your life coach",
    accept_file=True,
    file_type=["txt"],
    )

if prompt:

    for file in prompt.files:
        if file.type.startswith("text/"):
            with st.chat_message("coach"):
                with st.status("⏳ Uploading file...") as status:
                    uploaded_file = client.files.create(
                        file=(file.name, file.getvalue()),
                        purpose="user_data",
                    )
                    status.update(label="⏳ Attaching file...")
                    client.vector_stores.files.create(
                        vector_store_id=VECTOR_STORE_ID,
                        file_id=uploaded_file.id,
                    )
                    status.update(label="✅ File uploaded", state="complete")

    if prompt.text:
        with st.chat_message("human"):
            st.write(prompt.text)
        asyncio.run(run_agent(prompt.text))


=======
        except OutputGuardrailTripwireTriggered:
            st.write("Cant show you that answer.")
            st.session_state["text_placeholder"].empty()

message = st.chat_input(
    "Write a message for your assistant",
)

if message:

    if message:
        with st.chat_message("human"):
            st.write(message)
        asyncio.run(run_agent(message))

>>>>>>> main

with st.sidebar:
    reset = st.button("Reset memory")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))