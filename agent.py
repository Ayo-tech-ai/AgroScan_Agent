# agent.py
import os
import uuid
from datetime import date

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool
from google.adk.tools.skill_toolset import SkillToolset
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from config import MODEL_NAME, APP_TITLE, APP_ICON
from tools import (
    record_daily_farm_data,
    get_farm_record,
    get_most_recent_farm_record,
    get_farm_summary
)
from skills import create_farm_manager_core_skill, create_farm_record_skill


def create_agroscan_agent(api_key: str) -> tuple[Agent, Runner, InMemorySessionService, str]:
    """
    Create and configure the AgroScan AI Farm Manager agent.
    
    Returns:
        tuple: (agent, runner, session_service, user_id)
    """
    # Set API key
    os.environ["GROQ_API_KEY"] = api_key

    # Create skills
    core_skill = create_farm_manager_core_skill()
    record_skill = create_farm_record_skill()

    # Create tools
    farm_record_tool = FunctionTool(record_daily_farm_data)
    farm_record_lookup_tool = FunctionTool(get_farm_record)
    most_recent_record_tool = FunctionTool(get_most_recent_farm_record)
    farm_summary_tool = FunctionTool(get_farm_summary)

    # Create toolset
    agroscan_toolset = SkillToolset(
        skills=[core_skill, record_skill],
        additional_tools=[]
    )

    today_str = date.today().isoformat()

    # Create agent
    agent = Agent(
        model=LiteLlm(model=MODEL_NAME),
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

• Never expose internal implementation details.

• Never mention Skills.

• Never mention Tool calls.

• Never mention FunctionTools.

• Never invent farm records.

• Never invent production figures.

• Never invent revenue.

• Treat the Farm Record Book as the single source of truth.

• To record or update daily farm data, call the
record_daily_farm_data tool directly. This tool is
always available.

• To look up a specific date's record, call get_farm_record
directly with an exact date. This tool is always available.

• To find the most recent record on file (when the farmer doesn't
name a specific date), call get_most_recent_farm_record directly.
This tool is always available.

• To summarize performance over a period (totals, profit/loss),
call get_farm_summary directly with an exact start and end date.
This tool is always available.

• All monetary values must be reported using the ₦ (Naira) symbol,
never $ or any other currency symbol.

• Load the farm-record-management skill to guide how you
interpret and communicate about farm records, lookups, and
summaries.

• Load the farm-manager-core skill to guide your identity,
tone, and communication style.

• Never simulate tool execution.

• Wait for tool results before responding.

• If required information is missing,
ask only for the missing information.

Maintain a friendly, professional and practical tone.
""",
        tools=[
            farm_record_tool,
            farm_record_lookup_tool,
            most_recent_record_tool,
            farm_summary_tool,
            agroscan_toolset,
        ]
    )

    # Create session service and session
    session_service = InMemorySessionService()
    unique_user_id = str(uuid.uuid4())
    
    agroscan_session = session_service.create_session_sync(
        app_name="agroscan_app",
        user_id=unique_user_id
    )

    # Create runner
    runner = Runner(
        app_name="agroscan_app",
        agent=agent,
        session_service=session_service
    )

    return agent, runner, session_service, unique_user_id, agroscan_session
