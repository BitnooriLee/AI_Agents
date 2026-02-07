from google.adk.agents import Agent
from .prompt import IMAGE_BUILDER_DESCRIPTION, IMAGE_BUILDER_PROMPT
from google.adk.models.lite_llm import LiteLlm
from .tool import generate_images

MODEL = LiteLlm(model="openai/gpt-4o")
image_builder_agent = Agent(
    name="ImageBuilder",
    description=IMAGE_BUILDER_DESCRIPTION,
    instruction=IMAGE_BUILDER_PROMPT,
    model=MODEL,
    output_key="image_builder_output",
    tools=[
        generate_images
        ],
)
