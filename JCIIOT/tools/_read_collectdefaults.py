import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py'\n"
    "s=open(p).read()\n"
    "for k in ['DEFAULT_UP_STEPS','DEFAULT_XY_STEPS','DEFAULT_DOWN_STEPS','DEFAULT_SETTLE_STEPS','DEFAULT_GRASP_STEPS','DEFAULT_VIEW_STEPS','DEFAULT_NUM_ROLLOUTS','DEFAULT_MAX_ACTION','DEFAULT_DEMO_DIR','DEFAULT_EP_PATH','DEFAULT_INITIAL_VIEW_STEPS']:\n"
    "    m=re.search(k+r'\\s*=\\s*([^\\n]+)', s)\n"
    "    print(k,'=', m.group(1).strip() if m else 'NOT FOUND')\n"
)
print(d.Dswhub().run_python(code, timeout=60))
