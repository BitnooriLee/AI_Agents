import dotenv
import asyncio
dotenv.load_dotenv()

from openai import OpenAI
import streamlit as st
from agents import Agent, Runner, SQLiteSession, WebSearchTool, FileSearchTool

client = OpenAI()

VECTOR_STORE_ID = "vs_697e40198c28819197e07822c03fc07f"

if "agent" not in st.session_state:
    st.session_state["agent"] = Agent(
        name="Assistant Agent",
        instructions="""
        You are a helpful assistant.

        You have access to the following tools:
            - Web Search Tool: Use this when the user asks a question that isn't in your training data. Use this to learn about current events.
            - File Search Tool: Use this when the user asks a question that is related to the files in the vector store. Or when the user asks questions about specific files.
        """,
        tools=[
            WebSearchTool(),
            FileSearchTool(
                vector_store_ids=[VECTOR_STORE_ID],
                max_num_results=3,
            ),
            ],
    )
agent = st.session_state["agent"]

if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
    "chat-history",
    "chat-gpt-clone-memory.db",
)
session = st.session_state["session"]

async def paint_history():
    messages = await session.get_items()

    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                else: 
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"].replace("$","\$"))
        if "type" in message:
            if message["type"] == "web_search_call": 
                with st.chat_message("ai"):
                    st.write("Searched the web...") 
            elif message["type"] == "file_search_call":
                with st.chat_message("ai"):
                    st.write("Searched the files...") 

def update_status(status_container, event):
    status_messages = {
        'response.web_search_call.completed' : (" Web Search completed", "complete"),
        'response.web_search_call.in_progress': (" Web Search in progress...", "running"),
        'response.web_search_call.searching': (" Starting web search...", "running"),
        'response.file_search_call.completed' : (" File Search completed", "complete"),
        'response.file_search_call.in_progress': (" File Search in progress...", "running"),
        'response.file_search_call.searching': (" Starting file search...", "running"),
        'response.completes': ("", "complete"),
    }

    if event in status_messages:
        label, state = status_messages[event]
        status_container.update(label=label, state=state)

asyncio.run(paint_history())

async def run_agent(message):
    with st.chat_message("ai"):
        text_placeholder = st.empty()
        response = ""
        status_container = st.status("", expanded=False)
        stream = Runner.run_streamed(
            agent,
            message,
            session=session,
        )

        async for event in stream.stream_events():
            if event.type == "raw_response_event":

                update_status(status_container, event.data.type)

                if event.data.type == "response.output_text.delta":
                    response += event.data.delta
                    text_placeholder.write(response.replace("$","\$"))


prompt =st.chat_input(
    "Write a message for your assistant",
    accept_file=True,
    file_type=["txt"],
    )

if prompt:
    for file in prompt.files:
        if file.type.startswith("text/"):
            with st.chat_message("ai"):
                with st.status("Uploading file...") as status:
                    uploaded_file =client.files.create(
                        file=(file.name, file.getvalue()),
                        purpose="user_data",
                    )
                    status.update(label="Attaching file")
                    client.vector_stores.files.create(
                        vector_store_id=VECTOR_STORE_ID,
                        file_id=uploaded_file.id,
                    )
                    status.update(label="File uploaded", state="complete")
                

    if prompt.text:
        with st.chat_message("human"):
            st.write(prompt.text)
        asyncio.run(run_agent(prompt.text))
    
    

with st.sidebar:
    reset = st.button("Reset Memory")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))
