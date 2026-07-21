import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os\n"
    "base='/mnt/workspace/JCIIOT_repo/JCIIOT'\n"
    "checks={\n"
    " 'robot_params.json': base+'/knowledge/robot_params.json',\n"
    " 'champion_transport.py': base+'/src/robot_agent/workflows/champion_transport.py',\n"
    " 'checkpoint': base+'/robosuite/robosuite/model_epoch_150.pth',\n"
    " 'viewer_patch': base+'/src/robot_agent/environments/robosuite_backend.py',\n"
    "}\n"
    "for k,p in checks.items():\n"
    "    print(k, os.path.exists(p), (os.path.getsize(p) if os.path.exists(p) else '-'))\n"
    "# verify viewer guard present\n"
    "s=open(checks['viewer_patch']).read()\n"
    "print('viewer guard present:', 'if not self._headless:' in s and '_set_viewer_camera(self._env' in s)\n"
    "# verify robot_params llm\n"
    "import json\n"
    "rp=json.load(open(checks['robot_params.json'],encoding='utf-8'))\n"
    "print('llm:', json.dumps(rp.get('llm',{}), ensure_ascii=False))\n"
)
print(d.Dswhub().run_python(code, timeout=90))
