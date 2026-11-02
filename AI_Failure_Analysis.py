import html
import json
import re
from pathlib import Path

from .ai_agent import AIAgent


class FailureAgent:

    INVALID_LOCATOR_NAMES = {
        "",
        "$",
        "_",
        "unknown",
        "na",
        "n/a",
        "none",
        "null",
    }

    AUTO_FIXABLE_ERROR_TYPES = {
        "unknown page locator",
        "missing page object locator",
        "invalid locator",
        "invalid selector",
        "stale locator",
        "broken locator",
    }

    NON_HEALABLE_ERROR_TYPES = {
        "assertion failure",
        "timeout",
        "navigation failure",
        "environment failure",
        "script syntax error",
        "javascript syntax error",
    }

    def __init__(self):
        self.ai = AIAgent()

    # ==================================================
    # PATH HELPERS
    # ==================================================
    def _package_dir(self):
        return Path(__file__).resolve().parent

    def _pages_dir(self):
        return self._package_dir() / "generated" / "pages"

    def _resolve_pom_path(self, pom_file):
        if not pom_file:
            return None

        pom_text = html.unescape(str(pom_file)).strip()
        if pom_text.lower() in self.INVALID_LOCATOR_NAMES:
            return None

        supplied_path = Path(pom_text)
        if supplied_path.is_absolute() and supplied_path.exists():
            return supplied_path

        return self._pages_dir() / supplied_path.name

    # ==================================================
    # DETERMINISTIC ERROR CLASSIFICATION
    # ==================================================
    def classify_failure(self, error_log):
        text = html.unescape(str(error_log or ""))
        lower_text = text.lower()

        if "unknown page locator" in lower_text:
            return {
                "category": "LOCATOR",
                "error_type": "Unknown page locator",
                "auto_fix_possible": "YES",
            }

        environment_patterns = (
            "command was not found",
            "executable was not found",
            "winerror 2",
            "browser executable doesn't exist",
            "browser executable does not exist",
            "playwright install",
            "permission denied",
            "access is denied",
        )
        if any(pattern in lower_text for pattern in environment_patterns):
            return {
                "category": "ENVIRONMENT",
                "error_type": "Environment failure",
                "auto_fix_possible": "NO",
            }

        syntax_patterns = (
            "syntaxerror",
            "syntax error",
            "unexpected token",
            "unexpected identifier",
            "unterminated string",
        )
        if any(pattern in lower_text for pattern in syntax_patterns):
            return {
                "category": "SCRIPT_SYNTAX",
                "error_type": "Script syntax error",
                "auto_fix_possible": "NO",
            }

        assertion_patterns = (
            "expect(received)",
            "assertionerror",
            "tobetruthy",
            "tobefalsy",
            "tocontaintext",
            "tohavetext",
            "expected:",
            "received:",
        )
        if any(pattern in lower_text for pattern in assertion_patterns):
            return {
                "category": "ASSERTION",
                "error_type": "Assertion failure",
                "auto_fix_possible": "NO",
            }

        navigation_patterns = (
            "page.goto",
            "page.waitforurl",
            "navigation timeout",
            "net::err_",
        )
        if any(pattern in lower_text for pattern in navigation_patterns):
            return {
                "category": "NAVIGATION",
                "error_type": "Navigation failure",
                "auto_fix_possible": "NO",
            }

        if "strict mode violation" in lower_text:
            return {
                "category": "LOCATOR",
                "error_type": "Strict mode violation",
                "auto_fix_possible": "NO",
            }

        if "timeouterror" in lower_text or "timeout" in lower_text:
            return {
                "category": "SYNCHRONIZATION",
                "error_type": "Timeout",
                "auto_fix_possible": "NO",
            }

        return {
            "category": "UNKNOWN",
            "error_type": "Playwright runtime error",
            "auto_fix_possible": "NO",
        }

    # ==================================================
    # EXTRACT ERROR DETAILS
    # ==================================================
    def _extract_error_details(self, error_log):
        error_log = html.unescape(str(error_log or ""))

        details = {
            "pom_file": "Unknown",
            "script_file": "Unknown",
            "line_number": "Unknown",
            "missing_locator": "Unknown",
        }

        pom_matches = re.findall(
            r"generated[\\/]+pages[\\/]+([^\\/\s:]+\.js)",
            error_log,
            flags=re.IGNORECASE,
        )
        if not pom_matches:
            pom_matches = re.findall(
                r"(?:^|[\\/:\s])([A-Za-z0-9_$.-]+Page\.js)(?=[:\s\)])",
                error_log,
                flags=re.IGNORECASE,
            )
        if pom_matches:
            details["pom_file"] = pom_matches[0]

        script_matches = re.findall(
            r"generated[\\/]+tests[\\/]+([^\\/\s:]+\.spec\.js)",
            error_log,
            flags=re.IGNORECASE,
        )
        if not script_matches:
            script_matches = re.findall(
                r"([A-Za-z0-9_$.-]+\.spec\.js)(?=[:\s\)])",
                error_log,
                flags=re.IGNORECASE,
            )
        if script_matches:
            details["script_file"] = script_matches[0]

        locator_matches = re.findall(
            r"Unknown\s+page\s+locator\s*:\s*"
            r"([^\r\n]+)",
            error_log,
            flags=re.IGNORECASE,
        )

        unique_locators = []
        for locator_name in locator_matches:
            normalized = locator_name.strip()
            if re.search(r"\$\{[^}]+\}", normalized):
                continue
            if normalized.lower() in self.INVALID_LOCATOR_NAMES:
                continue
            if normalized not in unique_locators:
                unique_locators.append(normalized)

        if unique_locators:
            details["missing_locator"] = ", ".join(unique_locators)

        line_matches = re.findall(
            r"\.spec\.js:(\d+):\d+",
            error_log,
            flags=re.IGNORECASE,
        )
        if not line_matches:
            line_matches = re.findall(
                r"\.js:(\d+):\d+",
                error_log,
                flags=re.IGNORECASE,
            )
        if line_matches:
            details["line_number"] = line_matches[0]

        return details

    # ==================================================
    # MISSING LOCATOR PARSING
    # ==================================================
    def _sanitize_locator_name(self, value):
        value = str(value or "").strip()
        if re.fullmatch(
            r"[A-Za-z_$][A-Za-z0-9_$]*(?:[\s/.-]+"
            r"[A-Za-z_$][A-Za-z0-9_$]*)*",
            value,
        ):
            words = re.findall(r"[A-Za-z_$][A-Za-z0-9_$]*", value)
            return words[0] + "".join(
                word[0].upper() + word[1:]
                for word in words[1:]
            )

        match = re.search(
            r"[A-Za-z_$][A-Za-z0-9_$]*",
            value,
        )
        return match.group(0) if match else "Unknown"

    def _parse_missing_locators(self, value):
        raw_values = (
            list(value)
            if isinstance(value, (list, tuple, set))
            else [value]
        )
        missing_locators = []
        patterns = (
            r"Unknown page locator:\s*([^\r\n]+)",
            r"Missing Page Object locator:\s*([^\r\n]+)",
            r"locatorName\s*[:=]\s*[\"']([A-Za-z_$][A-Za-z0-9_$]*)[\"']",
        )

        for raw in raw_values:
            text = html.unescape(str(raw or ""))
            matched = False
            for locator_pattern in patterns:
                matches = re.findall(
                    locator_pattern,
                    text,
                    flags=re.IGNORECASE,
                )
                if matches:
                    matched = True
                for item in matches:
                    name = self._sanitize_locator_name(item)
                    if name not in {"Unknown", "locatorName"} and name not in missing_locators:
                        missing_locators.append(name)

            if matched:
                continue

            for item in re.split(r"[,;\n\r]+", text):
                name = self._sanitize_locator_name(item)
                if name not in {"Unknown", "locatorName"} and name not in missing_locators:
                    missing_locators.append(name)

        return missing_locators

    def _extract_confirmed_missing_locator(self, error_log):
        missing_locators = self._parse_missing_locators(error_log)
        return missing_locators[0] if missing_locators else "Unknown"

    # ==================================================
    # EXTRACT LOCATOR DECLARATIONS
    # ==================================================
    def _extract_locator_declarations(self, suggested_code):
        code = html.unescape(str(suggested_code or ""))
        code = (
            code.replace("```javascript", "")
            .replace("```js", "")
            .replace("```", "")
            .strip()
        )

        declarations = []
        start_pattern = re.compile(
            r"this\.([A-Za-z_$][\w$]*)\s*=\s*(page\.)",
            flags=re.MULTILINE,
        )

        for match in start_pattern.finditer(code):
            locator_name = match.group(1)
            statement_start = match.start()
            index = match.end()
            quote = None
            escaped = False
            round_depth = 0
            square_depth = 0
            curly_depth = 0

            while index < len(code):
                character = code[index]

                if escaped:
                    escaped = False
                    index += 1
                    continue
                if character == "\\":
                    escaped = True
                    index += 1
                    continue
                if quote:
                    if character == quote:
                        quote = None
                    index += 1
                    continue
                if character in {"'", '"', "`"}:
                    quote = character
                    index += 1
                    continue

                if character == "(":
                    round_depth += 1
                elif character == ")":
                    round_depth = max(0, round_depth - 1)
                elif character == "[":
                    square_depth += 1
                elif character == "]":
                    square_depth = max(0, square_depth - 1)
                elif character == "{":
                    curly_depth += 1
                elif character == "}":
                    curly_depth = max(0, curly_depth - 1)
                elif (
                    character == ";"
                    and round_depth == 0
                    and square_depth == 0
                    and curly_depth == 0
                ):
                    statement = code[statement_start:index + 1].strip()
                    expression_match = re.match(
                        r"this\.[A-Za-z_$][\w$]*\s*=\s*(page\.[\s\S]+);$",
                        statement,
                    )
                    if expression_match:
                        expression = expression_match.group(1).strip()
                        if re.match(
                            r"page\.(?:locator|getByRole|getByText|getByLabel|"
                            r"getByPlaceholder|getByTestId|getByAltText|getByTitle)\(",
                            expression,
                        ):
                            declarations.append(
                                {
                                    "name": locator_name,
                                    "expression": expression,
                                    "code": (
                                        f"this.{locator_name} = {expression};"
                                    ),
                                }
                            )
                    break

                index += 1

        unique = {}
        for declaration in declarations:
            unique[declaration["name"]] = declaration
        return list(unique.values())

    # ==================================================
    # POM CONTENT HELPERS
    # ==================================================
    def _locator_exists(self, content, locator_name):
        return bool(
            re.search(
                r"\bthis\." + re.escape(locator_name) + r"\s*=",
                content,
            )
        )

    def _find_constructor_insert_position(self, content):
        constructor_match = re.search(
            r"\bconstructor\s*\(\s*page\s*\)\s*\{",
            content,
        )
        if not constructor_match:
            return None

        opening_brace = content.find("{", constructor_match.start())
        if opening_brace == -1:
            return None

        brace_depth = 0
        quote = None
        escaped = False
        index = opening_brace

        while index < len(content):
            character = content[index]

            if escaped:
                escaped = False
                index += 1
                continue
            if character == "\\":
                escaped = True
                index += 1
                continue
            if quote:
                if character == quote:
                    quote = None
                index += 1
                continue
            if character in {"'", '"', "`"}:
                quote = character
                index += 1
                continue

            if character == "/" and index + 1 < len(content):
                next_character = content[index + 1]
                if next_character == "/":
                    newline = content.find("\n", index + 2)
                    if newline == -1:
                        return None
                    index = newline + 1
                    continue
                if next_character == "*":
                    comment_end = content.find("*/", index + 2)
                    if comment_end == -1:
                        return None
                    index = comment_end + 2
                    continue

            if character == "{":
                brace_depth += 1
            elif character == "}":
                brace_depth -= 1
                if brace_depth == 0:
                    return index

            index += 1

        return None

    def _replace_existing_declaration(
        self,
        content,
        locator_name,
        locator_expression,
    ):
        start_match = re.search(
            r"(?m)^(?P<indent>[ \t]*)this\."
            + re.escape(locator_name)
            + r"\s*=",
            content,
        )
        if not start_match:
            return content, False

        index = start_match.end()
        quote = None
        escaped = False
        round_depth = 0
        square_depth = 0
        curly_depth = 0

        while index < len(content):
            character = content[index]

            if escaped:
                escaped = False
                index += 1
                continue
            if character == "\\":
                escaped = True
                index += 1
                continue
            if quote:
                if character == quote:
                    quote = None
                index += 1
                continue
            if character in {"'", '"', "`"}:
                quote = character
                index += 1
                continue

            if character == "(":
                round_depth += 1
            elif character == ")":
                round_depth = max(0, round_depth - 1)
            elif character == "[":
                square_depth += 1
            elif character == "]":
                square_depth = max(0, square_depth - 1)
            elif character == "{":
                curly_depth += 1
            elif character == "}":
                curly_depth = max(0, curly_depth - 1)
            elif (
                character == ";"
                and round_depth == 0
                and square_depth == 0
                and curly_depth == 0
            ):
                replacement = (
                    f"{start_match.group('indent')}"
                    f"this.{locator_name} = {locator_expression};"
                )
                return (
                    content[:start_match.start()]
                    + replacement
                    + content[index + 1:],
                    True,
                )

            index += 1

        return content, False

    # ==================================================
    # AUTO FIX ELIGIBILITY
    # ==================================================
    def _is_auto_fix_eligible(self, failure_analysis):
        auto_fix_possible = str(
            failure_analysis.get("auto_fix_possible", "NO")
        ).strip().upper()
        if auto_fix_possible not in {"YES", "TRUE", "Y"}:
            return False

        category = str(
            failure_analysis.get("category", "")
        ).strip().upper()
        error_type = str(
            failure_analysis.get("error_type", "")
        ).strip().lower()
        missing_locators = self._parse_missing_locators(
            failure_analysis.get("missing_locator", "")
        )

        if category and category != "LOCATOR":
            return False
        if error_type in self.NON_HEALABLE_ERROR_TYPES:
            return False
        if "assertion" in error_type or "timeout" in error_type:
            return False
        if "navigation" in error_type or "environment" in error_type:
            return False

        return bool(missing_locators)

    # ==================================================
    # AUTO FIX POM
    # ==================================================
    def auto_fix_pom(self, failure_analysis):
        if not isinstance(failure_analysis, dict):
            print("Invalid failure analysis.")
            return False

        if not self._is_auto_fix_eligible(failure_analysis):
            print(
                "Failure is not eligible for locator auto-healing. "
                "Only confirmed missing-locator failures are patched."
            )
            return False

        missing_locators = self._parse_missing_locators(
            failure_analysis.get("missing_locator", "")
        )

        if len(missing_locators) != 1:
            print(
                "Automatic patch rejected: exactly one confirmed missing "
                "locator is required."
            )
            return False

        missing_locator = missing_locators[0]
        discovery_result = failure_analysis.get("discovery_result", {})

        if not isinstance(discovery_result, dict):
            print(
                "Automatic patch rejected: locator discovery result is missing."
            )
            return False

        if not discovery_result.get("success", False):
            print(
                "Automatic patch rejected: runtime DOM discovery did not "
                f"confirm the locator '{missing_locator}'."
            )
            return False

        matched_locator = self._sanitize_locator_name(
            discovery_result.get("matched_locator")
        )

        if matched_locator != missing_locator:
            print(
                "Automatic patch rejected: discovered locator name does not "
                "match the confirmed missing locator."
            )
            return False

        locator_expression = str(
            discovery_result.get("locator_expression", "")
        ).strip()

        if not locator_expression:
            print(
                "Automatic patch rejected: confirmed locator expression is empty."
            )
            return False

        # Patch only the runtime-confirmed expression, never AI-guessed code.
        suggested_code = (
            f"this.{missing_locator} = "
            f"{locator_expression};"
        )

        page_path = self._resolve_pom_path(
            failure_analysis.get("pom_file", "")
        )

        if not page_path or not page_path.exists():
            print(f"POM file not found: {page_path}")
            return False

        try:
            content = page_path.read_text(encoding="utf-8")
            declarations = self._extract_locator_declarations(
                suggested_code
            )

            declarations = [
                declaration
                for declaration in declarations
                if declaration["name"] in missing_locators
            ]

            if not declarations:
                print(
                    "No valid suggested declarations matched the confirmed "
                    "missing locator names."
                )
                return False

            added_locators = []
            replaced_locators = []
            skipped_locators = []
            declarations_to_insert = []

            error_text = (
                str(failure_analysis.get("error_type", ""))
                + " "
                + str(failure_analysis.get("root_cause", ""))
            ).lower()
            replacement_allowed = any(
                keyword in error_text
                for keyword in {
                    "invalid selector",
                    "broken locator",
                    "stale locator",
                }
            )

            for declaration in declarations:
                locator_name = declaration["name"]
                locator_expression = declaration["expression"]

                if self._locator_exists(content, locator_name):
                    if replacement_allowed:
                        content, replaced = self._replace_existing_declaration(
                            content,
                            locator_name,
                            locator_expression,
                        )
                        if replaced:
                            replaced_locators.append(locator_name)
                            continue

                    skipped_locators.append(locator_name)
                    continue

                declarations_to_insert.append(declaration["code"])
                added_locators.append(locator_name)

            if declarations_to_insert:
                insert_position = self._find_constructor_insert_position(
                    content
                )
                if insert_position is None:
                    print("Constructor block was not found.")
                    return False

                indented_code = "\n".join(
                    "        " + line.strip()
                    for line in declarations_to_insert
                    if line.strip()
                )
                content = (
                    content[:insert_position]
                    + "\n\n"
                    + indented_code
                    + "\n"
                    + content[insert_position:]
                )

            if not added_locators and not replaced_locators:
                if skipped_locators:
                    print(
                        "Confirmed locator declarations already exist: "
                        + ", ".join(skipped_locators)
                    )
                return False

            page_path.write_text(
                content.rstrip() + "\n",
                encoding="utf-8",
            )
            saved_content = page_path.read_text(encoding="utf-8")

            for locator_name in added_locators + replaced_locators:
                if not self._locator_exists(saved_content, locator_name):
                    print(
                        f"Auto-fix verification failed for: {locator_name}"
                    )
                    return False

            if added_locators:
                print(
                    "Auto Fix added locators: "
                    + ", ".join(added_locators)
                )
            if replaced_locators:
                print(
                    "Auto Fix replaced locators: "
                    + ", ".join(replaced_locators)
                )
            if skipped_locators:
                print(
                    "Existing locators skipped: "
                    + ", ".join(skipped_locators)
                )

            print(f"Auto Fix Applied: {page_path.name}")
            return True

        except Exception as error:
            print(f"Auto Fix Error: {error}")
            return False

    # ==================================================
    # AUTO LOCATOR RECOVERY
    # ==================================================
    def auto_discover_locator(
        self,
        url,
        missing_locator,
        locator_agent,
    ):
        missing_locators = self._parse_missing_locators(missing_locator)

        if len(missing_locators) != 1:
            print(
                "Exactly one valid missing locator is required for discovery."
            )
            return {
                "success": False,
                "reason": "A single confirmed locator name is required.",
            }

        confirmed_name = missing_locators[0]
        print(f"Discovering locator: {confirmed_name}")

        requirement_text = (
            "Discover only this missing UI element and its relevant page "
            f"state: {confirmed_name}"
        )

        try:
            discovered = locator_agent.extract_locators(
                url=url,
                requirement=requirement_text,
            )
        except Exception as error:
            print(f"Auto locator discovery error: {error}")
            return {
                "success": False,
                "missing_locator": confirmed_name,
                "reason": str(error),
            }

        discovered_locators = {}
        if isinstance(discovered, dict):
            nested = discovered.get("locators")
            discovered_locators = (
                nested if isinstance(nested, dict) else discovered
            )

        exact_match = discovered_locators.get(confirmed_name)
        if not isinstance(exact_match, dict):
            return {
                "success": False,
                "missing_locator": confirmed_name,
                "matched_locator": None,
                "reason": (
                    "Exact missing locator was not found during runtime DOM "
                    "discovery. Unsafe AI-guessed patch was blocked."
                ),
                "locators": discovered_locators,
            }

        locator_expression = str(
            exact_match.get("locator", "")
        ).strip()

        if not locator_expression:
            return {
                "success": False,
                "missing_locator": confirmed_name,
                "matched_locator": None,
                "reason": "Discovered locator expression is empty.",
                "locators": discovered_locators,
            }

        return {
            "success": True,
            "missing_locator": confirmed_name,
            "matched_locator": confirmed_name,
            "locator_expression": locator_expression,
            "locator_metadata": exact_match,
        }

    # ==================================================
    # BACKWARD-COMPATIBLE AUTO UPDATE
    # ==================================================
    def auto_update_pom(self, pom_file, suggested_code):
        print(
            "auto_update_pom was blocked because safe locator healing "
            "requires runtime DOM discovery."
        )
        return False

    # ==================================================
    # JSON RESPONSE EXTRACTION
    # ==================================================
    def _extract_json_response(self, response):
        response = (
            str(response or "")
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            json_match = re.search(r"\{[\s\S]*\}", response)
            if not json_match:
                return None
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                return None

    # ==================================================
    # ANALYZE FAILURE
    # ==================================================
    def analyze_failure(self, error_log):
        error_log = html.unescape(str(error_log or ""))
        details = self._extract_error_details(error_log)
        confirmed_locator = self._extract_confirmed_missing_locator(
            error_log
        )

        if confirmed_locator != "Unknown":
            details["missing_locator"] = confirmed_locator
        else:
            details["missing_locator"] = self._sanitize_locator_name(
                details.get("missing_locator")
            )
        classification = self.classify_failure(error_log)

        # Non-locator failures must never receive locator code.
        if classification["category"] != "LOCATOR":
            return {
                "pom_file": details["pom_file"],
                "script_file": details["script_file"],
                "line_number": details["line_number"],
                "missing_locator": details["missing_locator"],
                "category": classification["category"],
                "error_type": classification["error_type"],
                "root_cause": (
                    "The failure is not a confirmed missing-locator failure. "
                    "Smart waits may handle synchronization delays, while "
                    "assertion, navigation, environment, and syntax failures "
                    "must remain real failures."
                ),
                "impact": "Test execution failed.",
                "severity": "High",
                "suggested_fix": (
                    "Review the failing step, runtime data, page state, and "
                    "the generated execution report."
                ),
                "suggested_code": "",
                "recommendation": (
                    "Do not patch the Page Object unless a missing or stale "
                    "locator is confirmed."
                ),
                "confidence": "High",
                "auto_fix_possible": "NO",
            }

        missing_locators = self._parse_missing_locators(
            details["missing_locator"]
        )
        if not missing_locators:
            classification["auto_fix_possible"] = "NO"

        prompt = f"""
Analyze this confirmed Playwright locator failure.

ERROR LOG:
{error_log}

DETECTED INFORMATION:
POM FILE: {details["pom_file"]}
SCRIPT FILE: {details["script_file"]}
LINE NUMBER: {details["line_number"]}
MISSING LOCATOR: {details["missing_locator"]}
CATEGORY: {classification["category"]}

STRICT RULES:
1. This request is eligible for auto-fix only when the log contains
   'Unknown page locator'.
2. Preserve the exact detected camelCase missing locator names.
3. suggested_code must contain exactly one Page Object constructor
   declaration for each detected missing locator and no unrelated locators.
4. Use only page.locator(), page.getByRole(), page.getByText(),
   page.getByLabel(), page.getByPlaceholder(), page.getByTestId(),
   page.getByAltText(), or page.getByTitle().
5. Do not return methods, classes, imports, exports, comments, markdown,
   this.locators objects, timeout changes, assertion changes, or test changes.
6. Do not weaken or remove assertions.
7. Return valid JSON only.

REQUIRED JSON FORMAT:
{{
    "pom_file": "{details["pom_file"]}",
    "script_file": "{details["script_file"]}",
    "line_number": "{details["line_number"]}",
    "missing_locator": "{details["missing_locator"]}",
    "category": "LOCATOR",
    "error_type": "Missing Page Object locator",
    "root_cause": "",
    "impact": "",
    "severity": "High",
    "suggested_fix": "",
    "suggested_code": "",
    "recommendation": "",
    "confidence": "",
    "auto_fix_possible": "YES"
}}
"""

        response = self.ai.ask_ai(prompt)
        result = self._extract_json_response(response)

        if not isinstance(result, dict):
            return {
                "pom_file": details["pom_file"],
                "script_file": details["script_file"],
                "line_number": details["line_number"],
                "missing_locator": details["missing_locator"],
                "category": "LOCATOR",
                "error_type": "Missing Page Object locator",
                "root_cause": "Unable to parse AI response.",
                "impact": "Test execution failed.",
                "severity": "High",
                "suggested_fix": "Review the execution log.",
                "suggested_code": "",
                "recommendation": "Review the Page Object manually.",
                "confidence": "Low",
                "auto_fix_possible": "NO",
            }

        result["pom_file"] = details["pom_file"]
        result["script_file"] = details["script_file"]
        result["line_number"] = details["line_number"]
        result["missing_locator"] = details["missing_locator"]
        result["category"] = "LOCATOR"
        result["error_type"] = "Missing Page Object locator"

        defaults = {
            "root_cause": "One or more Page Object locators are missing.",
            "impact": "The affected test step cannot execute.",
            "severity": "High",
            "suggested_fix": "Add the missing locator declarations.",
            "suggested_code": "",
            "recommendation": "Verify selectors against the current DOM.",
            "confidence": "Medium",
            "auto_fix_possible": "NO",
        }
        for key, default_value in defaults.items():
            if not result.get(key):
                result[key] = default_value

        result["suggested_code"] = (
            html.unescape(str(result.get("suggested_code", "")))
            .replace("```javascript", "")
            .replace("```js", "")
            .replace("```", "")
            .strip()
        )

        declarations = self._extract_locator_declarations(
            result["suggested_code"]
        )
        declaration_names = {
            declaration["name"]
            for declaration in declarations
        }
        expected_names = set(missing_locators)

        if not declarations or declaration_names != expected_names:
            result["suggested_code"] = ""
            result["auto_fix_possible"] = "NO"
            result["recommendation"] = (
                "AI locator code did not exactly match the confirmed missing "
                "locator names; no automatic patch was allowed."
            )
        else:
            result["auto_fix_possible"] = "YES"

        return result
