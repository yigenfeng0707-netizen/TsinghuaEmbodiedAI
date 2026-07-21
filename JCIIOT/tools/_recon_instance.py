import sys
sys.path.insert(0, ".")
import tools.dswhub as d

code = r'''
import sys, subprocess, os
print("PY", sys.version.split()[0])
try:
    import torch; print("torch", torch.__version__, "cuda/rocm avail", torch.cuda.is_available())
except Exception as e: print("torch ERR", e)
try:
    import mujoco; print("mujoco", mujoco.__version__)
except Exception as e: print("mujoco ERR", e)
try:
    os.environ["MUJOCO_GL"] = "mujoco"
    import numpy as np
    m = mujoco.MjModel.from_xml_string('<mujoco><worldbody><geom type="sphere" size="0.1"/></worldbody></mujoco>')
    r = mujoco.Renderer(m, 64, 64); r.update_scene(mujoco.MjData(m)); r.render(); print("SW RENDER OK")
except Exception as e: print("SW RENDER ERR", repr(e)[:160])
try:
    import robomimic; print("robomimic", getattr(robomimic, "__version__", "?"))
except Exception as e: print("robomimic ERR", repr(e)[:160])
try:
    import robosuite; print("robosuite", getattr(robosuite, "__version__", "?"))
except Exception as e: print("robosuite ERR", repr(e)[:160])
print("DISK", subprocess.run(["df","-h","/mnt/workspace"],capture_output=True,text=True).stdout.strip().splitlines()[-1])
print("MEM", subprocess.run(["free","-h"],capture_output=True,text=True).stdout.strip().splitlines()[1])
print("CPU", subprocess.run(["nproc"],capture_output=True,text=True).stdout.strip())
print("CWD", os.getcwd())
print("PYTHONPATH", os.environ.get("PYTHONPATH",""))
'''

c = d.Dswhub()
print(c.run_python(code))
