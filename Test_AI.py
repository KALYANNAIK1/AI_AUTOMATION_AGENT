import argparse
import html
import json
import re
import sys
import traceback
from pathlib import Path


# ==================================================
# PROJECT PATHS
# ==================================================

PROJECT_DIR = Path(__file__).resolve().parent
PROJECT_PARENT = PROJECT_DIR.parent
GENERATED_DIR = PROJECT_DIR / "generated"

if str(PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(PROJECT_PARENT))

if not __package__:
    __package__ = PROJECT_DIR.name


# ==================================================
# IMPORTS
# ==================================================

from .AI_Failure_Analysis import FailureAgent
from .Excel_Agent import ExcelAgent
from .dashboard_agent import DashboardAgent
from .execution_agent import ExecutionAgent
from .fdd_reader import FDDReader
from .jira_agent import JiraAgent
from .locator_agent import LocatorAgent
from .notification_agent import NotificationAgent
from .pageobject_agent import PageObjectAgent
from .playwright_agent import PlaywrightAgent
from .report_agent import ReportAgent
from .requirement_agent import RequirementAgent
from .rtm_agent import RTMAgent
from .scenario_agent import ScenarioAgent
from .testcase_agent import TestCaseAgent
from .testdata_agent import TestDataAgent

notification_agent = None

#==================================================
# CONSOLE COLOR CLASS   
#==================================================
class ConsoleColor:

    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    PINK = "\033[95m"


def print_error(message):

    print(
        f"{ConsoleColor.BOLD}"
        f"{ConsoleColor.RED}"
        f"{message}"
        f"{ConsoleColor.RESET}"
    )


def print_warning(message):

    print(
        f"{ConsoleColor.YELLOW}"
        f"{message}"
        f"{ConsoleColor.RESET}"
    )


def print_success(message):

    print(
        f"{ConsoleColor.GREEN}"
        f"{message}"
        f"{ConsoleColor.RESET}"
    )


def print_info(message):

    print(
        f"{ConsoleColor.CYAN}"
        f"{message}"
        f"{ConsoleColor.RESET}"
    )


def print_healing(message):

    print(
        f"{ConsoleColor.MAGENTA}"
        f"{message}"
        f"{ConsoleColor.RESET}"
    )
def print_pink(message):

    print(
        f"{ConsoleColor.BOLD}"
        f"{ConsoleColor.PINK}"
        f"{message}"
        f"{ConsoleColor.RESET}"
    )
# ==================================================
# CONSOLE ENCODING
# ==================================================

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(errors="replace")


# ==================================================
# HELPERS
# ==================================================

def clean_html_text(text):
    if text is None:
        return ""

    text = html.unescape(str(text))
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def normalize_url(text):
    if not text:
        return None

    text = html.unescape(str(text))

    href_match = re.search(
        r'<a\b[^>]*\bhref=["\']([^"\']+)["\'][^>]*>',
        text,
        flags=re.IGNORECASE,
    )
    if href_match:
        return href_match.group(1).strip()

    url_match = re.search(
        r"https?://[^\s<>\"']+",
        text,
        flags=re.IGNORECASE,
    )
    if url_match:
        return url_match.group(0).rstrip(".,);")

    return None


def extract_runtime_data(requirement):
    requirement_text = html.unescape(str(requirement or ""))

    data = {
        "url": normalize_url(requirement_text),
        "username": None,
        "email": None,
        "login_credential": None,
        "password": None,
        "search_keyword": None,
        "expected_search_result": None,
    }

    patterns = {
        "username": r"Username\s*:\s*([^\n\r]+)",
        "email": r"Email\s*:\s*([^\n\r]+)",
        "password": r"Password\s*:\s*([^\n\r]+)",
        "search_keyword": r"Search\s+Keyword\s*:\s*([^\n\r]+)",
        "expected_search_result": (
            r"Expected\s+Search\s+Result\s*:\s*([^\n\r]+)"
        ),
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, requirement_text, flags=re.IGNORECASE)
        if match:
            data[key] = clean_html_text(match.group(1))

    login_value = data.get("username") or data.get("email")
    if login_value:
        data["login_credential"] = login_value

    return {
        key: value
        for key, value in data.items()
        if value not in (None, "")
    }


def strip_code_fence(content):
    content = str(content or "").strip()
    if not content.startswith("```"):
        return content

    lines = content.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def write_text(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(content).rstrip() + "\n", encoding="utf-8")
    return path


def build_error_log(execution_result):
    return (
        str(execution_result.get("stdout", ""))
        + "\n"
        + str(execution_result.get("stderr", ""))
    )


def normalize_status(execution_result):
    status = str(execution_result.get("status", "")).upper()
    if status in {"SUCCESS", "PASSED", "PASS"}:
        return "PASSED"
    return "FAILED"


def failure_signature(failure_analysis):
    category = str(failure_analysis.get("category", "")).strip().lower()
    error_type = str(failure_analysis.get("error_type", "")).strip().lower()
    missing_locator = str(
        failure_analysis.get("missing_locator", "")
    ).strip().lower()
    root_cause = str(
        failure_analysis.get("root_cause", "")
    ).strip().lower()

    return "|".join(
        [
            category,
            error_type,
            missing_locator,
            root_cause[:200],
        ]
    )


def execution_category(execution_result, execution_agent):
    category = str(
        execution_result.get("error_category", "")
    ).strip().upper()

    if category:
        return {
            "category": category,

            "auto_healing_allowed": bool(
                execution_result.get(
                    "auto_healing_allowed",
                    False
                )
            ),

            "retry_allowed": bool(
                execution_result.get(
                    "retry_allowed",
                    False
                )
            ),

            "healing_reason": execution_result.get(
                "healing_reason",
                ""
            ),

            "failed_locator": execution_result.get(
                "failed_locator"
            ),

            "failed_method": execution_result.get(
                "failed_method"
            ),

            "current_url": execution_result.get(
                "current_url"
            ),
        }

    return execution_agent.classify_execution_error(
        stdout=execution_result.get("stdout", ""),
        stderr=execution_result.get("stderr", ""),
    )


# ==================================================
# SELF-HEALING EXECUTION
# ==================================================

def execute_with_healing(
    execution_agent,
    failure_agent,
    locator_agent,
    playwright_path,
    feature_name,
    url,
    page_object_path,
    max_healing_attempts=4,
):
    execution_result = execution_agent.execute_tests(
        playwright_path,
        feature_name,
        attempt_number=1,
        max_failures=1,
    )

    healing_history = []
    previous_signatures = set()
    synchronization_retry_used = False

    for attempt in range(1, max_healing_attempts + 1):
        if normalize_status(execution_result) == "PASSED":
            break

        classification = execution_category(
            execution_result,
            execution_agent,
        )
        category = classification["category"]
        error_log = build_error_log(execution_result)

        print(f"\n===== RECOVERY ATTEMPT {attempt} =====")
        print(f"\nError Category: {category}")
        print("\n===== ERROR LOG =====")
        print(error_log[:5000])

        # One controlled retry is allowed for timing/navigation instability.
        # No POM changes are made for these categories.
        if category in {
    "TIMEOUT",
    "NAVIGATION",
    "LOCATOR_OR_SYNCHRONIZATION",
    "SYNCHRONIZATION",
    "STALE_OR_WRONG_STATE_LOCATOR",
}:
            if classification.get("retry_allowed") and not synchronization_retry_used:
                synchronization_retry_used = True
                healing_history.append(
    {
        "attempt": attempt,
        "execution_attempt": attempt,
        "status": "CONTROLLED_RETRY",
        "category": category,
        "auto_fix_applied": False,

        "reason": classification.get(
            "healing_reason"
        ) or (
            "One retry was allowed for a possible "
            "transient synchronization or navigation delay."
        ),

        "failed_locator": classification.get(
            "failed_locator"
        ),

        "failed_method": classification.get(
            "failed_method"
        ),

        "current_url": classification.get(
            "current_url"
        ),
    }
)

                print(
                    "\nTransient synchronization/navigation failure detected. "
                    "Re-running once without changing locators or assertions..."
                )

                execution_result = execution_agent.execute_tests(
                    playwright_path,
                    feature_name,
                    attempt_number=attempt + 1,
                    max_failures=1,
                )
                continue

            healing_history.append(
    {
        "attempt": attempt,
        "execution_attempt": attempt,
        "status": "RETRY_EXHAUSTED",
        "category": category,
        "auto_fix_applied": False,

        "reason": classification.get(
            "healing_reason",
            "Controlled retry was exhausted."
        ),

        "failed_locator": classification.get(
            "failed_locator"
        ),

        "failed_method": classification.get(
            "failed_method"
        ),

        "current_url": classification.get(
            "current_url"
        ),
    }
)
            print(
                "\nSynchronization retry was already used. "
                "The failure remains a real test failure."
            )
            break

        # Assertions, environment failures, and syntax failures are not
        # locator-healed. This prevents real defects from being hidden.
        if category in {
            "ASSERTION",
            "ENVIRONMENT",
            "SCRIPT_SYNTAX",
            "UNKNOWN",
        }:
            failure_analysis = failure_agent.analyze_failure(error_log)

            if page_object_path:
                failure_analysis["pom_file"] = Path(page_object_path).name

            healing_history.append(
    {
        "attempt": attempt,
        "execution_attempt": attempt,
        "status": "NOT_HEALABLE",
        "category": category,
        "analysis": failure_analysis,
        "auto_fix_applied": False,

        "reason": classification.get(
            "healing_reason",
            "This failure is not eligible for automatic healing."
        ),

        "failed_locator": classification.get(
            "failed_locator"
        ),

        "failed_method": classification.get(
            "failed_method"
        ),

        "current_url": classification.get(
            "current_url"
        ),
    }
)

            print(
                "\nAuto-healing skipped. Assertions, environment errors, "
                "syntax errors, and unknown failures must remain visible."
            )
            break

        # Only confirmed missing-locator failures reach this block.
        if category != "LOCATOR" or not classification.get(
            "auto_healing_allowed"
        ):
            healing_history.append(
                {
                    "attempt": attempt,
                    "execution_attempt": attempt,
                    "status": "NOT_ELIGIBLE_FOR_LOCATOR_HEALING",
                    "category": category,
                    "auto_fix_applied": False,
                }
            )
            break

        failure_analysis = failure_agent.analyze_failure(error_log)
        failure_analysis["category"] = "LOCATOR"

        if page_object_path:
            failure_analysis["pom_file"] = Path(page_object_path).name

        signature = failure_signature(failure_analysis)
        if signature in previous_signatures:
            print(
                "\nHealing stopped because the same locator failure "
                "occurred again."
            )
            healing_history.append(
                {
                    "attempt": attempt,
                    "execution_attempt": attempt,
                    "status": "REPEATED_FAILURE",
                    "category": "LOCATOR",
                    "analysis": failure_analysis,
                    "auto_fix_applied": False,
                }
            )
            break

        previous_signatures.add(signature)

        missing_locator = str(
            failure_analysis.get("missing_locator", "")
        ).strip()
        discovered = {}

        if missing_locator.lower() not in {
            "",
            "unknown",
            "n/a",
            "none",
            "null",
            "$",
            "_",
        }:
            discovered = failure_agent.auto_discover_locator(
                url=url,
                missing_locator=missing_locator,
                locator_agent=locator_agent,
            )
            failure_analysis[
    "discovery_result"
] = discovered

            print("\n===== AUTO DISCOVERED LOCATOR =====")
            print(json.dumps(discovered, indent=4, default=str))

        auto_fix_result = failure_agent.auto_fix_pom(
            failure_analysis
        )

        healing_history.append(
            {
                "attempt": attempt,
                "execution_attempt": attempt,
                "status": (
                    "LOCATOR_FIX_APPLIED"
                    if auto_fix_result
                    else "LOCATOR_FIX_FAILED"
                ),
                "category": "LOCATOR",
                "analysis": failure_analysis,
                "discovered": discovered,
                "auto_fix_applied": bool(auto_fix_result),
            }
        )

        if not auto_fix_result:
            print("\nAuto-healing could not apply a safe locator fix.")
            break

        print("\nRe-running tests after automatic locator fix...")
        execution_result = execution_agent.execute_tests(
            playwright_path,
            feature_name,
            attempt_number=attempt + 1,
            max_failures=1,
        )

    return execution_result, healing_history


# ==================================================
# MAIN
# ==================================================

def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Generate and execute AI-based Playwright automation artifacts."
        )
    )

    parser.add_argument(
        "--requirement",
        type=Path,
        default=PROJECT_DIR / "Requirements" / "login_requirement.txt",
        help="Requirement file path",
    )
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Execute the generated Playwright tests",
    )
    parser.add_argument(
        "--max-healing-attempts",
        type=int,
        default=4,
        help="Maximum automatic recovery attempts",
    )

    args = parser.parse_args(argv)

    requirement_path = args.requirement
    if not requirement_path.is_absolute():
        requirement_path = Path.cwd() / requirement_path

    if not requirement_path.exists():
        parser.error(f"Requirement file not found: {requirement_path}")

    requirement = FDDReader().read_file(requirement_path).strip()
    if not requirement:
        parser.error(f"Requirement file is empty: {requirement_path}")

    print("\n===== REQUIREMENT =====")
    print(requirement)

    requirement_agent = RequirementAgent()
    scenario_agent = ScenarioAgent()
    testcase_agent = TestCaseAgent()
    testdata_agent = TestDataAgent()
    locator_agent = LocatorAgent()
    pageobject_agent = PageObjectAgent()
    playwright_agent = PlaywrightAgent()
    execution_agent = ExecutionAgent()
    failure_agent = FailureAgent()
    report_agent = ReportAgent()
    dashboard_agent = DashboardAgent()
    excel_agent = ExcelAgent()
    rtm_agent = RTMAgent()
    jira_agent = JiraAgent()
    notification_agent = NotificationAgent()

    analysis = requirement_agent.analyze_requirement(requirement)
    print("\n===== REQUIREMENT ANALYSIS =====")
    print(json.dumps(analysis, indent=4, default=str))

    feature_name = str(analysis.get("feature_name", "Automation") or "Automation")
    business_flow = analysis.get("business_flow", [])

    scenarios = scenario_agent.generate_scenarios(requirement)
    print("\n===== AI GENERATED SCENARIOS =====")
    print(json.dumps(scenarios, indent=4, default=str))

    testcases = testcase_agent.generate_testcases(scenarios)
    print("\n===== AI GENERATED TEST CASES =====")
    print(json.dumps(testcases, indent=4, default=str))

    test_data = testdata_agent.generate_test_data(testcases)
    print("\n===== GENERATED TEST DATA =====")
    print(json.dumps(test_data, indent=4, default=str))

    runtime_data = extract_runtime_data(requirement)
    url = normalize_url(runtime_data.get("url"))
    if url:
        runtime_data["url"] = url

    print("\n===== RUNTIME DATA =====")
    print(json.dumps(runtime_data, indent=4, default=str))

    if not url or not url.startswith(("http://", "https://")):
        raise ValueError(
            "A valid plain HTTP or HTTPS URL could not be extracted."
        )

    locator_data = locator_agent.extract_locators(
        url=url,
        requirement=requirement,
        business_flow=business_flow,
        username=runtime_data.get("login_credential"),
        password=runtime_data.get("password"),
    )

    if isinstance(locator_data, dict) and isinstance(
        locator_data.get("locators"), dict
    ):
        locators = locator_data.get("locators", {})
    elif isinstance(locator_data, dict):
        locators = locator_data
    else:
        locators = {}

    print("\n===== GENERATED LOCATORS =====")
    print(json.dumps(locators, indent=4, default=str))
    print("\n===== IFRAMES =====")
    print(
        json.dumps(
            locator_data.get("iframes", [])
            if isinstance(locator_data, dict)
            else [],
            indent=4,
            default=str,
        )
    )
    print("\n===== WINDOWS =====")
    print(
        json.dumps(
            locator_data.get("windows", [])
            if isinstance(locator_data, dict)
            else [],
            indent=4,
            default=str,
        )
    )

    requirements_for_rtm = [
        {
            "requirement_id": "REQ-001",
            "requirement": feature_name,
            "scenario_id": (
                scenarios[0].get("scenario_id", "TS-001")
                if scenarios and isinstance(scenarios[0], dict)
                else "TS-001"
            ),
        }
    ]
    rtm = rtm_agent.generate_rtm(
        requirements_for_rtm,
        scenarios,
        testcases,
    )
    print("\n===== RTM =====")
    print(json.dumps(rtm, indent=4, default=str))

    page_name = pageobject_agent.generate_file_name(feature_name)
    page_object = pageobject_agent.generate_page_object(
        requirement,
        locators,
    )

    if not str(page_object).strip():
        raise ValueError("Page Object generation returned empty content.")
    if (
        "class PageObject" not in page_object
        or "module.exports = PageObject" not in page_object
    ):
        raise ValueError(
            "Generated Page Object is missing the class or CommonJS export."
        )

    page_object_path = pageobject_agent.save_page_object(
        page_object,
        page_name,
    )
    print("\n===== GENERATED PAGE OBJECT =====")
    print(page_object)

    playwright_script = playwright_agent.generate_playwright_script(
        requirement=requirement,
        testcases=testcases,
        runtime_data=runtime_data,
        locators=locators,
        page_object_content=page_object,
        page_name=page_name,
    )
    playwright_script = strip_code_fence(playwright_script)

    if not playwright_script.strip():
        raise ValueError("Playwright script generation returned empty content.")

    print("\n===== GENERATED PLAYWRIGHT SCRIPT =====")
    print(playwright_script)

    analysis_path = write_text(
        GENERATED_DIR / "analysis" / "requirement_analysis.json",
        json.dumps(analysis, indent=4, default=str),
    )
    scenarios_path = write_text(
        GENERATED_DIR / "scenarios" / "scenarios.json",
        json.dumps(scenarios, indent=4, default=str),
    )
    testcases_path = write_text(
        GENERATED_DIR / "testcases" / "testcases.json",
        json.dumps(testcases, indent=4, default=str),
    )
    testdata_path = write_text(
        GENERATED_DIR / "testdata" / "testdata.json",
        json.dumps(test_data, indent=4, default=str),
    )
    rtm_path = write_text(
        GENERATED_DIR / "rtm" / "rtm.json",
        json.dumps(rtm, indent=4, default=str),
    )
    locators_path = locator_agent.save_locators(
        locators,
        GENERATED_DIR / "locators" / "locators.json",
    )
    playwright_path = playwright_agent.save_script(
        playwright_script,
        feature_name,
    )

    req_excel = excel_agent.save_requirements(requirement)
    scenario_excel = excel_agent.save_scenarios(scenarios)
    testcase_excel = excel_agent.save_testcases(testcases)

    print("\n===== GENERATED ARTIFACTS =====")
    for artifact_path in [
        analysis_path,
        scenarios_path,
        testcases_path,
        testdata_path,
        rtm_path,
        locators_path,
        page_object_path,
        playwright_path,
        req_excel,
        scenario_excel,
        testcase_excel,
    ]:
        print(f"Generated: {artifact_path}")

    if not args.run_tests:
        print(
            "\nPlaywright execution skipped.\n"
            "Run with:\n"
            "python Test_AI.py --run-tests"
        )
        return 0

    execution_result, healing_history = execute_with_healing(
        execution_agent=execution_agent,
        failure_agent=failure_agent,
        locator_agent=locator_agent,
        playwright_path=playwright_path,
        feature_name=feature_name,
        url=url,
        page_object_path=page_object_path,
        max_healing_attempts=max(1, args.max_healing_attempts),
    )

    final_status = normalize_status(execution_result)
    execution_result["status"] = final_status

    healing_history_path = write_text(
        GENERATED_DIR / "healing" / "healing_history.json",
        json.dumps(healing_history, indent=4, default=str),
    )

    report = report_agent.generate_report(execution_result)
    report_path = write_text(
        GENERATED_DIR / "reports" / "execution_report.json",
        json.dumps(report, indent=4, default=str),
    )
    html_report = report_agent.generate_html_report(report)
    html_report_path = write_text(
        GENERATED_DIR / "reports" / "execution_report.html",
        html_report,
    )
    dashboard_path = dashboard_agent.generate_dashboard(
        feature_name,
        report,
    )

    print("\n===== FINAL EXECUTION REPORT =====")
    print(json.dumps(report, indent=4, default=str))
    print("\n===== HEALING HISTORY =====")
    print(json.dumps(healing_history, indent=4, default=str))

    jira_result = None
    final_failure_analysis = None
    if final_status == "FAILED":
        final_error_log = build_error_log(execution_result)
        final_failure_analysis = failure_agent.analyze_failure(
            final_error_log
        )
        if page_object_path:
            final_failure_analysis["pom_file"] = Path(
                page_object_path
            ).name
        final_failure_analysis["failed_locator"] = execution_result.get(
            "failed_locator"
        )
        final_failure_analysis["failed_method"] = execution_result.get(
            "failed_method"
        )
        final_failure_analysis["current_url"] = execution_result.get(
            "current_url"
        )
        final_failure_analysis["healing_reason"] = execution_result.get(
            "healing_reason"
        )

        jira_result = jira_agent.create_defect(
            summary=f"Playwright Failure - {feature_name}",
            description=str(final_failure_analysis),
            severity=final_failure_analysis.get("severity", "High"),
        )
        print("\n===== JIRA DEFECT =====")
        print(jira_result)
    failure_analysis = final_failure_analysis or {}
#==================================================
# ROOT CAUSE ANALYSIS PRINTING  
#=================================================      
    category = str(
        failure_analysis.get(
            "category",
            "UNKNOWN"
        )
    )

    error_type = str(
        failure_analysis.get(
            "error_type",
            "Unknown Error"
        )
    )

    missing_locator = str(
        failure_analysis.get(
            "missing_locator",
            "Unknown"
        )
    )

    root_cause = str(
        failure_analysis.get(
            "root_cause",
            "Root cause was not identified."
        )
    )

    impact = str(
        failure_analysis.get(
            "impact",
            "Impact was not identified."
        )
    )

    suggested_fix = str(
        failure_analysis.get(
            "suggested_fix",
            "No suggested fix is available."
        )
    )

    recommendation = str(
        failure_analysis.get(
            "recommendation",
            "No recommendation is available."
        )
    )

    confidence = str(
        failure_analysis.get(
            "confidence",
            "Unknown"
        )
    )

    print_pink(
        "\n"
        "========================================\n"
        "         ROOT CAUSE ANALYSIS\n"
        "========================================"
    )

    print_pink(
        f"Category        : {category}"
    )

    print_pink(
        f"Error Type      : {error_type}"
    )

    if missing_locator.lower() not in {
        "",
        "unknown",
        "none",
        "null",
        "n/a"
    }:

        print_pink(
            f"Missing Locator : {missing_locator}"
        )

    print_pink(
        f"Root Cause      : {root_cause}"
    )

    print_pink(
        f"Impact          : {impact}"
    )

    print_pink(
        f"Suggested Fix   : {suggested_fix}"
    )

    print_pink(
        f"Recommendation  : {recommendation}"
    )

    print_pink(
        f"Confidence      : {confidence}"
    )

    print_pink(
        "========================================"
    )

    notification_agent.send_notification(
        f"""
Automation Execution Completed

Feature:
{feature_name}

Status:
{final_status}

Recovery Attempts:
{len(locals().get('healing_history', []))}

Final Error Category:
{execution_result.get('error_category', 'NONE')}

Screenshots Folder:
{execution_result.get('screenshots_dir', 'N/A')}

JSON Report:
{report_path}

HTML Report:
{html_report_path}

Healing History:
{healing_history_path}

Dashboard:
{dashboard_path}
""",
        status=final_status,
    )

    report_opened = execution_agent.open_playwright_report(
        project_root=PROJECT_DIR,
        report_port=9323,
    )

    if report_opened:
        print_info("\nPlaywright HTML report opened at:")
        print_info("http://127.0.0.1:9323")
    else:
        print_warning("\nPlaywright HTML report could not be opened.")

    if final_status == "PASSED":
        print_success("\n===== OVERALL STATUS: PASSED =====")
    else:
        print_error("\n===== OVERALL STATUS: FAILED =====")

    print_info("\nAll framework processing completed.")

    return (
        0
        if final_status == "PASSED"
        else int(execution_result.get("returncode", 1) or 1)
    )

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as error:
        print("\nUNEXPECTED FRAMEWORK ERROR:")
        print(f"{type(error).__name__}: {error}")
        traceback.print_exc()
        raise SystemExit(1)
