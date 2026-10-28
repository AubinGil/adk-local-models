import importlib.metadata as md, importlib.util, json, sys
from pathlib import Path
from packaging.requirements import Requirement
from packaging.markers import default_environment
root=Path('runs/007-native-compare/dependencies'); root.mkdir(parents=True,exist_ok=True)
label=sys.argv[1]
dists=sorted(md.distributions(),key=lambda d:d.metadata['Name'].lower())
inventory=[]
for d in dists:
    inventory.append({'name':d.metadata['Name'],'version':d.version,'requires':d.requires or [],'installed_file_bytes':sum(f.locate().stat().st_size for f in (d.files or []) if f.locate().is_file()),'license_expression':d.metadata.get('License-Expression'),'license':d.metadata.get('License')})
seen={}; processed=set(); pending=[('google-adk',('openai',) if label=='native' else ())]
while pending:
    name,extras=pending.pop(); key=name.lower().replace('_','-')
    state=(key,tuple(sorted(extras)))
    if state in processed: continue
    processed.add(state)
    d=md.distribution(name); edges=set(seen.get(key,{}).get('dependencies',[]))
    for spec in d.requires or []:
        req=Requirement(spec)
        if req.marker is None or any(req.marker.evaluate(dict(default_environment(),extra=e)) for e in ('',*extras)):
            edges.add(req.name); pending.append((req.name,tuple(req.extras)))
    seen[key]={'version':d.version,'dependencies':sorted(edges)}
(root/(label+'.json')).write_text(json.dumps({'inventory':inventory,'closure':seen,'openai_importable':importlib.util.find_spec('openai') is not None,'litellm_importable':importlib.util.find_spec('litellm') is not None},indent=2)+'\n')
print(label,len(inventory),len(seen),sum(x['installed_file_bytes'] for x in inventory))
