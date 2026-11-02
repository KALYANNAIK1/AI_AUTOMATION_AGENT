import html
import json
import re
from pathlib import Path

from .ai_agent import AIAgent


class PageObjectAgent:

    def __init__(self):
        self.ai = AIAgent()

    # ==================================================
    # HTML CLEANUP
    # ==================================================
    def clean_html(
        self,
        text
    ):

        if text is None:
            return ""

        text = html.unescape(
            str(text)
        )

        href_match = re.search(
            r'<a\b[^>]*\bhref=["\']'
            r'([^"\']+)'
            r'["\'][^>]*>',
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
    # SAFE PROPERTY NAME
    # ==================================================
    def _sanitize_property_name(
        self,
        value
    ):

        if not value:
            return ""

        value = html.unescape(
            str(value).strip()
        )

        # Underscores and special characters are treated
        # as word separators to generate camelCase names.
        words = re.findall(
            r"[A-Za-z0-9]+",
            value
        )

        if not words:
            return ""

        safe_name = (
            words[0][:1].lower()
            + words[0][1:]
            + "".join(
                word[:1].upper()
                + word[1:]
                for word in words[1:]
            )
        )

        safe_name = re.sub(
            r"[^A-Za-z0-9_$]",
            "",
            safe_name
        )

        if not safe_name:
            return ""

        if safe_name[0].isdigit():
            safe_name = (
                "item"
                + safe_name
            )

        return safe_name

    # ==================================================
    # NORMALIZE LOCATOR INPUT
    # ==================================================
    def _normalize_locators(
        self,
        locators
    ):

        if not isinstance(
            locators,
            dict
        ):
            return {}

        if (
            "locators" in locators
            and isinstance(
                locators.get("locators"),
                dict
            )
        ):
            return locators.get(
                "locators",
                {}
            )

        return locators

    # ==================================================
    # VALIDATE LOCATOR EXPRESSION
    # ==================================================
    def _is_valid_locator_expression(
        self,
        locator_expression
    ):

        if not locator_expression:
            return False

        locator_expression = str(
            locator_expression
        ).strip()

        allowed_prefixes = (
            "page.locator(",
            "page.getByRole(",
            "page.getByText(",
            "page.getByLabel(",
            "page.getByPlaceholder(",
            "page.getByTestId(",
            "page.getByAltText(",
            "page.getByTitle("
        )

        return locator_expression.startswith(
            allowed_prefixes
        )

    # ==================================================
    # GENERATE LOCATOR DECLARATIONS
    # ==================================================
    def _generate_locator_lines(
        self,
        locators
    ):

        locator_metadata = (
            self._normalize_locators(
                locators
            )
        )

        ignored_keys = {
            "_token",
            "token",
            "csrfmiddlewaretoken"
        }

        used_names = set()
        locator_lines = []
        accepted_metadata = {}

        for original_key, metadata in (
            locator_metadata.items()
        ):

            safe_key = (
                self._sanitize_property_name(
                    original_key
                )
            )

            if not safe_key:
                continue

            if safe_key.lower() in ignored_keys:
                continue

            if safe_key in used_names:
                continue

            if not isinstance(
                metadata,
                dict
            ):
                metadata = {
                    "locator": metadata,
                    "type": "unknown",
                    "priority": 99,
                    "options": []
                }

            locator_expression = (
                self.clean_html(
                    metadata.get(
                        "locator",
                        ""
                    )
                )
            )

            if not self._is_valid_locator_expression(
                locator_expression
            ):

                print(
                    "Skipping invalid locator "
                    f"expression for '{safe_key}': "
                    f"{locator_expression}"
                )

                continue

            locator_lines.append(
                f"        this.{safe_key} = "
                f"{locator_expression};"
            )

            accepted_metadata[safe_key] = {
                "locator": locator_expression,
                "type": metadata.get(
                    "type",
                    "unknown"
                ),
                "priority": metadata.get(
                    "priority",
                    99
                ),
                "options": metadata.get(
                    "options",
                    []
                ),
                "state": metadata.get(
                    "state",
                    "unknown"
                ),
                "page_url": self.clean_html(
                    metadata.get(
                        "page_url",
                        ""
                    )
                )
            }

            used_names.add(
                safe_key
            )

        return (
            locator_lines,
            accepted_metadata
        )

    # ==================================================
    # GENERIC JAVASCRIPT METHODS
    # ==================================================
    def _generate_generic_methods(
        self
    ):

        return """
    async waitForPageReady(
        timeout = this.navigationTimeout
    ) {

        await this.page.waitForLoadState(
            'domcontentloaded',
            {
                timeout
            }
        );

        try {

            await this.page.waitForLoadState(
                'load',
                {
                    timeout
                }
            );

        } catch (error) {

            // Some applications continuously load
            // analytics or background resources.
        }
    }


    async navigate(
        url,
        timeout = this.navigationTimeout
    ) {

        await this.page.goto(
            url,
            {
                waitUntil: 'domcontentloaded',
                timeout
            }
        );

        await this.waitForPageReady(
            timeout
        );
    }


    async waitForElement(
        locatorName,
        timeout = this.defaultTimeout
    ) {

        const locator =
            this._resolveLocator(
                locatorName
            );

        if (!locator) {
            throw new Error(
                `Unknown page locator: ${locatorName}`
            );
        }

        const target =
            locator.first();

        await target.waitFor({
            state: 'visible',
            timeout
        });

        return target;
    }


    async waitForElementAttached(
        locatorName,
        timeout = this.defaultTimeout
    ) {

        const locator =
            this._resolveLocator(
                locatorName
            );

        if (!locator) {
            throw new Error(
                `Unknown page locator: ${locatorName}`
            );
        }

        const target =
            locator.first();

        await target.waitFor({
            state: 'attached',
            timeout
        });

        return target;
    }


    async waitForElementHidden(
        locatorName,
        timeout = this.defaultTimeout
    ) {

        const locator =
            this._resolveLocator(
                locatorName
            );

        if (!locator) {
            throw new Error(
                `Unknown page locator: ${locatorName}`
            );
        }

        await locator
            .first()
            .waitFor({
                state: 'hidden',
                timeout
            });

        return true;
    }


    async waitForUrl(
        urlPattern,
        timeout = this.navigationTimeout
    ) {

        await this.page.waitForURL(
            urlPattern,
            {
                timeout
            }
        );

        await this.waitForPageReady(
            timeout
        );

        return true;
    }


    async clickElement(
        locatorName,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElement(
                locatorName,
                timeout
            );

        await target.scrollIntoViewIfNeeded();

        await target.click({
            timeout
        });
    }


    async fillField(
        locatorName,
        value,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElement(
                locatorName,
                timeout
            );

        await target.scrollIntoViewIfNeeded();

        await target.fill(
            String(value),
            {
                timeout
            }
        );
    }


    async typeText(
        locatorName,
        value,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElement(
                locatorName,
                timeout
            );

        await target.scrollIntoViewIfNeeded();

        await target.fill(
            String(value),
            {
                timeout
            }
        );
    }


    async selectOption(
        locatorName,
        value,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElement(
                locatorName,
                timeout
            );

        await target.scrollIntoViewIfNeeded();

        return await target.selectOption(
            value,
            {
                timeout
            }
        );
    }


    async checkElement(
        locatorName,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElement(
                locatorName,
                timeout
            );

        await target.scrollIntoViewIfNeeded();

        await target.check({
            timeout
        });
    }


    async uncheckElement(
        locatorName,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElement(
                locatorName,
                timeout
            );

        await target.scrollIntoViewIfNeeded();

        await target.uncheck({
            timeout
        });
    }


    async isChecked(
        locatorName,
        timeout = this.assertionTimeout
    ) {

        try {

            const target =
                await this.waitForElement(
                    locatorName,
                    timeout
                );

            const startTime =
                Date.now();

            while (
                Date.now() - startTime
                < timeout
            ) {

                if (
                    await target.isChecked()
                ) {
                    return true;
                }

                await this.page.waitForTimeout(
                    250
                );
            }

            return false;

        } catch (error) {

            return false;
        }
    }


    async getText(
        locatorName,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElement(
                locatorName,
                timeout
            );

        const text =
            await target.textContent();

        return String(
            text || ''
        ).trim();
    }


    async isVisible(
        locatorName,
        timeout = this.assertionTimeout
    ) {

        const locator =
            this._resolveLocator(
                locatorName
            );

        if (!locator) {
            throw new Error(
                `Unknown page locator: ${locatorName}`
            );
        }

        try {

            await locator
                .first()
                .waitFor({
                    state: 'visible',
                    timeout
                });

            return true;

        } catch (error) {

            return false;
        }
    }


    async hasText(
        locatorName,
        expectedText,
        timeout = this.assertionTimeout
    ) {

        const locator =
            this._resolveLocator(
                locatorName
            );

        if (!locator) {
            throw new Error(
                `Unknown page locator: ${locatorName}`
            );
        }

        const target =
            locator.first();

        try {

            await target.waitFor({
                state: 'visible',
                timeout
            });

            const expected =
                String(expectedText);

            const startTime =
                Date.now();

            while (
                Date.now() - startTime
                < timeout
            ) {

                const actualText =
                    String(
                        await target.textContent()
                        || ''
                    );

                if (
                    actualText.includes(
                        expected
                    )
                ) {
                    return true;
                }

                await this.page.waitForTimeout(
                    300
                );
            }

            return false;

        } catch (error) {

            return false;
        }
    }


    async hasExactText(
        locatorName,
        expectedText,
        timeout = this.assertionTimeout
    ) {

        const locator =
            this._resolveLocator(
                locatorName
            );

        if (!locator) {
            throw new Error(
                `Unknown page locator: ${locatorName}`
            );
        }

        const target =
            locator.first();

        try {

            await target.waitFor({
                state: 'visible',
                timeout
            });

            const expected =
                String(expectedText).trim();

            const startTime =
                Date.now();

            while (
                Date.now() - startTime
                < timeout
            ) {

                const actualText =
                    String(
                        await target.textContent()
                        || ''
                    ).trim();

                if (
                    actualText === expected
                ) {
                    return true;
                }

                await this.page.waitForTimeout(
                    300
                );
            }

            return false;

        } catch (error) {

            return false;
        }
    }


    async waitForText(
        locatorName,
        expectedText,
        timeout = this.assertionTimeout
    ) {

        const hasExpectedText =
            await this.hasText(
                locatorName,
                expectedText,
                timeout
            );

        if (!hasExpectedText) {

            throw new Error(
                `Expected text "${expectedText}" `
                + `was not found in locator: `
                + `${locatorName}`
            );
        }

        return true;
    }


    async scrollToElement(
        locatorName,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElementAttached(
                locatorName,
                timeout
            );

        await target.scrollIntoViewIfNeeded();
    }


    async scrollToTop() {

        await this.page.evaluate(
            () => {
                window.scrollTo(
                    0,
                    0
                );
            }
        );
    }


    async scrollToBottom() {

        await this.page.evaluate(
            () => {
                window.scrollTo(
                    0,
                    document.body.scrollHeight
                );
            }
        );
    }


    async scrollByPixels(
        pixels
    ) {

        await this.page.evaluate(
            (value) => {
                window.scrollBy(
                    0,
                    value
                );
            },
            pixels
        );
    }


    async hoverElement(
        locatorName,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElement(
                locatorName,
                timeout
            );

        await target.scrollIntoViewIfNeeded();

        await target.hover({
            timeout
        });
    }


    async pressKey(
        locatorName,
        key,
        timeout = this.defaultTimeout
    ) {

        const target =
            await this.waitForElement(
                locatorName,
                timeout
            );

        await target.press(
            key,
            {
                timeout
            }
        );
    }
    async clickAndSwitchToNewTab(
    locatorName,
    timeout = this.navigationTimeout
) {
    const target =
        await this.waitForElement(
            locatorName,
            timeout
        );

    const [
        newPage
    ] = await Promise.all([
        this.page.context().waitForEvent(
            'page',
            {
                timeout
            }
        ),

        target.click({
            timeout
        })
    ]);

    await newPage.waitForLoadState(
        'domcontentloaded',
        {
            timeout
        }
    );

    this.parentPage =
        this.page;

    this.page =
        newPage;

    return newPage;
}


async switchToTabByUrl(
    expectedUrl,
    timeout = this.navigationTimeout
) {
    const expected =
        String(expectedUrl);

    const startTime =
        Date.now();

    while (
        Date.now() - startTime
        < timeout
    ) {
        const pages =
            this.page.context().pages();

        for (
            const openPage
            of pages
        ) {
            if (
                openPage.url().includes(
                    expected
                )
            ) {
                this.page =
                    openPage;

                await this.page.bringToFront();

                return true;
            }
        }

        await this.page.waitForTimeout(
            250
        );
    }

    return false;
}


async switchToTabByTitle(
    expectedTitle,
    timeout = this.navigationTimeout
) {
    const expected =
        String(expectedTitle);

    const startTime =
        Date.now();

    while (
        Date.now() - startTime
        < timeout
    ) {
        const pages =
            this.page.context().pages();

        for (
            const openPage
            of pages
        ) {
            const title =
                await openPage.title();

            if (
                title.includes(
                    expected
                )
            ) {
                this.page =
                    openPage;

                await this.page.bringToFront();

                return true;
            }
        }

        await this.page.waitForTimeout(
            250
        );
    }

    return false;
}


async switchToParentTab() {
    if (
        !this.parentPage
        || this.parentPage.isClosed()
    ) {
        throw new Error(
            'Parent browser tab is not available.'
        );
    }

    this.page =
        this.parentPage;

    await this.page.bringToFront();

    return true;
}


async closeCurrentTab() {
    if (
        this.page.isClosed()
    ) {
        return true;
    }

    await this.page.close();

    if (
        this.parentPage
        && !this.parentPage.isClosed()
    ) {
        this.page =
            this.parentPage;

        await this.page.bringToFront();
    }

    return true;
}


async getOpenTabCount() {
    return this.page
        .context()
        .pages()
        .filter(
            openPage =>
                !openPage.isClosed()
        )
        .length;
}


    async getCurrentUrl() {

        return this.page.url();
    }


    async urlContains(
        expectedValue,
        timeout = this.assertionTimeout
    ) {

        const expected =
            String(expectedValue);

        const startTime =
            Date.now();

        while (
            Date.now() - startTime
            < timeout
        ) {

            const currentUrl =
                this.page.url();

            if (
                currentUrl.includes(
                    expected
                )
            ) {
                return true;
            }

            await this.page.waitForTimeout(
                300
            );
        }

        return false;
    }
"""

    # ==================================================
    # GENERATE PAGE OBJECT
    # ==================================================
    def generate_page_object(
        self,
        requirement,
        locators=None
    ):

        requirement = self.clean_html(
            requirement
        )

        (
            locator_lines,
            accepted_metadata
        ) = self._generate_locator_lines(
            locators
        )

        if not locator_lines:

            locator_block = (
                "        // No valid locators "
                "were extracted."
            )

        else:

            locator_block = "\n".join(
                locator_lines
            )

        generic_methods = (
            self._generate_generic_methods()
        )

        page_object = f"""
class PageObject {{

    constructor(page) {{

        this.page = page;

        this.defaultTimeout = 20000;
        this.navigationTimeout = 30000;
        this.assertionTimeout = 15000;

        this._resolveLocator = (
            locatorName
        ) => {{

            if (!locatorName) {{
                return null;
            }}

            if (this[locatorName]) {{
                return this[locatorName];
            }}

            const normalized = String(
                locatorName
            )
                .toLowerCase()
                .replace(
                    /[^a-z0-9]/g,
                    ''
                );

            for (
                const propertyName
                of Object.keys(this)
            ) {{

                if (
                    propertyName === 'page'
                    || propertyName ===
                        '_resolveLocator'
                    || propertyName ===
                        'defaultTimeout'
                    || propertyName ===
                        'navigationTimeout'
                    || propertyName ===
                        'assertionTimeout'
                ) {{
                    continue;
                }}

                const candidate = propertyName
                    .toLowerCase()
                    .replace(
                        /[^a-z0-9]/g,
                        ''
                    );

                if (
                    candidate === normalized
                ) {{
                    return this[propertyName];
                }}

            }}

            const semanticButtonName = String(
                locatorName
            ).match(/^(.+?)Button$/i);

            if (semanticButtonName) {{
                const buttonName = semanticButtonName[1]
                    .replace(
                        /([a-z0-9])([A-Z])/g,
                        '$1 $2'
                    )
                    .replace(
                        /[_-]+/g,
                        ' '
                    )
                    .trim();

                if (buttonName) {{
                    const accessibleName =
                        buttonName[0].toUpperCase()
                        + buttonName.slice(1);

                    return this.page.getByRole(
                        'button',
                        {{
                            name: accessibleName,
                            exact: true
                        }}
                    );
                }}
            }}

            return null;
        }};

{locator_block}

    }}

{generic_methods}

}}

module.exports = PageObject;
"""

        page_object = (
            page_object.strip()
            + "\n"
        )

        self._validate_generated_page_object(
            page_object,
            accepted_metadata
        )

        return page_object

    # ==================================================
    # BASIC GENERATED PAGE OBJECT VALIDATION
    # ==================================================
    def _validate_generated_page_object(
        self,
        page_object,
        locator_metadata
    ):

        if not page_object.strip():

            raise ValueError(
                "Generated Page Object is empty."
            )

        required_fragments = [
            "class PageObject",
            "constructor(page)",
            "this.page = page",
            "this.defaultTimeout = 20000",
            "this.navigationTimeout = 30000",
            "this.assertionTimeout = 15000",
            "this._resolveLocator",
            "async waitForPageReady",
            "async clickElement",
            "async fillField",
            "async isVisible",
            "async hasText",
            "async waitForUrl",
            "module.exports = PageObject"
        ]

        missing_fragments = [
            fragment
            for fragment in required_fragments
            if fragment not in page_object
        ]

        if missing_fragments:

            raise ValueError(
                "Generated Page Object is missing: "
                + ", ".join(
                    missing_fragments
                )
            )

        duplicate_properties = []

        property_names = re.findall(
            r"this\.([A-Za-z_$][\w$]*)\s*=",
            page_object
        )

        seen = set()

        ignored_properties = {
            "page",
            "_resolveLocator",
            "defaultTimeout",
            "navigationTimeout",
            "assertionTimeout"
        }

        for property_name in property_names:

            if property_name in ignored_properties:
                continue

            if property_name in seen:

                duplicate_properties.append(
                    property_name
                )

            seen.add(
                property_name
            )

        if duplicate_properties:

            raise ValueError(
                "Duplicate Page Object properties: "
                + ", ".join(
                    sorted(
                        set(
                            duplicate_properties
                        )
                    )
                )
            )

        for locator_name in locator_metadata:

            declaration = (
                f"this.{locator_name} ="
            )

            if declaration not in page_object:

                raise ValueError(
                    "Locator declaration was not "
                    f"generated: {locator_name}"
                )

    # ==================================================
    # LOAD LOCATORS
    # ==================================================
    def load_locators(
        self,
        locator_file
    ):

        locator_path = Path(
            locator_file
        )

        if not locator_path.exists():

            raise FileNotFoundError(
                f"Locator file not found: "
                f"{locator_path}"
            )

        with locator_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            loaded_data = json.load(
                file
            )

        if (
            isinstance(
                loaded_data,
                dict
            )
            and isinstance(
                loaded_data.get(
                    "locators"
                ),
                dict
            )
        ):

            return loaded_data.get(
                "locators",
                {}
            )

        return loaded_data

    # ==================================================
    # SAVE PAGE OBJECT
    # ==================================================
    def save_page_object(
        self,
        page_content,
        page_name="PageObject.js"
    ):

        output_dir = (
            Path(__file__).resolve().parent
            / "generated"
            / "pages"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        safe_page_name = Path(
            str(page_name)
        ).name

        if not safe_page_name.endswith(
            ".js"
        ):

            safe_page_name = (
                safe_page_name
                + ".js"
            )

        file_path = (
            output_dir
            / safe_page_name
        )

        page_content = str(
            page_content
        ).strip()

        if not page_content:

            raise ValueError(
                "Cannot save an empty "
                "Page Object."
            )

        self._validate_generated_page_object(
            page_content,
            {}
        )

        file_path.write_text(
            page_content.rstrip()
            + "\n",
            encoding="utf-8"
        )

        saved_content = file_path.read_text(
            encoding="utf-8"
        )

        if not saved_content.strip():

            raise ValueError(
                "Saved Page Object file "
                "is unexpectedly empty."
            )

        print(
            "Generated Page Object: "
            f"{safe_page_name}"
        )

        return str(
            file_path
        )

    # ==================================================
    # GENERATE PAGE OBJECT FILE NAME
    # ==================================================
    def generate_file_name(
        self,
        feature_name
    ):

        if not feature_name:
            return "PageObject.js"

        clean_name = "".join(
            character
            for character in str(
                feature_name
            )
            if character.isalnum()
        )

        if not clean_name:
            clean_name = "PageObject"

        if clean_name.endswith(
            "Page"
        ):
            return f"{clean_name}.js"

        return f"{clean_name}Page.js"