"""Reusable connector to a ModelScope DSW JupyterLab instance.

Connection strategy: reuse the user's locally-logged-in Chrome session via the
Chrome DevTools Protocol (CDP). This preserves the ModelScope / Aliyun login
state, so no separate token is needed. The instance URL is provided by the
caller (env var DSW_URL or function argument).

Read-only by default: it only opens the instance and can read the JupyterLab
environment. Any command execution must be explicitly requested.

NOTE: this module reuses the operator's authenticated browser session. Keep it
local; do not commit credentials. The DSW URL is passed in, not hardcoded.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME):
    CHROME = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

USER_DATA = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
CDP_PORT = 9222


def chrome_is_running() -> bool:
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
                         capture_output=True, text=True).stdout
    return "chrome.exe" in out


def kill_chrome() -> None:
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"],
                   capture_output=True, text=True)


def launch_chrome_cdp(url: str) -> subprocess.Popen:
    """Launch Chrome with CDP enabled, reusing the Default profile (keeps login).

    If a Chrome already owns the profile / CDP port, restart it with CDP so we
    can attach. The login state lives in the profile on disk, so it survives.
    """
    if chrome_is_running():
        print("[cdp] restarting Chrome with CDP (preserves profile login state)...", flush=True)
        kill_chrome()
        time.sleep(3)
    proc = subprocess.Popen([
        CHROME,
        f"--remote-debugging-port={CDP_PORT}",
        "--remote-allow-origins=*",
        f"--user-data-dir={USER_DATA}",
        "--no-first-run",
        "--no-default-browser-check",
        "--restore-last-session",
        url,
    ])
    print(f"[cdp] launched Chrome PID={proc.pid}", flush=True)
    return proc


def wait_cdp_ready(retries: int = 30, delay: float = 2.0) -> bool:
    import requests
    for i in range(retries):
        time.sleep(delay)
        try:
            r = requests.get(f"http://127.0.0.1:{CDP_PORT}/json/version", timeout=3)
            if r.ok:
                print(f"[cdp] ready after {i+1} tries: {r.json().get('Browser','?')}", flush=True)
                return True
        except Exception:
            if i % 5 == 4:
                print(f"[cdp] waiting CDP ({i+1}/{retries})...", flush=True)
    return False


def connect(url: str | None = None):
    """Open the DSW instance reusing the user's Chrome profile cookies.

    Uses Playwright's persistent context on the Default user-data-dir so the
    ModelScope / Aliyun login cookies are reused (no token needed). The running
    Chrome must be closed first because the profile is locked.
    """
    from playwright.sync_api import sync_playwright
    url = url or os.environ.get("DSW_URL")
    if not url:
        raise RuntimeError("No DSW_URL provided (arg or env var).")
    if chrome_is_running():
        print("[connect] closing running Chrome to unlock profile...", flush=True)
        kill_chrome()
        time.sleep(3)
    pw = sync_playwright().start()
    context = pw.chromium.launch_persistent_context(
        user_data_dir=USER_DATA,
        headless=False,
        args=["--disable-blink-features=AutomationControlled"],
        viewport={"width": 1440, "height": 900},
    )
    page = context.new_page()
    print(f"[connect] opening {url}", flush=True)
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(12)
    try:
        page.wait_for_load_state("networkidle", timeout=30000)
    except Exception:
        pass
    return context, pw, page


def find_dsw_page(browser, url_substr: str = "dsw-"):
    for ctx in browser.contexts:
        for pg in ctx.pages:
            if url_substr in pg.url:
                return pg
    return None


def probe_environment(page) -> str:
    """Read-only: dump JupyterLab env info via the in-page terminal, return text."""
    base = page.url.split("/lab")[0].rstrip("/")
    term_url = base + "/terminals/web-1"
    page.goto(term_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    diag = (
        'echo "=== GPU ==="; nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv 2>&1 | head; '
        'echo "=== TORCH ==="; python -c "import torch;print(torch.__version__, \\\"cuda=\\\", torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else \\\"CPU\\\")" 2>&1; '
        'echo "=== PKGS ==="; python -c "import importlib;\\nfor m in [\\\'robosuite\\\',\\\'robomimic\\\',\\\'mujoco\\\',\\\'h5py\\\']:\\n try: importlib.import_module(m); print(m,\\\"OK\\\")\\n except Exception as e: print(m,\\\"MISSING\\\")" 2>&1; '
        'echo "=== PWD ==="; pwd; ls -la | head; '
        'echo "=== DONE ==="'
    )
    try:
        page.locator(".xterm-helper-textarea").click(timeout=5000)
    except Exception:
        page.click("body", timeout=2000)
    page.keyboard.type(diag, delay=1)
    page.keyboard.press("Enter")
    time.sleep(20)
    try:
        return page.inner_text("body")[:5000]
    except Exception as e:
        return f"(read failed: {e})"


if __name__ == "__main__":
    u = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DSW_URL")
    context, pw, page = connect(u)
    try:
        print(f"[probe] page url: {page.url}", flush=True)
        if "login" in page.url.lower() or "signin" in page.url.lower():
            print("[probe] REDIRECTED TO LOGIN — session not reusable from this profile.", flush=True)
            try:
                print(page.inner_text("body")[:800])
            except Exception:
                pass
        else:
            out = probe_environment(page)
            print("[probe] ENV:\n" + out)
    finally:
        try:
            context.close()
        except Exception:
            pass
        pw.stop()
