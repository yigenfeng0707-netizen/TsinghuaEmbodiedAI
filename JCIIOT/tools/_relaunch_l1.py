import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import os, sys, json, importlib.util, traceback as _tb
os.environ["MUJOCO_GL"]="osmesa"; os.environ["PYOPENGL_PLATFORM"]="osmesa"; os.environ["GATE_OLLAMA"]="false"
os.environ["OPENAI_API_KEY"]="608e441d08264fa98257baf063c6a7b7.Ko08EDn4wCaO5QS8"
os.environ["OPENAI_BASE_URL"]="https://open.bigmodel.cn/api/paas/v4/"
os.environ["OPENAI_MODEL"]="glm-5.2"
os.environ["VLM_BASE_URL"]="https://open.bigmodel.cn/api/paas/v4/"
os.environ["VLM_API_KEY"]="608e441d08264fa98257baf063c6a7b7.Ko08EDn4wCaO5QS8"
os.environ["VLM_MODEL"]="GLM-5V-Turbo"
APP="/mnt/workspace/JCIIOT_repo/JCIIOT"
for p in [APP+"/src",APP,APP+"/robomimic",APP+"/robosuite/robosuite"]:
    sys.path.insert(0,p)
spec=importlib.util.spec_from_file_location("tsr",APP+"/src/robot_agent/task_subprocess_runner.py")
tsr=importlib.util.module_from_spec(spec); spec.loader.exec_module(tsr)
from pathlib import Path as P
tsr._configure_paths(P(APP))
def log(*a): print(*a, flush=True)
log("START")
from robot_agent.core.map_loader import load_map_files
from robot_agent.core.scene_context import SceneContext
from robot_agent.environments import RobosuiteBackend
from robot_agent.workflows.champion_transport import ChampionTransportFlow
app_dir=P(APP); task_index=0
env_name=tsr._scene_env_name(task_index)
semantic,grid_file=tsr._choose_map_files(app_dir,task_index)
scene,grid=load_map_files(semantic,grid_file)
scene_ctx=SceneContext.from_semantic_map(scene)
backend=RobosuiteBackend(env_name=env_name,camera="birdview",headless=True,drive_mode="direct")
backend._scene_context=scene_ctx
backend.reset(); log("reset1 ok")
raw=getattr(backend.env,"material_metadata",{}) or {}
dyn={}
for on,info in raw.items():
    if not isinstance(info,dict): continue
    pn=str(info.get("port_name") or "")
    if pn:
        dyn[pn]=on
        if pn.startswith("input_"): dyn["line_"+pn.split("_",1)[1]]=on
        elif pn.startswith("line_"): dyn["input_"+pn.split("_",1)[1]]=on
full=dict(dyn); full.update(tsr.SCENE_INPUT_OBJECT_MAP.get(env_name,{}))
backend.set_physics_grasp_config(device="cpu",object_map=full)
backend.reset(); log("reset2 ok; building flow")
flow=ChampionTransportFlow(backend=backend,scene_context=scene_ctx,grid=grid,task_config_path=APP+"/knowledge/task_config.json")
log("=== running L1 ===")
try:
    rep=flow.execute_level("L1")
except Exception as _e:
    log("EXC execute_level:", repr(_e)); log(_tb.format_exc()); backend.close(); log("DONE-EXC"); raise SystemExit(0)
log("=== L1 REPORT ===")
log("success:",rep.success,"failed_step:",rep.failed_step)
for s in rep.steps:
    log(f"  - {s.skill_name}: success={s.success} msg={s.message}")
obj=rep.object_name; log("object_name:",obj)
obj_pos=None
md=getattr(backend.env,"material_metadata",{}) or {}
info=md.get(obj)
if info and "body_name" in info:
    obj_pos=backend.env.sim.data.body_xpos[backend.env.sim.model.body_name2id(info["body_name"])].copy()
elif hasattr(backend.env,"obj_body_id") and obj in backend.env.obj_body_id:
    obj_pos=backend.env.sim.data.body_xpos[backend.env.obj_body_id[obj]].copy()
log("final object pos:",None if obj_pos is None else obj_pos.tolist())
tc=json.loads(P(APP+"/knowledge/task_config.json").read_text(encoding="utf-8"))
t=next(x for x in tc["tasks"] if x["level"]=="L1")
src=tc["grasp_poses"].get(t["source"],{}).get("pos")
log("source grasp pos:",src)
# also report distance to target
tgt=tc["grasp_poses"].get(t["target"],{}).get("pos")
log("target pos:",tgt)
if obj_pos is not None and tgt:
    import numpy as _np
    d=np.linalg.norm(_np.array(obj_pos[:2])-_np.array(tgt[:2]))
    log("dist to target (xy):",round(float(d),3))
backend.close(); log("DONE")
'''

c=d.Dswhub()
c.s.put(d.BASE+"/api/contents/_run_l1b.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
code = (
    "import subprocess,os\n"
    "env={**os.environ,'MUJOCO_GL':'osmesa','PYOPENGL_PLATFORM':'osmesa','GATE_OLLAMA':'false',\n"
    " 'OPENAI_API_KEY':'608e441d08264fa98257baf063c6a7b7.Ko08EDn4wCaO5QS8','OPENAI_BASE_URL':'https://open.bigmodel.cn/api/paas/v4/','OPENAI_MODEL':'glm-5.2',\n"
    " 'VLM_BASE_URL':'https://open.bigmodel.cn/api/paas/v4/','VLM_API_KEY':'608e441d08264fa98257baf063c6a7b7.Ko08EDn4wCaO5QS8','VLM_MODEL':'GLM-5V-Turbo'}\n"
    "p=subprocess.Popen(['python','/mnt/workspace/_run_l1b.py'],stdout=open('/mnt/workspace/_run_l1b.log','w'),stderr=subprocess.STDOUT,env=env)\n"
    "print('LAUNCHED pid',p.pid)\n"
)
print(c.run_python(code, timeout=60))
