import vertexai 
import vertexai.agent_engines
from vertexai import agent_engines

PROJECT_ID = "gen-lang-client-487219"
LOCATION = "europe-west4"

vertexai.init(
    project=PROJECT_ID, 
    location=LOCATION,
)

#deployments = agent_engines.list()

#for deployment in deployments:
#    print(deployment)

DEPLOYMENT_ID= "projects/934974662898/locations/europe-west4/reasoningEngines/8529131598983987200"
SESSION_ID = "8832876633959432192"
remote_app = agent_engines.get(DEPLOYMENT_ID)
remote_app.delete(force=True)

#remote_session = remote_app.create_session(user_id="u_123")
#print(remote_session["id"])

for event in remote_app.stream_query(
    user_id="u_123",
    session_id=SESSION_ID,
    message="I want to go to Tokyo, any tips?"
):
    print(event, "\n", "=" * 50)
   
