import sys
sys.path.insert(0, ".")
import tools.dswhub as d

# Run recon entirely via the kernel, using subprocess to probe candidate interpreters.
code = r'''
import subprocess, json, os, shlex

def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=40)
        return (r.returncode, r.stdout.strip() + r.stderr.strip())
    except Exception as e:
        return (-1, repr(e))

candidates = ["python", "python3", "/usr/bin/python3", "/usr/local/bin/python3",
              "bash -c 'source ~/.bashrc; python'", "bash -c 'source ~/.profile; python'"]
report = {}
for cand in candidates:
    rc, out = run(f"{cand} -c \"import mujoco,robosuite,robomimic; print('OK',mujoco.__version__,robosuite.__version__)\" 2>&1 | head -3")
    report[cand] = out[:200]

# find venvs / conda
rc, out = run("ls -d /opt/conda/envs/* 2>/dev/null; ls -d /root/*venv* /mnt/workspace/*venv* 2>/dev/null; which conda 2>/dev/null; find / -maxdepth 6 -name 'robomimic' -type d 2>/dev/null | head")
report["_venv_search"] = out[:300]

rc, out = run("pip --version 2>&1; python -m pip --version 2>&1")
report["_pip"] = out[:200]

rc, out = run("cat /mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_1_3fo3erfhisem_collect.py 2>/dev/null | head -20")
report["_collect_head"] = out[:400]

print(json.dumps(report, ensure_ascii=False, indent=1))
'''

c = d.Dswhub()
print(c.run_python(code, timeout=120))
