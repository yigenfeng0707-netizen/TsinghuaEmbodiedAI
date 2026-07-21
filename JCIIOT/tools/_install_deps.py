"""Install JCIIOT deps on the DSW instance against the existing ROCm torch.

Strategy:
  - Do NOT touch torch (ROCm build already present).
  - Install mujoco==3.9.0 (repo pin) and numpy/h5py/scipy if missing.
  - pip install -e the vendored robosuite & robomimic with --no-deps so we keep
    the existing scientific stack and the ROCm torch.
  - Force MUJOCO_GL=mujoco (software offscreen) because EGL fails on the AMD
    compute chip (no amdgpu_dri.so).
"""
import sys
sys.path.insert(0, ".")
import tools.dswhub as d

SCRIPT = r'''#!/bin/bash
set -e
export MUJOCO_GL=mujoco
export PYTHONUNBUFFERED=1
LOG=/mnt/workspace/_install.log
exec > >(tee -a $LOG) 2>&1
echo "INSTALL START $(date)"

python - <<'PY'
import importlib, sys
need = ["numpy","scipy","h5py","mujoco","numba","qpsolvers","opencv-python","Pillow","tqdm","termcolor","pytest","imageio","psutil","pyyaml"]
for m in need:
    try:
        importlib.import_module(m.replace("-","_").split("[")[0].split(">=")[0].split("==")[0])
        print("OK", m)
    except Exception as e:
        print("MISSING", m)
PY

echo "=== install mujoco==3.9.0 (keep torch) ==="
pip install "mujoco==3.9.0" --no-deps -q 2>&1 | tail -5

echo "=== install scientific deps that may be missing (no torch) ==="
pip install "numpy==1.26.4" "scipy" "h5py" "numba" "qpsolvers[quadprog]" "opencv-python" "Pillow" "tqdm" "termcolor" "pytest" "imageio" "psutil" "pyyaml" "einops" "tensorboard" "hydra-core" "paramiko" "gdown" 2>&1 | tail -8

cd /mnt/workspace/JCIIOT_repo/JCIIOT
echo "=== pip install -e robosuite --no-deps ==="
pip install -e ./robosuite --no-deps -q 2>&1 | tail -5
echo "=== pip install -e robomimic --no-deps ==="
pip install -e ./robomimic --no-deps -q 2>&1 | tail -5

echo "=== verify ==="
python -c "import mujoco,robosuite,robomimic,torch,numpy,h5py; print('mujoco',mujoco.__version__,'robosuite OK robomimic OK torch',torch.__version__,'numpy',numpy.__version__)"
echo "=== sw render test ==="
MUJOCO_GL=mujoco python -c "import mujoco,numpy as np; m=mujoco.MjModel.from_xml_string('<mujoco><worldbody><geom type=\"sphere\" size=\"0.1\"/></worldbody></mujoco>'); r=mujoco.Renderer(m,64,64); r.update_scene(mujoco.MjData(m)); r.render(); print('SW RENDER OK')"
echo "INSTALL DONE $(date)"
'''

# upload script via contents API PUT
c = d.Dswhub()
payload = {"type": "file", "format": "text", "content": SCRIPT}
r = c.s.put(d.BASE + "/api/contents/_install_deps.sh", json=payload, timeout=30)
print("upload script:", r.status_code)
# run via kernel subprocess
out = c.run_python(
    "import subprocess; r=subprocess.run(['bash','/mnt/workspace/_install_deps.sh'],capture_output=True,text=True,timeout=600); "
    "print('RC',r.returncode); print(r.stdout[-3000:]); print('ERR',r.stderr[-1500:])",
    timeout=600,
)
print(out)
