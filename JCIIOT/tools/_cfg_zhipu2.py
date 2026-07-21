import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os\n"
    "os.makedirs('/mnt/workspace/JCIIOT_repo/JCIIOT/tools', exist_ok=True)\n"
    "ZHIPU_BASE='https://open.bigmodel.cn/api/paas/v4/'\n"
    "ZHIPU_KEY='608e441d08264fa98257baf063c6a7b7.Ko08EDn4wCaO5QS8'\n"
    "env={'OPENAI_BASE_URL':ZHIPU_BASE,'OPENAI_MODEL':'glm-5.2','OPENAI_API_KEY':ZHIPU_KEY,'VLM_BASE_URL':ZHIPU_BASE,'VLM_API_KEY':ZHIPU_KEY,'VLM_MODEL':'GLM-5V-Turbo','MUJOCO_GL':'osmesa','GATE_OLLAMA':'false'}\n"
    "open('/mnt/workspace/JCIIOT_repo/JCIIOT/tools/zhipu_env.sh','w').write('\\n'.join(f'export {k}=\"{v}\"' for k,v in env.items())+'\\n')\n"
    "print('env written')\n"
    "# verify robot_params\n"
    "import json\n"
    "d=json.load(open('/mnt/workspace/JCIIOT_repo/JCIIOT/knowledge/robot_params.json',encoding='utf-8'))\n"
    "print('llm:',json.dumps(d['llm'],ensure_ascii=False))\n"
)
print(d.Dswhub().run_python(code, timeout=90))
