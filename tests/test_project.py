import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from Agent_AUTOMATION_AI import Test_AI as app
from Agent_AUTOMATION_AI.AI_Failure_Analysis import FailureAgent
from Agent_AUTOMATION_AI.ai_agent import AIAgent, GeminiQuotaError
from Agent_AUTOMATION_AI.Excel_Agent import ExcelAgent
from Agent_AUTOMATION_AI.execution_agent import ExecutionAgent
from Agent_AUTOMATION_AI.locator_agent import LocatorAgent
from Agent_AUTOMATION_AI.pageobject_agent import PageObjectAgent
from Agent_AUTOMATION_AI.playwright_agent import PlaywrightAgent
from Agent_AUTOMATION_AI.testdata_agent import TestDataAgent


class StubAgent:
    def analyze_requirement(self, requirement):
        return {"feature_name": "Login"}

    def generate_scenarios(self, requirement):
        return [{"scenario_id": "TS_LOGIN_001", "name": "Login"}]

    def generate_testcases(self, scenarios):
        return [{"tc_id": "TC_LOGIN_001", "scenario_id": "TS_LOGIN_001"}]

    def generate_file_name(self, feature_name):
        return "LoginPage.js"

    def generate_page_object(self, requirement, locators=None):
        return "class PageObject {}\nmodule.exports = PageObject;"

    def save_page_object(self, page_object, page_name):
        output_path = app.GENERATED_DIR / "pages" / page_name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(page_object, encoding="utf-8")
        return output_path

    def generate_playwright_script(
        self,
        requirement=None,
        testcases=None,
        runtime_data=None,
        locators=None,
        page_object_content="",
        page_name="",
    ):
        return "```javascript\ntest('login', async () => {});\n```"

    def save_script(self, script_content, feature_name="Automation"):
        output_path = app.GENERATED_DIR / "tests" / "Login.spec.js"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(script_content, encoding="utf-8")
        return output_path


class StubLocatorAgent:
    def extract_locators(self, **kwargs):
        return {}

    def save_locators(self, locators, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(locators), encoding="utf-8")
        return path


class StubRTMAgent:
    def generate_rtm(self, requirements, scenarios, testcases):
        return [{"requirement_id": "REQ-001"}]


class StubTestDataAgent:
    def generate_test_data(self, testcases):
        return [{"tc_id": "TC_LOGIN_001"}]


class StubExcelAgent:
    def save_requirements(self, requirement):
        return "Requirements.xlsx"

    def save_scenarios(self, scenarios):
        return "Scenarios.xlsx"

    def save_testcases(self, testcases):
        return "TestCases.xlsx"


class ProjectTests(unittest.TestCase):
    def test_code_fence_is_removed(self):
        self.assertEqual(
            app.strip_code_fence("```javascript\nconst x = 1;\n```"),
            "const x = 1;",
        )

    def test_cli_generates_all_artifacts_without_running_browser_tests(self):
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory) / "generated"
            requirement_path = Path(directory) / "requirement.txt"
            requirement_path.write_text(
                "URL: https://example.com\nUsername: user@example.com\n"
                "Password: test-password\n",
                encoding="utf-8",
            )
            with (
                patch.object(app, "GENERATED_DIR", output_dir),
                patch.object(app, "RequirementAgent", StubAgent),
                patch.object(app, "ScenarioAgent", StubAgent),
                patch.object(app, "TestCaseAgent", StubAgent),
                patch.object(app, "PageObjectAgent", StubAgent),
                patch.object(app, "PlaywrightAgent", StubAgent),
                patch.object(app, "TestDataAgent", StubTestDataAgent),
                patch.object(app, "ExcelAgent", StubExcelAgent),
                patch.object(app, "LocatorAgent", StubLocatorAgent),
                patch.object(app, "RTMAgent", StubRTMAgent),
                patch.object(app, "ExecutionAgent") as execution_agent,
                patch.object(app, "FailureAgent"),
                patch.object(app, "ReportAgent"),
                patch.object(app, "JiraAgent"),
                patch.object(app, "NotificationAgent"),
                patch.object(app, "DashboardAgent"),
            ):
                self.assertEqual(
                    app.main(["--requirement", str(requirement_path)]),
                    0,
                )

            execution_agent.return_value.execute_tests.assert_not_called()
            self.assertEqual(
                json.loads(
                    (output_dir / "analysis" / "requirement_analysis.json").read_text(
                        encoding="utf-8"
                    )
                ),
                {"feature_name": "Login"},
            )
            self.assertEqual(
                json.loads(
                    (output_dir / "scenarios" / "scenarios.json").read_text(
                        encoding="utf-8"
                    )
                ),
                [{"scenario_id": "TS_LOGIN_001", "name": "Login"}],
            )
            self.assertEqual(
                (output_dir / "pages" / "LoginPage.js").read_text(
                    encoding="utf-8"
                ),
                "class PageObject {}\nmodule.exports = PageObject;",
            )
            self.assertEqual(
                (output_dir / "tests" / "Login.spec.js").read_text(
                    encoding="utf-8"
                ),
                "test('login', async () => {});",
            )

    def test_excel_exports_are_created_in_project_generated_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            agent = ExcelAgent()
            agent.output_dir = Path(directory)

            paths = [
                agent.save_requirements("Login requirement"),
                agent.save_scenarios("Generated scenarios"),
                agent.save_testcases("Generated test cases"),
            ]

            self.assertEqual(
                [Path(path).name for path in paths],
                ["Requirements.xlsx", "Scenarios.xlsx", "TestCases.xlsx"],
            )
            self.assertTrue(all(Path(path).is_file() for path in paths))

    def test_opt_in_playwright_execution_receives_generated_spec(self):
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory) / "generated"
            requirement_path = Path(directory) / "requirement.txt"
            requirement_path.write_text(
                "URL: https://example.com\nUsername: user@example.com\n"
                "Password: test-password\n",
                encoding="utf-8",
            )
            execution_agent = Mock()
            execution_agent.execute_tests.return_value = {
                "status": "SUCCESS",
                "returncode": 0,
                "stdout": "1 passed",
                "stderr": "",
            }
            report_agent = Mock()
            report_agent.generate_report.return_value = {
                "status": "SUCCESS",
                "returncode": 0,
                "output": "1 passed",
                "error": "",
            }
            with (
                patch.object(app, "GENERATED_DIR", output_dir),
                patch.object(app, "RequirementAgent", StubAgent),
                patch.object(app, "ScenarioAgent", StubAgent),
                patch.object(app, "TestCaseAgent", StubAgent),
                patch.object(app, "PageObjectAgent", StubAgent),
                patch.object(app, "PlaywrightAgent", StubAgent),
                patch.object(app, "TestDataAgent", StubTestDataAgent),
                patch.object(app, "ExcelAgent", StubExcelAgent),
                patch.object(app, "LocatorAgent", StubLocatorAgent),
                patch.object(app, "RTMAgent", StubRTMAgent),
                patch.object(
                    app,
                    "ExecutionAgent",
                    return_value=execution_agent,
                ),
                patch.object(app, "ReportAgent", return_value=report_agent),
                patch.object(app, "NotificationAgent"),
                patch.object(app, "FailureAgent"),
                patch.object(app, "JiraAgent"),
                patch.object(app, "DashboardAgent"),
            ):
                report_agent.generate_html_report.return_value = "<html></html>"
                self.assertEqual(
                    app.main(
                        [
                            "--requirement",
                            str(requirement_path),
                            "--run-tests",
                        ]
                    ),
                    0,
                )

            execution_agent.execute_tests.assert_called_once_with(
                output_dir / "tests" / "Login.spec.js",
                "Login",
                attempt_number=1,
                max_failures=1,
            )
            self.assertTrue(
                (output_dir / "reports" / "execution_report.json").is_file()
            )


class AIAgentTests(unittest.TestCase):
    def setUp(self):
        self.agent = object.__new__(AIAgent)
        self.agent.model = "test-model"
        self.agent.timeout = 5
        self.agent.ca_bundle = "test-ca.pem"
        self.agent.session = Mock()

    @staticmethod
    def response(body, ok=True, status_code=200):
        response = Mock()
        response.ok = ok
        response.status_code = status_code
        response.text = ""
        response.json.return_value = body
        return response

    def test_ask_ai_polls_and_returns_model_output_only(self):
        self.agent.session.post.return_value = self.response({
            "id": "interaction-1",
            "status": "in_progress",
        })
        self.agent.session.get.return_value = self.response({
            "id": "interaction-1",
            "status": "completed",
            "steps": [
                {
                    "type": "user_input",
                    "content": [{"type": "text", "text": "input"}],
                },
                {
                    "type": "model_output",
                    "content": [{"type": "text", "text": "answer"}],
                },
            ],
        })

        with patch("Agent_AUTOMATION_AI.ai_agent.time.sleep"):
            self.assertEqual(self.agent.ask_ai("prompt"), "answer")

        self.assertTrue(
            self.agent.session.post.call_args.kwargs["json"]["background"]
        )
        self.assertIn(
            "interaction-1",
            self.agent.session.get.call_args.args[0],
        )

    def test_ask_ai_reports_failed_interaction(self):
        self.agent.session.post.return_value = self.response({
            "id": "interaction-2",
            "status": "failed",
            "errors": [
                {
                    "code": "RESOURCE_EXHAUSTED",
                    "message": "There was a problem processing your request.",
                }
            ],
        })

        with self.assertRaisesRegex(
            GeminiQuotaError,
            "RESOURCE_EXHAUSTED.*Google AI Studio project",
        ):
            self.agent.ask_ai("prompt")

    def test_ask_ai_retries_transient_internal_interaction_failure(self):
        self.agent.session.post.side_effect = [
            self.response({
                "id": "interaction-3",
                "status": "failed",
                "errors": [
                    {
                        "code": "INTERNAL",
                        "message": (
                            "There was a problem processing your request."
                        ),
                    }
                ],
            }),
            self.response({
                "id": "interaction-4",
                "status": "completed",
                "output_text": "answer",
            }),
        ]

        with patch("Agent_AUTOMATION_AI.ai_agent.time.sleep") as sleep:
            self.assertEqual(self.agent.ask_ai("prompt"), "answer")

        self.assertEqual(self.agent.session.post.call_count, 2)
        self.assertEqual(
            self.agent.session.post.call_args_list[0].kwargs["json"]["input"],
            "prompt",
        )
        self.assertEqual(
            self.agent.session.post.call_args_list[1].kwargs["json"]["input"],
            "prompt",
        )
        sleep.assert_called_once_with(1)

    def test_ask_ai_reports_quota_guidance_for_immediate_api_error(self):
        self.agent.session.post.return_value = self.response(
            {
                "error": {
                    "code": 429,
                    "status": "RESOURCE_EXHAUSTED",
                    "message": "Quota exceeded",
                }
            },
            ok=False,
            status_code=429,
        )

        with self.assertRaisesRegex(
            GeminiQuotaError,
            "RESOURCE_EXHAUSTED.*quota and rate limits",
        ):
            self.agent.ask_ai("prompt")

    def test_ask_ai_rejects_empty_prompt(self):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            self.agent.ask_ai("   ")


class FailureAgentTests(unittest.TestCase):
    def test_missing_locator_parser_preserves_slash_in_heading_text(self):
        agent = object.__new__(FailureAgent)

        details = agent._extract_error_details(
            "Error: Unknown page locator: Add/Remove Elements\n"
            "    at PageObject.isVisible (Page.js:42:15)"
        )

        self.assertEqual(
            details["missing_locator"],
            "Add/Remove Elements",
        )
        self.assertEqual(
            agent._parse_missing_locators(details["missing_locator"]),
            ["AddRemoveElements"],
        )

    def test_missing_locator_parser_ignores_template_line_in_error_frame(self):
        agent = object.__new__(FailureAgent)

        details = agent._extract_error_details(
            "Error: Unknown page locator: myntraLogo\n"
            "    at PageObject.isVisible (Page.js:453:19)\n"
            "    `Unknown page locator: ${locatorName}`"
        )

        self.assertEqual(details["missing_locator"], "myntraLogo")
        self.assertEqual(
            agent._parse_missing_locators(details["missing_locator"]),
            ["myntraLogo"],
        )

    def test_analysis_and_auto_fix_accept_only_actual_runtime_locator(self):
        agent = object.__new__(FailureAgent)
        agent.ai = Mock()
        agent.ai.ask_ai.return_value = json.dumps(
            {
                "suggested_code": (
                    'this.myntraLogo = '
                    'page.getByAltText("Myntra");'
                ),
                "auto_fix_possible": "YES",
            }
        )
        error_log = (
            "Error: Unknown page locator: myntraLogo\n"
            "    at PageObject.isVisible (Page.js:453:19)\n"
            "    `Unknown page locator: ${locatorName}`"
        )

        with tempfile.TemporaryDirectory() as directory:
            page_object_path = Path(directory) / "Page.js"
            page_object_path.write_text(
                "class PageObject { constructor(page) {} }\n",
                encoding="utf-8",
            )
            with patch.object(
                agent,
                "_resolve_pom_path",
                return_value=page_object_path,
            ):
                analysis = agent.analyze_failure(error_log)

                self.assertEqual(
                    analysis["missing_locator"],
                    "myntraLogo",
                )
                self.assertEqual(analysis["auto_fix_possible"], "YES")
                analysis["discovery_result"] = {
                    "success": True,
                    "matched_locator": "myntraLogo",
                    "locator_expression": 'page.getByAltText("Myntra")',
                }
                self.assertTrue(agent.auto_fix_pom(analysis))

            updated_page_object = page_object_path.read_text(
                encoding="utf-8"
            )

        self.assertIn(
            'this.myntraLogo = page.getByAltText("Myntra");',
            updated_page_object,
        )
        self.assertIn(
            '"missing_locator": "myntraLogo"',
            agent.ai.ask_ai.call_args.args[0],
        )


class TestDataAgentTests(unittest.TestCase):
    def test_generate_test_data_expands_javascript_repeat_expression(self):
        agent = object.__new__(TestDataAgent)
        agent.ai = Mock()
        agent.ai.ask_ai.return_value = (
            '[{"tc_id":"TC_001","boundary_data":'
            '{"candidate_name":"A".repeat(256)}}]'
        )

        test_data = agent.generate_test_data([])

        self.assertEqual(len(test_data[0]["boundary_data"]["candidate_name"]), 256)
        self.assertEqual(test_data[0]["boundary_data"]["candidate_name"], "A" * 256)

    def test_generate_test_data_raises_on_other_invalid_json(self):
        agent = object.__new__(TestDataAgent)
        agent.ai = Mock()
        agent.ai.ask_ai.return_value = '[{"tc_id": "TC_001",}]'

        with self.assertRaisesRegex(RuntimeError, "AI returned invalid JSON"):
            agent.generate_test_data([])


class PlaywrightAgentTests(unittest.TestCase):
    def test_generated_script_normalizes_import_and_runtime_values(self):
        agent = object.__new__(PlaywrightAgent)
        agent.ai = Mock()
        agent.ai.ask_ai.return_value = (
            "const { test, expect } = require('@playwright/test');\n"
            "const RecruitmentPage = require('../pages/OldPage.js');\n"
            "await page.goto(process.env.URL);\n"
            "const username = process.env.USERNAME;\n"
            "const password = process.env.PASSWORD;"
        )

        script = agent.generate_playwright_script(
            requirement="OrangeHRM recruitment",
            testcases=[],
            runtime_data={
                "url": "https://opensource-demo.orangehrmlive.com/",
                "username": "Admin",
                "password": "admin123",
            },
            page_object_content="class PageObject {}",
            page_name="RecruitmentPage.js",
        )

        self.assertIn(
            "const PageObject = require('../pages/RecruitmentPage.js');",
            script,
        )
        self.assertIn(
            'await page.goto("https://opensource-demo.orangehrmlive.com/");',
            script,
        )
        self.assertIn(
            'const username = "Admin";\nconst password = "admin123";',
            script,
        )


class PageObjectAgentTests(unittest.TestCase):
    def test_generated_page_object_resolves_semantic_dynamic_buttons(self):
        agent = object.__new__(PageObjectAgent)

        page_object = agent.generate_page_object(
            requirement="Add and remove elements",
            locators={},
        )

        self.assertIn(
            "const semanticButtonName = String(",
            page_object,
        )
        self.assertIn(
            "return this.page.getByRole(",
            page_object,
        )


class LocatorAgentTests(unittest.TestCase):
    def test_logo_class_generates_semantic_key_and_locator(self):
        agent = object.__new__(LocatorAgent)
        element = Mock()
        attributes = {
            "data-qa": None,
            "data-testid": None,
            "name": None,
            "id": None,
            "placeholder": None,
            "aria-label": None,
            "value": None,
            "title": None,
            "class": "myntraweb-sprite desktop-logo sprites-headerLogo",
            "alt": None,
            "role": None,
        }
        element.get_attribute.side_effect = attributes.get
        element.inner_text.return_value = ""

        self.assertEqual(
            agent._build_key(element, "a", "a", 0),
            "headerLogo",
        )
        self.assertEqual(
            agent._build_best_locator(element, "a"),
            'page.locator("[class~=\\"sprites-headerLogo\\"]").first()',
        )


class ExecutionAgentTests(unittest.TestCase):
    def test_execution_uses_project_root_for_config_and_report_paths(self):
        agent = ExecutionAgent()
        with tempfile.TemporaryDirectory() as directory:
            project_dir = Path(directory)
            test_path = project_dir / "generated" / "tests" / "sample.spec.js"
            test_path.parent.mkdir(parents=True)
            test_path.write_text(
                "test('sample', async () => {});",
                encoding="utf-8",
            )

            completed = Mock(returncode=0, stdout="1 passed", stderr="")
            with (
                patch(
                    "Agent_AUTOMATION_AI.execution_agent.__file__",
                    str(project_dir / "execution_agent.py"),
                ),
                patch.object(
                    agent,
                    "_resolve_playwright_command",
                    return_value=["playwright"],
                ),
                patch(
                    "Agent_AUTOMATION_AI.execution_agent.subprocess.run",
                    return_value=completed,
                ) as run,
            ):
                result = agent.execute_tests(
                    test_path,
                    "Sample",
                    headed=False,
                )

            self.assertEqual(run.call_args.kwargs["cwd"], project_dir)
            self.assertIn(
                "generated/tests/sample.spec.js",
                run.call_args.args[0],
            )
            self.assertEqual(
                result["playwright_report_dir"],
                str(
                    project_dir
                    / "generated"
                    / "reports"
                    / "playwright-report"
                ),
            )


if __name__ == "__main__":
    unittest.main()
