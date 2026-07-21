import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c = d.Dswhub()
print("==== bc_l1_config.json ====")
print(c.run_python("print(open('/mnt/workspace/JCIIOT_repo/JCIIOT/bc_l1_config.json').read())", timeout=30))
print("==== find demo hdf5 ====")
print(c.run_python(
"import os,glob\n"
"for root in ['/mnt/workspace/JCIIOT_repo/JCIIOT','/mnt/workspace']:\n"
"    for f in glob.glob(root+'/**/*.hdf5',recursive=True)[:15]:\n"
"        print(f, os.path.getsize(f))\n", timeout=60))
