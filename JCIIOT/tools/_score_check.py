import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c = d.Dswhub()
print(c.run_python(
"import json, math\n"
"APP='/mnt/workspace/JCIIOT_repo/JCIIOT'\n"
"cfg=json.load(open(APP+'/knowledge/task_config.json'))\n"
"task=next(t for t in cfg['tasks'] if t['level']=='L1')\n"
"src=[7.059,4.619]; final=[-0.0136,-7.3127]\n"
"dist_moved=math.sqrt(sum((a-b)**2 for a,b in zip(src,final)))\n"
"print('object moved:', round(dist_moved,3), 'm  >1m:', dist_moved>1)\n"
"map_dir=APP+'/robosuite/robosuite/environments/factory_sorting/generated_maps'\n"
"sm=json.load(open(map_dir+'/factory_sorting_1_3fo3erfhisem_scene_regenerated_semantic_map.json'))\n"
"tgt=None\n"
"for st in sm.get('stations',[]):\n"
"    if st.get('name')=='output_4' or st.get('id')=='output_4':\n"
"        tgt=st; break\n"
"print('target output_4:', tgt)\n"
"if tgt:\n"
"    tp=tgt.get('position') or tgt.get('pos') or tgt.get('xy')\n"
"    print('target pos:', tp)\n"
"    if tp:\n"
"        td=math.sqrt(sum((a-b)**2 for a,b in zip([final[0],final[1]], tp[:2])))\n"
"        print('dist to target:', round(td,3), 'm  <0.8m:', td<0.8)\n", timeout=30))
