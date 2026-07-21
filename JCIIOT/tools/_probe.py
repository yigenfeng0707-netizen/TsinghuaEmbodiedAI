import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

c = d.Dswhub()
BASE = d.BASE
for path in ["/", "/api", "/api/status", "/api/sessions", "/lab"]:
    try:
        r = c.s.get(BASE + path, timeout=15, allow_redirects=False)
        print(path, "->", r.status_code, r.headers.get("location",""))
    except Exception as e:
        print(path, "ERR", repr(e)[:120])
