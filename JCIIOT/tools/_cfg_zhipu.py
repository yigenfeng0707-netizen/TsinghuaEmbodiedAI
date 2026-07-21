import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

INNER = r'''
import json, os
p = "/mnt/workspace/JCIIOT_repo/JCIIOT/knowledge/robot_params.json"
data = json.load(open(p, encoding="utf-8"))
ZHIPU_BASE = "https://open.bigmodel.cn/api/paas/v4/"
ZHIPU_KEY = "608e441d08264fa98257baf063c6a7b7.Ko08EDn4wCaO5QS8"
llm = data.setdefault("llm", {})
llm["openai_base_url"] = ZHIPU_BASE
llm["openai_model"] = "glm-5.2"
llm["vision_model"] = "GLM-5V-Turbo"
json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

env = {
    "OPENAI_BASE_URL": ZHIPU_BASE,
    "OPENAI_MODEL": "glm-5.2",
    "OPENAI_API_KEY": ZHIPU_KEY,
    "VLM_BASE_URL": ZHIPU_BASE,
    "VLM_API_KEY": ZHIPU_KEY,
    "VLM_MODEL": "GLM-5V-Turbo",
    "MUJOCO_GL": "osmesa",
    "GATE_OLLAMA": "false",
}
open("/mnt/workspace/JCIIOT_repo/JCIIOT/tools/zhipu_env.sh", "w").write(
    "\n".join(f'export {k}="{v}"' for k, v in env.items()) + "\n"
)
print("robot_params llm updated:", json.dumps(data["llm"], ensure_ascii=False))
print("zhipu_env.sh written")
'''

c = d.Dswhub()
c.s.put(d.BASE + "/api/contents/_cfg_zhipu.py", json={"type":"file","format":"text","content":INNER}, timeout=30)
print(c.run_python("import subprocess,os\nr=subprocess.run(['python','/mnt/workspace/_cfg_zhipu.py'],capture_output=True,text=True,timeout=60,env={**os.environ,'MUJOCO_GL':'osmesa'}); print(r.stdout); print('ERR',r.stderr[-400:])", timeout=90))
