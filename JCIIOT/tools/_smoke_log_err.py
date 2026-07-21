import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = r'''
txt = open("/mnt/workspace/_smoke.log").read()
import re
# find all traceback / error lines
lines = txt.splitlines()
errs = [l for l in lines if any(k in l for k in ["Traceback","Error","Exception","raise","assert","File \"", "line "])]
print("=== error-ish lines (first 40) ===")
for l in errs[:40]:
    print(l[:200])
# also print the very tail after the big array
# find where the array ends (RC=)
idx = txt.rfind("RC=")
print("=== around RC ===")
print(txt[max(0,idx-600):idx+20])
'''
c = d.Dswhub()
print(c.run_python(code, timeout=60))
