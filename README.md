# Agent Automation AI

This package uses Gemini to analyze a requirement and generate Playwright
artifacts. It does not execute generated browser tests unless you explicitly
pass `--run-tests`.

## Setup

From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r Agent_AUTOMATION_AI\requirements.txt
Copy-Item Agent_AUTOMATION_AI\.env.example Agent_AUTOMATION_AI\.env
```

Edit `Agent_AUTOMATION_AI\.env` and set `GEMINI_API_KEY` to your own key. Do not
commit this file or paste its contents into chat. `GEMINI_MODEL` and
`GEMINI_TIMEOUT_SECONDS` can be changed if needed.

If Gemini reports `RESOURCE_EXHAUSTED` or HTTP 429, the configured project/model
has no available quota for that request. Check its quota and billing in Google
AI Studio, wait for the limit to reset, or select a model that has available
quota. The CLI reports this as an actionable error; it cannot increase or
bypass the provider's quota.

The repository's existing Playwright dependencies are installed from the root:

```powershell
npm install
npx playwright install
```

## Generate artifacts

From the repository root:

```powershell
python -m Agent_AUTOMATION_AI.main
```

Or, from inside `Agent_AUTOMATION_AI`:

```powershell
..\venv\Scripts\python.exe .\main.py
```

To run the standalone Gemini smoke test from inside `Agent_AUTOMATION_AI`:

```powershell
python .\Test_AI.py
```

To use another UTF-8 requirement file:

```powershell
python -m Agent_AUTOMATION_AI.main --requirement path\to\requirements.txt
```

Generated Markdown, JavaScript, and Excel workbooks are written beneath
`Agent_AUTOMATION_AI\generated`.

## Run generated browser tests

Review the generated JavaScript and its target URL before running it. Then:

```powershell
python -m Agent_AUTOMATION_AI.main --run-tests
```

The test runner uses the root Playwright configuration and runs the generated
spec explicitly. Failure analysis uses Gemini; the Jira agent currently returns
a local placeholder and does not create a real Jira issue.

## Project layout

```text
Agent_AUTOMATION_AI/
  Requirements/       Input requirement files
  generated/          Generated analysis, test artifacts, reports, and exports
  tests/              Local unit tests
  main.py             CLI entry point
  ai_agent.py         Gemini API client
  requirements.txt    Python dependencies
  .env.example        Safe environment-variable template
```
