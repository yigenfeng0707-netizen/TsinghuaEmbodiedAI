import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = '''import os, subprocess
os.environ["MUJOCO_GL"] = "osmesa"
os.environ.pop("PYOPENGL_PLATFORM", None)
script = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py"
cmd = ["python", script, "--num-rollouts", "1", "--no-render", "--output-name", "demo_smoke_l1"]
with open("/mnt/workspace/_smoke.log", "w") as log:
    r = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, timeout=400)
    log.write("\\nRC=%d\\n" % r.returncode)
print("done rc", r.returncode)
'''

c = d.Dswhub()
payload = {"type": "file", "format": "text", "content": INNER}
c.s.put(d.BASE + "/api/contents/_smoke_collect2.py", json=payload, timeout=30)

code = r'''
import subprocess, os
env = {**os.environ, "MUJOCO_GL": "osmesa"}
r = subprocess.run(["python", "/mnt/workspace/_smoke_collect2.py"], capture_output=True, text=True, timeout=450, env=env)
print("outer RC", r.returncode, r.stdout[-300:], r.stderr[-300:])
# read the log
print("=== _smoke.log tail ===")
print(open("/mnt/workspace/_smoke.log").read()[-2500:])
'''
print(c.run_python(code, timeout=480))
