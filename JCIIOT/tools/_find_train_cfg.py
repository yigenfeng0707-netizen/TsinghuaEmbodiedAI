import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import subprocess\n"
    "base='/mnt/workspace/JCIIOT_repo/JCIIOT'\n"
    "# find configs/json mentioning factory or tiago or the obs keys\n"
    "r = subprocess.run(\"grep -rln 'robot0_left_eef_pos\\|factory_sorting\\|FactorySorting' \"+base+\"/robomimic/exps \"+base+\"/robosuite 2>/dev/null | head -20\", shell=True, capture_output=True, text=True)\n"
    "print('CONFIG FILES:', r.stdout.strip())\n"
    "# list exps dirs\n"
    "r2 = subprocess.run('find '+base+'/robomimic/exps -maxdepth 2 -type d 2>/dev/null', shell=True, capture_output=True, text=True)\n"
    "print('EXPS DIRS:', r2.stdout.strip())\n"
    "# any json with 'left_eef' or dual arm\n"
    "r3 = subprocess.run(\"grep -rln 'robot0_left_eef_pos' \"+base+\" --include=*.json --include=*.yaml 2>/dev/null | head\", shell=True, capture_output=True, text=True)\n"
    "print('JSON WITH left_eef:', r3.stdout.strip())\n"
    "# train.py usage / args\n"
    "r4 = subprocess.run('grep -n \"add_argument\\|dataset\\|config\" '+base+'/robomimic/scripts/train.py | head -30', shell=True, capture_output=True, text=True)\n"
    "print('TRAIN.PY ARGS:', r4.stdout.strip())\n"
)
print(d.Dswhub().run_python(code, timeout=90))
