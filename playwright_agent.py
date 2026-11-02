from datetime import datetime
from pathlib import Path
import html
import json
import re

from .ai_agent import AIAgent


class PlaywrightAgent:

    def __init__(self):
        self.ai = AIAgent()

    # ==================================================
    # HTML CLEANUP
    # ==================================================
    def clean_html(
        self,
        text
    ):

        if not text:
            return ""

        text = html.unescape(
            str(text)
        )

        # Extract plain URL from an HTML anchor.
        href_match = re.search(
            r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>',
            text,
            flags=re.IGNORECASE
        )

        if href_match:
            return href_match.group(1).strip()

        text = re.sub(
            r"<br\s*/?>",
            "\n",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"<[^>]+>",
            "",
            text
        )

        return text.strip()

    # ==================================================
    # JAVASCRIPT STRING
    # ==================================================
    def _javascript_string(
        self,
        value
    ):

        return json.dumps(
            str(value),
            ensure_ascii=False
        )

    # ==================================================
    # LOCATOR METADATA FORMATTING
    # ==================================================
    def _format_locator_metadata(
        self,
        locators
    ):

        locator_metadata = {}

        if isinstance(locators, dict):

            if (
                "locators" in locators
                and isinstance(
                    locators.get("locators"),
                    dict
                )
            ):
                locator_metadata = locators.get(
                    "locators",
                    {}
                )

            else:
                locator_metadata = locators

        available_locators = list(
            locator_metadata.keys()
        )

        locator_lines = []

        for locator_name, metadata in (
            locator_metadata.items()
        ):

            if isinstance(metadata, dict):

                element_type = metadata.get(
                    "type",
                    "unknown"
                )

                locator_expression = metadata.get(
                    "locator",
                    ""
                )

                priority = metadata.get(
                    "priority",
                    ""
                )

                options = metadata.get(
                    "options",
                    []
                )

                state = metadata.get(
                    "state",
                    ""
                )

                page_url = metadata.get(
                    "page_url",
                    ""
                )

            else:

                element_type = "unknown"
                locator_expression = str(
                    metadata
                )
                priority = ""
                options = []
                state = ""
                page_url = ""

            metadata_parts = [
                f"name={locator_name}",
                f"type={element_type}",
                f"locator={locator_expression}"
            ]

            if priority != "":
                metadata_parts.append(
                    f"priority={priority}"
                )

            if state:
                metadata_parts.append(
                    f"state={state}"
                )

            if page_url:
                metadata_parts.append(
                    f"pageUrl={page_url}"
                )

            if options:

                options_text = ", ".join(
                    str(option)
                    for option in options
                )

                metadata_parts.append(
                    f"options=[{options_text}]"
                )

            locator_lines.append(
                "- " + " | ".join(
                    metadata_parts
                )
            )

        locators_text = "\n".join(
            locator_lines
        )

        if not locators_text:
            locators_text = (
                "NO PAGE OBJECT LOCATORS AVAILABLE"
            )

        return (
            locator_metadata,
            available_locators,
            locators_text
        )

    # ==================================================
    # EXTRACT LOCATOR USAGE
    # ==================================================
    def _extract_used_locators(
        self,
        script_content
    ):

        locator_pattern = re.compile(
            r"(?:"
            r"clickElement|"
            r"fillField|"
            r"typeText|"
            r"getText|"
            r"isVisible|"
            r"scrollToElement|"
            r"selectOption|"
            r"checkElement|"
            r"uncheckElement|"
            r"hoverElement|"
            r"waitForElement|"
            r"pressKey"
            r")"
            r"\(\s*['\"]([A-Za-z0-9_$-]+)['\"]"
        )

        return locator_pattern.findall(
            str(script_content)
        )

    # ==================================================
    # VALIDATE LOCATOR NAMES
    # ==================================================
    def _validate_locator_names(
        self,
        script_content,
        available_locators
    ):

        used_locators = (
            self._extract_used_locators(
                script_content
            )
        )

        available_locator_set = set(
            available_locators
        )

        invalid_locators = sorted(
            {
                locator_name
                for locator_name in used_locators
                if locator_name
                not in available_locator_set
            }
        )

        if invalid_locators:

            print(
                "\nWARNING: AI generated locator names "
                "that are not currently available in "
                "the Page Object:"
            )

            for locator_name in invalid_locators:
                print(
                    f"- {locator_name}"
                )

            print(
                "Execution will continue so the "
                "FailureAgent can attempt self-healing."
            )

        return invalid_locators

    # ==================================================
    # VALIDATE LOCATOR TYPES
    # ==================================================
    def _validate_locator_types(
        self,
        script_content,
        locator_metadata
    ):

        method_pattern = re.compile(
            r"(fillField|typeText|clickElement|"
            r"selectOption|isVisible|getText|"
            r"scrollToElement|checkElement|"
            r"uncheckElement|hoverElement|"
            r"waitForElement|pressKey)"
            r"\(\s*['\"]([A-Za-z0-9_$-]+)['\"]"
        )

        type_errors = []

        fill_types = {
            "input",
            "textarea",
            "contenteditable"
        }

        click_types = {
            "button",
            "a",
            "link",
            "anchor",
            "checkbox",
            "radio",
            "clickable input"
        }

        select_types = {
            "select",
            "dropdown"
        }

        check_types = {
            "checkbox",
            "radio"
        }

        for method_name, locator_name in (
            method_pattern.findall(
                str(script_content)
            )
        ):

            # Missing locator names are handled by
            # FailureAgent self-healing at runtime.
            if locator_name not in locator_metadata:
                continue

            metadata = locator_metadata.get(
                locator_name,
                {}
            )

            if not isinstance(metadata, dict):
                continue

            element_type = str(
                metadata.get(
                    "type",
                    "unknown"
                )
            ).lower().strip()

            if (
                method_name
                in {
                    "fillField",
                    "typeText"
                }
                and element_type
                not in fill_types
            ):
                type_errors.append(
                    f"{method_name}('{locator_name}') "
                    f"cannot use type={element_type}"
                )

            elif (
                method_name == "clickElement"
                and element_type
                not in click_types
            ):
                type_errors.append(
                    f"clickElement('{locator_name}') "
                    f"cannot use type={element_type}"
                )

            elif (
                method_name == "selectOption"
                and element_type
                not in select_types
            ):
                type_errors.append(
                    f"selectOption('{locator_name}') "
                    f"cannot use type={element_type}"
                )

            elif (
                method_name
                in {
                    "checkElement",
                    "uncheckElement"
                }
                and element_type
                not in check_types
            ):
                type_errors.append(
                    f"{method_name}('{locator_name}') "
                    f"cannot use type={element_type}"
                )

        type_errors = sorted(
            set(type_errors)
        )

        if type_errors:

            print(
                "\nWARNING: AI generated incompatible "
                "locator and method combinations:"
            )

            for error in type_errors:
                print(
                    f"- {error}"
                )

            print(
                "Execution will continue so runtime "
                "failure analysis can process the issue."
            )

        return type_errors

    # ==================================================
    # VALIDATE PAGE OBJECT METHODS
    # ==================================================
    def _validate_page_object_methods(
        self,
        script_content,
        available_methods
    ):

        used_methods = re.findall(
            r"\bpageObject\."
            r"([A-Za-z_$][\w$]*)\s*\(",
            str(script_content)
        )

        available_method_set = set(
            available_methods
        )

        invalid_methods = sorted(
            {
                method_name
                for method_name in used_methods
                if method_name
                not in available_method_set
            }
        )

        if invalid_methods:

            print(
                "\nWARNING: AI generated Page Object "
                "methods that are not currently available:"
            )

            for method_name in invalid_methods:
                print(
                    f"- {method_name}"
                )

            print(
                "Execution will continue so the "
                "FailureAgent can analyze the issue."
            )

        return invalid_methods

    # ==================================================
    # NORMALIZE GENERATED SCRIPT
    # ==================================================
    def _normalize_generated_script(
        self,
        response,
        url,
        username,
        password
    ):

        response = (
            str(response)
            .replace(
                "```javascript",
                ""
            )
            .replace(
                "```js",
                ""
            )
            .replace(
                "```",
                ""
            )
            .strip()
        )

        # Convert encoded HTML entities without damaging
        # valid JavaScript comparison operators.
        response = html.unescape(
            response
        )

        # Remove accidental HTML anchor tags while keeping
        # their displayed URL or text.
        response = re.sub(
            r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>'
            r'.*?</a>',
            r"\1",
            response,
            flags=re.IGNORECASE | re.DOTALL
        )

        response = re.sub(
            r"<br\s*/?>",
            "\n",
            response,
            flags=re.IGNORECASE
        )

        response = response.replace(
            "process.env.URL",
            self._javascript_string(
                url
            )
        )

        response = response.replace(
            "process.env.USERNAME",
            self._javascript_string(
                username
            )
        )

        response = response.replace(
            "process.env.EMAIL",
            self._javascript_string(
                username
            )
        )

        response = response.replace(
            "process.env.PASSWORD",
            self._javascript_string(
                password
            )
        )

        # Normalize inconsistent Page Object variable names.
        response = re.sub(
            r"\b(?:"
            r"loginPage|"
            r"registrationPage|"
            r"dashboardPage|"
            r"searchPage|"
            r"productPage|"
            r"cartPage|"
            r"homePage|"
            r"po"
            r")\.",
            "pageObject.",
            response
        )

        # Normalize unsupported custom helper calls.
        response = re.sub(
            r"pageObject\.clickLoginButton\("
            r"(?:[^)]*)\)",
            "pageObject.clickElement('loginButton')",
            response
        )

        response = re.sub(
            r"pageObject\.fillUserName\("
            r"([^)]+)\)",
            r"pageObject.fillField('username', \1)",
            response
        )

        response = re.sub(
            r"pageObject\.fillPassword\("
            r"([^)]+)\)",
            r"pageObject.fillField('password', \1)",
            response
        )

        response = re.sub(
            r"pageObject\.isErrorMessageVisible\(\)",
            "pageObject.isVisible('errorMessage')",
            response
        )

        return response.strip()

    # ==================================================
    # NORMALIZE PAGE OBJECT IMPORT
    # ==================================================
    def _normalize_page_object_import(
        self,
        response,
        page_name
    ):

        safe_page_name = Path(
            str(page_name)
        ).name

        import_pattern = re.compile(
            r"(?m)^"
            r"\s*const\s+"
            r"[A-Za-z_$][\w$]*\s*=\s*"
            r"require\(['\"]"
            r"\.\./pages/[^'\"]+"
            r"['\"]\)\s*;?\s*$"
        )

        expected_import = (
            "const PageObject = "
            f"require('../pages/{safe_page_name}');"
        )

        if import_pattern.search(
            response
        ):

            response = import_pattern.sub(
                expected_import,
                response,
                count=1
            )

        elif expected_import not in response:

            playwright_import_pattern = re.compile(
                r"(?m)^"
                r"\s*const\s*\{\s*test\s*,\s*expect\s*\}"
                r"\s*=\s*require\("
                r"['\"]@playwright/test['\"]"
                r"\)\s*;?\s*$"
            )

            match = (
                playwright_import_pattern.search(
                    response
                )
            )

            if match:

                insertion_position = (
                    match.end()
                )

                response = (
                    response[:insertion_position]
                    + "\n"
                    + expected_import
                    + response[insertion_position:]
                )

            else:

                response = (
                    "const { test, expect } = "
                    "require('@playwright/test');\n"
                    + expected_import
                    + "\n"
                    + response
                )

        return response

    # ==================================================
    # REMOVE DUPLICATE SCREENSHOT HOOKS
    # ==================================================
    def _remove_duplicate_after_each_blocks(
        self,
        response
    ):
        after_each_pattern = re.compile(
            r"test\.afterEach\s*\("
            r"[\s\S]*?"
            r"\n\s*\}\s*\);",
            flags=re.MULTILINE
        )

        matches = list(after_each_pattern.finditer(response))

        if len(matches) <= 1:
            return response

        first_match = matches[0]

        cleaned_response = response[:first_match.end()]

        remaining_text = response[first_match.end():]

        remaining_text = after_each_pattern.sub("", remaining_text)

        return cleaned_response + remaining_text

    # =====================*============================
    #*GENERATE PLAYWRIGHT SCRIPT
    # =*==================================*=============
    def generate_playwright_script(
        self,
       requirement,
        testcases,
        runtime_data=None,
        locators=None,
        page_object_content="",
        page_name="PageObject"
    ):
        runtime_data = runtime_data or {}

        requirement = self.clean_html(
            requirement
        )

        url = self.clean_html(
            runtime_data.get(
                "url",
               (
                    "https://opensource-demo."
                   "orangehrmlive.com/"
               )
            )
        )

        username = self.clean_html(
            runtime_data.get(
               "login_credential",
             runtime_data.get(
                  "username",
                   runtime_data.get(
                       "email",
                      "Admin"
                 )
                )
          )
        )

        password = self.clean_html(
            runtime_data.get(
                "password",
                "admin123"
            )
        )

        search_keyword = self.clean_html(
            runtime_data.get(
                "search_keyword",
                ""
            )
        )

        expected_search_result = self.clean_html(
            runtime_data.get(
                "expected_search_result",
                ""
            )
        )

        available_methods = re.findall(
            r"async\s+"
            r"([A-Za-z_$][\w$]*)"
            r"\s*\(",
            str(page_object_content)
        )

        methods_text = "\n".join(
            f"- {method}"
            for method in available_methods
        )

        if not methods_text:
            methods_text = (
                "NO PAGE OBJECT METHODS AVAILABLE"
            )

        (
            locator_metadata,
            available_locators,
            locators_text
        ) = self._format_locator_metadata(locators)

        prompt = f"""
Generate a complete, runnable Playwright JavaScript test specification.

REQUIREMENT:
{requirement}

TEST CASES:
{testcases}

RUNTIME DATA:

URL:
{url}

LOGIN CREDENTIAL:
{username}

PASSWORD:
{password}

SEARCH KEYWORD:
{search_keyword}

EXPECTED SEARCH RESULT:
{expected_search_result}

AVAILABLE PAGE OBJECT METHODS:
{methods_text}

AVAILABLE PAGE OBJECT LOCATOR METADATA:
{locators_text}

Each locator entry contains:

- name: Exact locator name allowed in Page Object methods.
- type: Element type for selecting the correct method.
- locator: Existing locator expression for reference only.
- priority: Locator preference ranking.
- options: Dropdown options when applicable.
- state: Page state where the locator was found.
- pageUrl: URL where the locator was found.

Use the exact value from the name field whenever available.

Never copy locator expressions into the generated test script.

Never pass raw locator expressions to Page Object methods.


STRICT LOCATOR RULES:

1. Prefer exact locator names from AVAILABLE PAGE OBJECT LOCATOR
   METADATA.

2. Existing locator names are case-sensitive.

3. Never rename, translate, or create synonyms for an existing
   locator name.

4. Never substitute an unrelated locator.

5. Never pass CSS selectors, XPath expressions, IDs, classes,
   element text, or raw Playwright locators to Page Object
   methods.

6. If a required later-page locator is unavailable:

   - Do not substitute an unrelated locator.
   - Do not pass raw CSS or XPath.
   - Generate one clear semantic locator name.
   - Use camelCase only.
   - The name must describe its purpose and element type.
   - Runtime FailureAgent will discover and heal it.

   Valid semantic names include:

   loginEmail
   loginPassword
   loginButton
   logoutLink
   searchProduct
   searchProductInput
   submitSearch
   searchedProductList
   cartBadge
   productsContainer
   errorMessage

   Never use snake_case names such as:

   login_email
   login_password
   search_product
   submit_search

7. Do not generate different locator names for the same element.

8. If no locators are available, generate only navigation and
   test setup code.


ELEMENT TYPE RULES:

1. fillField() and typeText() may use only:

   - input
   - textarea
   - contenteditable

2. clickElement() may use only:

   - button
   - link
   - anchor
   - a
   - checkbox
   - radio
   - clickable input

3. selectOption() may use only:

   - select
   - dropdown

4. checkElement() and uncheckElement() may use only:

   - checkbox
   - radio

5. isVisible(), getText(), scrollToElement(), hoverElement(),
   waitForElement(), and pressKey() may use any valid locator.

6. Never call fillField() or typeText() on a button or link.

7. Never call selectOption() on a normal input, button, link,
   checkbox, or radio.

8. Never call clickElement() on a normal text input unless the
   requirement explicitly requires clicking or focusing it.

9. Verify the locator name and element type before generating
   every interaction.


VALID LOCATOR USAGE:

If locator metadata contains:

- name=userName | type=input
- name=password | type=input
- name=loginButton | type=button

Valid usage:

await pageObject.fillField(
    'userName',
    {self._javascript_string(username)}
);

await pageObject.fillField(
    'password',
    {self._javascript_string(password)}
);

await pageObject.clickElement(
    'loginButton'
);

Invalid usage:

await pageObject.fillField(
    'loginButton',
    {self._javascript_string(username)}
);

await pageObject.isVisible(
    '.inventory_list'
);

await pageObject.clickElement(
    '#login-button'
);


PAGE OBJECT METHOD RULES:

1. Use methods from AVAILABLE PAGE OBJECT METHODS.

2. Prefer generic methods:

   - navigate()
   - fillField()
   - typeText()
   - clickElement()
   - selectOption()
   - checkElement()
   - uncheckElement()
   - isVisible()
   - getText()
   - scrollToElement()
   - scrollToTop()
   - scrollToBottom()
   - scrollByPixels()
   - hoverElement()
   - pressKey()
   - waitForElement()

3. Do not generate custom helper methods such as:

   - fillUserName()
   - fillPassword()
   - clickLoginButton()
   - enterSearchQuery()
   - verifySearchResults()

4. Always use this Page Object variable name:

pageObject

5. Do not switch between pageObject, loginPage, po,
   registrationPage, productPage, cartPage, homePage,
   or dashboardPage.

6. All element interactions must use Page Object methods.

7. Direct page usage is allowed only for:

   - page.goto()
   - page.waitForLoadState()
   - page.screenshot()


SCROLL RULES:

1. If an element may be outside the viewport and
   scrollToElement() exists, use:

await pageObject.scrollToElement(
    '<exactLocatorName>'
);

2. Use an available exact locator name whenever possible.

3. Do not generate scrollToElement() when it is not listed in
   AVAILABLE PAGE OBJECT METHODS.


RUNTIME DATA RULES:

1. Use this exact URL:

{url}

2. Use this exact login credential:

{username}

3. Use this exact password:

{password}

4. Use this search keyword when the requirement contains search:

{search_keyword}

5. Use this expected search result when applicable:

{expected_search_result}

6. Never use:

   - process.env.URL
   - process.env.USERNAME
   - process.env.EMAIL
   - process.env.PASSWORD

7. Do not create placeholder credentials.

8. Do not modify runtime values.

9. The URL must remain a plain URL.

10. Never include HTML anchor tags in the URL.


JAVASCRIPT AND PLAYWRIGHT RULES:

1. Generate syntactically valid JavaScript.

2. Use CommonJS syntax.

3. Import Playwright exactly as:

const {{ test, expect }} =
require('@playwright/test');

4. Import the Page Object exactly as:

const PageObject =
require('../pages/{page_name}');

5. Use test.describe().

6. Generate tests for all supplied test cases.

7. Use async/await for asynchronous operations.

8. Instantiate the Page Object exactly as:

const pageObject =
new PageObject(page);

9. When navigate() exists in AVAILABLE PAGE OBJECT METHODS,
   navigate using:

await pageObject.navigate(
    {self._javascript_string(url)}
);

10. If navigate() is unavailable, use:

await page.goto(
    {self._javascript_string(url)},
    {{
        waitUntil: 'domcontentloaded'
    }}
);

await page.waitForLoadState(
    'load'
);

11. Do not use direct locator APIs:

   - page.locator()
   - page.$()
   - page.$$()
   - page.getByRole()
   - page.getByText()
   - page.getByLabel()
   - page.getByPlaceholder()
   - page.getByTestId()
   - xpath=

12. Never pass raw selectors to Page Object methods.

13. Generate assertions only through Page Object methods.

14. Do not use CSS selectors directly in assertions.


SCREENSHOT RULES:

Generate exactly one test.afterEach() block inside the
test.describe() block.

Capture a screenshot only when the test fails.

Use exactly:

test.afterEach(
    async ({{ page }}, testInfo) => {{

        if (
            testInfo.status !==
            testInfo.expectedStatus
        ) {{

            const timestamp = new Date()
                .toISOString()
                .replace(/[:.]/g, '-');

            const safeTitle = testInfo.title
                .replace(/[^a-zA-Z0-9_-]/g, '_');

            await page.screenshot({{
                path:
                    `Agent_AUTOMATION_AI/generated/screenshots/${{safeTitle}}_${{timestamp}}.png`,
                fullPage: true
            }});

        }}

    }}
);

Do not generate more than one test.afterEach() block.


FINAL OUTPUT RULES:

1. Return executable JavaScript only.

2. Do not return Markdown fences.

3. Do not return explanations.

4. Do not return comments.

5. Do not return HTML.

6. Do not return encoded HTML entities.

7. Do not return hyperlinks or HTML anchor tags.

8. Do not include text outside JavaScript.

9. Before returning, verify:

   - Page Object variable names are consistent.
   - Existing locator names are used exactly.
   - Missing later-page locator names use camelCase.
   - Locator types match methods where metadata exists.
   - Raw selectors are not used.
   - URL is plain text.
   - JavaScript syntax is valid.
"""

        response = self.ai.ask_ai(
            prompt
        )

        response = (
            self._normalize_generated_script(
                response=response,
                url=url,
                username=username,
                password=password
            )
        )

        response = (
            self._normalize_page_object_import(
                response=response,
                page_name=page_name
            )
        )

        response = (
            self._remove_duplicate_after_each_blocks(
                response
            )
        )

        invalid_methods = (
            self._validate_page_object_methods(
                response,
                available_methods
            )
        )

        invalid_locators = (
            self._validate_locator_names(
                response,
                available_locators
            )
        )

        type_errors = (
            self._validate_locator_types(
                response,
                locator_metadata
            )
        )

        if (
            invalid_methods
            or invalid_locators
            or type_errors
        ):

            print(
                "\nGenerated script contains items "
                "that may require runtime self-healing."
            )

        return response

    # ==================================================
    # SAVE GENERATED SCRIPT
    # ==================================================
    def save_script(
        self,
        script_content,
        feature_name="Automation"
    ):

        safe_name = "".join(
            character
            for character in str(
                feature_name
            )
            if character.isalnum()
        )

        if not safe_name:
            safe_name = "Automation"

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        file_name = (
            f"{safe_name}_{timestamp}.spec.js"
        )

        output_dir = (
            Path(__file__).resolve().parent
            / "generated"
            / "tests"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        script_path = (
            output_dir
            / file_name
        )

        script_content = str(
            script_content
        ).strip()

        if not script_content:

            raise ValueError(
                "Cannot save an empty "
                "Playwright script."
            )

        script_path.write_text(
            script_content + "\n",
            encoding="utf-8"
        )

        saved_content = script_path.read_text(
            encoding="utf-8"
        )

        if not saved_content.strip():

            raise ValueError(
                "Saved Playwright script is empty."
            )

        print(
            f"Generated Script: {file_name}"
        )

        return str(
            script_path
        )