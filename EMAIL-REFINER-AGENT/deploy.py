import dotenv
dotenv.load_dotenv()

import os
import vertexai 
from travel_advisor_agent.agent import travel_advisor_agent
import vertexai.agent_engines
from vertexai.preview import reasoning_engines

PROJECT_ID = "gen-lang-client-487219"
LOCATION = "europe-west4"
BUCKET_NAME = "gs://bitnoori-weather_agent"

vertexai.init(
    project=PROJECT_ID, 
    location=LOCATION,
    staging_bucket=BUCKET_NAME,
)

app = reasoning_engines.AdkApp(
    agent=travel_advisor_agent,
    enable_tracing=True,
)

remote_app = vertexai.agent_engines.create(
    display_name="Travel Advisor Agent",
    agent_engine=app,
    requirements=[
        "google-cloud-aiplatform[adk,agent-engines]",
        "litellm",
    ],
    extra_packages=[
        "travel_advisor_agent"
    ],
    env_vars={
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    }
)