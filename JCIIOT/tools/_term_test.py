import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import time, websocket, json as _json

c = d.Dswhub()
# create terminal
r = c.s.post(d.BASE + "/api/terminals", timeout=30)
print("create term:", r.status_code, r.json())
term = r.json()["name"]
ws_url = d.DOMAIN.replace("https://", "wss://") + f"/dsw-2041922/terminals/websocket/{term}"
ws = websocket.create_connection(ws_url, header=[f"Cookie: login_aliyunid_ticket={c.ticket}"], timeout=30)
# send a single echo command
ws.send(_json.dumps(["stdin", "echo PROBE_OK; python3 --version; ls /usr/local/lib/python3.12/dist-packages | grep -i mujoco; echo DONE\n"]))
buf = ""
deadline = time.time() + 10
while time.time() < deadline:
    try:
        msg = ws.recv()
        if isinstance(msg, tuple) and len(msg) > 1:
            buf += msg[1]
    except Exception:
        break
ws.close()
print("TERMINAL OUTPUT:")
print(repr(buf))
