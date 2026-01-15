"""
Configuration for NotebookLM Skill
Centralizes constants, selectors, and paths
"""

from pathlib import Path

# Paths
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
BROWSER_STATE_DIR = DATA_DIR / "browser_state"
BROWSER_PROFILE_DIR = BROWSER_STATE_DIR / "browser_profile"
STATE_FILE = BROWSER_STATE_DIR / "state.json"
AUTH_INFO_FILE = DATA_DIR / "auth_info.json"
LIBRARY_FILE = DATA_DIR / "library.json"

# NotebookLM Selectors
QUERY_INPUT_SELECTORS = [
    "textarea.query-box-input",  # Primary
    'textarea[aria-label="Feld für Anfragen"]',  # Fallback German
    'textarea[aria-label="Input for queries"]',  # Fallback English
]

RESPONSE_SELECTORS = [
    ".to-user-container .message-text-content",  # Primary
    "[data-message-author='bot']",
    "[data-message-author='assistant']",
]

# Browser Configuration
BROWSER_ARGS = [
    '--disable-blink-features=AutomationControlled',  # Patches navigator.webdriver
    '--disable-dev-shm-usage',
    '--no-sandbox',
    '--no-first-run',
    '--no-default-browser-check'
]

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Timeouts (in milliseconds for Playwright, unless noted)
LOGIN_TIMEOUT_MINUTES = 10
QUERY_TIMEOUT_SECONDS = 120
PAGE_LOAD_TIMEOUT_MS = 30000  # 30 seconds
ELEMENT_WAIT_TIMEOUT_MS = 10000  # 10 seconds
NAVIGATION_TIMEOUT_MS = 30000  # 30 seconds

# CI/CD adjustments - increase timeouts for slower environments
import os
IS_CI_CD = os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'

if IS_CI_CD:
    # CI/CD environments are slower (Xvfb, network latency, etc.)
    PAGE_LOAD_TIMEOUT_MS = 60000  # 60 seconds
    ELEMENT_WAIT_TIMEOUT_MS = 30000  # 30 seconds
    NAVIGATION_TIMEOUT_MS = 60000  # 60 seconds
    QUERY_TIMEOUT_SECONDS = 180  # 3 minutes
