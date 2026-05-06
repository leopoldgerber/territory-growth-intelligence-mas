# Parse Reports Agents

Playwright-agent implementation for the Semrush report pipeline.

The Selenium implementation in `../parse_reports_modules` remains the reference pipeline. This package replaces only the browser behavior layer and reuses shared parsing, transformation, Excel writing, settings, domain, and progress modules from the modular implementation.

## Structure

- `agent_app/agent/` contains agent lifecycle, state, tasks, runner, policy, recovery, validators, and logging.
- `agent_app/agent_tools/` contains safe browser and Semrush tools.
- `agent_app/playwright_runtime/` contains browser startup, low-level actions, locators, and download manifest helpers.
- `agent_app/shared/` adapts reusable modules from `../parse_reports_modules/app`.
- `tests/` covers state, tools, manifest, validators, and dry-run planning without real Semrush access.

## Commands

```powershell
pip install -r requirements.txt
python -m playwright install chromium
python main.py --engine playwright-agent --mode full
python main.py --engine playwright-agent --mode download --headless
python main.py --engine playwright-agent --mode process
python main.py --engine playwright-agent --mode full --start 0 --amount 1 --months 1 --dry-run
```

Copy `.env.example` to `.env` and fill credentials and paths before real browser downloads.

## Modes

- `download` opens Semrush with Playwright-agent and exports CSV files.
- `process` reuses the modular processing pipeline and creates Excel files.
- `full` runs download and processing.
- `dry-run` builds and logs the task plan without clicking or downloading.

## Readiness

The current implementation is a safe agent runner with structured tools, state, manifest, validation, retries, and dry-run support. Real Semrush stability still depends on locator validation against the live UI.
