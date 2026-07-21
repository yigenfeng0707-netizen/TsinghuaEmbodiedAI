import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,sys\n"
    "os.environ['MUJOCO_GL']='osmesa'\n"
    "APP='/mnt/workspace/JCIIOT_repo/JCIIOT'\n"
    "for p in [APP+'/src',APP,APP+'/robomimic',APP+'/robosuite/robosuite']:\n"
    "    sys.path.insert(0,p)\n"
    "import robot_agent\n"
    "print('robot_agent file:', robot_agent.__file__)\n"
    "import robot_agent.workflows as w\n"
    "print('workflows:', w.__file__, os.listdir(os.path.dirname(w.__file__)))\n"
    "try:\n"
    "    from robot_agent.workflows.champion_transport import ChampionTransportFlow\n"
    "    print('champion OK')\n"
    "except Exception as e:\n"
    "    import traceback; traceback.print_exc()\n"
)
print(d.Dswhub().run_python(code, timeout=120))
