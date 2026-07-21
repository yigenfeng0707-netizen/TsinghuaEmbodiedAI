import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)

code = (
    "import os,re\n"
    "p='/mnt/workspace/JCIIOT_repo/JCIIOT/robosuite/robosuite/environments/factory_sorting/load_factory_sorting_evalization.py'\n"
    "src=open(p).read()\n"
    "i=src.find('def run_factory_sorting_grasp_from_args(')\n"
    "# find 'env =' and 'policy' and 'evaluate_once' after i\n"
    "seg=src[i:]\n"
    "for kw in ['env =','make_eval_env','load_factory_sorting_policy','policy =','evaluate_once','obs, _, _, _','policy(obs','get_observation','env.step']:\n"
    "    j=seg.find(kw)\n"
    "    print('===',kw,'@',j,'===')\n"
    "    if j>=0: print(seg[max(0,j-60):j+120].replace(chr(10),' '))\n"
)
print(d.Dswhub().run_python(code, timeout=60))
