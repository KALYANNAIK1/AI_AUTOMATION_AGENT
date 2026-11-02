import atexit
import base64
import os
import ssl
import tempfile
import time
from pathlib import Path

import certifi
import requests
from dotenv import dotenv_values


_windows_ca_bundle = None


class GeminiQuotaError(RuntimeError):
    """Raised when Gemini rejects a request because the quota is exhausted."""


class GeminiTransientError(RuntimeError):
    """Raised for a Gemini interaction failure that may succeed on retry."""


def _get_ca_bundle(config):
    global _windows_ca_bundle

    configured_bundle = os.getenv("GEMINI_CA_BUNDLE") or config.get(
        "GEMINI_CA_BUNDLE"
    )
    if configured_bundle:
        ca_path = Path(configured_bundle).expanduser()
        if not ca_path.is_file():
            raise ValueError(
                f"GEMINI_CA_BUNDLE does not point to a file: {ca_path}"
            )
        return str(ca_path.resolve())

    if os.name != "nt":
        return certifi.where()

    if _windows_ca_bundle and Path(_windows_ca_bundle).is_file():
        return _windows_ca_bundle

    certificates = [Path(certifi.where()).read_bytes()]
    for certificate, encoding, _trust in ssl.enum_certificates("ROOT"):
        if encoding != "x509_asn":
            continue

        encoded = base64.b64encode(certificate).decode("ascii")
        pem_lines = "\n".join(
            encoded[index:index + 64]
            for index in range(0, len(encoded), 64)
        )
        certificates.append(
            (
                f"-----BEGIN CERTIFICATE-----\n{pem_lines}\n"
                "-----END CERTIFICATE-----\n"
            ).encode("ascii")
        )

    with tempfile.NamedTemporaryFile(
        mode="wb",
        suffix=".pem",
        prefix="gemini-ca-",
        delete=False,
    ) as bundle:
        bundle.write(b"\n".join(certificates))
        _windows_ca_bundle = bundle.name

    bundle_path = _windows_ca_bundle
    atexit.register(lambda: Path(bundle_path).unlink(missing_ok=True))
    return _windows_ca_bundle


class AIAgent:

    def __init__(self):
        self.config = dotenv_values(Path(__file__).with_name(".env"))
        self.api_key = (
            os.getenv("GEMINI_API_KEY")
            or self.config.get("GEMINI_API_KEY")
        )
        if not self.api_key or self.api_key.startswith("replace-with-"):
            raise ValueError(
                "Set a valid GEMINI_API_KEY in the environment or "
                "Agent_AUTOMATION_AI/.env."
            )

        self.model = (
            os.getenv("GEMINI_MODEL")
            or self.config.get("GEMINI_MODEL")
            or "gemini-3.1-flash-lite"
        )
        try:
            self.timeout = float(
                os.getenv("GEMINI_TIMEOUT_SECONDS")
                or self.config.get("GEMINI_TIMEOUT_SECONDS")
                or "300"
            )
        except ValueError as exc:
            raise ValueError("GEMINI_TIMEOUT_SECONDS must be a number.") from exc
        if self.timeout <= 0:
            raise ValueError("GEMINI_TIMEOUT_SECONDS must be greater than zero.")

        self.session = requests.Session()
        self.session.headers.update({
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
            "Api-Revision": "2026-05-20",
        })
        self.ca_bundle = _get_ca_bundle(self.config)

    def _execute_with_retry(self, method, *args, **kwargs):
        max_retries = 3

        for attempt in range(max_retries):
            try:
                return method(*args, **kwargs)
            except requests.RequestException:
                if attempt == max_retries - 1:
                    raise

                wait_time = (attempt + 1) * 30
                print(
                    f"[Retry {attempt + 1}/{max_retries}] "
                    f"Waiting {wait_time} seconds..."
                )
                time.sleep(wait_time)

    @staticmethod
    def _raise_api_error(response):
        if response.ok:
            return

        try:
            error = response.json().get("error", {})
            if not isinstance(error, dict):
                error = {}
            message = error.get("message", response.text)
            status = error.get("status", response.status_code)
            error_code = error.get("code")
        except ValueError:
            message = response.text
            status = response.status_code
            error_code = None

        if (
            response.status_code == 429
            or status == "RESOURCE_EXHAUSTED"
            or error_code == 429
            or error_code == "RESOURCE_EXHAUSTED"
        ):
            message = AIAgent._add_quota_guidance(message)
            raise GeminiQuotaError(
                f"Gemini API quota exceeded ({status}): {message}"
            )
        raise RuntimeError(f"Gemini API error {status}: {message}")

    @staticmethod
    def _parse_response(response, context):
        try:
            return response.json()
        except ValueError as exc:
            raise RuntimeError(
                f"Gemini API returned invalid JSON {context}."
            ) from exc

    def ask_ai(self, prompt):
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be a non-empty string.")

        print(f"Prompt Length: {len(prompt)}")
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                return self._ask_ai_once(prompt)
            except GeminiTransientError as exc:
                if attempt == max_attempts - 1:
                    raise RuntimeError(
                        "Gemini returned a temporary INTERNAL error after "
                        f"{max_attempts} attempts: {exc}"
                    ) from exc

                wait_time = 2 ** attempt
                print(
                    f"[Retry {attempt + 1}/{max_attempts - 1}] "
                    f"Gemini returned a temporary INTERNAL error; "
                    f"retrying in {wait_time} seconds."
                )
                time.sleep(wait_time)

    def _ask_ai_once(self, prompt):
        deadline = time.monotonic() + self.timeout
        interactions_url = (
            "https://generativelanguage.googleapis.com/v1beta/interactions"
        )

        try:
           response = self._execute_with_retry(
    self.session.post,
    interactions_url,
    json={
        "model": self.model,
        "input": prompt,
        "background": True,
    },
    timeout=(
        min(10, self.timeout),
        min(30, self.timeout)
    ),
    verify=self.ca_bundle,
)
        except requests.Timeout as exc:
            raise TimeoutError(
                "Gemini did not accept the background request before the "
                "connection timed out."
            ) from exc
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Could not connect to the Gemini API: {exc}"
            ) from exc

        self._raise_api_error(response)
        result = self._parse_response(response, "when creating an interaction")
        interaction_id = result.get("id")
        if not interaction_id:
            raise RuntimeError(
                "Gemini accepted the request but returned no interaction ID."
            )

        while result.get("status") in {"in_progress", "queued"}:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(
                    f"Gemini interaction {interaction_id} did not finish "
                    f"within {self.timeout:g} seconds."
                )

            time.sleep(min(2, remaining))
            try:
                response = self.session.get(
                    f"{interactions_url}/{interaction_id}",
                    timeout=(min(10, remaining), min(15, remaining)),
                    verify=self.ca_bundle,
                )
            except requests.Timeout as exc:
                raise TimeoutError(
                    "Timed out while checking the Gemini interaction status."
                ) from exc
            except requests.RequestException as exc:
                raise RuntimeError(
                    f"Could not retrieve Gemini interaction status: {exc}"
                ) from exc

            self._raise_api_error(response)
            result = self._parse_response(
                response,
                "while checking interaction status",
            )

        if result.get("status") != "completed":
            error_details = self._interaction_error(result)

            if "RESOURCE_EXHAUSTED" in str(error_details):
                raise GeminiQuotaError(
                    f"Gemini API quota exceeded: {error_details} Check the "
                    "quota for the current Google AI Studio project and "
                    "selected model. Wait for the quota to reset or enable "
                    "billing if appropriate. Changing the model only helps "
                    "if that model has available quota."
                )

            if self._has_internal_error(result):
                raise GeminiTransientError(error_details)

            raise RuntimeError(
                f"Gemini interaction finished with status "
                f"{result.get('status')}: {error_details}"
            )

        output_text = result.get("output_text")
        if output_text:
            return output_text

        text_parts = [
            part["text"]
            for step in result.get("steps", [])
            if step.get("type") == "model_output"
            for part in step.get("content", [])
            if part.get("type") == "text" and part.get("text")
        ]
        if text_parts:
            return "\n".join(text_parts)

        raise RuntimeError(
            "Gemini completed the request but returned no text output."
        )

    @staticmethod
    def _has_internal_error(result):
        errors = result.get("errors")
        if isinstance(errors, list):
            return any(
                isinstance(error, dict)
                and error.get("code") == "INTERNAL"
                for error in errors
            )
        error = result.get("error")
        return isinstance(error, dict) and error.get("code") == "INTERNAL"

    @staticmethod
    def _interaction_error(result):
        errors = result.get("errors")
        if isinstance(errors, list):
            details = []
            for error in errors:
                if isinstance(error, dict):
                    code = error.get("code")
                    message = error.get("message")
                    detail = ": ".join(
                        str(value)
                        for value in (code, message)
                        if value
                    )
                    if detail:
                        details.append(detail)
                elif error:
                    details.append(str(error))
            if details:
                return "; ".join(details)

        error = result.get("error")
        if isinstance(error, dict):
            return error.get("message") or str(error)
        return error or "no error details returned"

    @staticmethod
    def _add_quota_guidance(message):
        return (
            f"{message}. Check Gemini API quota and rate limits in Google AI "
            "Studio; wait for the limit to reset or enable billing."
        )
