import asyncio
import datetime
import os
import sys
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route

# Ensure the ADK is available
# Note: In a real project you would install these dependencies

try:
    from google.adk.agents import LlmAgent  # type: ignore[import-untyped]
    from google.adk.tools.google_api_tool import CalendarToolset  # type: ignore[import-untyped]
    from google.adk.runners import Runner  
    from google.adk.sessions import InMemorySessionService  
    from google.adk.memory import InMemoryMemoryService  
    from google.adk.artifacts import InMemoryArtifactService  
    
    # Note: A2A-specific imports may require additional dependencies
    # For a simpler demonstration, we'll create a basic web service
except ImportError as e:
    print(f"Error importing Google ADK: {e}")
    print("Please install google-adk[sqlalchemy]")
    sys.exit(1)

async def create_agent(client_id, client_secret) -> LlmAgent:
    """Constructs the ADK agent."""
    # In a real environment, you might fetch credentials.
    # For this demo, we'll assume they might be provided, 
    # but we'll fallback gracefully if not to allow the script to 'run' as a demo.
    
    if client_id and client_secret:
        toolset = CalendarToolset(client_id=client_id, client_secret=client_secret)
        tools = await toolset.get_tools()
        print("Initialized CalendarToolset")
    else:
        print("No credentials provided, using empty toolset for demonstration.")
        tools = []

    return LlmAgent(
        model='gemini-2.0-flash-001',
        name='calendar_agent',
        description="An agent that can help manage a user's calendar",
        instruction=f"""
        You are an agent that can help manage a user's calendar.
        Users will request information about the state of their calendar
        or to make changes to their calendar. Use the provided tools for
        interacting with the calendar API.
        If not specified, assume the calendar the user wants is the 'primary'
        calendar.
        When using the Calendar API tools, use well-formed RFC3339
        timestamps.
        Today is {datetime.datetime.now()}.
        """,
        tools=tools,
    )

async def main_async(host: str, port: int):
    """
    Simplified demonstration of the Calendar Agent.
    Note: Full A2A integration requires additional setup beyond this script.
    """
    # Determine credentials (demo mode support)
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

    # Create the ADK Agent
    adk_agent = await create_agent(client_id, client_secret)
    
    print(f"\n{'='*60}")
    print(f"Calendar Agent Created Successfully!")
    print(f"{'='*60}")
    print(f"Agent Name: {adk_agent.name}")
    print(f"Agent Description: {adk_agent.description}")
    print(f"Model: {adk_agent.model}")
    print(f"Number of tools: {len(adk_agent.tools) if adk_agent.tools else 0}")
    print(f"{'='*60}\n")

    # Setup Runner for basic agent execution
    runner = Runner(
        app_name='Calendar Agent Demo',
        agent=adk_agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )
    
    print("✓ Runner initialized successfully")
    print("✓ Agent is ready to process requests\n")
    
    # Simple demonstration of agent execution
    print("To use this agent in an A2A setup, you would need to:")
    print("1. Configure the A2A executor and request handlers")
    print("2. Set up the Starlette application with A2A routes")
    print("3. Deploy with proper authentication and OAuth callback handling")
    print("\nFor now, this script confirms the agent can be created and configured.")
    print(f"\nAgent would be served at: http://{host}:{port}/")
    
    # Note: Full A2A server implementation removed due to missing dependencies
    # in google-adk v1.22.0 standard install
    
    # Simple server to show the endpoint would work
    async def root(request: Request) -> PlainTextResponse:
        return PlainTextResponse(
            f"Calendar Agent is running!\n"
            f"Agent: {adk_agent.name}\n"
            f"Description: {adk_agent.description}\n"
            f"Note: Full A2A protocol requires additional configuration."
        )
    
    routes = [Route('/', endpoint=root, methods=['GET'])]
    app = Starlette(routes=routes)
    
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    print(f"\n🚀 Starting basic web server on http://{host}:{port}/\n")
    await server.serve()


def main():
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"Starting Agent-to-Agent Service on {host}:{port}")
    try:
        asyncio.run(main_async(host, port))
    except KeyboardInterrupt:
        print("Server stopped.")

if __name__ == "__main__":
    main()
