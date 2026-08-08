"""Minimal authenticated client for the Aliyun DSW JupyterLab gateway.

Authentication uses a single browser session cookie extracted via CDP from a
logged-in Chrome profile (see tools/cdp_ms.py). The DSW gateway accepts the
`login_aliyunid_ticket` cookie to authorize JupyterHub REST API calls.

All methods talk to:
    https://dsw-gateway-cn-hangzhou.data.aliyun.com/dsw-2085479/api/...
"""
from __future__ import annotations

import json
import os
import requests

DOMAIN = "https://dsw-gateway-cn-hangzhou.data.aliyun.com"
BASE = DOMAIN + "/dsw-2085479"
COOKIE_CACHE = os.path.join(os.path.dirname(__file__), "..", "ms_session_cookies.json")


def load_ticket(cache_path: str = COOKIE_CACHE) -> str:
    data = json.load(open(os.path.abspath(cache_path), encoding="utf-8"))
    return data["cookies"]["login_aliyunid_ticket"]


class Dswhub:
    def __init__(self, ticket: str | None = None, cache_path: str = COOKIE_CACHE):
        self.ticket = ticket or load_ticket(cache_path)
        self.s = requests.Session()
        self.s.headers.update({"Cookie": f"login_aliyunid_ticket={self.ticket}"})
        self.s.verify = True

    def _get(self, path, **kw):
        r = self.s.get(BASE + path, timeout=30, allow_redirects=False, **kw)
        if r.status_code in (301, 302) and "login" in r.headers.get("Location", ""):
            raise RuntimeError("session expired - re-extract cookie via cdp_ms.py")
        r.raise_for_status()
        return r

    def _post(self, path, **kw):
        # Jupyter needs XSRF token for state-changing calls
        r0 = self._get("/api/me")
        # _xsrf cookie isn't carried by our minimal header; try without first
        r = self.s.post(BASE + path, timeout=60, **kw)
        r.raise_for_status()
        return r

    # --- read API ---
    def me(self):
        return self._get("/api/me").json()

    def contents(self, path: str = "", content: int = 1):
        return self._get(f"/api/contents/{path}", params={"content": content}).json()

    def sessions(self):
        return self._get("/api/sessions").json()

    def kernels(self):
        return self._get("/api/kernels").json()

    def terminals(self):
        return self._get("/api/terminals").json()

    # --- terminal exec: open a terminal, run cmd, read output ---
    def run_in_terminal(self, cmd: str, wait: float = 8.0):
        """Best-effort: create a terminal, send command, poll output.
        DSW terminals are websocket-based; for longer jobs prefer a kernel
        execute. This returns the terminal id and is mainly for quick checks."""
        import time, websocket, json as _json
        r = self.s.post(BASE + "/api/terminals", timeout=30)
        r.raise_for_status()
        term = r.json()["name"]
        ws_url = DOMAIN.replace("https://", "wss://") + f"/dsw-2085479/terminals/websocket/{term}"
        ws = websocket.create_connection(ws_url, header=[f"Cookie: login_aliyunid_ticket={self.ticket}"], timeout=30)
        ws.send(_json.dumps(["stdin", cmd + "\r"]))
        buf = ""
        deadline = time.time() + wait
        while time.time() < deadline:
            try:
                typ, data = ws.recv()
                if typ in ("stdout", "stderr"):
                    buf += data
            except Exception:
                break
        ws.close()
        return term, buf

    # --- kernel exec: run python and get result (used for setup checks) ---
    def run_python(self, code: str, kernel_name: str = "python3", timeout: int = 60):
        import time, websocket, json as _json, uuid
        # find or start a kernel
        kernels = self.kernels()
        kid = None
        for k in kernels:
            if k.get("name") == kernel_name:
                kid = k["id"]; break
        if not kid:
            r = self.s.post(BASE + "/api/kernels", json={"name": kernel_name}, timeout=30)
            r.raise_for_status(); kid = r.json()["id"]
        # open channels websocket
        ws_url = DOMAIN.replace("https://", "wss://") + f"/dsw-2085479/api/kernels/{kid}/channels"
        ws = websocket.create_connection(ws_url, header=[f"Cookie: login_aliyunid_ticket={self.ticket}"], timeout=timeout)
        msg_id = "op-" + uuid.uuid4().hex[:8]
        ws.send(_json.dumps({"header": {"msg_id": msg_id, "username": "opencode", "session": msg_id,
                                         "msg_type": "execute_request", "version": "5.3"},
                             "parent_header": {}, "metadata": {}, "content": {
                                 "code": code, "silent": False, "store_history": True,
                                 "user_expressions": {}, "allow_stdin": False}, "channel": "shell"}))
        outputs = []
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                raw = ws.recv()
                if isinstance(raw, tuple): raw = raw[1]
                o = _json.loads(raw)
            except Exception:
                break
            if o.get("parent_header", {}).get("msg_id") != msg_id:
                continue
            mtype = o.get("msg_type")
            if mtype == "stream":
                outputs.append(o["content"].get("text", ""))
            elif mtype in ("execute_result", "display_data"):
                outputs.append(o["content"].get("data", {}).get("text/plain", ""))
            elif mtype == "error":
                outputs.append("ERR: " + "\n".join(o["content"].get("traceback", [])))
            elif mtype == "status" and o["content"].get("execution_state") == "idle":
                break
        ws.close()
        return "".join(outputs)


if __name__ == "__main__":
    d = Dswhub()
    print("me:", d.me().get("identity"))
    print("contents root:", [c["name"] for c in d.contents("")["content"]][:12])
