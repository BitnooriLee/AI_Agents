import dotenv
import asyncio
dotenv.load_dotenv()

from openai import OpenAI
import streamlit as st
from agents import (
    Agent, 
    Runner, 
    SQLiteSession, 
    WebSearchTool, 
    FileSearchTool, 
    ImageGenerationTool,
    CodeInterpreterTool,
)
import base64

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
            - Code Interpreter Tool: Use this tool when you need to write and run code to answer the user's question. 
        """,
        tools=[
            WebSearchTool(),
            FileSearchTool(
                vector_store_ids=[VECTOR_STORE_ID],
                max_num_results=3,
            ),
            ImageGenerationTool(
                tool_config={
                    "type": "image_generation",
                    "quality": "low:",
                    "output_format": "jpeg",
                    "moderate":"low",
                    "partial_images": 1,
                }
            ),
            CodeInterpreterTool(
                tool_config={
                    "type": "code_interpreter",
                    "container": {
                        "type": "auto",
                    }
                }
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
                    content = message["content"]
                    if isinstance(content, str):
                        st.write(content.replace("$","\$"))
                    elif isinstance(content, list):
                        for part in content:
                            if "image_url" in part:
                                st.image(part["image_url"])
                else: 
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"].replace("$","\$"))
        if "type" in message:
            message_type = message["type"]
            if message_type == "web_search_call": 
                with st.chat_message("ai"):
                    st.write("Searched the web...") 
            elif message_type == "file_search_call":
                with st.chat_message("ai"):
                    st.write("Searched the files...") 
            elif message_type == "image_generation_call":
                image = base64.b64decode(message["result"])
                with st.chat_message("ai"):
                    st.image(image) 

def update_status(status_container, event):
    status_messages = {
        'response.web_search_call.completed' : (" Web Search completed", "complete"),
        'response.web_search_call.in_progress': (" Web Search in progress...", "running"),
        'response.web_search_call.searching': (" Starting web search...", "running"),
        'response.file_search_call.completed' : (" File Search completed", "complete"),
        'response.file_search_call.in_progress': (" File Search in progress...", "running"),
        'response.file_search_call.searching': (" Starting file search...", "running"),
        'response.image_generation_call.in_progress': (" Image Generation in progress...", "running"),
        'response.image_generation_call.generating': (" Starting image generation...", "running"),
        'response.code_interpreter_call.done': (" Ran code.", "complete"),
        'response.code_interpreter_call.completed': (" Ran code.", "complete"),
        'response.code_interpreter_call.in_progress' : (" Running code...", "running"),
        'response.code_interpreter_call.interpreting': (" Interpreting code...", "running"),
        'response.completes': ("", "complete"),
  
    }

    if event in status_messages:
        label, state = status_messages[event]
        status_container.update(label=label, state=state)

asyncio.run(paint_history())

async def run_agent(message):
    with st.chat_message("ai"):
        status_container = st.status("", expanded=False)
        text_placeholder = st.empty()
        code_placeholder = st.empty()
        image_placeholder = st.empty()
        response = ""
        code_response = ""
        
        st.session_state["code_placeholder"] = code_placeholder
        st.session_state["image_placeholder"] = image_placeholder
        st.session_state["text_placeholder"] = text_placeholder
      
        
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

                if event.data.type == "response.code_interpreter_call.delta":
                    code_response += event.data.delta
                    code_placeholder.write(code_response.replace("$","\$"))

                elif event.data.type == "response.image_generation_call.partial_image":
                    image = base64.b64decode(event.data.partial_image_b64)
                    image_placeholder.image(image)


prompt =st.chat_input(
    "Write a message for your assistant",
    accept_file=True,
    file_type=["txt", "jpg", "jpeg", "png"],
    )

if prompt:
    if "code_placeholder" in st.session_state:
        st.session_state["code_placeholder"].empty()
    if "image_placeholder" in st.session_state:
        st.session_state["image_placeholder"].empty()
    if "text_placeholder" in st.session_state:
        st.session_state["text_placeholder"].empty()
      
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
                
        elif file.type.startswith("image/"):
            with st.status("Uploading image...") as status:
                file_bytes = file.getvalue()
                base64_data = base64.b64encode(file_bytes).decode("utf-8")
                data_uri = f"data:{file.type};base64,{base64_data}"
                status.update(label="Uploading image...")
                asyncio.run(
                    session.add_items(
                        [
                            {
                                "role":"user", 
                                "content": [
                                    {
                                        "type":"input_image", 
                                        "detail":"auto", 
                                        "image_url": data_uri,
                                    }
                                ],
                            }
                        ]
                    )
                )
                status.update(label="Image uploaded", state="complete")
            with st.chat_message("human"):
                st.image(data_uri)
            

    if prompt.text:
        with st.chat_message("human"):
            st.write(prompt.text)
        asyncio.run(run_agent(prompt.text))
    
    

with st.sidebar:
    reset = st.button("Reset Memory")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))
