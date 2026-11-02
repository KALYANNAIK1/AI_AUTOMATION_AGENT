from .ai_agent import AIAgent
import json


class ScenarioAgent:

    def __init__(self):

        self.ai = AIAgent()

    def generate_scenarios(
        self,
        requirement
    ):

        prompt = f"""
Generate comprehensive test scenarios.

Requirement:

{requirement}

Generate:

1. Positive Scenarios
2. Negative Scenarios
3. Validation Scenarios
4. Boundary Scenarios
5. Security Scenarios
6. Usability Scenarios

For each scenario provide:

- scenario_id
- scenario_name
- type
- priority

IMPORTANT:

Return VALID JSON ARRAY ONLY.

Output must start with:

[

Output must end with:

]

Do NOT return markdown.

Do NOT return explanation.

Do NOT return notes.

Do NOT return comments.

Do NOT return text before JSON.

Do NOT return text after JSON.

Example:

[
    {{
        "scenario_id": "TS_LOGIN_001",
        "scenario_name": "Verify successful login",
        "type": "Positive",
        "priority": "High"
    }},
    {{
        "scenario_id": "TS_LOGIN_002",
        "scenario_name": "Verify invalid login",
        "type": "Negative",
        "priority": "High"
    }}
]
"""

        response = self.ai.ask_ai(
            prompt
        )

        response = (
            response
            .replace(
                "```json",
                ""
            )
            .replace(
                "```",
                ""
            )
            .strip()
        )

        try:

            if not response.startswith("["):

                raise ValueError(
                    "Scenario response is not JSON array"
                )

            scenarios = json.loads(
                response
            )

            if not isinstance(
                scenarios,
                list
            ):
                raise ValueError(
                    "Scenario response is not list"
                )

            return scenarios

        except Exception:

            print(
                "\nInvalid Scenario JSON Returned By AI\n"
            )

            print(response)

            return [

                {
                    "scenario_id":
                    "TS_FALLBACK_001",

                    "scenario_name":
                    "Verify application functionality",

                    "type":
                    "Positive",

                    "priority":
                    "High"
                },

                {
                    "scenario_id":
                    "TS_FALLBACK_002",

                    "scenario_name":
                    "Verify invalid data handling",

                    "type":
                    "Negative",

                    "priority":
                    "High"
                }

            ]