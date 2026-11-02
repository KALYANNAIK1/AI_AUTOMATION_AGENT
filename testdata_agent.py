import html
import json
import re

from .ai_agent import AIAgent


class TestDataAgent:

    def __init__(self):
        self.ai = AIAgent()

    @staticmethod
    def clean_html(text):

        if not isinstance(text, str):
            return text

        text = html.unescape(text)

        # Convert HTML links to plain URLs
        text = re.sub(
            r'<a[^>]*href="([^"]+)"[^>]*>.*?</a>',
            r'\1',
            text,
            flags=re.IGNORECASE | re.DOTALL
        )

        # Convert <br> tags to new lines
        text = re.sub(
            r"<br\s*/?>",
            "\n",
            text,
            flags=re.IGNORECASE
        )

        # Remove remaining HTML tags
        text = re.sub(
            r"<[^>]+>",
            "",
            text
        )

        return text.strip()

    @staticmethod
    def _expand_repeat_expressions(response):

        repeat_pattern = re.compile(
            r'"((?:\\.|[^"\\])*)"\.repeat\((\d+)\)'
        )

        def replace_repeat(match):

            value = json.loads(
                f'"{match.group(1)}"'
            )

            count = int(
                match.group(2)
            )

            if count > 100000:

                raise ValueError(
                    "AI-generated test data contains "
                    "an oversized repeat expression."
                )

            return json.dumps(
                value * count,
                ensure_ascii=False
            )

        return repeat_pattern.sub(
            replace_repeat,
            response
        )

    def generate_test_data(
        self,
        testcases
    ):

        prompt = f"""
Generate test data for the following test cases.

Test Cases:
{json.dumps(testcases, indent=4)}

Rules:

1. Return ONLY valid JSON.
2. Do not return markdown.
3. Do not return explanations.
4. Use double quotes only.
5. Return a JSON array.
6. Ensure proper commas between objects.
7. No trailing commas.
8. Do not use JavaScript expressions.
9. Do not use .repeat().
10. Do not include comments.
11. Do not include # symbols.
12. Must be parsable by json.loads().
13. Return literal values only.

Example:

[
    {{
        "tc_id": "TC_LOGIN_001",
        "valid_data": {{
            "username": "standard_user",
            "password": "secret_sauce"
        }},
        "invalid_data": {{
            "username": "invalid_user",
            "password": "wrong_password"
        }},
        "boundary_data": {{
            "username": "a",
            "password": "12345678"
        }},
        "empty_data": {{
            "username": "",
            "password": ""
        }},
        "special_character_data": {{
            "username": "!@#$%",
            "password": "^&*()"
        }}
    }}
]
"""

        response = self.ai.ask_ai(
            prompt
        )

        # Remove markdown fences
        response = response.replace(
            "```json",
            ""
        )

        response = response.replace(
            "```",
            ""
        )

        response = response.strip()

        # Decode HTML entities
        response = html.unescape(
            response
        )

        # Expand repeat expressions
        response = self._expand_repeat_expressions(
            response
        )

        # Extract JSON array only
        start = response.find("[")

        end = (
            response.rfind("]")
            + 1
        )

        if start != -1 and end > start:

            response = response[
                start:end
            ]

        else:

            raise RuntimeError(
                "AI returned test data "
                "without a JSON array."
            )

        print(
            "\n===== AI GENERATED TEST DATA ====="
        )

        print(response)

        try:

            test_data = json.loads(
                response
            )

        except json.JSONDecodeError as exc:

            print(
                "\n===== INVALID TEST DATA JSON ====="
            )

            print(response)

            raise RuntimeError(
                "AI returned invalid JSON at "
                f"line {exc.lineno}, "
                f"column {exc.colno}: "
                f"{exc.msg}"
            ) from exc

        if not isinstance(
            test_data,
            list
        ):

            raise RuntimeError(
                "AI test-data response "
                "must be a JSON array."
            )

        for item in test_data:

            if not isinstance(
                item,
                dict
            ):
                continue

            for key, value in item.items():

                if isinstance(
                    value,
                    dict
                ):

                    for sub_key, sub_value in value.items():

                        if isinstance(
                            sub_value,
                            str
                        ):

                            value[sub_key] = (
                                self.clean_html(
                                    sub_value
                                )
                            )

                elif isinstance(
                    value,
                    str
                ):

                    item[key] = (
                        self.clean_html(
                            value
                        )
                    )

        return test_data

    def save_test_data(
        self,
        test_data,
        output_file
    ):

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                test_data,
                file,
                indent=4,
                ensure_ascii=False
            )

        return output_file