import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess\n"
    "base='/mnt/workspace/JCIIOT_repo/JCIIOT'\n"
    "# how is the BC policy loaded/evaluated? search grasp_policy / policy loading\n"
    "r = subprocess.run('grep -rln \"robomimic\\|policy\\|checkpoint\\|model_epoch\" '+base+'/src '+base+'/app.py 2>/dev/null | head', shell=True, capture_output=True, text=True)\n"
    "print('FILES:', r.stdout.strip())\n"
    "# look at grasp_policy skill\n"
    "r2 = subprocess.run('ls '+base+'/src/robot_agent/skills/', shell=True, capture_output=True, text=True)\n"
    "print('SKILLS:', r2.stdout.strip())\n"
    "# grep for robomimic policy load / env type in src\n"
    "r3 = subprocess.run(\"grep -rn 'ROBOMIMIC_ROBOSUITE_ENV_TYPE\\|robomimic.envs\\|RolloutRunner\\|run_rollout\\|playback\\|env_meta\\|env_name' \"+base+\"/src 2>/dev/null | head -20\", shell=True, capture_output=True, text=True)\n"
    "print('SRC REFS:', r3.stdout.strip())\n"
)
print(d.Dswhub().run_python(code, timeout=90))
