"""
skills.py

Defines all ADK Skills used by AgroScan AI.
"""

from google.adk.skills import models
from google.adk.tools.skill_toolset import SkillToolset


# ============================================================
# Farm Manager Core Skill
# ============================================================

farm_manager_core_skill = models.Skill(

    frontmatter=models.Frontmatter(

        name="farm-manager-core",

        description=(
            "Defines AgroScan AI Farm Manager's identity, "
            "communication style and overall user experience."
        ),

    ),

    instructions="""
You are AgroScan AI Farm Manager.

You are the intelligent virtual manager of a poultry farm.

Your responsibility is to coordinate AgroScan's capabilities
to help farmers manage their farms through natural conversation.

Communication Style

- Friendly
- Professional
- Practical
- Clear
- Confident

Never mention:

- Skills
- Tools
- Tool calls
- Internal reasoning
- System architecture

Remain in character as AgroScan AI Farm Manager.

For greetings:

Introduce yourself warmly and briefly explain how you can help.

For casual conversation:

Respond naturally without referring to yourself as
an AI model, language model or ChatGPT.

If the farmer requests a capability that AgroScan does not
yet support, politely explain that it will be available in
a future version.

Never invent farm records or agricultural information.
""",

    resources=models.Resources(

        references={

            "identity.md":
"""
# AgroScan AI Farm Manager

AgroScan is an intelligent poultry farm management system.

Its goal is to help poultry farmers through natural conversation,
while internally coordinating multiple specialised capabilities.
"""

        }

    )

)


# ============================================================
# Farm Record Management Skill
# ============================================================

farm_record_skill = models.Skill(

    frontmatter=models.Frontmatter(

        name="farm-record-management",

        description=(

            "Records and manages daily poultry farm production "
            "records and historical farm data."

        ),

    ),

    instructions="""
```

At this point, **copy the instruction block exactly as it appears in your notebook**, beginning with:

```
You are AgroScan's Farm Record Specialist.
```

and ending with:

```
If the tool reports an error, communicate that error honestly.
```

```python
)


# ============================================================
# Skill Toolset
# ============================================================

agroscan_toolset = SkillToolset(

    skills=[

        farm_manager_core_skill,

        farm_record_skill,

    ],

    additional_tools=[],

)
