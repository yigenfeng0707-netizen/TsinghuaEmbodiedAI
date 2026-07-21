import sys
sys.path.insert(0, "tools")
import json, time
import tools.cdp_ms as m

ws = m.get_ws_url()
cdp = m.CDP(ws)
url = ("https://dsw-gateway-cn-hangzhou.data.aliyun.com/dsw-2041922/lab"
       "?appId=MAAS&instanceId=dsw-jrm3mxumbmm8q80372&site=cn&features=EnableSubDomainProxy")
cdp.navigate(url)
time.sleep(15)
r = cdp.call("Runtime.evaluate", {"expression": "location.href", "returnByValue": True})
print("FINAL URL:", r.get("result", {}).get("value", ""))
# look for a consent/authorize/submit button
for sel in ["button[type=submit]", "input[type=submit]", "a.btn", "#submit", ".btn-primary", "button"]:
    try:
        cnt = cdp.call("Runtime.evaluate", {"expression": f"document.querySelectorAll('{sel}').length",
                                             "returnByValue": True}).get("result", {}).get("value", 0)
        if cnt:
            print("FOUND", sel, "count", cnt)
    except Exception:
        pass
txt = cdp.call("Runtime.evaluate", {"expression": "document.body ? document.body.innerText.slice(0,500) : ''",
                                     "returnByValue": True}).get("result", {}).get("value", "")
print("PAGE TEXT:", repr(txt[:500]))
