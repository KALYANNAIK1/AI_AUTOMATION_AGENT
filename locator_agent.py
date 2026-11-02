from pathlib import Path
import html
import json
import os
import re

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)


class LocatorAgent:

    def __init__(self):

        self.ignored_frame_domains = {
            "doubleclick.net",
            "googlesyndication.com",
            "googleads.g.doubleclick.net",
            "adtrafficquality.google",
            "google.com/recaptcha",
            "googleadservices.com"
        }

    # ==================================================
    # HTML AND URL CLEANUP
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

        href_match = re.search(
            r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>',
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

    def _normalize_url(
        self,
        value
    ):

        value = self.clean_html(
            value
        )

        match = re.search(
            r"https?://[^\s<>\"']+",
            value,
            flags=re.IGNORECASE
        )

        if not match:
            return None

        return match.group(0).rstrip(
            ".,);"
        )

    # ==================================================
    # SAFE JAVASCRIPT STRING
    # ==================================================
    def _js_string(
        self,
        value
    ):

        return json.dumps(
            str(value),
            ensure_ascii=False
        )

    # ==================================================
    # LOCATOR KEY SANITIZATION
    # ==================================================
    def _sanitize_key(
        self,
        value
    ):

        if not value:
            return ""

        value = html.unescape(
            str(value)
        )

        value = re.sub(
            r"[^a-zA-Z0-9_$ ]",
            " ",
            value
        )

        words = value.split()

        if not words:
            return ""

        key = (
            words[0].lower()
            + "".join(
                word[:1].upper()
                + word[1:]
                for word in words[1:]
            )
        )

        key = re.sub(
            r"[^a-zA-Z0-9_$]",
            "",
            key
        )

        if not key:
            return ""

        if key[0].isdigit():
            key = "item" + key

        return key

    def _unique_key(
        self,
        base_key,
        locators
    ):

        if base_key not in locators:
            return base_key

        number = 2

        while (
            f"{base_key}{number}"
            in locators
        ):
            number += 1

        return f"{base_key}{number}"

    def _logo_class_candidate(self, class_name):
        candidates = []
        for class_token in str(class_name or "").split():
            sanitized = self._sanitize_key(class_token)
            match = re.search(r"(?i)(header)?logo$", sanitized)
            if not match:
                continue
            key = "headerLogo" if match.group(1) else "logo"
            candidates.append((key, class_token))

        return next(
            (candidate for candidate in candidates if candidate[0] == "headerLogo"),
            candidates[0] if candidates else None,
        )

    # ==================================================
    # ELEMENT TYPE CLASSIFICATION
    # ==================================================
    def _classify_element_type(
        self,
        element,
        tag_name
    ):

        tag_name = str(
            tag_name or ""
        ).lower()

        input_type = str(
            element.get_attribute("type")
            or ""
        ).lower()

        role = str(
            element.get_attribute("role")
            or ""
        ).lower()

        if tag_name == "textarea":
            return "textarea"

        if tag_name == "select":
            return "select"

        if tag_name == "button":
            return "button"

        if tag_name == "a":
            return "a"

        if tag_name == "input":

            if input_type in {
                "submit",
                "button",
                "reset",
                "image"
            }:
                return "button"

            if input_type == "checkbox":
                return "checkbox"

            if input_type == "radio":
                return "radio"

            return "input"

        if role == "button":
            return "button"

        if role == "link":
            return "link"

        if role == "checkbox":
            return "checkbox"

        if role == "radio":
            return "radio"

        if role in {
            "combobox",
            "textbox",
            "searchbox"
        }:
            return "input"

        if (
            element.get_attribute(
                "contenteditable"
            )
            == "true"
        ):
            return "contenteditable"

        return tag_name or "unknown"

    def _get_priority(
        self,
        element_type
    ):

        return {
            "input": 1,
            "textarea": 2,
            "contenteditable": 2,
            "select": 3,
            "dropdown": 3,
            "button": 4,
            "checkbox": 4,
            "radio": 4,
            "a": 5,
            "link": 5,
            "anchor": 5
        }.get(
            element_type,
            99
        )

    # ==================================================
    # ELEMENT KEY GENERATION
    # ==================================================
    def _build_key(
        self,
        element,
        tag_name,
        element_type,
        index
    ):

        attributes = {
            "data_qa": element.get_attribute(
                "data-qa"
            ),
            "testid": element.get_attribute(
                "data-testid"
            ),
            "name": element.get_attribute(
                "name"
            ),
            "id": element.get_attribute(
                "id"
            ),
            "placeholder": element.get_attribute(
                "placeholder"
            ),
            "aria_label": element.get_attribute(
                "aria-label"
            ),
            "value": element.get_attribute(
                "value"
            ),
            "title": element.get_attribute(
                "title"
            ),
            "class": element.get_attribute(
                "class"
            )
        }

        text = ""

        try:
            text = " ".join(
                element.inner_text()
                .strip()
                .split()
            )
        except Exception:
            text = ""

        candidates = [
            attributes["data_qa"],
            attributes["testid"],
            attributes["name"],
            attributes["id"],
            attributes["placeholder"],
            attributes["aria_label"],
            attributes["value"],
            attributes["title"],
            text,
        ]

        base_key = ""

        for candidate in candidates:

            base_key = self._sanitize_key(
                candidate
            )

            if base_key:
                break

        logo_candidate = self._logo_class_candidate(
            attributes["class"]
        )
        if not base_key and logo_candidate:
            base_key = logo_candidate[0]

        if not base_key:
            base_key = (
                f"{element_type}"
                f"{index + 1}"
            )

        lower_key = base_key.lower()

        if element_type == "button":

            known_button_terms = {
                "button",
                "submit",
                "login",
                "search",
                "add",
                "continue",
                "save",
                "cancel",
                "subscribe",
                "register",
                "sign",
                "logout"
            }

            if not any(
                term in lower_key
                for term in known_button_terms
            ):
                base_key = (
                    base_key
                    + "Button"
                )

        return base_key

    # ==================================================
    # BEST LOCATOR GENERATION
    # ==================================================
    def _build_best_locator(
        self,
        element,
        tag_name=None
    ):

        try:

            data_qa = element.get_attribute(
                "data-qa"
            )

            testid = element.get_attribute(
                "data-testid"
            )

            element_id = element.get_attribute(
                "id"
            )

            name = element.get_attribute(
                "name"
            )

            role = element.get_attribute(
                "role"
            )

            aria_label = element.get_attribute(
                "aria-label"
            )

            alt = element.get_attribute(
                "alt"
            )

            class_name = element.get_attribute(
                "class"
            )

            placeholder = element.get_attribute(
                "placeholder"
            )

            value = element.get_attribute(
                "value"
            )

            text = ""

            try:
                text = " ".join(
                    element.inner_text()
                    .strip()
                    .split()
                )
            except Exception:
                text = ""

            if data_qa:

                return (
                    "page.locator("
                    + self._js_string(
                        f'[data-qa="{data_qa}"]'
                    )
                    + ")"
                )

            if testid:

                return (
                    "page.getByTestId("
                    + self._js_string(
                        testid
                    )
                    + ")"
                )

            if element_id:

                return (
                    "page.locator("
                    + self._js_string(
                        f"#{element_id}"
                    )
                    + ")"
                )

            if name:

                return (
                    "page.locator("
                    + self._js_string(
                        f'[name="{name}"]'
                    )
                    + ")"
                )

            if placeholder:

                return (
                    "page.getByPlaceholder("
                    + self._js_string(
                        placeholder
                    )
                    + ")"
                )

            if (
                role
                and (
                    aria_label
                    or text
                    or value
                )
            ):

                accessible_name = (
                    aria_label
                    or text
                    or value
                )

                return (
                    "page.getByRole("
                    + self._js_string(
                        role
                    )
                    + ", { name: "
                    + self._js_string(
                        accessible_name
                    )
                    + " }).first()"
                )

            if aria_label:

                tag = (
                    tag_name
                    if tag_name
                    else "*"
                )

                return (
                    "page.locator("
                    + self._js_string(
                        f'{tag}[aria-label="{aria_label}"]'
                    )
                    + ").first()"
                )

            if alt:
                return (
                    "page.getByAltText("
                    + self._js_string(alt)
                    + ", { exact: true })"
                )

            logo_candidate = self._logo_class_candidate(class_name)
            if logo_candidate:
                return (
                    "page.locator("
                    + self._js_string(
                        f'[class~="{logo_candidate[1]}"]'
                    )
                    + ").first()"
                )

            if (
                tag_name == "input"
                and value
            ):

                return (
                    "page.locator("
                    + self._js_string(
                        f'input[value="{value}"]'
                    )
                    + ").first()"
                )

            if (
                text
                and len(text) < 100
            ):

                return (
                    "page.getByText("
                    + self._js_string(
                        text
                    )
                    + ", { exact: true }).first()"
                )

            if tag_name:

                return (
                    "page.locator("
                    + self._js_string(
                        tag_name
                    )
                    + ").first()"
                )

        except Exception:
            pass

        return None

    # ==================================================
    # SCAN CURRENT PAGE
    # ==================================================
    def _scan_page(
        self,
        page,
        locators,
        generated_locators,
        state_name="initial"
    ):

        selectors = [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "img",
            "[role='img']",
            "input",
            "textarea",
            "select",
            "button",
            "a",
            "[role='button']",
            "[role='link']",
            "[role='checkbox']",
            "[role='radio']",
            "[contenteditable='true']"
        ]

        added_count = 0

        for selector in selectors:

            elements = page.locator(
                selector
            )

            try:
                count = elements.count()
            except Exception:
                continue

            for index in range(count):

                try:

                    element = elements.nth(
                        index
                    )

                    if not element.is_visible():
                        continue

                    tag_name = str(
                        element.evaluate(
                            "element => "
                            "element.tagName.toLowerCase()"
                        )
                    ).lower()

                    element_type = (
                        self._classify_element_type(
                            element,
                            tag_name
                        )
                    )

                    locator_expression = (
                        self._build_best_locator(
                            element,
                            tag_name
                        )
                    )

                    if not locator_expression:
                        continue

                    if (
                        locator_expression
                        in generated_locators
                    ):
                        continue

                    key = self._build_key(
                        element,
                        tag_name,
                        element_type,
                        index
                    )

                    if not key:
                        continue

                    key = self._unique_key(
                        key,
                        locators
                    )

                    options = []

                    if element_type == "select":

                        try:
                            options = (
                                element
                                .locator("option")
                                .all_inner_texts()
                            )
                        except Exception:
                            options = []

                    locators[key] = {
                        "locator": locator_expression,
                        "type": element_type,
                        "priority": self._get_priority(
                            element_type
                        ),
                        "options": options,
                        "state": state_name,
                        "page_url": (
                            self._normalize_url(
                                page.url
                            )
                            or page.url
                        )
                    }

                    generated_locators.add(
                        locator_expression
                    )

                    added_count += 1

                except Exception:
                    continue

        print(
            f"State '{state_name}': "
            f"{added_count} locators added"
        )

    # ==================================================
    # SAFE PAGE WAIT
    # ==================================================
    def _wait_after_action(
        self,
        page,
        timeout=5000
    ):

        try:
            page.wait_for_load_state(
                "domcontentloaded",
                timeout=timeout
            )
        except Exception:
            pass

        try:
            page.wait_for_timeout(
                1200
            )
        except Exception:
            pass

    # ==================================================
    # CLICK FIRST AVAILABLE LOCATOR
    # ==================================================
    def _click_first_available(
        self,
        page,
        locator_candidates,
        timeout=3000
    ):

        for candidate in locator_candidates:
            try:
                locator = candidate(page).first
                locator.wait_for(
                    state="visible",
                    timeout=timeout
                )
                locator.click(timeout=timeout)
                self._wait_after_action(page)
                return True
            except Exception:
                continue

        return False

    # ==================================================
    # STAGE: LOGIN PAGE DISCOVERY
    # ==================================================
    def _discover_login_page(
        self,
        page,
        locators,
        generated_locators,
        requirement_text
    ):

        login_terms = {
            "login",
            "log in",
            "sign in",
            "signup / login",
            "authentication",
            "username",
            "password",
            "email"
        }

        if not any(
            term in requirement_text
            for term in login_terms
        ):
            return False

        try:
            login_form_exists = (
                page.locator(
                    "input[type='password']"
                ).count()
                > 0
            )
        except Exception:
            login_form_exists = False

        if not login_form_exists:

            clicked = (
                self._click_first_available(
                    page,
                    [
                        lambda current_page: (
                            current_page.get_by_text(
                                "Signup / Login",
                                exact=True
                            )
                        ),
                        lambda current_page: (
                            current_page.get_by_role(
                                "link",
                                name=re.compile(
                                    r"sign\s*up\s*/\s*login",
                                    re.IGNORECASE
                                )
                            )
                        ),
                        lambda current_page: (
                            current_page.get_by_role(
                                "link",
                                name=re.compile(
                                    r"log\s*in|login|sign\s*in",
                                    re.IGNORECASE
                                )
                            )
                        ),
                        lambda current_page: (
                            current_page.get_by_text(
                                re.compile(
                                    r"log\s*in|login|sign\s*in",
                                    re.IGNORECASE
                                )
                            )
                        )
                    ]
                )
            )

            if not clicked:
                return False

        self._scan_page(
            page,
            locators,
            generated_locators,
            state_name="loginPage"
        )

        return True
    

    # ==================================================
    # STAGE: PRODUCTS / SEARCH PAGE DISCOVERY
    # ==================================================
    def _discover_products_page(
        self,
        page,
        original_url,
        locators,
        generated_locators,
        requirement_text
    ):

        search_terms = {
            "product",
            "products",
            "search",
            "cart",
            "add to cart",
            "shopping"
        }

        if not any(
            term in requirement_text
            for term in search_terms
        ):
            return False

        try:

            page.goto(
                original_url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            self._wait_after_action(
                page
            )

        except Exception:
            return False

        clicked = (
            self._click_first_available(
                page,
                [
                    lambda current_page: (
                        current_page.get_by_role(
                            "link",
                            name=re.compile(
                                r"^\s*products?\s*$",
                                re.IGNORECASE
                            )
                        )
                    ),
                    lambda current_page: (
                        current_page.get_by_text(
                            re.compile(
                                r"^\s*products?\s*$",
                                re.IGNORECASE
                            )
                        )
                    ),
                    lambda current_page: (
                        current_page.locator(
                            'a[href*="product"]'
                        )
                    )
                ]
            )
        )

        if not clicked:
            return False

        self._scan_page(
            page,
            locators,
            generated_locators,
            state_name="productsPage"
        )

        return True

    # ==================================================
    # STATE-AWARE SEARCH RESULTS DISCOVERY
    # ==================================================
    def _requested_locator_names(
        self,
        requirement_text
    ):
        text = str(
            requirement_text or ""
        )

        names = []

        patterns = (
            (
                r"missing UI element"
                r"(?:s)?(?: and[^:]*)?:\s*"
                r"([A-Za-z_$][A-Za-z0-9_$]*)"
            ),
            (
                r"Discover only this missing UI element"
                r"(?: and[^:]*)?:\s*"
                r"([A-Za-z_$][A-Za-z0-9_$]*)"
            ),
            (
                r"Unknown page locator:\s*"
                r"([A-Za-z_$][A-Za-z0-9_$]*)"
            ),
        )

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            for match in matches:

                if match not in names:
                    names.append(
                        match
                    )

        return names


    def _extract_search_keyword(
        self,
        requirement_text
    ):
        text = html.unescape(
            str(requirement_text or "")
        )

        patterns = (
            (
                r"Search\s+Keyword\s*:\s*"
                r"([^\n\r]+)"
            ),
            (
                r"search(?:ed)?\s+(?:for|with)\s+"
                r"[\"']([^\"']+)[\"']"
            ),
            (
                r"enter\s+[\"']([^\"']+)[\"']"
                r"\s+in(?:to)?\s+the\s+search"
            ),
        )

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            if match:

                keyword = self.clean_html(
                    match.group(1)
                ).strip()

                if keyword:
                    return keyword

        return None


    def _add_confirmed_semantic_locator(
        self,
        page,
        locators,
        generated_locators,
        requested_name,
        selector,
        element_type,
        state_name
    ):
        try:
            candidate = page.locator(
                selector
            )

            count = candidate.count()

            if count <= 0:
                return False

            candidate.first.wait_for(
                state="attached",
                timeout=5000
            )

            locator_expression = (
                "page.locator("
                + self._js_string(
                    selector
                )
                + ")"
            )

            locators[
                requested_name
            ] = {
                "locator": locator_expression,
                "type": element_type,
                "priority": self._get_priority(
                    element_type
                ),
                "options": [],
                "state": state_name,
                "page_url": (
                    self._normalize_url(
                        page.url
                    )
                    or page.url
                ),
                "match_count": count,
                "runtime_confirmed": True
            }

            generated_locators.add(
                locator_expression
            )

            print(
                "Runtime-confirmed locator added: "
                f"{requested_name} -> {selector}"
            )

            return True

        except Exception:
            return False


    def _discover_search_results_page(
        self,
        page,
        original_url,
        locators,
        generated_locators,
        requirement_text
    ):
        requested_names = (
            self._requested_locator_names(
                requirement_text
            )
        )

        lower_requirement = str(
            requirement_text or ""
        ).lower()

        supported_names = {
            "searchedProductList",
            "productResultsContainer",
            "firstProductInList",
            "noResultsMessage"
        }

        should_discover = (
            any(
                name in supported_names
                for name in requested_names
            )
            or "search" in lower_requirement
            or "product result" in lower_requirement
        )

        if not should_discover:
            return False

        try:
            page.goto(
                original_url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            self._wait_after_action(
                page
            )

            search_input = page.locator(
                (
                    'input[placeholder*="search" i], '
                    'input[type="search"], '
                    'input[aria-label*="search" i], '
                    'input[class*="search" i]'
                )
            ).first

            search_input.wait_for(
                state="visible",
                timeout=8000
            )

            keyword = (
                self._extract_search_keyword(
                    requirement_text
                )
                or "shirt"
            )

            search_input.fill(
                keyword
            )

            search_input.press(
                "Enter"
            )

            self._wait_after_action(
                page,
                timeout=15000
            )

            self._scan_page(
                page,
                locators,
                generated_locators,
                state_name="searchResultsPage"
            )

            product_list_candidates = (
                "ul.results-base",
                "li.product-base",
                ".search-searchProductsContainer",
                "[class*='results-base']",
                "[class*='product-base']",
                "[class*='product-list']"
            )

            first_product_candidates = (
                "li.product-base",
                "[class*='product-base']",
                "[class*='product-card']",
                "a[href*='/buy']"
            )

            no_result_candidates = (
                "[class*='noResults']",
                "[class*='no-results']",
                "[class*='search-noResults']"
            )

            for requested_name in requested_names:

                if requested_name in {
                    "searchedProductList",
                    "productResultsContainer"
                }:

                    for selector in (
                        product_list_candidates
                    ):

                        added = (
                            self
                            ._add_confirmed_semantic_locator(
                                page,
                                locators,
                                generated_locators,
                                requested_name,
                                selector,
                                "container",
                                "searchResultsPage"
                            )
                        )

                        if added:
                            break

                elif (
                    requested_name
      == "firstProductInList"
                ):

                    for selector in (
                        first_product_candidates
                    ):

                        added = (
                            self
                            ._add_confirmed_semantic_locator(
                                page,
                                locators,
                                generated_locators,
                                requested_name,
                                selector,
                                "a",
                                "searchResultsPage"
                            )
                        )

                        if added:
                            break

                elif (
                    requested_name
                    == "noResultsMessage"
                ):

                    for selector in (
                        no_result_candidates
                    ):

                        added = (
                            self
                            ._add_confirmed_semantic_locator(
                                page,
                                locators,
                                generated_locators,
                                requested_name,
                                selector,
                                "message",
                                "searchResultsPage"
                            )
                        )

                        if added:
                            break

            return True

        except Exception as error:

            print(
                "Search-results discovery skipped: "
                f"{error}"
            )

            return False
    # ==================================================
    # STAGE: POST-LOGIN PAGE DISCOVERY
    # ==================================================
    def _discover_post_login_page(
        self,
        page,
        original_url,
        username,
        password,
        locators,
        generated_locators,
        requirement_text
    ):

        if not (
            username
            and password
        ):
            return False

        login_terms = {
            "dashboard",
            "logout",
            "log out",
            "products page",
            "after login",
            "successful login"
        }

        if not any(
            term in requirement_text
            for term in login_terms
        ):
            return False

        try:

            page.goto(
                original_url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            self._wait_after_action(
                page
            )

            login_discovered = (
                self._discover_login_page(
                    page,
                    locators,
                    generated_locators,
                    requirement_text
                )
            )

            if not login_discovered:

                password_fields = page.locator(
                    'input[type="password"]'
                )

                if password_fields.count() == 0:
                    return False

            credential_input = page.locator(
                (
                    'input[data-qa="login-email"], '
                    'input[type="email"], '
                    'input[name*="email" i], '
                    'input[name*="user" i], '
                    'input[placeholder*="email" i], '
                    'input[placeholder*="username" i], '
                    'input[type="text"]'
                )
            ).first

            password_input = page.locator(
                'input[type="password"]'
            ).first

            credential_input.wait_for(
                state="visible",
                timeout=5000
            )

            password_input.wait_for(
                state="visible",
                timeout=5000
            )

            credential_input.fill(
                username
            )

            password_input.fill(
                password
            )

            submit_locator = page.locator(
                (
                    '[data-qa="login-button"], '
                    'button[type="submit"], '
                    'input[type="submit"]'
                )
            ).first

            submit_locator.wait_for(
                state="visible",
                timeout=5000
            )

            submit_locator.click(
                timeout=5000
            )

            self._wait_after_action(
                page,
                timeout=8000
            )

            self._scan_page(
                page,
                locators,
                generated_locators,
                state_name="postLoginPage"
            )

            return True

        except Exception:

            print(
                "Post-login discovery skipped. "
                "Credentials may be invalid or the "
                "login flow may require another action."
            )

            return False



    # ==================================================
    # IFRAME COLLECTION
    # ==================================================
    def _is_ignored_frame(
        self,
        frame_url
    ):

        frame_url = str(
            frame_url or ""
        ).lower()

        return any(
            domain in frame_url
            for domain in self.ignored_frame_domains
        )

    def _collect_iframes(
        self,
        page
    ):

        iframes = []

        for frame in page.frames:

            if frame == page.main_frame:
                continue

            frame_url = (
                self._normalize_url(
                    frame.url
                )
                or frame.url
            )

            if self._is_ignored_frame(
                frame_url
            ):
                continue

            iframes.append(
                {
                    "name": frame.name,
                    "url": frame_url
                }
            )

        return iframes

    # ==================================================
    # WINDOW COLLECTION
    # ==================================================
    def _collect_windows(
        self,
        page
    ):

        windows = []

        for open_page in (
            page.context.pages
        ):

            try:
                title = open_page.title()
            except Exception:
                title = ""

            window_url = (
                self._normalize_url(
                    open_page.url
                )
                or open_page.url
            )

            windows.append(
                {
                    "title": title,
                    "url": window_url
                }
            )

        return windows

    # ==================================================
    # MAIN LOCATOR EXTRACTION
    # ==================================================
    def extract_locators(
        self,
        url,
        requirement="",
        business_flow=None,
        username=None,
        password=None
    ):

        locators = {}
        generated_locators = set()

        requirement = (
            str(requirement)
            if requirement is not None
            else ""
        )

        business_flow = (
            business_flow
            if business_flow is not None
            else []
        )

        if isinstance(
            business_flow,
            str
        ):
            business_flow = [
                business_flow
            ]

        elif not isinstance(
            business_flow,
            (
                list,
                tuple,
                set
            )
        ):
            business_flow = []

        requirement_text = (
            requirement
            + " "
            + " ".join(
                str(step)
                for step in business_flow
            )
        ).lower()

        normalized_url = (
            self._normalize_url(
                url
            )
        )

        if not normalized_url:

            print(
                "Locator Extraction Error: "
                "Invalid URL"
            )

            return {
                "locators": {},
                "iframes": [],
                "windows": [],
                "alerts_supported": True,
                "states": []
            }

        print(
            f"Normalized URL: "
            f"{normalized_url}"
        )

        states = []
        iframes = []
        windows = []

        try:

            with sync_playwright() as playwright:

                browser = (
                    playwright.chromium.launch(
                        headless=True
                    )
                )

                context = browser.new_context(
                    viewport={
                        "width": 1440,
                        "height": 900
                    }
                )

                page = context.new_page()

                try:

                    try:
                        page.goto(
                            normalized_url,
                            wait_until="domcontentloaded",
                            timeout=60000
                        )
                    except Exception as error:
                        if (
                            os.name != "nt"
                            or "ERR_HTTP2_PROTOCOL_ERROR"
                            not in str(error)
                        ):
                            raise

                        print(
                            "Headless locator discovery hit an HTTP/2 "
                            "protocol error; retrying with the visible "
                            "Chromium browser."
                        )
                        context.close()
                        browser.close()
                        browser = playwright.chromium.launch(
                            headless=False
                        )
                        context = browser.new_context(
                            viewport={
                                "width": 1440,
                                "height": 900
                            }
                        )
                        page = context.new_page()
                        page.goto(
                            normalized_url,
                            wait_until="domcontentloaded",
                            timeout=60000
                        )

                    self._wait_after_action(
                        page
                    )

                    self._scan_page(
                        page,
                        locators,
                        generated_locators,
                        state_name="initialPage"
                    )

                    states.append(
                        {
                            "name": "initialPage",
                            "url": (
                                self._normalize_url(
                                    page.url
                                )
                                or page.url
                            )
                        }
                    )

                    login_discovered = (
                        self._discover_login_page(
                            page,
                            locators,
                            generated_locators,
                            requirement_text
                        )
                    )

                    search_results_discovered = (
                        self._discover_search_results_page(
                            page,
                            normalized_url,
                            locators,
                            generated_locators,
                            requirement_text
                        )
                    )

                    if search_results_discovered:

                        states.append(
                            {
                                "name": (
                                    "searchResultsPage"
                                ),
                                "url": (
                                    self._normalize_url(
                                        page.url
                                    )
                                    or page.url
                                )
                            }
                        )

                    if login_discovered:

                        states.append(
                            {
                                "name": "loginPage",
                                "url": (
                                    self._normalize_url(
                                        page.url
                                    )
                                    or page.url
                                )
                            }
                        )

                    products_discovered = (
                        self._discover_products_page(
                            page,
                            normalized_url,
                            locators,
                            generated_locators,
                            requirement_text
                        )
                    )

                    if products_discovered:

                        states.append(
                            {
                                "name": "productsPage",
                                "url": (
                                    self._normalize_url(
                                        page.url
                                    )
                                    or page.url
                                )
                            }
                        )

                    post_login_discovered = (
                        self._discover_post_login_page(
                            page,
                            normalized_url,
                            username or "",
                            password or "",
                            locators,
                            generated_locators,
                            requirement_text
                        )
                    )

                    if post_login_discovered:

                        states.append(
                            {
                                "name": "postLoginPage",
                                "url": (
                                    self._normalize_url(
                                        page.url
                                    )
                                    or page.url
                                )
                            }
                        )

                    iframes = self._collect_iframes(
                        page
                    )

                    windows = self._collect_windows(
                        page
                    )

                finally:

                    context.close()
                    browser.close()

            print(
                "Total Locators Found: "
                f"{len(locators)}"
            )

            return {
                "locators": locators,
                "iframes": iframes,
                "windows": windows,
                "alerts_supported": True,
                "states": states
            }

        except PlaywrightTimeoutError as error:

            print(
                "Locator Extraction Timeout: "
                f"{error}"
            )

        except Exception as error:

            print(
                "Locator Extraction Error: "
                f"{error}"
            )

        return {
            "locators": locators,
            "iframes": iframes,
            "windows": windows,
            "alerts_supported": True,
            "states": states
        }

    # ==================================================
    # SAVE LOCATORS
    # ==================================================
    def save_locators(
        self,
        locators,
        output_file
    ):

        output_path = Path(
            output_file
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path.write_text(
            json.dumps(
                locators,
                indent=4,
                ensure_ascii=False
            )
            + "\n",
            encoding="utf-8"
        )

        return str(
            output_path
        )