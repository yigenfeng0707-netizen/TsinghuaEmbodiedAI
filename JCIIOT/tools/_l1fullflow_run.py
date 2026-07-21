import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import os, sys, importlib.util, traceback as _tb, json, numpy as np
os.environ["MUJOCO_GL"]="osmesa"; os.environ["PYOPENGL_PLATFORM"]="osmesa"
os.environ["GATE_OLLAMA"]="false"; os.environ["GATE_STEP_TIMEOUT"]="false"
APP="/mnt/workspace/JCIIOT_repo/JCIIOT"
for p in [APP+"/src",APP,APP+"/robomimic",APP+"/robosuite/robosuite"]:
    sys.path.insert(0,p)
spec=importlib.util.spec_from_file_location("tsr",APP+"/src/robot_agent/task_subprocess_runner.py")
tsr=importlib.util.module_from_spec(spec); spec.loader.exec_module(tsr)
from pathlib import Path as P
tsr._configure_paths(P(APP))
def log(*a): print(*a, flush=True)

agent = tsr._build_agent(P(APP), task_index=0, knowledge_enabled=False)
log("agent built, backend=", type(agent.backend).__name__)

from robot_agent.workflows.champion_transport import ChampionTransportFlow
cfg_path = str(P(APP) / "knowledge" / "task_config.json")
flow = ChampionTransportFlow(
    backend=agent.backend,
    scene_context=agent.scene_context,
    grid=agent.grid,
    task_config_path=cfg_path,
)
log("flow built, running L1...")
try:
    report = flow.execute_level("L1")
    log("=== L1 RESULT ===")
    log("success:", report.success)
    log("failed_step:", report.failed_step)
    log("source:", report.source, "target:", report.target, "object:", report.object_name)
    for s in report.steps:
        log("  step:", s.skill_name, "success:", s.success, (s.message or "")[:80])
except Exception as e:
    log("L1 FAIL:", repr(e)[:300])
    log(_tb.format_exc()[-1500:])

cfg = json.load(open(cfg_path))
task = next(t for t in cfg["tasks"] if t["level"] == "L1")
env = agent.backend.env
for jn in env.sim.model.joint_names:
    if task["object"] in jn and ("_free" in jn or "_joint0" in jn):
        qpos = env.sim.data.get_joint_qpos(jn)
        log("final object pos:", qpos.tolist()[:3])
        break
agent.backend.close()
log("DONE")
'''

c = d.Dswhub()
c.s.put(d.BASE+"/api/contents/_l1fullflow.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python(
"import subprocess,os\n"
"env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa','GATE_OLLAMA':'false'}\n"
"p=subprocess.Popen(['python','/mnt/workspace/_l1fullflow.py'],stdout=open('/mnt/workspace/_l1fullflow.log','w'),stderr=subprocess.STDOUT,env=env)\n"
"print('LAUNCHED',p.pid)\n", timeout=30))
