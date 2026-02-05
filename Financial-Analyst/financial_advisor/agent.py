from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

MODEL = LiteLlm("openai/gpt-4o")

def get_weather(city: str):
    return f"The weather in {city} is 30 degrees."

def conver_units(degrees:int):
    return f"That is 40 fahrenheit"

geo_agent = Agent(
    name="GeoAgent",
    instruction="You help the user with geo related questions",
    model=MODEL,
    description="Transfer to this agent when you have a geo related question",
)
weather_agent = Agent(
    name="WeatherAgent",
    instruction="You help the user with weather related questions",
    model=MODEL,
    tools=[
        get_weather,
        conver_units,
        ],
    sub_agents=[geo_agent],
)

root_agent = weather_agent 