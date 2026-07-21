import sys
sys.path.insert(0, ".")
import tools.dswhub as d
import os as _os
_os.environ.pop("MUJOCO_GL", None)
c = d.Dswhub()
print(c.run_python(
"import json, math\n"
"APP='/mnt/workspace/JCIIOT_repo/JCIIOT'\n"
"map_dir=APP+'/robosuite/robosuite/environments/factory_sorting/generated_maps'\n"
"sm=json.load(open(map_dir+'/factory_sorting_1_3fo3erfhisem_scene_regenerated_semantic_map.json'))\n"
"# search all entries for output_4\n"
"def find_output4(obj, path=''):\n"
"    if isinstance(obj, dict):\n"
"        if obj.get('name')=='output_4' or obj.get('id')=='output_4':\n"
"            print('FOUND at', path, ':', obj)\n"
"        for k,v in obj.items(): find_output4(v, path+'.'+k)\n"
"    elif isinstance(obj, list):\n"
"        for i,v in enumerate(obj): find_output4(v, path+'['+str(i)+']')\n"
"find_output4(sm)\n"
"final=[-0.0136,-7.3127]\n"
"# also check output stations with center near final\n"
"for st in sm.get('stations',[]):\n"
"    if st.get('role')=='output':\n"
"        c2=st.get('center')\n"
"        if c2:\n"
"            td=math.sqrt(sum((a-b)**2 for a,b in zip(final,c2[:2])))\n"
"            print(st.get('name'), 'center', c2[:2], 'dist_to_final', round(td,3))\n", timeout=30))
