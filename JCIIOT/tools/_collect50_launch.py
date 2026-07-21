import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''import os, subprocess
os.environ["MUJOCO_GL"] = "osmesa"
os.environ.pop("PYOPENGL_PLATFORM", None)
script = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py"
cmd = ["python", script, "--num-rollouts", "50", "--no-render", "--output-name", "l1_50"]
with open("/mnt/workspace/_collect50.log", "w") as log:
    r = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, timeout=7200)
    log.write("\nCOLLECT_RC=%d\n" % r.returncode)
print("collect launched, rc", r.returncode)
'''

c = d.Dswhub()
payload = {"type": "file", "format": "text", "content": INNER}
c.s.put(d.BASE + "/api/contents/_collect50.py", json=payload, timeout=30)

# launch in background via nohup so it survives; we read the log later
code = r'''
import subprocess, os
env = {**os.environ, "MUJOCO_GL": "osmesa"}
# launch detached
r = subprocess.Popen(["nohup", "python", "/mnt/workspace/_collect50.py"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True, env=env)
print("launched pid", r.pid)
'''
print(c.run_python(code, timeout=60))
