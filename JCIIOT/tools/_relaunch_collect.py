import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''import os, subprocess
# kill everything related
subprocess.run("pkill -9 -f collect50.py; pkill -9 -f load_factory_sorting_1_3fo3erfhisem_collect", shell=True)
print("killed")
'''

c = d.Dswhub()
payload = {"type": "file", "format": "text", "content": INNER}
c.s.put(d.BASE + "/api/contents/_kill2.py", json=payload, timeout=30)
code = r'''import subprocess, os, time
r = subprocess.run(["python", "/mnt/workspace/_kill2.py"], capture_output=True, text=True, timeout=60, env={**os.environ, "MUJOCO_GL":"osmesa"})
print(r.stdout[-200:])
time.sleep(3)
r2 = subprocess.run("pgrep -af 'collect50.py|load_factory_sorting_1_3fo3erfhisem_collect' | head", shell=True, capture_output=True, text=True)
print("remaining:", r2.stdout.strip() or "none")
''

# Now relaunch with thread limits
INNER2 = r'''import os, subprocess
os.environ["MUJOCO_GL"] = "osmesa"
os.environ.pop("PYOPENGL_PLATFORM", None)
# limit thread oversubscription for speed
os.environ["OMP_NUM_THREADS"] = "8"
os.environ["OPENBLAS_NUM_THREADS"] = "8"
os.environ["MKL_NUM_THREADS"] = "8"
os.environ["NUMEXPR_NUM_THREADS"] = "8"
script = "/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py"
cmd = ["python", script, "--num-rollouts", "50", "--no-render", "--output-name", "l1_50"]
with open("/mnt/workspace/_collect50b.log", "w") as log:
    r = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, timeout=21600, env=os.environ.copy())
    log.write("\nCOLLECT_RC=%d\n" % r.returncode)
print("collect rc", r.returncode)
'''
payload2 = {"type": "file", "format": "text", "content": INNER2}
c.s.put(d.BASE + "/api/contents/_collect50b.py", json=payload2, timeout=30)

code2 = r'''import subprocess, os
env = {**os.environ, "MUJOCO_GL": "osmesa", "OMP_NUM_THREADS":"8","OPENBLAS_NUM_THREADS":"8","MKL_NUM_THREADS":"8","NUMEXPR_NUM_THREADS":"8"}
r = subprocess.Popen(["nohup", "python", "/mnt/workspace/_collect50b.py"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True, env=env)
print("relaunched pid", r.pid)
'''
c2out = c.run_python(code, timeout=90)
print(c2out)
print(c.run_python(code2, timeout=60))
