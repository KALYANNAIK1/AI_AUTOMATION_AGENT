from .ai_agent import AIAgent
import json
import re


class RequirementAgent:

    def __init__(self):

        self.ai = AIAgent()

    def extract_url(
        self,
        requirement
    ):

        match = re.search(
            r'https?://[^\s"<>\']+',
            requirement
        )

        if match:
            return match.group(0)

        return None

    def analyze_requirement(
        self,
        requirement
    ):

        prompt = f"""
Analyze the following requirement.

Requirement:

{requirement}

Provide structured analysis.

Identify:

1. Feature Name
2. Module
3. Actors
4. Business Flow
5. Functional Requirements
6. Business Rules
7. Risks
8. Validation Rules
9. Acceptance Criteria
10. Testable Areas

IMPORTANT:

Return VALID JSON ONLY.

Do not return markdown.

Do not return explanation.

Do not return notes.

Do not return code block.

Do not return text before JSON.

Do not return text after JSON.

Expected format:

{{
    "feature_name": "",
    "module": "",
    "actors": [],
    "business_flow": [],
    "functional_requirements": [],
    "business_rules": [],
    "risks": [],
    "validation_rules": [],
    "acceptance_criteria": [],
    "testable_areas": []
}}
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

            data = json.loads(
                response
            )

            return data

        except Exception:

            print(
                "\nInvalid JSON returned by AI\n"
            )

            print(response)

            # fallback response

            return {

                "feature_name":
                "UnknownFeature",

                "module":
                "UnknownModule",

                "actors":
                [],

                "business_flow":
                [],

                "functional_requirements":
                [],

                "business_rules":
                [],

                "risks":
                [],

                "validation_rules":
                [],

                "acceptance_criteria":
                [],

                "testable_areas":
                []

            }