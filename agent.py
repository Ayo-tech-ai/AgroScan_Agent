"""
agent.py

Creates the AgroScan AI Agent,
Session Service and Runner.
"""

from datetime import date

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from config import MODEL_NAME
from tools import (
    farm_record_tool,
    farm_record_lookup_tool,
    most_recent_record_tool,
    farm_summary_tool,
)
from skills import (
    farm_manager_core_skill,
    farm_record_skill,
    agroscan_toolset,
)


def create_agent():
    """
    Create a new AgroScan AI agent.
    """

    today_str = date.today().isoformat()

    return Agent(

        model=LiteLlm(
            model=MODEL_NAME,
        ),

        name="farm_manager",

        description=(
            "An intelligent poultry farm management system "
            "that assists farmers using specialized capabilities."
        ),

        instruction=f"""
```

At this point,

**copy the Agent instruction exactly from your notebook**, beginning with

```text
You are AgroScan AI Farm Manager.
```

and ending with

```text
Maintain a friendly, professional and practical tone.
```

Then continue with:

```python
""",

        tools=[
            farm_record_tool,
            farm_record_lookup_tool,
            most_recent_record_tool,
            farm_summary_tool,
            agroscan_toolset,
        ],

    )


def create_session_service():
    """
    Create a new ADK Session Service.
    """

    return InMemorySessionService()


def create_runner(session_service):
    """
    Create the ADK Runner.
    """

    return Runner(
        app_name="agroscan_app",
        agent=create_agent(),
        session_service=session_service,
    )
