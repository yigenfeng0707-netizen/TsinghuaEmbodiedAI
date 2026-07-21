import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "for name,path in [('COLLECT','/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py'),\n"
    "                  ('EVAL','/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py')]:\n"
    "    s=open(path).read()\n"
    "    print('====',name,'====')\n"
    "    for k in ['DEFAULT_ROBOT_BASE_POS','DEFAULT_ROBOT_BASE_ORI','DEFAULT_FACTORY_SCENE','DEFAULT_OBJECT_NAME','DEFAULT_GRIPPER_TARGET_OFFSET','DEFAULT_POST_HOLD_STEPS','DEFAULT_INITIAL_VIEW_STEPS']:\n"
    "        m=re.search(k+r'\\s*=\\s*([^\\)\\n]+)', s)\n"
    "        print(' ',k,'=', m.group(1).strip() if m else None)\n"
)
print(d.Dswhub().run_python(code, timeout=60))
