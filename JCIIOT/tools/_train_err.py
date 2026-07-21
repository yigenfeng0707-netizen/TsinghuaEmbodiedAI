import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os, subprocess\n"
    "txt=open('/mnt/workspace/_train.log').read().splitlines()\n"
    "# print lines around first Traceback and the huggingface url\n"
    "out=[]\n"
    "for i,l in enumerate(txt):\n"
    "    if 'huggingface' in l.lower() or 'hf_hub' in l or 'Traceback' in l or 'raise' in l or 'File ' in l and 'train.py' in l:\n"
    "        out.append((i,l))\n"
    "for i,l in out[:40]:\n"
    "    print(i, l[:180])\n"
    "print('--- first 30 lines ---')\n"
    "for l in txt[:30]: print(l[:180])\n"
)
print(d.Dswhub().run_python(code, timeout=60))
