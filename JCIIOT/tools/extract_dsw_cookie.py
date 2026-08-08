"""提取 DSW cookie 并保存到 ms_session_cookies.json（通过 CDP）。"""
import json
import time

import requests
import websocket

CDP_PORT = 9222
DSW_URL = "https://dsw-gateway-cn-hangzhou.data.aliyun.com/dsw-2085479/lab/tree/dswQinghua"
COOKIE_DOMAINS = [
    "https://dsw-gateway-cn-hangzhou.data.aliyun.com",
    "https://account.aliyun.com",
    "https://www.modelscope.cn",
    "https://modelscope.cn",
]
OUTPUT = "ms_session_cookies.json"


def main():
    targets = requests.get(f"http://127.0.0.1:{CDP_PORT}/json").json()
    ws_url = None
    for t in targets:
        if t.get("type") == "page":
            ws_url = t["webSocketDebuggerUrl"]
            break
    if not ws_url:
        print("No page target found")
        return 1

    ws = websocket.create_connection(ws_url, timeout=30)
    mid = [0]

    def cdp_call(method, params=None):
        mid[0] += 1
        ws.send(json.dumps({"id": mid[0], "method": method, "params": params or {}}))
        while True:
            r = json.loads(ws.recv())
            if r.get("id") == mid[0]:
                return r.get("result", {})

    # 导航到 DSW 页面
    cdp_call("Page.enable")
    cdp_call("Page.navigate", {"url": DSW_URL})
    time.sleep(12)

    # 检查当前 URL
    result = cdp_call("Runtime.evaluate", {"expression": "window.location.href"})
    url = result.get("result", {}).get("value", "unknown")
    print(f"Current URL: {url[:120]}")

    # 提取 cookies
    all_cookies = {}
    for d in COOKIE_DOMAINS:
        res = cdp_call("Storage.getCookies", {"urls": [d]})
        for c in res.get("cookies", []):
            all_cookies[c["name"]] = c["value"]

    # 保存
    out = {
        "domain": "https://dsw-gateway-cn-hangzhou.data.aliyun.com",
        "cookies": all_cookies,
        "captured_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    has_ticket = "login_aliyunid_ticket" in all_cookies
    ticket_val = all_cookies.get("login_aliyunid_ticket", "")
    if has_ticket:
        print(f"login_aliyunid_ticket FOUND ({len(ticket_val)} chars)")
        print(f"Cookie saved to {OUTPUT}")
    else:
        print(f"login_aliyunid_ticket MISSING. Got {len(all_cookies)} cookies:")
        for k in sorted(all_cookies.keys()):
            print(f"  {k}")

    ws.close()
    return 0 if has_ticket else 1


if __name__ == "__main__":
    raise SystemExit(main())
