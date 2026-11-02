import os
import re
import shutil
import socket
import subprocess
import time
import webbrowser
from datetime import datetime
from pathlib import Path


class ExecutionAgent:

    # ==================================================
    # SANITIZE FOLDER NAME
    # ==================================================
    def _sanitize_folder_name(self, value):
        safe_value = re.sub(
            r"[^A-Za-z0-9_-]+",
            "_",
            str(value or "Automation"),
        ).strip("_")
        return safe_value or "Automation"

    # ==================================================
    # RESOLVE PLAYWRIGHT COMMAND
    # ==================================================
    def _resolve_playwright_command(self, project_root):
        project_root = Path(project_root).resolve()

        if os.name == "nt":
            local_playwright = (
                project_root / "node_modules" / ".bin" / "playwright.cmd"
            )
        else:
            local_playwright = (
                project_root / "node_modules" / ".bin" / "playwright"
            )

        if local_playwright.is_file():
            return [str(local_playwright)]

        if os.name == "nt":
            npx_command = (
                shutil.which("npx.cmd")
                or shutil.which("npx.exe")
                or shutil.which("npx")
            )
        else:
            npx_command = shutil.which("npx")

        if npx_command:
            return [npx_command, "playwright"]

        if os.name == "nt":
            fixed_npx_path = Path(r"C:\Program Files\nodejs\npx.cmd")
            if fixed_npx_path.is_file():
                return [str(fixed_npx_path), "playwright"]

        raise FileNotFoundError(
            "Neither the local Playwright executable nor npx.cmd was found. "
            "Verify Node.js and @playwright/test installation."
        )

    # ==================================================
    # ERROR DIAGNOSTICS
    # ==================================================
    def _extract_error_diagnostics(self, stdout="", stderr=""):
        error_log = f"{stdout}\n{stderr}"

        failed_locator = None
        locator_patterns = (
            r"Unknown page locator:\s*([^\r\n]+)",
            r"Known locator is not visible in current page state:\s*([^;\r\n]+)",
            r"waiting for (.+?) to be visible",
            r"locator\(['\"]([^'\"]+)['\"]\)",
        )

        for pattern in locator_patterns:
            match = re.search(pattern, error_log, flags=re.IGNORECASE)
            if match:
                failed_locator = match.group(1).strip().strip("`'\"")
                break

        failed_method = None
        method_match = re.search(
            r"(?:at PageObject\.|locator\.)([A-Za-z][A-Za-z0-9_]*)",
            error_log,
            flags=re.IGNORECASE,
        )
        if method_match:
            failed_method = method_match.group(1)

        current_url = None
        url_matches = re.findall(
            r"https?://[^\s<>\"']+",
            error_log,
            flags=re.IGNORECASE,
        )
        if url_matches:
            current_url = url_matches[-1].rstrip(".,);")

        return {
            "failed_locator": failed_locator,
            "failed_method": failed_method,
            "current_url": current_url,
        }

    # ==================================================
    # CLASSIFY EXECUTION ERROR
    # ==================================================
    def classify_execution_error(self, stdout="", stderr=""):
        error_log = f"{stdout}\n{stderr}".lower()
        diagnostics = self._extract_error_diagnostics(stdout, stderr)

        environment_patterns = (
        "command was not found",
        "executable was not found",
        "winerror 2",
        "browser executable doesn't exist",
            "browser executable does not exist",
            "please run the following command",
            "playwright install",
            "access is denied",
            "permission denied",
            "cannot find the file specified",
            "neither the local playwright executable",
            "node is not recognized",
        "npx is not recognized",
        
            # Browser context configuration failures
            "devicescalefactor",
            "not supported with null \"viewport\"",
            "browser.newcontext",
        )
        

        syntax_patterns = (
            "syntaxerror",
            "syntax error",
            "unexpected token",
            "unexpected identifier",
            "missing ) after argument list",
            "unterminated string",
        )

        navigation_patterns = (
            "page.goto",
            "page.waitforurl",
            "navigation timeout",
            "net::err_",
            "failed to load resource",
            'timeout exceeded while waiting for event "load"',
        )

        assertion_patterns = (
            "expect(received)",
            "tobetruthy",
            "tobefalsy",
            "tocontain",
            "toequal",
            "tohavetext",
            "tocontaintext",
            "expected:",
            "received:",
            "assertionerror",
        )

        locator_sync_patterns = (
            "strict mode violation",
            "waiting for locator",
            "element is not attached",
            "element is not visible",
            "element is not enabled",
            "element is outside of the viewport",
            "locator.click",
            "locator.fill",
            "locator.waitfor",
            "locator.check",
            "locator.selectoption",
        )

        result = {
            "category": "UNKNOWN",
            "auto_healing_allowed": False,
            "retry_allowed": False,
            "healing_reason": (
                "The failure did not match a safe automatic-healing category."
            ),
            **diagnostics,
        }

        if any(pattern in error_log for pattern in environment_patterns):
            result.update(
                category="ENVIRONMENT",
                healing_reason=(
                    "Environment and installation failures must be fixed "
                    "outside the Page Object."
                ),
            )
            return result

        if any(pattern in error_log for pattern in syntax_patterns):
            result.update(
                category="SCRIPT_SYNTAX",
                healing_reason=(
                    "Generated-code syntax failures must not trigger locator healing."
                ),
            )
            return result

        # Confirmed missing Page Object locator: safe candidate for discovery/patching.
        if "unknown page locator" in error_log:
            result.update(
                category="LOCATOR",
                auto_healing_allowed=True,
                retry_allowed=True,
                healing_reason=(
                    "The test referenced a Page Object locator that is not registered."
                ),
            )
            return result

        # Known locator exists but is not visible in the current page state.
        # Retry once, but do not blindly patch because this can be a wrong-page-state
        # or semantic-locator-generation problem.
        stale_patterns = (
            "known locator is not visible in current page state",
            "known locator is not attached in current page state",
            "locator exists but is not visible",
        )
        if any(pattern in error_log for pattern in stale_patterns):
            result.update(
                category="STALE_OR_WRONG_STATE_LOCATOR",
                auto_healing_allowed=False,
                retry_allowed=True,
                healing_reason=(
                    "The locator is registered but does not match the current page "
                    "state. Retry once; then fix semantic locator generation."
                ),
            )
            return result

        # Assertion failures intentionally remain real failures. This protects
        # application defects and incorrect generated expectations from being hidden.
        if any(pattern in error_log for pattern in assertion_patterns):
            result.update(
                category="ASSERTION",
                auto_healing_allowed=False,
                retry_allowed=False,
                healing_reason=(
                    "The locator resolved, but the expected condition was false. "
                    "Assertions are never auto-healed."
                ),
            )
            return result

        if any(pattern in error_log for pattern in navigation_patterns):
            result.update(
                category="NAVIGATION",
                auto_healing_allowed=False,
                retry_allowed=True,
                healing_reason=(
                    "Navigation may be transient, so one controlled retry is allowed."
                ),
            )
            return result

        if any(pattern in error_log for pattern in locator_sync_patterns):
            result.update(
                category="LOCATOR_OR_SYNCHRONIZATION",
                auto_healing_allowed=False,
                retry_allowed=True,
                healing_reason=(
                    "The locator exists but interaction or visibility failed. "
                    "One controlled retry is allowed without changing assertions."
                ),
            )
            return result

        if "timeouterror" in error_log or "timeout" in error_log:
            result.update(
                category="TIMEOUT",
                auto_healing_allowed=False,
                retry_allowed=True,
                healing_reason=(
                    "A generic timeout allows one controlled retry only."
                ),
            )
            return result

        return result

    # ==================================================
    # BUILD FAILED EXECUTION RESULT
    # ==================================================
    def _failed_result(
        self,
        error_message,
        project_root,
        screenshots_dir,
        feature_name,
        attempt_number,
        command=None,
        test_path=None,
        test_argument=None,
    ):
        command = command or []
        command_text = subprocess.list2cmdline(command) if command else ""
        classification = self.classify_execution_error(
            stderr=str(error_message)
        )

        report_directory = (
            Path(project_root)
            / "generated"
            / "reports"
            / "playwright-report"
        )

        return {
            "status": "FAILED",
            "returncode": 1,
            "stdout": "",
            "stderr": str(error_message),
            "command": command_text,
            "working_directory": str(project_root),
            "test_file": str(test_path) if test_path else None,
            "test_argument": test_argument,
            "feature_name": feature_name,
            "attempt_number": attempt_number,
            "screenshots_dir": str(screenshots_dir),
            "playwright_report_dir": str(report_directory),
            "error_category": classification["category"],
            "auto_healing_allowed": classification["auto_healing_allowed"],
            "retry_allowed": classification["retry_allowed"],
            "healing_reason": classification["healing_reason"],
            "failed_locator": classification.get("failed_locator"),
            "failed_method": classification.get("failed_method"),
            "current_url": classification.get("current_url"),
        }

    # ==================================================
    # REPORT SERVER HELPERS
    # ==================================================
    def _is_port_open(self, host, port, timeout=0.5):
        try:
            with socket.create_connection(
                (host, int(port)),
                timeout=timeout,
            ):
                return True
        except OSError:
            return False

    # ==================================================
    # OPEN PLAYWRIGHT HTML REPORT
    # ==================================================
    def open_playwright_report(
        self,
        project_root,
        report_port=9323,
        open_browser=True,
    ):
        project_root = Path(project_root).resolve()
        report_directory = (
            project_root
            / "generated"
            / "reports"
            / "playwright-report"
        )

        if not report_directory.is_dir():
            print(f"\nPlaywright HTML report not found: {report_directory}")
            return False

        host = "127.0.0.1"
        port = int(report_port)
        report_url = f"http://{host}:{port}"

        try:
            # Reuse an existing report server instead of causing EADDRINUSE.
            if self._is_port_open(host, port):
                print("\nPlaywright HTML report server is already running:")
                print(report_url)
                if open_browser:
                    webbrowser.open(report_url)
                return True

            command = self._resolve_playwright_command(project_root)
            command.extend(
                [
                    "show-report",
                    str(report_directory),
                    f"--host={host}",
                    f"--port={port}",
                ]
            )

            print("\nOpening Playwright HTML Report:")
            print(report_url)

            creation_flags = 0
            if os.name == "nt":
                creation_flags = getattr(
                    subprocess,
                    "CREATE_NEW_PROCESS_GROUP",
                    0,
                )

            subprocess.Popen(
                command,
                cwd=project_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=os.environ.copy(),
                shell=False,
                creationflags=creation_flags,
            )

            for _ in range(20):
                if self._is_port_open(host, port):
                    break
                time.sleep(0.25)

            if open_browser:
                webbrowser.open(report_url)

            return True

        except Exception as error:
            print(f"\nUnable to open Playwright HTML report: {error}")
            return False

    # ==================================================
    # EXECUTE PLAYWRIGHT TESTS
    # ==================================================
    def execute_tests(
        self,
        test_file=None,
        feature_name="Automation",
        attempt_number=1,
        headed=True,
        max_failures=1,
    ):
        package_dir = Path(__file__).resolve().parent
        project_root = package_dir

        safe_feature_name = self._sanitize_folder_name(feature_name)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_folder = (
            f"{safe_feature_name}_{timestamp}_Attempt_{attempt_number}"
        )
        screenshots_dir = (
            package_dir / "generated" / "screenshots" / screenshot_folder
        )
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        report_directory = (
            package_dir / "generated" / "reports" / "playwright-report"
        )

        print("\nScreenshots Folder:")
        print(screenshots_dir)

        try:
            command = self._resolve_playwright_command(project_root)
        except FileNotFoundError as error:
            return self._failed_result(
                error_message=error,
                project_root=project_root,
                screenshots_dir=screenshots_dir,
                feature_name=safe_feature_name,
                attempt_number=attempt_number,
            )

        command.append("test")
        if headed:
            command.append("--headed")

        command.extend(
            [
                "--project=chromium",
                "--workers=1",
                f"--max-failures={max(1, int(max_failures))}",
            ]
        )

        test_path = None
        test_argument = None

        if test_file is not None:
            test_path = Path(test_file).resolve()
            if not test_path.is_file():
                return self._failed_result(
                    error_message=f"Playwright test file not found: {test_path}",
                    project_root=project_root,
                    screenshots_dir=screenshots_dir,
                    feature_name=safe_feature_name,
                    attempt_number=attempt_number,
                    command=command,
                    test_path=test_path,
                )

            try:
                test_argument = test_path.relative_to(project_root).as_posix()
            except ValueError:
                test_argument = test_path.as_posix()
            command.append(test_argument)

        execution_environment = os.environ.copy()
        execution_environment["PLAYWRIGHT_SCREENSHOTS_DIR"] = (
            screenshots_dir.as_posix()
        )
        execution_environment["PLAYWRIGHT_FEATURE_NAME"] = safe_feature_name
        execution_environment["PLAYWRIGHT_ATTEMPT_NUMBER"] = str(
            attempt_number
        )

        if os.name == "nt":
            nodejs_directory = Path(r"C:\Program Files\nodejs")
            if nodejs_directory.is_dir():
                current_path = execution_environment.get("PATH", "")
                nodejs_text = str(nodejs_directory)
                path_entries = [
                    entry.lower()
                    for entry in current_path.split(os.pathsep)
                    if entry
                ]
                if nodejs_text.lower() not in path_entries:
                    execution_environment["PATH"] = (
                        nodejs_text + os.pathsep + current_path
                    )

        command_text = subprocess.list2cmdline(command)

        print("\nExecuting Command:")
        print(command)
        print("\nWorking Directory:")
        print(project_root)
        print("\nExecuting:")
        print(command_text)

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=project_root,
                env=execution_environment,
                shell=False,
                check=False,
            )

            status = "PASSED" if result.returncode == 0 else "FAILED"
            classification = self.classify_execution_error(
                stdout=result.stdout or "",
                stderr=result.stderr or "",
            )

            if status == "PASSED":
                classification = {
                    "category": "NONE",
                    "auto_healing_allowed": False,
                    "retry_allowed": False,
                    "healing_reason": "Execution passed; healing is not required.",
                    "failed_locator": None,
                    "failed_method": None,
                    "current_url": None,
                }

            return {
                "status": status,
                "returncode": result.returncode,
                "stdout": result.stdout or "",
                "stderr": result.stderr or "",
                "command": command_text,
                "working_directory": str(project_root),
                "test_file": str(test_path) if test_path else None,
                "test_argument": test_argument,
                "feature_name": safe_feature_name,
                "attempt_number": attempt_number,
                "screenshots_dir": str(screenshots_dir),
                "playwright_report_dir": str(report_directory),
                "error_category": classification["category"],
                "auto_healing_allowed": classification[
                    "auto_healing_allowed"
                ],
                "retry_allowed": classification["retry_allowed"],
                "healing_reason": classification["healing_reason"],
                "failed_locator": classification.get("failed_locator"),
                "failed_method": classification.get("failed_method"),
                "current_url": classification.get("current_url"),
            }

        except FileNotFoundError as error:
            return self._failed_result(
                error_message=(
                    "Unable to execute Playwright. Executable was not found: "
                    f"{error}"
                ),
                project_root=project_root,
                screenshots_dir=screenshots_dir,
                feature_name=safe_feature_name,
                attempt_number=attempt_number,
                command=command,
                test_path=test_path,
                test_argument=test_argument,
            )

        except Exception as error:
            return self._failed_result(
                error_message=(
                    "Unexpected Playwright execution error: "
                    f"{error}"
                ),
                project_root=project_root,
                screenshots_dir=screenshots_dir,
                feature_name=safe_feature_name,
                attempt_number=attempt_number,
                command=command,
                test_path=test_path,
                test_argument=test_argument,
            )
            