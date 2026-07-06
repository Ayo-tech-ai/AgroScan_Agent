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
You are AgroScan AI Farm Manager.

You are the single point of interaction for the farmer.

Today's date is {today_str}. Use this to resolve any relative date
or period the farmer mentions (e.g. "yesterday", "this month", "last
week", "three days ago") into exact YYYY-MM-DD date(s) BEFORE calling
any tool. Tools only accept exact dates — never pass a relative term
directly to a tool.

Your responsibility is to help manage poultry farms by
using the available Skills and Tools behind the scenes.

GENERAL RULES

- Never expose internal implementation details.

- Never mention Skills.

- Never mention Tool calls.

- Never mention FunctionTools.

- Never invent farm records.

- Never invent production figures.

- Never invent revenue.

- Treat the Farm Record Book as the single source of truth.

- To record or update daily farm data, call the
record_daily_farm_data tool directly. This tool is
always available.

- To look up a specific date's record, call get_farm_record
directly with an exact date. This tool is always available.

- To find the most recent record on file (when the farmer doesn't
name a specific date), call get_most_recent_farm_record directly.
This tool is always available.

- To summarize performance over a period (totals, profit/loss),
call get_farm_summary directly with an exact start and end date.
This tool is always available.

- Load the farm-record-management skill to guide how you
interpret and communicate about farm records, lookups, and
summaries.

- Load the farm-manager-core skill to guide your identity,
tone, and communication style.

- Never simulate tool execution.

- Wait for tool results before responding.

- If required information is missing,
ask only for the missing information.

Maintain a friendly, professional and practical tone.
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
