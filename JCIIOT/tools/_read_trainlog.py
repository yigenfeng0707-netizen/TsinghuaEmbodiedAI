import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c = d.Dswhub()
# check if train log exists and read loss trend
print(c.run_python(
"import os\n"
"p='/mnt/workspace/_train.log'\n"
"print('train log exists:', os.path.exists(p), os.path.getsize(p) if os.path.exists(p) else 0)\n"
"if os.path.exists(p):\n"
"    t=open(p).read()\n"
"    import re\n"
"    losses=re.findall(r'Epoch \\d+.*?Avg Loss\\s*:([\\d.]+)', t)\n"
"    print('num epochs logged:', len(losses))\n"
"    if losses:\n"
"        print('first 5 losses:', losses[:5])\n"
"        print('last 5 losses:', losses[-5:])\n"
"    # also check TRAIN_RC\n"
"    idx=t.find('TRAIN_RC')\n"
"    print('rc:', t[idx:idx+20] if idx>=0 else 'not found')\n"
"    # last 500 chars\n"
"    print('--- tail ---')\n"
"    print(t[-500:])\n", timeout=30))
