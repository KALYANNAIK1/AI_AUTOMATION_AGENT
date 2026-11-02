from .ai_agent import AIAgent
import json


class TestCaseAgent:

    def __init__(self):
        self.ai = AIAgent()

    def generate_testcases(self, scenarios):

        prompt = f"""
Generate ONLY 2 test cases in JSON array format.

Scenarios:

{scenarios}

Generate exactly these test cases:

1. Positive Scenario
   - Successful execution
   - Expected result should be displayed

2. Negative Scenario
   - Invalid input or failure condition
   - Appropriate error message should be displayed

Do NOT generate more than 2 test cases.

Do NOT generate:
- Additional positive scenarios
- Additional negative scenarios
- Boundary test cases
- Edge cases
- Security test cases
- Performance test cases
- Usability test cases

Each test case must contain:

- tc_id
- scenario_id
- summary
- priority
- type
- precondition
- steps
- actual_result
- expected_result

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
        "tc_id": "TC_POS_001",
        "scenario_id": "TS_POS_001",
        "summary": "Verify successful execution",
        "priority": "High",
        "type": "Positive",
        "precondition": "Application is available",
        "steps": [
            "Launch application",
            "Perform valid action"
        ],
        "actual_result": [
            "Operation completed successfully"
        ],
        "expected_result": [
            "Operation should complete successfully"
        ]
    }},
    {{
        "tc_id": "TC_NEG_001",
        "scenario_id": "TS_NEG_001",
        "summary": "Verify invalid execution",
        "priority": "High",
        "type": "Negative",
        "precondition": "Application is available",
        "steps": [
            "Launch application",
            "Perform invalid action"
        ],
        "actual_result": [
            "Error message displayed"
        ],
        "expected_result": [
            "Proper error message should be displayed"
        ]
    }}
]
"""

        try:
            response = self.ai.ask_ai(prompt)
        except Exception as exc:
            print(f"AI test case generation unavailable: {exc}. Using deterministic fallback.")
            return [
                {"tc_id":"TC_POS_001","scenario_id":"TS_POS_001","summary":"Verify successful execution","priority":"High","type":"Positive","steps":["Launch the application","Perform the valid action","Submit the form"],"expected_result":["The expected successful result is displayed"]},
                {"tc_id":"TC_NEG_001","scenario_id":"TS_NEG_001","summary":"Verify invalid execution","priority":"High","type":"Negative","steps":["Launch the application","Perform an invalid action","Submit the form"],"expected_result":["A validation error is displayed"]}
            ]

        response = (
            response
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        try:

            if not response.startswith("["):
                raise ValueError(
                    "Test case response is not JSON array"
                )

            testcases = json.loads(response)

            if not isinstance(testcases, list):
                raise ValueError(
                    "Test cases response is not list"
                )

            # Keep only first 2 test cases
            testcases = testcases[:2]

            return testcases

        except Exception:

            print("\nInvalid Test Case JSON Returned By AI\n")
            print(response)

            return [
                {
                    "tc_id": "TC_POS_001",
                    "scenario_id": "TS_POS_001",
                    "summary": "Verify successful execution",
                    "priority": "High",
                    "type": "Positive",
                    "precondition": "Application is available",
                    "steps": [
                        "Launch application",
                        "Perform valid action"
                    ],
                    "actual_result": [
                        "Operation completed successfully"
                    ],
                    "expected_result": [
                        "Operation should complete successfully"
                    ]
                },
                {
                    "tc_id": "TC_NEG_001",
                    "scenario_id": "TS_NEG_001",
                    "summary": "Verify invalid execution",
                    "priority": "High",
                    "type": "Negative",
                    "precondition": "Application is available",
                    "steps": [
                        "Launch application",
                        "Perform invalid action"
                    ],
                    "actual_result": [
                        "Error message displayed"
                    ],
                    "expected_result": [
                        "Proper error message should be displayed"
                    ]
                }
            ]