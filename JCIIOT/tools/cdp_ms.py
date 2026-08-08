"""Reuse a logged-in Chrome session via CDP to authenticate ModelScope/Aliyun
DSW instances (based on the auto-cookie-extraction skill pattern).

Flow:
  1. Kill any running Chrome, relaunch with --remote-debugging-port + the
     Default user-data-dir (preserves login state).
  2. Wait for the CDP port, fetch the page WebSocket endpoint.
  3. Extract decrypted cookies for the DSW / Aliyun domain via Storage.getCookies.
  4. Save them to a LOCAL json (never committed) so subsequent Jupyter-API calls
     can carry the session Cookie header and bypass the SSO redirect.

NOTE: this only works if the user is actually logged into ModelScope/Aliyun in
this Chrome Default profile. If the profile has no session, cookies will be empty
and DSW will still redirect to login — in that case the user must sign in once.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

try:
    import requests
    import websocket
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "websocket-client", "requests"])
    import requests  # noqa: E402
    import websocket  # noqa: E402

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME):
    CHROME = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
USER_DATA = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
PORT = 9222
COOKIE_CACHE = os.path.join(os.path.dirname(__file__), "..", "ms_session_cookies.json")


def launch_chrome(target_url: str = "about:blank") -> None:
    # 如果 CDP 端口已开,复用现有实例(不杀 Chrome)
    try:
        requests.get(f"http://127.0.0.1:{PORT}/json/version", timeout=2)
        return
    except Exception:
        pass
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True, text=True)
    time.sleep(2)
    subprocess.Popen([
        CHROME, f"--remote-debugging-port={PORT}", "--remote-allow-origins=*",
        f"--user-data-dir={USER_DATA}", "--no-first-run", "--no-default-browser-check",
        "--restore-last-session", target_url,
    ])
    # wait for port
    for _ in range(30):
        time.sleep(1)
        try:
            requests.get(f"http://127.0.0.1:{PORT}/json/version", timeout=2)
            return
        except Exception:
            pass
    raise RuntimeError("CDP port did not open after 30s")


def get_ws_url() -> str:
    targets = requests.get(f"http://127.0.0.1:{PORT}/json").json()
    pages = [t for t in targets if t.get("type") == "page"]
    # 优先选非 about:blank 的页面
    for t in pages:
        if t.get("url", "") != "about:blank":
            return t["webSocketDebuggerUrl"]
    if pages:
        return pages[0]["webSocketDebuggerUrl"]
    raise RuntimeError("no page target found")


class CDP:
    def __init__(self, ws_url: str):
        self.ws = websocket.create_connection(ws_url, timeout=30)
        self._id = 0

    def call(self, method, params=None):
        self._id += 1
        self.ws.send(json.dumps({"id": self._id, "method": method, "params": params or {}}))
        while True:
            r = json.loads(self.ws.recv())
            if r.get("id") == self._id:
                return r.get("result", {})
            # ignore events

    def cookies(self, url):
        res = self.call("Storage.getCookies", {"urls": [url]})
        return {c["name"]: c["value"] for c in res.get("cookies", [])}

    def navigate(self, url):
        self.call("Page.enable")
        self.call("Page.navigate", {"url": url})

    def current_url(self) -> str:
        res = self.call("Runtime.evaluate", {"expression": "window.location.href"})
        return res.get("result", {}).get("value", "")


def extract_and_save(domain_url: str, cache_path: str = COOKIE_CACHE) -> dict:
    launch_chrome(domain_url)
    ws = get_ws_url()
    cdp = CDP(ws)
    cdp.navigate(domain_url)
    time.sleep(8)  # let SSO redirect / page settle

    # 检测是否在登录页,如果是则等待用户手动登录
    cur = cdp.current_url()
    if any(k in cur.lower() for k in ["login", "account.aliyun", "signin"]):
        print("[cdp] 登录态已过期,请在 Chrome 窗口手动登录阿里云,脚本会自动检测...")
        for i in range(300):
            time.sleep(2)
            cur = cdp.current_url()
            if not any(k in cur.lower() for k in ["login", "account.aliyun", "signin"]):
                print(f"[cdp] 登录成功: {cur[:80]}")
                time.sleep(10)  # 等 DSW 页面加载
                break
            if i % 15 == 14:
                print(f"  仍在等待登录... ({(i+1)*2}s)")
        else:
            print("[cdp] 登录超时(10分钟),退出")
            cdp.ws.close()
            return {}

    cookies = cdp.cookies(domain_url)
    cookies.update(cdp.cookies("https://account.aliyun.com"))
    cookies.update(cdp.cookies("https://www.modelscope.cn"))
    cookies.update(cdp.cookies("https://modelscope.cn"))
    out = {"domain": domain_url, "cookies": cookies,
           "captured_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    os.makedirs(os.path.dirname(os.path.abspath(cache_path)), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    cdp.ws.close()
    return cookies


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else (
        "https://dsw-gateway-cn-hangzhou.data.aliyun.com/dsw-2085479/lab/tree/dswQinghua")
    cookies = extract_and_save(url)
    print(f"[cdp] extracted {len(cookies)} cookies for DSW/Aliyun/modelscope")
    for k in cookies:
        print(f"  - {k}")
    if not cookies:
        print("[cdp] NO cookies — the Default Chrome profile is not logged into "
              "ModelScope/Aliyun. Please sign in once in this Chrome profile, then re-run.")
